"""環境管理器

處理不同環境的配置、環境變量和密鑰管理。
"""

import os
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog
import threading
from datetime import datetime, timedelta

logger = structlog.get_logger(__name__)


class Environment(Enum):
    """環境類型"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


@dataclass
class EnvironmentVariable:
    """環境變量"""
    name: str
    value: str
    description: str = ""
    required: bool = False
    sensitive: bool = False
    default_value: Optional[str] = None
    validation_pattern: Optional[str] = None
    environment_specific: bool = False
    
    def __post_init__(self):
        if self.sensitive and not self.value:
            # 敏感變量不應該有空值
            if self.required:
                raise ValueError(f"Sensitive required variable {self.name} cannot be empty")


@dataclass
class EnvironmentConfig:
    """環境配置"""
    name: str
    environment: Environment
    variables: Dict[str, EnvironmentVariable] = field(default_factory=dict)
    config_overrides: Dict[str, Any] = field(default_factory=dict)
    enabled_features: List[str] = field(default_factory=list)
    disabled_features: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_variable(self, variable: EnvironmentVariable) -> None:
        """添加環境變量
        
        Args:
            variable: 環境變量
        """
        self.variables[variable.name] = variable
    
    def get_variable(self, name: str) -> Optional[EnvironmentVariable]:
        """獲取環境變量
        
        Args:
            name: 變量名
            
        Returns:
            Optional[EnvironmentVariable]: 環境變量
        """
        return self.variables.get(name)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """檢查功能是否啟用
        
        Args:
            feature: 功能名
            
        Returns:
            bool: 是否啟用
        """
        if feature in self.disabled_features:
            return False
        return feature in self.enabled_features


class SecretManager:
    """密鑰管理器
    
    提供密鑰的加密存儲和安全訪問。
    """
    
    def __init__(self, 
                 secrets_file: Union[str, Path] = ".secrets",
                 master_key: Optional[str] = None,
                 auto_generate_key: bool = True):
        self.secrets_file = Path(secrets_file)
        self.logger = logger.bind(component="SecretManager")
        
        # 加密密鑰
        self._fernet = None
        self._master_key = master_key
        self._auto_generate_key = auto_generate_key
        
        # 密鑰存儲
        self._secrets: Dict[str, str] = {}
        self._encrypted_secrets: Dict[str, str] = {}
        
        # 線程鎖
        self._lock = threading.RLock()
        
        # 初始化
        self._init_encryption()
        self._load_secrets()
    
    def _init_encryption(self) -> None:
        """初始化加密"""
        if self._master_key:
            # 使用提供的主密鑰
            key = self._derive_key(self._master_key.encode())
        else:
            # 嘗試從環境變量獲取
            env_key = os.getenv('CRAWLER_ENGINE_MASTER_KEY')
            if env_key:
                key = self._derive_key(env_key.encode())
            elif self._auto_generate_key:
                # 自動生成密鑰
                key = Fernet.generate_key()
                self.logger.warning(
                    "自動生成加密密鑰",
                    message="建議設置CRAWLER_ENGINE_MASTER_KEY環境變量"
                )
            else:
                self.logger.warning("未設置加密密鑰，密鑰將以明文存儲")
                return
        
        self._fernet = Fernet(key)
    
    def _derive_key(self, password: bytes) -> bytes:
        """從密碼派生密鑰"""
        salt = b'crawler_engine_salt'  # 在生產環境中應該使用隨機鹽
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def _load_secrets(self) -> None:
        """加載密鑰"""
        if not self.secrets_file.exists():
            return
        
        try:
            with open(self.secrets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._encrypted_secrets = data.get('encrypted', {})
            
            # 解密密鑰
            if self._fernet:
                for name, encrypted_value in self._encrypted_secrets.items():
                    try:
                        decrypted_value = self._fernet.decrypt(encrypted_value.encode()).decode()
                        self._secrets[name] = decrypted_value
                    except Exception as e:
                        self.logger.error(
                            "解密密鑰失敗",
                            name=name,
                            error=str(e)
                        )
            else:
                # 明文存儲（不推薦）
                self._secrets = data.get('plain', {})
            
            self.logger.info(
                "密鑰加載完成",
                count=len(self._secrets)
            )
            
        except Exception as e:
            self.logger.error(
                "加載密鑰文件失敗",
                file=str(self.secrets_file),
                error=str(e)
            )
    
    def _save_secrets(self) -> None:
        """保存密鑰"""
        try:
            # 確保目錄存在
            self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            
            if self._fernet:
                # 加密存儲
                encrypted = {}
                for name, value in self._secrets.items():
                    encrypted_value = self._fernet.encrypt(value.encode()).decode()
                    encrypted[name] = encrypted_value
                
                data['encrypted'] = encrypted
                self._encrypted_secrets = encrypted
            else:
                # 明文存儲（不推薦）
                data['plain'] = self._secrets
            
            with open(self.secrets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # 設置文件權限（僅所有者可讀寫）
            if os.name != 'nt':  # Unix系統
                os.chmod(self.secrets_file, 0o600)
            
            self.logger.debug(
                "密鑰保存完成",
                count=len(self._secrets)
            )
            
        except Exception as e:
            self.logger.error(
                "保存密鑰文件失敗",
                file=str(self.secrets_file),
                error=str(e)
            )
    
    def set_secret(self, name: str, value: str) -> None:
        """設置密鑰
        
        Args:
            name: 密鑰名
            value: 密鑰值
        """
        with self._lock:
            self._secrets[name] = value
            self._save_secrets()
        
        self.logger.info(
            "設置密鑰",
            name=name
        )
    
    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """獲取密鑰
        
        Args:
            name: 密鑰名
            default: 默認值
            
        Returns:
            Optional[str]: 密鑰值
        """
        with self._lock:
            return self._secrets.get(name, default)
    
    def has_secret(self, name: str) -> bool:
        """檢查密鑰是否存在
        
        Args:
            name: 密鑰名
            
        Returns:
            bool: 是否存在
        """
        with self._lock:
            return name in self._secrets
    
    def delete_secret(self, name: str) -> bool:
        """刪除密鑰
        
        Args:
            name: 密鑰名
            
        Returns:
            bool: 是否成功刪除
        """
        with self._lock:
            if name in self._secrets:
                del self._secrets[name]
                self._save_secrets()
                
                self.logger.info(
                    "刪除密鑰",
                    name=name
                )
                return True
            
            return False
    
    def list_secrets(self) -> List[str]:
        """列出所有密鑰名
        
        Returns:
            List[str]: 密鑰名列表
        """
        with self._lock:
            return list(self._secrets.keys())
    
    def rotate_encryption_key(self, new_master_key: str) -> None:
        """輪換加密密鑰
        
        Args:
            new_master_key: 新的主密鑰
        """
        with self._lock:
            # 使用新密鑰創建新的Fernet實例
            new_key = self._derive_key(new_master_key.encode())
            new_fernet = Fernet(new_key)
            
            # 重新加密所有密鑰
            old_secrets = self._secrets.copy()
            self._fernet = new_fernet
            self._master_key = new_master_key
            
            # 保存重新加密的密鑰
            self._save_secrets()
            
            self.logger.info(
                "加密密鑰輪換完成",
                count=len(old_secrets)
            )


class EnvironmentManager:
    """環境管理器
    
    管理不同環境的配置、變量和密鑰。
    """
    
    def __init__(self, 
                 default_env: Environment = Environment.DEVELOPMENT,
                 env_file: Union[str, Path] = ".env",
                 auto_detect: bool = True):
        self.default_env = default_env
        self.env_file = Path(env_file)
        self.auto_detect = auto_detect
        self.logger = logger.bind(component="EnvironmentManager")
        
        # 環境配置
        self._environments: Dict[str, EnvironmentConfig] = {}
        self._current_env: Optional[Environment] = None
        
        # 密鑰管理器
        self._secret_manager: Optional[SecretManager] = None
        
        # 線程鎖
        self._lock = threading.RLock()
        
        # 初始化
        self._init_environments()
        self._detect_current_environment()
    
    def _init_environments(self) -> None:
        """初始化環境配置"""
        # 創建默認環境配置
        for env in Environment:
            config = EnvironmentConfig(
                name=env.value,
                environment=env
            )
            self._environments[env.value] = config
        
        # 加載環境文件
        self._load_env_file()
    
    def _detect_current_environment(self) -> None:
        """檢測當前環境"""
        if self.auto_detect:
            # 從環境變量檢測
            env_name = os.getenv('ENVIRONMENT') or os.getenv('ENV') or os.getenv('NODE_ENV')
            
            if env_name:
                try:
                    self._current_env = Environment(env_name.lower())
                    self.logger.info(
                        "檢測到環境",
                        environment=self._current_env.value
                    )
                except ValueError:
                    self.logger.warning(
                        "未知環境類型",
                        environment=env_name,
                        default=self.default_env.value
                    )
                    self._current_env = self.default_env
            else:
                self._current_env = self.default_env
        else:
            self._current_env = self.default_env
    
    def _load_env_file(self) -> None:
        """加載環境文件"""
        if not self.env_file.exists():
            return
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 跳過空行和註釋
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析變量
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # 設置環境變量
                        os.environ[key] = value
                        
                        # 添加到當前環境配置
                        if self._current_env:
                            env_config = self._environments[self._current_env.value]
                            variable = EnvironmentVariable(
                                name=key,
                                value=value,
                                description=f"Loaded from {self.env_file}"
                            )
                            env_config.add_variable(variable)
            
            self.logger.info(
                "環境文件加載完成",
                file=str(self.env_file)
            )
            
        except Exception as e:
            self.logger.error(
                "加載環境文件失敗",
                file=str(self.env_file),
                error=str(e)
            )
    
    def set_current_environment(self, environment: Environment) -> None:
        """設置當前環境
        
        Args:
            environment: 環境類型
        """
        with self._lock:
            self._current_env = environment
            
            self.logger.info(
                "切換環境",
                environment=environment.value
            )
    
    def get_current_environment(self) -> Optional[Environment]:
        """獲取當前環境
        
        Returns:
            Optional[Environment]: 當前環境
        """
        return self._current_env
    
    def register_environment(self, config: EnvironmentConfig) -> None:
        """註冊環境配置
        
        Args:
            config: 環境配置
        """
        with self._lock:
            self._environments[config.name] = config
            
            self.logger.info(
                "註冊環境配置",
                name=config.name,
                environment=config.environment.value,
                variables=len(config.variables)
            )
    
    def get_environment_config(self, name: Optional[str] = None) -> Optional[EnvironmentConfig]:
        """獲取環境配置
        
        Args:
            name: 環境名稱，如果為None則返回當前環境
            
        Returns:
            Optional[EnvironmentConfig]: 環境配置
        """
        if name is None:
            if self._current_env:
                name = self._current_env.value
            else:
                return None
        
        return self._environments.get(name)
    
    def add_variable(self, 
                    variable: EnvironmentVariable,
                    environment: Optional[str] = None) -> None:
        """添加環境變量
        
        Args:
            variable: 環境變量
            environment: 環境名稱，如果為None則添加到當前環境
        """
        env_config = self.get_environment_config(environment)
        if env_config:
            env_config.add_variable(variable)
            
            # 如果是當前環境，同時設置到系統環境變量
            if environment is None or environment == self._current_env.value:
                os.environ[variable.name] = variable.value
            
            self.logger.debug(
                "添加環境變量",
                name=variable.name,
                environment=env_config.name,
                sensitive=variable.sensitive
            )
    
    def get_variable(self, 
                    name: str,
                    environment: Optional[str] = None,
                    default: Optional[str] = None) -> Optional[str]:
        """獲取環境變量
        
        Args:
            name: 變量名
            environment: 環境名稱
            default: 默認值
            
        Returns:
            Optional[str]: 變量值
        """
        # 首先從系統環境變量獲取
        value = os.getenv(name)
        if value is not None:
            return value
        
        # 從環境配置獲取
        env_config = self.get_environment_config(environment)
        if env_config:
            variable = env_config.get_variable(name)
            if variable:
                return variable.value
        
        return default
    
    def set_variable(self, 
                    name: str,
                    value: str,
                    environment: Optional[str] = None,
                    **kwargs) -> None:
        """設置環境變量
        
        Args:
            name: 變量名
            value: 變量值
            environment: 環境名稱
            **kwargs: 其他變量屬性
        """
        variable = EnvironmentVariable(
            name=name,
            value=value,
            **kwargs
        )
        
        self.add_variable(variable, environment)
    
    def enable_secret_management(self, 
                               secrets_file: Union[str, Path] = ".secrets",
                               master_key: Optional[str] = None) -> None:
        """啟用密鑰管理
        
        Args:
            secrets_file: 密鑰文件路徑
            master_key: 主密鑰
        """
        self._secret_manager = SecretManager(
            secrets_file=secrets_file,
            master_key=master_key
        )
        
        self.logger.info(
            "密鑰管理已啟用",
            secrets_file=str(secrets_file)
        )
    
    def get_secret_manager(self) -> Optional[SecretManager]:
        """獲取密鑰管理器
        
        Returns:
            Optional[SecretManager]: 密鑰管理器
        """
        return self._secret_manager
    
    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """獲取密鑰
        
        Args:
            name: 密鑰名
            default: 默認值
            
        Returns:
            Optional[str]: 密鑰值
        """
        if self._secret_manager:
            return self._secret_manager.get_secret(name, default)
        
        # 回退到環境變量
        return self.get_variable(name, default=default)
    
    def set_secret(self, name: str, value: str) -> None:
        """設置密鑰
        
        Args:
            name: 密鑰名
            value: 密鑰值
        """
        if self._secret_manager:
            self._secret_manager.set_secret(name, value)
        else:
            # 回退到環境變量
            self.set_variable(name, value, sensitive=True)
    
    def validate_environment(self, environment: Optional[str] = None) -> List[str]:
        """驗證環境配置
        
        Args:
            environment: 環境名稱
            
        Returns:
            List[str]: 錯誤列表
        """
        errors = []
        env_config = self.get_environment_config(environment)
        
        if not env_config:
            errors.append(f"Environment config not found: {environment}")
            return errors
        
        # 檢查必需變量
        for variable in env_config.variables.values():
            if variable.required:
                value = self.get_variable(variable.name, environment)
                if not value:
                    errors.append(f"Required variable {variable.name} is missing")
                
                # 驗證模式
                if variable.validation_pattern and value:
                    import re
                    if not re.match(variable.validation_pattern, value):
                        errors.append(
                            f"Variable {variable.name} does not match pattern {variable.validation_pattern}"
                        )
        
        return errors
    
    def export_environment(self, 
                          environment: Optional[str] = None,
                          include_sensitive: bool = False) -> Dict[str, str]:
        """導出環境變量
        
        Args:
            environment: 環境名稱
            include_sensitive: 是否包含敏感變量
            
        Returns:
            Dict[str, str]: 環境變量字典
        """
        result = {}
        env_config = self.get_environment_config(environment)
        
        if env_config:
            for variable in env_config.variables.values():
                if variable.sensitive and not include_sensitive:
                    continue
                
                result[variable.name] = variable.value
        
        return result
    
    def save_to_file(self, 
                    file_path: Union[str, Path],
                    environment: Optional[str] = None,
                    include_sensitive: bool = False) -> None:
        """保存環境變量到文件
        
        Args:
            file_path: 文件路徑
            environment: 環境名稱
            include_sensitive: 是否包含敏感變量
        """
        file_path = Path(file_path)
        variables = self.export_environment(environment, include_sensitive)
        
        # 確保目錄存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Environment: {environment or 'current'}\n")
            f.write(f"# Generated at: {datetime.utcnow().isoformat()}\n\n")
            
            for name, value in sorted(variables.items()):
                f.write(f"{name}={value}\n")
        
        # 設置文件權限
        if os.name != 'nt':  # Unix系統
            os.chmod(file_path, 0o600)
        
        self.logger.info(
            "環境變量導出完成",
            file=str(file_path),
            environment=environment,
            count=len(variables)
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = {
            'current_environment': self._current_env.value if self._current_env else None,
            'total_environments': len(self._environments),
            'secret_manager_enabled': self._secret_manager is not None,
            'environments': {}
        }
        
        for name, config in self._environments.items():
            stats['environments'][name] = {
                'variables_count': len(config.variables),
                'sensitive_variables': sum(
                    1 for v in config.variables.values() if v.sensitive
                ),
                'required_variables': sum(
                    1 for v in config.variables.values() if v.required
                ),
                'enabled_features': len(config.enabled_features),
                'disabled_features': len(config.disabled_features)
            }
        
        if self._secret_manager:
            stats['secrets_count'] = len(self._secret_manager.list_secrets())
        
        return stats