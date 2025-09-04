"""數據處理管道

提供靈活的數據處理管道，支持多階段處理、並行執行和錯誤恢復。
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Union, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import structlog
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path

logger = structlog.get_logger(__name__)


class PipelineStage(Enum):
    """管道階段枚舉"""
    VALIDATION = "validation"          # 數據驗證
    CLEANING = "cleaning"              # 數據清洗
    TRANSFORMATION = "transformation"  # 數據轉換
    ENRICHMENT = "enrichment"          # 數據豐富化
    DEDUPLICATION = "deduplication"    # 去重
    STORAGE = "storage"                # 存儲
    EXPORT = "export"                  # 導出


class ProcessingStatus(Enum):
    """處理狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineConfig:
    """管道配置"""
    name: str
    description: str = ""
    batch_size: int = 100
    max_workers: int = 4
    timeout: int = 300
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_parallel: bool = True
    enable_cache: bool = True
    enable_metrics: bool = True
    checkpoint_interval: int = 1000
    checkpoint_path: Optional[str] = None
    stages: List[PipelineStage] = field(default_factory=lambda: [
        PipelineStage.VALIDATION,
        PipelineStage.CLEANING,
        PipelineStage.TRANSFORMATION,
        PipelineStage.DEDUPLICATION,
        PipelineStage.STORAGE
    ])
    stage_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ProcessingMetrics:
    """處理指標"""
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    stage_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_items == 0:
            return 0.0
        return self.processed_items / self.total_items
    
    @property
    def processing_time(self) -> float:
        """處理時間（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def throughput(self) -> float:
        """吞吐量（項目/秒）"""
        if self.processing_time > 0:
            return self.processed_items / self.processing_time
        return 0.0


@dataclass
class ProcessingResult:
    """處理結果"""
    status: ProcessingStatus
    data: Any = None
    error: Optional[str] = None
    stage: Optional[PipelineStage] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineProcessor(ABC):
    """管道處理器基類"""
    
    def __init__(self, stage: PipelineStage, config: Dict[str, Any] = None):
        self.stage = stage
        self.config = config or {}
        self.logger = structlog.get_logger(f"{__name__}.{stage.value}")
    
    @abstractmethod
    async def process(self, data: Any) -> ProcessingResult:
        """處理數據
        
        Args:
            data: 輸入數據
            
        Returns:
            ProcessingResult: 處理結果
        """
        pass
    
    async def process_batch(self, batch: List[Any]) -> List[ProcessingResult]:
        """批量處理數據
        
        Args:
            batch: 數據批次
            
        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        results = []
        for item in batch:
            try:
                result = await self.process(item)
                results.append(result)
            except Exception as e:
                self.logger.error(
                    "處理項目失敗",
                    stage=self.stage.value,
                    error=str(e)
                )
                results.append(ProcessingResult(
                    status=ProcessingStatus.FAILED,
                    error=str(e),
                    stage=self.stage
                ))
        return results
    
    def validate_config(self) -> bool:
        """驗證配置
        
        Returns:
            bool: 配置是否有效
        """
        return True


