"""成本控制器

監控和控制系統資源使用成本，包括API調用、存儲、帶寬等。
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import structlog
from collections import defaultdict, deque

logger = structlog.get_logger(__name__)


class ResourceType(Enum):
    """資源類型"""
    API_CALLS = "api_calls"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    COMPUTE = "compute"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    GPU = "gpu"


class TimeWindow(Enum):
    """時間窗口"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class AlertLevel(Enum):
    """告警級別"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CostLimit:
    """成本限制"""
    resource_type: ResourceType
    limit: float
    time_window: TimeWindow
    soft_limit: Optional[float] = None  # 軟限制（警告閾值）
    enabled: bool = True
    description: str = ""
    
    def __post_init__(self):
        if self.soft_limit is None:
            self.soft_limit = self.limit * 0.8  # 默認80%為軟限制


@dataclass
class CostAlert:
    """成本告警"""
    resource_type: ResourceType
    level: AlertLevel
    message: str
    current_usage: float
    limit: float
    time_window: TimeWindow
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False


@dataclass
class CostMetrics:
    """成本指標"""
    resource_type: ResourceType
    current_usage: float
    limit: float
    soft_limit: float
    time_window: TimeWindow
    usage_percentage: float
    remaining: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_over_soft_limit(self) -> bool:
        """是否超過軟限制"""
        return self.current_usage >= self.soft_limit
    
    @property
    def is_over_hard_limit(self) -> bool:
        """是否超過硬限制"""
        return self.current_usage >= self.limit


@dataclass
class CostConfig:
    """成本控制配置"""
    limits: List[CostLimit] = field(default_factory=list)
    check_interval: int = 60  # 檢查間隔（秒）
    alert_cooldown: int = 300  # 告警冷卻時間（秒）
    enable_auto_throttling: bool = True  # 啟用自動限流
    enable_alerts: bool = True  # 啟用告警
    metrics_retention_hours: int = 24  # 指標保留時間
    
    # API成本配置
    api_cost_per_call: Dict[str, float] = field(default_factory=dict)
    
    # 存儲成本配置
    storage_cost_per_mb: float = 0.001
    
    # 帶寬成本配置
    bandwidth_cost_per_mb: float = 0.01
    
    # 計算成本配置
    compute_cost_per_minute: float = 0.1


class CostTracker:
    """成本追蹤器"""
    
    def __init__(self, resource_type: ResourceType, time_window: TimeWindow):
        self.resource_type = resource_type
        self.time_window = time_window
        self.usage_history: deque = deque(maxlen=1000)
        self.current_usage = 0.0
        self.last_reset = datetime.utcnow()
    
    def add_usage(self, amount: float) -> None:
        """添加使用量"""
        now = datetime.utcnow()
        
        # 檢查是否需要重置
        if self._should_reset(now):
            self._reset_usage(now)
        
        self.current_usage += amount
        self.usage_history.append({
            "timestamp": now,
            "amount": amount,
            "total": self.current_usage
        })
    
    def get_current_usage(self) -> float:
        """獲取當前使用量"""
        now = datetime.utcnow()
        
        if self._should_reset(now):
            self._reset_usage(now)
        
        return self.current_usage
    
    def _should_reset(self, now: datetime) -> bool:
        """檢查是否應該重置"""
        if self.time_window == TimeWindow.MINUTE:
            return (now - self.last_reset).total_seconds() >= 60
        elif self.time_window == TimeWindow.HOUR:
            return (now - self.last_reset).total_seconds() >= 3600
        elif self.time_window == TimeWindow.DAY:
            return (now - self.last_reset).total_seconds() >= 86400
        elif self.time_window == TimeWindow.WEEK:
            return (now - self.last_reset).total_seconds() >= 604800
        elif self.time_window == TimeWindow.MONTH:
            return (now - self.last_reset).total_seconds() >= 2592000
        return False
    
    def _reset_usage(self, now: datetime) -> None:
        """重置使用量"""
        self.current_usage = 0.0
        self.last_reset = now
    
    def get_usage_history(self, hours: int = 1) -> List[Dict]:
        """獲取使用歷史"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            entry for entry in self.usage_history
            if entry["timestamp"] >= cutoff_time
        ]


