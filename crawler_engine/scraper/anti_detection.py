"""反檢測管理器

提供各種反檢測技術，包括用戶代理輪換、行為模擬、指紋偽造等。
"""

import asyncio
import random
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import structlog
from playwright.async_api import BrowserContext, Page

from ..config import ScrapingConfig

logger = structlog.get_logger(__name__)


@dataclass
class UserAgentProfile:
    """用戶代理配置文件"""
    user_agent: str
    platform: str
    browser: str
    version: str
    mobile: bool = False


class AntiDetectionManager:
    """反檢測管理器
    
    提供全面的反檢測功能，包括用戶代理輪換、行為模擬、指紋偽造等。
    """
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.logger = logger.bind(component="anti_detection")
        
        # 用戶代理池
        self.user_agents = self._load_user_agents()
        
        # 行為模式配置
        self.behavior_patterns = {
            "scroll_delay": (1.0, 3.0),
            "click_delay": (0.5, 2.0),
            "typing_delay": (0.1, 0.3),
            "page_view_time": (5.0, 15.0)
        }
        
        # 指紋偽造配置
        self.fingerprint_config = {
            "languages": ["en-US", "en"],
            "timezones": ["America/New_York", "America/Los_Angeles", "Europe/London"],
            "screen_resolutions": [
                {"width": 1920, "height": 1080},
                {"width": 1366, "height": 768},
                {"width": 1440, "height": 900},
                {"width": 1536, "height": 864}
            ]
        }
    
    def _load_user_agents(self) -> List[UserAgentProfile]:
        """加載用戶代理池"""
        return [
            # Chrome用戶代理
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="Windows",
                browser="Chrome",
                version="120.0.0.0"
            ),
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="macOS",
                browser="Chrome",
                version="120.0.0.0"
            ),
            UserAgentProfile(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="Linux",
                browser="Chrome",
                version="120.0.0.0"
            ),
            
            # Firefox用戶代理
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                platform="Windows",
                browser="Firefox",
                version="121.0"
            ),
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                platform="macOS",
                browser="Firefox",
                version="121.0"
            ),
            
            # Safari用戶代理
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
                platform="macOS",
                browser="Safari",
                version="17.2"
            ),
            
            # Edge用戶代理
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                platform="Windows",
                browser="Edge",
                version="120.0.0.0"
            ),
            
            # 移動端用戶代理
            UserAgentProfile(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                platform="iOS",
                browser="Safari",
                version="17.2",
                mobile=True
            ),
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                platform="Android",
                browser="Chrome",
                version="120.0.0.0",
                mobile=True
            )
        ]
    
    async def get_random_user_agent(self, mobile: bool = False) -> str:
        """獲取隨機用戶代理
        
        Args:
            mobile: 是否返回移動端用戶代理
            
        Returns:
            str: 用戶代理字符串
        """
        filtered_agents = [ua for ua in self.user_agents if ua.mobile == mobile]
        if not filtered_agents:
            filtered_agents = self.user_agents
        
        selected_agent = random.choice(filtered_agents)
        
        self.logger.debug(
            "選擇用戶代理",
            browser=selected_agent.browser,
            platform=selected_agent.platform,
            mobile=selected_agent.mobile
        )
        
        return selected_agent.user_agent
    
    async def apply_stealth_mode(self, context: BrowserContext):
        """應用隱身模式配置
        
        Args:
            context: 瀏覽器上下文
        """
        try:
            self.logger.debug("應用隱身模式配置")
            
            # 添加初始化腳本
            await context.add_init_script(self._get_stealth_script())
            
            # 設置額外的HTTP頭
            await context.set_extra_http_headers(self._get_stealth_headers())
            
            self.logger.debug("隱身模式配置完成")
            
        except Exception as e:
            self.logger.error("應用隱身模式失敗", error=str(e))
            raise
    
    def _get_stealth_script(self) -> str:
        """獲取隱身腳本"""
        return """
        // 覆蓋webdriver屬性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // 覆蓋plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // 覆蓋languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        
        // 覆蓋permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 覆蓋chrome屬性
        window.chrome = {
            runtime: {},
        };
        
        // 移除自動化相關屬性
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        
        // 覆蓋toString方法
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === window.navigator.permissions.query) {
                return 'function query() { [native code] }';
            }
            return originalToString.apply(this, arguments);
        };
        
        // 模擬真實的屏幕屬性
        Object.defineProperty(screen, 'availHeight', {
            get: () => screen.height - 40,
        });
        
        Object.defineProperty(screen, 'availWidth', {
            get: () => screen.width,
        });
        
        // 添加隨機噪聲到canvas指紋
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type) {
            const context = getContext.apply(this, arguments);
            if (type === '2d') {
                const originalFillText = context.fillText;
                context.fillText = function() {
                    // 添加微小的隨機偏移
                    arguments[1] += Math.random() * 0.1;
                    arguments[2] += Math.random() * 0.1;
                    return originalFillText.apply(this, arguments);
                };
            }
            return context;
        };
        """
    
    def _get_stealth_headers(self) -> Dict[str, str]:
        """獲取隱身HTTP頭"""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
    
    async def simulate_human_behavior(self, page: Page, action_type: str = "browse"):
        """模擬人類行為
        
        Args:
            page: 頁面對象
            action_type: 行為類型 (browse, search, scroll)
        """
        try:
            self.logger.debug("模擬人類行為", action_type=action_type)
            
            if action_type == "browse":
                await self._simulate_browsing_behavior(page)
            elif action_type == "search":
                await self._simulate_search_behavior(page)
            elif action_type == "scroll":
                await self._simulate_scroll_behavior(page)
            
        except Exception as e:
            self.logger.warning("人類行為模擬失敗", error=str(e))
    
    async def _simulate_browsing_behavior(self, page: Page):
        """模擬瀏覽行為"""
        # 隨機移動鼠標
        await page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600)
        )
        
        # 隨機停留時間
        view_time = random.uniform(*self.behavior_patterns["page_view_time"])
        await asyncio.sleep(view_time)
        
        # 隨機滾動
        scroll_count = random.randint(1, 3)
        for _ in range(scroll_count):
            await page.mouse.wheel(0, random.randint(200, 500))
            await asyncio.sleep(random.uniform(*self.behavior_patterns["scroll_delay"]))
    
    async def _simulate_search_behavior(self, page: Page):
        """模擬搜索行為"""
        # 查找搜索框
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='search']",
            "input[name*='search']",
            "input[id*='search']"
        ]
        
        search_input = None
        for selector in search_selectors:
            search_input = await page.query_selector(selector)
            if search_input:
                break
        
        if search_input:
            # 點擊搜索框
            await search_input.click()
            await asyncio.sleep(random.uniform(*self.behavior_patterns["click_delay"]))
            
            # 模擬打字行為
            await self._simulate_typing(search_input, "software engineer")
    
    async def _simulate_scroll_behavior(self, page: Page):
        """模擬滾動行為"""
        # 獲取頁面高度
        page_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        
        if page_height <= viewport_height:
            return
        
        # 分段滾動
        scroll_steps = random.randint(3, 8)
        step_size = (page_height - viewport_height) // scroll_steps
        
        for i in range(scroll_steps):
            scroll_y = step_size * (i + 1)
            await page.evaluate(f"window.scrollTo(0, {scroll_y})")
            
            # 隨機停留時間
            await asyncio.sleep(random.uniform(*self.behavior_patterns["scroll_delay"]))
            
            # 偶爾向上滾動一點
            if random.random() < 0.3:
                back_scroll = random.randint(50, 200)
                await page.evaluate(f"window.scrollBy(0, -{back_scroll})")
                await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def _simulate_typing(self, element, text: str):
        """模擬打字行為
        
        Args:
            element: 輸入元素
            text: 要輸入的文本
        """
        # 清空現有內容
        await element.fill("")
        
        # 逐字符輸入
        for char in text:
            await element.type(char)
            # 隨機打字延遲
            delay = random.uniform(*self.behavior_patterns["typing_delay"])
            await asyncio.sleep(delay)
        
        # 偶爾模擬打字錯誤和修正
        if random.random() < 0.1:
            # 添加錯誤字符
            await element.type(random.choice("abcdefghijklmnopqrstuvwxyz"))
            await asyncio.sleep(0.5)
            # 刪除錯誤字符
            await element.press("Backspace")
            await asyncio.sleep(0.3)
    
    async def randomize_viewport(self, context: BrowserContext):
        """隨機化視窗大小
        
        Args:
            context: 瀏覽器上下文
        """
        resolution = random.choice(self.fingerprint_config["screen_resolutions"])
        
        # 添加隨機偏移
        width = resolution["width"] + random.randint(-50, 50)
        height = resolution["height"] + random.randint(-50, 50)
        
        await context.set_viewport_size({"width": width, "height": height})
        
        self.logger.debug("設置隨機視窗大小", width=width, height=height)
    
    async def randomize_timezone(self, context: BrowserContext):
        """隨機化時區
        
        Args:
            context: 瀏覽器上下文
        """
        timezone = random.choice(self.fingerprint_config["timezones"])
        
        # 注意：Playwright在創建上下文時設置時區，這裡只是記錄
        self.logger.debug("使用時區", timezone=timezone)
    
    async def add_request_interceptor(self, page: Page):
        """添加請求攔截器
        
        Args:
            page: 頁面對象
        """
        async def handle_request(request):
            # 隨機延遲請求
            if random.random() < 0.1:  # 10%的請求添加延遲
                await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # 修改某些請求頭
            headers = request.headers
            if "referer" not in headers:
                headers["referer"] = "https://www.google.com/"
            
            await request.continue_(headers=headers)
        
        await page.route("**/*", handle_request)
    
    async def detect_bot_detection(self, page: Page) -> Dict[str, Any]:
        """檢測反爬蟲機制
        
        Args:
            page: 頁面對象
            
        Returns:
            Dict[str, Any]: 檢測結果
        """
        detection_result = {
            "captcha_detected": False,
            "rate_limit_detected": False,
            "access_denied": False,
            "suspicious_elements": []
        }
        
        try:
            # 檢測驗證碼
            captcha_selectors = [
                "[id*='captcha']",
                "[class*='captcha']",
                "[src*='captcha']",
                "iframe[src*='recaptcha']",
                ".g-recaptcha",
                "#cf-challenge-stage"
            ]
            
            for selector in captcha_selectors:
                element = await page.query_selector(selector)
                if element:
                    detection_result["captcha_detected"] = True
                    detection_result["suspicious_elements"].append(selector)
            
            # 檢測訪問被拒絕
            page_content = await page.content()
            access_denied_keywords = [
                "access denied",
                "403 forbidden",
                "rate limit",
                "too many requests",
                "blocked",
                "suspicious activity"
            ]
            
            for keyword in access_denied_keywords:
                if keyword.lower() in page_content.lower():
                    if "rate limit" in keyword or "too many requests" in keyword:
                        detection_result["rate_limit_detected"] = True
                    else:
                        detection_result["access_denied"] = True
            
            # 檢測頁面標題
            title = await page.title()
            if any(word in title.lower() for word in ["blocked", "denied", "error", "captcha"]):
                detection_result["access_denied"] = True
            
            # 記錄檢測結果
            if any(detection_result.values()):
                self.logger.warning("檢測到反爬蟲機制", detection_result=detection_result)
            
        except Exception as e:
            self.logger.error("反爬蟲檢測失敗", error=str(e))
        
        return detection_result
    
    async def handle_bot_detection(self, page: Page, detection_result: Dict[str, Any]) -> bool:
        """處理反爬蟲檢測
        
        Args:
            page: 頁面對象
            detection_result: 檢測結果
            
        Returns:
            bool: 是否成功處理
        """
        try:
            if detection_result["captcha_detected"]:
                self.logger.warning("檢測到驗證碼，嘗試刷新頁面")
                await page.reload(wait_until="networkidle")
                await asyncio.sleep(random.uniform(3, 6))
                return True
            
            if detection_result["rate_limit_detected"]:
                self.logger.warning("檢測到速率限制，等待後重試")
                wait_time = random.uniform(30, 60)
                await asyncio.sleep(wait_time)
                await page.reload(wait_until="networkidle")
                return True
            
            if detection_result["access_denied"]:
                self.logger.error("訪問被拒絕，需要更換策略")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("處理反爬蟲檢測失敗", error=str(e))
            return False
    
    def get_random_delay(self, min_delay: float = 1.0, max_delay: float = 5.0) -> float:
        """獲取隨機延遲時間
        
        Args:
            min_delay: 最小延遲時間（秒）
            max_delay: 最大延遲時間（秒）
            
        Returns:
            float: 隨機延遲時間
        """
        return random.uniform(min_delay, max_delay)
    
    def should_use_mobile_agent(self, platform: str) -> bool:
        """判斷是否應該使用移動端用戶代理
        
        Args:
            platform: 平台名稱
            
        Returns:
            bool: 是否使用移動端用戶代理
        """
        # 某些平台在移動端有更好的反檢測效果
        mobile_friendly_platforms = ["instagram", "tiktok", "twitter"]
        
        if platform.lower() in mobile_friendly_platforms:
            return random.random() < 0.3  # 30%概率使用移動端
        
        return random.random() < 0.1  # 10%概率使用移動端