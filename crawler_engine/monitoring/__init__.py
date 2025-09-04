"""監控和成本控制模組

提供系統監控、成本控制、性能分析和告警功能。
"""

from .cost_controller import (
    CostController,
    CostConfig,
    CostMetrics,
    CostLimit,
    CostAlert,
    ResourceType,
    CostTracker
)

from .performance_monitor import (
    PerformanceMonitor,
    PerformanceMetrics,
    SystemMetrics,
    ResourceUsage,
    PerformanceAlert
)

from .health_checker import (
    HealthChecker,
    HealthStatus,
    HealthCheck,
    ComponentHealth,
    HealthReport
)

from .alerting import (
    AlertManager,
    Alert,
    AlertLevel,
    AlertChannel,
    NotificationConfig
)

from .metrics_collector import (
    MetricsCollector,
    Metric,
    MetricType,
    MetricsStorage,
    MetricsQuery
)

__version__ = "1.0.0"

# 默認配置
DEFAULT_COST_LIMITS = {
    "api_calls_per_hour": 1000,
    "api_calls_per_day": 10000,
    "storage_mb": 1000,
    "bandwidth_mb": 5000,
    "compute_minutes": 60
}

DEFAULT_PERFORMANCE_THRESHOLDS = {
    "cpu_usage_percent": 80,
    "memory_usage_percent": 85,
    "disk_usage_percent": 90,
    "response_time_ms": 5000,
    "error_rate_percent": 5
}

DEFAULT_HEALTH_CHECK_INTERVAL = 30  # 秒
DEFAULT_METRICS_RETENTION_DAYS = 30

__all__ = [
    # 成本控制
    "CostController",
    "CostConfig",
    "CostMetrics",
    "CostLimit",
    "CostAlert",
    "ResourceType",
    "CostTracker",
    
    # 性能監控
    "PerformanceMonitor",
    "PerformanceMetrics",
    "SystemMetrics",
    "ResourceUsage",
    "PerformanceAlert",
    
    # 健康檢查
    "HealthChecker",
    "HealthStatus",
    "HealthCheck",
    "ComponentHealth",
    "HealthReport",
    
    # 告警系統
    "AlertManager",
    "Alert",
    "AlertLevel",
    "AlertChannel",
    "NotificationConfig",
    
    # 指標收集
    "MetricsCollector",
    "Metric",
    "MetricType",
    "MetricsStorage",
    "MetricsQuery",
    
    # 默認配置
    "DEFAULT_COST_LIMITS",
    "DEFAULT_PERFORMANCE_THRESHOLDS",
    "DEFAULT_HEALTH_CHECK_INTERVAL",
    "DEFAULT_METRICS_RETENTION_DAYS"
]