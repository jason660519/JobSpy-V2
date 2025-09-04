"""平台適配器基礎類

定義所有平台適配器的通用接口和基礎功能。
"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog
from playwright.async_api import Page, BrowserContext

logger = structlog.get_logger(__name__)


class PlatformCapability(Enum):
    """平台功能枚舉"""
    JOB_SEARCH = "job_search"  # 職位搜索
    JOB_DETAILS = "job_details"  # 職位詳情
    COMPANY_INFO = "company_info"  # 公司信息
    SALARY_INFO = "salary_info"  # 薪資信息
    COMPANY_REVIEWS = "company_reviews"  # 公司評價
    PROFILE_INFO = "profile_info"  # 個人資料
    APPLICATION_TRACKING = "application_tracking"  # 申請追蹤


class SearchMethod(Enum):
    """搜索方法枚舉"""
    API = "api"  # API接口
    WEB_SCRAPING = "web_scraping"  # 網頁爬取
    AI_VISION = "ai_vision"  # AI視覺分析
    HYBRID = "hybrid"  # 混合模式


@dataclass
class PlatformConfig:
    """平台配置"""
    name: str
    base_url: str
    search_url: str
    job_detail_url_pattern: str
    
    # 搜索配置
    max_results_per_page: int = 25
    max_pages: int = 10
    search_delay_range: tuple = (2, 5)  # 搜索間隔（秒）
    
    # 反檢測配置
    use_proxy: bool = True
    rotate_user_agent: bool = True
    simulate_human_behavior: bool = True
    
    # API配置（如果支持）
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    rate_limit_per_minute: int = 60
    
    # 選擇器配置
    selectors: Dict[str, str] = field(default_factory=dict)
    
    # 其他配置
    timeout: int = 30
    retry_attempts: int = 3
    enable_screenshots: bool = True


@dataclass
class SearchRequest:
    """搜索請求"""
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    experience_level: Optional[str] = None  # entry, mid, senior
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    company: Optional[str] = None
    date_posted: Optional[str] = None  # 24h, 3d, 7d, 14d, 30d
    remote: Optional[bool] = None
    
    # 分頁參數
    page: int = 1
    limit: int = 25
    
    # 排序參數
    sort_by: str = "relevance"  # relevance, date, salary
    
    # 額外參數
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobData:
    """標準化職位數據"""
    # 基本信息
    title: str
    company: str
    location: str
    url: str
    
    # 詳細信息
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    
    # 薪資信息
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    salary_period: str = "yearly"  # yearly, monthly, hourly
    
    # 工作類型
    job_type: Optional[str] = None  # full-time, part-time, contract
    experience_level: Optional[str] = None
    remote: Optional[bool] = None
    
    # 時間信息
    posted_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    
    # 公司信息
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    company_logo_url: Optional[str] = None
    
    # 元數據
    platform: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    
    # 唯一標識
    job_id: Optional[str] = None
    external_id: Optional[str] = None


@dataclass
class SearchResult:
    """搜索結果"""
    jobs: List[JobData]
    total_count: int
    page: int
    has_next_page: bool
    search_query: str
    platform: str
    
    # 執行信息
    execution_time: float
    method_used: SearchMethod
    success: bool = True
    error_message: Optional[str] = None
    
    # 統計信息
    scraped_count: int = 0
    filtered_count: int = 0
    duplicate_count: int = 0
    
    # 元數據
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BasePlatformAdapter(ABC):
    """平台適配器基礎類
    
    所有平台適配器都應該繼承此類並實現抽象方法。
    """
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.logger = logger.bind(platform=config.name)
        
        # 統計信息
        self._stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "total_jobs_found": 0,
            "total_execution_time": 0.0,
            "api_calls": 0,
            "scraping_requests": 0,
            "ai_vision_requests": 0
        }
        
        # 速率限制
        self._last_request_time = None
        self._request_count = 0
        self._request_window_start = datetime.now()
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名稱"""
        pass
    
    @property
    @abstractmethod
    def supported_capabilities(self) -> List[PlatformCapability]:
        """支持的功能列表"""
        pass
    
    @property
    @abstractmethod
    def supported_methods(self) -> List[SearchMethod]:
        """支持的搜索方法"""
        pass
    
    @abstractmethod
    async def search_jobs(self, request: SearchRequest, 
                         method: SearchMethod = SearchMethod.WEB_SCRAPING) -> SearchResult:
        """搜索職位
        
        Args:
            request: 搜索請求
            method: 搜索方法
            
        Returns:
            SearchResult: 搜索結果
        """
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str, 
                            method: SearchMethod = SearchMethod.WEB_SCRAPING) -> Optional[JobData]:
        """獲取職位詳情
        
        Args:
            job_url: 職位URL
            method: 獲取方法
            
        Returns:
            Optional[JobData]: 職位詳情
        """
        pass
    
    @abstractmethod
    def build_search_url(self, request: SearchRequest) -> str:
        """構建搜索URL
        
        Args:
            request: 搜索請求
            
        Returns:
            str: 搜索URL
        """
        pass
    
    @abstractmethod
    async def extract_job_links(self, page: Page) -> List[str]:
        """從搜索結果頁面提取職位鏈接
        
        Args:
            page: 頁面對象
            
        Returns:
            List[str]: 職位鏈接列表
        """
        pass
    
    @abstractmethod
    async def parse_job_data(self, page: Page, job_url: str) -> Optional[JobData]:
        """解析職位數據
        
        Args:
            page: 頁面對象
            job_url: 職位URL
            
        Returns:
            Optional[JobData]: 解析的職位數據
        """
        pass
    
    # 通用方法
    
    async def validate_request(self, request: SearchRequest) -> bool:
        """驗證搜索請求
        
        Args:
            request: 搜索請求
            
        Returns:
            bool: 是否有效
        """
        if not request.query or not request.query.strip():
            self.logger.warning("搜索查詢為空")
            return False
        
        if request.page < 1:
            self.logger.warning("頁碼無效", page=request.page)
            return False
        
        if request.limit < 1 or request.limit > self.config.max_results_per_page:
            self.logger.warning(
                "每頁結果數量無效", 
                limit=request.limit, 
                max_allowed=self.config.max_results_per_page
            )
            return False
        
        return True
    
    async def check_rate_limit(self) -> bool:
        """檢查速率限制
        
        Returns:
            bool: 是否可以繼續請求
        """
        now = datetime.now()
        
        # 重置計數器（每分鐘）
        if (now - self._request_window_start).total_seconds() >= 60:
            self._request_count = 0
            self._request_window_start = now
        
        # 檢查速率限制
        if self._request_count >= self.config.rate_limit_per_minute:
            wait_time = 60 - (now - self._request_window_start).total_seconds()
            if wait_time > 0:
                self.logger.info("達到速率限制，等待中", wait_seconds=wait_time)
                await asyncio.sleep(wait_time)
                self._request_count = 0
                self._request_window_start = datetime.now()
        
        # 檢查請求間隔
        if self._last_request_time:
            min_delay, max_delay = self.config.search_delay_range
            elapsed = (now - self._last_request_time).total_seconds()
            if elapsed < min_delay:
                wait_time = min_delay - elapsed
                await asyncio.sleep(wait_time)
        
        self._last_request_time = datetime.now()
        self._request_count += 1
        
        return True
    
    def supports_capability(self, capability: PlatformCapability) -> bool:
        """檢查是否支持特定功能
        
        Args:
            capability: 功能類型
            
        Returns:
            bool: 是否支持
        """
        return capability in self.supported_capabilities
    
    def supports_method(self, method: SearchMethod) -> bool:
        """檢查是否支持特定搜索方法
        
        Args:
            method: 搜索方法
            
        Returns:
            bool: 是否支持
        """
        return method in self.supported_methods
    
    def get_best_method(self, request: SearchRequest) -> SearchMethod:
        """獲取最佳搜索方法
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchMethod: 推薦的搜索方法
        """
        # 優先級：API > 混合 > 網頁爬取 > AI視覺
        if SearchMethod.API in self.supported_methods and self.config.api_key:
            return SearchMethod.API
        elif SearchMethod.HYBRID in self.supported_methods:
            return SearchMethod.HYBRID
        elif SearchMethod.WEB_SCRAPING in self.supported_methods:
            return SearchMethod.WEB_SCRAPING
        elif SearchMethod.AI_VISION in self.supported_methods:
            return SearchMethod.AI_VISION
        else:
            return self.supported_methods[0] if self.supported_methods else SearchMethod.WEB_SCRAPING
    
    async def handle_pagination(self, page: Page) -> bool:
        """處理分頁
        
        Args:
            page: 頁面對象
            
        Returns:
            bool: 是否有下一頁
        """
        try:
            # 查找下一頁按鈕
            next_selectors = [
                'a[aria-label*="Next"]',
                'a[aria-label*="next"]',
                '.np:last-child',
                '[data-testid="pagination-page-next"]',
                '.pn',
                'a:has-text("Next")',
                'a:has-text("下一頁")',
                'button:has-text("Next")',
                'button:has-text("下一頁")'
            ]
            
            for selector in next_selectors:
                next_button = await page.query_selector(selector)
                if next_button:
                    # 檢查按鈕是否可點擊
                    is_disabled = await next_button.get_attribute("disabled")
                    if not is_disabled:
                        return True
            
            return False
            
        except Exception as e:
            self.logger.warning("檢查分頁失敗", error=str(e))
            return False
    
    async def click_next_page(self, page: Page) -> bool:
        """點擊下一頁
        
        Args:
            page: 頁面對象
            
        Returns:
            bool: 是否成功點擊
        """
        try:
            next_selectors = [
                'a[aria-label*="Next"]',
                'a[aria-label*="next"]',
                '.np:last-child',
                '[data-testid="pagination-page-next"]',
                '.pn',
                'a:has-text("Next")',
                'a:has-text("下一頁")',
                'button:has-text("Next")',
                'button:has-text("下一頁")'
            ]
            
            for selector in next_selectors:
                next_button = await page.query_selector(selector)
                if next_button:
                    is_disabled = await next_button.get_attribute("disabled")
                    if not is_disabled:
                        await next_button.click()
                        await page.wait_for_load_state("networkidle")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error("點擊下一頁失敗", error=str(e))
            return False
    
    def update_stats(self, search_result: SearchResult):
        """更新統計信息
        
        Args:
            search_result: 搜索結果
        """
        self._stats["total_searches"] += 1
        
        if search_result.success:
            self._stats["successful_searches"] += 1
            self._stats["total_jobs_found"] += len(search_result.jobs)
        else:
            self._stats["failed_searches"] += 1
        
        self._stats["total_execution_time"] += search_result.execution_time
        
        # 更新方法統計
        if search_result.method_used == SearchMethod.API:
            self._stats["api_calls"] += 1
        elif search_result.method_used == SearchMethod.WEB_SCRAPING:
            self._stats["scraping_requests"] += 1
        elif search_result.method_used == SearchMethod.AI_VISION:
            self._stats["ai_vision_requests"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = self._stats.copy()
        
        # 計算成功率
        if stats["total_searches"] > 0:
            stats["success_rate"] = (stats["successful_searches"] / stats["total_searches"]) * 100
        else:
            stats["success_rate"] = 0.0
        
        # 計算平均執行時間
        if stats["successful_searches"] > 0:
            stats["average_execution_time"] = stats["total_execution_time"] / stats["successful_searches"]
        else:
            stats["average_execution_time"] = 0.0
        
        # 計算平均每次搜索找到的職位數
        if stats["successful_searches"] > 0:
            stats["average_jobs_per_search"] = stats["total_jobs_found"] / stats["successful_searches"]
        else:
            stats["average_jobs_per_search"] = 0.0
        
        return stats
    
    async def cleanup(self):
        """清理資源"""
        self.logger.info("平台適配器清理完成", platform=self.platform_name)