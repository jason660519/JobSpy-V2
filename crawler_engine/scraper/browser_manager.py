"""瀏覽器管理器

提供瀏覽器實例的管理、池化和資源控制功能。
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog
from playwright.async_api import Playwright, Browser, BrowserType

from ..config import ScrapingConfig

logger = structlog.get_logger(__name__)


@dataclass
class BrowserInstance:
    """瀏覽器實例信息"""
    browser: Browser
    browser_type: str
    created_at: datetime
    last_used: datetime
    context_count: int = 0
    max_contexts: int = 10
    is_healthy: bool = True
    
    def is_overloaded(self) -> bool:
        """檢查是否過載"""
        return self.context_count >= self.max_contexts
    
    def is_expired(self, max_age_minutes: int = 60) -> bool:
        """檢查是否過期"""
        age = datetime.now() - self.created_at
        return age > timedelta(minutes=max_age_minutes)


class BrowserManager:
    """瀏覽器管理器
    
    提供瀏覽器實例的創建、管理、池化和資源控制功能。
    """
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.logger = logger.bind(component="browser_manager")
        
        # 瀏覽器池
        self.browser_pool: List[BrowserInstance] = []
        self.max_browsers = 3  # 最大瀏覽器實例數
        self.max_browser_age_minutes = 60  # 瀏覽器最大存活時間
        
        # Playwright實例
        self._playwright: Optional[Playwright] = None
        
        # 瀏覽器類型配置
        self.browser_types = {
            "chromium": {
                "weight": 70,  # 使用權重
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection"
                ]
            },
            "firefox": {
                "weight": 20,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            },
            "webkit": {
                "weight": 10,
                "args": []
            }
        }
        
        # 統計信息
        self._stats = {
            "browsers_created": 0,
            "browsers_destroyed": 0,
            "contexts_created": 0,
            "contexts_destroyed": 0,
            "current_browsers": 0,
            "current_contexts": 0
        }
        
        # 清理任務
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self, playwright: Playwright):
        """初始化瀏覽器管理器
        
        Args:
            playwright: Playwright實例
        """
        try:
            self.logger.info("正在初始化瀏覽器管理器...")
            
            self._playwright = playwright
            
            # 創建初始瀏覽器實例
            await self._create_initial_browsers()
            
            # 啟動清理任務
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info(
                "瀏覽器管理器初始化完成",
                browser_count=len(self.browser_pool)
            )
            
        except Exception as e:
            self.logger.error("瀏覽器管理器初始化失敗", error=str(e))
            raise
    
    async def _create_initial_browsers(self):
        """創建初始瀏覽器實例"""
        # 創建一個默認的Chromium瀏覽器
        try:
            browser = await self._create_browser("chromium")
            if browser:
                self.logger.info("創建了初始瀏覽器實例")
        except Exception as e:
            self.logger.warning("創建初始瀏覽器失敗", error=str(e))
    
    async def get_browser(self, preferred_type: Optional[str] = None) -> Browser:
        """獲取可用的瀏覽器實例
        
        Args:
            preferred_type: 首選瀏覽器類型
            
        Returns:
            Browser: 瀏覽器實例
        """
        # 清理過期和不健康的瀏覽器
        await self._cleanup_browsers()
        
        # 查找可用的瀏覽器
        available_browser = self._find_available_browser(preferred_type)
        
        if available_browser:
            available_browser.last_used = datetime.now()
            self.logger.debug(
                "使用現有瀏覽器",
                browser_type=available_browser.browser_type,
                context_count=available_browser.context_count
            )
            return available_browser.browser
        
        # 如果沒有可用瀏覽器且未達到最大數量，創建新的
        if len(self.browser_pool) < self.max_browsers:
            browser_type = preferred_type or self._select_browser_type()
            browser = await self._create_browser(browser_type)
            if browser:
                return browser.browser
        
        # 如果無法創建新瀏覽器，使用負載最小的現有瀏覽器
        if self.browser_pool:
            least_loaded = min(self.browser_pool, key=lambda b: b.context_count)
            least_loaded.last_used = datetime.now()
            self.logger.warning(
                "使用過載的瀏覽器",
                browser_type=least_loaded.browser_type,
                context_count=least_loaded.context_count
            )
            return least_loaded.browser
        
        # 最後手段：創建臨時瀏覽器
        self.logger.error("無可用瀏覽器，創建臨時實例")
        temp_browser = await self._create_temporary_browser()
        return temp_browser
    
    def _find_available_browser(self, preferred_type: Optional[str] = None) -> Optional[BrowserInstance]:
        """查找可用的瀏覽器實例"""
        # 過濾健康且未過載的瀏覽器
        available_browsers = [
            b for b in self.browser_pool 
            if b.is_healthy and not b.is_overloaded()
        ]
        
        if not available_browsers:
            return None
        
        # 如果指定了首選類型，優先選擇
        if preferred_type:
            preferred_browsers = [
                b for b in available_browsers 
                if b.browser_type == preferred_type
            ]
            if preferred_browsers:
                return min(preferred_browsers, key=lambda b: b.context_count)
        
        # 選擇負載最小的瀏覽器
        return min(available_browsers, key=lambda b: b.context_count)
    
    def _select_browser_type(self) -> str:
        """基於權重選擇瀏覽器類型"""
        browser_types = list(self.browser_types.keys())
        weights = [self.browser_types[bt]["weight"] for bt in browser_types]
        
        # 加權隨機選擇
        total_weight = sum(weights)
        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                return browser_types[i]
        
        return "chromium"  # 默認選擇
    
    async def _create_browser(self, browser_type: str) -> Optional[BrowserInstance]:
        """創建新的瀏覽器實例
        
        Args:
            browser_type: 瀏覽器類型
            
        Returns:
            Optional[BrowserInstance]: 瀏覽器實例
        """
        try:
            self.logger.debug("創建瀏覽器實例", browser_type=browser_type)
            
            # 獲取瀏覽器類型對象
            browser_launcher = getattr(self._playwright, browser_type)
            
            # 準備啟動參數
            launch_options = {
                "headless": True,
                "args": self.browser_types[browser_type]["args"].copy()
            }
            
            # 添加隨機化參數
            if browser_type == "chromium":
                launch_options["args"].extend([
                    f"--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}",
                    f"--user-agent={await self._get_random_user_agent()}"
                ])
            
            # 啟動瀏覽器
            browser = await browser_launcher.launch(**launch_options)
            
            # 創建瀏覽器實例對象
            browser_instance = BrowserInstance(
                browser=browser,
                browser_type=browser_type,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
            
            # 添加到池中
            self.browser_pool.append(browser_instance)
            self._stats["browsers_created"] += 1
            self._stats["current_browsers"] = len(self.browser_pool)
            
            self.logger.info(
                "瀏覽器實例創建成功",
                browser_type=browser_type,
                total_browsers=len(self.browser_pool)
            )
            
            return browser_instance
            
        except Exception as e:
            self.logger.error(
                "瀏覽器實例創建失敗",
                browser_type=browser_type,
                error=str(e)
            )
            return None
    
    async def _create_temporary_browser(self) -> Browser:
        """創建臨時瀏覽器實例（不加入池中）"""
        try:
            self.logger.warning("創建臨時瀏覽器實例")
            
            browser_launcher = self._playwright.chromium
            browser = await browser_launcher.launch(
                headless=True,
                args=self.browser_types["chromium"]["args"]
            )
            
            return browser
            
        except Exception as e:
            self.logger.error("臨時瀏覽器創建失敗", error=str(e))
            raise
    
    async def _get_random_user_agent(self) -> str:
        """獲取隨機用戶代理"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        return random.choice(user_agents)
    
    async def notify_context_created(self, browser: Browser):
        """通知上下文已創建
        
        Args:
            browser: 瀏覽器實例
        """
        browser_instance = self._find_browser_instance(browser)
        if browser_instance:
            browser_instance.context_count += 1
            self._stats["contexts_created"] += 1
            self._stats["current_contexts"] += 1
            
            self.logger.debug(
                "上下文已創建",
                browser_type=browser_instance.browser_type,
                context_count=browser_instance.context_count
            )
    
    async def notify_context_closed(self, browser: Browser):
        """通知上下文已關閉
        
        Args:
            browser: 瀏覽器實例
        """
        browser_instance = self._find_browser_instance(browser)
        if browser_instance:
            browser_instance.context_count = max(0, browser_instance.context_count - 1)
            self._stats["contexts_destroyed"] += 1
            self._stats["current_contexts"] = max(0, self._stats["current_contexts"] - 1)
            
            self.logger.debug(
                "上下文已關閉",
                browser_type=browser_instance.browser_type,
                context_count=browser_instance.context_count
            )
    
    def _find_browser_instance(self, browser: Browser) -> Optional[BrowserInstance]:
        """查找瀏覽器實例對象"""
        for browser_instance in self.browser_pool:
            if browser_instance.browser == browser:
                return browser_instance
        return None
    
    async def _cleanup_browsers(self):
        """清理過期和不健康的瀏覽器"""
        browsers_to_remove = []
        
        for browser_instance in self.browser_pool:
            should_remove = False
            
            # 檢查是否過期
            if browser_instance.is_expired(self.max_browser_age_minutes):
                self.logger.debug(
                    "瀏覽器已過期",
                    browser_type=browser_instance.browser_type,
                    age_minutes=(datetime.now() - browser_instance.created_at).total_seconds() / 60
                )
                should_remove = True
            
            # 檢查健康狀態
            if not await self._check_browser_health(browser_instance):
                self.logger.debug(
                    "瀏覽器不健康",
                    browser_type=browser_instance.browser_type
                )
                should_remove = True
            
            if should_remove:
                browsers_to_remove.append(browser_instance)
        
        # 移除標記的瀏覽器
        for browser_instance in browsers_to_remove:
            await self._remove_browser(browser_instance)
    
    async def _check_browser_health(self, browser_instance: BrowserInstance) -> bool:
        """檢查瀏覽器健康狀態
        
        Args:
            browser_instance: 瀏覽器實例
            
        Returns:
            bool: 是否健康
        """
        try:
            # 檢查瀏覽器是否仍然連接
            if browser_instance.browser.is_connected():
                browser_instance.is_healthy = True
                return True
            else:
                browser_instance.is_healthy = False
                return False
                
        except Exception as e:
            self.logger.debug(
                "瀏覽器健康檢查失敗",
                browser_type=browser_instance.browser_type,
                error=str(e)
            )
            browser_instance.is_healthy = False
            return False
    
    async def _remove_browser(self, browser_instance: BrowserInstance):
        """移除瀏覽器實例
        
        Args:
            browser_instance: 要移除的瀏覽器實例
        """
        try:
            # 關閉瀏覽器
            if browser_instance.browser.is_connected():
                await browser_instance.browser.close()
            
            # 從池中移除
            if browser_instance in self.browser_pool:
                self.browser_pool.remove(browser_instance)
                self._stats["browsers_destroyed"] += 1
                self._stats["current_browsers"] = len(self.browser_pool)
                
                # 更新上下文統計
                self._stats["current_contexts"] = max(
                    0, 
                    self._stats["current_contexts"] - browser_instance.context_count
                )
            
            self.logger.debug(
                "瀏覽器實例已移除",
                browser_type=browser_instance.browser_type,
                remaining_browsers=len(self.browser_pool)
            )
            
        except Exception as e:
            self.logger.error(
                "移除瀏覽器實例失敗",
                browser_type=browser_instance.browser_type,
                error=str(e)
            )
    
    async def _cleanup_loop(self):
        """清理循環任務"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分鐘清理一次
                await self._cleanup_browsers()
                
                self.logger.debug(
                    "瀏覽器清理完成",
                    active_browsers=len(self.browser_pool),
                    total_contexts=sum(b.context_count for b in self.browser_pool)
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("瀏覽器清理循環錯誤", error=str(e))
                await asyncio.sleep(60)  # 錯誤後等待1分鐘
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = self._stats.copy()
        
        # 添加詳細信息
        stats["browser_details"] = []
        for browser_instance in self.browser_pool:
            stats["browser_details"].append({
                "browser_type": browser_instance.browser_type,
                "created_at": browser_instance.created_at.isoformat(),
                "last_used": browser_instance.last_used.isoformat(),
                "context_count": browser_instance.context_count,
                "max_contexts": browser_instance.max_contexts,
                "is_healthy": browser_instance.is_healthy,
                "is_overloaded": browser_instance.is_overloaded(),
                "is_expired": browser_instance.is_expired(self.max_browser_age_minutes)
            })
        
        return stats
    
    async def cleanup(self):
        """清理所有資源"""
        try:
            self.logger.info("正在清理瀏覽器管理器...")
            
            # 取消清理任務
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # 關閉所有瀏覽器
            for browser_instance in self.browser_pool.copy():
                await self._remove_browser(browser_instance)
            
            self.browser_pool.clear()
            
            self.logger.info("瀏覽器管理器已清理")
            
        except Exception as e:
            self.logger.error("瀏覽器管理器清理失敗", error=str(e))