"""JobSpy v2 爬蟲引擎

現代化的AI增強型求職爬蟲引擎，支持多平台智能數據採集。

核心功能:
- AI視覺分析 (GPT-4V)
- 智能反檢測爬蟲
- 多平台適配
- 成本控制機制
- 數據處理管道
"""

__version__ = "2.0.0"
__author__ = "JobSpy Team"

from .core.engine import CrawlerEngine
from .ai_vision.service import AIVisionService
from .scrapers.smart_scraper import SmartScraper
from .platforms import PlatformRegistry
from .config import CrawlerConfig

__all__ = [
    "CrawlerEngine",
    "AIVisionService", 
    "SmartScraper",
    "PlatformRegistry",
    "CrawlerConfig"
]