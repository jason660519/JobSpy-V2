"""性能監控器

監控系統性能指標，包括CPU、內存、磁盤、網絡等資源使用情況。
"""

import asyncio
import psutil
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import structlog
from collections import deque

logger = structlog.get_logger(__name__)


class MetricType(Enum):
    """指標類型"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    DISK_IO = "disk_io"
    PROCESS_COUNT = "process_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    QUEUE_SIZE = "queue_size"


class AlertLevel(Enum):
    """告警級別"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemMetrics:
    """系統指標"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    disk_read_bytes: int
    disk_write_bytes: int
    process_count: int
    load_average: Optional[List[float]] = None  # Linux/Mac only


@dataclass
class ResourceUsage:
    """資源使用情況"""
    metric_type: MetricType
    value: float
    unit: str
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_over_threshold(self) -> bool:
        """是否超過閾值"""
        return self.threshold is not None and self.value >= self.threshold


@dataclass
class PerformanceAlert:
    """性能告警"""
    metric_type: MetricType
    level: AlertLevel
    message: str
    current_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    duration: Optional[float] = None  # 持續時間（秒）


@dataclass
class PerformanceMetrics:
    """性能指標"""
    system_metrics: SystemMetrics
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    alerts: List[PerformanceAlert] = field(default_factory=list)
    
    def add_custom_metric(self, name: str, value: float) -> None:
        """添加自定義指標"""
        self.custom_metrics[name] = value
    
    def get_metric_value(self, metric_type: MetricType) -> Optional[float]:
        """獲取指標值"""
        if metric_type == MetricType.CPU_USAGE:
            return self.system_metrics.cpu_percent
        elif metric_type == MetricType.MEMORY_USAGE:
            return self.system_metrics.memory_percent
        elif metric_type == MetricType.DISK_USAGE:
            return self.system_metrics.disk_usage_percent
        elif metric_type == MetricType.PROCESS_COUNT:
            return self.system_metrics.process_count
        else:
            return self.custom_metrics.get(metric_type.value)


class PerformanceThreshold:
    """性能閾值"""
    
    def __init__(self, 
                 metric_type: MetricType,
                 warning_threshold: float,
                 critical_threshold: float,
                 enabled: bool = True):
        self.metric_type = metric_type
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.enabled = enabled
    
    def check_threshold(self, value: float) -> Optional[AlertLevel]:
        """檢查閾值"""
        if not self.enabled:
            return None
        
        if value >= self.critical_threshold:
            return AlertLevel.CRITICAL
        elif value >= self.warning_threshold:
            return AlertLevel.WARNING
        
        return None


class MetricsCollector:
    """指標收集器"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.custom_collectors: Dict[str, Callable[[], float]] = {}
        self.logger = logger.bind(component="MetricsCollector")
    
    def add_custom_collector(self, name: str, collector: Callable[[], float]) -> None:
        """添加自定義指標收集器
        
        Args:
            name: 指標名稱
            collector: 收集器函數，返回指標值
        """
        self.custom_collectors[name] = collector
        self.logger.info("添加自定義指標收集器", name=name)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系統指標"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 內存使用情況
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            
            # 磁盤使用情況
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            # 網絡IO
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # 磁盤IO
            disk_io = psutil.disk_io_counters()
            disk_read_bytes = disk_io.read_bytes if disk_io else 0
            disk_write_bytes = disk_io.write_bytes if disk_io else 0
            
            # 進程數量
            process_count = len(psutil.pids())
            
            # 負載平均值（Linux/Mac）
            load_average = None
            try:
                load_average = list(psutil.getloadavg())
            except (AttributeError, OSError):
                pass  # Windows不支持
            
            metrics = SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                disk_read_bytes=disk_read_bytes,
                disk_write_bytes=disk_write_bytes,
                process_count=process_count,
                load_average=load_average
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error("收集系統指標失敗", error=str(e))
            # 返回默認值
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                disk_read_bytes=0,
                disk_write_bytes=0,
                process_count=0
            )
    
    def collect_custom_metrics(self) -> Dict[str, float]:
        """收集自定義指標"""
        custom_metrics = {}
        
        for name, collector in self.custom_collectors.items():
            try:
                value = collector()
                custom_metrics[name] = value
            except Exception as e:
                self.logger.error(
                    "收集自定義指標失敗",
                    name=name,
                    error=str(e)
                )
                custom_metrics[name] = 0.0
        
        return custom_metrics
    
    def collect_all_metrics(self) -> PerformanceMetrics:
        """收集所有指標"""
        system_metrics = self.collect_system_metrics()
        custom_metrics = self.collect_custom_metrics()
        
        performance_metrics = PerformanceMetrics(
            system_metrics=system_metrics,
            custom_metrics=custom_metrics
        )
        
        # 保存到歷史記錄
        self.metrics_history.append(performance_metrics)
        
        return performance_metrics
    
    def get_metrics_history(self, hours: int = 1) -> List[PerformanceMetrics]:
        """獲取指標歷史
        
        Args:
            hours: 時間範圍（小時）
            
        Returns:
            List[PerformanceMetrics]: 指標歷史列表
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self.metrics_history
            if metrics.system_metrics.timestamp >= cutoff_time
        ]
    
    def get_average_metrics(self, hours: int = 1) -> Dict[str, float]:
        """獲取平均指標
        
        Args:
            hours: 時間範圍（小時）
            
        Returns:
            Dict[str, float]: 平均指標字典
        """
        history = self.get_metrics_history(hours)
        
        if not history:
            return {}
        
        # 計算系統指標平均值
        avg_metrics = {
            "cpu_percent": sum(m.system_metrics.cpu_percent for m in history) / len(history),
            "memory_percent": sum(m.system_metrics.memory_percent for m in history) / len(history),
            "disk_usage_percent": sum(m.system_metrics.disk_usage_percent for m in history) / len(history),
            "process_count": sum(m.system_metrics.process_count for m in history) / len(history)
        }
        
        # 計算自定義指標平均值
        if history[0].custom_metrics:
            for metric_name in history[0].custom_metrics.keys():
                values = [m.custom_metrics.get(metric_name, 0) for m in history]
                avg_metrics[f"custom_{metric_name}"] = sum(values) / len(values)
        
        return avg_metrics


class PerformanceMonitor:
    """性能監控器
    
    監控系統性能並觸發告警。
    """
    
    def __init__(self, 
                 collection_interval: int = 30,
                 alert_cooldown: int = 300):
        self.collection_interval = collection_interval
        self.alert_cooldown = alert_cooldown
        self.logger = logger.bind(component="PerformanceMonitor")
        
        # 指標收集器
        self.collector = MetricsCollector()
        
        # 性能閾值
        self.thresholds: Dict[MetricType, PerformanceThreshold] = {}
        
        # 告警歷史
        self.alert_history: List[PerformanceAlert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # 回調函數
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # 運行狀態
        self._running = False
        self._monitor_task = None
        
        # 設置默認閾值
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self) -> None:
        """設置默認閾值"""
        self.thresholds = {
            MetricType.CPU_USAGE: PerformanceThreshold(
                MetricType.CPU_USAGE, 70.0, 90.0
            ),
            MetricType.MEMORY_USAGE: PerformanceThreshold(
                MetricType.MEMORY_USAGE, 80.0, 95.0
            ),
            MetricType.DISK_USAGE: PerformanceThreshold(
                MetricType.DISK_USAGE, 85.0, 95.0
            )
        }
    
    async def start(self) -> None:
        """啟動性能監控器"""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        
        self.logger.info(
            "性能監控器已啟動",
            collection_interval=self.collection_interval,
            thresholds_count=len(self.thresholds)
        )
    
    async def stop(self) -> None:
        """停止性能監控器"""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("性能監控器已停止")
    
    def add_threshold(self, threshold: PerformanceThreshold) -> None:
        """添加性能閾值
        
        Args:
            threshold: 性能閾值
        """
        self.thresholds[threshold.metric_type] = threshold
        
        self.logger.info(
            "添加性能閾值",
            metric_type=threshold.metric_type.value,
            warning=threshold.warning_threshold,
            critical=threshold.critical_threshold
        )
    
    def add_custom_metric_collector(self, name: str, collector: Callable[[], float]) -> None:
        """添加自定義指標收集器
        
        Args:
            name: 指標名稱
            collector: 收集器函數
        """
        self.collector.add_custom_collector(name, collector)
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """添加告警回調
        
        Args:
            callback: 告警回調函數
        """
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """獲取當前指標"""
        return self.collector.collect_all_metrics()
    
    def get_metrics_history(self, hours: int = 1) -> List[PerformanceMetrics]:
        """獲取指標歷史"""
        return self.collector.get_metrics_history(hours)
    
    def get_average_metrics(self, hours: int = 1) -> Dict[str, float]:
        """獲取平均指標"""
        return self.collector.get_average_metrics(hours)
    
    def get_alerts(self, 
                  resolved: Optional[bool] = None,
                  hours: int = 24) -> List[PerformanceAlert]:
        """獲取告警列表
        
        Args:
            resolved: 是否已解決（None為全部）
            hours: 時間範圍（小時）
            
        Returns:
            List[PerformanceAlert]: 告警列表
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def _check_thresholds(self, metrics: PerformanceMetrics) -> List[PerformanceAlert]:
        """檢查閾值"""
        alerts = []
        
        for metric_type, threshold in self.thresholds.items():
            if not threshold.enabled:
                continue
            
            value = metrics.get_metric_value(metric_type)
            if value is None:
                continue
            
            alert_level = threshold.check_threshold(value)
            if alert_level is not None:
                # 檢查告警冷卻
                alert_key = f"{metric_type.value}_{alert_level.value}"
                now = datetime.utcnow()
                
                if alert_key in self.last_alert_time:
                    last_time = self.last_alert_time[alert_key]
                    if (now - last_time).total_seconds() < self.alert_cooldown:
                        continue
                
                # 創建告警
                alert = PerformanceAlert(
                    metric_type=metric_type,
                    level=alert_level,
                    message=f"{metric_type.value}超過{alert_level.value}閾值: {value:.2f}%",
                    current_value=value,
                    threshold=threshold.critical_threshold if alert_level == AlertLevel.CRITICAL else threshold.warning_threshold,
                    timestamp=now
                )
                
                alerts.append(alert)
                self.last_alert_time[alert_key] = now
        
        return alerts
    
    def _trigger_alerts(self, alerts: List[PerformanceAlert]) -> None:
        """觸發告警"""
        for alert in alerts:
            self.alert_history.append(alert)
            
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
                "觸發性能告警",
                metric_type=alert.metric_type.value,
                level=alert.level.value,
                message=alert.message,
                current_value=alert.current_value,
                threshold=alert.threshold
            )
    
    async def _monitor_loop(self) -> None:
        """監控循環"""
        while self._running:
            try:
                # 收集指標
                metrics = self.collector.collect_all_metrics()
                
                # 檢查閾值
                alerts = self._check_thresholds(metrics)
                
                # 觸發告警
                if alerts:
                    self._trigger_alerts(alerts)
                
                # 清理舊告警
                self._cleanup_old_alerts()
                
                # 記錄指標（僅在高使用率時）
                if (metrics.system_metrics.cpu_percent > 50 or 
                    metrics.system_metrics.memory_percent > 50):
                    self.logger.debug(
                        "性能指標",
                        cpu_percent=metrics.system_metrics.cpu_percent,
                        memory_percent=metrics.system_metrics.memory_percent,
                        disk_usage_percent=metrics.system_metrics.disk_usage_percent
                    )
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("監控循環錯誤", error=str(e))
                await asyncio.sleep(self.collection_interval)
    
    def _cleanup_old_alerts(self) -> None:
        """清理舊告警"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        original_count = len(self.alert_history)
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        cleaned_count = original_count - len(self.alert_history)
        if cleaned_count > 0:
            self.logger.debug("清理舊性能告警", count=cleaned_count)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """獲取性能摘要"""
        current_metrics = self.get_current_metrics()
        avg_metrics = self.get_average_metrics(hours=1)
        alerts = self.get_alerts(resolved=False, hours=24)
        
        summary = {
            "current_metrics": {
                "cpu_percent": current_metrics.system_metrics.cpu_percent,
                "memory_percent": current_metrics.system_metrics.memory_percent,
                "disk_usage_percent": current_metrics.system_metrics.disk_usage_percent,
                "process_count": current_metrics.system_metrics.process_count,
                "memory_available_mb": current_metrics.system_metrics.memory_available_mb,
                "disk_free_gb": current_metrics.system_metrics.disk_free_gb
            },
            "average_metrics_1h": avg_metrics,
            "active_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.level == AlertLevel.CRITICAL]),
            "warning_alerts": len([a for a in alerts if a.level == AlertLevel.WARNING]),
            "thresholds": {
                metric_type.value: {
                    "warning": threshold.warning_threshold,
                    "critical": threshold.critical_threshold,
                    "enabled": threshold.enabled
                }
                for metric_type, threshold in self.thresholds.items()
            }
        }
        
        return summary