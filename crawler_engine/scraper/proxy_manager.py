"""代理管理器

提供代理服務器的管理、輪換和健康檢查功能。
"""

import asyncio
import aiohttp
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ProxyConfig:
    """代理配置"""
    enabled: bool = False
    proxy_list: List[Dict[str, Any]] = field(default_factory=list)
    rotation_interval: int = 300  # 代理輪換間隔（秒）
    health_check_interval: int = 600  # 健康檢查間隔（秒）
    max_failures: int = 3  # 最大失敗次數
    timeout: int = 10  # 連接超時時間
    test_url: str = "https://httpbin.org/ip"  # 測試URL


@dataclass
class ProxyInfo:
    """代理信息"""
    host: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    provider: Optional[str] = None
    
    # 狀態信息
    is_active: bool = True
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    response_time: Optional[float] = None
    success_rate: float = 100.0
    total_requests: int = 0
    successful_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
            "username": self.username,
            "password": self.password,
            "country": self.country,
            "provider": self.provider
        }
    
    def get_url(self) -> str:
        """獲取代理URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"


class ProxyManager:
    """代理管理器
    
    提供代理服務器的管理、輪換、健康檢查和負載均衡功能。
    """
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.logger = logger.bind(component="proxy_manager")
        
        # 代理池
        self.proxies: List[ProxyInfo] = []
        self.active_proxies: List[ProxyInfo] = []
        
        # 當前代理索引
        self.current_proxy_index = 0
        
        # 健康檢查任務
        self._health_check_task: Optional[asyncio.Task] = None
        self._rotation_task: Optional[asyncio.Task] = None
        
        # 統計信息
        self._stats = {
            "total_proxies": 0,
            "active_proxies": 0,
            "failed_proxies": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0
        }
        
        # HTTP會話
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """初始化代理管理器"""
        if not self.config.enabled:
            self.logger.info("代理功能已禁用")
            return
        
        try:
            self.logger.info("正在初始化代理管理器...")
            
            # 創建HTTP會話
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # 加載代理列表
            await self._load_proxies()
            
            # 執行初始健康檢查
            await self._perform_health_check()
            
            # 啟動後台任務
            if self.active_proxies:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
                self._rotation_task = asyncio.create_task(self._rotation_loop())
            
            self.logger.info(
                "代理管理器初始化完成",
                total_proxies=len(self.proxies),
                active_proxies=len(self.active_proxies)
            )
            
        except Exception as e:
            self.logger.error("代理管理器初始化失敗", error=str(e))
            raise
    
    async def _load_proxies(self):
        """加載代理列表"""
        self.proxies = []
        
        for proxy_data in self.config.proxy_list:
            try:
                proxy = ProxyInfo(
                    host=proxy_data["host"],
                    port=proxy_data["port"],
                    protocol=proxy_data.get("protocol", "http"),
                    username=proxy_data.get("username"),
                    password=proxy_data.get("password"),
                    country=proxy_data.get("country"),
                    provider=proxy_data.get("provider")
                )
                self.proxies.append(proxy)
                
            except KeyError as e:
                self.logger.warning("代理配置缺少必要字段", missing_field=str(e), proxy_data=proxy_data)
            except Exception as e:
                self.logger.warning("加載代理失敗", error=str(e), proxy_data=proxy_data)
        
        self._stats["total_proxies"] = len(self.proxies)
        self.logger.info(f"加載了 {len(self.proxies)} 個代理")
    
    async def get_proxy(self) -> Optional[Dict[str, Any]]:
        """獲取可用的代理
        
        Returns:
            Optional[Dict[str, Any]]: 代理信息字典，如果沒有可用代理則返回None
        """
        if not self.config.enabled or not self.active_proxies:
            return None
        
        # 使用輪詢策略選擇代理
        proxy = self._select_proxy_round_robin()
        
        if proxy:
            # 更新使用統計
            proxy.last_used = datetime.now()
            proxy.total_requests += 1
            self._stats["total_requests"] += 1
            
            self.logger.debug(
                "選擇代理",
                host=proxy.host,
                port=proxy.port,
                country=proxy.country,
                success_rate=proxy.success_rate
            )
            
            return proxy.to_dict()
        
        return None
    
    def _select_proxy_round_robin(self) -> Optional[ProxyInfo]:
        """使用輪詢策略選擇代理"""
        if not self.active_proxies:
            return None
        
        # 輪詢選擇
        proxy = self.active_proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.active_proxies)
        
        return proxy
    
    def _select_proxy_weighted(self) -> Optional[ProxyInfo]:
        """使用加權策略選擇代理（基於成功率和響應時間）"""
        if not self.active_proxies:
            return None
        
        # 計算權重
        weights = []
        for proxy in self.active_proxies:
            # 基於成功率和響應時間的權重
            success_weight = proxy.success_rate / 100.0
            speed_weight = 1.0 / (proxy.response_time or 1.0)
            weight = success_weight * speed_weight
            weights.append(weight)
        
        # 加權隨機選擇
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(self.active_proxies)
        
        rand_val = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if rand_val <= cumulative_weight:
                return self.active_proxies[i]
        
        return self.active_proxies[-1]
    
    async def report_proxy_result(self, proxy_dict: Dict[str, Any], success: bool, 
                                response_time: Optional[float] = None):
        """報告代理使用結果
        
        Args:
            proxy_dict: 代理信息字典
            success: 是否成功
            response_time: 響應時間
        """
        # 查找對應的代理對象
        proxy = self._find_proxy(proxy_dict["host"], proxy_dict["port"])
        if not proxy:
            return
        
        # 更新統計信息
        if success:
            proxy.successful_requests += 1
            proxy.failure_count = 0  # 重置失敗計數
            self._stats["successful_requests"] += 1
        else:
            proxy.failure_count += 1
            self._stats["failed_requests"] += 1
        
        # 更新響應時間
        if response_time is not None:
            if proxy.response_time is None:
                proxy.response_time = response_time
            else:
                # 使用指數移動平均
                proxy.response_time = 0.7 * proxy.response_time + 0.3 * response_time
        
        # 更新成功率
        if proxy.total_requests > 0:
            proxy.success_rate = (proxy.successful_requests / proxy.total_requests) * 100
        
        # 檢查是否需要禁用代理
        if proxy.failure_count >= self.config.max_failures:
            await self._disable_proxy(proxy)
        
        self.logger.debug(
            "代理結果報告",
            host=proxy.host,
            port=proxy.port,
            success=success,
            failure_count=proxy.failure_count,
            success_rate=proxy.success_rate
        )
    
    def _find_proxy(self, host: str, port: int) -> Optional[ProxyInfo]:
        """查找代理對象"""
        for proxy in self.proxies:
            if proxy.host == host and proxy.port == port:
                return proxy
        return None
    
    async def _disable_proxy(self, proxy: ProxyInfo):
        """禁用代理"""
        proxy.is_active = False
        
        if proxy in self.active_proxies:
            self.active_proxies.remove(proxy)
            self._stats["active_proxies"] = len(self.active_proxies)
            self._stats["failed_proxies"] += 1
        
        self.logger.warning(
            "代理已禁用",
            host=proxy.host,
            port=proxy.port,
            failure_count=proxy.failure_count,
            success_rate=proxy.success_rate
        )
    
    async def _perform_health_check(self):
        """執行健康檢查"""
        if not self.proxies:
            return
        
        self.logger.info("開始代理健康檢查")
        
        # 並發檢查所有代理
        tasks = [self._check_proxy_health(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 更新活躍代理列表
        self.active_proxies = [proxy for proxy in self.proxies if proxy.is_active]
        self._stats["active_proxies"] = len(self.active_proxies)
        
        healthy_count = sum(1 for result in results if result is True)
        self.logger.info(
            "代理健康檢查完成",
            total_proxies=len(self.proxies),
            healthy_proxies=healthy_count,
            active_proxies=len(self.active_proxies)
        )
    
    async def _check_proxy_health(self, proxy: ProxyInfo) -> bool:
        """檢查單個代理的健康狀態
        
        Args:
            proxy: 代理信息
            
        Returns:
            bool: 是否健康
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # 構建代理配置
            proxy_url = proxy.get_url()
            
            # 發送測試請求
            async with self._session.get(
                self.config.test_url,
                proxy=proxy_url
            ) as response:
                if response.status == 200:
                    # 計算響應時間
                    response_time = asyncio.get_event_loop().time() - start_time
                    
                    # 更新代理狀態
                    proxy.is_active = True
                    proxy.last_checked = datetime.now()
                    proxy.response_time = response_time
                    proxy.failure_count = 0
                    
                    # 驗證返回的IP
                    try:
                        data = await response.json()
                        returned_ip = data.get("origin", "")
                        if returned_ip and returned_ip != proxy.host:
                            self.logger.debug(
                                "代理IP驗證",
                                proxy_host=proxy.host,
                                returned_ip=returned_ip
                            )
                    except:
                        pass
                    
                    return True
                else:
                    proxy.failure_count += 1
                    return False
        
        except Exception as e:
            proxy.failure_count += 1
            proxy.last_checked = datetime.now()
            
            self.logger.debug(
                "代理健康檢查失敗",
                host=proxy.host,
                port=proxy.port,
                error=str(e)
            )
            
            # 如果失敗次數過多，禁用代理
            if proxy.failure_count >= self.config.max_failures:
                proxy.is_active = False
            
            return False
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("健康檢查循環錯誤", error=str(e))
                await asyncio.sleep(60)  # 錯誤後等待1分鐘
    
    async def _rotation_loop(self):
        """代理輪換循環"""
        while True:
            try:
                await asyncio.sleep(self.config.rotation_interval)
                
                # 重新排序活躍代理（基於性能）
                self.active_proxies.sort(
                    key=lambda p: (p.success_rate, -p.response_time or 0),
                    reverse=True
                )
                
                self.logger.debug("代理列表已重新排序")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("代理輪換循環錯誤", error=str(e))
                await asyncio.sleep(60)
    
    async def add_proxy(self, host: str, port: int, protocol: str = "http",
                       username: Optional[str] = None, password: Optional[str] = None,
                       country: Optional[str] = None, provider: Optional[str] = None):
        """動態添加代理
        
        Args:
            host: 代理主機
            port: 代理端口
            protocol: 協議類型
            username: 用戶名
            password: 密碼
            country: 國家
            provider: 提供商
        """
        proxy = ProxyInfo(
            host=host,
            port=port,
            protocol=protocol,
            username=username,
            password=password,
            country=country,
            provider=provider
        )
        
        # 檢查代理健康狀態
        if await self._check_proxy_health(proxy):
            self.proxies.append(proxy)
            self.active_proxies.append(proxy)
            self._stats["total_proxies"] += 1
            self._stats["active_proxies"] += 1
            
            self.logger.info(
                "代理已添加",
                host=host,
                port=port,
                country=country
            )
        else:
            self.logger.warning(
                "代理添加失敗（健康檢查未通過）",
                host=host,
                port=port
            )
    
    async def remove_proxy(self, host: str, port: int):
        """移除代理
        
        Args:
            host: 代理主機
            port: 代理端口
        """
        proxy = self._find_proxy(host, port)
        if proxy:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                self._stats["total_proxies"] -= 1
            
            if proxy in self.active_proxies:
                self.active_proxies.remove(proxy)
                self._stats["active_proxies"] -= 1
            
            self.logger.info("代理已移除", host=host, port=port)
        else:
            self.logger.warning("要移除的代理不存在", host=host, port=port)
    
    def get_proxy_stats(self) -> Dict[str, Any]:
        """獲取代理統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        stats = self._stats.copy()
        
        # 計算成功率
        if stats["total_requests"] > 0:
            stats["overall_success_rate"] = (stats["successful_requests"] / stats["total_requests"]) * 100
        else:
            stats["overall_success_rate"] = 0.0
        
        # 添加代理詳細信息
        stats["proxy_details"] = []
        for proxy in self.proxies:
            stats["proxy_details"].append({
                "host": proxy.host,
                "port": proxy.port,
                "country": proxy.country,
                "provider": proxy.provider,
                "is_active": proxy.is_active,
                "success_rate": proxy.success_rate,
                "response_time": proxy.response_time,
                "total_requests": proxy.total_requests,
                "failure_count": proxy.failure_count,
                "last_used": proxy.last_used.isoformat() if proxy.last_used else None,
                "last_checked": proxy.last_checked.isoformat() if proxy.last_checked else None
            })
        
        return stats
    
    async def cleanup(self):
        """清理資源"""
        try:
            # 取消後台任務
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            if self._rotation_task:
                self._rotation_task.cancel()
                try:
                    await self._rotation_task
                except asyncio.CancelledError:
                    pass
            
            # 關閉HTTP會話
            if self._session:
                await self._session.close()
            
            self.logger.info("代理管理器已清理")
            
        except Exception as e:
            self.logger.error("代理管理器清理失敗", error=str(e))