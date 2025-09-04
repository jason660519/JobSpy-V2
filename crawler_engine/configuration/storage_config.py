"""存儲配置模組

定義數據存儲相關的配置參數。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class StorageConfig:
    """存儲配置"""
    
    # MinIO 配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_region: str = "us-east-1"
    
    # 數據庫配置
    database_url: str = "sqlite:///jobs.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False
    
    # 存儲桶配置
    raw_data_bucket: str = "raw-data"
    processed_data_bucket: str = "processed-data"
    cleaned_data_bucket: str = "cleaned-data"
    exported_data_bucket: str = "exported-data"
    
    # 本地存儲配置
    local_storage_path: Optional[Path] = None
    enable_local_backup: bool = True
    
    # 緩存配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 小時
    cache_max_size: int = 1000
    
    def __post_init__(self):
        """初始化後處理"""
        if self.local_storage_path is None:
            self.local_storage_path = Path("./data")
        elif isinstance(self.local_storage_path, str):
            self.local_storage_path = Path(self.local_storage_path)
    
    def get_minio_config(self) -> Dict[str, Any]:
        """獲取 MinIO 配置"""
        return {
            "endpoint": self.minio_endpoint,
            "access_key": self.minio_access_key,
            "secret_key": self.minio_secret_key,
            "secure": self.minio_secure,
            "region": self.minio_region
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """獲取數據庫配置"""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "echo": self.database_echo
        }
    
    def get_bucket_names(self) -> Dict[str, str]:
        """獲取所有存儲桶名稱"""
        return {
            "raw_data": self.raw_data_bucket,
            "processed_data": self.processed_data_bucket,
            "cleaned_data": self.cleaned_data_bucket,
            "exported_data": self.exported_data_bucket
        }