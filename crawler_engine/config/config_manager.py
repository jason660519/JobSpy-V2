"""配置管理器

提供統一的配置加載、驗證、監控和管理功能。
"""

import os
import json
import yaml
import toml
import configparser
from typing import Dict, Any, Optional, List, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import time
from datetime import datetime
import structlog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import copy
import hashlib

logger = structlog.get_logger(__name__)


class ConfigFormat(Enum):
    """配置格式"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"


class ConfigSource(Enum):
    """配置來源"""
    FILE = "file"
    ENVIRONMENT = "environment"
    COMMAND_LINE = "command_line"
    DATABASE = "database"
    REMOTE = "remote"
    DEFAULT = "default"


class ConfigValidationError(Exception):
    """配置驗證錯誤"""
    pass


class ConfigNotFoundError(Exception):
    """配置未找到錯誤"""
    pass


@dataclass
class ConfigValue:
    """配置值"""
    value: Any
    source: ConfigSource
    path: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.value, dict):
            # 遞歸處理嵌套字典
            self.value = {k: v for k, v in self.value.items()}


@dataclass
class ConfigSchema:
    """配置模式"""
    required_keys: List[str] = field(default_factory=list)
    optional_keys: List[str] = field(default_factory=list)
    key_types: Dict[str, Type] = field(default_factory=dict)
    validators: Dict[str, Callable[[Any], bool]] = field(default_factory=dict)
    default_values: Dict[str, Any] = field(default_factory=dict)
    nested_schemas: Dict[str, 'ConfigSchema'] = field(default_factory=dict)
    
    def validate(self, config: Dict[str, Any], path: str = "") -> List[str]:
        """驗證配置
        
        Args:
            config: 配置字典
            path: 當前路徑
            
        Returns:
            List[str]: 錯誤列表
        """
        errors = []
        
        # 檢查必需鍵
        for key in self.required_keys:
            if key not in config:
                errors.append(f"{path}.{key} is required" if path else f"{key} is required")
        
        # 檢查類型和驗證器
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            # 類型檢查
            if key in self.key_types:
                expected_type = self.key_types[key]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"{current_path} should be {expected_type.__name__}, got {type(value).__name__}"
                    )
            
            # 自定義驗證器
            if key in self.validators:
                validator = self.validators[key]
                try:
                    if not validator(value):
                        errors.append(f"{current_path} failed validation")
                except Exception as e:
                    errors.append(f"{current_path} validation error: {str(e)}")
            
            # 嵌套模式驗證
            if key in self.nested_schemas and isinstance(value, dict):
                nested_errors = self.nested_schemas[key].validate(value, current_path)
                errors.extend(nested_errors)
        
        return errors


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件監控處理器"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.logger = logger.bind(component="ConfigFileHandler")
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path in self.config_manager._watched_files:
                self.logger.info(
                    "配置文件已修改",
                    file_path=str(file_path)
                )
                self.config_manager._reload_config(file_path)


class ConfigWatcher:
    """配置文件監控器"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.observer = Observer()
        self.handler = ConfigFileHandler(config_manager)
        self.watching = False
        self.logger = logger.bind(component="ConfigWatcher")
    
    def start_watching(self, paths: List[Path]) -> None:
        """開始監控
        
        Args:
            paths: 要監控的路徑列表
        """
        if self.watching:
            return
        
        # 監控目錄
        watched_dirs = set()
        for path in paths:
            if path.exists():
                watch_dir = path.parent if path.is_file() else path
                if watch_dir not in watched_dirs:
                    self.observer.schedule(self.handler, str(watch_dir), recursive=False)
                    watched_dirs.add(watch_dir)
        
        if watched_dirs:
            self.observer.start()
            self.watching = True
            
            self.logger.info(
                "配置文件監控已啟動",
                watched_dirs=len(watched_dirs)
            )
    
    def stop_watching(self) -> None:
        """停止監控"""
        if self.watching:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            
            self.logger.info("配置文件監控已停止")


