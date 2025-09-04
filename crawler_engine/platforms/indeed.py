"""Indeed平台適配器

實現Indeed求職網站的專用爬取邏輯，包括搜索、數據解析和反檢測策略。
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import structlog
from playwright.async_api import Page

from .base import (
    BasePlatformAdapter,
    PlatformCapability,
    SearchMethod,
    SearchRequest,
    SearchResult,
    JobData,
    PlatformConfig
)

logger = structlog.get_logger(__name__)


class IndeedAdapter(BasePlatformAdapter):
    """Indeed平台適配器
    
    專門處理Indeed網站的職位搜索和數據提取。
    """
    
    @property
    def platform_name(self) -> str:
        return "indeed"
    
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
        
        # Indeed特定的選擇器
        self.selectors = {
            # 搜索結果頁面
            "job_cards": '[data-jk]',
            "job_title": 'h2.jobTitle a span',
            "job_link": 'h2.jobTitle a',
            "company_name": '[data-testid="company-name"]',
            "company_link": '[data-testid="company-name"] a',
            "location": '[data-testid="job-location"]',
            "salary": '[data-testid="attribute_snippet_testid"]',
            "job_snippet": '[data-testid="job-snippet"]',
            "posted_date": '.date',
            
            # 分頁
            "next_page": 'a[aria-label="Next Page"]',
            "page_info": '.np',
            
            # 職位詳情頁面
            "job_description": '#jobDescriptionText',
            "job_header": '.jobsearch-JobInfoHeader-title',
            "company_info": '.jobsearch-CompanyInfoContainer',
            "job_meta": '.jobsearch-JobMetadataHeader-item',
            "apply_button": '.jobsearch-IndeedApplyButton',
            
            # 反檢測相關
            "captcha": '#captcha-challenge',
            "blocked_message": '.blocked',
            "rate_limit": '.rate-limit'
        }
        
        # 更新配置中的選擇器
        self.config.selectors.update(self.selectors)
    
    def build_search_url(self, request: SearchRequest) -> str:
        """構建Indeed搜索URL
        
        Args:
            request: 搜索請求
            
        Returns:
            str: 搜索URL
        """
        base_url = "https://www.indeed.com/jobs"
        
        params = {
            "q": request.query,
            "limit": min(request.limit, 50),  # Indeed最大50個結果每頁
            "start": (request.page - 1) * request.limit
        }
        
        # 添加位置
        if request.location:
            params["l"] = request.location
        
        # 添加工作類型
        if request.job_type:
            job_type_map = {
                "full-time": "fulltime",
                "part-time": "parttime",
                "contract": "contract",
                "temporary": "temporary",
                "internship": "internship"
            }
            if request.job_type in job_type_map:
                params["jt"] = job_type_map[request.job_type]
        
        # 添加薪資範圍
        if request.salary_min:
            params["salary"] = f"${request.salary_min}+"
        
        # 添加發布時間
        if request.date_posted:
            date_map = {
                "24h": "1",
                "3d": "3",
                "7d": "7",
                "14d": "14",
                "30d": "30"
            }
            if request.date_posted in date_map:
                params["fromage"] = date_map[request.date_posted]
        
        # 添加遠程工作
        if request.remote:
            params["remotejob"] = "1"
        
        # 添加排序
        if request.sort_by == "date":
            params["sort"] = "date"
        
        # 添加額外參數
        params.update(request.extra_params)
        
        url = f"{base_url}?{urlencode(params)}"
        
        self.logger.debug(
            "構建搜索URL",
            url=url,
            query=request.query,
            location=request.location,
            page=request.page
        )
        
        return url
    
    async def search_jobs(self, request: SearchRequest, 
                         method: SearchMethod = SearchMethod.WEB_SCRAPING) -> SearchResult:
        """搜索Indeed職位
        
        Args:
            request: 搜索請求
            method: 搜索方法
            
        Returns:
            SearchResult: 搜索結果
        """
        start_time = asyncio.get_event_loop().time()
        
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
        
        # 檢查速率限制
        await self.check_rate_limit()
        
        try:
            if method == SearchMethod.WEB_SCRAPING:
                result = await self._search_by_scraping(request)
            elif method == SearchMethod.AI_VISION:
                result = await self._search_by_ai_vision(request)
            elif method == SearchMethod.HYBRID:
                result = await self._search_by_hybrid(request)
            else:
                raise ValueError(f"不支持的搜索方法: {method}")
            
            # 計算執行時間
            execution_time = asyncio.get_event_loop().time() - start_time
            result.execution_time = execution_time
            result.method_used = method
            
            # 更新統計
            self.update_stats(result)
            
            self.logger.info(
                "Indeed搜索完成",
                query=request.query,
                jobs_found=len(result.jobs),
                execution_time=execution_time,
                method=method.value
            )
            
            return result
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            
            error_result = SearchResult(
                jobs=[],
                total_count=0,
                page=request.page,
                has_next_page=False,
                search_query=request.query,
                platform=self.platform_name,
                execution_time=execution_time,
                method_used=method,
                success=False,
                error_message=str(e)
            )
            
            self.update_stats(error_result)
            
            self.logger.error(
                "Indeed搜索失敗",
                query=request.query,
                error=str(e),
                method=method.value
            )
            
            return error_result
    
    async def _search_by_scraping(self, request: SearchRequest) -> SearchResult:
        """通過網頁爬取搜索職位
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        from ..scraper import SmartScraper, ScrapingRequest
        
        # 這裡需要從外部注入SmartScraper實例
        # 為了演示，我們創建一個模擬的搜索結果
        
        search_url = self.build_search_url(request)
        
        # 模擬爬取邏輯
        jobs = []
        
        # 實際實現中，這裡會使用SmartScraper進行爬取
        # scraper = SmartScraper(config)
        # scraping_request = ScrapingRequest(url=search_url, ...)
        # scraping_result = await scraper.scrape(scraping_request)
        
        # 解析職位數據
        # jobs = await self._parse_search_results(scraping_result.page)
        
        return SearchResult(
            jobs=jobs,
            total_count=len(jobs),
            page=request.page,
            has_next_page=False,  # 需要實際檢測
            search_query=request.query,
            platform=self.platform_name,
            execution_time=0.0,
            method_used=SearchMethod.WEB_SCRAPING,
            success=True
        )
    
    async def _search_by_ai_vision(self, request: SearchRequest) -> SearchResult:
        """通過AI視覺分析搜索職位
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        # 實現AI視覺分析邏輯
        # 這裡需要集成AIVisionService
        
        return SearchResult(
            jobs=[],
            total_count=0,
            page=request.page,
            has_next_page=False,
            search_query=request.query,
            platform=self.platform_name,
            execution_time=0.0,
            method_used=SearchMethod.AI_VISION,
            success=True
        )
    
    async def _search_by_hybrid(self, request: SearchRequest) -> SearchResult:
        """通過混合方法搜索職位
        
        Args:
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        # 實現混合搜索邏輯
        # 結合網頁爬取和AI視覺分析
        
        return SearchResult(
            jobs=[],
            total_count=0,
            page=request.page,
            has_next_page=False,
            search_query=request.query,
            platform=self.platform_name,
            execution_time=0.0,
            method_used=SearchMethod.HYBRID,
            success=True
        )
    
    async def extract_job_links(self, page: Page) -> List[str]:
        """從Indeed搜索結果頁面提取職位鏈接
        
        Args:
            page: 頁面對象
            
        Returns:
            List[str]: 職位鏈接列表
        """
        try:
            # 等待職位卡片加載
            await page.wait_for_selector(self.selectors["job_cards"], timeout=10000)
            
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
            
            # 轉換為絕對URL
            absolute_links = []
            for link in job_links:
                if link.startswith('/'):
                    absolute_links.append(f"https://www.indeed.com{link}")
                else:
                    absolute_links.append(link)
            
            self.logger.debug(
                "提取Indeed職位鏈接",
                count=len(absolute_links),
                url=page.url
            )
            
            return absolute_links
            
        except Exception as e:
            self.logger.error(
                "提取Indeed職位鏈接失敗",
                error=str(e),
                url=page.url
            )
            return []
    
    async def parse_job_data(self, page: Page, job_url: str) -> Optional[JobData]:
        """解析Indeed職位數據
        
        Args:
            page: 頁面對象
            job_url: 職位URL
            
        Returns:
            Optional[JobData]: 解析的職位數據
        """
        try:
            # 等待頁面加載
            await page.wait_for_load_state("networkidle")
            
            # 檢查是否被阻止
            if await self._check_blocked(page):
                self.logger.warning("頁面被阻止", url=job_url)
                return None
            
            # 提取基本信息
            job_data = await page.evaluate(f"""
                () => {{
                    const data = {{}};
                    
                    // 職位標題
                    const titleElement = document.querySelector('{self.selectors["job_header"]}');
                    data.title = titleElement ? titleElement.textContent.trim() : '';
                    
                    // 公司名稱
                    const companyElement = document.querySelector('{self.selectors["company_info"]} a, {self.selectors["company_info"]} span');
                    data.company = companyElement ? companyElement.textContent.trim() : '';
                    
                    // 位置
                    const locationElements = document.querySelectorAll('{self.selectors["job_meta"]}');
                    for (const element of locationElements) {{
                        const text = element.textContent.trim();
                        if (text && !text.includes('$') && !text.includes('hour') && !text.includes('year')) {{
                            data.location = text;
                            break;
                        }}
                    }}
                    
                    // 職位描述
                    const descElement = document.querySelector('{self.selectors["job_description"]}');
                    data.description = descElement ? descElement.innerHTML : '';
                    
                    // 薪資信息
                    const salaryElements = document.querySelectorAll('{self.selectors["job_meta"]}');
                    for (const element of salaryElements) {{
                        const text = element.textContent.trim();
                        if (text.includes('$')) {{
                            data.salary_text = text;
                            break;
                        }}
                    }}
                    
                    return data;
                }}
            """)
            
            if not job_data.get('title'):
                self.logger.warning("無法提取職位標題", url=job_url)
                return None
            
            # 解析薪資
            salary_min, salary_max, salary_currency, salary_period = self._parse_salary(
                job_data.get('salary_text', '')
            )
            
            # 提取職位ID
            job_id = self._extract_job_id(job_url)
            
            # 創建JobData對象
            job = JobData(
                title=job_data['title'],
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                url=job_url,
                description=job_data.get('description', ''),
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=salary_currency,
                salary_period=salary_period,
                platform=self.platform_name,
                job_id=job_id,
                external_id=job_id,
                raw_data=job_data
            )
            
            self.logger.debug(
                "解析Indeed職位數據成功",
                title=job.title,
                company=job.company,
                url=job_url
            )
            
            return job
            
        except Exception as e:
            self.logger.error(
                "解析Indeed職位數據失敗",
                error=str(e),
                url=job_url
            )
            return None
    
    async def get_job_details(self, job_url: str, 
                            method: SearchMethod = SearchMethod.WEB_SCRAPING) -> Optional[JobData]:
        """獲取Indeed職位詳情
        
        Args:
            job_url: 職位URL
            method: 獲取方法
            
        Returns:
            Optional[JobData]: 職位詳情
        """
        try:
            # 檢查速率限制
            await self.check_rate_limit()
            
            if method == SearchMethod.WEB_SCRAPING:
                # 使用SmartScraper獲取頁面
                # 這裡需要實際的SmartScraper實例
                pass
            
            # 暫時返回None，實際實現需要完整的爬取邏輯
            return None
            
        except Exception as e:
            self.logger.error(
                "獲取Indeed職位詳情失敗",
                error=str(e),
                url=job_url
            )
            return None
    
    def _parse_salary(self, salary_text: str) -> tuple:
        """解析薪資信息
        
        Args:
            salary_text: 薪資文本
            
        Returns:
            tuple: (最低薪資, 最高薪資, 貨幣, 週期)
        """
        if not salary_text:
            return None, None, "USD", "yearly"
        
        # 移除多餘的空格和符號
        salary_text = re.sub(r'\s+', ' ', salary_text.strip())
        
        # 檢測貨幣
        currency = "USD"
        if "$" in salary_text:
            currency = "USD"
        elif "€" in salary_text:
            currency = "EUR"
        elif "£" in salary_text:
            currency = "GBP"
        
        # 檢測週期
        period = "yearly"
        if "hour" in salary_text.lower():
            period = "hourly"
        elif "month" in salary_text.lower():
            period = "monthly"
        elif "year" in salary_text.lower():
            period = "yearly"
        
        # 提取數字
        numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
        
        if len(numbers) >= 2:
            # 範圍薪資
            try:
                min_salary = int(numbers[0].replace(',', ''))
                max_salary = int(numbers[1].replace(',', ''))
                return min_salary, max_salary, currency, period
            except ValueError:
                pass
        elif len(numbers) == 1:
            # 單一薪資
            try:
                salary = int(numbers[0].replace(',', ''))
                return salary, salary, currency, period
            except ValueError:
                pass
        
        return None, None, currency, period
    
    def _extract_job_id(self, job_url: str) -> Optional[str]:
        """從URL中提取職位ID
        
        Args:
            job_url: 職位URL
            
        Returns:
            Optional[str]: 職位ID
        """
        try:
            # Indeed的職位ID通常在URL的jk參數中
            parsed_url = urlparse(job_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'jk' in query_params:
                return query_params['jk'][0]
            
            # 或者從路徑中提取
            path_parts = parsed_url.path.split('/')
            for part in path_parts:
                if part and len(part) > 10:  # 職位ID通常較長
                    return part
            
            return None
            
        except Exception as e:
            self.logger.warning("提取職位ID失敗", error=str(e), url=job_url)
            return None
    
    async def _check_blocked(self, page: Page) -> bool:
        """檢查頁面是否被阻止
        
        Args:
            page: 頁面對象
            
        Returns:
            bool: 是否被阻止
        """
        try:
            # 檢查CAPTCHA
            captcha = await page.query_selector(self.selectors["captcha"])
            if captcha:
                self.logger.warning("檢測到CAPTCHA", url=page.url)
                return True
            
            # 檢查阻止消息
            blocked = await page.query_selector(self.selectors["blocked_message"])
            if blocked:
                self.logger.warning("檢測到阻止消息", url=page.url)
                return True
            
            # 檢查速率限制
            rate_limit = await page.query_selector(self.selectors["rate_limit"])
            if rate_limit:
                self.logger.warning("檢測到速率限制", url=page.url)
                return True
            
            # 檢查頁面標題
            title = await page.title()
            if "blocked" in title.lower() or "captcha" in title.lower():
                self.logger.warning("頁面標題顯示被阻止", title=title, url=page.url)
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning("檢查阻止狀態失敗", error=str(e))
            return False
    
    async def _parse_search_results(self, page: Page) -> List[JobData]:
        """解析搜索結果頁面的職位數據
        
        Args:
            page: 頁面對象
            
        Returns:
            List[JobData]: 職位數據列表
        """
        jobs = []
        
        try:
            # 等待職位卡片加載
            await page.wait_for_selector(self.selectors["job_cards"], timeout=10000)
            
            # 獲取所有職位卡片
            job_cards = await page.query_selector_all(self.selectors["job_cards"])
            
            for card in job_cards:
                try:
                    # 提取基本信息
                    title_element = await card.query_selector(self.selectors["job_title"])
                    title = await title_element.text_content() if title_element else ""
                    
                    link_element = await card.query_selector(self.selectors["job_link"])
                    link = await link_element.get_attribute("href") if link_element else ""
                    
                    company_element = await card.query_selector(self.selectors["company_name"])
                    company = await company_element.text_content() if company_element else ""
                    
                    location_element = await card.query_selector(self.selectors["location"])
                    location = await location_element.text_content() if location_element else ""
                    
                    snippet_element = await card.query_selector(self.selectors["job_snippet"])
                    snippet = await snippet_element.text_content() if snippet_element else ""
                    
                    salary_element = await card.query_selector(self.selectors["salary"])
                    salary_text = await salary_element.text_content() if salary_element else ""
                    
                    if not title or not link:
                        continue
                    
                    # 轉換為絕對URL
                    if link.startswith('/'):
                        link = f"https://www.indeed.com{link}"
                    
                    # 解析薪資
                    salary_min, salary_max, salary_currency, salary_period = self._parse_salary(salary_text)
                    
                    # 提取職位ID
                    job_id = self._extract_job_id(link)
                    
                    # 創建JobData對象
                    job = JobData(
                        title=title.strip(),
                        company=company.strip(),
                        location=location.strip(),
                        url=link,
                        description=snippet.strip(),
                        salary_min=salary_min,
                        salary_max=salary_max,
                        salary_currency=salary_currency,
                        salary_period=salary_period,
                        platform=self.platform_name,
                        job_id=job_id,
                        external_id=job_id,
                        raw_data={
                            "title": title,
                            "company": company,
                            "location": location,
                            "snippet": snippet,
                            "salary_text": salary_text
                        }
                    )
                    
                    jobs.append(job)
                    
                except Exception as e:
                    self.logger.warning("解析職位卡片失敗", error=str(e))
                    continue
            
            self.logger.debug(
                "解析Indeed搜索結果",
                jobs_found=len(jobs),
                url=page.url
            )
            
        except Exception as e:
            self.logger.error(
                "解析Indeed搜索結果失敗",
                error=str(e),
                url=page.url
            )
        
        return jobs