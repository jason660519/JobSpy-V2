"""平台註冊器

管理和註冊所有可用的平台適配器，提供統一的平台選擇和管理接口。
"""

import asyncio
from typing import Dict, List, Optional, Type, Any, Set
from dataclasses import dataclass
from datetime import datetime
import structlog

from .base import (
    BasePlatformAdapter, 
    PlatformCapability, 
    SearchMethod, 
    SearchRequest, 
    SearchResult,
    PlatformConfig
)

logger = structlog.get_logger(__name__)


@dataclass
class PlatformInfo:
    """平台信息"""
    name: str
    adapter_class: Type[BasePlatformAdapter]
    config: PlatformConfig
    capabilities: List[PlatformCapability]
    methods: List[SearchMethod]
    priority: int = 1  # 優先級，數字越大優先級越高
    enabled: bool = True
    health_score: float = 1.0  # 健康分數 (0.0-1.0)
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0


class PlatformRegistry:
    """平台註冊器
    
    管理所有可用的平台適配器，提供平台選擇、健康檢查和負載均衡功能。
    """
    
    def __init__(self):
        self.logger = logger.bind(component="platform_registry")
        
        # 註冊的平台
        self._platforms: Dict[str, PlatformInfo] = {}
        
        # 活躍的適配器實例
        self._adapters: Dict[str, BasePlatformAdapter] = {}
        
        # 統計信息
        self._stats = {
            "total_platforms": 0,
            "enabled_platforms": 0,
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0
        }
    
    def register_platform(self, 
                         name: str,
                         adapter_class: Type[BasePlatformAdapter],
                         config: PlatformConfig,
                         priority: int = 1,
                         enabled: bool = True) -> bool:
        """註冊平台適配器
        
        Args:
            name: 平台名稱
            adapter_class: 適配器類
            config: 平台配置
            priority: 優先級
            enabled: 是否啟用
            
        Returns:
            bool: 是否註冊成功
        """
        try:
            # 創建臨時實例以獲取能力信息
            temp_adapter = adapter_class(config)
            
            platform_info = PlatformInfo(
                name=name,
                adapter_class=adapter_class,
                config=config,
                capabilities=temp_adapter.supported_capabilities,
                methods=temp_adapter.supported_methods,
                priority=priority,
                enabled=enabled
            )
            
            self._platforms[name] = platform_info
            self._stats["total_platforms"] += 1
            
            if enabled:
                self._stats["enabled_platforms"] += 1
            
            self.logger.info(
                "平台註冊成功",
                platform=name,
                capabilities=len(platform_info.capabilities),
                methods=len(platform_info.methods),
                priority=priority,
                enabled=enabled
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "平台註冊失敗",
                platform=name,
                error=str(e)
            )
            return False
    
    def unregister_platform(self, name: str) -> bool:
        """取消註冊平台
        
        Args:
            name: 平台名稱
            
        Returns:
            bool: 是否取消註冊成功
        """
        if name in self._platforms:
            platform_info = self._platforms[name]
            
            # 清理適配器實例
            if name in self._adapters:
                del self._adapters[name]
            
            del self._platforms[name]
            self._stats["total_platforms"] -= 1
            
            if platform_info.enabled:
                self._stats["enabled_platforms"] -= 1
            
            self.logger.info("平台取消註冊成功", platform=name)
            return True
        
        return False
    
    def enable_platform(self, name: str) -> bool:
        """啟用平台
        
        Args:
            name: 平台名稱
            
        Returns:
            bool: 是否啟用成功
        """
        if name in self._platforms:
            if not self._platforms[name].enabled:
                self._platforms[name].enabled = True
                self._stats["enabled_platforms"] += 1
                self.logger.info("平台已啟用", platform=name)
            return True
        return False
    
    def disable_platform(self, name: str) -> bool:
        """禁用平台
        
        Args:
            name: 平台名稱
            
        Returns:
            bool: 是否禁用成功
        """
        if name in self._platforms:
            if self._platforms[name].enabled:
                self._platforms[name].enabled = False
                self._stats["enabled_platforms"] -= 1
                
                # 清理適配器實例
                if name in self._adapters:
                    del self._adapters[name]
                
                self.logger.info("平台已禁用", platform=name)
            return True
        return False
    
    async def get_adapter(self, name: str) -> Optional[BasePlatformAdapter]:
        """獲取平台適配器實例
        
        Args:
            name: 平台名稱
            
        Returns:
            Optional[BasePlatformAdapter]: 適配器實例
        """
        if name not in self._platforms:
            self.logger.warning("平台未註冊", platform=name)
            return None
        
        platform_info = self._platforms[name]
        
        if not platform_info.enabled:
            self.logger.warning("平台已禁用", platform=name)
            return None
        
        # 如果適配器實例不存在，創建新實例
        if name not in self._adapters:
            try:
                adapter = platform_info.adapter_class(platform_info.config)
                self._adapters[name] = adapter
                
                self.logger.debug("創建適配器實例", platform=name)
                
            except Exception as e:
                self.logger.error(
                    "創建適配器實例失敗",
                    platform=name,
                    error=str(e)
                )
                return None
        
        return self._adapters[name]
    
    def get_platforms_by_capability(self, capability: PlatformCapability) -> List[str]:
        """根據功能獲取支持的平台列表
        
        Args:
            capability: 所需功能
            
        Returns:
            List[str]: 支持該功能的平台名稱列表
        """
        platforms = []
        
        for name, info in self._platforms.items():
            if info.enabled and capability in info.capabilities:
                platforms.append(name)
        
        # 按優先級和健康分數排序
        platforms.sort(
            key=lambda x: (self._platforms[x].priority, self._platforms[x].health_score),
            reverse=True
        )
        
        return platforms
    
    def get_platforms_by_method(self, method: SearchMethod) -> List[str]:
        """根據搜索方法獲取支持的平台列表
        
        Args:
            method: 搜索方法
            
        Returns:
            List[str]: 支持該方法的平台名稱列表
        """
        platforms = []
        
        for name, info in self._platforms.items():
            if info.enabled and method in info.methods:
                platforms.append(name)
        
        # 按優先級和健康分數排序
        platforms.sort(
            key=lambda x: (self._platforms[x].priority, self._platforms[x].health_score),
            reverse=True
        )
        
        return platforms
    
    def select_best_platforms(self, 
                            request: SearchRequest,
                            capability: PlatformCapability = PlatformCapability.JOB_SEARCH,
                            max_platforms: int = 3) -> List[str]:
        """選擇最佳平台組合
        
        Args:
            request: 搜索請求
            capability: 所需功能
            max_platforms: 最大平台數量
            
        Returns:
            List[str]: 推薦的平台名稱列表
        """
        # 獲取支持該功能的平台
        candidate_platforms = self.get_platforms_by_capability(capability)
        
        if not candidate_platforms:
            self.logger.warning("沒有找到支持該功能的平台", capability=capability.value)
            return []
        
        # 根據搜索請求進行平台評分
        scored_platforms = []
        
        for platform_name in candidate_platforms:
            score = self._calculate_platform_score(platform_name, request)
            scored_platforms.append((platform_name, score))
        
        # 按分數排序
        scored_platforms.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前N個平台
        selected = [platform for platform, score in scored_platforms[:max_platforms]]
        
        self.logger.debug(
            "選擇最佳平台",
            selected_platforms=selected,
            total_candidates=len(candidate_platforms)
        )
        
        return selected
    
    def _calculate_platform_score(self, platform_name: str, request: SearchRequest) -> float:
        """計算平台分數
        
        Args:
            platform_name: 平台名稱
            request: 搜索請求
            
        Returns:
            float: 平台分數
        """
        platform_info = self._platforms[platform_name]
        
        # 基礎分數
        score = platform_info.priority * 10
        
        # 健康分數權重
        score += platform_info.health_score * 20
        
        # 成功率權重
        total_requests = platform_info.success_count + platform_info.error_count
        if total_requests > 0:
            success_rate = platform_info.success_count / total_requests
            score += success_rate * 30
        
        # 支持的方法數量權重
        score += len(platform_info.methods) * 5
        
        # 特定平台的額外評分邏輯
        if platform_name == "indeed":
            # Indeed通常有更多的職位
            score += 15
        elif platform_name == "linkedin":
            # LinkedIn適合專業職位
            if any(keyword in request.query.lower() for keyword in 
                   ["senior", "manager", "director", "lead", "architect"]):
                score += 10
        elif platform_name == "glassdoor":
            # Glassdoor適合薪資相關搜索
            if request.salary_min or request.salary_max:
                score += 10
        
        return score
    
    async def health_check(self, platform_name: Optional[str] = None) -> Dict[str, bool]:
        """執行健康檢查
        
        Args:
            platform_name: 特定平台名稱，如果為None則檢查所有平台
            
        Returns:
            Dict[str, bool]: 平台健康狀態
        """
        results = {}
        
        platforms_to_check = [platform_name] if platform_name else list(self._platforms.keys())
        
        for name in platforms_to_check:
            if name not in self._platforms or not self._platforms[name].enabled:
                continue
            
            try:
                adapter = await self.get_adapter(name)
                if adapter:
                    # 執行簡單的健康檢查（可以是ping測試或簡單請求）
                    health_status = await self._perform_health_check(adapter)
                    results[name] = health_status
                    
                    # 更新健康分數
                    platform_info = self._platforms[name]
                    platform_info.last_health_check = datetime.now()
                    
                    if health_status:
                        platform_info.health_score = min(1.0, platform_info.health_score + 0.1)
                        platform_info.success_count += 1
                    else:
                        platform_info.health_score = max(0.0, platform_info.health_score - 0.2)
                        platform_info.error_count += 1
                        
                        # 如果健康分數過低，暫時禁用平台
                        if platform_info.health_score < 0.3:
                            self.logger.warning(
                                "平台健康分數過低，暫時禁用",
                                platform=name,
                                health_score=platform_info.health_score
                            )
                            platform_info.enabled = False
                else:
                    results[name] = False
                    
            except Exception as e:
                self.logger.error(
                    "健康檢查失敗",
                    platform=name,
                    error=str(e)
                )
                results[name] = False
        
        return results
    
    async def _perform_health_check(self, adapter: BasePlatformAdapter) -> bool:
        """執行具體的健康檢查
        
        Args:
            adapter: 平台適配器
            
        Returns:
            bool: 是否健康
        """
        try:
            # 這裡可以實現具體的健康檢查邏輯
            # 例如：訪問平台首頁、檢查API狀態等
            
            # 簡單的超時測試
            await asyncio.wait_for(
                asyncio.sleep(0.1),  # 模擬檢查
                timeout=5.0
            )
            
            return True
            
        except Exception:
            return False
    
    async def search_multiple_platforms(self, 
                                      request: SearchRequest,
                                      platforms: Optional[List[str]] = None,
                                      max_concurrent: int = 3) -> Dict[str, SearchResult]:
        """在多個平台上並發搜索
        
        Args:
            request: 搜索請求
            platforms: 指定平台列表，如果為None則自動選擇
            max_concurrent: 最大並發數
            
        Returns:
            Dict[str, SearchResult]: 各平台的搜索結果
        """
        if platforms is None:
            platforms = self.select_best_platforms(request)
        
        if not platforms:
            self.logger.warning("沒有可用的平台進行搜索")
            return {}
        
        # 創建搜索任務
        tasks = []
        for platform_name in platforms:
            task = self._search_single_platform(platform_name, request)
            tasks.append((platform_name, task))
        
        # 限制並發數
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_search(platform_name: str, task):
            async with semaphore:
                return platform_name, await task
        
        # 執行並發搜索
        limited_tasks = [limited_search(name, task) for name, task in tasks]
        completed_tasks = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # 處理結果
        results = {}
        for result in completed_tasks:
            if isinstance(result, Exception):
                self.logger.error("搜索任務異常", error=str(result))
                continue
            
            platform_name, search_result = result
            results[platform_name] = search_result
            
            # 更新統計
            self._stats["total_searches"] += 1
            if search_result.success:
                self._stats["successful_searches"] += 1
            else:
                self._stats["failed_searches"] += 1
        
        self.logger.info(
            "多平台搜索完成",
            platforms=list(results.keys()),
            total_jobs=sum(len(r.jobs) for r in results.values() if r.success)
        )
        
        return results
    
    async def _search_single_platform(self, platform_name: str, request: SearchRequest) -> SearchResult:
        """在單個平台上搜索
        
        Args:
            platform_name: 平台名稱
            request: 搜索請求
            
        Returns:
            SearchResult: 搜索結果
        """
        try:
            adapter = await self.get_adapter(platform_name)
            if not adapter:
                return SearchResult(
                    jobs=[],
                    total_count=0,
                    page=request.page,
                    has_next_page=False,
                    search_query=request.query,
                    platform=platform_name,
                    execution_time=0.0,
                    method_used=SearchMethod.WEB_SCRAPING,
                    success=False,
                    error_message="無法獲取適配器實例"
                )
            
            # 選擇最佳搜索方法
            method = adapter.get_best_method(request)
            
            # 執行搜索
            result = await adapter.search_jobs(request, method)
            
            # 更新平台統計
            platform_info = self._platforms[platform_name]
            if result.success:
                platform_info.success_count += 1
            else:
                platform_info.error_count += 1
            
            return result
            
        except Exception as e:
            self.logger.error(
                "平台搜索失敗",
                platform=platform_name,
                error=str(e)
            )
            
            return SearchResult(
                jobs=[],
                total_count=0,
                page=request.page,
                has_next_page=False,
                search_query=request.query,
                platform=platform_name,
                execution_time=0.0,
                method_used=SearchMethod.WEB_SCRAPING,
                success=False,
                error_message=str(e)
            )
    
    def get_platform_info(self, name: str) -> Optional[PlatformInfo]:
        """獲取平台信息
        
        Args:
            name: 平台名稱
            
        Returns:
            Optional[PlatformInfo]: 平台信息
        """
        return self._platforms.get(name)
    
    def list_platforms(self, enabled_only: bool = True) -> List[str]:
        """列出所有平台
        
        Args:
            enabled_only: 是否只返回啟用的平台
            
        Returns:
            List[str]: 平台名稱列表
        """
        if enabled_only:
            return [name for name, info in self._platforms.items() if info.enabled]
        else:
            return list(self._platforms.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取註冊器統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = self._stats.copy()
        
        # 添加平台詳細統計
        platform_stats = {}
        for name, info in self._platforms.items():
            total_requests = info.success_count + info.error_count
            success_rate = (info.success_count / total_requests * 100) if total_requests > 0 else 0.0
            
            platform_stats[name] = {
                "enabled": info.enabled,
                "priority": info.priority,
                "health_score": info.health_score,
                "success_count": info.success_count,
                "error_count": info.error_count,
                "success_rate": success_rate,
                "capabilities": [cap.value for cap in info.capabilities],
                "methods": [method.value for method in info.methods],
                "last_health_check": info.last_health_check.isoformat() if info.last_health_check else None
            }
        
        stats["platforms"] = platform_stats
        
        # 計算總體成功率
        if stats["total_searches"] > 0:
            stats["overall_success_rate"] = (stats["successful_searches"] / stats["total_searches"]) * 100
        else:
            stats["overall_success_rate"] = 0.0
        
        return stats
    
    async def cleanup(self):
        """清理所有資源"""
        # 清理所有適配器實例
        for adapter in self._adapters.values():
            try:
                await adapter.cleanup()
            except Exception as e:
                self.logger.warning("清理適配器失敗", error=str(e))
        
        self._adapters.clear()
        
        self.logger.info("平台註冊器清理完成")