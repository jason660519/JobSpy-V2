#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seek ETL Pipeline 完整測試腳本

此腳本用於測試 Seek 平台的完整 ETL 流程，包括：
1. 數據抓取
2. AI 解析處理
3. 數據清理
4. 數據庫載入
5. CSV 導出
"""

import asyncio
import logging
import sys
from pathlib import Path
import time
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from crawler_engine.platforms.seek import SeekETLProcessor, SeekConfig
from crawler_engine.configuration.ai_config import AIConfig
from crawler_engine.configuration.storage_config import StorageConfig
from crawler_engine.configuration.export_config import ExportConfig

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'seek_pipeline_test_{int(time.time())}.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def test_seek_etl_pipeline():
    """測試 Seek ETL Pipeline"""
    logger.info("=" * 60)
    logger.info("開始 Seek ETL Pipeline 完整測試")
    logger.info("=" * 60)
    
    try:
        # 1. 初始化配置
        logger.info("步驟 1: 初始化配置")
        
        # Seek 平台配置
        seek_config = SeekConfig()
        
        # AI 配置
        ai_config = AIConfig(
            openai_api_key="your-openai-api-key",  # 請替換為實際的 API key
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0.1
        )
        
        # 存儲配置
        storage_config = StorageConfig(
            minio_endpoint="localhost:9000",
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin",
            minio_secure=False,
            database_url="sqlite:///seek_jobs.db"
        )
        
        # 導出配置
        export_config = ExportConfig(
            output_dir="./exports",
            file_format="csv",
            include_headers=True
        )
        
        # 2. 初始化 ETL 處理器
        logger.info("步驟 2: 初始化 ETL 處理器")
        etl_processor = SeekETLProcessor(
            seek_config=seek_config,
            ai_config=ai_config,
            storage_config=storage_config,
            export_config=export_config
        )
        
        # 3. 執行完整 ETL 流程
        logger.info("步驟 3: 執行完整 ETL 流程")
        
        # 測試搜索參數
        search_params = {
            'keywords': 'python developer',
            'location': 'Sydney',
            'limit': 10  # 限制數量以便測試
        }
        
        start_time = time.time()
        
        # 執行 ETL 流程
        results = await etl_processor.run_etl_pipeline(
            search_params=search_params,
            enable_ai_processing=True,
            batch_size=5
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 4. 驗證結果
        logger.info("步驟 4: 驗證結果")
        
        if results:
            logger.info(f"✅ ETL 流程執行成功！")
            logger.info(f"📊 處理統計:")
            logger.info(f"   - 總處理時間: {processing_time:.2f} 秒")
            logger.info(f"   - 原始數據: {results.get('raw_jobs_count', 0)} 條")
            logger.info(f"   - AI 處理: {results.get('ai_processed_count', 0)} 條")
            logger.info(f"   - 清理後: {results.get('cleaned_jobs_count', 0)} 條")
            logger.info(f"   - 數據庫存儲: {results.get('stored_jobs_count', 0)} 條")
            logger.info(f"   - CSV 導出: {results.get('csv_export_path', 'N/A')}")
            
            # 檢查文件存放位置
            logger.info(f"📁 文件存放位置:")
            if results.get('csv_export_path'):
                csv_path = Path(results['csv_export_path'])
                if csv_path.exists():
                    logger.info(f"   ✅ CSV 文件: {csv_path.absolute()}")
                    logger.info(f"   📏 文件大小: {csv_path.stat().st_size} bytes")
                else:
                    logger.warning(f"   ❌ CSV 文件不存在: {csv_path}")
            
            # 檢查數據庫
            db_stats = await etl_processor.database_storage.get_stats()
            if db_stats:
                logger.info(f"   📊 數據庫統計: {db_stats}")
            
        else:
            logger.error("❌ ETL 流程執行失敗，未返回結果")
            return False
        
        # 5. 清理測試數據（可選）
        logger.info("步驟 5: 測試完成")
        logger.info("💡 提示: 如需清理測試數據，請手動刪除生成的文件")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ETL Pipeline 測試失敗: {e}")
        logger.exception("詳細錯誤信息:")
        return False


async def test_individual_stages():
    """測試各個獨立階段"""
    logger.info("\n" + "=" * 60)
    logger.info("開始各階段獨立測試")
    logger.info("=" * 60)
    
    try:
        # 初始化配置（簡化版）
        seek_config = SeekConfig()
        ai_config = AIConfig(openai_api_key="test-key")
        storage_config = StorageConfig()
        export_config = ExportConfig()
        
        etl_processor = SeekETLProcessor(
            seek_config=seek_config,
            ai_config=ai_config,
            storage_config=storage_config,
            export_config=export_config
        )
        
        # 測試數據抓取
        logger.info("🔍 測試階段 1: 數據抓取")
        search_params = {'keywords': 'test', 'limit': 3}
        raw_jobs = await etl_processor._scrape_jobs(search_params)
        logger.info(f"   抓取到 {len(raw_jobs)} 條原始數據")
        
        if raw_jobs:
            # 測試 AI 處理
            logger.info("🤖 測試階段 2: AI 處理")
            ai_jobs = await etl_processor._process_with_ai(raw_jobs[:2])  # 只處理前2條
            logger.info(f"   AI 處理了 {len(ai_jobs)} 條數據")
            
            # 測試數據清理
            logger.info("🧹 測試階段 3: 數據清理")
            cleaned_jobs = await etl_processor._clean_jobs(ai_jobs)
            logger.info(f"   清理後保留 {len(cleaned_jobs)} 條數據")
            
            # 測試數據庫載入
            logger.info("💾 測試階段 4: 數據庫載入")
            if cleaned_jobs:
                stored_count = await etl_processor._load_to_database(cleaned_jobs)
                logger.info(f"   存儲了 {stored_count} 條數據到數據庫")
                
                # 測試 CSV 導出
                logger.info("📄 測試階段 5: CSV 導出")
                csv_path = await etl_processor._export_to_csv(cleaned_jobs)
                logger.info(f"   CSV 導出到: {csv_path}")
        
        logger.info("✅ 各階段獨立測試完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 各階段測試失敗: {e}")
        logger.exception("詳細錯誤信息:")
        return False


async def main():
    """主函數"""
    logger.info(f"🚀 Seek ETL Pipeline 測試開始 - {datetime.now()}")
    
    # 測試完整 ETL 流程
    success1 = await test_seek_etl_pipeline()
    
    # 測試各個獨立階段
    success2 = await test_individual_stages()
    
    # 總結
    logger.info("\n" + "=" * 60)
    logger.info("測試總結")
    logger.info("=" * 60)
    logger.info(f"完整 ETL 流程: {'✅ 通過' if success1 else '❌ 失敗'}")
    logger.info(f"各階段獨立測試: {'✅ 通過' if success2 else '❌ 失敗'}")
    logger.info(f"總體結果: {'🎉 全部通過' if success1 and success2 else '⚠️ 部分失敗'}")
    logger.info(f"測試結束時間: {datetime.now()}")
    
    return success1 and success2


if __name__ == "__main__":
    # 運行測試
    result = asyncio.run(main())
    sys.exit(0 if result else 1)