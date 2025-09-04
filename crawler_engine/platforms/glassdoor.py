"""Glassdoor平台適配器

實現Glassdoor求職網站的專用爬取邏輯，包括搜索、數據解析和反檢測策略。
"""

import asyncio
import re
import json
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


class GlassdoorAdapter(BasePlatformAdapter):
    """Glassdoor平台適配器
    
    專門處理Glassdoor網站的職位搜索和數據提取。
    Glassdoor提供豐富的薪資和公司評價信息。
    """
    
    @property
    def platform_name(self) -> str:
        return "glassdoor"
    
    @property
    def supported_capabilities(self) -> List[PlatformCapability]:
        return [
            PlatformCapability.JOB_SEARCH,
            PlatformCapability.JOB_DETAILS,
            PlatformCapability.COMPANY_INFO,
            PlatformCapability.SALARY_INFO,
            PlatformCapability.COMPANY_REVIEWS
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
        
        # Glassdoor特定的選擇器
        self.selectors = {
            # 搜索結果頁面
            "job_cards": '[data-test="job-listing"], .react-job-listing',
            "job_title": '[data-test="job-title"], .jobTitle',
            "job_link": '[data-test="job-title"] a, .jobTitle a',
            "company_name": '[data-test="employer-name"], .employerName',
            "company_link": '[data-test="employer-name"] a, .employerName a',
            "location": '[data-test="job-location"], .location',
            "salary_estimate": '[data-test="detailSalary"], .salaryText',
            "rating": '[data-test="rating"], .rating',
            "job_age": '[data-test="job-age"], .jobAge',
            
            # 分頁
            "next_page": '[data-test="pagination-next"], .next',
            "page_numbers": '[data-test="page-x"], .pageNumber',
            
            # 職位詳情頁面
            "job_description": '[data-test="jobDescriptionContent"], .jobDescriptionContent',
            "job_header": '[data-test="job-title"], .css-17x2pwl',
            "company_info": '[data-test="employer-name"], .css-16nw49e',
            "salary_info": '[data-test="salary-estimate"], .css-1bluz6i',
            "company_rating": '[data-test="employer-rating"], .rating',
            "company_size": '[data-test="employer-size"], .companySize',
            "company_industry": '[data-test="employer-industry"], .industry',
            
            # 薪資詳情
            "salary_range": '.salaryRange',
            "salary_breakdown": '.salaryBreakdown',
            "benefits_info": '.benefits',
            
            # 公司評價
            "company_reviews": '.employerReviews',
            "review_rating": '.ratingNumber',
            "review_text": '.reviewText',
            
            # 反檢測相關
            "captcha": '.captcha-container',
            "blocked_message": '.blocked-content',
            "rate_limit": '.rate-limit-message',
            "signup_modal": '[data-test="sign-up-modal"]',
            "login_wall": '.authwall'
        }
        
        # 更新配置中的選擇器
        self.config.selectors.update(self.selectors)
        
        # Glassdoor特定配置
        self.base_url = "https://www.glassdoor.com"
        self.jobs_search_url = "https://www.glassdoor.com/Job/jobs.htm"
        self.salaries_url = "https://www.glassdoor.com/Salaries/index.htm"
    
    def build_search_url(self, request: SearchRequest) -> str:
        """構建Glassdoor搜索URL
        
        Args:
            request: 搜索請求
            
        Returns:
            str: 搜索URL
        """
        base_url = self.jobs_search_url
        
        params = {
            "sc.keyword": request.query,
            "p": request.page
        }
        
        # 添加位置
        if request.location:
            params["locT"] = "C"  # City
            params["locId"] = request.location
        
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
                params["jobType"] = job_type_map[request.job_type]
        
        # 添加薪資範圍
        if request.salary_min:
            params["minSalary"] = request.salary_min
        if request.salary_max:
            params["maxSalary"] = request.salary_max
        
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
                params["fromAge"] = date_map[request.date_posted]
        
        # 添加公司規模
        if "company_size" in request.extra_params:
            size_map = {
                "startup": "1,2",      # 1-50
                "small": "3,4",        # 51-500
                "medium": "5,6",       # 501-5000
                "large": "7,8,9"       # 5001+
            }
            size = request.extra_params["company_size"]
            if size in size_map:
                params["companySize"] = size_map[size]
        
        # 添加行業
        if "industry" in request.extra_params:
            params["industry"] = request.extra_params["industry"]
        
        # 添加排序
        if request.sort_by == "date":
            params["sortBy"] = "date_desc"
        elif request.sort_by == "relevance":
            params["sortBy"] = "relevance"
        elif request.sort_by == "salary":
            params["sortBy"] = "salary_desc"
        
        # 添加額外參數
        params.update(request.extra_params)
        
        url = f"{base_url}?{urlencode(params)}"
        
        self.logger.debug(
            "構建Glassdoor搜索URL",
            url=url,
            query=request.query,
            location=request.location,
            page=request.page
        )
        
        return url
    
    async def search_jobs(self, request: SearchRequest, 
                         method: SearchMethod = SearchMethod.WEB_SCRAPING) -> SearchResult:
        """搜索Glassdoor職位
        
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
                "Glassdoor搜索完成",
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
                "Glassdoor搜索失敗",
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
        search_url = self.build_search_url(request)
        
        # 模擬搜索結果
        jobs = []
        
        # 實際實現中需要：
        # 1. 使用SmartScraper導航到搜索URL
        # 2. 處理可能的登錄牆或註冊提示
        # 3. 等待頁面加載
        # 4. 解析職位數據
        # 5. 處理分頁
        # 6. 提取薪資和評價信息
        
        return SearchResult(
            jobs=jobs,
            total_count=len(jobs),
            page=request.page,
            has_next_page=False,
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
        # Glassdoor的頁面結構相對穩定，但有反檢測機制
        
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
        # 結合傳統爬取和AI視覺分析
        
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
        """從Glassdoor搜索結果頁面提取職位鏈接
        
        Args:
            page: 頁面對象
            
        Returns:
            List[str]: 職位鏈接列表
        """
        try:
            # 等待職位卡片加載
            await page.wait_for_selector(self.selectors["job_cards"], timeout=15000)
            
            # 處理可能的註冊提示
            await self._handle_signup_modal(page)
            
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
                    absolute_links.append(f"{self.base_url}{link}")
                else:
                    absolute_links.append(link)
            
            self.logger.debug(
                "提取Glassdoor職位鏈接",
                count=len(absolute_links),
                url=page.url
            )
            
            return absolute_links
            
        except Exception as e:
            self.logger.error(
                "提取Glassdoor職位鏈接失敗",
                error=str(e),
                url=page.url
            )
            return []
    
    async def parse_job_data(self, page: Page, job_url: str) -> Optional[JobData]:
        """解析Glassdoor職位數據
        
        Args:
            page: 頁面對象
            job_url: 職位URL
            
        Returns:
            Optional[JobData]: 解析的職位數據
        """
        try:
            # 等待頁面加載
            await page.wait_for_load_state("networkidle")
            
            # 檢查是否被阻止或需要註冊
            if await self._check_blocked(page):
                self.logger.warning("頁面被阻止或需要註冊", url=job_url)
                return None
            
            # 處理註冊提示
            await self._handle_signup_modal(page)
            
            # 等待職位詳情加載
            await page.wait_for_selector(self.selectors["job_header"], timeout=10000)
            
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
                    data.description = descElement ? descElement.innerHTML : '';
                    
                    // 薪資信息
                    const salaryElement = document.querySelector('{self.selectors["salary_info"]}');
                    data.salary_text = salaryElement ? salaryElement.textContent.trim() : '';
                    
                    // 公司評分
                    const ratingElement = document.querySelector('{self.selectors["company_rating"]}');
                    data.company_rating = ratingElement ? ratingElement.textContent.trim() : '';
                    
                    // 公司規模
                    const sizeElement = document.querySelector('{self.selectors["company_size"]}');
                    data.company_size = sizeElement ? sizeElement.textContent.trim() : '';
                    
                    // 行業
                    const industryElement = document.querySelector('{self.selectors["company_industry"]}');
                    data.industry = industryElement ? industryElement.textContent.trim() : '';
                    
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
            
            # 解析公司評分
            company_rating = self._parse_rating(job_data.get('company_rating', ''))
            
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
                raw_data={
                    **job_data,
                    "company_rating": company_rating,
                    "company_size": job_data.get('company_size', ''),
                    "industry": job_data.get('industry', '')
                }
            )
            
            self.logger.debug(
                "解析Glassdoor職位數據成功",
                title=job.title,
                company=job.company,
                url=job_url
            )
            
            return job
            
        except Exception as e:
            self.logger.error(
                "解析Glassdoor職位數據失敗",
                error=str(e),
                url=job_url
            )
            return None
    
    async def get_job_details(self, job_url: str, 
                            method: SearchMethod = SearchMethod.WEB_SCRAPING) -> Optional[JobData]:
        """獲取Glassdoor職位詳情
        
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
                # 需要處理Glassdoor的註冊牆
                pass
            
            # 暫時返回None，實際實現需要完整的爬取邏輯
            return None
            
        except Exception as e:
            self.logger.error(
                "獲取Glassdoor職位詳情失敗",
                error=str(e),
                url=job_url
            )
            return None
    
    async def get_salary_info(self, job_title: str, company: str, location: str) -> Dict[str, Any]:
        """獲取薪資信息
        
        Args:
            job_title: 職位標題
            company: 公司名稱
            location: 位置
            
        Returns:
            Dict[str, Any]: 薪資信息
        """
        try:
            # 構建薪資搜索URL
            params = {
                "keyword": job_title,
                "location": location
            }
            
            if company:
                params["company"] = company
            
            salary_url = f"{self.salaries_url}?{urlencode(params)}"
            
            # 這裡需要實現薪資頁面的爬取邏輯
            # 返回薪資範圍、分佈、福利等信息
            
            return {
                "salary_range": None,
                "average_salary": None,
                "salary_distribution": [],
                "benefits": [],
                "source_url": salary_url
            }
            
        except Exception as e:
            self.logger.error(
                "獲取薪資信息失敗",
                error=str(e),
                job_title=job_title,
                company=company
            )
            return {}
    
    async def get_company_reviews(self, company: str) -> Dict[str, Any]:
        """獲取公司評價
        
        Args:
            company: 公司名稱
            
        Returns:
            Dict[str, Any]: 公司評價信息
        """
        try:
            # 構建公司評價URL
            # Glassdoor的公司評價URL格式較複雜，需要先搜索公司
            
            # 這裡需要實現公司評價頁面的爬取邏輯
            # 返回評分、評價、工作環境等信息
            
            return {
                "overall_rating": None,
                "ratings": {
                    "culture_values": None,
                    "diversity_inclusion": None,
                    "work_life_balance": None,
                    "senior_management": None,
                    "compensation_benefits": None,
                    "career_opportunities": None
                },
                "reviews": [],
                "pros": [],
                "cons": [],
                "advice_to_management": []
            }
            
        except Exception as e:
            self.logger.error(
                "獲取公司評價失敗",
                error=str(e),
                company=company
            )
            return {}
    
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
        if "hour" in salary_text.lower() or "/hr" in salary_text.lower():
            period = "hourly"
        elif "month" in salary_text.lower() or "/mo" in salary_text.lower():
            period = "monthly"
        elif "year" in salary_text.lower() or "/yr" in salary_text.lower():
            period = "yearly"
        
        # 提取數字（支持K等單位）
        numbers = re.findall(r'[\d,]+(?:\.\d+)?[Kk]?', salary_text)
        
        def parse_number(num_str):
            """解析數字字符串，支持K等單位"""
            num_str = num_str.replace(',', '')
            if num_str.lower().endswith('k'):
                return int(float(num_str[:-1]) * 1000)
            else:
                return int(float(num_str))
        
        if len(numbers) >= 2:
            # 範圍薪資
            try:
                min_salary = parse_number(numbers[0])
                max_salary = parse_number(numbers[1])
                return min_salary, max_salary, currency, period
            except ValueError:
                pass
        elif len(numbers) == 1:
            # 單一薪資或估算
            try:
                salary = parse_number(numbers[0])
                # Glassdoor通常提供估算範圍，這裡假設±20%
                min_salary = int(salary * 0.8)
                max_salary = int(salary * 1.2)
                return min_salary, max_salary, currency, period
            except ValueError:
                pass
        
        return None, None, currency, period
    
    def _parse_rating(self, rating_text: str) -> Optional[float]:
        """解析評分
        
        Args:
            rating_text: 評分文本
            
        Returns:
            Optional[float]: 評分數值
        """
        if not rating_text:
            return None
        
        # 提取數字評分
        match = re.search(r'(\d+\.\d+|\d+)', rating_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _extract_job_id(self, job_url: str) -> Optional[str]:
        """從URL中提取職位ID
        
        Args:
            job_url: 職位URL
            
        Returns:
            Optional[str]: 職位ID
        """
        try:
            # Glassdoor的職位ID通常在URL路徑中
            # 例如: https://www.glassdoor.com/job-listing/software-engineer-company-JV_IC1147401_KO0,17_KE18,25.htm?jl=1234567890
            
            # 從查詢參數中提取
            parsed_url = urlparse(job_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'jl' in query_params:
                return query_params['jl'][0]
            
            # 從路徑中提取
            path_parts = parsed_url.path.split('/')
            for part in path_parts:
                if part and len(part) > 10 and not part.endswith('.htm'):
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
            
            # 檢查登錄牆
            login_wall = await page.query_selector(self.selectors["login_wall"])
            if login_wall:
                self.logger.warning("檢測到登錄牆", url=page.url)
                return True
            
            # 檢查頁面標題
            title = await page.title()
            if "blocked" in title.lower() or "access denied" in title.lower():
                self.logger.warning("頁面標題顯示被阻止", title=title, url=page.url)
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning("檢查阻止狀態失敗", error=str(e))
            return False
    
    async def _handle_signup_modal(self, page: Page) -> None:
        """處理註冊彈窗
        
        Args:
            page: 頁面對象
        """
        try:
            # 檢查是否有註冊彈窗
            signup_modal = await page.query_selector(self.selectors["signup_modal"])
            if signup_modal:
                # 嘗試關閉彈窗
                close_button = await signup_modal.query_selector('[data-test="modal-close"], .close-button')
                if close_button:
                    await close_button.click()
                    await asyncio.sleep(1)
                    self.logger.debug("關閉註冊彈窗")
                
                # 或者點擊背景關閉
                else:
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(1)
                    self.logger.debug("使用ESC關閉註冊彈窗")
                    
        except Exception as e:
            self.logger.warning("處理註冊彈窗失敗", error=str(e))
    
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
            
            # 處理註冊提示
            await self._handle_signup_modal(page)
            
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
                    
                    salary_element = await card.query_selector(self.selectors["salary_estimate"])
                    salary_text = await salary_element.text_content() if salary_element else ""
                    
                    rating_element = await card.query_selector(self.selectors["rating"])
                    rating_text = await rating_element.text_content() if rating_element else ""
                    
                    if not title or not link:
                        continue
                    
                    # 轉換為絕對URL
                    if link.startswith('/'):
                        link = f"{self.base_url}{link}"
                    
                    # 解析薪資
                    salary_min, salary_max, salary_currency, salary_period = self._parse_salary(salary_text)
                    
                    # 解析評分
                    company_rating = self._parse_rating(rating_text)
                    
                    # 提取職位ID
                    job_id = self._extract_job_id(link)
                    
                    # 創建JobData對象
                    job = JobData(
                        title=title.strip(),
                        company=company.strip(),
                        location=location.strip(),
                        url=link,
                        description="",  # 搜索結果頁面通常沒有完整描述
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
                            "salary_text": salary_text,
                            "rating_text": rating_text,
                            "company_rating": company_rating
                        }
                    )
                    
                    jobs.append(job)
                    
                except Exception as e:
                    self.logger.warning("解析職位卡片失敗", error=str(e))
                    continue
            
            self.logger.debug(
                "解析Glassdoor搜索結果",
                jobs_found=len(jobs),
                url=page.url
            )
            
        except Exception as e:
            self.logger.error(
                "解析Glassdoor搜索結果失敗",
                error=str(e),
                url=page.url
            )
        
        return jobs