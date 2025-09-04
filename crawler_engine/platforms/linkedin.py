"""LinkedIn平台適配器

實現LinkedIn求職網站的專用爬取邏輯，包括搜索、數據解析和反檢測策略。
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


class LinkedInAdapter(BasePlatformAdapter):
    """LinkedIn平台適配器
    
    專門處理LinkedIn網站的職位搜索和數據提取。
    注意：LinkedIn有嚴格的反爬蟲機制，需要謹慎處理。
    """
    
    @property
    def platform_name(self) -> str:
        return "linkedin"
    
    @property
    def supported_capabilities(self) -> List[PlatformCapability]:
        return [
            PlatformCapability.JOB_SEARCH,
            PlatformCapability.JOB_DETAILS,
            PlatformCapability.COMPANY_INFO,
            PlatformCapability.SALARY_INFO,
            PlatformCapability.PROFILE_INFO
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
        
        # LinkedIn特定的選擇器
        self.selectors = {
            # 搜索結果頁面
            "job_cards": '.job-search-card, .jobs-search-results__list-item',
            "job_title": '.job-search-card__title a, .base-search-card__title',
            "job_link": '.job-search-card__title a, .base-search-card__title a',
            "company_name": '.job-search-card__subtitle-link, .base-search-card__subtitle',
            "company_link": '.job-search-card__subtitle-link',
            "location": '.job-search-card__location, .job-search-card__location-text',
            "posted_date": '.job-search-card__listdate, .job-search-card__listdate--new',
            "job_insights": '.job-search-card__job-insight',
            
            # 分頁
            "next_page": 'button[aria-label="Next"]',
            "page_numbers": '.artdeco-pagination__pages li',
            
            # 職位詳情頁面
            "job_description": '.jobs-description-content__text, .jobs-box__html-content',
            "job_header": '.jobs-unified-top-card__job-title, .job-details-jobs-unified-top-card__job-title',
            "company_info": '.jobs-unified-top-card__company-name, .job-details-jobs-unified-top-card__company-name',
            "job_criteria": '.jobs-unified-top-card__job-insight, .job-details-jobs-unified-top-card__job-insight',
            "apply_button": '.jobs-apply-button, .jobs-s-apply button',
            "salary_info": '.jobs-unified-top-card__job-insight--salary',
            
            # 登錄相關
            "login_form": '#organic-div',
            "email_input": '#username',
            "password_input": '#password',
            "login_button": '.btn__primary--large',
            
            # 反檢測相關
            "challenge": '.challenge-page',
            "captcha": '.captcha-internal',
            "blocked_message": '.blocked-warning',
            "rate_limit": '.rate-limit-warning',
            "security_check": '.security-challenge-consumer'
        }
        
        # 更新配置中的選擇器
        self.config.selectors.update(self.selectors)
        
        # LinkedIn特定配置
        self.requires_login = True
        self.login_url = "https://www.linkedin.com/login"
        self.base_jobs_url = "https://www.linkedin.com/jobs/search"
    
    def build_search_url(self, request: SearchRequest) -> str:
        """構建LinkedIn搜索URL
        
        Args:
            request: 搜索請求
            
        Returns:
            str: 搜索URL
        """
        base_url = self.base_jobs_url
        
        params = {
            "keywords": request.query,
            "start": (request.page - 1) * 25,  # LinkedIn每頁25個結果
        }
        
        # 添加位置
        if request.location:
            params["location"] = request.location
        
        # 添加工作類型
        if request.job_type:
            job_type_map = {
                "full-time": "F",
                "part-time": "P",
                "contract": "C",
                "temporary": "T",
                "internship": "I",
                "volunteer": "V"
            }
            if request.job_type in job_type_map:
                params["f_JT"] = job_type_map[request.job_type]
        
        # 添加經驗等級
        if "experience_level" in request.extra_params:
            exp_level_map = {
                "internship": "1",
                "entry": "2",
                "associate": "3",
                "mid": "4",
                "senior": "5",
                "director": "6",
                "executive": "7"
            }
            exp_level = request.extra_params["experience_level"]
            if exp_level in exp_level_map:
                params["f_E"] = exp_level_map[exp_level]
        
        # 添加發布時間
        if request.date_posted:
            date_map = {
                "24h": "r86400",
                "3d": "r259200",
                "7d": "r604800",
                "14d": "r1209600",
                "30d": "r2592000"
            }
            if request.date_posted in date_map:
                params["f_TPR"] = date_map[request.date_posted]
        
        # 添加遠程工作
        if request.remote:
            params["f_WT"] = "2"  # Remote
        
        # 添加公司規模
        if "company_size" in request.extra_params:
            size_map = {
                "startup": "A,B",  # 1-10, 11-50
                "small": "C,D",    # 51-200, 201-500
                "medium": "E,F",   # 501-1000, 1001-5000
                "large": "G,H,I"   # 5001-10000, 10001+
            }
            size = request.extra_params["company_size"]
            if size in size_map:
                params["f_C"] = size_map[size]
        
        # 添加排序
        if request.sort_by == "date":
            params["sortBy"] = "DD"  # Date Descending
        elif request.sort_by == "relevance":
            params["sortBy"] = "R"   # Relevance
        
        # 添加額外參數
        params.update(request.extra_params)
        
        url = f"{base_url}?{urlencode(params)}"
        
        self.logger.debug(
            "構建LinkedIn搜索URL",
            url=url,
            query=request.query,
            location=request.location,
            page=request.page
        )
        
        return url
    
    async def search_jobs(self, request: SearchRequest, 
                         method: SearchMethod = SearchMethod.WEB_SCRAPING) -> SearchResult:
        """搜索LinkedIn職位
        
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
                "LinkedIn搜索完成",
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
                "LinkedIn搜索失敗",
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
        # LinkedIn需要登錄才能訪問完整的職位信息
        # 這裡需要實現登錄邏輯或使用已登錄的會話
        
        search_url = self.build_search_url(request)
        
        # 模擬搜索結果
        jobs = []
        
        # 實際實現中需要：
        # 1. 檢查登錄狀態
        # 2. 如果未登錄，執行登錄流程
        # 3. 導航到搜索URL
        # 4. 等待頁面加載
        # 5. 解析職位數據
        # 6. 處理分頁
        
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
        # LinkedIn的頁面結構複雜，AI視覺分析可能更有效
        
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
        # 先嘗試傳統爬取，如果遇到反檢測，切換到AI視覺分析
        
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
        """從LinkedIn搜索結果頁面提取職位鏈接
        
        Args:
            page: 頁面對象
            
        Returns:
            List[str]: 職位鏈接列表
        """
        try:
            # 等待職位卡片加載
            await page.wait_for_selector(self.selectors["job_cards"], timeout=15000)
            
            # 滾動頁面以加載更多內容
            await self._scroll_to_load_jobs(page)
            
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
            
            # 清理和去重鏈接
            unique_links = list(set(job_links))
            
            self.logger.debug(
                "提取LinkedIn職位鏈接",
                count=len(unique_links),
                url=page.url
            )
            
            return unique_links
            
        except Exception as e:
            self.logger.error(
                "提取LinkedIn職位鏈接失敗",
                error=str(e),
                url=page.url
            )
            return []
    
    async def parse_job_data(self, page: Page, job_url: str) -> Optional[JobData]:
        """解析LinkedIn職位數據
        
        Args:
            page: 頁面對象
            job_url: 職位URL
            
        Returns:
            Optional[JobData]: 解析的職位數據
        """
        try:
            # 等待頁面加載
            await page.wait_for_load_state("networkidle")
            
            # 檢查是否需要登錄或被阻止
            if await self._check_login_required(page) or await self._check_blocked(page):
                self.logger.warning("頁面需要登錄或被阻止", url=job_url)
                return None
            
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
                    const locationElements = document.querySelectorAll('{self.selectors["job_criteria"]}');
                    for (const element of locationElements) {{
                        const text = element.textContent.trim();
                        if (text && (text.includes(',') || text.includes('Remote') || text.includes('Hybrid'))) {{
                            data.location = text;
                            break;
                        }}
                    }}
                    
                    // 職位描述
                    const descElement = document.querySelector('{self.selectors["job_description"]}');
                    data.description = descElement ? descElement.innerHTML : '';
                    
                    // 薪資信息
                    const salaryElement = document.querySelector('{self.selectors["salary_info"]}');
                    data.salary_text = salaryElement ? salaryElement.textContent.trim() : '';
                    
                    // 工作類型和經驗等級
                    const criteriaElements = document.querySelectorAll('{self.selectors["job_criteria"]}');
                    criteriaElements.forEach(element => {{
                        const text = element.textContent.trim();
                        if (text.includes('Full-time') || text.includes('Part-time') || text.includes('Contract')) {{
                            data.job_type = text;
                        }}
                        if (text.includes('Entry level') || text.includes('Mid-Senior') || text.includes('Executive')) {{
                            data.experience_level = text;
                        }}
                    }});
                    
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
            
            # 解析工作類型
            job_type = self._parse_job_type(job_data.get('job_type', ''))
            
            # 創建JobData對象
            job = JobData(
                title=job_data['title'],
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                url=job_url,
                description=job_data.get('description', ''),
                job_type=job_type,
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
                "解析LinkedIn職位數據成功",
                title=job.title,
                company=job.company,
                url=job_url
            )
            
            return job
            
        except Exception as e:
            self.logger.error(
                "解析LinkedIn職位數據失敗",
                error=str(e),
                url=job_url
            )
            return None
    
    async def get_job_details(self, job_url: str, 
                            method: SearchMethod = SearchMethod.WEB_SCRAPING) -> Optional[JobData]:
        """獲取LinkedIn職位詳情
        
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
                # 需要處理LinkedIn的登錄要求
                pass
            
            # 暫時返回None，實際實現需要完整的爬取邏輯
            return None
            
        except Exception as e:
            self.logger.error(
                "獲取LinkedIn職位詳情失敗",
                error=str(e),
                url=job_url
            )
            return None
    
    async def login(self, page: Page, email: str, password: str) -> bool:
        """登錄LinkedIn
        
        Args:
            page: 頁面對象
            email: 郵箱
            password: 密碼
            
        Returns:
            bool: 登錄是否成功
        """
        try:
            # 導航到登錄頁面
            await page.goto(self.login_url)
            await page.wait_for_load_state("networkidle")
            
            # 填寫登錄表單
            await page.fill(self.selectors["email_input"], email)
            await page.fill(self.selectors["password_input"], password)
            
            # 點擊登錄按鈕
            await page.click(self.selectors["login_button"])
            
            # 等待登錄完成
            await page.wait_for_load_state("networkidle")
            
            # 檢查是否登錄成功
            current_url = page.url
            if "feed" in current_url or "jobs" in current_url:
                self.logger.info("LinkedIn登錄成功")
                return True
            else:
                self.logger.warning("LinkedIn登錄失敗", url=current_url)
                return False
                
        except Exception as e:
            self.logger.error("LinkedIn登錄過程失敗", error=str(e))
            return False
    
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
        elif "¥" in salary_text:
            currency = "JPY"
        
        # 檢測週期
        period = "yearly"
        if "hour" in salary_text.lower() or "/hr" in salary_text.lower():
            period = "hourly"
        elif "month" in salary_text.lower() or "/mo" in salary_text.lower():
            period = "monthly"
        elif "year" in salary_text.lower() or "/yr" in salary_text.lower():
            period = "yearly"
        
        # 提取數字（支持K, M等單位）
        numbers = re.findall(r'[\d,]+(?:\.\d+)?[KkMm]?', salary_text)
        
        def parse_number(num_str):
            """解析數字字符串，支持K, M等單位"""
            num_str = num_str.replace(',', '')
            if num_str.lower().endswith('k'):
                return int(float(num_str[:-1]) * 1000)
            elif num_str.lower().endswith('m'):
                return int(float(num_str[:-1]) * 1000000)
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
            # 單一薪資
            try:
                salary = parse_number(numbers[0])
                return salary, salary, currency, period
            except ValueError:
                pass
        
        return None, None, currency, period
    
    def _parse_job_type(self, job_type_text: str) -> Optional[str]:
        """解析工作類型
        
        Args:
            job_type_text: 工作類型文本
            
        Returns:
            Optional[str]: 標準化的工作類型
        """
        if not job_type_text:
            return None
        
        job_type_text = job_type_text.lower()
        
        if "full-time" in job_type_text or "full time" in job_type_text:
            return "full-time"
        elif "part-time" in job_type_text or "part time" in job_type_text:
            return "part-time"
        elif "contract" in job_type_text:
            return "contract"
        elif "temporary" in job_type_text or "temp" in job_type_text:
            return "temporary"
        elif "internship" in job_type_text or "intern" in job_type_text:
            return "internship"
        elif "volunteer" in job_type_text:
            return "volunteer"
        
        return None
    
    def _extract_job_id(self, job_url: str) -> Optional[str]:
        """從URL中提取職位ID
        
        Args:
            job_url: 職位URL
            
        Returns:
            Optional[str]: 職位ID
        """
        try:
            # LinkedIn的職位ID通常在URL路徑中
            # 例如: https://www.linkedin.com/jobs/view/1234567890
            match = re.search(r'/jobs/view/(\d+)', job_url)
            if match:
                return match.group(1)
            
            # 或者在查詢參數中
            parsed_url = urlparse(job_url)
            query_params = parse_qs(parsed_url.query)
            
            if 'currentJobId' in query_params:
                return query_params['currentJobId'][0]
            
            return None
            
        except Exception as e:
            self.logger.warning("提取職位ID失敗", error=str(e), url=job_url)
            return None
    
    async def _check_login_required(self, page: Page) -> bool:
        """檢查頁面是否需要登錄
        
        Args:
            page: 頁面對象
            
        Returns:
            bool: 是否需要登錄
        """
        try:
            # 檢查登錄表單
            login_form = await page.query_selector(self.selectors["login_form"])
            if login_form:
                return True
            
            # 檢查URL
            current_url = page.url
            if "login" in current_url or "authwall" in current_url:
                return True
            
            # 檢查頁面標題
            title = await page.title()
            if "sign in" in title.lower() or "login" in title.lower():
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning("檢查登錄狀態失敗", error=str(e))
            return False
    
    async def _check_blocked(self, page: Page) -> bool:
        """檢查頁面是否被阻止
        
        Args:
            page: 頁面對象
            
        Returns:
            bool: 是否被阻止
        """
        try:
            # 檢查安全挑戰
            security_check = await page.query_selector(self.selectors["security_check"])
            if security_check:
                self.logger.warning("檢測到安全挑戰", url=page.url)
                return True
            
            # 檢查CAPTCHA
            captcha = await page.query_selector(self.selectors["captcha"])
            if captcha:
                self.logger.warning("檢測到CAPTCHA", url=page.url)
                return True
            
            # 檢查挑戰頁面
            challenge = await page.query_selector(self.selectors["challenge"])
            if challenge:
                self.logger.warning("檢測到挑戰頁面", url=page.url)
                return True
            
            # 檢查阻止消息
            blocked = await page.query_selector(self.selectors["blocked_message"])
            if blocked:
                self.logger.warning("檢測到阻止消息", url=page.url)
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning("檢查阻止狀態失敗", error=str(e))
            return False
    
    async def _scroll_to_load_jobs(self, page: Page) -> None:
        """滾動頁面以加載更多職位
        
        Args:
            page: 頁面對象
        """
        try:
            # LinkedIn使用懶加載，需要滾動來加載更多內容
            for i in range(3):  # 滾動3次
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)  # 等待內容加載
                
                # 檢查是否有新內容加載
                job_count = await page.evaluate(f"""
                    document.querySelectorAll('{self.selectors["job_cards"]}').length
                """)
                
                self.logger.debug(f"滾動後職位數量: {job_count}")
                
        except Exception as e:
            self.logger.warning("滾動加載職位失敗", error=str(e))