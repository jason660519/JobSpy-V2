"""指標收集器

收集、存儲和查詢系統指標數據。
"""

import asyncio
import time
import json
import sqlite3
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import structlog
from collections import defaultdict, deque
import threading

logger = structlog.get_logger(__name__)


class MetricType(Enum):
    """指標類型"""
    COUNTER = "counter"        # 計數器（只增不減）
    GAUGE = "gauge"            # 儀表（可增可減）
    HISTOGRAM = "histogram"    # 直方圖
    SUMMARY = "summary"        # 摘要
    TIMER = "timer"            # 計時器


class AggregationType(Enum):
    """聚合類型"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    P50 = "p50"  # 50th percentile
    P90 = "p90"  # 90th percentile
    P95 = "p95"  # 95th percentile
    P99 = "p99"  # 99th percentile


@dataclass
class Metric:
    """指標"""
    name: str
    value: Union[float, int]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.value, (int, float)):
            raise ValueError("Metric value must be numeric")
    
    @property
    def key(self) -> str:
        """指標唯一鍵"""
        tag_str = ','.join([f"{k}={v}" for k, v in sorted(self.tags.items())])
        return f"{self.name}[{tag_str}]" if tag_str else self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """從字典創建"""
        return cls(
            name=data['name'],
            value=data['value'],
            metric_type=MetricType(data['type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            tags=data.get('tags', {}),
            metadata=data.get('metadata', {})
        )


@dataclass
class MetricsQuery:
    """指標查詢"""
    metric_names: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    aggregation: Optional[AggregationType] = None
    group_by: Optional[List[str]] = None  # 按標籤分組
    limit: Optional[int] = None
    
    def matches(self, metric: Metric) -> bool:
        """檢查指標是否匹配查詢條件"""
        # 檢查指標名稱
        if self.metric_names and metric.name not in self.metric_names:
            return False
        
        # 檢查時間範圍
        if self.start_time and metric.timestamp < self.start_time:
            return False
        
        if self.end_time and metric.timestamp > self.end_time:
            return False
        
        # 檢查標籤
        if self.tags:
            for key, value in self.tags.items():
                if metric.tags.get(key) != value:
                    return False
        
        return True


@dataclass
class MetricsStats:
    """指標統計"""
    total_metrics: int = 0
    metrics_by_type: Dict[str, int] = field(default_factory=dict)
    storage_size_mb: float = 0.0
    oldest_metric: Optional[datetime] = None
    newest_metric: Optional[datetime] = None
    collection_rate: float = 0.0  # 每秒收集的指標數


class MetricsStorage:
    """指標存儲基類"""
    
    async def store_metric(self, metric: Metric) -> None:
        """存儲指標"""
        raise NotImplementedError
    
    async def store_metrics(self, metrics: List[Metric]) -> None:
        """批量存儲指標"""
        for metric in metrics:
            await self.store_metric(metric)
    
    async def query_metrics(self, query: MetricsQuery) -> List[Metric]:
        """查詢指標"""
        raise NotImplementedError
    
    async def get_stats(self) -> MetricsStats:
        """獲取統計信息"""
        raise NotImplementedError
    
    async def cleanup_old_metrics(self, days: int) -> int:
        """清理舊指標"""
        raise NotImplementedError


class MemoryMetricsStorage(MetricsStorage):
    """內存指標存儲"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.lock = threading.RLock()
        self.logger = logger.bind(component="MemoryMetricsStorage")
    
    async def store_metric(self, metric: Metric) -> None:
        """存儲指標到內存"""
        with self.lock:
            self.metrics.append(metric)
    
    async def store_metrics(self, metrics: List[Metric]) -> None:
        """批量存儲指標"""
        with self.lock:
            self.metrics.extend(metrics)
    
    async def query_metrics(self, query: MetricsQuery) -> List[Metric]:
        """查詢指標"""
        with self.lock:
            # 過濾指標
            filtered_metrics = [
                metric for metric in self.metrics
                if query.matches(metric)
            ]
            
            # 排序（按時間倒序）
            filtered_metrics.sort(key=lambda x: x.timestamp, reverse=True)
            
            # 限制數量
            if query.limit:
                filtered_metrics = filtered_metrics[:query.limit]
            
            return filtered_metrics
    
    async def get_stats(self) -> MetricsStats:
        """獲取統計信息"""
        with self.lock:
            if not self.metrics:
                return MetricsStats()
            
            # 統計指標類型
            type_counts = defaultdict(int)
            for metric in self.metrics:
                type_counts[metric.metric_type.value] += 1
            
            # 時間範圍
            timestamps = [m.timestamp for m in self.metrics]
            oldest = min(timestamps) if timestamps else None
            newest = max(timestamps) if timestamps else None
            
            return MetricsStats(
                total_metrics=len(self.metrics),
                metrics_by_type=dict(type_counts),
                storage_size_mb=0.0,  # 內存存儲不計算大小
                oldest_metric=oldest,
                newest_metric=newest
            )
    
    async def cleanup_old_metrics(self, days: int) -> int:
        """清理舊指標"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        with self.lock:
            original_count = len(self.metrics)
            
            # 過濾掉舊指標
            self.metrics = deque(
                (metric for metric in self.metrics if metric.timestamp >= cutoff_time),
                maxlen=self.max_metrics
            )
            
            cleaned_count = original_count - len(self.metrics)
            
            if cleaned_count > 0:
                self.logger.info(
                    "清理舊指標",
                    count=cleaned_count,
                    days=days
                )
            
            return cleaned_count


class DatabaseMetricsStorage(MetricsStorage):
    """數據庫指標存儲"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logger.bind(component="DatabaseMetricsStorage")
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化數據庫"""
        # 確保目錄存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 創建指標表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 創建索引
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(type)"
        )
        
        conn.commit()
        conn.close()
        
        self.logger.info("數據庫指標存儲初始化完成", db_path=self.db_path)
    
    async def store_metric(self, metric: Metric) -> None:
        """存儲指標到數據庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO metrics (name, value, type, timestamp, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.name,
                metric.value,
                metric.metric_type.value,
                metric.timestamp.isoformat(),
                json.dumps(metric.tags) if metric.tags else None,
                json.dumps(metric.metadata) if metric.metadata else None
            ))
            
            conn.commit()
            
        except Exception as e:
            self.logger.error(
                "存儲指標失敗",
                metric_name=metric.name,
                error=str(e)
            )
            raise
        finally:
            conn.close()
    
    async def store_metrics(self, metrics: List[Metric]) -> None:
        """批量存儲指標"""
        if not metrics:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            data = [
                (
                    metric.name,
                    metric.value,
                    metric.metric_type.value,
                    metric.timestamp.isoformat(),
                    json.dumps(metric.tags) if metric.tags else None,
                    json.dumps(metric.metadata) if metric.metadata else None
                )
                for metric in metrics
            ]
            
            cursor.executemany("""
                INSERT INTO metrics (name, value, type, timestamp, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)
            
            conn.commit()
            
            self.logger.debug(
                "批量存儲指標完成",
                count=len(metrics)
            )
            
        except Exception as e:
            self.logger.error(
                "批量存儲指標失敗",
                count=len(metrics),
                error=str(e)
            )
            raise
        finally:
            conn.close()
    
    async def query_metrics(self, query: MetricsQuery) -> List[Metric]:
        """查詢指標"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 構建SQL查詢
            sql = "SELECT name, value, type, timestamp, tags, metadata FROM metrics WHERE 1=1"
            params = []
            
            # 指標名稱過濾
            if query.metric_names:
                placeholders = ','.join(['?' for _ in query.metric_names])
                sql += f" AND name IN ({placeholders})"
                params.extend(query.metric_names)
            
            # 時間範圍過濾
            if query.start_time:
                sql += " AND timestamp >= ?"
                params.append(query.start_time.isoformat())
            
            if query.end_time:
                sql += " AND timestamp <= ?"
                params.append(query.end_time.isoformat())
            
            # 排序
            sql += " ORDER BY timestamp DESC"
            
            # 限制數量
            if query.limit:
                sql += " LIMIT ?"
                params.append(query.limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # 轉換為Metric對象
            metrics = []
            for row in rows:
                name, value, metric_type, timestamp, tags_json, metadata_json = row
                
                tags = json.loads(tags_json) if tags_json else {}
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType(metric_type),
                    timestamp=datetime.fromisoformat(timestamp),
                    tags=tags,
                    metadata=metadata
                )
                
                # 檢查標籤過濾
                if query.tags:
                    match = True
                    for key, value in query.tags.items():
                        if metric.tags.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            self.logger.error(
                "查詢指標失敗",
                error=str(e)
            )
            raise
        finally:
            conn.close()
    
    async def get_stats(self) -> MetricsStats:
        """獲取統計信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 總指標數
            cursor.execute("SELECT COUNT(*) FROM metrics")
            total_metrics = cursor.fetchone()[0]
            
            # 按類型統計
            cursor.execute("""
                SELECT type, COUNT(*) FROM metrics GROUP BY type
            """)
            type_counts = dict(cursor.fetchall())
            
            # 時間範圍
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp) FROM metrics
            """)
            time_range = cursor.fetchone()
            oldest = datetime.fromisoformat(time_range[0]) if time_range[0] else None
            newest = datetime.fromisoformat(time_range[1]) if time_range[1] else None
            
            # 數據庫文件大小
            db_size_mb = Path(self.db_path).stat().st_size / (1024 * 1024)
            
            return MetricsStats(
                total_metrics=total_metrics,
                metrics_by_type=type_counts,
                storage_size_mb=db_size_mb,
                oldest_metric=oldest,
                newest_metric=newest
            )
            
        except Exception as e:
            self.logger.error(
                "獲取統計信息失敗",
                error=str(e)
            )
            return MetricsStats()
        finally:
            conn.close()
    
    async def cleanup_old_metrics(self, days: int) -> int:
        """清理舊指標"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 刪除舊指標
            cursor.execute(
                "DELETE FROM metrics WHERE timestamp < ?",
                (cutoff_time.isoformat(),)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # 清理數據庫
            cursor.execute("VACUUM")
            
            if deleted_count > 0:
                self.logger.info(
                    "清理舊指標",
                    count=deleted_count,
                    days=days
                )
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(
                "清理舊指標失敗",
                error=str(e)
            )
            return 0
        finally:
            conn.close()


class MetricsCollector:
    """指標收集器
    
    收集、聚合和存儲系統指標。
    """
    
    def __init__(self, 
                 storage: MetricsStorage,
                 batch_size: int = 100,
                 flush_interval: int = 60):
        self.storage = storage
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.logger = logger.bind(component="MetricsCollector")
        
        # 指標緩衝區
        self.metric_buffer: List[Metric] = []
        self.buffer_lock = threading.RLock()
        
        # 自定義收集器
        self.custom_collectors: Dict[str, Callable[[], Union[Metric, List[Metric]]]] = {}
        
        # 運行狀態
        self._running = False
        self._flush_task = None
        
        # 統計信息
        self.collection_stats = {
            'metrics_collected': 0,
            'metrics_flushed': 0,
            'flush_errors': 0,
            'last_flush_time': None,
            'collection_rate': 0.0
        }
        
        self._last_collection_count = 0
        self._last_rate_check = time.time()
    
    def add_custom_collector(self, 
                           name: str, 
                           collector: Callable[[], Union[Metric, List[Metric]]]) -> None:
        """添加自定義指標收集器
        
        Args:
            name: 收集器名稱
            collector: 收集器函數，返回Metric或Metric列表
        """
        self.custom_collectors[name] = collector
        
        self.logger.info(
            "添加自定義指標收集器",
            name=name
        )
    
    def remove_custom_collector(self, name: str) -> None:
        """移除自定義指標收集器
        
        Args:
            name: 收集器名稱
        """
        if name in self.custom_collectors:
            del self.custom_collectors[name]
            
            self.logger.info(
                "移除自定義指標收集器",
                name=name
            )
    
    def collect_metric(self, 
                      name: str,
                      value: Union[float, int],
                      metric_type: MetricType = MetricType.GAUGE,
                      tags: Optional[Dict[str, str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """收集單個指標
        
        Args:
            name: 指標名稱
            value: 指標值
            metric_type: 指標類型
            tags: 標籤
            metadata: 元數據
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self._add_to_buffer(metric)
    
    def collect_counter(self, 
                       name: str,
                       value: Union[float, int] = 1,
                       tags: Optional[Dict[str, str]] = None) -> None:
        """收集計數器指標
        
        Args:
            name: 指標名稱
            value: 增量值
            tags: 標籤
        """
        self.collect_metric(name, value, MetricType.COUNTER, tags)
    
    def collect_gauge(self, 
                     name: str,
                     value: Union[float, int],
                     tags: Optional[Dict[str, str]] = None) -> None:
        """收集儀表指標
        
        Args:
            name: 指標名稱
            value: 當前值
            tags: 標籤
        """
        self.collect_metric(name, value, MetricType.GAUGE, tags)
    
    def collect_timer(self, 
                     name: str,
                     duration_ms: float,
                     tags: Optional[Dict[str, str]] = None) -> None:
        """收集計時器指標
        
        Args:
            name: 指標名稱
            duration_ms: 持續時間（毫秒）
            tags: 標籤
        """
        self.collect_metric(name, duration_ms, MetricType.TIMER, tags)
    
    def timer_context(self, 
                     name: str,
                     tags: Optional[Dict[str, str]] = None):
        """計時器上下文管理器
        
        Args:
            name: 指標名稱
            tags: 標籤
            
        Returns:
            計時器上下文管理器
        """
        return TimerContext(self, name, tags)
    
    def _add_to_buffer(self, metric: Metric) -> None:
        """添加指標到緩衝區"""
        with self.buffer_lock:
            self.metric_buffer.append(metric)
            self.collection_stats['metrics_collected'] += 1
            
            # 檢查是否需要立即刷新
            if len(self.metric_buffer) >= self.batch_size:
                asyncio.create_task(self._flush_buffer())
    
    async def collect_custom_metrics(self) -> None:
        """收集自定義指標"""
        for name, collector in self.custom_collectors.items():
            try:
                result = collector()
                
                if isinstance(result, Metric):
                    self._add_to_buffer(result)
                elif isinstance(result, list):
                    for metric in result:
                        if isinstance(metric, Metric):
                            self._add_to_buffer(metric)
                else:
                    self.logger.warning(
                        "自定義收集器返回無效類型",
                        collector=name,
                        type=type(result).__name__
                    )
                    
            except Exception as e:
                self.logger.error(
                    "自定義指標收集失敗",
                    collector=name,
                    error=str(e)
                )
    
    async def _flush_buffer(self) -> None:
        """刷新緩衝區"""
        with self.buffer_lock:
            if not self.metric_buffer:
                return
            
            # 複製並清空緩衝區
            metrics_to_flush = self.metric_buffer.copy()
            self.metric_buffer.clear()
        
        try:
            # 存儲指標
            await self.storage.store_metrics(metrics_to_flush)
            
            self.collection_stats['metrics_flushed'] += len(metrics_to_flush)
            self.collection_stats['last_flush_time'] = datetime.utcnow()
            
            self.logger.debug(
                "指標緩衝區刷新完成",
                count=len(metrics_to_flush)
            )
            
        except Exception as e:
            self.collection_stats['flush_errors'] += 1
            
            self.logger.error(
                "指標緩衝區刷新失敗",
                count=len(metrics_to_flush),
                error=str(e)
            )
            
            # 將失敗的指標重新加入緩衝區
            with self.buffer_lock:
                self.metric_buffer.extend(metrics_to_flush)
    
    def _update_collection_rate(self) -> None:
        """更新收集速率"""
        now = time.time()
        time_diff = now - self._last_rate_check
        
        if time_diff >= 60:  # 每分鐘更新一次
            count_diff = self.collection_stats['metrics_collected'] - self._last_collection_count
            self.collection_stats['collection_rate'] = count_diff / time_diff
            
            self._last_collection_count = self.collection_stats['metrics_collected']
            self._last_rate_check = now
    
    async def start(self) -> None:
        """啟動指標收集器"""
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
        
        self.logger.info(
            "指標收集器已啟動",
            batch_size=self.batch_size,
            flush_interval=self.flush_interval,
            custom_collectors=len(self.custom_collectors)
        )
    
    async def stop(self) -> None:
        """停止指標收集器"""
        self._running = False
        
        # 停止刷新任務
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # 最後一次刷新緩衝區
        await self._flush_buffer()
        
        self.logger.info("指標收集器已停止")
    
    async def _flush_loop(self) -> None:
        """刷新循環"""
        while self._running:
            try:
                # 收集自定義指標
                await self.collect_custom_metrics()
                
                # 刷新緩衝區
                await self._flush_buffer()
                
                # 更新收集速率
                self._update_collection_rate()
                
                await asyncio.sleep(self.flush_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("刷新循環錯誤", error=str(e))
                await asyncio.sleep(self.flush_interval)
    
    async def query_metrics(self, query: MetricsQuery) -> List[Metric]:
        """查詢指標
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Metric]: 指標列表
        """
        return await self.storage.query_metrics(query)
    
    async def get_aggregated_metrics(self, 
                                   query: MetricsQuery,
                                   aggregation: AggregationType,
                                   interval_minutes: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """獲取聚合指標
        
        Args:
            query: 查詢條件
            aggregation: 聚合類型
            interval_minutes: 聚合間隔（分鐘）
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 聚合結果
        """
        metrics = await self.query_metrics(query)
        
        if not metrics:
            return {}
        
        # 按指標名稱和時間間隔分組
        grouped_metrics = defaultdict(lambda: defaultdict(list))
        
        for metric in metrics:
            # 計算時間間隔
            interval_start = metric.timestamp.replace(
                minute=(metric.timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0
            )
            
            grouped_metrics[metric.name][interval_start].append(metric.value)
        
        # 聚合計算
        result = {}
        for metric_name, intervals in grouped_metrics.items():
            result[metric_name] = []
            
            for interval_start, values in sorted(intervals.items()):
                if aggregation == AggregationType.SUM:
                    agg_value = sum(values)
                elif aggregation == AggregationType.AVG:
                    agg_value = sum(values) / len(values)
                elif aggregation == AggregationType.MIN:
                    agg_value = min(values)
                elif aggregation == AggregationType.MAX:
                    agg_value = max(values)
                elif aggregation == AggregationType.COUNT:
                    agg_value = len(values)
                elif aggregation == AggregationType.P50:
                    sorted_values = sorted(values)
                    agg_value = sorted_values[len(sorted_values) // 2]
                elif aggregation == AggregationType.P90:
                    sorted_values = sorted(values)
                    agg_value = sorted_values[int(len(sorted_values) * 0.9)]
                elif aggregation == AggregationType.P95:
                    sorted_values = sorted(values)
                    agg_value = sorted_values[int(len(sorted_values) * 0.95)]
                elif aggregation == AggregationType.P99:
                    sorted_values = sorted(values)
                    agg_value = sorted_values[int(len(sorted_values) * 0.99)]
                else:
                    agg_value = sum(values) / len(values)  # 默認平均值
                
                result[metric_name].append({
                    'timestamp': interval_start.isoformat(),
                    'value': agg_value,
                    'count': len(values)
                })
        
        return result
    
    async def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        storage_stats = await self.storage.get_stats()
        
        with self.buffer_lock:
            buffer_size = len(self.metric_buffer)
        
        return {
            'collection_stats': self.collection_stats,
            'storage_stats': asdict(storage_stats),
            'buffer_size': buffer_size,
            'custom_collectors': len(self.custom_collectors),
            'running': self._running
        }
    
    async def cleanup_old_metrics(self, days: int = 30) -> int:
        """清理舊指標
        
        Args:
            days: 保留天數
            
        Returns:
            int: 清理的指標數量
        """
        return await self.storage.cleanup_old_metrics(days)


class TimerContext:
    """計時器上下文管理器"""
    
    def __init__(self, 
                 collector: MetricsCollector,
                 name: str,
                 tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.collect_timer(self.name, duration_ms, self.tags)


# 便捷函數
def timer(collector: MetricsCollector, 
         name: str,
         tags: Optional[Dict[str, str]] = None):
    """計時器裝飾器
    
    Args:
        collector: 指標收集器
        name: 指標名稱
        tags: 標籤
        
    Returns:
        裝飾器函數
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                with collector.timer_context(name, tags):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                with collector.timer_context(name, tags):
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator