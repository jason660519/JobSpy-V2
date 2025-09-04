"""智能爬蟲引擎

基於Playwright的智能爬蟲，集成反檢測、代理管理和自適應策略。
"""

import asyncio
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .anti_detection import AntiDetectionManager
from .proxy_manager import ProxyManager
from .browser_manager import BrowserManager
from .screenshot_service import ScreenshotService
from ..config import ScrapingConfig

logger = structlog.get_logger(__name__)


@dataclass
class ScrapingRequest:
    """爬蟲請求"""
    url: str
    platform: str
    search_query: Optional[str] = None
    max_pages: int = 1
    wait_time: float = 2.0
    screenshot: bool = True
    extract_links: bool = True
    custom_selectors: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class ScrapingResult:
    """爬蟲結果"""
    success: bool
    url: str
    platform: str
    html_content: str
    screenshot_data: Optional[bytes] = None
    extracted_data: Optional[Dict[str, Any]] = None
    links: List[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0


class SmartScraper:
    """智能爬蟲引擎
    
    提供智能化的網頁爬取功能，包括反檢測、自適應策略和錯誤恢復。
    """
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.logger = logger.bind(component="smart_scraper")
        
        # 初始化組件
        self.anti_detection = AntiDetectionManager(config)
        self.proxy_manager = ProxyManager(config.proxy_config) if config.proxy_config else None
        self.browser_manager = BrowserManager(config)
        self.screenshot_service = ScreenshotService()
        
        # 狀態管理
        self._playwright = None
        self._browser = None
        self._context = None
        self._is_initialized = False
        
        # 統計信息
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_pages_scraped": 0,
            "total_execution_time": 0.0
        }
    
    async def initialize(self):
        """初始化爬蟲引擎"""
        if self._is_initialized:
            return
        
        try:
            self.logger.info("正在初始化智能爬蟲引擎...")
            
            # 啟動Playwright
            self._playwright = await async_playwright().start()
            
            # 初始化瀏覽器管理器
            await self.browser_manager.initialize(self._playwright)
            
            # 初始化代理管理器
            if self.proxy_manager:
                await self.proxy_manager.initialize()
            
            self._is_initialized = True
            self.logger.info("智能爬蟲引擎初始化完成")
            
        except Exception as e:
            self.logger.error("爬蟲引擎初始化失敗", error=str(e))
            raise
    
    async def scrape(self, request: ScrapingRequest) -> ScrapingResult:
        """執行爬蟲任務
        
        Args:
            request: 爬蟲請求
            
        Returns:
            ScrapingResult: 爬蟲結果
        """
        start_time = asyncio.get_event_loop().time()
        self._stats["total_requests"] += 1
        
        try:
            self.logger.info(
                "開始爬蟲任務",
                url=request.url,
                platform=request.platform,
                max_pages=request.max_pages
            )
            
            # 確保已初始化
            if not self._is_initialized:
                await self.initialize()
            
            # 創建瀏覽器上下文
            context = await self._create_browser_context(request)
            
            try:
                # 執行爬蟲
                result = await self._execute_scraping(context, request)
                
                # 更新統計
                execution_time = asyncio.get_event_loop().time() - start_time
                result.execution_time = execution_time
                self._stats["total_execution_time"] += execution_time
                
                if result.success:
                    self._stats["successful_requests"] += 1
                    self._stats["total_pages_scraped"] += request.max_pages
                else:
                    self._stats["failed_requests"] += 1
                
                return result
                
            finally:
                # 清理上下文
                await context.close()
        
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self._stats["failed_requests"] += 1
            
            self.logger.error(
                "爬蟲任務失敗",
                url=request.url,
                error=str(e),
                execution_time=execution_time
            )
            
            return ScrapingResult(
                success=False,
                url=request.url,
                platform=request.platform,
                html_content="",
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def scrape_multiple(self, requests: List[ScrapingRequest], 
                            max_concurrent: int = 3) -> List[ScrapingResult]:
        """並發爬取多個URL
        
        Args:
            requests: 爬蟲請求列表
            max_concurrent: 最大並發數
            
        Returns:
            List[ScrapingResult]: 爬蟲結果列表
        """
        self.logger.info("開始並發爬蟲任務", total_requests=len(requests), max_concurrent=max_concurrent)
        
        # 創建信號量控制並發
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(request: ScrapingRequest) -> ScrapingResult:
            async with semaphore:
                return await self.scrape(request)
        
        # 執行並發爬蟲
        tasks = [scrape_with_semaphore(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理異常結果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ScrapingResult(
                    success=False,
                    url=requests[i].url,
                    platform=requests[i].platform,
                    html_content="",
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful_count = sum(1 for r in processed_results if r.success)
        self.logger.info(
            "並發爬蟲任務完成",
            total_requests=len(requests),
            successful_requests=successful_count,
            failed_requests=len(requests) - successful_count
        )
        
        return processed_results
    
    async def _create_browser_context(self, request: ScrapingRequest) -> BrowserContext:
        """創建瀏覽器上下文"""
        # 獲取瀏覽器實例
        browser = await self.browser_manager.get_browser()
        
        # 準備上下文選項
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": await self.anti_detection.get_random_user_agent(),
            "locale": "en-US",
            "timezone_id": "America/New_York"
        }
        
        # 添加代理配置
        if self.proxy_manager:
            proxy = await self.proxy_manager.get_proxy()
            if proxy:
                context_options["proxy"] = {
                    "server": f"{proxy['protocol']}://{proxy['host']}:{proxy['port']}",
                    "username": proxy.get('username'),
                    "password": proxy.get('password')
                }
        
        # 添加自定義headers
        if request.headers:
            context_options["extra_http_headers"] = request.headers
        
        # 創建上下文
        context = await browser.new_context(**context_options)
        
        # 應用反檢測措施
        await self.anti_detection.apply_stealth_mode(context)
        
        return context
    
    async def _execute_scraping(self, context: BrowserContext, 
                              request: ScrapingRequest) -> ScrapingResult:
        """執行實際的爬蟲操作"""
        page = await context.new_page()
        
        try:
            # 設置頁面事件監聽
            await self._setup_page_listeners(page)
            
            # 導航到目標URL
            await self._navigate_to_url(page, request)
            
            # 等待頁面加載
            await self._wait_for_page_load(page, request)
            
            # 處理多頁爬取
            all_content = []
            all_links = []
            screenshot_data = None
            
            for page_num in range(request.max_pages):
                self.logger.debug(f"正在爬取第 {page_num + 1} 頁", url=page.url)
                
                # 等待內容加載
                await asyncio.sleep(request.wait_time)
                
                # 獲取頁面內容
                content = await page.content()
                all_content.append(content)
                
                # 提取鏈接
                if request.extract_links:
                    links = await self._extract_links(page, request.platform)
                    all_links.extend(links)
                
                # 截圖（只在第一頁）
                if request.screenshot and page_num == 0:
                    screenshot_data = await self.screenshot_service.take_screenshot(page)
                
                # 導航到下一頁
                if page_num < request.max_pages - 1:
                    next_page_success = await self._navigate_to_next_page(page, request.platform)
                    if not next_page_success:
                        self.logger.info("無法導航到下一頁，停止爬取")
                        break
            
            # 提取結構化數據
            extracted_data = await self._extract_structured_data(page, request)
            
            # 生成元數據
            metadata = {
                "final_url": page.url,
                "pages_scraped": len(all_content),
                "total_links": len(all_links),
                "timestamp": datetime.now().isoformat(),
                "user_agent": await page.evaluate("navigator.userAgent")
            }
            
            return ScrapingResult(
                success=True,
                url=request.url,
                platform=request.platform,
                html_content="\n\n<!-- PAGE SEPARATOR -->\n\n".join(all_content),
                screenshot_data=screenshot_data,
                extracted_data=extracted_data,
                links=list(set(all_links)),  # 去重
                metadata=metadata
            )
        
        finally:
            await page.close()
    
    async def _setup_page_listeners(self, page: Page):
        """設置頁面事件監聽器"""
        # 監聽請求
        page.on("request", lambda request: self.logger.debug(
            "頁面請求", url=request.url, method=request.method
        ))
        
        # 監聽響應
        page.on("response", lambda response: self.logger.debug(
            "頁面響應", url=response.url, status=response.status
        ))
        
        # 監聽控制台消息
        page.on("console", lambda msg: self.logger.debug(
            "控制台消息", type=msg.type, text=msg.text
        ))
    
    async def _navigate_to_url(self, page: Page, request: ScrapingRequest):
        """導航到目標URL"""
        try:
            # 隨機延遲
            await asyncio.sleep(random.uniform(1, 3))
            
            # 導航到URL
            response = await page.goto(
                request.url,
                wait_until="domcontentloaded",
                timeout=30000
            )
            
            if response and response.status >= 400:
                raise Exception(f"HTTP錯誤: {response.status}")
            
            self.logger.debug("成功導航到URL", url=request.url)
            
        except Exception as e:
            self.logger.error("導航失敗", url=request.url, error=str(e))
            raise
    
    async def _wait_for_page_load(self, page: Page, request: ScrapingRequest):
        """等待頁面加載完成"""
        try:
            # 等待網絡空閒
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            # 平台特定的等待邏輯
            if request.platform.lower() == "linkedin":
                await self._wait_for_linkedin_load(page)
            elif request.platform.lower() == "indeed":
                await self._wait_for_indeed_load(page)
            elif request.platform.lower() == "glassdoor":
                await self._wait_for_glassdoor_load(page)
            
            # 額外等待時間
            await asyncio.sleep(request.wait_time)
            
        except Exception as e:
            self.logger.warning("頁面加載等待超時", error=str(e))
    
    async def _wait_for_linkedin_load(self, page: Page):
        """等待LinkedIn頁面加載"""
        try:
            # 等待職位列表容器
            await page.wait_for_selector(
                ".jobs-search__results-list, .job-search-results-list",
                timeout=10000
            )
        except:
            self.logger.debug("LinkedIn職位列表選擇器未找到")
    
    async def _wait_for_indeed_load(self, page: Page):
        """等待Indeed頁面加載"""
        try:
            # 等待職位列表容器
            await page.wait_for_selector(
                "#resultsCol, .jobsearch-SerpJobCard, [data-testid='job-result']",
                timeout=10000
            )
        except:
            self.logger.debug("Indeed職位列表選擇器未找到")
    
    async def _wait_for_glassdoor_load(self, page: Page):
        """等待Glassdoor頁面加載"""
        try:
            # 等待職位列表容器
            await page.wait_for_selector(
                ".JobsList_jobsList__lqjTr, .react-job-listing",
                timeout=10000
            )
        except:
            self.logger.debug("Glassdoor職位列表選擇器未找到")
    
    async def _extract_links(self, page: Page, platform: str) -> List[str]:
        """提取頁面鏈接"""
        try:
            # 平台特定的鏈接選擇器
            selectors = {
                "linkedin": "a[href*='/jobs/view/'], a[href*='/jobs/collections/']",
                "indeed": "a[href*='/viewjob'], a[href*='/clk']",
                "glassdoor": "a[href*='/job-listing/'], a[href*='/partner/jobListing']",
                "generic": "a[href]"
            }
            
            selector = selectors.get(platform.lower(), selectors["generic"])
            
            # 提取鏈接
            links = await page.evaluate(f"""
                () => {{
                    const elements = document.querySelectorAll('{selector}');
                    return Array.from(elements).map(el => el.href).filter(href => href);
                }}
            """)
            
            # 過濾和清理鏈接
            cleaned_links = []
            for link in links:
                if link.startswith('http') and 'job' in link.lower():
                    cleaned_links.append(link)
            
            return cleaned_links[:50]  # 限制鏈接數量
            
        except Exception as e:
            self.logger.warning("鏈接提取失敗", error=str(e))
            return []
    
    async def _navigate_to_next_page(self, page: Page, platform: str) -> bool:
        """導航到下一頁"""
        try:
            # 平台特定的下一頁選擇器
            next_selectors = {
                "linkedin": "button[aria-label*='next'], .artdeco-pagination__button--next",
                "indeed": "a[aria-label*='Next'], a[href*='start=']",
                "glassdoor": "button[data-test*='next'], .next",
                "generic": "a:contains('Next'), button:contains('Next'), .next"
            }
            
            selector = next_selectors.get(platform.lower(), next_selectors["generic"])
            
            # 查找下一頁按鈕
            next_button = await page.query_selector(selector)
            if not next_button:
                return False
            
            # 檢查按鈕是否可點擊
            is_disabled = await next_button.is_disabled()
            if is_disabled:
                return False
            
            # 點擊下一頁
            await next_button.click()
            
            # 等待頁面更新
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            return True
            
        except Exception as e:
            self.logger.debug("下一頁導航失敗", error=str(e))
            return False
    
    async def _extract_structured_data(self, page: Page, 
                                     request: ScrapingRequest) -> Optional[Dict[str, Any]]:
        """提取結構化數據"""
        try:
            # 使用自定義選擇器
            if request.custom_selectors:
                data = {}
                for key, selector in request.custom_selectors.items():
                    try:
                        elements = await page.query_selector_all(selector)
                        data[key] = [await el.text_content() for el in elements]
                    except:
                        data[key] = []
                return data
            
            # 默認結構化數據提取
            return await self._extract_default_job_data(page, request.platform)
            
        except Exception as e:
            self.logger.warning("結構化數據提取失敗", error=str(e))
            return None
    
    async def _extract_default_job_data(self, page: Page, platform: str) -> Dict[str, Any]:
        """提取默認的職位數據"""
        data = {
            "titles": [],
            "companies": [],
            "locations": [],
            "descriptions": []
        }
        
        try:
            # 平台特定的選擇器
            if platform.lower() == "linkedin":
                data["titles"] = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('.job-search-card__title a, .base-search-card__title a'))
                        .map(el => el.textContent.trim())
                """)
                data["companies"] = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('.job-search-card__subtitle, .base-search-card__subtitle'))
                        .map(el => el.textContent.trim())
                """)
            
            elif platform.lower() == "indeed":
                data["titles"] = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('[data-testid="job-title"] a, .jobTitle a'))
                        .map(el => el.textContent.trim())
                """)
                data["companies"] = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('[data-testid="company-name"], .companyName'))
                        .map(el => el.textContent.trim())
                """)
            
            elif platform.lower() == "glassdoor":
                data["titles"] = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('.JobCard_jobTitle__rbjTE a, .job-title'))
                        .map(el => el.textContent.trim())
                """)
                data["companies"] = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('.JobCard_employerName__rqEib, .employer-name'))
                        .map(el => el.textContent.trim())
                """)
        
        except Exception as e:
            self.logger.warning("默認數據提取失敗", platform=platform, error=str(e))
        
        return data
    
    async def cleanup(self):
        """清理資源"""
        try:
            if self.browser_manager:
                await self.browser_manager.cleanup()
            
            if self.proxy_manager:
                await self.proxy_manager.cleanup()
            
            if self._playwright:
                await self._playwright.stop()
            
            self._is_initialized = False
            self.logger.info("智能爬蟲引擎已清理")
            
        except Exception as e:
            self.logger.error("清理資源失敗", error=str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        stats = self._stats.copy()
        if stats["total_requests"] > 0:
            stats["success_rate"] = stats["successful_requests"] / stats["total_requests"] * 100
            stats["average_execution_time"] = stats["total_execution_time"] / stats["total_requests"]
        else:
            stats["success_rate"] = 0.0
            stats["average_execution_time"] = 0.0
        
        return stats