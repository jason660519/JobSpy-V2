"""Seek 平台整合測試

測試完整的 ETL 流程，包括所有階段的整合測試。
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from crawler_engine.platforms.seek.etl_processor import SeekETLProcessor
from crawler_engine.platforms.seek.config import SeekConfig
from crawler_engine.data.storage import StorageConfig
from crawler_engine.data.exporter import ExportConfig, ExportFormat
from crawler_engine.config import AIConfig


class SeekETLTest:
    """Seek ETL 整合測試類"""
    
    def __init__(self):
        """初始化測試環境"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 測試配置
        self.seek_config = SeekConfig(
            max_pages=2,  # 限制頁數以加快測試
            jobs_per_page=10,
            request_delay=1.0  # 減少延遲
        )
        
        self.ai_config = {
            "openai_api_key": "your-openai-api-key",
            "openai_model": "gpt-3.5-turbo",
            "openai_base_url": "https://api.openai.com/v1"
        }
        
        self.storage_config = StorageConfig(
            backend="sqlite",
            connection_string="test_seek_jobs.db"
        )
        
        self.export_config = ExportConfig(
            format=ExportFormat.CSV,
            output_path="test_seek_export.csv",
            encoding="utf-8"
        )
    
    def setup_logging(self):
        """設置日誌配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('seek_etl_test.log', encoding='utf-8')
            ]
        )
    
    async def test_full_etl_pipeline(self):
        """測試完整的 ETL 流程"""
        self.logger.info("開始 Seek ETL 完整流程測試")
        
        try:
            # 初始化 ETL 處理器
            etl_processor = SeekETLProcessor(
                seek_config=self.seek_config,
                ai_config=self.ai_config,
                storage_config=self.storage_config,
                export_config=self.export_config
            )
            
            # 運行完整 ETL 流程
            results = await etl_processor.run_full_etl(
                keywords="python developer",
                location="Melbourne",
                max_jobs=20
            )
            
            # 輸出結果
            self.logger.info("ETL 流程完成")
            self.logger.info(f"處理結果: {results}")
            
            # 驗證結果
            self._validate_results(results)
            
            # 獲取統計信息
            stats = await etl_processor.get_processing_stats()
            self.logger.info(f"處理統計: {stats}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"ETL 測試失敗: {e}")
            raise
    
    def _validate_results(self, results):
        """驗證 ETL 結果"""
        assert "stages" in results, "結果中缺少 stages 信息"
        assert "total_jobs_processed" in results, "結果中缺少處理總數"
        
        # 檢查各階段是否完成
        expected_stages = ["extract", "ai_processing", "cleaning", "database_load", "csv_export"]
        for stage in expected_stages:
            assert stage in results["stages"], f"缺少階段: {stage}"
            assert results["stages"][stage]["status"] == "completed", f"階段 {stage} 未完成"
        
        # 檢查輸出檔案是否存在
        if "csv_export" in results["stages"]:
            export_path = results["stages"]["csv_export"].get("export_path")
            if export_path:
                assert Path(export_path).exists(), f"導出檔案不存在: {export_path}"
        
        self.logger.info("結果驗證通過")
    
    async def test_individual_stages(self):
        """測試各個階段的獨立功能"""
        self.logger.info("開始個別階段測試")
        
        try:
            etl_processor = SeekETLProcessor(
                seek_config=self.seek_config,
                ai_config=self.ai_config,
                storage_config=self.storage_config,
                export_config=self.export_config
            )
            
            # 測試數據抓取
            self.logger.info("測試數據抓取階段")
            raw_jobs = await etl_processor._extract_jobs("software engineer", "Sydney", 5)
            assert len(raw_jobs) > 0, "未抓取到任何職位數據"
            self.logger.info(f"成功抓取 {len(raw_jobs)} 個職位")
            
            # 測試 AI 處理（如果有 API key）
            if self.ai_config.get("openai_api_key") and self.ai_config["openai_api_key"] != "your-openai-api-key":
                self.logger.info("測試 AI 處理階段")
                ai_jobs = await etl_processor._ai_process_jobs(raw_jobs[:2])  # 只處理前2個
                assert len(ai_jobs) > 0, "AI 處理失敗"
                self.logger.info(f"AI 處理完成 {len(ai_jobs)} 個職位")
            else:
                self.logger.info("跳過 AI 處理測試（需要有效的 API key）")
                ai_jobs = raw_jobs
            
            # 測試數據清理
            self.logger.info("測試數據清理階段")
            cleaned_jobs = await etl_processor._clean_jobs(ai_jobs)
            assert len(cleaned_jobs) > 0, "數據清理失敗"
            self.logger.info(f"數據清理完成 {len(cleaned_jobs)} 個職位")
            
            # 測試數據庫載入
            self.logger.info("測試數據庫載入階段")
            loaded_count = await etl_processor._load_to_database(cleaned_jobs)
            assert loaded_count > 0, "數據庫載入失敗"
            self.logger.info(f"成功載入 {loaded_count} 個職位到數據庫")
            
            # 測試 CSV 導出
            self.logger.info("測試 CSV 導出階段")
            export_path = await etl_processor._export_to_csv(cleaned_jobs)
            assert export_path.exists(), "CSV 導出失敗"
            self.logger.info(f"CSV 導出完成: {export_path}")
            
            self.logger.info("所有個別階段測試通過")
            
        except Exception as e:
            self.logger.error(f"個別階段測試失敗: {e}")
            raise
    
    async def run_all_tests(self):
        """運行所有測試"""
        self.logger.info("開始運行所有 Seek ETL 測試")
        
        try:
            # 測試個別階段
            await self.test_individual_stages()
            
            # 測試完整流程
            results = await self.test_full_etl_pipeline()
            
            self.logger.info("所有測試完成")
            return results
            
        except Exception as e:
            self.logger.error(f"測試運行失敗: {e}")
            raise


async def main():
    """主測試函數"""
    test = SeekETLTest()
    
    try:
        results = await test.run_all_tests()
        print("\n=== 測試完成 ===")
        print(f"總處理職位數: {results.get('total_jobs_processed', 0)}")
        print(f"執行時間: {results.get('duration_seconds', 0):.2f} 秒")
        print(f"狀態: {results.get('status', 'unknown')}")
        
        if results.get('errors'):
            print(f"錯誤: {results['errors']}")
        
    except Exception as e:
        print(f"測試失敗: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # 運行測試
    success = asyncio.run(main())
    
    if success:
        print("\n✅ 所有測試通過")
    else:
        print("\n❌ 測試失敗")
        sys.exit(1)