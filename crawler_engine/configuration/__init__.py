"""配置管理模組

提供統一的配置管理、環境變量處理和配置驗證功能。
"""

from .config_manager import (
    ConfigManager,
    ConfigSource,
    ConfigFormat,
    ConfigValidationError,
    ConfigNotFoundError,
    ConfigSchema,
    ConfigValue,
    ConfigWatcher
)

from .environment import (
    EnvironmentManager,
    Environment,
    EnvironmentConfig,
    EnvironmentVariable,
    SecretManager
)

from .settings import (
    AppSettings as Settings,
    DatabaseSettings,
    APISettings,
    CrawlerSettings,
    MonitoringSettings,
    LoggingSettings,
    CacheSettings,
    SecuritySettings
)

from .validators import (
    ConfigValidator,
    ValidationRule,
    ValidationError,
    URLValidator,
    EmailValidator,
    PortValidator,
    PathValidator,
    RegexValidator
)

from .scraping_config import (
    ScrapingConfig,
    DEFAULT_SCRAPING_CONFIG,
    FAST_SCRAPING_CONFIG,
    CONSERVATIVE_SCRAPING_CONFIG,
    PRODUCTION_SCRAPING_CONFIG,
    get_scraping_config,
    create_custom_scraping_config
)



__all__ = [
    # 配置管理
    'ConfigManager',
    'ConfigSource',
    'ConfigFormat',
    'ConfigValidationError',
    'ConfigNotFoundError',
    'ConfigSchema',
    'ConfigValue',
    'ConfigWatcher',
    
    # 環境管理
    'EnvironmentManager',
    'Environment',
    'EnvironmentConfig',
    'EnvironmentVariable',
    'SecretManager',
    
    # 設置
    'Settings',
    'DatabaseSettings',
    'APISettings',
    'CrawlerSettings',
    'MonitoringSettings',
    'LoggingSettings',
    'CacheSettings',
    'SecuritySettings',
    
    # 驗證器
    'ConfigValidator',
    'ValidationRule',
    'ValidationError',
    'URLValidator',
    'EmailValidator',
    'PortValidator',
    'PathValidator',
    'RegexValidator',
    
    # 爬蟲配置
    'ScrapingConfig',
    'DEFAULT_SCRAPING_CONFIG',
    'FAST_SCRAPING_CONFIG',
    'CONSERVATIVE_SCRAPING_CONFIG',
    'PRODUCTION_SCRAPING_CONFIG',
    'get_scraping_config',
    'create_custom_scraping_config'
]

# 版本信息
__version__ = '1.0.0'

# 支持的配置格式
SUPPORTED_FORMATS = [
    'json',
    'yaml',
    'toml',
    'ini',
    'env'
]

# 默認配置
DEFAULT_CONFIG = {
    'config': {
        'auto_reload': True,
        'watch_interval': 5,
        'validation_enabled': True,
        'cache_enabled': True,
        'backup_enabled': True,
        'max_backups': 10
    },
    'environment': {
        'auto_detect': True,
        'default_env': 'development',
        'env_file': '.env',
        'secrets_file': '.secrets',
        'encryption_enabled': False
    },
    'validation': {
        'strict_mode': False,
        'fail_fast': True,
        'custom_validators': {},
        'schema_cache': True
    }
}

# 環境變量前綴
ENV_PREFIX = 'CRAWLER_ENGINE_'

# 配置文件搜索路徑
CONFIG_SEARCH_PATHS = [
    '.',
    './config',
    './configs',
    '~/.crawler_engine',
    '/etc/crawler_engine'
]

# 默認配置文件名
DEFAULT_CONFIG_FILES = [
    'config.yaml',
    'config.yml',
    'config.json',
    'config.toml',
    'config.ini'
]