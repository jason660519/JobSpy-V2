"""配置設置類

定義各個模組的配置結構、默認值和設置管理。
"""

import os
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


class LogLevel(Enum):
    """日誌級別"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheBackend(Enum):
    """緩存後端"""
    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"
    HYBRID = "hybrid"


class DatabaseType(Enum):
    """數據庫類型"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class StorageBackend(Enum):
    """存儲後端"""
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"


@dataclass
class DatabaseSettings:
    """數據庫配置"""
    # 基本配置
    type: DatabaseType = DatabaseType.SQLITE
    url: str = "sqlite:///crawler_engine.db"
    host: str = "localhost"
    port: int = 5432
    database: str = "crawler_engine"
    username: str = ""
    password: str = ""
    
    # 連接池配置
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # 查詢配置
    query_timeout: int = 30
    statement_timeout: int = 60
    
    # SSL配置
    ssl_enabled: bool = False
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    ssl_ca_path: str = ""
    
    # 其他配置
    echo: bool = False
    autocommit: bool = False
    autoflush: bool = True
    
    def get_connection_url(self) -> str:
        """獲取數據庫連接URL
        
        Returns:
            str: 連接URL
        """
        if self.url and self.url != "sqlite:///crawler_engine.db":
            return self.url
        
        if self.type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"
        elif self.type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.MYSQL:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.MONGODB:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return self.url


@dataclass
class APISettings:
    """API配置"""
    # OpenAI配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4-vision-preview"
    openai_timeout: int = 60
    openai_max_retries: int = 3
    
    # 其他AI服務
    anthropic_api_key: str = ""
    google_api_key: str = ""
    azure_api_key: str = ""
    
    # 代理配置
    proxy_enabled: bool = False
    proxy_url: str = ""
    proxy_username: str = ""
    proxy_password: str = ""
    
    # 速率限制
    rate_limit_enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # 重試配置
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    
    # 超時配置
    connect_timeout: int = 10
    read_timeout: int = 60
    total_timeout: int = 120


@dataclass
class CrawlerSettings:
    """爬蟲配置"""
    # 並發配置
    max_concurrent: int = 5
    max_concurrent_per_domain: int = 2
    
    # 延遲配置
    delay: float = 1.0
    random_delay: bool = True
    delay_range: tuple = (0.5, 2.0)
    
    # 重試配置
    max_retries: int = 3
    retry_delay: float = 2.0
    retry_backoff: float = 2.0
    
    # 超時配置
    page_timeout: int = 30
    navigation_timeout: int = 30
    element_timeout: int = 10
    
    # 瀏覽器配置
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # 反檢測配置
    stealth_mode: bool = True
    disable_images: bool = False
    disable_javascript: bool = False
    disable_css: bool = False
    
    # 代理配置
    proxy_enabled: bool = False
    proxy_rotation: bool = False
    proxy_list: List[str] = field(default_factory=list)
    
    # 存儲配置
    screenshot_enabled: bool = False
    screenshot_path: str = "screenshots"
    save_html: bool = False
    html_path: str = "html"
    
    # 過濾配置
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    blocked_resources: List[str] = field(default_factory=lambda: ["image", "font", "media"])


@dataclass
class MonitoringSettings:
    """監控配置"""
    # 基本配置
    enabled: bool = True
    check_interval: int = 60  # 秒
    
    # 成本控制
    cost_control_enabled: bool = True
    daily_cost_limit: float = 100.0
    monthly_cost_limit: float = 1000.0
    
    # 性能監控
    performance_monitoring: bool = True
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    disk_threshold: float = 90.0
    
    # 健康檢查
    health_check_enabled: bool = True
    health_check_interval: int = 30
    health_check_timeout: int = 10
    
    # 告警配置
    alert_enabled: bool = True
    alert_cooldown: int = 300  # 5分鐘
    email_alerts: bool = False
    webhook_alerts: bool = False
    
    # 指標收集
    metrics_enabled: bool = True
    metrics_retention_days: int = 30
    metrics_batch_size: int = 100


@dataclass
class LoggingSettings:
    """日誌配置"""
    # 基本配置
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 文件配置
    file_enabled: bool = True
    file_path: str = "logs/crawler_engine.log"
    file_max_size: int = 10 * 1024 * 1024  # 10MB
    file_backup_count: int = 5
    
    # 控制台配置
    console_enabled: bool = True
    console_level: LogLevel = LogLevel.INFO
    
    # 結構化日誌
    structured_logging: bool = True
    json_format: bool = False
    
    # 過濾配置
    ignored_loggers: List[str] = field(default_factory=lambda: ["urllib3", "requests"])
    
    # 遠程日誌
    remote_logging: bool = False
    remote_url: str = ""
    remote_api_key: str = ""


