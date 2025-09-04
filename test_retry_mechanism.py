#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重試機制測試腳本

測試新添加的重試裝飾器功能。
"""

import asyncio
import logging
from datetime import datetime
from crawler_engine.utils import async_retry, RetryConfig, NETWORK_RETRY_CONFIG

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('retry_test.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class MockNetworkError(Exception):
    """模擬網絡錯誤"""
    pass


class TestRetryMechanism:
    """重試機制測試類"""
    
    def __init__(self):
        self.attempt_count = 0
        self.success_on_attempt = 3  # 第3次嘗試成功
    
    @async_retry(NETWORK_RETRY_CONFIG)
    async def simulate_network_request(self, should_succeed: bool = True) -> str:
        """
        模擬網絡請求
        
        Args:
            should_succeed: 是否最終成功
            
        Returns:
            str: 請求結果
        """
        self.attempt_count += 1
        logger.info(f"嘗試第 {self.attempt_count} 次網絡請求")
        
        # 模擬網絡延遲
        await asyncio.sleep(0.1)
        
        if should_succeed and self.attempt_count >= self.success_on_attempt:
            logger.info(f"網絡請求在第 {self.attempt_count} 次嘗試成功")
            return f"請求成功，嘗試次數: {self.attempt_count}"
        else:
            logger.warning(f"網絡請求第 {self.attempt_count} 次嘗試失敗")
            raise MockNetworkError(f"模擬網絡錯誤 - 嘗試 {self.attempt_count}")
    
    @async_retry(RetryConfig(max_attempts=2, base_delay=0.5))
    async def simulate_quick_fail(self) -> str:
        """
        模擬快速失敗的請求
        
        Returns:
            str: 請求結果
        """
        self.attempt_count += 1
        logger.info(f"快速失敗測試 - 嘗試第 {self.attempt_count} 次")
        raise MockNetworkError("總是失敗的請求")
    
    def reset(self):
        """重置計數器"""
        self.attempt_count = 0


async def test_successful_retry():
    """測試成功重試的情況"""
    logger.info("=" * 50)
    logger.info("測試 1: 成功重試")
    logger.info("=" * 50)
    
    tester = TestRetryMechanism()
    
    try:
        start_time = datetime.now()
        result = await tester.simulate_network_request(should_succeed=True)
        end_time = datetime.now()
        
        logger.info(f"測試結果: {result}")
        logger.info(f"總執行時間: {(end_time - start_time).total_seconds():.2f} 秒")
        logger.info("✅ 成功重試測試通過")
        
    except Exception as e:
        logger.error(f"❌ 成功重試測試失敗: {e}")


async def test_failed_retry():
    """測試重試失敗的情況"""
    logger.info("=" * 50)
    logger.info("測試 2: 重試失敗")
    logger.info("=" * 50)
    
    tester = TestRetryMechanism()
    tester.reset()
    
    try:
        start_time = datetime.now()
        result = await tester.simulate_network_request(should_succeed=False)
        end_time = datetime.now()
        
        logger.error("❌ 預期應該失敗，但卻成功了")
        
    except MockNetworkError as e:
        end_time = datetime.now()
        logger.info(f"預期的失敗: {e}")
        logger.info(f"總執行時間: {(end_time - start_time).total_seconds():.2f} 秒")
        logger.info(f"總嘗試次數: {tester.attempt_count}")
        logger.info("✅ 重試失敗測試通過")
    except Exception as e:
        logger.error(f"❌ 重試失敗測試出現意外錯誤: {e}")


async def test_quick_fail():
    """測試快速失敗配置"""
    logger.info("=" * 50)
    logger.info("測試 3: 快速失敗配置")
    logger.info("=" * 50)
    
    tester = TestRetryMechanism()
    tester.reset()
    
    try:
        start_time = datetime.now()
        result = await tester.simulate_quick_fail()
        end_time = datetime.now()
        
        logger.error("❌ 預期應該失敗，但卻成功了")
        
    except MockNetworkError as e:
        end_time = datetime.now()
        logger.info(f"預期的失敗: {e}")
        logger.info(f"總執行時間: {(end_time - start_time).total_seconds():.2f} 秒")
        logger.info(f"總嘗試次數: {tester.attempt_count}")
        
        if tester.attempt_count == 2:
            logger.info("✅ 快速失敗測試通過")
        else:
            logger.error(f"❌ 預期嘗試 2 次，實際嘗試 {tester.attempt_count} 次")
    except Exception as e:
        logger.error(f"❌ 快速失敗測試出現意外錯誤: {e}")


async def main():
    """主測試函數"""
    logger.info("開始重試機制測試")
    logger.info(f"測試時間: {datetime.now()}")
    
    try:
        # 測試 1: 成功重試
        await test_successful_retry()
        await asyncio.sleep(1)
        
        # 測試 2: 重試失敗
        await test_failed_retry()
        await asyncio.sleep(1)
        
        # 測試 3: 快速失敗
        await test_quick_fail()
        
        logger.info("=" * 50)
        logger.info("所有重試機制測試完成")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")


if __name__ == "__main__":
    asyncio.run(main())