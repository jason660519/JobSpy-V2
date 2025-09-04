"""任務調度器

管理並發任務執行，實現智能負載均衡和資源控制。
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任務優先級"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """任務數據結構"""
    id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at is None:
            self.created_at = time.time()


class TaskScheduler:
    """任務調度器
    
    提供並發任務執行、優先級調度、重試機制和資源控制功能。
    """
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logger.bind(component="task_scheduler")
        
        # 任務隊列和狀態
        self._pending_tasks: List[Task] = []
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, Task] = {}
        
        # 控制信號
        self._shutdown_event = asyncio.Event()
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # 統計信息
        self._stats = {
            "total_submitted": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_cancelled": 0
        }
    
    async def start(self):
        """啟動調度器"""
        if self._scheduler_task is not None:
            self.logger.warning("調度器已經在運行")
            return
        
        self.logger.info("啟動任務調度器", max_concurrent=self.max_concurrent_tasks)
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self):
        """停止調度器"""
        self.logger.info("正在停止任務調度器...")
        
        # 設置停止信號
        self._shutdown_event.set()
        
        # 等待調度器任務完成
        if self._scheduler_task:
            await self._scheduler_task
        
        # 取消所有運行中的任務
        await self._cancel_all_running_tasks()
        
        self.logger.info("任務調度器已停止")
    
    async def submit_task(self, task: Task) -> str:
        """提交任務
        
        Args:
            task: 要執行的任務
            
        Returns:
            str: 任務ID
        """
        self._stats["total_submitted"] += 1
        
        # 按優先級插入任務
        self._insert_task_by_priority(task)
        
        self.logger.info(
            "任務已提交", 
            task_id=task.id, 
            task_name=task.name, 
            priority=task.priority.name,
            queue_size=len(self._pending_tasks)
        )
        
        return task.id
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """獲取任務狀態"""
        # 檢查運行中的任務
        if task_id in self._running_tasks:
            return TaskStatus.RUNNING
        
        # 檢查已完成的任務
        if task_id in self._completed_tasks:
            return self._completed_tasks[task_id].status
        
        # 檢查待處理的任務
        for task in self._pending_tasks:
            if task.id == task_id:
                return TaskStatus.PENDING
        
        return None
    
    async def get_task_result(self, task_id: str) -> Any:
        """獲取任務結果"""
        if task_id in self._completed_tasks:
            task = self._completed_tasks[task_id]
            if task.status == TaskStatus.COMPLETED:
                return task.result
            elif task.status == TaskStatus.FAILED:
                raise task.error
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任務"""
        # 取消運行中的任務
        if task_id in self._running_tasks:
            asyncio_task = self._running_tasks[task_id]
            asyncio_task.cancel()
            return True
        
        # 從待處理隊列中移除
        for i, task in enumerate(self._pending_tasks):
            if task.id == task_id:
                task.status = TaskStatus.CANCELLED
                self._pending_tasks.pop(i)
                self._completed_tasks[task_id] = task
                self._stats["total_cancelled"] += 1
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取調度器統計信息"""
        return {
            **self._stats,
            "pending_tasks": len(self._pending_tasks),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": len(self._completed_tasks),
            "max_concurrent": self.max_concurrent_tasks
        }
    
    async def _scheduler_loop(self):
        """調度器主循環"""
        self.logger.info("調度器主循環已啟動")
        
        try:
            while not self._shutdown_event.is_set():
                # 清理已完成的任務
                await self._cleanup_completed_tasks()
                
                # 調度新任務
                await self._schedule_pending_tasks()
                
                # 短暫休眠避免CPU過度使用
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            self.logger.info("調度器主循環被取消")
        except Exception as e:
            self.logger.error("調度器主循環發生錯誤", error=str(e))
        finally:
            self.logger.info("調度器主循環已退出")
    
    async def _schedule_pending_tasks(self):
        """調度待處理任務"""
        # 檢查是否有可用的執行槽位
        available_slots = self.max_concurrent_tasks - len(self._running_tasks)
        
        if available_slots <= 0 or not self._pending_tasks:
            return
        
        # 按優先級調度任務
        tasks_to_schedule = self._pending_tasks[:available_slots]
        
        for task in tasks_to_schedule:
            await self._start_task(task)
            self._pending_tasks.remove(task)
    
    async def _start_task(self, task: Task):
        """啟動單個任務"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        # 創建asyncio任務
        asyncio_task = asyncio.create_task(self._execute_task(task))
        self._running_tasks[task.id] = asyncio_task
        
        self.logger.info(
            "任務已啟動", 
            task_id=task.id, 
            task_name=task.name,
            running_count=len(self._running_tasks)
        )
    
    async def _execute_task(self, task: Task):
        """執行任務"""
        try:
            # 設置超時
            if task.timeout:
                result = await asyncio.wait_for(
                    task.func(*task.args, **task.kwargs),
                    timeout=task.timeout
                )
            else:
                result = await task.func(*task.args, **task.kwargs)
            
            # 任務成功完成
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            self._stats["total_completed"] += 1
            
            self.logger.info(
                "任務執行成功", 
                task_id=task.id, 
                task_name=task.name,
                execution_time=task.completed_at - task.started_at
            )
            
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self._stats["total_cancelled"] += 1
            
            self.logger.info("任務被取消", task_id=task.id, task_name=task.name)
            
        except Exception as e:
            task.error = e
            task.completed_at = time.time()
            
            # 檢查是否需要重試
            if task.retry_count < task.max_retries:
                await self._retry_task(task)
            else:
                task.status = TaskStatus.FAILED
                self._stats["total_failed"] += 1
                
                self.logger.error(
                    "任務執行失敗", 
                    task_id=task.id, 
                    task_name=task.name,
                    error=str(e),
                    retry_count=task.retry_count
                )
        
        finally:
            # 從運行任務中移除
            if task.id in self._running_tasks:
                del self._running_tasks[task.id]
            
            # 添加到已完成任務
            self._completed_tasks[task.id] = task
    
    async def _retry_task(self, task: Task):
        """重試任務"""
        task.retry_count += 1
        task.status = TaskStatus.PENDING
        task.started_at = None
        task.error = None
        
        # 計算重試延遲（指數退避）
        delay = min(2 ** task.retry_count, 60)  # 最大60秒
        
        self.logger.info(
            "任務將重試", 
            task_id=task.id, 
            task_name=task.name,
            retry_count=task.retry_count,
            delay=delay
        )
        
        # 延遲後重新加入隊列
        await asyncio.sleep(delay)
        self._insert_task_by_priority(task)
    
    async def _cleanup_completed_tasks(self):
        """清理已完成的任務（保留最近1000個）"""
        if len(self._completed_tasks) > 1000:
            # 按完成時間排序，保留最新的1000個
            sorted_tasks = sorted(
                self._completed_tasks.values(),
                key=lambda t: t.completed_at or 0,
                reverse=True
            )
            
            # 重建已完成任務字典
            self._completed_tasks = {
                task.id: task for task in sorted_tasks[:1000]
            }
    
    async def _cancel_all_running_tasks(self):
        """取消所有運行中的任務"""
        if not self._running_tasks:
            return
        
        self.logger.info("正在取消所有運行中的任務", count=len(self._running_tasks))
        
        # 取消所有任務
        for asyncio_task in self._running_tasks.values():
            asyncio_task.cancel()
        
        # 等待所有任務完成取消
        if self._running_tasks:
            await asyncio.gather(
                *self._running_tasks.values(),
                return_exceptions=True
            )
        
        self._running_tasks.clear()
    
    def _insert_task_by_priority(self, task: Task):
        """按優先級插入任務"""
        # 找到合適的插入位置
        insert_index = 0
        for i, existing_task in enumerate(self._pending_tasks):
            if task.priority.value > existing_task.priority.value:
                insert_index = i
                break
            insert_index = i + 1
        
        self._pending_tasks.insert(insert_index, task)


# 便利函數
async def create_task(task_id: str, name: str, func: Callable, *args, 
                     priority: TaskPriority = TaskPriority.NORMAL,
                     timeout: Optional[float] = None,
                     max_retries: int = 3,
                     **kwargs) -> Task:
    """創建任務的便利函數"""
    return Task(
        id=task_id,
        name=name,
        func=func,
        args=args,
        kwargs=kwargs,
        priority=priority,
        timeout=timeout,
        max_retries=max_retries
    )