@dataclass
class CacheSettings:
    """緩存配置"""
    # 基本配置
    enabled: bool = True
    backend: CacheBackend = CacheBackend.MEMORY
    
    # 內存緩存
    memory_max_size: int = 1000
    memory_ttl: int = 3600  # 1小時
    
    # 文件緩存
    file_cache_dir: str = "cache"
    file_max_size: int = 100 * 1024 * 1024  # 100MB
    file_ttl: int = 86400  # 24小時
    
    # Redis緩存
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str = ""
    redis_ttl: int = 3600
    
    # 緩存策略
    eviction_policy: str = "lru"  # lru, lfu, fifo
    compression_enabled: bool = False
    
    # 預熱配置
    preload_enabled: bool = False
    preload_keys: List[str] = field(default_factory=list)


@dataclass
class SecuritySettings:
    """安全配置"""
    # 加密配置
    encryption_enabled: bool = True
    encryption_key: str = ""
    
    # API安全
    api_key_required: bool = True
    api_key_header: str = "X-API-Key"
    
    # 速率限制
    rate_limiting: bool = True
    max_requests_per_minute: int = 100
    
    # IP白名單
    ip_whitelist_enabled: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    
    # 數據脫敏
    data_masking: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: ["password", "token", "key"])
    
    # 審計日誌
    audit_logging: bool = True
    audit_log_path: str = "logs/audit.log"


@dataclass
class StorageSettings:
    """存儲配置"""
    # 基本配置
    backend: StorageBackend = StorageBackend.LOCAL
    
    # 本地存儲
    local_base_path: str = "data"
    local_max_size: int = 1024 * 1024 * 1024  # 1GB
    
    # AWS S3
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    
    # Google Cloud Storage
    gcs_bucket: str = ""
    gcs_project_id: str = ""
    gcs_credentials_path: str = ""
    
    # Azure Blob Storage
    azure_account_name: str = ""
    azure_account_key: str = ""
    azure_container: str = ""
    
    # 壓縮配置
    compression_enabled: bool = True
    compression_level: int = 6
    
    # 備份配置
    backup_enabled: bool = False
    backup_interval: int = 86400  # 24小時
    backup_retention: int = 7  # 7天


