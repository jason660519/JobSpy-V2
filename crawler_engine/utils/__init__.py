"""工具模組

提供通用的工具函數和裝飾器。
"""

from .retry_decorator import (
    RetryConfig,
    async_retry,
    sync_retry,
    NETWORK_RETRY_CONFIG,
    API_RETRY_CONFIG,
    SCRAPING_RETRY_CONFIG
)

__all__ = [
    "RetryConfig",
    "async_retry",
    "sync_retry",
    "NETWORK_RETRY_CONFIG",
    "API_RETRY_CONFIG",
    "SCRAPING_RETRY_CONFIG"
]