class CostController:
    """成本控制器
    
    監控和控制系統資源使用成本。
    """
    
    def __init__(self, config: CostConfig):
        self.config = config
        self.logger = logger.bind(component="CostController")
        
        # 成本限制映射
        self.limits: Dict[str, CostLimit] = {}
        for limit in config.limits:
            key = f"{limit.resource_type.value}_{limit.time_window.value}"
            self.limits[key] = limit
        
        # 成本追蹤器
        self.trackers: Dict[str, CostTracker] = {}
        for limit in config.limits:
            key = f"{limit.resource_type.value}_{limit.time_window.value}"
            self.trackers[key] = CostTracker(limit.resource_type, limit.time_window)
        
        # 告警歷史
        self.alert_history: List[CostAlert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # 回調函數
        self.alert_callbacks: List[Callable[[CostAlert], None]] = []
        self.throttle_callbacks: List[Callable[[ResourceType, float], None]] = []
        
        # 運行狀態
        self._running = False
        self._monitor_task = None
    
    async def start(self) -> None:
        """啟動成本控制器"""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        
        self.logger.info(
            "成本控制器已啟動",
            limits_count=len(self.limits),
            check_interval=self.config.check_interval
        )
    
    async def stop(self) -> None:
        """停止成本控制器"""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("成本控制器已停止")
    
    def add_usage(self, 
                  resource_type: ResourceType, 
                  amount: float, 
                  time_window: TimeWindow = TimeWindow.HOUR) -> bool:
        """添加資源使用量
        
        Args:
            resource_type: 資源類型
            amount: 使用量
            time_window: 時間窗口
            
        Returns:
            bool: 是否允許使用（未超過限制）
        """
        key = f"{resource_type.value}_{time_window.value}"
        
        # 檢查是否有對應的追蹤器
        if key not in self.trackers:
            self.logger.warning(
                "未找到對應的成本追蹤器",
                resource_type=resource_type.value,
                time_window=time_window.value
            )
            return True
        
        # 添加使用量
        tracker = self.trackers[key]
        tracker.add_usage(amount)
        
        # 檢查限制
        if key in self.limits:
            limit = self.limits[key]
            current_usage = tracker.get_current_usage()
            
            # 檢查硬限制
            if current_usage >= limit.limit:
                self._trigger_alert(
                    resource_type,
                    AlertLevel.CRITICAL,
                    f"資源使用量超過硬限制: {current_usage:.2f}/{limit.limit:.2f}",
                    current_usage,
                    limit.limit,
                    time_window
                )
                
                # 觸發限流
                if self.config.enable_auto_throttling:
                    self._trigger_throttle(resource_type, current_usage)
                
                return False
            
            # 檢查軟限制
            elif current_usage >= limit.soft_limit:
                self._trigger_alert(
                    resource_type,
                    AlertLevel.WARNING,
                    f"資源使用量超過軟限制: {current_usage:.2f}/{limit.soft_limit:.2f}",
                    current_usage,
                    limit.soft_limit,
                    time_window
                )
        
        return True
    
    def get_metrics(self, 
                   resource_type: Optional[ResourceType] = None) -> List[CostMetrics]:
        """獲取成本指標
        
        Args:
            resource_type: 資源類型（可選，為None時返回所有）
            
        Returns:
            List[CostMetrics]: 成本指標列表
        """
        metrics = []
        
        for key, tracker in self.trackers.items():
            if resource_type and tracker.resource_type != resource_type:
                continue
            
            if key in self.limits:
                limit = self.limits[key]
                current_usage = tracker.get_current_usage()
                
                usage_percentage = (current_usage / limit.limit * 100) if limit.limit > 0 else 0
                remaining = max(0, limit.limit - current_usage)
                
                metric = CostMetrics(
                    resource_type=tracker.resource_type,
                    current_usage=current_usage,
                    limit=limit.limit,
                    soft_limit=limit.soft_limit,
                    time_window=tracker.time_window,
                    usage_percentage=usage_percentage,
                    remaining=remaining
                )
                
                metrics.append(metric)
        
        return metrics
    
    def get_alerts(self, 
                  resolved: Optional[bool] = None,
                  hours: int = 24) -> List[CostAlert]:
        """獲取告警列表
        
        Args:
            resolved: 是否已解決（None為全部）
            hours: 時間範圍（小時）
            
        Returns:
            List[CostAlert]: 告警列表
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def add_alert_callback(self, callback: Callable[[CostAlert], None]) -> None:
        """添加告警回調
        
        Args:
            callback: 告警回調函數
        """
        self.alert_callbacks.append(callback)
    
    def add_throttle_callback(self, callback: Callable[[ResourceType, float], None]) -> None:
        """添加限流回調
        
        Args:
            callback: 限流回調函數
        """
        self.throttle_callbacks.append(callback)
    
    def update_limit(self, 
                    resource_type: ResourceType, 
                    time_window: TimeWindow,
                    new_limit: float,
                    new_soft_limit: Optional[float] = None) -> bool:
        """更新成本限制
        
        Args:
            resource_type: 資源類型
            time_window: 時間窗口
            new_limit: 新的硬限制
            new_soft_limit: 新的軟限制
            
        Returns:
            bool: 是否成功更新
        """
        key = f"{resource_type.value}_{time_window.value}"
        
        if key in self.limits:
            limit = self.limits[key]
            limit.limit = new_limit
            if new_soft_limit is not None:
                limit.soft_limit = new_soft_limit
            else:
                limit.soft_limit = new_limit * 0.8
            
            self.logger.info(
                "更新成本限制",
                resource_type=resource_type.value,
                time_window=time_window.value,
                new_limit=new_limit,
                new_soft_limit=limit.soft_limit
            )
            
            return True
        
        return False
    
    def reset_usage(self, 
                   resource_type: ResourceType, 
                   time_window: TimeWindow) -> bool:
        """重置資源使用量
        
        Args:
            resource_type: 資源類型
            time_window: 時間窗口
            
        Returns:
            bool: 是否成功重置
        """
        key = f"{resource_type.value}_{time_window.value}"
        
        if key in self.trackers:
            tracker = self.trackers[key]
            tracker._reset_usage(datetime.utcnow())
            
            self.logger.info(
                "重置資源使用量",
                resource_type=resource_type.value,
                time_window=time_window.value
            )
            
            return True
        
        return False
    
    def _trigger_alert(self, 
                      resource_type: ResourceType,
                      level: AlertLevel,
                      message: str,
                      current_usage: float,
                      limit: float,
                      time_window: TimeWindow) -> None:
        """觸發告警"""
        if not self.config.enable_alerts:
            return
        
        # 檢查告警冷卻
        alert_key = f"{resource_type.value}_{level.value}"
        now = datetime.utcnow()
        
        if alert_key in self.last_alert_time:
            last_time = self.last_alert_time[alert_key]
            if (now - last_time).total_seconds() < self.config.alert_cooldown:
                return
        
        # 創建告警
        alert = CostAlert(
            resource_type=resource_type,
            level=level,
            message=message,
            current_usage=current_usage,
            limit=limit,
            time_window=time_window,
            timestamp=now
        )
        
        self.alert_history.append(alert)
        self.last_alert_time[alert_key] = now
        
        # 觸發回調
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(
                    "告警回調執行失敗",
                    callback=callback.__name__,
                    error=str(e)
                )
        
        self.logger.warning(
            "觸發成本告警",
            resource_type=resource_type.value,
            level=level.value,
            message=message,
            current_usage=current_usage,
            limit=limit
        )
    
    def _trigger_throttle(self, resource_type: ResourceType, current_usage: float) -> None:
        """觸發限流"""
        for callback in self.throttle_callbacks:
            try:
                callback(resource_type, current_usage)
            except Exception as e:
                self.logger.error(
                    "限流回調執行失敗",
                    callback=callback.__name__,
                    error=str(e)
                )
        
        self.logger.warning(
            "觸發資源限流",
            resource_type=resource_type.value,
            current_usage=current_usage
        )
    
    async def _monitor_loop(self) -> None:
        """監控循環"""
        while self._running:
            try:
                await asyncio.sleep(self.config.check_interval)
                
                # 檢查所有指標
                metrics = self.get_metrics()
                
                for metric in metrics:
                    # 檢查是否需要清理舊告警
                    self._cleanup_old_alerts()
                    
                    # 記錄指標
                    if metric.usage_percentage > 50:  # 只記錄使用率超過50%的指標
                        self.logger.debug(
                            "成本指標",
                            resource_type=metric.resource_type.value,
                            usage_percentage=metric.usage_percentage,
                            current_usage=metric.current_usage,
                            limit=metric.limit
                        )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("監控循環錯誤", error=str(e))
    
    def _cleanup_old_alerts(self) -> None:
        """清理舊告警"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.config.metrics_retention_hours)
        
        original_count = len(self.alert_history)
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        cleaned_count = original_count - len(self.alert_history)
        if cleaned_count > 0:
            self.logger.debug("清理舊告警", count=cleaned_count)
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """獲取成本摘要"""
        metrics = self.get_metrics()
        alerts = self.get_alerts(resolved=False, hours=24)
        
        summary = {
            "total_resources": len(metrics),
            "resources_over_soft_limit": len([m for m in metrics if m.is_over_soft_limit]),
            "resources_over_hard_limit": len([m for m in metrics if m.is_over_hard_limit]),
            "active_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.level == AlertLevel.CRITICAL]),
            "warning_alerts": len([a for a in alerts if a.level == AlertLevel.WARNING]),
            "metrics": [
                {
                    "resource_type": m.resource_type.value,
                    "time_window": m.time_window.value,
                    "usage_percentage": m.usage_percentage,
                    "current_usage": m.current_usage,
                    "limit": m.limit,
                    "remaining": m.remaining
                }
                for m in metrics
            ]
        }
        
        return summary