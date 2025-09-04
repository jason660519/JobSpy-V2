"""智能爬蟲引擎模組

提供基於Playwright的智能爬蟲功能，包括反檢測、代理管理和自適應策略。
"""

from .smart_scraper import SmartScraper
from .anti_detection import AntiDetectionManager
from .proxy_manager import ProxyManager
from .browser_manager import BrowserManager
from .screenshot_service import ScreenshotService

__all__ = [
    'SmartScraper',
    'AntiDetectionManager',
    'ProxyManager', 
    'BrowserManager',
    'ScreenshotService'
]

__version__ = '1.0.0'