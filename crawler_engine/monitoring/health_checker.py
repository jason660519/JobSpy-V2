"""健康檢查器

檢查系統各組件的健康狀態，包括數據庫連接、API服務、存儲等。
"""

import asyncio
import aiohttp
import sqlite3
import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)


class HealthStatus(Enum):
    """健康狀態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """組件類型"""
    DATABASE = "database"
    API_SERVICE = "api_service"
    STORAGE = "storage"
    CACHE = "cache"
    EXTERNAL_API = "external_api"
    QUEUE = "queue"
    CUSTOM = "custom"


@dataclass
class HealthCheck:
    """健康檢查配置"""
    name: str
    component_type: ComponentType
    check_function: Callable[[], Union[bool, Dict[str, Any]]]
    interval: int = 60  # 檢查間隔（秒）
    timeout: int = 30   # 超時時間（秒）
    retries: int = 3    # 重試次數
    enabled: bool = True
    critical: bool = False  # 是否為關鍵組件
    dependencies: List[str] = field(default_factory=list)  # 依賴的其他組件
    
    def __post_init__(self):
        if not callable(self.check_function):
            raise ValueError("check_function must be callable")


@dataclass
class ComponentHealth:
    """組件健康狀態"""
    name: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    response_time: float  # 響應時間（毫秒）
    last_check: datetime
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    uptime_percentage: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_healthy(self) -> bool:
        """是否健康"""
        return self.status == HealthStatus.HEALTHY
    
    @property
    def is_critical_failure(self) -> bool:
        """是否為關鍵故障"""
        return self.status == HealthStatus.UNHEALTHY and self.failure_count >= 3


@dataclass
class HealthReport:
    """健康報告"""
    timestamp: datetime
    overall_status: HealthStatus
    components: Dict[str, ComponentHealth]
    summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def healthy_components(self) -> List[ComponentHealth]:
        """健康組件列表"""
        return [comp for comp in self.components.values() if comp.is_healthy]
    
    @property
    def unhealthy_components(self) -> List[ComponentHealth]:
        """不健康組件列表"""
        return [comp for comp in self.components.values() if not comp.is_healthy]
    
    @property
    def critical_failures(self) -> List[ComponentHealth]:
        """關鍵故障列表"""
        return [comp for comp in self.components.values() if comp.is_critical_failure]


class BuiltinHealthChecks:
    """內建健康檢查"""
    
    @staticmethod
    def database_check(db_path: str) -> Dict[str, Any]:
        """數據庫健康檢查
        
        Args:
            db_path: 數據庫文件路徑
            
        Returns:
            Dict[str, Any]: 檢查結果
        """
        try:
            start_time = time.time()
            
            # 檢查文件是否存在
            if not Path(db_path).exists():
                return {
                    "success": False,
                    "message": "數據庫文件不存在",
                    "response_time": (time.time() - start_time) * 1000
                }
            
            # 嘗試連接數據庫
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            
            # 執行簡單查詢
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            # 檢查表是否存在
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = cursor.fetchall()
            
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "message": "數據庫連接正常",
                "response_time": response_time,
                "metadata": {
                    "tables_count": len(tables),
                    "file_size_mb": Path(db_path).stat().st_size / (1024 * 1024)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"數據庫連接失敗: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            }
    
    @staticmethod
    async def api_service_check(url: str, 
                               method: str = "GET",
                               headers: Optional[Dict[str, str]] = None,
                               timeout: int = 30) -> Dict[str, Any]:
        """API服務健康檢查
        
        Args:
            url: API端點URL
            method: HTTP方法
            headers: 請求頭
            timeout: 超時時間
            
        Returns:
            Dict[str, Any]: 檢查結果
        """
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.request(method, url, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    # 檢查狀態碼
                    if 200 <= response.status < 300:
                        return {
                            "success": True,
                            "message": f"API服務正常 (狀態碼: {response.status})",
                            "response_time": response_time,
                            "metadata": {
                                "status_code": response.status,
                                "content_type": response.headers.get("content-type", "unknown")
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"API服務異常 (狀態碼: {response.status})",
                            "response_time": response_time,
                            "metadata": {
                                "status_code": response.status
                            }
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "message": f"API服務超時 (>{timeout}秒)",
                "response_time": timeout * 1000
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"API服務檢查失敗: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            }
    
    @staticmethod
    def storage_check(storage_path: str, 
                     min_free_space_gb: float = 1.0) -> Dict[str, Any]:
        """存儲健康檢查
        
        Args:
            storage_path: 存儲路徑
            min_free_space_gb: 最小可用空間（GB）
            
        Returns:
            Dict[str, Any]: 檢查結果
        """
        try:
            start_time = time.time()
            
            path = Path(storage_path)
            
            # 檢查路徑是否存在
            if not path.exists():
                return {
                    "success": False,
                    "message": "存儲路徑不存在",
                    "response_time": (time.time() - start_time) * 1000
                }
            
            # 檢查是否可寫
            if not path.is_dir():
                path = path.parent
            
            # 獲取磁盤使用情況
            import shutil
            total, used, free = shutil.disk_usage(path)
            
            free_gb = free / (1024 ** 3)
            total_gb = total / (1024 ** 3)
            used_gb = used / (1024 ** 3)
            usage_percent = (used / total) * 100
            
            # 檢查可用空間
            if free_gb < min_free_space_gb:
                return {
                    "success": False,
                    "message": f"存儲空間不足: {free_gb:.2f}GB < {min_free_space_gb}GB",
                    "response_time": (time.time() - start_time) * 1000,
                    "metadata": {
                        "free_gb": free_gb,
                        "total_gb": total_gb,
                        "used_gb": used_gb,
                        "usage_percent": usage_percent
                    }
                }
            
            # 嘗試寫入測試文件
            test_file = path / ".health_check_test"
            try:
                test_file.write_text("health check test")
                test_file.unlink()  # 刪除測試文件
            except Exception as e:
                return {
                    "success": False,
                    "message": f"存儲寫入測試失敗: {str(e)}",
                    "response_time": (time.time() - start_time) * 1000
                }
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "message": "存儲正常",
                "response_time": response_time,
                "metadata": {
                    "free_gb": free_gb,
                    "total_gb": total_gb,
                    "used_gb": used_gb,
                    "usage_percent": usage_percent
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"存儲檢查失敗: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            }


class HealthChecker:
    """健康檢查器
    
    管理和執行系統組件的健康檢查。
    """
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.logger = logger.bind(component="HealthChecker")
        
        # 健康檢查配置
        self.health_checks: Dict[str, HealthCheck] = {}
        
        # 組件健康狀態
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # 健康報告歷史
        self.health_history: List[HealthReport] = []
        
        # 回調函數
        self.status_change_callbacks: List[Callable[[str, HealthStatus, HealthStatus], None]] = []
        
        # 運行狀態
        self._running = False
        self._check_task = None
    
    def add_health_check(self, health_check: HealthCheck) -> None:
        """添加健康檢查
        
        Args:
            health_check: 健康檢查配置
        """
        self.health_checks[health_check.name] = health_check
        
        # 初始化組件健康狀態
        self.component_health[health_check.name] = ComponentHealth(
            name=health_check.name,
            component_type=health_check.component_type,
            status=HealthStatus.UNKNOWN,
            message="尚未檢查",
            response_time=0.0,
            last_check=datetime.utcnow()
        )
        
        self.logger.info(
            "添加健康檢查",
            name=health_check.name,
            component_type=health_check.component_type.value,
            interval=health_check.interval,
            critical=health_check.critical
        )
    
    def remove_health_check(self, name: str) -> None:
        """移除健康檢查
        
        Args:
            name: 檢查名稱
        """
        if name in self.health_checks:
            del self.health_checks[name]
        
        if name in self.component_health:
            del self.component_health[name]
        
        self.logger.info("移除健康檢查", name=name)
    
    def add_status_change_callback(self, 
                                  callback: Callable[[str, HealthStatus, HealthStatus], None]) -> None:
        """添加狀態變更回調
        
        Args:
            callback: 回調函數 (component_name, old_status, new_status)
        """
        self.status_change_callbacks.append(callback)
    
    async def check_component(self, name: str) -> ComponentHealth:
        """檢查單個組件
        
        Args:
            name: 組件名稱
            
        Returns:
            ComponentHealth: 組件健康狀態
        """
        if name not in self.health_checks:
            raise ValueError(f"健康檢查 '{name}' 不存在")
        
        health_check = self.health_checks[name]
        
        if not health_check.enabled:
            return self.component_health[name]
        
        start_time = time.time()
        old_status = self.component_health[name].status
        
        try:
            # 執行健康檢查（帶重試）
            for attempt in range(health_check.retries + 1):
                try:
                    # 執行檢查函數
                    if asyncio.iscoroutinefunction(health_check.check_function):
                        result = await asyncio.wait_for(
                            health_check.check_function(),
                            timeout=health_check.timeout
                        )
                    else:
                        result = await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(
                                None, health_check.check_function
                            ),
                            timeout=health_check.timeout
                        )
                    
                    # 處理結果
                    if isinstance(result, bool):
                        success = result
                        message = "檢查通過" if success else "檢查失敗"
                        metadata = {}
                        response_time = (time.time() - start_time) * 1000
                    elif isinstance(result, dict):
                        success = result.get("success", False)
                        message = result.get("message", "無消息")
                        metadata = result.get("metadata", {})
                        response_time = result.get("response_time", (time.time() - start_time) * 1000)
                    else:
                        success = False
                        message = f"無效的檢查結果類型: {type(result)}"
                        metadata = {}
                        response_time = (time.time() - start_time) * 1000
                    
                    if success:
                        break  # 成功則退出重試循環
                    
                    if attempt < health_check.retries:
                        await asyncio.sleep(1)  # 重試前等待1秒
                        
                except asyncio.TimeoutError:
                    if attempt == health_check.retries:
                        success = False
                        message = f"檢查超時 (>{health_check.timeout}秒)"
                        metadata = {}
                        response_time = health_check.timeout * 1000
                    else:
                        await asyncio.sleep(1)
                        continue
                except Exception as e:
                    if attempt == health_check.retries:
                        success = False
                        message = f"檢查異常: {str(e)}"
                        metadata = {}
                        response_time = (time.time() - start_time) * 1000
                    else:
                        await asyncio.sleep(1)
                        continue
            
            # 更新組件健康狀態
            now = datetime.utcnow()
            component_health = self.component_health[name]
            
            if success:
                component_health.status = HealthStatus.HEALTHY
                component_health.last_success = now
                component_health.success_count += 1
                component_health.failure_count = 0  # 重置失敗計數
            else:
                component_health.failure_count += 1
                component_health.last_failure = now
                
                # 根據失敗次數確定狀態
                if component_health.failure_count >= 3:
                    component_health.status = HealthStatus.UNHEALTHY
                else:
                    component_health.status = HealthStatus.DEGRADED
            
            component_health.message = message
            component_health.response_time = response_time
            component_health.last_check = now
            component_health.metadata = metadata
            
            # 計算正常運行時間百分比
            total_checks = component_health.success_count + component_health.failure_count
            if total_checks > 0:
                component_health.uptime_percentage = (component_health.success_count / total_checks) * 100
            
            # 觸發狀態變更回調
            if old_status != component_health.status:
                for callback in self.status_change_callbacks:
                    try:
                        callback(name, old_status, component_health.status)
                    except Exception as e:
                        self.logger.error(
                            "狀態變更回調執行失敗",
                            callback=callback.__name__,
                            error=str(e)
                        )
            
            return component_health
            
        except Exception as e:
            self.logger.error(
                "組件健康檢查失敗",
                component=name,
                error=str(e)
            )
            
            # 設置為未知狀態
            component_health = self.component_health[name]
            component_health.status = HealthStatus.UNKNOWN
            component_health.message = f"檢查異常: {str(e)}"
            component_health.response_time = (time.time() - start_time) * 1000
            component_health.last_check = datetime.utcnow()
            
            return component_health
    
    async def check_all_components(self) -> HealthReport:
        """檢查所有組件
        
        Returns:
            HealthReport: 健康報告
        """
        # 並行檢查所有組件
        tasks = []
        for name in self.health_checks.keys():
            task = asyncio.create_task(self.check_component(name))
            tasks.append((name, task))
        
        # 等待所有檢查完成
        results = {}
        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                self.logger.error(
                    "組件檢查任務失敗",
                    component=name,
                    error=str(e)
                )
                # 使用當前狀態作為結果
                results[name] = self.component_health[name]
        
        # 計算整體狀態
        overall_status = self._calculate_overall_status(results)
        
        # 生成摘要
        summary = self._generate_summary(results)
        
        # 創建健康報告
        report = HealthReport(
            timestamp=datetime.utcnow(),
            overall_status=overall_status,
            components=results,
            summary=summary
        )
        
        # 保存到歷史記錄
        self.health_history.append(report)
        
        # 限制歷史記錄數量
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        return report
    
    def _calculate_overall_status(self, 
                                 components: Dict[str, ComponentHealth]) -> HealthStatus:
        """計算整體健康狀態
        
        Args:
            components: 組件健康狀態字典
            
        Returns:
            HealthStatus: 整體健康狀態
        """
        if not components:
            return HealthStatus.UNKNOWN
        
        # 檢查關鍵組件
        critical_components = [
            comp for name, comp in components.items()
            if self.health_checks.get(name, HealthCheck("", ComponentType.CUSTOM, lambda: True)).critical
        ]
        
        # 如果有關鍵組件不健康，整體狀態為不健康
        for comp in critical_components:
            if comp.status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY
        
        # 統計各狀態的組件數量
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0
        }
        
        for comp in components.values():
            status_counts[comp.status] += 1
        
        total_components = len(components)
        
        # 如果超過50%的組件不健康
        if status_counts[HealthStatus.UNHEALTHY] > total_components * 0.5:
            return HealthStatus.UNHEALTHY
        
        # 如果有不健康的組件或超過30%的組件降級
        if (status_counts[HealthStatus.UNHEALTHY] > 0 or 
            status_counts[HealthStatus.DEGRADED] > total_components * 0.3):
            return HealthStatus.DEGRADED
        
        # 如果所有組件都健康
        if status_counts[HealthStatus.HEALTHY] == total_components:
            return HealthStatus.HEALTHY
        
        # 其他情況為降級
        return HealthStatus.DEGRADED
    
    def _generate_summary(self, 
                         components: Dict[str, ComponentHealth]) -> Dict[str, Any]:
        """生成健康摘要
        
        Args:
            components: 組件健康狀態字典
            
        Returns:
            Dict[str, Any]: 健康摘要
        """
        if not components:
            return {}
        
        # 統計各狀態的組件數量
        status_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unknown": 0
        }
        
        total_response_time = 0
        total_uptime = 0
        
        for comp in components.values():
            if comp.status == HealthStatus.HEALTHY:
                status_counts["healthy"] += 1
            elif comp.status == HealthStatus.DEGRADED:
                status_counts["degraded"] += 1
            elif comp.status == HealthStatus.UNHEALTHY:
                status_counts["unhealthy"] += 1
            else:
                status_counts["unknown"] += 1
            
            total_response_time += comp.response_time
            total_uptime += comp.uptime_percentage
        
        total_components = len(components)
        avg_response_time = total_response_time / total_components if total_components > 0 else 0
        avg_uptime = total_uptime / total_components if total_components > 0 else 0
        
        return {
            "total_components": total_components,
            "status_counts": status_counts,
            "health_percentage": (status_counts["healthy"] / total_components * 100) if total_components > 0 else 0,
            "average_response_time": avg_response_time,
            "average_uptime": avg_uptime,
            "critical_failures": [
                comp.name for comp in components.values()
                if comp.is_critical_failure
            ]
        }
    
    async def start(self) -> None:
        """啟動健康檢查器"""
        self._running = True
        self._check_task = asyncio.create_task(self._check_loop())
        
        self.logger.info(
            "健康檢查器已啟動",
            check_interval=self.check_interval,
            components_count=len(self.health_checks)
        )
    
    async def stop(self) -> None:
        """停止健康檢查器"""
        self._running = False
        
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("健康檢查器已停止")
    
    async def _check_loop(self) -> None:
        """檢查循環"""
        while self._running:
            try:
                # 執行健康檢查
                report = await self.check_all_components()
                
                # 記錄整體狀態
                self.logger.info(
                    "健康檢查完成",
                    overall_status=report.overall_status.value,
                    healthy_count=len(report.healthy_components),
                    unhealthy_count=len(report.unhealthy_components),
                    critical_failures=len(report.critical_failures)
                )
                
                # 如果有關鍵故障，記錄詳細信息
                if report.critical_failures:
                    for comp in report.critical_failures:
                        self.logger.error(
                            "關鍵組件故障",
                            component=comp.name,
                            message=comp.message,
                            failure_count=comp.failure_count
                        )
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("健康檢查循環錯誤", error=str(e))
                await asyncio.sleep(self.check_interval)
    
    def get_current_status(self) -> HealthReport:
        """獲取當前健康狀態
        
        Returns:
            HealthReport: 當前健康報告
        """
        if self.health_history:
            return self.health_history[-1]
        
        # 如果沒有歷史記錄，創建一個基於當前狀態的報告
        overall_status = self._calculate_overall_status(self.component_health)
        summary = self._generate_summary(self.component_health)
        
        return HealthReport(
            timestamp=datetime.utcnow(),
            overall_status=overall_status,
            components=self.component_health.copy(),
            summary=summary
        )
    
    def get_component_status(self, name: str) -> Optional[ComponentHealth]:
        """獲取組件狀態
        
        Args:
            name: 組件名稱
            
        Returns:
            Optional[ComponentHealth]: 組件健康狀態
        """
        return self.component_health.get(name)
    
    def get_health_history(self, hours: int = 24) -> List[HealthReport]:
        """獲取健康歷史
        
        Args:
            hours: 時間範圍（小時）
            
        Returns:
            List[HealthReport]: 健康報告列表
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            report for report in self.health_history
            if report.timestamp >= cutoff_time
        ]
    
    def setup_default_checks(self, 
                           db_path: Optional[str] = None,
                           storage_path: Optional[str] = None,
                           api_endpoints: Optional[List[str]] = None) -> None:
        """設置默認健康檢查
        
        Args:
            db_path: 數據庫路徑
            storage_path: 存儲路徑
            api_endpoints: API端點列表
        """
        # 數據庫檢查
        if db_path:
            self.add_health_check(HealthCheck(
                name="database",
                component_type=ComponentType.DATABASE,
                check_function=lambda: BuiltinHealthChecks.database_check(db_path),
                interval=60,
                timeout=10,
                critical=True
            ))
        
        # 存儲檢查
        if storage_path:
            self.add_health_check(HealthCheck(
                name="storage",
                component_type=ComponentType.STORAGE,
                check_function=lambda: BuiltinHealthChecks.storage_check(storage_path),
                interval=120,
                timeout=15,
                critical=True
            ))
        
        # API端點檢查
        if api_endpoints:
            for i, endpoint in enumerate(api_endpoints):
                self.add_health_check(HealthCheck(
                    name=f"api_endpoint_{i}",
                    component_type=ComponentType.API_SERVICE,
                    check_function=lambda url=endpoint: BuiltinHealthChecks.api_service_check(url),
                    interval=60,
                    timeout=30,
                    critical=False
                ))
        
        self.logger.info(
            "設置默認健康檢查完成",
            database=db_path is not None,
            storage=storage_path is not None,
            api_endpoints=len(api_endpoints) if api_endpoints else 0
        )