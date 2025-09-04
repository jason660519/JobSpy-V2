"""爬蟲引擎主控制器

統一管理所有爬蟲任務的執行、調度和結果處理。
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import structlog

from ..config import CrawlerConfig, ProcessingStrategy
from ..ai.vision_service import AIVisionService
from ..scraper.smart_scraper import SmartScraper
from ..platforms.registry import PlatformRegistry
from .scheduler import TaskScheduler
from .processor import ResultProcessor

logger = structlog.get_logger(__name__)


@dataclass
class SearchRequest:
    """搜索請求數據結構"""
    query: str
    location: str = ""
    platforms: List[str] = None
    max_results: int = 50
    filters: Dict[str, Any] = None
    user_id: Optional[str] = None
    request_id: str = None
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())
        if self.platforms is None:
            self.platforms = ["indeed", "linkedin", "glassdoor"]
        if self.filters is None:
            self.filters = {}


@dataclass
class SearchResult:
    """搜索結果數據結構"""
    request_id: str
    jobs: List[Dict[str, Any]]
    total_found: int
    successful_platforms: List[str]
    failed_platforms: List[str]
    processing_time_ms: int
    cost_breakdown: Dict[str, float]
    confidence_score: float
    metadata: Dict[str, Any]
    created_at: datetime


class CrawlerEngine:
    """爬蟲引擎主控制器
    
    負責協調AI視覺服務、智能爬蟲和平台適配器，
    實現高效的多平台求職數據採集。
    """
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.logger = logger.bind(component="crawler_engine")
        
        # 初始化核心服務
        self.ai_vision = AIVisionService(config.ai)
        self.scraper = SmartScraper(config.scraping)
        self.platform_registry = PlatformRegistry(config.platforms)
        self.scheduler = TaskScheduler(config.max_concurrent_jobs)
        self.processor = ResultProcessor(config.storage)
        
        # 運行時狀態
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._cost_tracker = CostTracker(config.ai.daily_budget_usd)
        
    async def initialize(self):
        """初始化引擎"""
        self.logger.info("正在初始化爬蟲引擎...")
        
        try:
            # 初始化各個組件
            await self.ai_vision.initialize()
            await self.scraper.initialize()
            await self.platform_registry.initialize()
            await self.processor.initialize()
            
            self.logger.info("爬蟲引擎初始化完成")
            
        except Exception as e:
            self.logger.error("爬蟲引擎初始化失敗", error=str(e))
            raise
    
    async def search_jobs(self, request: SearchRequest) -> AsyncGenerator[Dict[str, Any], None]:
        """執行求職搜索
        
        Args:
            request: 搜索請求
            
        Yields:
            Dict: 實時搜索進度和結果
        """
        start_time = datetime.now()
        self.logger.info("開始執行求職搜索", request_id=request.request_id, query=request.query)
        
        try:
            # 1. 驗證請求
            yield {"stage": "validation", "message": "驗證搜索請求", "progress": 5}
            await self._validate_request(request)
            
            # 2. 分析查詢
            yield {"stage": "analysis", "message": "分析搜索查詢", "progress": 15}
            analysis = await self._analyze_query(request)
            
            # 3. 選擇平台
            yield {"stage": "platform_selection", "message": "選擇搜索平台", "progress": 25}
            selected_platforms = await self._select_platforms(request, analysis)
            
            # 4. 執行搜索
            yield {"stage": "searching", "message": "執行多平台搜索", "progress": 40}
            
            search_results = []
            async for platform_result in self._execute_platform_searches(request, selected_platforms):
                search_results.append(platform_result)
                progress = 40 + (len(search_results) / len(selected_platforms)) * 40
                yield {
                    "stage": "searching", 
                    "message": f"已完成 {platform_result['platform']} 搜索",
                    "progress": progress,
                    "partial_results": platform_result
                }
            
            # 5. 處理結果
            yield {"stage": "processing", "message": "處理和整合結果", "progress": 85}
            final_result = await self._process_results(request, search_results, start_time)
            
            # 6. 存儲結果
            yield {"stage": "storage", "message": "存儲搜索結果", "progress": 95}
            await self.processor.store_search_result(final_result)
            
            # 7. 完成
            yield {
                "stage": "completed", 
                "message": "搜索完成", 
                "progress": 100,
                "result": final_result
            }
            
        except Exception as e:
            self.logger.error("搜索執行失敗", request_id=request.request_id, error=str(e))
            yield {
                "stage": "error",
                "message": f"搜索失敗: {str(e)}",
                "progress": 0,
                "error": str(e)
            }
    
    async def _validate_request(self, request: SearchRequest):
        """驗證搜索請求"""
        if not request.query.strip():
            raise ValueError("搜索查詢不能為空")
        
        if request.max_results <= 0 or request.max_results > 1000:
            raise ValueError("結果數量必須在1-1000之間")
        
        # 檢查成本限制
        if not await self._cost_tracker.can_proceed():
            raise ValueError("已達到每日成本限制")
    
    async def _analyze_query(self, request: SearchRequest) -> Dict[str, Any]:
        """分析搜索查詢"""
        # 使用AI分析查詢意圖和關鍵詞
        if self.config.processing_strategy in [ProcessingStrategy.AI_VISION_ONLY, ProcessingStrategy.HYBRID]:
            analysis = await self.ai_vision.analyze_search_query(request.query, request.location)
        else:
            # 簡單的關鍵詞分析
            analysis = {
                "keywords": request.query.split(),
                "job_type": "unknown",
                "experience_level": "unknown",
                "industry": "unknown"
            }
        
        return analysis
    
    async def _select_platforms(self, request: SearchRequest, analysis: Dict[str, Any]) -> List[str]:
        """選擇最適合的搜索平台"""
        available_platforms = list(self.platform_registry.get_available_platforms())
        
        # 如果用戶指定了平台，使用用戶選擇
        if request.platforms:
            selected = [p for p in request.platforms if p in available_platforms]
        else:
            # 基於分析結果智能選擇平台
            selected = await self._intelligent_platform_selection(analysis, available_platforms)
        
        return selected
    
    async def _intelligent_platform_selection(self, analysis: Dict[str, Any], available: List[str]) -> List[str]:
        """智能平台選擇"""
        # 基於職位類型和行業選擇最佳平台
        job_type = analysis.get("job_type", "unknown")
        industry = analysis.get("industry", "unknown")
        
        platform_scores = {}
        for platform in available:
            score = 1.0  # 基礎分數
            
            # 根據平台特性調整分數
            if platform == "linkedin" and job_type in ["management", "sales", "marketing"]:
                score += 0.3
            elif platform == "indeed" and job_type in ["technical", "engineering"]:
                score += 0.2
            elif platform == "glassdoor" and "salary" in analysis.get("keywords", []):
                score += 0.2
            
            platform_scores[platform] = score
        
        # 選擇分數最高的平台（最多3個）
        sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_platforms[:3]]
    
    async def _execute_platform_searches(self, request: SearchRequest, platforms: List[str]) -> AsyncGenerator[Dict[str, Any], None]:
        """執行多平台搜索"""
        tasks = []
        
        for platform in platforms:
            task = asyncio.create_task(
                self._search_single_platform(request, platform)
            )
            tasks.append(task)
        
        # 等待所有任務完成，但允許部分失敗
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                yield result
            except Exception as e:
                self.logger.error("平台搜索失敗", platform=platform, error=str(e))
                yield {
                    "platform": platform,
                    "success": False,
                    "error": str(e),
                    "jobs": []
                }
    
    async def _search_single_platform(self, request: SearchRequest, platform: str) -> Dict[str, Any]:
        """搜索單個平台"""
        platform_config = self.platform_registry.get_platform_config(platform)
        
        try:
            # 根據處理策略選擇搜索方法
            if self.config.processing_strategy == ProcessingStrategy.API_FIRST:
                jobs = await self._try_api_search(platform, request)
            elif self.config.processing_strategy == ProcessingStrategy.AI_VISION_ONLY:
                jobs = await self._ai_vision_search(platform, request)
            else:
                # 混合策略：先嘗試API，再嘗試爬蟲，最後使用AI視覺
                jobs = await self._hybrid_search(platform, request)
            
            return {
                "platform": platform,
                "success": True,
                "jobs": jobs,
                "count": len(jobs)
            }
            
        except Exception as e:
            self.logger.error("平台搜索失敗", platform=platform, error=str(e))
            raise
    
    async def _try_api_search(self, platform: str, request: SearchRequest) -> List[Dict[str, Any]]:
        """嘗試API搜索"""
        # 大多數求職網站不提供公開API，這裡主要是預留接口
        raise NotImplementedError(f"{platform} API搜索暫未實現")
    
    async def _ai_vision_search(self, platform: str, request: SearchRequest) -> List[Dict[str, Any]]:
        """AI視覺搜索"""
        platform_config = self.platform_registry.get_platform_config(platform)
        
        # 構建搜索URL
        search_url = await self._build_search_url(platform, request)
        
        # 使用智能爬蟲獲取頁面截圖
        screenshot = await self.scraper.capture_page_screenshot(search_url)
        
        # 使用AI視覺分析提取職位信息
        prompt = platform_config.ai_prompts.get("extract_jobs", "請提取頁面中的所有職位信息")
        jobs = await self.ai_vision.extract_jobs_from_screenshot(screenshot, prompt)
        
        return jobs
    
    async def _hybrid_search(self, platform: str, request: SearchRequest) -> List[Dict[str, Any]]:
        """混合搜索策略"""
        try:
            # 1. 嘗試傳統爬蟲
            jobs = await self._traditional_scraping(platform, request)
            if jobs:
                return jobs
        except Exception as e:
            self.logger.warning("傳統爬蟲失敗，嘗試AI視覺", platform=platform, error=str(e))
        
        # 2. 回退到AI視覺分析
        return await self._ai_vision_search(platform, request)
    
    async def _traditional_scraping(self, platform: str, request: SearchRequest) -> List[Dict[str, Any]]:
        """傳統爬蟲方法"""
        platform_config = self.platform_registry.get_platform_config(platform)
        search_url = await self._build_search_url(platform, request)
        
        # 使用智能爬蟲執行傳統DOM解析
        jobs = await self.scraper.scrape_jobs_traditional(
            search_url, 
            platform_config.selectors,
            max_results=request.max_results
        )
        
        return jobs
    
    async def _build_search_url(self, platform: str, request: SearchRequest) -> str:
        """構建搜索URL"""
        platform_config = self.platform_registry.get_platform_config(platform)
        
        # 基礎URL
        base_url = platform_config.base_url + platform_config.search_endpoint
        
        # 構建查詢參數
        params = {
            "q": request.query,
            "l": request.location
        }
        
        # 平台特定參數
        if platform == "indeed":
            params.update({"sort": "date", "limit": request.max_results})
        elif platform == "linkedin":
            params.update({"keywords": request.query, "locationId": request.location})
        elif platform == "glassdoor":
            params.update({"sc.keyword": request.query, "locT": "C", "locId": request.location})
        
        # 構建完整URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])
        return f"{base_url}?{query_string}"
    
    async def _process_results(self, request: SearchRequest, search_results: List[Dict[str, Any]], start_time: datetime) -> SearchResult:
        """處理和整合搜索結果"""
        all_jobs = []
        successful_platforms = []
        failed_platforms = []
        cost_breakdown = {}
        
        for result in search_results:
            if result["success"]:
                all_jobs.extend(result["jobs"])
                successful_platforms.append(result["platform"])
            else:
                failed_platforms.append(result["platform"])
        
        # 去重和排序
        unique_jobs = await self._deduplicate_jobs(all_jobs)
        sorted_jobs = await self._sort_jobs(unique_jobs, request)
        
        # 限制結果數量
        final_jobs = sorted_jobs[:request.max_results]
        
        # 計算置信度分數
        confidence_score = self._calculate_confidence_score(successful_platforms, failed_platforms, len(final_jobs))
        
        # 計算處理時間
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return SearchResult(
            request_id=request.request_id,
            jobs=final_jobs,
            total_found=len(all_jobs),
            successful_platforms=successful_platforms,
            failed_platforms=failed_platforms,
            processing_time_ms=processing_time,
            cost_breakdown=cost_breakdown,
            confidence_score=confidence_score,
            metadata={
                "query": request.query,
                "location": request.location,
                "filters": request.filters,
                "strategy": self.config.processing_strategy.value
            },
            created_at=datetime.now()
        )
    
    async def _deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重複職位"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # 使用標題+公司+地點作為去重鍵
            key = f"{job.get('title', '')}-{job.get('company', '')}-{job.get('location', '')}".lower()
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    async def _sort_jobs(self, jobs: List[Dict[str, Any]], request: SearchRequest) -> List[Dict[str, Any]]:
        """排序職位"""
        # 簡單的相關性排序（可以後續使用AI改進）
        query_keywords = set(request.query.lower().split())
        
        def relevance_score(job):
            title_words = set(job.get("title", "").lower().split())
            desc_words = set(job.get("description", "").lower().split())
            
            title_matches = len(query_keywords.intersection(title_words))
            desc_matches = len(query_keywords.intersection(desc_words))
            
            return title_matches * 2 + desc_matches  # 標題匹配權重更高
        
        return sorted(jobs, key=relevance_score, reverse=True)
    
    def _calculate_confidence_score(self, successful: List[str], failed: List[str], job_count: int) -> float:
        """計算置信度分數"""
        total_platforms = len(successful) + len(failed)
        if total_platforms == 0:
            return 0.0
        
        success_rate = len(successful) / total_platforms
        job_factor = min(job_count / 50, 1.0)  # 假設50個職位是理想數量
        
        return (success_rate * 0.7 + job_factor * 0.3) * 100
    
    async def get_search_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """獲取搜索狀態"""
        if request_id in self._active_tasks:
            task = self._active_tasks[request_id]
            return {
                "status": "running" if not task.done() else "completed",
                "request_id": request_id
            }
        return None
    
    async def cancel_search(self, request_id: str) -> bool:
        """取消搜索"""
        if request_id in self._active_tasks:
            task = self._active_tasks[request_id]
            task.cancel()
            del self._active_tasks[request_id]
            return True
        return False
    
    async def cleanup(self):
        """清理資源"""
        self.logger.info("正在清理爬蟲引擎資源...")
        
        # 取消所有活動任務
        for task in self._active_tasks.values():
            task.cancel()
        
        # 清理各個組件
        await self.scraper.cleanup()
        await self.ai_vision.cleanup()
        await self.processor.cleanup()
        
        self.logger.info("爬蟲引擎資源清理完成")


class CostTracker:
    """成本追蹤器"""
    
    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.current_cost = 0.0
        self.last_reset = datetime.now().date()
    
    async def can_proceed(self) -> bool:
        """檢查是否可以繼續（未超出預算）"""
        self._reset_if_new_day()
        return self.current_cost < self.daily_budget
    
    async def add_cost(self, amount: float):
        """添加成本"""
        self._reset_if_new_day()
        self.current_cost += amount
    
    def _reset_if_new_day(self):
        """如果是新的一天，重置成本"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.current_cost = 0.0
            self.last_reset = today