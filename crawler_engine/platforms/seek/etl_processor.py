"""Seek 平台 ETL 處理器

整合 Seek 平台的完整 ETL 流程，包括數據抓取、AI 解析、清理和存儲。
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from ...ai.processor import AIProcessor
from ...data.pipeline import DataPipeline, PipelineConfig, PipelineStage
from ...data.storage import DatabaseStorage, StorageConfig
from ...data.exporter import CSVExporter, ExportConfig, ExportFormat
from ...storage.minio_client import MinIOClient
from .adapter import SeekAdapter
from .config import SeekConfig, create_seek_config


class SeekETLProcessor:
    """Seek 平台專用 ETL 處理器
    
    整合完整的 ETL 流程：
    1. 數據抓取 (Extract)
    2. AI 解析處理 (Transform - AI)
    3. 數據清理 (Transform - Clean)
    4. 數據載入 (Load)
    5. CSV 導出 (Export)
    """
    
    def __init__(self, 
                 seek_config: Optional[SeekConfig] = None,
                 ai_config: Optional[Dict] = None,
                 storage_config: Optional[StorageConfig] = None,
                 export_config: Optional[ExportConfig] = None):
        """初始化 Seek ETL 處理器
        
        Args:
            seek_config: Seek 平台配置
            ai_config: AI 處理配置
            storage_config: 存儲配置
            export_config: 導出配置
        """
        self.logger = logging.getLogger(__name__)
        
        # 配置初始化
        self.seek_config = seek_config or SeekConfig()
        self.ai_config = ai_config or {
            "openai_api_key": "your-api-key",
            "openai_model": "gpt-3.5-turbo",
            "openai_base_url": "https://api.openai.com/v1"
        }
        
        # 存儲配置
        self.storage_config = storage_config or StorageConfig(
            database_url="sqlite:///seek_jobs.db"
        )
        
        # 導出配置
        self.export_config = export_config or ExportConfig(
            format=ExportFormat.CSV,
            output_path="seek_jobs_export.csv",
            encoding="utf-8"
        )
        
        # 組件初始化
        self._init_components()
        
    def _init_components(self):
        """初始化所有 ETL 組件"""
        try:
            # Seek 適配器
            platform_config = create_seek_config()
            self.seek_adapter = SeekAdapter(platform_config)
            
            # MinIO 客戶端
            self.minio_client = MinIOClient(self.storage_config)
            
            # AI 處理器
            self.ai_processor = AIProcessor(self.ai_config)
            
            # 數據管道
            pipeline_config = PipelineConfig(
                name="seek_etl_pipeline",
                description="Seek 平台 ETL 數據處理管道",
                stages=[PipelineStage.VALIDATION, PipelineStage.CLEANING, PipelineStage.TRANSFORMATION]
            )
            self.data_pipeline = DataPipeline(pipeline_config)
            
            # 數據庫存儲
            self.database_storage = DatabaseStorage(self.storage_config)
            
            # CSV 導出器
            self.csv_exporter = CSVExporter(self.export_config)
            
            self.logger.info("所有 ETL 組件初始化完成")
            
        except Exception as e:
            self.logger.error(f"ETL 組件初始化失敗: {e}")
            raise
    
    async def run_full_etl(self, 
                          keywords: str = "software engineer",
                          location: str = "Sydney",
                          max_jobs: int = 50) -> Dict[str, Any]:
        """運行完整的 ETL 流程
        
        Args:
            keywords: 搜索關鍵詞
            location: 工作地點
            max_jobs: 最大職位數量
            
        Returns:
            Dict: ETL 處理結果統計
        """
        start_time = datetime.now()
        results = {
            "start_time": start_time.isoformat(),
            "stages": {},
            "total_jobs_processed": 0,
            "errors": []
        }
        
        try:
            # 階段 1: 數據抓取
            self.logger.info("開始階段 1: 數據抓取")
            raw_jobs = await self._extract_jobs(keywords, location, max_jobs)
            results["stages"]["extract"] = {
                "jobs_found": len(raw_jobs),
                "status": "completed"
            }
            
            if not raw_jobs:
                self.logger.warning("未找到任何職位數據")
                return results
            
            # 階段 2: AI 解析處理
            self.logger.info("開始階段 2: AI 解析處理")
            ai_processed_jobs = await self._ai_process_jobs(raw_jobs)
            results["stages"]["ai_processing"] = {
                "jobs_processed": len(ai_processed_jobs),
                "status": "completed"
            }
            
            # 階段 3: 數據清理
            self.logger.info("開始階段 3: 數據清理")
            cleaned_jobs = await self._clean_jobs(ai_processed_jobs)
            results["stages"]["cleaning"] = {
                "jobs_cleaned": len(cleaned_jobs),
                "status": "completed"
            }
            
            # 階段 4: 數據庫載入
            self.logger.info("開始階段 4: 數據庫載入")
            loaded_count = await self._load_to_database(cleaned_jobs)
            results["stages"]["database_load"] = {
                "jobs_loaded": loaded_count,
                "status": "completed"
            }
            
            # 階段 5: CSV 導出
            self.logger.info("開始階段 5: CSV 導出")
            export_path = await self._export_to_csv(cleaned_jobs)
            results["stages"]["csv_export"] = {
                "export_path": str(export_path),
                "status": "completed"
            }
            
            results["total_jobs_processed"] = len(cleaned_jobs)
            results["status"] = "success"
            
        except Exception as e:
            self.logger.error(f"ETL 流程執行失敗: {e}")
            results["errors"].append(str(e))
            results["status"] = "failed"
        
        finally:
            end_time = datetime.now()
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = (end_time - start_time).total_seconds()
            
        return results
    
    async def _extract_jobs(self, keywords: str, location: str, max_jobs: int) -> List[Dict]:
        """階段 1: 數據抓取"""
        try:
            # 使用 Seek 適配器搜索職位
            search_params = {
                "keywords": keywords,
                "location": location,
                "max_results": max_jobs
            }
            
            jobs = await self.seek_adapter.search_jobs(search_params)
            
            # 存儲原始數據到 MinIO
            bucket_name = self.seek_config.etl_config["storage_buckets"]["raw_data"]
            await self._store_to_minio(jobs, bucket_name, "raw_jobs.json")
            
            self.logger.info(f"成功抓取 {len(jobs)} 個職位")
            return jobs
            
        except Exception as e:
            self.logger.error(f"數據抓取失敗: {e}")
            raise
    
    async def _ai_process_jobs(self, raw_jobs: List[Dict]) -> List[Dict]:
        """階段 2: AI 解析處理"""
        processed_jobs = []
        
        for job in raw_jobs:
            try:
                # 使用 AI 處理器解析職位信息
                prompt = self.seek_config.ai_prompts["job_extraction"]
                job_text = json.dumps(job, ensure_ascii=False)
                
                ai_result = await self.ai_processor.process_text(
                    text=job_text,
                    prompt=prompt
                )
                
                # 合併原始數據和 AI 解析結果
                enhanced_job = {
                    **job,
                    "ai_processed": ai_result,
                    "processing_timestamp": datetime.now().isoformat()
                }
                
                processed_jobs.append(enhanced_job)
                
            except Exception as e:
                self.logger.error(f"AI 處理職位失敗: {e}")
                # 保留原始數據，標記處理失敗
                job["ai_processing_error"] = str(e)
                processed_jobs.append(job)
        
        # 存儲 AI 處理結果
        bucket_name = self.seek_config.etl_config["storage_buckets"]["ai_processed"]
        await self._store_to_minio(processed_jobs, bucket_name, "ai_processed_jobs.json")
        
        self.logger.info(f"AI 處理完成，處理了 {len(processed_jobs)} 個職位")
        return processed_jobs
    
    async def _clean_jobs(self, ai_processed_jobs: List[Dict]) -> List[Dict]:
        """階段 3: 數據清理"""
        self.logger.info(f"開始數據清理，共 {len(ai_processed_jobs)} 條記錄")
        
        cleaned_jobs = []
        
        for job in ai_processed_jobs:
            try:
                # 使用 DataPipeline 的 process_item 方法進行數據清理
                cleaned_job = await self.data_pipeline.process_item(job)
                
                # 添加清理時間戳
                cleaned_job["cleaning_timestamp"] = datetime.now().isoformat()
                
                # 過濾空記錄（檢查必填字段）
                if (cleaned_job.get('title') and 
                    cleaned_job.get('company') and 
                    not cleaned_job.get('title_missing') and 
                    not cleaned_job.get('company_missing')):
                    cleaned_jobs.append(cleaned_job)
                else:
                    self.logger.warning(f"跳過無效記錄: {cleaned_job.get('title', 'N/A')}")
                
            except Exception as e:
                self.logger.error(f"數據清理失敗: {e}")
                # 保留原始數據，標記清理失敗
                job["cleaning_error"] = str(e)
                cleaned_jobs.append(job)
        
        # 存儲清理後的數據
        bucket_name = self.seek_config.etl_config["storage_buckets"]["cleaned_data"]
        await self._store_to_minio(cleaned_jobs, bucket_name, "cleaned_jobs.json")
        
        self.logger.info(f"數據清理完成，保留 {len(cleaned_jobs)} 條有效記錄")
        return cleaned_jobs
    
    async def _load_to_database(self, cleaned_jobs: List[Dict]) -> int:
        """階段 4: 數據庫載入"""
        try:
            loaded_count = 0
            
            for job in cleaned_jobs:
                try:
                    # 使用數據庫存儲組件保存數據
                    await self.database_storage.store_job(job)
                    loaded_count += 1
                    
                except Exception as e:
                    self.logger.error(f"數據庫載入失敗: {e}")
            
            self.logger.info(f"成功載入 {loaded_count} 個職位到數據庫")
            return loaded_count
            
        except Exception as e:
            self.logger.error(f"數據庫載入階段失敗: {e}")
            raise
    
    async def _export_to_csv(self, cleaned_jobs: List[Dict]) -> Path:
        """階段 5: CSV 導出"""
        try:
            # 使用 CSV 導出器導出數據
            export_success = await self.csv_exporter.export(cleaned_jobs, self.export_config.output_path)
            
            if not export_success:
                raise Exception("CSV 導出失敗")
            
            export_path = Path(self.export_config.output_path)
            
            # 同時存儲到 MinIO
            bucket_name = self.seek_config.etl_config["storage_buckets"]["final_data"]
            with open(export_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            await self._store_to_minio_text(csv_content, bucket_name, "final_export.csv")
            
            self.logger.info(f"CSV 導出完成: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"CSV 導出失敗: {e}")
            raise
    
    async def _store_to_minio(self, data: List[Dict], bucket_name: str, object_name: str):
        """存儲數據到 MinIO"""
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            await self.minio_client.upload_text(bucket_name, object_name, json_data)
            self.logger.debug(f"數據已存儲到 MinIO: {bucket_name}/{object_name}")
            
        except Exception as e:
            self.logger.error(f"MinIO 存儲失敗: {e}")
    
    async def _store_to_minio_text(self, text: str, bucket_name: str, object_name: str):
        """存儲文本數據到 MinIO"""
        try:
            await self.minio_client.upload_text(bucket_name, object_name, text)
            self.logger.debug(f"文本數據已存儲到 MinIO: {bucket_name}/{object_name}")
            
        except Exception as e:
            self.logger.error(f"MinIO 文本存儲失敗: {e}")
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計信息"""
        try:
            stats = {
                "database_stats": await self.database_storage.get_stats(),
                "minio_buckets": list(self.seek_config.etl_config["storage_buckets"].values()),
                "pipeline_stats": self.data_pipeline.get_stats() if hasattr(self.data_pipeline, 'get_stats') else {},
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取統計信息失敗: {e}")
            return {"error": str(e)}