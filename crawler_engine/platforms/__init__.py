"""多平台適配器

提供針對不同求職平台的專用適配器，包括Indeed、LinkedIn、Glassdoor等。
每個適配器實現平台特定的爬取邏輯、數據解析和反檢測策略。
"""

from .base import BasePlatformAdapter, PlatformCapability
from .registry import PlatformRegistry
from .indeed import IndeedAdapter
from .linkedin import LinkedInAdapter
from .glassdoor import GlassdoorAdapter

__all__ = [
    # 基礎類
    "BasePlatformAdapter",
    "PlatformCapability",
    
    # 註冊器
    "PlatformRegistry",
    
    # 平台適配器
    "IndeedAdapter",
    "LinkedInAdapter",
    "GlassdoorAdapter",
]

# 版本信息
__version__ = "1.0.0"

# 支持的平台列表
SUPPORTED_PLATFORMS = [
    "indeed",
    "linkedin", 
    "glassdoor"
]

# 平台能力映射
PLATFORM_CAPABILITIES = {
    "indeed": [
        PlatformCapability.JOB_SEARCH,
        PlatformCapability.JOB_DETAILS,
        PlatformCapability.COMPANY_INFO,
        PlatformCapability.SALARY_INFO
    ],
    "linkedin": [
        PlatformCapability.JOB_SEARCH,
        PlatformCapability.JOB_DETAILS,
        PlatformCapability.COMPANY_INFO,
        PlatformCapability.PROFILE_INFO
    ],
    "glassdoor": [
        PlatformCapability.JOB_SEARCH,
        PlatformCapability.JOB_DETAILS,
        PlatformCapability.COMPANY_INFO,
        PlatformCapability.SALARY_INFO,
        PlatformCapability.COMPANY_REVIEWS
    ]
}

def get_supported_platforms():
    """獲取支持的平台列表
    
    Returns:
        List[str]: 支持的平台名稱列表
    """
    return SUPPORTED_PLATFORMS.copy()

def get_platform_capabilities(platform: str):
    """獲取平台支持的功能
    
    Args:
        platform: 平台名稱
        
    Returns:
        List[PlatformCapability]: 平台支持的功能列表
    """
    return PLATFORM_CAPABILITIES.get(platform, [])

def is_platform_supported(platform: str) -> bool:
    """檢查平台是否支持
    
    Args:
        platform: 平台名稱
        
    Returns:
        bool: 是否支持該平台
    """
    return platform.lower() in SUPPORTED_PLATFORMS