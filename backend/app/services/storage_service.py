"""存儲服務模組

提供統一的數據存儲接口，整合 MinIO 對象存儲和 PostgreSQL 數據庫。
實現爬蟲數據的完整生命週期管理。
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.minio_client import get_minio_client
from app.core.database import get_db
from app.models.job import JobListing

logger = structlog.get_logger(__name__)

class StorageService:
    """存儲服務類，管理數據的完整生命週期"""
    
    def __init__(self):
        """初始化存儲服務"""
        self.minio_client = None
        
    async def _get_minio_client(self):
        """獲取 MinIO 客戶端實例"""
        if not self.minio_client:
            self.minio_client = await get_minio_client()
        return self.minio_client
    
    async def store_raw_scraping_data(self, 
                                    site_name: str, 
                                    search_query: str, 
                                    raw_data: bytes,
                                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """存儲原始爬蟲數據到 MinIO
        
        Args:
            site_name: 爬蟲網站名稱 (如 'indeed', 'linkedin')
            search_query: 搜索查詢條件
            raw_data: 原始數據 (HTML, JSON 等)
            metadata: 額外的元數據
            
        Returns:
            str: 存儲的文件路徑
        """
        try:
            # 生成唯一的文件路徑
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_id = str(uuid.uuid4())[:8]
            file_path = f"{site_name}/{timestamp}/{search_query.replace(' ', '_')}_{file_id}.raw"
            
            # 準備元數據
            storage_metadata = {
                "site_name": site_name,
                "search_query": search_query,
                "scraping_time": datetime.utcnow().isoformat(),
                "data_type": "raw_scraping",
                "file_size": len(raw_data)
            }
            if metadata:
                storage_metadata.update(metadata)
            
            # 上傳到 MinIO
            minio_client = await self._get_minio_client()
            success = await minio_client.upload_raw_data(file_path, raw_data, storage_metadata)
            
            if success:
                logger.info("原始數據存儲成功", 
                          site_name=site_name, 
                          search_query=search_query, 
                          file_path=file_path)
                return file_path
            else:
                raise Exception("MinIO 上傳失敗")
                
        except Exception as e:
            logger.error("原始數據存儲失敗", 
                        site_name=site_name, 
                        search_query=search_query, 
                        error=str(e))
            raise
    
    async def store_ai_processed_data(self, 
                                    raw_file_path: str,
                                    processed_data: Dict[str, Any],
                                    ai_model: str = "gpt-4-vision",
                                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """存儲 AI 處理後的數據到 MinIO
        
        Args:
            raw_file_path: 原始數據文件路徑
            processed_data: AI 處理後的結構化數據
            ai_model: 使用的 AI 模型名稱
            metadata: 額外的元數據
            
        Returns:
            str: 存儲的文件路徑
        """
        try:
            # 基於原始文件路徑生成處理後文件路徑
            base_path = raw_file_path.replace('.raw', '')
            file_path = f"{base_path}_ai_processed.json"
            
            # 準備元數據
            storage_metadata = {
                "source_raw_file": raw_file_path,
                "ai_model": ai_model,
                "processing_time": datetime.utcnow().isoformat(),
                "data_type": "ai_processed",
                "job_count": len(processed_data.get('jobs', []))
            }
            if metadata:
                storage_metadata.update(metadata)
            
            # 上傳到 MinIO
            minio_client = await self._get_minio_client()
            success = await minio_client.upload_ai_processed_data(file_path, processed_data, storage_metadata)
            
            if success:
                logger.info("AI 處理數據存儲成功", 
                          raw_file_path=raw_file_path, 
                          file_path=file_path,
                          job_count=storage_metadata['job_count'])
                return file_path
            else:
                raise Exception("MinIO 上傳失敗")
                
        except Exception as e:
            logger.error("AI 處理數據存儲失敗", 
                        raw_file_path=raw_file_path, 
                        error=str(e))
            raise
    
    async def store_cleaned_data(self, 
                               ai_processed_file_path: str,
                               cleaned_data: Dict[str, Any],
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """存儲清理後的一致格式數據到 MinIO
        
        Args:
            ai_processed_file_path: AI 處理後的文件路徑
            cleaned_data: 清理後的一致格式數據
            metadata: 額外的元數據
            
        Returns:
            str: 存儲的文件路徑
        """
        try:
            # 基於 AI 處理文件路徑生成清理後文件路徑
            base_path = ai_processed_file_path.replace('_ai_processed.json', '')
            file_path = f"{base_path}_cleaned.json"
            
            # 準備元數據
            storage_metadata = {
                "source_ai_file": ai_processed_file_path,
                "cleaning_time": datetime.utcnow().isoformat(),
                "data_type": "cleaned",
                "job_count": len(cleaned_data.get('jobs', [])),
                "schema_version": "1.0"
            }
            if metadata:
                storage_metadata.update(metadata)
            
            # 上傳到 MinIO
            minio_client = await self._get_minio_client()
            success = await minio_client.upload_cleaned_data(file_path, cleaned_data, storage_metadata)
            
            if success:
                logger.info("清理數據存儲成功", 
                          ai_processed_file_path=ai_processed_file_path, 
                          file_path=file_path,
                          job_count=storage_metadata['job_count'])
                return file_path
            else:
                raise Exception("MinIO 上傳失敗")
                
        except Exception as e:
            logger.error("清理數據存儲失敗", 
                        ai_processed_file_path=ai_processed_file_path, 
                        error=str(e))
            raise
    
    async def load_to_database(self, 
                             cleaned_file_path: str,
                             db: AsyncSession) -> List[JobListing]:
        """將清理後的數據載入到 PostgreSQL 數據庫
        
        Args:
            cleaned_file_path: 清理後數據的文件路徑
            db: 數據庫會話
            
        Returns:
            List[JobListing]: 創建的工作記錄列表
        """
        try:
            # 從 MinIO 下載清理後的數據
            minio_client = await self._get_minio_client()
            data_bytes = await minio_client.download_data("cleaned-data", cleaned_file_path)
            
            if not data_bytes:
                raise Exception("無法從 MinIO 下載數據")
            
            # 解析 JSON 數據
            cleaned_data = json.loads(data_bytes.decode('utf-8'))
            jobs_data = cleaned_data.get('jobs', [])
            
            # 創建數據庫記錄
            created_jobs = []
            for job_data in jobs_data:
                # 創建 JobListing 實例
                job = JobListing(
                    title=job_data.get('title'),
                    company=job_data.get('company'),
                    location=job_data.get('location'),
                    description=job_data.get('description'),
                    salary_range={
                        'min': job_data.get('salary_min'),
                        'max': job_data.get('salary_max')
                    } if job_data.get('salary_min') or job_data.get('salary_max') else None,
                    source_url=job_data.get('url'),
                    source=job_data.get('site', 'unknown'),
                    posted_date=datetime.strptime(job_data.get('date_posted'), '%Y-%m-%d').date() if job_data.get('date_posted') else None,
                    job_type=job_data.get('job_type'),
                    # 存儲 MinIO 文件路徑作為參考
                    raw_data={'minio_file_path': cleaned_file_path}
                )
                
                db.add(job)
                created_jobs.append(job)
            
            # 提交到數據庫
            await db.commit()
            
            logger.info("數據載入數據庫成功", 
                      cleaned_file_path=cleaned_file_path, 
                      job_count=len(created_jobs))
            
            return created_jobs
            
        except Exception as e:
            await db.rollback()
            logger.error("數據載入數據庫失敗", 
                        cleaned_file_path=cleaned_file_path, 
                        error=str(e))
            raise
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """獲取存儲統計信息
        
        Returns:
            Dict[str, Any]: 存儲統計信息
        """
        try:
            minio_client = await self._get_minio_client()
            bucket_stats = await minio_client.get_bucket_stats()
            
            # 計算總體統計
            total_objects = sum(stats.get('object_count', 0) for stats in bucket_stats.values() if 'object_count' in stats)
            total_size_mb = sum(stats.get('total_size_mb', 0) for stats in bucket_stats.values() if 'total_size_mb' in stats)
            
            return {
                "bucket_stats": bucket_stats,
                "total_objects": total_objects,
                "total_size_mb": total_size_mb,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("獲取存儲統計失敗", error=str(e))
            return {"error": str(e)}
    
    async def complete_data_pipeline(self, 
                                   site_name: str,
                                   search_query: str,
                                   raw_data: bytes,
                                   ai_processed_data: Dict[str, Any],
                                   cleaned_data: Dict[str, Any],
                                   db: AsyncSession,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """完整的數據管道：從原始數據到數據庫載入
        
        Args:
            site_name: 爬蟲網站名稱
            search_query: 搜索查詢
            raw_data: 原始數據
            ai_processed_data: AI 處理後數據
            cleaned_data: 清理後數據
            db: 數據庫會話
            metadata: 額外元數據
            
        Returns:
            Dict[str, str]: 各階段的文件路徑
        """
        try:
            # 1. 存儲原始數據
            raw_file_path = await self.store_raw_scraping_data(
                site_name, search_query, raw_data, metadata
            )
            
            # 2. 存儲 AI 處理數據
            ai_file_path = await self.store_ai_processed_data(
                raw_file_path, ai_processed_data, metadata=metadata
            )
            
            # 3. 存儲清理數據
            cleaned_file_path = await self.store_cleaned_data(
                ai_file_path, cleaned_data, metadata
            )
            
            # 4. 載入到數據庫
            jobs = await self.load_to_database(cleaned_file_path, db)
            
            result = {
                "raw_file_path": raw_file_path,
                "ai_file_path": ai_file_path,
                "cleaned_file_path": cleaned_file_path,
                "database_records": len(jobs)
            }
            
            logger.info("完整數據管道執行成功", 
                      site_name=site_name, 
                      search_query=search_query,
                      **result)
            
            return result
            
        except Exception as e:
            logger.error("數據管道執行失敗", 
                        site_name=site_name, 
                        search_query=search_query, 
                        error=str(e))
            raise

# 全局存儲服務實例
storage_service = StorageService()

async def get_storage_service() -> StorageService:
    """獲取存儲服務實例
    
    Returns:
        StorageService: 存儲服務實例
    """
    return storage_service