class ConfigManager:
    """配置管理器
    
    提供統一的配置加載、驗證、監控和管理功能。
    """
    
    def __init__(self, 
                 auto_reload: bool = True,
                 watch_interval: int = 5,
                 validation_enabled: bool = True,
                 cache_enabled: bool = True):
        self.auto_reload = auto_reload
        self.watch_interval = watch_interval
        self.validation_enabled = validation_enabled
        self.cache_enabled = cache_enabled
        self.logger = logger.bind(component="ConfigManager")
        
        # 配置存儲
        self._config: Dict[str, ConfigValue] = {}
        self._schemas: Dict[str, ConfigSchema] = {}
        self._watchers: Dict[str, ConfigWatcher] = {}
        self._watched_files: Set[Path] = set()
        
        # 緩存
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = 300  # 5分鐘
        
        # 回調函數
        self._change_callbacks: List[Callable[[str, Any, Any], None]] = []
        
        # 線程鎖
        self._lock = threading.RLock()
        
        # 備份
        self._backups: Dict[str, List[Dict[str, Any]]] = {}
        self._max_backups = 10
    
    def register_schema(self, name: str, schema: ConfigSchema) -> None:
        """註冊配置模式
        
        Args:
            name: 模式名稱
            schema: 配置模式
        """
        with self._lock:
            self._schemas[name] = schema
            
            self.logger.info(
                "註冊配置模式",
                name=name,
                required_keys=len(schema.required_keys),
                optional_keys=len(schema.optional_keys)
            )
    
    def add_change_callback(self, callback: Callable[[str, Any, Any], None]) -> None:
        """添加配置變更回調
        
        Args:
            callback: 回調函數 (key, old_value, new_value)
        """
        self._change_callbacks.append(callback)
    
    def load_from_file(self, 
                      file_path: Union[str, Path],
                      format_type: Optional[ConfigFormat] = None,
                      namespace: str = "",
                      watch: bool = True) -> None:
        """從文件加載配置
        
        Args:
            file_path: 文件路徑
            format_type: 格式類型，如果為None則自動檢測
            namespace: 命名空間
            watch: 是否監控文件變化
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigNotFoundError(f"Config file not found: {file_path}")
        
        # 自動檢測格式
        if format_type is None:
            format_type = self._detect_format(file_path)
        
        # 加載配置
        config_data = self._load_file(file_path, format_type)
        
        # 存儲配置
        self._store_config(config_data, ConfigSource.FILE, str(file_path), namespace)
        
        # 監控文件
        if watch and self.auto_reload:
            self._watch_file(file_path)
        
        self.logger.info(
            "從文件加載配置",
            file_path=str(file_path),
            format=format_type.value,
            namespace=namespace,
            keys=len(config_data) if isinstance(config_data, dict) else 1
        )
    
    def load_from_env(self, 
                     prefix: str = "",
                     namespace: str = "") -> None:
        """從環境變量加載配置
        
        Args:
            prefix: 環境變量前綴
            namespace: 命名空間
        """
        config_data = {}
        
        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue
            
            # 移除前綴
            config_key = key[len(prefix):] if prefix else key
            config_key = config_key.lower()
            
            # 嘗試轉換類型
            config_data[config_key] = self._convert_env_value(value)
        
        # 存儲配置
        self._store_config(config_data, ConfigSource.ENVIRONMENT, "environment", namespace)
        
        self.logger.info(
            "從環境變量加載配置",
            prefix=prefix,
            namespace=namespace,
            keys=len(config_data)
        )
    
    def load_from_dict(self, 
                      config_data: Dict[str, Any],
                      source: ConfigSource = ConfigSource.DEFAULT,
                      namespace: str = "") -> None:
        """從字典加載配置
        
        Args:
            config_data: 配置數據
            source: 配置來源
            namespace: 命名空間
        """
        self._store_config(config_data, source, "dict", namespace)
        
        self.logger.info(
            "從字典加載配置",
            source=source.value,
            namespace=namespace,
            keys=len(config_data)
        )
    
    def get(self, 
           key: str,
           default: Any = None,
           namespace: str = "",
           use_cache: bool = True) -> Any:
        """獲取配置值
        
        Args:
            key: 配置鍵
            default: 默認值
            namespace: 命名空間
            use_cache: 是否使用緩存
            
        Returns:
            Any: 配置值
        """
        full_key = f"{namespace}.{key}" if namespace else key
        
        # 檢查緩存
        if use_cache and self.cache_enabled:
            cached_value = self._get_from_cache(full_key)
            if cached_value is not None:
                return cached_value
        
        with self._lock:
            # 直接查找
            if full_key in self._config:
                value = self._config[full_key].value
                if use_cache and self.cache_enabled:
                    self._set_cache(full_key, value)
                return value
            
            # 嵌套查找
            value = self._get_nested_value(key, namespace)
            if value is not None:
                if use_cache and self.cache_enabled:
                    self._set_cache(full_key, value)
                return value
            
            return default
    
    def set(self, 
           key: str,
           value: Any,
           namespace: str = "",
           source: ConfigSource = ConfigSource.DEFAULT) -> None:
        """設置配置值
        
        Args:
            key: 配置鍵
            value: 配置值
            namespace: 命名空間
            source: 配置來源
        """
        full_key = f"{namespace}.{key}" if namespace else key
        
        with self._lock:
            # 獲取舊值
            old_value = self.get(key, namespace=namespace)
            
            # 設置新值
            self._config[full_key] = ConfigValue(
                value=value,
                source=source,
                path=full_key
            )
            
            # 清除緩存
            self._clear_cache(full_key)
            
            # 觸發回調
            for callback in self._change_callbacks:
                try:
                    callback(full_key, old_value, value)
                except Exception as e:
                    self.logger.error(
                        "配置變更回調錯誤",
                        key=full_key,
                        error=str(e)
                    )
        
        self.logger.debug(
            "設置配置值",
            key=full_key,
            source=source.value
        )
    
    def has(self, key: str, namespace: str = "") -> bool:
        """檢查配置是否存在
        
        Args:
            key: 配置鍵
            namespace: 命名空間
            
        Returns:
            bool: 是否存在
        """
        full_key = f"{namespace}.{key}" if namespace else key
        
        with self._lock:
            if full_key in self._config:
                return True
            
            return self._get_nested_value(key, namespace) is not None
    
    def delete(self, key: str, namespace: str = "") -> bool:
        """刪除配置
        
        Args:
            key: 配置鍵
            namespace: 命名空間
            
        Returns:
            bool: 是否成功刪除
        """
        full_key = f"{namespace}.{key}" if namespace else key
        
        with self._lock:
            if full_key in self._config:
                old_value = self._config[full_key].value
                del self._config[full_key]
                
                # 清除緩存
                self._clear_cache(full_key)
                
                # 觸發回調
                for callback in self._change_callbacks:
                    try:
                        callback(full_key, old_value, None)
                    except Exception as e:
                        self.logger.error(
                            "配置刪除回調錯誤",
                            key=full_key,
                            error=str(e)
                        )
                
                self.logger.debug("刪除配置", key=full_key)
                return True
            
            return False
    
    def validate(self, schema_name: str, namespace: str = "") -> List[str]:
        """驗證配置
        
        Args:
            schema_name: 模式名稱
            namespace: 命名空間
            
        Returns:
            List[str]: 錯誤列表
        """
        if not self.validation_enabled:
            return []
        
        if schema_name not in self._schemas:
            raise ConfigValidationError(f"Schema not found: {schema_name}")
        
        schema = self._schemas[schema_name]
        config_dict = self.get_namespace(namespace)
        
        return schema.validate(config_dict, namespace)
    
    def get_namespace(self, namespace: str = "") -> Dict[str, Any]:
        """獲取命名空間下的所有配置
        
        Args:
            namespace: 命名空間
            
        Returns:
            Dict[str, Any]: 配置字典
        """
        result = {}
        prefix = f"{namespace}." if namespace else ""
        
        with self._lock:
            for key, config_value in self._config.items():
                if key.startswith(prefix):
                    # 移除命名空間前綴
                    relative_key = key[len(prefix):]
                    
                    # 處理嵌套鍵
                    self._set_nested_value(result, relative_key, config_value.value)
        
        return result
    
    def get_all(self) -> Dict[str, Any]:
        """獲取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置
        """
        result = {}
        
        with self._lock:
            for key, config_value in self._config.items():
                self._set_nested_value(result, key, config_value.value)
        
        return result
    
    def backup(self, name: str) -> None:
        """備份當前配置
        
        Args:
            name: 備份名稱
        """
        with self._lock:
            backup_data = {
                key: {
                    'value': copy.deepcopy(config_value.value),
                    'source': config_value.source.value,
                    'path': config_value.path,
                    'timestamp': config_value.timestamp.isoformat()
                }
                for key, config_value in self._config.items()
            }
            
            if name not in self._backups:
                self._backups[name] = []
            
            self._backups[name].append(backup_data)
            
            # 限制備份數量
            if len(self._backups[name]) > self._max_backups:
                self._backups[name] = self._backups[name][-self._max_backups:]
        
        self.logger.info(
            "配置備份完成",
            name=name,
            config_count=len(backup_data)
        )
    
    def restore(self, name: str, index: int = -1) -> None:
        """恢復配置
        
        Args:
            name: 備份名稱
            index: 備份索引，-1表示最新
        """
        if name not in self._backups or not self._backups[name]:
            raise ConfigNotFoundError(f"Backup not found: {name}")
        
        backup_data = self._backups[name][index]
        
        with self._lock:
            # 清除當前配置
            self._config.clear()
            self._cache.clear()
            
            # 恢復配置
            for key, data in backup_data.items():
                self._config[key] = ConfigValue(
                    value=data['value'],
                    source=ConfigSource(data['source']),
                    path=data['path'],
                    timestamp=datetime.fromisoformat(data['timestamp'])
                )
        
        self.logger.info(
            "配置恢復完成",
            name=name,
            index=index,
            config_count=len(backup_data)
        )
    
    def export_to_file(self, 
                      file_path: Union[str, Path],
                      format_type: ConfigFormat,
                      namespace: str = "") -> None:
        """導出配置到文件
        
        Args:
            file_path: 文件路徑
            format_type: 格式類型
            namespace: 命名空間
        """
        file_path = Path(file_path)
        config_data = self.get_namespace(namespace)
        
        # 確保目錄存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入文件
        self._write_file(file_path, config_data, format_type)
        
        self.logger.info(
            "配置導出完成",
            file_path=str(file_path),
            format=format_type.value,
            namespace=namespace
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        with self._lock:
            # 按來源統計
            source_counts = {}
            for config_value in self._config.values():
                source = config_value.source.value
                source_counts[source] = source_counts.get(source, 0) + 1
            
            return {
                'total_configs': len(self._config),
                'source_counts': source_counts,
                'schemas_registered': len(self._schemas),
                'watched_files': len(self._watched_files),
                'cache_size': len(self._cache),
                'backups': {name: len(backups) for name, backups in self._backups.items()},
                'change_callbacks': len(self._change_callbacks)
            }
    
    def _detect_format(self, file_path: Path) -> ConfigFormat:
        """檢測文件格式"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.json']:
            return ConfigFormat.JSON
        elif suffix in ['.yaml', '.yml']:
            return ConfigFormat.YAML
        elif suffix in ['.toml']:
            return ConfigFormat.TOML
        elif suffix in ['.ini', '.cfg']:
            return ConfigFormat.INI
        elif suffix in ['.env']:
            return ConfigFormat.ENV
        else:
            # 嘗試根據內容檢測
            try:
                content = file_path.read_text(encoding='utf-8')
                if content.strip().startswith('{'):
                    return ConfigFormat.JSON
                elif '=' in content and '[' not in content:
                    return ConfigFormat.ENV
                else:
                    return ConfigFormat.YAML  # 默認YAML
            except Exception:
                return ConfigFormat.YAML
    
    def _load_file(self, file_path: Path, format_type: ConfigFormat) -> Dict[str, Any]:
        """加載文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if format_type == ConfigFormat.JSON:
                return json.loads(content)
            elif format_type == ConfigFormat.YAML:
                return yaml.safe_load(content) or {}
            elif format_type == ConfigFormat.TOML:
                return toml.loads(content)
            elif format_type == ConfigFormat.INI:
                parser = configparser.ConfigParser()
                parser.read_string(content)
                return {section: dict(parser[section]) for section in parser.sections()}
            elif format_type == ConfigFormat.ENV:
                result = {}
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        result[key.strip()] = self._convert_env_value(value.strip())
                return result
            else:
                raise ConfigValidationError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            raise ConfigValidationError(f"Failed to load config file {file_path}: {str(e)}")
    
    def _write_file(self, file_path: Path, data: Dict[str, Any], format_type: ConfigFormat) -> None:
        """寫入文件"""
        try:
            if format_type == ConfigFormat.JSON:
                content = json.dumps(data, indent=2, ensure_ascii=False)
            elif format_type == ConfigFormat.YAML:
                content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            elif format_type == ConfigFormat.TOML:
                content = toml.dumps(data)
            elif format_type == ConfigFormat.INI:
                parser = configparser.ConfigParser()
                for section, values in data.items():
                    parser[section] = values
                content = ''
                parser.write(content)
            elif format_type == ConfigFormat.ENV:
                lines = []
                for key, value in data.items():
                    lines.append(f"{key}={value}")
                content = '\n'.join(lines)
            else:
                raise ConfigValidationError(f"Unsupported format: {format_type}")
            
            file_path.write_text(content, encoding='utf-8')
            
        except Exception as e:
            raise ConfigValidationError(f"Failed to write config file {file_path}: {str(e)}")
    
    def _convert_env_value(self, value: str) -> Any:
        """轉換環境變量值"""
        # 移除引號
        value = value.strip('"\'')
        
        # 布爾值
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # 數字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 列表（逗號分隔）
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        return value
    
    def _store_config(self, 
                     config_data: Dict[str, Any],
                     source: ConfigSource,
                     path: str,
                     namespace: str) -> None:
        """存儲配置"""
        with self._lock:
            # 扁平化配置
            flat_config = self._flatten_dict(config_data, namespace)
            
            for key, value in flat_config.items():
                self._config[key] = ConfigValue(
                    value=value,
                    source=source,
                    path=path
                )
            
            # 清除相關緩存
            self._clear_namespace_cache(namespace)
    
    def _flatten_dict(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """扁平化字典"""
        result = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                result.update(self._flatten_dict(value, full_key))
            else:
                result[full_key] = value
        
        return result
    
    def _get_nested_value(self, key: str, namespace: str) -> Any:
        """獲取嵌套值"""
        # 構建可能的鍵
        possible_keys = []
        
        if namespace:
            possible_keys.append(f"{namespace}.{key}")
        
        possible_keys.append(key)
        
        # 查找匹配的鍵
        for possible_key in possible_keys:
            for config_key in self._config:
                if config_key.startswith(possible_key + "."):
                    # 找到嵌套配置，構建字典
                    result = {}
                    prefix = possible_key + "."
                    
                    for ck, cv in self._config.items():
                        if ck.startswith(prefix):
                            relative_key = ck[len(prefix):]
                            self._set_nested_value(result, relative_key, cv.value)
                    
                    return result
        
        return None
    
    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any) -> None:
        """設置嵌套值"""
        keys = key.split('.')
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _get_from_cache(self, key: str) -> Any:
        """從緩存獲取"""
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key, 0)
            if time.time() - timestamp < self._cache_ttl:
                return self._cache[key]
            else:
                # 緩存過期
                del self._cache[key]
                del self._cache_timestamps[key]
        
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """設置緩存"""
        self._cache[key] = copy.deepcopy(value)
        self._cache_timestamps[key] = time.time()
    
    def _clear_cache(self, key: str) -> None:
        """清除緩存"""
        if key in self._cache:
            del self._cache[key]
            del self._cache_timestamps[key]
    
    def _clear_namespace_cache(self, namespace: str) -> None:
        """清除命名空間緩存"""
        prefix = f"{namespace}." if namespace else ""
        keys_to_remove = []
        
        for key in self._cache:
            if key.startswith(prefix):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._cache[key]
            del self._cache_timestamps[key]
    
    def _watch_file(self, file_path: Path) -> None:
        """監控文件"""
        self._watched_files.add(file_path)
        
        # 創建監控器
        if str(file_path) not in self._watchers:
            watcher = ConfigWatcher(self)
            watcher.start_watching([file_path])
            self._watchers[str(file_path)] = watcher
    
    def _reload_config(self, file_path: Path) -> None:
        """重新加載配置"""
        try:
            # 檢測格式
            format_type = self._detect_format(file_path)
            
            # 加載新配置
            new_config = self._load_file(file_path, format_type)
            
            # 更新配置
            self._store_config(new_config, ConfigSource.FILE, str(file_path), "")
            
            self.logger.info(
                "配置文件重新加載",
                file_path=str(file_path)
            )
            
        except Exception as e:
            self.logger.error(
                "配置文件重新加載失敗",
                file_path=str(file_path),
                error=str(e)
            )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 停止所有監控器
        for watcher in self._watchers.values():
            watcher.stop_watching()