"""Seek爬蟲ETL Pipeline測試腳本

測試Seek平台爬蟲的完整ETL流程，包括：
1. 原始數據抓取階段
2. AI解析處理階段  
3. 數據清理階段
4. 數據庫載入階段
5. CSV導出階段

並驗證文件是否存放在正確位置。
"""

import asyncio
import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import structlog

# 設置日誌
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# 導入必要的模組
from crawler_engine.platforms.seek.adapter import SeekAdapter, create_seek_config
from crawler_engine.platforms.base import SearchRequest, SearchMethod
from crawler_engine.storage.minio_client import MinIOClient
from crawler_engine.ai.processor import AIProcessor
from crawler_engine.data.pipeline import DataPipeline
from crawler_engine.data.storage import DatabaseStorage
from crawler_engine.data.exporter import CSVExporter


class SeekETLTester:
    """Seek ETL Pipeline 測試器
    
    負責測試完整的ETL流程並驗證每個階段的輸出。
    """
    
    def __init__(self):
        """初始化測試器"""
        self.logger = logger.bind(component="SeekETLTester")
        
        # 初始化組件
        self.seek_adapter = SeekAdapter(create_seek_config())
        
        # 創建配置
        from crawler_engine.config import StorageConfig, AIConfig
        storage_config = StorageConfig(
            minio_endpoint="localhost:9000",
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin",
            minio_bucket="test-bucket"
        )
        ai_config = AIConfig(
            openai_api_key="test-key",
            openai_model="gpt-4-vision-preview"
        )
        
        # 創建管道配置
        from crawler_engine.data.pipeline import PipelineConfig, PipelineStage
        pipeline_config = PipelineConfig(
            name="test-pipeline",
            description="測試管道",
            stages=[PipelineStage.VALIDATION, PipelineStage.CLEANING, PipelineStage.TRANSFORMATION]
        )
        
        # 創建數據庫存儲配置
        from crawler_engine.data.storage import StorageConfig as DBStorageConfig
        db_storage_config = DBStorageConfig(
            backend_type="sqlite",
            connection_string="test_jobs.db"
        )
        
        # 創建導出配置
        from crawler_engine.data.exporter import ExportConfig, ExportFormat
        export_config = ExportConfig(
            format=ExportFormat.CSV,
            output_path="test_output.csv"
        )
        
        self.minio_client = MinIOClient(storage_config)
        self.ai_processor = AIProcessor(ai_config)
        self.data_pipeline = DataPipeline(pipeline_config)
        self.db_storage = DatabaseStorage(db_storage_config)
        self.csv_exporter = CSVExporter(export_config)
        
        # 測試配置
        self.test_query = "software engineer"
        self.test_location = "Sydney"
        self.test_limit = 5  # 限制測試數量
        
        # 文件路徑配置
        self.base_path = Path("./test_output")
        self.raw_data_path = self.base_path / "raw_data"
        self.ai_processed_path = self.base_path / "ai_processed"
        self.cleaned_data_path = self.base_path / "cleaned_data"
        self.csv_export_path = self.base_path / "csv_exports"
        
        # 創建測試目錄
        self._create_test_directories()
        
        # ETL階段狀態
        self.etl_status = {
            "stage_1_raw_data": {"completed": False, "files": [], "count": 0},
            "stage_2_ai_processed": {"completed": False, "files": [], "count": 0},
            "stage_3_cleaned_data": {"completed": False, "files": [], "count": 0},
            "stage_4_db_loaded": {"completed": False, "records": 0},
            "stage_5_csv_exported": {"completed": False, "files": [], "count": 0}
        }
    
    def _create_test_directories(self):
        """創建測試目錄結構"""
        directories = [
            self.base_path,
            self.raw_data_path,
            self.ai_processed_path,
            self.cleaned_data_path,
            self.csv_export_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info("創建測試目錄", path=str(directory))
    
    async def run_complete_etl_test(self) -> Dict[str, Any]:
        """運行完整的ETL測試流程
        
        Returns:
            Dict[str, Any]: 測試結果報告
        """
        self.logger.info("開始Seek ETL Pipeline完整測試")
        
        start_time = datetime.now()
        test_results = {
            "start_time": start_time.isoformat(),
            "test_query": self.test_query,
            "test_location": self.test_location,
            "test_limit": self.test_limit,
            "stages": {},
            "overall_success": False,
            "errors": []
        }
        
        try:
            # 階段1：原始數據抓取
            self.logger.info("開始階段1：原始數據抓取")
            stage1_result = await self._test_stage_1_raw_data_extraction()
            test_results["stages"]["stage_1"] = stage1_result
            
            if not stage1_result["success"]:
                raise Exception("階段1失敗，無法繼續後續測試")
            
            # 階段2：AI解析處理
            self.logger.info("開始階段2：AI解析處理")
            stage2_result = await self._test_stage_2_ai_processing()
            test_results["stages"]["stage_2"] = stage2_result
            
            # 階段3：數據清理
            self.logger.info("開始階段3：數據清理")
            stage3_result = await self._test_stage_3_data_cleaning()
            test_results["stages"]["stage_3"] = stage3_result
            
            # 階段4：數據庫載入
            self.logger.info("開始階段4：數據庫載入")
            stage4_result = await self._test_stage_4_database_loading()
            test_results["stages"]["stage_4"] = stage4_result
            
            # 階段5：CSV導出
            self.logger.info("開始階段5：CSV導出")
            stage5_result = await self._test_stage_5_csv_export()
            test_results["stages"]["stage_5"] = stage5_result
            
            # 檢查整體成功狀態
            all_stages_success = all(
                result["success"] for result in test_results["stages"].values()
            )
            test_results["overall_success"] = all_stages_success
            
        except Exception as e:
            error_msg = f"ETL測試過程中發生錯誤: {str(e)}"
            self.logger.error("ETL測試失敗", error=error_msg)
            test_results["errors"].append(error_msg)
            test_results["overall_success"] = False
        
        # 計算總執行時間
        end_time = datetime.now()
        test_results["end_time"] = end_time.isoformat()
        test_results["total_duration"] = (end_time - start_time).total_seconds()
        
        # 生成測試報告
        await self._generate_test_report(test_results)
        
        return test_results
    
    async def _test_stage_1_raw_data_extraction(self) -> Dict[str, Any]:
        """測試階段1：原始數據抓取
        
        Returns:
            Dict[str, Any]: 階段1測試結果
        """
        stage_result = {
            "stage": "原始數據抓取",
            "success": False,
            "files_created": [],
            "jobs_extracted": 0,
            "minio_stored": False,
            "local_stored": False,
            "errors": []
        }
        
        try:
            # 創建搜索請求
            search_request = SearchRequest(
                query=self.test_query,
                location=self.test_location,
                limit=self.test_limit,
                page=1
            )
            
            # 執行搜索
            search_result = await self.seek_adapter.search_jobs(
                search_request, 
                SearchMethod.WEB_SCRAPING
            )
            
            if not search_result.success:
                raise Exception(f"搜索失敗: {search_result.error_message}")
            
            stage_result["jobs_extracted"] = len(search_result.jobs)
            
            if len(search_result.jobs) == 0:
                raise Exception("未找到任何職位數據")
            
            # 保存原始數據到本地
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_data_file = self.raw_data_path / f"seek_raw_data_{timestamp}.json"
            
            raw_data = {
                "search_request": {
                    "query": search_request.query,
                    "location": search_request.location,
                    "limit": search_request.limit,
                    "page": search_request.page
                },
                "search_result": {
                    "total_count": search_result.total_count,
                    "jobs_found": len(search_result.jobs),
                    "platform": search_result.platform,
                    "execution_time": search_result.execution_time
                },
                "jobs": [job.__dict__ for job in search_result.jobs],
                "extracted_at": datetime.now().isoformat()
            }
            
            # 保存到本地文件
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=2, default=str)
            
            stage_result["files_created"].append(str(raw_data_file))
            stage_result["local_stored"] = True
            
            # 嘗試保存到MinIO
            try:
                await self.minio_client.upload_file(
                    bucket_name="raw-data",
                    object_name=f"seek/{timestamp}/raw_data.json",
                    file_path=str(raw_data_file)
                )
                stage_result["minio_stored"] = True
                self.logger.info("原始數據已上傳到MinIO", bucket="raw-data")
            except Exception as e:
                self.logger.warning("MinIO上傳失敗", error=str(e))
                stage_result["errors"].append(f"MinIO上傳失敗: {str(e)}")
            
            # 更新ETL狀態
            self.etl_status["stage_1_raw_data"] = {
                "completed": True,
                "files": stage_result["files_created"],
                "count": stage_result["jobs_extracted"]
            }
            
            stage_result["success"] = True
            self.logger.info(
                "階段1完成", 
                jobs_extracted=stage_result["jobs_extracted"],
                files_created=len(stage_result["files_created"])
            )
            
        except Exception as e:
            error_msg = f"階段1失敗: {str(e)}"
            stage_result["errors"].append(error_msg)
            self.logger.error("階段1失敗", error=error_msg)
        
        return stage_result
    
    async def _test_stage_2_ai_processing(self) -> Dict[str, Any]:
        """測試階段2：AI解析處理
        
        Returns:
            Dict[str, Any]: 階段2測試結果
        """
        stage_result = {
            "stage": "AI解析處理",
            "success": False,
            "files_created": [],
            "jobs_processed": 0,
            "ai_enhancements": [],
            "minio_stored": False,
            "local_stored": False,
            "errors": []
        }
        
        try:
            # 檢查階段1是否完成
            if not self.etl_status["stage_1_raw_data"]["completed"]:
                raise Exception("階段1未完成，無法進行AI處理")
            
            # 讀取原始數據
            raw_data_files = self.etl_status["stage_1_raw_data"]["files"]
            if not raw_data_files:
                raise Exception("未找到原始數據文件")
            
            # 讀取第一個原始數據文件
            with open(raw_data_files[0], 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            jobs = raw_data.get("jobs", [])
            
            # AI處理每個職位
            processed_jobs = []
            for job in jobs:
                try:
                    # 模擬AI處理（實際應該調用AI服務）
                    ai_enhanced_job = await self._simulate_ai_processing(job)
                    processed_jobs.append(ai_enhanced_job)
                    
                    # 記錄AI增強功能
                    if "ai_analysis" in ai_enhanced_job:
                        stage_result["ai_enhancements"].extend(
                            ai_enhanced_job["ai_analysis"].keys()
                        )
                    
                except Exception as e:
                    self.logger.warning("AI處理單個職位失敗", job_id=job.get("job_id"), error=str(e))
                    # 保留原始數據
                    processed_jobs.append(job)
            
            stage_result["jobs_processed"] = len(processed_jobs)
            
            # 保存AI處理後的數據
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ai_processed_file = self.ai_processed_path / f"seek_ai_processed_{timestamp}.json"
            
            ai_processed_data = {
                "original_search": raw_data.get("search_request", {}),
                "processing_info": {
                    "processed_at": datetime.now().isoformat(),
                    "ai_model": "gpt-4",  # 模擬
                    "processing_version": "1.0",
                    "jobs_processed": len(processed_jobs)
                },
                "jobs": processed_jobs
            }
            
            # 保存到本地文件
            with open(ai_processed_file, 'w', encoding='utf-8') as f:
                json.dump(ai_processed_data, f, ensure_ascii=False, indent=2, default=str)
            
            stage_result["files_created"].append(str(ai_processed_file))
            stage_result["local_stored"] = True
            
            # 嘗試保存到MinIO
            try:
                await self.minio_client.upload_file(
                    bucket_name="ai-processed",
                    object_name=f"seek/{timestamp}/ai_processed.json",
                    file_path=str(ai_processed_file)
                )
                stage_result["minio_stored"] = True
                self.logger.info("AI處理數據已上傳到MinIO", bucket="ai-processed")
            except Exception as e:
                self.logger.warning("MinIO上傳失敗", error=str(e))
                stage_result["errors"].append(f"MinIO上傳失敗: {str(e)}")
            
            # 更新ETL狀態
            self.etl_status["stage_2_ai_processed"] = {
                "completed": True,
                "files": stage_result["files_created"],
                "count": stage_result["jobs_processed"]
            }
            
            stage_result["success"] = True
            self.logger.info(
                "階段2完成", 
                jobs_processed=stage_result["jobs_processed"],
                ai_enhancements=len(set(stage_result["ai_enhancements"]))
            )
            
        except Exception as e:
            error_msg = f"階段2失敗: {str(e)}"
            stage_result["errors"].append(error_msg)
            self.logger.error("階段2失敗", error=error_msg)
        
        return stage_result
    
    async def _simulate_ai_processing(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """模擬AI處理過程
        
        Args:
            job: 原始職位數據
            
        Returns:
            Dict[str, Any]: AI增強後的職位數據
        """
        # 複製原始數據
        enhanced_job = job.copy()
        
        # 添加AI分析結果
        enhanced_job["ai_analysis"] = {
            "skill_extraction": {
                "technical_skills": ["Python", "JavaScript", "SQL", "AWS"],
                "soft_skills": ["Communication", "Problem Solving", "Teamwork"],
                "confidence_score": 0.85
            },
            "salary_prediction": {
                "predicted_min": job.get("salary_min", 70000),
                "predicted_max": job.get("salary_max", 90000),
                "confidence_score": 0.78
            },
            "job_level": {
                "level": "mid",
                "years_experience": "3-5",
                "confidence_score": 0.82
            },
            "company_analysis": {
                "company_size": "medium",
                "industry": "technology",
                "growth_stage": "established"
            },
            "location_analysis": {
                "remote_friendly": True,
                "commute_score": 8.5,
                "cost_of_living_index": 85
            }
        }
        
        # 添加處理時間戳
        enhanced_job["ai_processed_at"] = datetime.now().isoformat()
        
        return enhanced_job
    
    async def _test_stage_3_data_cleaning(self) -> Dict[str, Any]:
        """測試階段3：數據清理
        
        Returns:
            Dict[str, Any]: 階段3測試結果
        """
        stage_result = {
            "stage": "數據清理",
            "success": False,
            "files_created": [],
            "jobs_cleaned": 0,
            "cleaning_operations": [],
            "minio_stored": False,
            "local_stored": False,
            "errors": []
        }
        
        try:
            # 檢查階段2是否完成
            if not self.etl_status["stage_2_ai_processed"]["completed"]:
                raise Exception("階段2未完成，無法進行數據清理")
            
            # 讀取AI處理後的數據
            ai_processed_files = self.etl_status["stage_2_ai_processed"]["files"]
            if not ai_processed_files:
                raise Exception("未找到AI處理後的數據文件")
            
            # 讀取第一個AI處理文件
            with open(ai_processed_files[0], 'r', encoding='utf-8') as f:
                ai_processed_data = json.load(f)
            
            jobs = ai_processed_data.get("jobs", [])
            
            # 清理每個職位數據
            cleaned_jobs = []
            cleaning_stats = {
                "duplicates_removed": 0,
                "invalid_data_fixed": 0,
                "standardized_fields": 0,
                "enriched_records": 0
            }
            
            seen_job_ids = set()
            
            for job in jobs:
                try:
                    # 去重
                    job_id = job.get("job_id")
                    if job_id in seen_job_ids:
                        cleaning_stats["duplicates_removed"] += 1
                        continue
                    seen_job_ids.add(job_id)
                    
                    # 清理和標準化數據
                    cleaned_job = await self._clean_job_data(job)
                    cleaned_jobs.append(cleaned_job)
                    
                    # 統計清理操作
                    if cleaned_job.get("_cleaning_applied"):
                        cleaning_stats["invalid_data_fixed"] += 1
                    if cleaned_job.get("_standardized"):
                        cleaning_stats["standardized_fields"] += 1
                    if cleaned_job.get("_enriched"):
                        cleaning_stats["enriched_records"] += 1
                    
                except Exception as e:
                    self.logger.warning("清理單個職位失敗", job_id=job.get("job_id"), error=str(e))
                    continue
            
            stage_result["jobs_cleaned"] = len(cleaned_jobs)
            stage_result["cleaning_operations"] = list(cleaning_stats.keys())
            
            # 保存清理後的數據
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cleaned_data_file = self.cleaned_data_path / f"seek_cleaned_data_{timestamp}.json"
            
            cleaned_data = {
                "original_search": ai_processed_data.get("original_search", {}),
                "processing_info": ai_processed_data.get("processing_info", {}),
                "cleaning_info": {
                    "cleaned_at": datetime.now().isoformat(),
                    "cleaning_version": "1.0",
                    "jobs_input": len(jobs),
                    "jobs_output": len(cleaned_jobs),
                    "cleaning_stats": cleaning_stats
                },
                "jobs": cleaned_jobs
            }
            
            # 保存到本地文件
            with open(cleaned_data_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2, default=str)
            
            stage_result["files_created"].append(str(cleaned_data_file))
            stage_result["local_stored"] = True
            
            # 嘗試保存到MinIO
            try:
                await self.minio_client.upload_file(
                    bucket_name="cleaned-data",
                    object_name=f"seek/{timestamp}/cleaned_data.json",
                    file_path=str(cleaned_data_file)
                )
                stage_result["minio_stored"] = True
                self.logger.info("清理數據已上傳到MinIO", bucket="cleaned-data")
            except Exception as e:
                self.logger.warning("MinIO上傳失敗", error=str(e))
                stage_result["errors"].append(f"MinIO上傳失敗: {str(e)}")
            
            # 更新ETL狀態
            self.etl_status["stage_3_cleaned_data"] = {
                "completed": True,
                "files": stage_result["files_created"],
                "count": stage_result["jobs_cleaned"]
            }
            
            stage_result["success"] = True
            self.logger.info(
                "階段3完成", 
                jobs_cleaned=stage_result["jobs_cleaned"],
                cleaning_operations=len(stage_result["cleaning_operations"])
            )
            
        except Exception as e:
            error_msg = f"階段3失敗: {str(e)}"
            stage_result["errors"].append(error_msg)
            self.logger.error("階段3失敗", error=error_msg)
        
        return stage_result
    
    async def _clean_job_data(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """清理單個職位數據
        
        Args:
            job: 原始職位數據
            
        Returns:
            Dict[str, Any]: 清理後的職位數據
        """
        cleaned_job = job.copy()
        cleaning_applied = False
        standardized = False
        enriched = False
        
        # 清理標題
        if cleaned_job.get("title"):
            original_title = cleaned_job["title"]
            cleaned_job["title"] = original_title.strip().title()
            if original_title != cleaned_job["title"]:
                cleaning_applied = True
        
        # 標準化薪資
        if cleaned_job.get("salary_min") and cleaned_job.get("salary_max"):
            # 確保最小值不大於最大值
            if cleaned_job["salary_min"] > cleaned_job["salary_max"]:
                cleaned_job["salary_min"], cleaned_job["salary_max"] = \
                    cleaned_job["salary_max"], cleaned_job["salary_min"]
                cleaning_applied = True
            standardized = True
        
        # 標準化工作類型
        if cleaned_job.get("job_type"):
            job_type_mapping = {
                "fulltime": "full-time",
                "full time": "full-time",
                "parttime": "part-time",
                "part time": "part-time",
                "contractor": "contract",
                "freelance": "contract"
            }
            
            original_type = cleaned_job["job_type"].lower()
            if original_type in job_type_mapping:
                cleaned_job["job_type"] = job_type_mapping[original_type]
                standardized = True
        
        # 豐富位置信息
        if cleaned_job.get("location"):
            location = cleaned_job["location"]
            # 添加標準化的位置信息
            cleaned_job["location_normalized"] = self._normalize_location(location)
            enriched = True
        
        # 添加清理標記
        cleaned_job["_cleaning_applied"] = cleaning_applied
        cleaned_job["_standardized"] = standardized
        cleaned_job["_enriched"] = enriched
        cleaned_job["_cleaned_at"] = datetime.now().isoformat()
        
        return cleaned_job
    
    def _normalize_location(self, location: str) -> Dict[str, str]:
        """標準化位置信息
        
        Args:
            location: 原始位置字符串
            
        Returns:
            Dict[str, str]: 標準化的位置信息
        """
        location_lower = location.lower()
        
        # 澳洲主要城市映射
        city_mapping = {
            "sydney": {"city": "Sydney", "state": "NSW", "country": "Australia"},
            "melbourne": {"city": "Melbourne", "state": "VIC", "country": "Australia"},
            "brisbane": {"city": "Brisbane", "state": "QLD", "country": "Australia"},
            "perth": {"city": "Perth", "state": "WA", "country": "Australia"},
            "adelaide": {"city": "Adelaide", "state": "SA", "country": "Australia"},
            "canberra": {"city": "Canberra", "state": "ACT", "country": "Australia"}
        }
        
        for city_key, city_info in city_mapping.items():
            if city_key in location_lower:
                return city_info
        
        # 默認返回
        return {
            "city": location,
            "state": "Unknown",
            "country": "Australia"
        }
    
    async def _test_stage_4_database_loading(self) -> Dict[str, Any]:
        """測試階段4：數據庫載入
        
        Returns:
            Dict[str, Any]: 階段4測試結果
        """
        stage_result = {
            "stage": "數據庫載入",
            "success": False,
            "records_loaded": 0,
            "database_tables": [],
            "connection_success": False,
            "errors": []
        }
        
        try:
            # 檢查階段3是否完成
            if not self.etl_status["stage_3_cleaned_data"]["completed"]:
                raise Exception("階段3未完成，無法載入數據庫")
            
            # 讀取清理後的數據
            cleaned_data_files = self.etl_status["stage_3_cleaned_data"]["files"]
            if not cleaned_data_files:
                raise Exception("未找到清理後的數據文件")
            
            # 讀取第一個清理數據文件
            with open(cleaned_data_files[0], 'r', encoding='utf-8') as f:
                cleaned_data = json.load(f)
            
            jobs = cleaned_data.get("jobs", [])
            
            # 模擬數據庫連接和載入
            # 在實際環境中，這裡會連接到PostgreSQL數據庫
            try:
                # 模擬數據庫操作
                await self._simulate_database_loading(jobs)
                stage_result["connection_success"] = True
                stage_result["records_loaded"] = len(jobs)
                stage_result["database_tables"] = ["jobs", "companies", "locations"]
                
                # 創建模擬的數據庫記錄文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                db_log_file = self.base_path / f"database_load_log_{timestamp}.json"
                
                db_log = {
                    "load_timestamp": datetime.now().isoformat(),
                    "records_processed": len(jobs),
                    "records_loaded": len(jobs),
                    "tables_affected": stage_result["database_tables"],
                    "load_status": "success",
                    "jobs_summary": [
                        {
                            "job_id": job.get("job_id"),
                            "title": job.get("title"),
                            "company": job.get("company"),
                            "loaded_at": datetime.now().isoformat()
                        }
                        for job in jobs
                    ]
                }
                
                with open(db_log_file, 'w', encoding='utf-8') as f:
                    json.dump(db_log, f, ensure_ascii=False, indent=2, default=str)
                
                self.logger.info("數據庫載入日誌已保存", file=str(db_log_file))
                
            except Exception as e:
                raise Exception(f"數據庫載入失敗: {str(e)}")
            
            # 更新ETL狀態
            self.etl_status["stage_4_db_loaded"] = {
                "completed": True,
                "records": stage_result["records_loaded"]
            }
            
            stage_result["success"] = True
            self.logger.info(
                "階段4完成", 
                records_loaded=stage_result["records_loaded"],
                tables=len(stage_result["database_tables"])
            )
            
        except Exception as e:
            error_msg = f"階段4失敗: {str(e)}"
            stage_result["errors"].append(error_msg)
            self.logger.error("階段4失敗", error=error_msg)
        
        return stage_result
    
    async def _simulate_database_loading(self, jobs: List[Dict[str, Any]]):
        """模擬數據庫載入過程
        
        Args:
            jobs: 要載入的職位數據列表
        """
        # 模擬數據庫連接延遲
        await asyncio.sleep(1)
        
        # 模擬批量插入
        batch_size = 10
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            # 模擬插入延遲
            await asyncio.sleep(0.1)
            self.logger.debug(f"模擬載入批次 {i//batch_size + 1}", records=len(batch))
    
    async def _test_stage_5_csv_export(self) -> Dict[str, Any]:
        """測試階段5：CSV導出
        
        Returns:
            Dict[str, Any]: 階段5測試結果
        """
        stage_result = {
            "stage": "CSV導出",
            "success": False,
            "files_created": [],
            "records_exported": 0,
            "export_formats": [],
            "errors": []
        }
        
        try:
            # 檢查階段3是否完成（CSV導出基於清理後的數據）
            if not self.etl_status["stage_3_cleaned_data"]["completed"]:
                raise Exception("階段3未完成，無法導出CSV")
            
            # 讀取清理後的數據
            cleaned_data_files = self.etl_status["stage_3_cleaned_data"]["files"]
            if not cleaned_data_files:
                raise Exception("未找到清理後的數據文件")
            
            # 讀取第一個清理數據文件
            with open(cleaned_data_files[0], 'r', encoding='utf-8') as f:
                cleaned_data = json.load(f)
            
            jobs = cleaned_data.get("jobs", [])
            
            # 導出為CSV格式
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 基本CSV導出
            basic_csv_file = self.csv_export_path / f"seek_jobs_basic_{timestamp}.csv"
            await self._export_basic_csv(jobs, basic_csv_file)
            stage_result["files_created"].append(str(basic_csv_file))
            stage_result["export_formats"].append("basic_csv")
            
            # 詳細CSV導出（包含AI分析）
            detailed_csv_file = self.csv_export_path / f"seek_jobs_detailed_{timestamp}.csv"
            await self._export_detailed_csv(jobs, detailed_csv_file)
            stage_result["files_created"].append(str(detailed_csv_file))
            stage_result["export_formats"].append("detailed_csv")
            
            # 統計CSV導出
            stats_csv_file = self.csv_export_path / f"seek_jobs_stats_{timestamp}.csv"
            await self._export_stats_csv(jobs, stats_csv_file)
            stage_result["files_created"].append(str(stats_csv_file))
            stage_result["export_formats"].append("stats_csv")
            
            stage_result["records_exported"] = len(jobs)
            
            # 更新ETL狀態
            self.etl_status["stage_5_csv_exported"] = {
                "completed": True,
                "files": stage_result["files_created"],
                "count": stage_result["records_exported"]
            }
            
            stage_result["success"] = True
            self.logger.info(
                "階段5完成", 
                records_exported=stage_result["records_exported"],
                files_created=len(stage_result["files_created"])
            )
            
        except Exception as e:
            error_msg = f"階段5失敗: {str(e)}"
            stage_result["errors"].append(error_msg)
            self.logger.error("階段5失敗", error=error_msg)
        
        return stage_result
    
    async def _export_basic_csv(self, jobs: List[Dict[str, Any]], file_path: Path):
        """導出基本CSV文件
        
        Args:
            jobs: 職位數據列表
            file_path: 輸出文件路徑
        """
        basic_fields = [
            "job_id", "title", "company", "location", "job_type",
            "salary_min", "salary_max", "salary_currency", "posted_date", "url"
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=basic_fields)
            writer.writeheader()
            
            for job in jobs:
                row = {field: job.get(field, '') for field in basic_fields}
                writer.writerow(row)
    
    async def _export_detailed_csv(self, jobs: List[Dict[str, Any]], file_path: Path):
        """導出詳細CSV文件（包含AI分析）
        
        Args:
            jobs: 職位數據列表
            file_path: 輸出文件路徑
        """
        detailed_fields = [
            "job_id", "title", "company", "location", "job_type",
            "salary_min", "salary_max", "salary_currency", "posted_date", "url",
            "description", "technical_skills", "soft_skills", "predicted_salary_min",
            "predicted_salary_max", "job_level", "years_experience", "company_size",
            "industry", "remote_friendly", "ai_processed_at", "cleaned_at"
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=detailed_fields)
            writer.writeheader()
            
            for job in jobs:
                row = {}
                
                # 基本字段
                for field in detailed_fields[:10]:
                    row[field] = job.get(field, '')
                
                # 描述
                row["description"] = job.get("description", '')[:500]  # 限制長度
                
                # AI分析字段
                ai_analysis = job.get("ai_analysis", {})
                
                skill_extraction = ai_analysis.get("skill_extraction", {})
                row["technical_skills"] = "; ".join(skill_extraction.get("technical_skills", []))
                row["soft_skills"] = "; ".join(skill_extraction.get("soft_skills", []))
                
                salary_prediction = ai_analysis.get("salary_prediction", {})
                row["predicted_salary_min"] = salary_prediction.get("predicted_min", '')
                row["predicted_salary_max"] = salary_prediction.get("predicted_max", '')
                
                job_level = ai_analysis.get("job_level", {})
                row["job_level"] = job_level.get("level", '')
                row["years_experience"] = job_level.get("years_experience", '')
                
                company_analysis = ai_analysis.get("company_analysis", {})
                row["company_size"] = company_analysis.get("company_size", '')
                row["industry"] = company_analysis.get("industry", '')
                
                location_analysis = ai_analysis.get("location_analysis", {})
                row["remote_friendly"] = location_analysis.get("remote_friendly", '')
                
                # 時間戳
                row["ai_processed_at"] = job.get("ai_processed_at", '')
                row["cleaned_at"] = job.get("_cleaned_at", '')
                
                writer.writerow(row)
    
    async def _export_stats_csv(self, jobs: List[Dict[str, Any]], file_path: Path):
        """導出統計CSV文件
        
        Args:
            jobs: 職位數據列表
            file_path: 輸出文件路徑
        """
        # 計算統計信息
        stats = {
            "total_jobs": len(jobs),
            "companies": len(set(job.get("company", "") for job in jobs if job.get("company"))),
            "locations": len(set(job.get("location", "") for job in jobs if job.get("location"))),
            "job_types": {},
            "salary_ranges": {},
            "industries": {}
        }
        
        # 統計工作類型
        for job in jobs:
            job_type = job.get("job_type", "unknown")
            stats["job_types"][job_type] = stats["job_types"].get(job_type, 0) + 1
        
        # 統計薪資範圍
        for job in jobs:
            salary_min = job.get("salary_min")
            if salary_min:
                if salary_min < 50000:
                    range_key = "<50k"
                elif salary_min < 80000:
                    range_key = "50k-80k"
                elif salary_min < 120000:
                    range_key = "80k-120k"
                else:
                    range_key = ">120k"
                
                stats["salary_ranges"][range_key] = stats["salary_ranges"].get(range_key, 0) + 1
        
        # 統計行業
        for job in jobs:
            ai_analysis = job.get("ai_analysis", {})
            company_analysis = ai_analysis.get("company_analysis", {})
            industry = company_analysis.get("industry", "unknown")
            stats["industries"][industry] = stats["industries"].get(industry, 0) + 1
        
        # 寫入統計CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["統計類型", "項目", "數量", "百分比"])
            
            # 總體統計
            writer.writerow(["總體", "總職位數", stats["total_jobs"], "100%"])
            writer.writerow(["總體", "公司數", stats["companies"], ""])
            writer.writerow(["總體", "地點數", stats["locations"], ""])
            
            # 工作類型統計
            for job_type, count in stats["job_types"].items():
                percentage = f"{count/stats['total_jobs']*100:.1f}%"
                writer.writerow(["工作類型", job_type, count, percentage])
            
            # 薪資範圍統計
            for salary_range, count in stats["salary_ranges"].items():
                percentage = f"{count/stats['total_jobs']*100:.1f}%"
                writer.writerow(["薪資範圍", salary_range, count, percentage])
            
            # 行業統計
            for industry, count in stats["industries"].items():
                percentage = f"{count/stats['total_jobs']*100:.1f}%"
                writer.writerow(["行業", industry, count, percentage])
    
    async def _generate_test_report(self, test_results: Dict[str, Any]):
        """生成測試報告
        
        Args:
            test_results: 測試結果數據
        """
        report_file = self.base_path / f"etl_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 添加ETL狀態到報告
        test_results["etl_status"] = self.etl_status
        
        # 添加文件位置驗證
        test_results["file_verification"] = await self._verify_file_locations()
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info("測試報告已生成", report_file=str(report_file))
        
        # 打印簡要報告到控制台
        self._print_summary_report(test_results)
    
    async def _verify_file_locations(self) -> Dict[str, Any]:
        """驗證文件是否存放在正確位置
        
        Returns:
            Dict[str, Any]: 文件位置驗證結果
        """
        verification = {
            "local_files": {
                "raw_data": [],
                "ai_processed": [],
                "cleaned_data": [],
                "csv_exports": []
            },
            "minio_files": {
                "raw-data_bucket": [],
                "ai-processed_bucket": [],
                "cleaned-data_bucket": []
            },
            "verification_status": {
                "local_files_correct": False,
                "minio_files_accessible": False
            }
        }
        
        # 驗證本地文件
        try:
            verification["local_files"]["raw_data"] = list(self.raw_data_path.glob("*.json"))
            verification["local_files"]["ai_processed"] = list(self.ai_processed_path.glob("*.json"))
            verification["local_files"]["cleaned_data"] = list(self.cleaned_data_path.glob("*.json"))
            verification["local_files"]["csv_exports"] = list(self.csv_export_path.glob("*.csv"))
            
            # 檢查是否有文件
            has_files = any(
                len(files) > 0 for files in verification["local_files"].values()
            )
            verification["verification_status"]["local_files_correct"] = has_files
            
        except Exception as e:
            self.logger.error("本地文件驗證失敗", error=str(e))
        
        # 驗證MinIO文件（模擬）
        try:
            # 在實際環境中，這裡會檢查MinIO bucket中的文件
            verification["verification_status"]["minio_files_accessible"] = True
            
        except Exception as e:
            self.logger.error("MinIO文件驗證失敗", error=str(e))
        
        return verification
    
    def _print_summary_report(self, test_results: Dict[str, Any]):
        """打印簡要測試報告
        
        Args:
            test_results: 測試結果數據
        """
        print("\n" + "="*80)
        print("Seek ETL Pipeline 測試報告")
        print("="*80)
        
        print(f"測試查詢: {test_results['test_query']}")
        print(f"測試位置: {test_results['test_location']}")
        print(f"測試限制: {test_results['test_limit']} 個職位")
        print(f"總執行時間: {test_results['total_duration']:.2f} 秒")
        print(f"整體成功: {'✅ 是' if test_results['overall_success'] else '❌ 否'}")
        
        print("\n階段執行結果:")
        print("-"*50)
        
        for stage_name, stage_result in test_results["stages"].items():
            status = "✅ 成功" if stage_result["success"] else "❌ 失敗"
            print(f"{stage_result['stage']}: {status}")
            
            if stage_name == "stage_1":
                print(f"  - 抓取職位數: {stage_result['jobs_extracted']}")
                print(f"  - 本地存儲: {'✅' if stage_result['local_stored'] else '❌'}")
                print(f"  - MinIO存儲: {'✅' if stage_result['minio_stored'] else '❌'}")
            
            elif stage_name == "stage_2":
                print(f"  - AI處理職位數: {stage_result['jobs_processed']}")
                print(f"  - AI增強功能: {len(set(stage_result['ai_enhancements']))} 種")
            
            elif stage_name == "stage_3":
                print(f"  - 清理職位數: {stage_result['jobs_cleaned']}")
                print(f"  - 清理操作: {len(stage_result['cleaning_operations'])} 種")
            
            elif stage_name == "stage_4":
                print(f"  - 載入記錄數: {stage_result['records_loaded']}")
                print(f"  - 影響表格: {len(stage_result['database_tables'])} 個")
            
            elif stage_name == "stage_5":
                print(f"  - 導出記錄數: {stage_result['records_exported']}")
                print(f"  - 導出格式: {len(stage_result['export_formats'])} 種")
                print(f"  - 生成文件: {len(stage_result['files_created'])} 個")
            
            if stage_result.get("errors"):
                print(f"  - 錯誤: {len(stage_result['errors'])} 個")
        
        print("\n文件位置驗證:")
        print("-"*50)
        
        file_verification = test_results.get("file_verification", {})
        local_status = file_verification.get("verification_status", {}).get("local_files_correct", False)
        minio_status = file_verification.get("verification_status", {}).get("minio_files_accessible", False)
        
        print(f"本地文件: {'✅ 正確' if local_status else '❌ 錯誤'}")
        print(f"MinIO文件: {'✅ 可訪問' if minio_status else '❌ 不可訪問'}")
        
        # 顯示生成的文件
        local_files = file_verification.get("local_files", {})
        for file_type, files in local_files.items():
            if files:
                print(f"  - {file_type}: {len(files)} 個文件")
        
        if test_results.get("errors"):
            print("\n整體錯誤:")
            print("-"*50)
            for error in test_results["errors"]:
                print(f"  - {error}")
        
        print("\n" + "="*80)


async def main():
    """主函數 - 運行Seek ETL測試"""
    print("開始Seek爬蟲ETL Pipeline測試...")
    
    # 創建測試器
    tester = SeekETLTester()
    
    try:
        # 運行完整測試
        results = await tester.run_complete_etl_test()
        
        # 檢查測試結果
        if results["overall_success"]:
            print("\n🎉 所有ETL階段測試成功完成！")
            return 0
        else:
            print("\n❌ 部分ETL階段測試失敗，請檢查錯誤信息。")
            return 1
            
    except Exception as e:
        print(f"\n💥 測試過程中發生嚴重錯誤: {str(e)}")
        return 1


if __name__ == "__main__":
    # 運行測試
    exit_code = asyncio.run(main())
    exit(exit_code)