class DataPipeline:
    """數據處理管道
    
    提供靈活的數據處理流水線，支持多階段處理、並行執行和錯誤恢復。
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = structlog.get_logger(f"{__name__}.{config.name}")
        
        # 處理器映射
        self.processors: Dict[PipelineStage, PipelineProcessor] = {}
        
        # 處理指標
        self.metrics = ProcessingMetrics()
        
        # 檢查點數據
        self.checkpoint_data: Dict[str, Any] = {}
        
        # 線程池
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        
        # 狀態
        self.is_running = False
        self.is_paused = False
    
    def register_processor(self, processor: PipelineProcessor) -> None:
        """註冊處理器
        
        Args:
            processor: 處理器實例
        """
        if processor.stage not in self.config.stages:
            raise ValueError(f"階段 {processor.stage.value} 不在管道配置中")
        
        # 驗證處理器配置
        if not processor.validate_config():
            raise ValueError(f"處理器 {processor.stage.value} 配置無效")
        
        self.processors[processor.stage] = processor
        
        self.logger.info(
            "註冊處理器",
            stage=processor.stage.value,
            processor_type=type(processor).__name__
        )
    
    async def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """處理單個數據項
        
        Args:
            item: 輸入數據項
            
        Returns:
            Dict[str, Any]: 處理後的數據項
        """
        try:
            # 基本數據清理
            cleaned_item = self._clean_basic_data(item)
            
            # 標準化字段
            standardized_item = self._standardize_fields(cleaned_item)
            
            # 驗證數據
            validated_item = self._validate_data(standardized_item)
            
            return validated_item
            
        except Exception as e:
            self.logger.error(f"處理數據項失敗: {e}")
            # 返回原始數據，標記處理失敗
            item['processing_error'] = str(e)
            return item
    
    def _clean_basic_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """基本數據清理"""
        cleaned = item.copy()
        
        # 清理字符串字段
        for key, value in cleaned.items():
            if isinstance(value, str):
                # 去除多餘空白
                cleaned[key] = value.strip()
                # 移除特殊字符
                if key in ['title', 'company', 'location']:
                    cleaned[key] = ' '.join(cleaned[key].split())
        
        return cleaned
    
    def _standardize_fields(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """標準化字段格式"""
        standardized = item.copy()
        
        # 標準化薪資信息
        if 'salary' in standardized:
            standardized['salary_info'] = self._parse_salary(standardized['salary'])
        
        # 標準化工作類型
        if 'work_type' in standardized:
            standardized['work_type'] = self._standardize_work_type(standardized['work_type'])
        
        # 標準化地點
        if 'location' in standardized:
            standardized['location'] = self._standardize_location(standardized['location'])
        
        return standardized
    
    def _validate_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """驗證數據完整性"""
        validated = item.copy()
        
        # 必填字段檢查
        required_fields = ['title', 'company']
        for field in required_fields:
            if not validated.get(field):
                validated[f'{field}_missing'] = True
        
        # 添加驗證時間戳
        validated['validation_timestamp'] = time.time()
        
        return validated
    
    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """解析薪資信息"""
        import re
        
        salary_info = {
            'original_text': salary_text,
            'min_salary': None,
            'max_salary': None,
            'currency': 'AUD',
            'period': 'yearly'
        }
        
        if not salary_text:
            return salary_info
        
        # 提取數字
        numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
        if numbers:
            if len(numbers) >= 2:
                salary_info['min_salary'] = int(numbers[0])
                salary_info['max_salary'] = int(numbers[1])
            elif len(numbers) == 1:
                salary_info['min_salary'] = int(numbers[0])
        
        # 檢測時間週期
        if any(word in salary_text.lower() for word in ['hour', 'hr', 'hourly']):
            salary_info['period'] = 'hourly'
        elif any(word in salary_text.lower() for word in ['day', 'daily']):
            salary_info['period'] = 'daily'
        elif any(word in salary_text.lower() for word in ['week', 'weekly']):
            salary_info['period'] = 'weekly'
        elif any(word in salary_text.lower() for word in ['month', 'monthly']):
            salary_info['period'] = 'monthly'
        
        return salary_info
    
    def _standardize_work_type(self, work_type: str) -> str:
        """標準化工作類型"""
        if not work_type:
            return 'Unknown'
        
        work_type_lower = work_type.lower()
        
        if any(word in work_type_lower for word in ['full', 'permanent']):
            return 'Full-time'
        elif any(word in work_type_lower for word in ['part']):
            return 'Part-time'
        elif any(word in work_type_lower for word in ['contract', 'temp']):
            return 'Contract'
        elif any(word in work_type_lower for word in ['casual']):
            return 'Casual'
        else:
            return work_type
    
    def _standardize_location(self, location: str) -> str:
        """標準化地點信息"""
        if not location:
            return 'Unknown'
        
        # 移除多餘的州/國家信息
        location = location.replace(', Australia', '').replace(', AU', '')
        
        # 標準化主要城市名稱
        city_mappings = {
            'sydney': 'Sydney',
            'melbourne': 'Melbourne',
            'brisbane': 'Brisbane',
            'perth': 'Perth',
            'adelaide': 'Adelaide',
            'canberra': 'Canberra',
            'darwin': 'Darwin',
            'hobart': 'Hobart'
        }
        
        location_lower = location.lower()
        for key, value in city_mappings.items():
            if key in location_lower:
                return value
        
        return location
    
    async def process_data(self, data: Union[Any, List[Any]]) -> List[ProcessingResult]:
        """處理數據
        
        Args:
            data: 輸入數據（單個或列表）
            
        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        # 確保數據是列表格式
        if not isinstance(data, list):
            data = [data]
        
        self.metrics.total_items = len(data)
        self.metrics.start_time = time.time()
        self.is_running = True
        
        try:
            # 按批次處理數據
            results = []
            for i in range(0, len(data), self.config.batch_size):
                if not self.is_running:
                    break
                
                batch = data[i:i + self.config.batch_size]
                batch_results = await self._process_batch(batch)
                results.extend(batch_results)
                
                # 更新指標
                self._update_metrics(batch_results)
                
                # 檢查點
                if (self.config.checkpoint_interval and 
                    len(results) % self.config.checkpoint_interval == 0):
                    await self._save_checkpoint(results)
                
                # 暫停檢查
                while self.is_paused and self.is_running:
                    await asyncio.sleep(0.1)
            
            self.metrics.end_time = time.time()
            
            self.logger.info(
                "數據處理完成",
                total_items=self.metrics.total_items,
                processed_items=self.metrics.processed_items,
                failed_items=self.metrics.failed_items,
                success_rate=self.metrics.success_rate,
                processing_time=self.metrics.processing_time,
                throughput=self.metrics.throughput
            )
            
            return results
            
        except Exception as e:
            self.logger.error("數據處理失敗", error=str(e))
            raise
        finally:
            self.is_running = False
    
    async def _process_batch(self, batch: List[Any]) -> List[ProcessingResult]:
        """處理數據批次
        
        Args:
            batch: 數據批次
            
        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        current_data = batch
        
        # 按階段順序處理
        for stage in self.config.stages:
            if not self.is_running:
                break
            
            processor = self.processors.get(stage)
            if not processor:
                self.logger.warning(f"未找到階段 {stage.value} 的處理器，跳過")
                continue
            
            stage_start_time = time.time()
            
            try:
                # 處理當前階段
                if self.config.enable_parallel and len(current_data) > 1:
                    stage_results = await self._process_stage_parallel(
                        processor, current_data
                    )
                else:
                    stage_results = await processor.process_batch(current_data)
                
                # 更新階段指標
                stage_time = time.time() - stage_start_time
                self._update_stage_metrics(stage, stage_results, stage_time)
                
                # 準備下一階段的數據
                current_data = [
                    result.data for result in stage_results 
                    if result.status == ProcessingStatus.COMPLETED and result.data
                ]
                
                if not current_data:
                    self.logger.warning(f"階段 {stage.value} 後無有效數據")
                    break
                
            except Exception as e:
                self.logger.error(
                    "階段處理失敗",
                    stage=stage.value,
                    error=str(e)
                )
                # 創建失敗結果
                return [
                    ProcessingResult(
                        status=ProcessingStatus.FAILED,
                        error=f"階段 {stage.value} 失敗: {str(e)}",
                        stage=stage
                    )
                    for _ in batch
                ]
        
        # 創建最終結果
        final_results = []
        for i, original_item in enumerate(batch):
            if i < len(current_data):
                final_results.append(ProcessingResult(
                    status=ProcessingStatus.COMPLETED,
                    data=current_data[i]
                ))
            else:
                final_results.append(ProcessingResult(
                    status=ProcessingStatus.FAILED,
                    error="處理過程中數據丟失"
                ))
        
        return final_results
    
    async def _process_stage_parallel(self, processor: PipelineProcessor, 
                                    data: List[Any]) -> List[ProcessingResult]:
        """並行處理階段
        
        Args:
            processor: 處理器
            data: 數據列表
            
        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        # 創建並行任務
        tasks = []
        for item in data:
            task = asyncio.create_task(processor.process(item))
            tasks.append(task)
        
        # 等待所有任務完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理異常結果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ProcessingResult(
                    status=ProcessingStatus.FAILED,
                    error=str(result),
                    stage=processor.stage
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _update_metrics(self, results: List[ProcessingResult]) -> None:
        """更新處理指標
        
        Args:
            results: 處理結果列表
        """
        for result in results:
            if result.status == ProcessingStatus.COMPLETED:
                self.metrics.processed_items += 1
            elif result.status == ProcessingStatus.FAILED:
                self.metrics.failed_items += 1
            elif result.status == ProcessingStatus.SKIPPED:
                self.metrics.skipped_items += 1
    
    def _update_stage_metrics(self, stage: PipelineStage, 
                            results: List[ProcessingResult], 
                            processing_time: float) -> None:
        """更新階段指標
        
        Args:
            stage: 處理階段
            results: 處理結果列表
            processing_time: 處理時間
        """
        stage_name = stage.value
        
        if stage_name not in self.metrics.stage_metrics:
            self.metrics.stage_metrics[stage_name] = {
                "processed": 0,
                "failed": 0,
                "skipped": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            }
        
        stage_metrics = self.metrics.stage_metrics[stage_name]
        
        for result in results:
            if result.status == ProcessingStatus.COMPLETED:
                stage_metrics["processed"] += 1
            elif result.status == ProcessingStatus.FAILED:
                stage_metrics["failed"] += 1
            elif result.status == ProcessingStatus.SKIPPED:
                stage_metrics["skipped"] += 1
        
        stage_metrics["total_time"] += processing_time
        total_items = (stage_metrics["processed"] + 
                      stage_metrics["failed"] + 
                      stage_metrics["skipped"])
        
        if total_items > 0:
            stage_metrics["avg_time"] = stage_metrics["total_time"] / total_items
    
    async def _save_checkpoint(self, results: List[ProcessingResult]) -> None:
        """保存檢查點
        
        Args:
            results: 當前處理結果
        """
        if not self.config.checkpoint_path:
            return
        
        try:
            checkpoint_path = Path(self.config.checkpoint_path)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            
            checkpoint_data = {
                "pipeline_name": self.config.name,
                "timestamp": time.time(),
                "metrics": {
                    "total_items": self.metrics.total_items,
                    "processed_items": self.metrics.processed_items,
                    "failed_items": self.metrics.failed_items,
                    "skipped_items": self.metrics.skipped_items
                },
                "results_count": len(results)
            }
            
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(
                "保存檢查點",
                path=str(checkpoint_path),
                processed_items=self.metrics.processed_items
            )
            
        except Exception as e:
            self.logger.warning("保存檢查點失敗", error=str(e))
    
    async def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """加載檢查點
        
        Returns:
            Optional[Dict[str, Any]]: 檢查點數據
        """
        if not self.config.checkpoint_path:
            return None
        
        try:
            checkpoint_path = Path(self.config.checkpoint_path)
            if not checkpoint_path.exists():
                return None
            
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            self.logger.info(
                "加載檢查點",
                path=str(checkpoint_path),
                timestamp=checkpoint_data.get("timestamp")
            )
            
            return checkpoint_data
            
        except Exception as e:
            self.logger.warning("加載檢查點失敗", error=str(e))
            return None
    
    def pause(self) -> None:
        """暫停管道"""
        self.is_paused = True
        self.logger.info("管道已暫停")
    
    def resume(self) -> None:
        """恢復管道"""
        self.is_paused = False
        self.logger.info("管道已恢復")
    
    def stop(self) -> None:
        """停止管道"""
        self.is_running = False
        self.is_paused = False
        self.logger.info("管道已停止")
    
    def get_metrics(self) -> ProcessingMetrics:
        """獲取處理指標
        
        Returns:
            ProcessingMetrics: 處理指標
        """
        return self.metrics
    
    def reset_metrics(self) -> None:
        """重置處理指標"""
        self.metrics = ProcessingMetrics()
        self.logger.debug("處理指標已重置")
    
    async def cleanup(self) -> None:
        """清理資源"""
        try:
            self.stop()
            
            # 關閉線程池
            self.executor.shutdown(wait=True)
            
            # 清理處理器
            for processor in self.processors.values():
                if hasattr(processor, 'cleanup'):
                    await processor.cleanup()
            
            self.logger.info("管道資源清理完成")
            
        except Exception as e:
            self.logger.error("清理資源失敗", error=str(e))
    
    def __del__(self):
        """析構函數"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
        except:
            pass