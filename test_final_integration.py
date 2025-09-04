#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終整合測試腳本
測試完整的 JobSpy 爬蟲系統，包括所有組件的協同工作
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 導入必要的模組
try:
    from crawler_engine.platforms.seek.adapter import SeekAdapter
    from crawler_engine.models.search_request import SearchRequest
    from crawler_engine.models.job_data import JobData
    from crawler_engine.configuration.ai_config import AIConfig
    from crawler_engine.configuration.storage_config import StorageConfig
    from crawler_engine.configuration.scraping_config import ScrapingConfig
except ImportError as e:
    logger.error(f"導入模組失敗: {e}")
    sys.exit(1)


class IntegrationTestSuite:
    """整合測試套件"""
    
    def __init__(self):
        """初始化測試套件"""
        self.adapter = None
        self.test_results = []
        self.start_time = None
        
    def setup_configs(self):
        """設置測試配置"""
        logger.info("設置測試配置...")
        
        # AI 配置
        ai_config = AIConfig(
            openai_api_key="test-key",
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.7,
            enable_ai_processing=False,  # 測試時關閉 AI 處理
            batch_size=10,
            max_retries=3,
            timeout=30,
            max_cost_per_request=0.01,
            daily_cost_limit=1.0,
            custom_prompts={}
        )
        
        # 存儲配置
        storage_config = StorageConfig(
            minio_endpoint="localhost:9000",
            minio_access_key="test",
            minio_secret_key="test123",
            minio_secure=False,
            minio_region="us-east-1",
            database_url="sqlite:///test_jobs.db"
        )
        
        # 爬蟲配置
        scraping_config = ScrapingConfig(
            max_workers=2,
            request_delay=1.0,
            timeout=30,
            max_retries=3,
            rotate_user_agent=True,
            use_proxy=False,
            proxy_rotation=False,
            max_pages=2,  # 限制頁數以加快測試
            max_jobs_per_page=20,
            max_total_jobs=50
        )
        
        return ai_config, storage_config, scraping_config
    
    async def test_adapter_initialization(self, ai_config, storage_config, scraping_config):
        """測試適配器初始化"""
        logger.info("測試適配器初始化...")
        
        try:
            # 導入 create_seek_config 函數
            from crawler_engine.platforms.seek import create_seek_config
            
            # 創建 Seek 配置
            seek_config = create_seek_config()
            
            # 初始化適配器
            self.adapter = SeekAdapter(seek_config)
            
            # 驗證適配器屬性
            assert hasattr(self.adapter, 'config'), "適配器缺少 config 屬性"
            assert hasattr(self.adapter, 'platform_name'), "適配器缺少 platform_name 屬性"
            assert self.adapter.platform_name == 'seek', "平台名稱不正確"
            
            self.test_results.append(("適配器初始化", True, "成功"))
            logger.info("✅ 適配器初始化測試通過")
            return True
            
        except Exception as e:
            self.test_results.append(("適配器初始化", False, str(e)))
            logger.error(f"❌ 適配器初始化測試失敗: {e}")
            return False
    
    async def test_search_request_creation(self):
        """測試搜索請求創建"""
        logger.info("測試搜索請求創建...")
        
        try:
            search_request = SearchRequest(
                query="python developer",
                location="Sydney",
                job_type="full-time",
                salary_min=80000,
                salary_max=120000,
                date_posted="week",
                sort_by="relevance",
                page=1,
                per_page=10
            )
            
            # 驗證搜索請求屬性
            assert search_request.query == "python developer", "查詢參數不正確"
            assert search_request.location == "Sydney", "位置參數不正確"
            assert search_request.job_type == "full-time", "工作類型參數不正確"
            
            self.test_results.append(("搜索請求創建", True, "成功"))
            logger.info("✅ 搜索請求創建測試通過")
            return search_request
            
        except Exception as e:
            self.test_results.append(("搜索請求創建", False, str(e)))
            logger.error(f"❌ 搜索請求創建測試失敗: {e}")
            return None
    
    async def test_url_building(self, search_request):
        """測試 URL 構建"""
        logger.info("測試 URL 構建...")
        
        try:
            if not self.adapter or not search_request:
                raise ValueError("適配器或搜索請求未初始化")
            
            url = self.adapter.build_search_url(search_request)
            
            # 驗證 URL 格式
            assert url.startswith("https://www.seek.com.au/"), "URL 格式不正確"
            assert "python-developer" in url, "查詢參數未正確編碼到 URL"
            
            self.test_results.append(("URL 構建", True, f"URL: {url[:100]}..."))
            logger.info(f"✅ URL 構建測試通過: {url[:100]}...")
            return url
            
        except Exception as e:
            self.test_results.append(("URL 構建", False, str(e)))
            logger.error(f"❌ URL 構建測試失敗: {e}")
            return None
    
    async def test_search_execution(self, search_request):
        """測試搜索執行"""
        logger.info("測試搜索執行...")
        
        try:
            if not self.adapter or not search_request:
                raise ValueError("適配器或搜索請求未初始化")
            
            # 執行搜索
            search_result = await self.adapter.search_jobs(search_request)
            
            # 驗證搜索結果
            assert search_result is not None, "搜索結果為空"
            assert hasattr(search_result, 'jobs'), "搜索結果缺少 jobs 屬性"
            assert hasattr(search_result, 'total_results'), "搜索結果缺少 total_results 屬性"
            assert hasattr(search_result, 'success'), "搜索結果缺少 success 屬性"
            
            job_count = len(search_result.jobs) if search_result.jobs else 0
            
            self.test_results.append((
                "搜索執行", 
                search_result.success, 
                f"找到 {job_count} 個職位，總計 {search_result.total_results} 個結果"
            ))
            
            if search_result.success:
                logger.info(f"✅ 搜索執行測試通過: 找到 {job_count} 個職位")
            else:
                logger.warning(f"⚠️ 搜索執行部分成功: {search_result.error_message}")
            
            return search_result
            
        except Exception as e:
            self.test_results.append(("搜索執行", False, str(e)))
            logger.error(f"❌ 搜索執行測試失敗: {e}")
            return None
    
    async def test_job_details_extraction(self, search_result):
        """測試職位詳情提取"""
        logger.info("測試職位詳情提取...")
        
        try:
            if not self.adapter or not search_result or not search_result.jobs:
                logger.warning("跳過職位詳情提取測試：無可用職位")
                self.test_results.append(("職位詳情提取", True, "跳過：無可用職位"))
                return True
            
            # 選擇第一個職位進行詳情提取
            first_job = search_result.jobs[0]
            
            if not hasattr(first_job, 'url') or not first_job.url:
                logger.warning("跳過職位詳情提取測試：職位缺少 URL")
                self.test_results.append(("職位詳情提取", True, "跳過：職位缺少 URL"))
                return True
            
            # 提取職位詳情
            job_details = await self.adapter.get_job_details(first_job.url)
            
            # 驗證職位詳情
            if job_details:
                assert hasattr(job_details, 'title'), "職位詳情缺少 title 屬性"
                assert hasattr(job_details, 'company'), "職位詳情缺少 company 屬性"
                
                self.test_results.append((
                    "職位詳情提取", 
                    True, 
                    f"成功提取職位: {job_details.title[:50]}..."
                ))
                logger.info(f"✅ 職位詳情提取測試通過: {job_details.title[:50]}...")
            else:
                self.test_results.append(("職位詳情提取", False, "未能提取職位詳情"))
                logger.warning("⚠️ 職位詳情提取測試失敗：未能提取詳情")
            
            return job_details
            
        except Exception as e:
            self.test_results.append(("職位詳情提取", False, str(e)))
            logger.error(f"❌ 職位詳情提取測試失敗: {e}")
            return None
    
    def print_test_summary(self):
        """打印測試摘要"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        logger.info("=" * 60)
        logger.info("整合測試摘要")
        logger.info("=" * 60)
        logger.info(f"測試開始時間: {self.start_time}")
        logger.info(f"測試結束時間: {end_time}")
        logger.info(f"總執行時間: {total_time:.2f} 秒")
        logger.info("-" * 60)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for test_name, success, message in self.test_results:
            status = "✅ 通過" if success else "❌ 失敗"
            logger.info(f"{test_name}: {status} - {message}")
            if success:
                passed_tests += 1
        
        logger.info("-" * 60)
        logger.info(f"測試結果: {passed_tests}/{total_tests} 通過")
        
        if passed_tests == total_tests:
            logger.info("🎉 所有測試通過！系統整合成功！")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} 個測試失敗")
        
        logger.info("=" * 60)
    
    async def run_all_tests(self):
        """運行所有測試"""
        self.start_time = datetime.now()
        logger.info("開始整合測試...")
        logger.info(f"測試時間: {self.start_time}")
        
        try:
            # 1. 設置配置
            ai_config, storage_config, scraping_config = self.setup_configs()
            
            # 2. 測試適配器初始化
            if not await self.test_adapter_initialization(ai_config, storage_config, scraping_config):
                logger.error("適配器初始化失敗，停止後續測試")
                return
            
            # 3. 測試搜索請求創建
            search_request = await self.test_search_request_creation()
            if not search_request:
                logger.error("搜索請求創建失敗，停止後續測試")
                return
            
            # 4. 測試 URL 構建
            url = await self.test_url_building(search_request)
            if not url:
                logger.error("URL 構建失敗，停止後續測試")
                return
            
            # 5. 測試搜索執行
            search_result = await self.test_search_execution(search_request)
            
            # 6. 測試職位詳情提取（即使搜索失敗也嘗試）
            await self.test_job_details_extraction(search_result)
            
        except Exception as e:
            logger.error(f"整合測試過程中發生未預期的錯誤: {e}")
            self.test_results.append(("整體測試", False, str(e)))
        
        finally:
            # 打印測試摘要
            self.print_test_summary()


async def main():
    """主函數"""
    logger.info("JobSpy 整合測試開始")
    
    # 創建並運行測試套件
    test_suite = IntegrationTestSuite()
    await test_suite.run_all_tests()
    
    logger.info("JobSpy 整合測試完成")


if __name__ == "__main__":
    # 運行整合測試
    asyncio.run(main())