#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seek ETL Pipeline 簡化測試腳本
"""

import asyncio
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent))

from crawler_engine.platforms.seek import SeekETLProcessor, SeekConfig
from crawler_engine.configuration.ai_config import AIConfig
from crawler_engine.configuration.storage_config import StorageConfig
from crawler_engine.configuration.export_config import ExportConfig


async def test_seek_etl():
    """測試 Seek ETL Pipeline"""
    print("Starting Seek ETL Pipeline Test...")
    
    try:
        # 1. 初始化配置
        print("Step 1: Initializing configurations...")
        
        seek_config = SeekConfig()
        ai_config = AIConfig(openai_api_key="test-key")
        storage_config = StorageConfig()
        export_config = ExportConfig()
        
        # 2. 初始化 ETL 處理器
        print("Step 2: Initializing ETL processor...")
        etl_processor = SeekETLProcessor(
            seek_config=seek_config,
            ai_config=ai_config,
            storage_config=storage_config,
            export_config=export_config
        )
        
        print("ETL Processor initialized successfully!")
        
        # 3. 測試基本功能
        print("Step 3: Testing basic functionality...")
        
        # 測試配置
        print(f"Seek base URL: {seek_config.base_url}")
        print(f"AI enabled: {ai_config.is_enabled}")
        print(f"Storage database: {storage_config.database_url}")
        print(f"Export format: {export_config.file_format}")
        
        print("Basic functionality test completed!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


async def main():
    """主函數"""
    print("=" * 50)
    print("Seek ETL Pipeline Simple Test")
    print("=" * 50)
    
    success = await test_seek_etl()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)