@dataclass
class AppSettings:
    """應用程序主配置"""
    # 基本信息
    name: str = "Crawler Engine"
    version: str = "1.0.0"
    description: str = "Advanced web crawling and data extraction engine"
    
    # 運行環境
    environment: str = "development"
    debug: bool = False
    testing: bool = False
    
    # 服務配置
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    
    # 路徑配置
    base_dir: str = field(default_factory=lambda: str(Path.cwd()))
    data_dir: str = "data"
    logs_dir: str = "logs"
    cache_dir: str = "cache"
    temp_dir: str = "temp"
    
    # 功能開關
    features: Dict[str, bool] = field(default_factory=lambda: {
        "ai_vision": True,
        "smart_scraping": True,
        "cost_control": True,
        "monitoring": True,
        "caching": True,
        "rate_limiting": True
    })
    
    # 子配置
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    api: APISettings = field(default_factory=APISettings)
    crawler: CrawlerSettings = field(default_factory=CrawlerSettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    storage: StorageSettings = field(default_factory=StorageSettings)
    
    def __post_init__(self):
        """初始化後處理"""
        # 確保目錄存在
        self._ensure_directories()
        
        # 從環境變量覆蓋配置
        self._load_from_env()
    
    def _ensure_directories(self) -> None:
        """確保必要的目錄存在"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.cache_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _load_from_env(self) -> None:
        """從環境變量加載配置"""
        # 基本配置
        self.environment = os.getenv('ENVIRONMENT', self.environment)
        self.debug = os.getenv('DEBUG', str(self.debug)).lower() == 'true'
        self.host = os.getenv('HOST', self.host)
        self.port = int(os.getenv('PORT', str(self.port)))
        
        # 數據庫配置
        if os.getenv('DATABASE_URL'):
            self.database.url = os.getenv('DATABASE_URL')
        
        # API配置
        if os.getenv('OPENAI_API_KEY'):
            self.api.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # 其他敏感配置
        env_mappings = {
            'DATABASE_PASSWORD': lambda x: setattr(self.database, 'password', x),
            'REDIS_URL': lambda x: setattr(self.cache, 'redis_url', x),
            'ENCRYPTION_KEY': lambda x: setattr(self.security, 'encryption_key', x),
        }
        
        for env_var, setter in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                setter(value)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """檢查功能是否啟用
        
        Args:
            feature: 功能名稱
            
        Returns:
            bool: 是否啟用
        """
        return self.features.get(feature, False)
    
    def enable_feature(self, feature: str) -> None:
        """啟用功能
        
        Args:
            feature: 功能名稱
        """
        self.features[feature] = True
    
    def disable_feature(self, feature: str) -> None:
        """禁用功能
        
        Args:
            feature: 功能名稱
        """
        self.features[feature] = False
    
    def get_data_path(self, *paths: str) -> Path:
        """獲取數據目錄路徑
        
        Args:
            *paths: 路徑組件
            
        Returns:
            Path: 完整路徑
        """
        return Path(self.data_dir) / Path(*paths)
    
    def get_logs_path(self, *paths: str) -> Path:
        """獲取日誌目錄路徑
        
        Args:
            *paths: 路徑組件
            
        Returns:
            Path: 完整路徑
        """
        return Path(self.logs_dir) / Path(*paths)
    
    def get_cache_path(self, *paths: str) -> Path:
        """獲取緩存目錄路徑
        
        Args:
            *paths: 路徑組件
            
        Returns:
            Path: 完整路徑
        """
        return Path(self.cache_dir) / Path(*paths)
    
    def get_temp_path(self, *paths: str) -> Path:
        """獲取臨時目錄路徑
        
        Args:
            *paths: 路徑組件
            
        Returns:
            Path: 完整路徑
        """
        return Path(self.temp_dir) / Path(*paths)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        from dataclasses import asdict
        return asdict(self)
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """從字典更新配置
        
        Args:
            data: 配置數據
        """
        for key, value in data.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), (DatabaseSettings, APISettings, 
                                                  CrawlerSettings, MonitoringSettings,
                                                  LoggingSettings, CacheSettings,
                                                  SecuritySettings, StorageSettings)):
                    # 更新子配置
                    if isinstance(value, dict):
                        sub_config = getattr(self, key)
                        for sub_key, sub_value in value.items():
                            if hasattr(sub_config, sub_key):
                                setattr(sub_config, sub_key, sub_value)
                else:
                    setattr(self, key, value)
    
    def validate(self) -> List[str]:
        """驗證配置
        
        Returns:
            List[str]: 錯誤列表
        """
        errors = []
        
        # 檢查必需的API密鑰
        if self.is_feature_enabled('ai_vision') and not self.api.openai_api_key:
            errors.append("OpenAI API key is required when AI vision is enabled")
        
        # 檢查數據庫配置
        if not self.database.url:
            errors.append("Database URL is required")
        
        # 檢查端口範圍
        if not (1 <= self.port <= 65535):
            errors.append(f"Invalid port number: {self.port}")
        
        # 檢查目錄權限
        for directory in [self.data_dir, self.logs_dir, self.cache_dir, self.temp_dir]:
            path = Path(directory)
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    errors.append(f"Cannot create directory: {directory}")
        
        return errors
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取配置摘要
        
        Returns:
            Dict[str, Any]: 配置摘要
        """
        return {
            'name': self.name,
            'version': self.version,
            'environment': self.environment,
            'debug': self.debug,
            'host': self.host,
            'port': self.port,
            'features': self.features,
            'database_type': self.database.type.value,
            'cache_backend': self.cache.backend.value,
            'storage_backend': self.storage.backend.value,
            'monitoring_enabled': self.monitoring.enabled,
            'security_enabled': self.security.encryption_enabled
        }


# 默認配置實例
default_settings = AppSettings()


def get_settings() -> AppSettings:
    """獲取應用程序設置
    
    Returns:
        AppSettings: 應用程序設置
    """
    return default_settings


def load_settings_from_file(file_path: Union[str, Path]) -> AppSettings:
    """從文件加載設置
    
    Args:
        file_path: 配置文件路徑
        
    Returns:
        AppSettings: 應用程序設置
    """
    import json
    import yaml
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")
        
        settings = AppSettings()
        settings.update_from_dict(data)
        
        logger.info(
            "配置文件加載完成",
            file=str(file_path),
            environment=settings.environment
        )
        
        return settings
        
    except Exception as e:
        logger.error(
            "配置文件加載失敗",
            file=str(file_path),
            error=str(e)
        )
        raise


def save_settings_to_file(settings: AppSettings, file_path: Union[str, Path]) -> None:
    """保存設置到文件
    
    Args:
        settings: 應用程序設置
        file_path: 配置文件路徑
    """
    import json
    import yaml
    
    file_path = Path(file_path)
    
    # 確保目錄存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = settings.to_dict()
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            elif file_path.suffix.lower() == '.json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")
        
        logger.info(
            "配置文件保存完成",
            file=str(file_path)
        )
        
    except Exception as e:
        logger.error(
            "配置文件保存失敗",
            file=str(file_path),
            error=str(e)
        )
        raise