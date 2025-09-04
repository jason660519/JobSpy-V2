"""Seek平台適配器

實現Seek求職網站的專用爬取邏輯，包括搜索、數據解析和完整的ETL pipeline。
"""

import asyncio
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import structlog
from playwright.async_api import Page

from ...utils import async_retry, SCRAPING_RETRY_CONFIG, NETWORK_RETRY_CONFIG

from ..base import (
    BasePlatformAdapter,
    PlatformCapability,
    SearchMethod,
    SearchRequest,
    SearchResult,
    JobData,
    PlatformConfig
)

logger = structlog.get_logger(__name__)


class SeekAdapter(BasePlatformAdapter):
    """Seek平台適配器
    
    專門處理Seek網站的職位搜索和數據提取，支持完整的ETL pipeline。
    """
    
    @property
    def platform_name(self) -> str:
        return "seek"
    
    @property
    def supported_capabilities(self) -> List[PlatformCapability]:
        return [
            PlatformCapability.JOB_SEARCH,
            PlatformCapability.JOB_DETAILS,
            PlatformCapability.COMPANY_INFO,
            PlatformCapability.SALARY_INFO
        ]
    
    @property
    def supported_methods(self) -> List[SearchMethod]:
        return [
            SearchMethod.WEB_SCRAPING,
            SearchMethod.AI_VISION,
            SearchMethod.HYBRID
        ]
    
    def __init__(self, config: PlatformConfig):
        super().__init__(config)
        
        # Seek特定的選擇器 (更新為2025年版本)
        self.selectors = {
            # 搜索結果頁面
            "job_cards": 'article[data-testid="job-card"]',
            "job_title": '[data-testid="job-card-title"] a, h3 a',
            "job_link": '[data-testid="job-card-title"] a, h3 a',
            "company_name": '[data-testid*="company"] a, [data-testid*="company"] span',
            "company_link": '[data-testid*="company"] a',
            "location": '[data-automation="jobLocation"], .job-tile-metadata-location',
            "posted_date": '[data-automation="jobListingDate"], .job-tile-metadata-date',
            "salary_info": '[data-automation="jobSalary"], .job-tile-salary',
            "job_type": '[data-testid="job-classification"]',
            
            # 分頁
            "next_page": '[data-automation="page-next"], .pagination-next',
            "page_numbers": '.pagination-page, [data-automation="page-number"]',
            
            # 職位詳情頁面
            "job_description": '[data-automation="jobAdDetails"], .job-detail-content',
            "job_header": '[data-automation="job-detail-title"], .job-header-title',
            "company_info": '[data-automation="advertiser-name"], .advertiser-name',
            "job_criteria": '.job-detail-criteria, .job-metadata',
            "apply_button": '[data-automation="job-detail-apply"], .apply-button',
            "requirements": '.job-requirements, .job-detail-requirements',
            "benefits": '.job-benefits, .job-detail-benefits',
            
            # 搜索表單
            "search_input": '[data-automation="keywords-input"], #keywords',
            "location_input": '[data-automation="location-input"], #location',
            "search_button": '[data-automation="searchButton"], .search-button',
            
            # 篩選器
            "salary_filter": '[data-automation="salary-filter"]',
            "job_type_filter": '[data-automation="workType-filter"]',
            "date_filter": '[data-automation="dateRange-filter"]'
        }
        
        # 更新配置中的選擇器
        self.config.selectors.update(self.selectors)
        
        # Seek特定配置
        self.base_url = "https://www.seek.com.au"
        self.search_url = f"{self.base_url}/jobs"
        
        # 初始化ETL pipeline組件
        self._init_etl_components()
    
    def _init_etl_components(self):
        """初始化ETL pipeline組件"""
        self.etl_stats = {
            "raw_data_stored": 0,
            "ai_processed": 0,
            "data_cleaned": 0,
            "db_loaded": 0,
            "csv_exported": 0
        }
    
    def build_search_url(self, request: SearchRequest) -> str:
        """構建Seek搜索URL
        
        Args:
            request: 搜索請求
            
        Returns:
            str: 搜索URL
        """
        params = {
            "q": request.query,
            "page": request.page
        }
        
        # 添加位置參數
        if request.location:
            params["l"] = request.location
        
        # 添加工作類型
        if request.job_type:
            job_type_mapping = {
                "full-time": "full-time",
                "part-time": "part-time",
                "contract": "contract",
                "casual": "casual",
                "temp": "temp"
            }
            if request.job_type in job_type_mapping:
                params["worktype"] = job_type_mapping[request.job_type]
        
        # 添加薪資範圍
        if request.salary_min:
            params["salaryFrom"] = request.salary_min
        if request.salary_max:
            params["salaryTo"] = request.salary_max
        
        # 添加發布日期
        if request.date_posted:
            date_mapping = {
                "24h": "1",
                "3d": "3",
                "7d": "7",
                "14d": "14",
                "30d": "31"
            }
            if request.date_posted in date_mapping:
                params["daterange"] = date_mapping[request.date_posted]
        
        # 添加排序
        sort_mapping = {
            "relevance": "relevance",
            "date": "date",
            "salary": "salary"
        }
        if request.sort_by in sort_mapping:
            params["sortmode"] = sort_mapping[request.sort_by]
        
        # 添加額外參數
        params.update(request.extra_params)
        
        url = f"{self.search_url}?{urlencode(params)}"
        self.logger.info("構建搜索URL", url=url, params=params)
        
        return url
    
    async def search_jobs(self, request: SearchRequest, 
                         method: SearchMethod = SearchMethod.WEB_SCRAPING) -> SearchResult:
        """搜索職位 - ETL Pipeline 第一階段：原始數據抓取
        
        Args:
            request: 搜索請求
            method: 搜索方法
            
        Returns:
            SearchResult: 搜索結果
        """
        start_time = datetime.now()
        
        try:
            # 驗證請求
            if not await self.validate_request(request):
                return SearchResult(
                    jobs=[],
                    total_count=0,
                    page=request.page,
                    has_next_page=False,
                    search_query=request.query,
                    platform=self.platform_name,
                    execution_time=0.0,
                    method_used=method,
                    success=False,
                    error_message="請求驗證失敗"
                )
            
            # 根據方法選擇搜索策略
            if method == SearchMethod.WEB_SCRAPING:
                result = await self._search_by_scraping(request)
            elif method == SearchMethod.AI_VISION:
                result = await self._search_by_ai_vision(request)
            elif method == SearchMethod.HYBRID:
                result = await self._search_by_hybrid(request)
            else:
                raise ValueError(f"不支持的搜索方法: {method}")
            
            # 計算執行時間
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # 更新統計信息
            self._stats["total_searches"] += 1
            if result.success:
                self._stats["successful_searches"] += 1
                self._stats["total_jobs_found"] += len(result.jobs)
            else:
                self._stats["failed_searches"] += 1
            
            self._stats["total_execution_time"] += execution_time
            
            # 記錄搜索結果
            self.logger.info(
                "搜索完成",
                platform=self.platform_name,
                query=request.query,
                method=method.value,
                jobs_found=len(result.jobs),
                execution_time=execution_time,
                success=result.success
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"搜索失敗: {str(e)}"
            
            self.logger.error(
                "搜索異常",
                platform=self.platform_name,
                query=request.query,
                method=method.value,
                error=error_msg,
                execution_time=execution_time
            )
            
            self._stats["total_searches"] += 1
            self._stats["failed_searches"] += 1
            self._stats["total_execution_time"] += execution_time
            
            return SearchResult(
                jobs=[],
                total_count=0,
                page=request.page,
                has_next_page=False,
                search_query=request.query,
                platform=self.platform_name,
                execution_time=execution_time,
                method_used=method,
                success=False,
                error_message=error_msg
            )
    
    @async_retry(SCRAPING_RETRY_CONFIG)
    async def _search_by_scraping(self, request: SearchRequest) -> SearchResult:
        """通過網頁爬取搜索職位
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        from ..scraper.browser_manager import BrowserManager
        from ..config import ScrapingConfig
        
        # 創建默認的爬蟲配置
        scraping_config = ScrapingConfig()
        browser_manager = BrowserManager(scraping_config)
        
        # 初始化 Playwright
        from playwright.async_api import async_playwright
        async with async_playwright() as playwright:
            await browser_manager.initialize(playwright)
            
            try:
                # 獲取瀏覽器實例
                browser = await browser_manager.get_browser()
                
                # 創建新的瀏覽器上下文
                context = await browser.new_context()
                
                # 創建新頁面
                page = await context.new_page()
                
                # 構建搜索URL
                search_url = self.build_search_url(request)
                
                # 導航到搜索頁面
                await page.goto(search_url, wait_until="networkidle")
                
                # 等待搜索結果加載
                await page.wait_for_selector(self.selectors["job_cards"], timeout=10000)
                
                # 提取職位鏈接
                job_links = await self.extract_job_links(page)
                
                # 解析職位數據
                jobs = []
                for job_url in job_links[:request.limit]:
                    try:
                        job_data = await self.get_job_details(job_url, SearchMethod.WEB_SCRAPING)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning("解析職位失敗", url=job_url, error=str(e))
                        continue
                
                # 檢查是否有下一頁
                has_next_page = await self._check_next_page(page)
                
                # 估算總數量
                total_count = await self._estimate_total_count(page)
                
                return SearchResult(
                    jobs=jobs,
                    total_count=total_count,
                    page=request.page,
                    has_next_page=has_next_page,
                    search_query=request.query,
                    platform=self.platform_name,
                    execution_time=0.0,  # 將在上層設置
                    method_used=SearchMethod.WEB_SCRAPING,
                    success=True,
                    scraped_count=len(jobs)
                )
                
            finally:
                # 關閉頁面和上下文
                if 'page' in locals():
                    await page.close()
                if 'context' in locals():
                    await context.close()
                await browser_manager.cleanup()
    
    async def extract_job_links(self, page: Page) -> List[str]:
        """從搜索結果頁面提取職位鏈接
        
        Args:
            page: 頁面對象
            
        Returns:
            List[str]: 職位鏈接列表
        """
        try:
            # 等待職位卡片加載
            await page.wait_for_selector(self.selectors["job_cards"], timeout=5000)
            
            # 提取所有職位鏈接
            job_links = await page.evaluate(f"""
                () => {{
                    const links = [];
                    const jobCards = document.querySelectorAll('{self.selectors["job_cards"]}');
                    
                    jobCards.forEach(card => {{
                        const linkElement = card.querySelector('{self.selectors["job_link"]}');
                        if (linkElement && linkElement.href) {{
                            links.push(linkElement.href);
                        }}
                    }});
                    
                    return links;
                }}
            """)
            
            # 確保鏈接是完整的URL
            full_links = []
            for link in job_links:
                if link.startswith('http'):
                    full_links.append(link)
                elif link.startswith('/'):
                    full_links.append(f"{self.base_url}{link}")
                else:
                    full_links.append(f"{self.base_url}/{link}")
            
            self.logger.info("提取職位鏈接", count=len(full_links))
            return full_links
            
        except Exception as e:
            self.logger.error("提取職位鏈接失敗", error=str(e))
            return []
    
    async def get_job_details(self, job_url: str, 
                            method: SearchMethod = SearchMethod.WEB_SCRAPING) -> Optional[JobData]:
        """獲取職位詳情
        
        Args:
            job_url: 職位URL
            method: 獲取方法
            
        Returns:
            Optional[JobData]: 職位詳情
        """
        from ..scraper.browser_manager import BrowserManager
        from ..config import ScrapingConfig
        
        # 創建默認的爬蟲配置
        scraping_config = ScrapingConfig()
        browser_manager = BrowserManager(scraping_config)
        
        # 初始化 Playwright
        from playwright.async_api import async_playwright
        async with async_playwright() as playwright:
            await browser_manager.initialize(playwright)
            
            try:
                # 獲取瀏覽器實例
                browser = await browser_manager.get_browser()
                
                # 創建新的瀏覽器上下文
                context = await browser.new_context()
                
                # 創建新頁面
                page = await context.new_page()
                
                # 導航到職位詳情頁面
                await page.goto(job_url, wait_until="networkidle")
                
                # 解析職位數據
                job_data = await self.parse_job_data(page, job_url)
                
                return job_data
                
            except Exception as e:
                self.logger.error("獲取職位詳情失敗", url=job_url, error=str(e))
                return None
                
            finally:
                # 關閉頁面和上下文
                if 'page' in locals():
                    await page.close()
                if 'context' in locals():
                    await context.close()
                await browser_manager.cleanup()
    
    async def parse_job_data(self, page: Page, job_url: str) -> Optional[JobData]:
        """解析職位數據
        
        Args:
            page: 頁面對象
            job_url: 職位URL
            
        Returns:
            Optional[JobData]: 解析的職位數據
        """
        try:
            # 等待頁面加載
            await page.wait_for_load_state("networkidle")
            
            # 提取基本信息
            job_data = await page.evaluate(f"""
                () => {{
                    const data = {{}};
                    
                    // 職位標題
                    const titleElement = document.querySelector('{self.selectors["job_header"]}');
                    data.title = titleElement ? titleElement.textContent.trim() : '';
                    
                    // 公司名稱
                    const companyElement = document.querySelector('{self.selectors["company_info"]}');
                    data.company = companyElement ? companyElement.textContent.trim() : '';
                    
                    // 位置
                    const locationElement = document.querySelector('{self.selectors["location"]}');
                    data.location = locationElement ? locationElement.textContent.trim() : '';
                    
                    // 職位描述
                    const descElement = document.querySelector('{self.selectors["job_description"]}');
                    data.description = descElement ? descElement.textContent.trim() : '';
                    
                    // 薪資信息
                    const salaryElement = document.querySelector('{self.selectors["salary_info"]}');
                    data.salary_text = salaryElement ? salaryElement.textContent.trim() : '';
                    
                    // 工作類型
                    const typeElement = document.querySelector('{self.selectors["job_type"]}');
                    data.job_type = typeElement ? typeElement.textContent.trim() : '';
                    
                    // 發布日期
                    const dateElement = document.querySelector('{self.selectors["posted_date"]}');
                    data.posted_date = dateElement ? dateElement.textContent.trim() : '';
                    
                    return data;
                }}
            """)
            
            # 解析薪資信息
            salary_min, salary_max, salary_currency = self._parse_salary(job_data.get('salary_text', ''))
            
            # 解析發布日期
            posted_date = self._parse_posted_date(job_data.get('posted_date', ''))
            
            # 生成唯一ID
            job_id = self._generate_job_id(job_url)
            
            # 創建JobData對象
            return JobData(
                title=job_data.get('title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                url=job_url,
                description=job_data.get('description', ''),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=salary_currency,
                job_type=self._normalize_job_type(job_data.get('job_type', '')),
                posted_date=posted_date,
                platform=self.platform_name,
                scraped_at=datetime.now(),
                job_id=job_id,
                external_id=job_id,
                raw_data=job_data
            )
            
        except Exception as e:
            self.logger.error("解析職位數據失敗", url=job_url, error=str(e))
            return None
    
    def _parse_salary(self, salary_text: str) -> tuple[Optional[int], Optional[int], str]:
        """解析薪資信息
        
        Args:
            salary_text: 薪資文本
            
        Returns:
            tuple: (最低薪資, 最高薪資, 貨幣)
        """
        if not salary_text:
            return None, None, "AUD"
        
        # 移除逗號和空格
        salary_text = salary_text.replace(',', '').replace(' ', '')
        
        # 匹配薪資範圍 (例如: $50,000 - $70,000)
        range_pattern = r'\$([0-9]+)(?:k|,?000)?\s*-\s*\$([0-9]+)(?:k|,?000)?'
        range_match = re.search(range_pattern, salary_text, re.IGNORECASE)
        
        if range_match:
            min_sal = int(range_match.group(1))
            max_sal = int(range_match.group(2))
            
            # 處理k表示的千位
            if 'k' in salary_text.lower():
                min_sal *= 1000
                max_sal *= 1000
            
            return min_sal, max_sal, "AUD"
        
        # 匹配單一薪資 (例如: $60,000)
        single_pattern = r'\$([0-9]+)(?:k|,?000)?'
        single_match = re.search(single_pattern, salary_text, re.IGNORECASE)
        
        if single_match:
            salary = int(single_match.group(1))
            
            if 'k' in salary_text.lower():
                salary *= 1000
            
            return salary, salary, "AUD"
        
        return None, None, "AUD"
    
    def _parse_posted_date(self, date_text: str) -> Optional[datetime]:
        """解析發布日期
        
        Args:
            date_text: 日期文本
            
        Returns:
            Optional[datetime]: 解析的日期
        """
        if not date_text:
            return None
        
        try:
            # 處理相對日期 (例如: "2 days ago", "1 week ago")
            if 'day' in date_text.lower():
                days_match = re.search(r'(\d+)\s*day', date_text, re.IGNORECASE)
                if days_match:
                    days = int(days_match.group(1))
                    return datetime.now() - timedelta(days=days)
            
            elif 'week' in date_text.lower():
                weeks_match = re.search(r'(\d+)\s*week', date_text, re.IGNORECASE)
                if weeks_match:
                    weeks = int(weeks_match.group(1))
                    return datetime.now() - timedelta(weeks=weeks)
            
            elif 'hour' in date_text.lower():
                hours_match = re.search(r'(\d+)\s*hour', date_text, re.IGNORECASE)
                if hours_match:
                    hours = int(hours_match.group(1))
                    return datetime.now() - timedelta(hours=hours)
            
            elif 'today' in date_text.lower():
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            elif 'yesterday' in date_text.lower():
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            
        except Exception as e:
            self.logger.warning("解析日期失敗", date_text=date_text, error=str(e))
        
        return None
    
    def _normalize_job_type(self, job_type: str) -> str:
        """標準化工作類型
        
        Args:
            job_type: 原始工作類型
            
        Returns:
            str: 標準化的工作類型
        """
        if not job_type:
            return "unknown"
        
        job_type_lower = job_type.lower()
        
        if 'full' in job_type_lower and 'time' in job_type_lower:
            return "full-time"
        elif 'part' in job_type_lower and 'time' in job_type_lower:
            return "part-time"
        elif 'contract' in job_type_lower:
            return "contract"
        elif 'casual' in job_type_lower:
            return "casual"
        elif 'temp' in job_type_lower:
            return "temp"
        else:
            return job_type.lower()
    
    def _generate_job_id(self, job_url: str) -> str:
        """生成職位唯一ID
        
        Args:
            job_url: 職位URL
            
        Returns:
            str: 職位ID
        """
        # 從URL中提取ID
        url_parts = job_url.split('/')
        for part in url_parts:
            if part.isdigit():
                return f"seek_{part}"
        
        # 如果無法從URL提取，使用URL的hash
        import hashlib
        return f"seek_{hashlib.md5(job_url.encode()).hexdigest()[:8]}"
    
    async def _check_next_page(self, page: Page) -> bool:
        """檢查是否有下一頁
        
        Args:
            page: 頁面對象
            
        Returns:
            bool: 是否有下一頁
        """
        try:
            next_button = await page.query_selector(self.selectors["next_page"])
            if next_button:
                is_disabled = await next_button.get_attribute("disabled")
                return is_disabled is None
            return False
        except Exception:
            return False
    
    async def _estimate_total_count(self, page: Page) -> int:
        """估算總職位數量
        
        Args:
            page: 頁面對象
            
        Returns:
            int: 估算的總數量
        """
        try:
            # 嘗試從頁面中提取總數量信息
            total_text = await page.evaluate("""
                () => {
                    // 查找包含總數的元素
                    const selectors = [
                        '[data-automation="totalJobsCount"]',
                        '.search-results-count',
                        '.total-results'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            return element.textContent;
                        }
                    }
                    
                    return '';
                }
            """)
            
            if total_text:
                # 提取數字
                numbers = re.findall(r'\d+', total_text.replace(',', ''))
                if numbers:
                    return int(numbers[0])
            
            # 如果無法獲取總數，返回當前頁面的職位數量 * 估算頁數
            current_jobs = len(await page.query_selector_all(self.selectors["job_cards"]))
            return current_jobs * 10  # 估算10頁
            
        except Exception:
            return 100  # 默認估算值
    
    async def _search_by_ai_vision(self, request: SearchRequest) -> SearchResult:
        """通過AI視覺搜索職位
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        # TODO: 實現AI視覺搜索
        self.logger.info("AI視覺搜索暫未實現，回退到網頁爬取")
        return await self._search_by_scraping(request)
    
    async def _search_by_hybrid(self, request: SearchRequest) -> SearchResult:
        """通過混合模式搜索職位
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        # TODO: 實現混合模式搜索
        self.logger.info("混合模式搜索暫未實現，回退到網頁爬取")
        return await self._search_by_scraping(request)
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        return {
            **self._stats,
            **self.etl_stats,
            "platform": self.platform_name,
            "config": {
                "base_url": self.base_url,
                "search_url": self.search_url,
                "max_results_per_page": self.config.max_results_per_page,
                "timeout": self.config.timeout
            }
        }


# 創建默認配置
def create_seek_config() -> PlatformConfig:
    """創建Seek平台的默認配置
    
    Returns:
        PlatformConfig: Seek平台配置
    """
    return PlatformConfig(
        name="seek",
        base_url="https://www.seek.com.au",
        search_url="https://www.seek.com.au/jobs",
        job_detail_url_pattern="https://www.seek.com.au/job/{job_id}",
        max_results_per_page=25,
        max_pages=10,
        search_delay_range=(2, 5),
        use_proxy=True,
        rotate_user_agent=True,
        simulate_human_behavior=True,
        timeout=30,
        retry_attempts=3,
        enable_screenshots=True
    )