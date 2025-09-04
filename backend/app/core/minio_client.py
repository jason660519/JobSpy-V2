"""MinIO 客戶端配置和操作模組

提供 MinIO 對象存儲的統一接口，支持數據分層存儲。"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from minio import Minio
from minio.error import S3Error
import structlog
from functools import wraps
import io

logger = structlog.get_logger(__name__)

def async_minio_operation(func):
    """裝飾器：將同步 MinIO 操作轉換為異步操作"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return wrapper

class MinIOClient:
    """MinIO 客戶端類，處理對象存儲操作"""
    
    def __init__(self):
        """初始化 MinIO 客戶端連接"""
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "password123")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        
        # 初始化 MinIO 客戶端
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # 定義數據分層的 bucket 名稱
        self.buckets = {
            "raw_data": "raw-data",
            "ai_processed": "ai-processed", 
            "cleaned_data": "cleaned-data",
            "backups": "backups"
        }
        
        logger.info("MinIO 客戶端初始化完成", endpoint=self.endpoint)
    
    @async_minio_operation
    def _ensure_bucket_exists_sync(self, bucket_name: str) -> bool:
        """同步版本的確保 bucket 存在"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"創建 bucket: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"確保 bucket 存在失敗: {e}")
            return False
    
    async def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """確保 bucket 存在，如果不存在則創建
        
        Args:
            bucket_name: bucket 名稱
            
        Returns:
            bool: 操作是否成功
        """
        return await self._ensure_bucket_exists_sync(bucket_name)
    
    async def ensure_buckets_exist(self) -> bool:
        """確保所有必要的 buckets 存在
        
        Returns:
            bool: 所有 buckets 是否成功創建或已存在
        """
        try:
            for bucket_type, bucket_name in self.buckets.items():
                success = await self.ensure_bucket_exists(bucket_name)
                if success:
                    logger.debug(f"Bucket 確保存在: {bucket_name}", bucket_type=bucket_type)
                else:
                    return False
            return True
        except Exception as e:
            logger.error("創建 buckets 失敗", error=str(e))
            return False
    
    @async_minio_operation
    def _upload_raw_data_sync(self, file_path: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """同步版本的上傳原始數據"""
        try:
            # 準備元數據
            object_metadata = {
                'Content-Type': 'application/octet-stream',
                'Upload-Time': datetime.utcnow().isoformat(),
                'Data-Type': 'raw-scraping'
            }
            if metadata:
                object_metadata.update({f'X-Amz-Meta-{k}': str(v) for k, v in metadata.items()})
            
            # 上傳數據
            data_stream = io.BytesIO(data)
            self.client.put_object(
                bucket_name=self.buckets['raw_data'],
                object_name=file_path,
                data=data_stream,
                length=len(data),
                metadata=object_metadata
            )
            
            logger.info("原始數據上傳成功", file_path=file_path, size=len(data))
            return True
            
        except S3Error as e:
            logger.error("原始數據上傳失敗", file_path=file_path, error=str(e))
            return False
    
    async def upload_raw_data(self, file_path: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """上傳原始爬蟲數據到 raw-data bucket
        
        Args:
            file_path: 文件在 bucket 中的路徑
            data: 文件數據
            metadata: 可選的元數據
            
        Returns:
            bool: 上傳是否成功
        """
        await self.ensure_bucket_exists(self.buckets['raw_data'])
        return await self._upload_raw_data_sync(file_path, data, metadata)
    
    async def upload_ai_processed_data(self, file_path: str, json_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """上傳 AI 處理後的 JSON 數據到 ai-processed bucket
        
        Args:
            file_path: 文件在 bucket 中的路徑
            json_data: JSON 數據
            metadata: 可選的元數據
            
        Returns:
            bool: 上傳是否成功
        """
        json_bytes = json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8')
        return await self._upload_data(self.buckets["ai_processed"], file_path, json_bytes, metadata)
    
    async def upload_cleaned_data(self, file_path: str, json_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """上傳清理後的一致格式 JSON 數據到 cleaned-data bucket
        
        Args:
            file_path: 文件在 bucket 中的路徑
            json_data: 清理後的 JSON 數據
            metadata: 可選的元數據
            
        Returns:
            bool: 上傳是否成功
        """
        json_bytes = json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8')
        return await self._upload_data(self.buckets["cleaned_data"], file_path, json_bytes, metadata)
    
    async def _upload_data(self, bucket_name: str, file_path: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """內部方法：上傳數據到指定 bucket
        
        Args:
            bucket_name: bucket 名稱
            file_path: 文件路徑
            data: 文件數據
            metadata: 元數據
            
        Returns:
            bool: 上傳是否成功
        """
        try:
            # 準備元數據
            upload_metadata = {
                "upload_time": datetime.utcnow().isoformat(),
                "content_type": "application/json" if file_path.endswith('.json') else "application/octet-stream"
            }
            if metadata:
                upload_metadata.update(metadata)
            
            # 上傳文件
            self.client.put_object(
                bucket_name,
                file_path,
                io.BytesIO(data),
                length=len(data),
                metadata=upload_metadata
            )
            
            logger.info("文件上傳成功", bucket=bucket_name, file_path=file_path, size=len(data))
            return True
            
        except S3Error as e:
            logger.error("文件上傳失敗", bucket=bucket_name, file_path=file_path, error=str(e))
            return False
    
    async def download_data(self, bucket_name: str, file_path: str) -> Optional[bytes]:
        """從指定 bucket 下載數據
        
        Args:
            bucket_name: bucket 名稱
            file_path: 文件路徑
            
        Returns:
            Optional[bytes]: 文件數據，如果失敗則返回 None
        """
        try:
            response = self.client.get_object(bucket_name, file_path)
            data = response.read()
            response.close()
            response.release_conn()
            
            logger.info("文件下載成功", bucket=bucket_name, file_path=file_path, size=len(data))
            return data
            
        except S3Error as e:
            logger.error("文件下載失敗", bucket=bucket_name, file_path=file_path, error=str(e))
            return None
    
    async def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """列出 bucket 中的對象
        
        Args:
            bucket_name: bucket 名稱
            prefix: 對象前綴過濾
            
        Returns:
            List[str]: 對象名稱列表
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error("列出對象失敗", bucket=bucket_name, prefix=prefix, error=str(e))
            return []
    
    async def delete_object(self, bucket_name: str, file_path: str) -> bool:
        """刪除指定對象
        
        Args:
            bucket_name: bucket 名稱
            file_path: 文件路徑
            
        Returns:
            bool: 刪除是否成功
        """
        try:
            self.client.remove_object(bucket_name, file_path)
            logger.info("對象刪除成功", bucket=bucket_name, file_path=file_path)
            return True
        except S3Error as e:
            logger.error("對象刪除失敗", bucket=bucket_name, file_path=file_path, error=str(e))
            return False
    
    async def get_bucket_stats(self) -> Dict[str, Dict[str, Any]]:
        """獲取所有 buckets 的統計信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 每個 bucket 的統計信息
        """
        stats = {}
        
        for bucket_type, bucket_name in self.buckets.items():
            try:
                objects = list(self.client.list_objects(bucket_name))
                total_size = sum(obj.size for obj in objects if obj.size is not None)
                object_count = len(objects)
                
                stats[bucket_type] = {
                    "bucket_name": bucket_name,
                    "object_count": object_count,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2)
                }
            except S3Error as e:
                logger.error(f"獲取 bucket 統計失敗: {bucket_name}", error=str(e))
                stats[bucket_type] = {
                    "bucket_name": bucket_name,
                    "error": str(e)
                }
        
        return stats

# 全局 MinIO 客戶端實例
_minio_client: Optional[MinIOClient] = None

async def get_minio_client() -> MinIOClient:
    """獲取 MinIO 客戶端實例
    
    Returns:
        MinIOClient: MinIO 客戶端實例
    """
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient()
        # 確保所有必要的 buckets 存在
        await _minio_client.ensure_buckets_exist()
    return _minio_client

async def init_minio_client() -> bool:
    """初始化 MinIO 客戶端
    
    Returns:
        bool: 初始化是否成功
    """
    try:
        client = await get_minio_client()
        logger.info("MinIO 客戶端初始化成功")
        return True
    except Exception as e:
        logger.error("MinIO 客戶端初始化失敗", error=str(e))
        return False