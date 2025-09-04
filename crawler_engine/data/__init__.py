"""數據處理管道模組

提供數據清洗、轉換、存儲和檢索功能，支持多種數據源和目標。
"""

from .pipeline import DataPipeline, PipelineStage, PipelineConfig
from .processors import (
    DataProcessor,
    JobDataProcessor,
    CompanyDataProcessor,
    SalaryDataProcessor,
    DuplicateRemover,
    DataValidator,
    DataEnricher
)
from .storage import (
    StorageBackend,
    DatabaseStorage,
    FileStorage,
    CacheStorage,
    StorageConfig
)
from .models import (
    ProcessedJobData,
    ProcessedCompanyData,
    ProcessedSalaryData,
    DataQualityMetrics,
    ProcessingResult
)
from .cache import (
    CacheManager,
    CacheConfig,
    CacheStrategy
)
from .export import (
    DataExporter,
    ExportFormat,
    ExportConfig
)

__all__ = [
    # 核心管道
    "DataPipeline",
    "PipelineStage",
    "PipelineConfig",
    
    # 數據處理器
    "DataProcessor",
    "JobDataProcessor",
    "CompanyDataProcessor",
    "SalaryDataProcessor",
    "DuplicateRemover",
    "DataValidator",
    "DataEnricher",
    
    # 存儲後端
    "StorageBackend",
    "DatabaseStorage",
    "FileStorage",
    "CacheStorage",
    "StorageConfig",
    
    # 數據模型
    "ProcessedJobData",
    "ProcessedCompanyData",
    "ProcessedSalaryData",
    "DataQualityMetrics",
    "ProcessingResult",
    
    # 緩存管理
    "CacheManager",
    "CacheConfig",
    "CacheStrategy",
    
    # 數據導出
    "DataExporter",
    "ExportFormat",
    "ExportConfig"
]

# 版本信息
__version__ = "1.0.0"

# 支持的數據格式
SUPPORTED_FORMATS = [
    "json",
    "csv",
    "excel",
    "parquet",
    "sqlite",
    "postgresql",
    "mongodb"
]

# 默認配置
DEFAULT_PIPELINE_CONFIG = {
    "batch_size": 100,
    "max_workers": 4,
    "timeout": 300,
    "retry_attempts": 3,
    "enable_cache": True,
    "enable_validation": True,
    "enable_deduplication": True,
    "enable_enrichment": False
}

DEFAULT_STORAGE_CONFIG = {
    "backend": "sqlite",
    "connection_string": "sqlite:///jobs.db",
    "table_prefix": "crawler_",
    "batch_size": 1000,
    "enable_compression": True
}

DEFAULT_CACHE_CONFIG = {
    "strategy": "lru",
    "max_size": 10000,
    "ttl": 3600,
    "enable_persistence": True,
    "persistence_path": "cache"
}