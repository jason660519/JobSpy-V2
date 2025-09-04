"""重試裝飾器模組

提供網絡請求重試機制和錯誤處理功能。
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Union, List
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class RetryConfig:
    """重試配置類"""
    
    def __init__(self,
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True,
                 retry_exceptions: Optional[List[Type[Exception]]] = None):
        """
        初始化重試配置
        
        Args:
            max_attempts: 最大重試次數
            base_delay: 基礎延遲時間（秒）
            max_delay: 最大延遲時間（秒）
            exponential_base: 指數退避基數
            jitter: 是否添加隨機抖動
            retry_exceptions: 需要重試的異常類型列表
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions or [
            ConnectionError,
            TimeoutError,
            OSError,
            Exception  # 通用異常
        ]
    
    def calculate_delay(self, attempt: int) -> float:
        """
        計算延遲時間
        
        Args:
            attempt: 當前嘗試次數
            
        Returns:
            float: 延遲時間（秒）
        """
        # 指數退避
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        
        # 限制最大延遲
        delay = min(delay, self.max_delay)
        
        # 添加隨機抖動
        if self.jitter:
            jitter_range = delay * 0.1  # 10% 抖動
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def should_retry(self, exception: Exception) -> bool:
        """
        判斷是否應該重試
        
        Args:
            exception: 發生的異常
            
        Returns:
            bool: 是否應該重試
        """
        return any(isinstance(exception, exc_type) for exc_type in self.retry_exceptions)


def async_retry(config: Optional[RetryConfig] = None):
    """
    異步重試裝飾器
    
    Args:
        config: 重試配置，如果為 None 則使用默認配置
        
    Returns:
        裝飾器函數
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    start_time = datetime.now()
                    result = await func(*args, **kwargs)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    if attempt > 1:
                        logger.info(
                            f"函數 {func.__name__} 在第 {attempt} 次嘗試成功",
                            execution_time=execution_time
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # 檢查是否應該重試
                    if not config.should_retry(e):
                        logger.error(
                            f"函數 {func.__name__} 發生不可重試的異常",
                            exception=str(e),
                            attempt=attempt,
                            execution_time=execution_time
                        )
                        raise e
                    
                    # 如果是最後一次嘗試，直接拋出異常
                    if attempt == config.max_attempts:
                        logger.error(
                            f"函數 {func.__name__} 在 {config.max_attempts} 次嘗試後仍然失敗",
                            exception=str(e),
                            execution_time=execution_time
                        )
                        raise e
                    
                    # 計算延遲時間並等待
                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"函數 {func.__name__} 第 {attempt} 次嘗試失敗，{delay:.2f}秒後重試",
                        exception=str(e),
                        next_attempt=attempt + 1,
                        delay=delay,
                        execution_time=execution_time
                    )
                    
                    await asyncio.sleep(delay)
            
            # 這裡不應該到達，但為了安全起見
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def sync_retry(config: Optional[RetryConfig] = None):
    """
    同步重試裝飾器
    
    Args:
        config: 重試配置，如果為 None 則使用默認配置
        
    Returns:
        裝飾器函數
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    start_time = datetime.now()
                    result = func(*args, **kwargs)
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    if attempt > 1:
                        logger.info(
                            f"函數 {func.__name__} 在第 {attempt} 次嘗試成功",
                            execution_time=execution_time
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # 檢查是否應該重試
                    if not config.should_retry(e):
                        logger.error(
                            f"函數 {func.__name__} 發生不可重試的異常",
                            exception=str(e),
                            attempt=attempt,
                            execution_time=execution_time
                        )
                        raise e
                    
                    # 如果是最後一次嘗試，直接拋出異常
                    if attempt == config.max_attempts:
                        logger.error(
                            f"函數 {func.__name__} 在 {config.max_attempts} 次嘗試後仍然失敗",
                            exception=str(e),
                            execution_time=execution_time
                        )
                        raise e
                    
                    # 計算延遲時間並等待
                    delay = config.calculate_delay(attempt)
                    logger.warning(
                        f"函數 {func.__name__} 第 {attempt} 次嘗試失敗，{delay:.2f}秒後重試",
                        exception=str(e),
                        next_attempt=attempt + 1,
                        delay=delay,
                        execution_time=execution_time
                    )
                    
                    import time
                    time.sleep(delay)
            
            # 這裡不應該到達，但為了安全起見
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


# 預定義的重試配置
NETWORK_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
    retry_exceptions=[
        ConnectionError,
        TimeoutError,
        OSError,
        Exception
    ]
)

API_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=60.0,
    exponential_base=1.5,
    jitter=True,
    retry_exceptions=[
        ConnectionError,
        TimeoutError,
        OSError
    ]
)

SCRAPING_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=45.0,
    exponential_base=2.0,
    jitter=True,
    retry_exceptions=[
        ConnectionError,
        TimeoutError,
        OSError,
        Exception
    ]
)