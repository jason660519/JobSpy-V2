#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試工具模組
提供測試過程中需要的各種輔助工具和斷言函數
"""

import asyncio
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from contextlib import contextmanager, asynccontextmanager
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pytest
from datetime import datetime, timedelta
import psutil
import threading
import queue
import logging

class TestTimer:
    """測試計時器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """開始計時"""
        self.start_time = time.time()
    
    def stop(self):
        """停止計時"""
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """獲取經過時間"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class MemoryMonitor:
    """內存監控器"""
    
    def __init__(self):
        self.initial_memory = None
        self.peak_memory = None
        self.final_memory = None
    
    def start(self):
        """開始監控"""
        process = psutil.Process()
        self.initial_memory = process.memory_info().rss
        self.peak_memory = self.initial_memory
    
    def update(self):
        """更新峰值內存"""
        process = psutil.Process()
        current_memory = process.memory_info().rss
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
    
    def stop(self):
        """停止監控"""
        process = psutil.Process()
        self.final_memory = process.memory_info().rss
    
    @property
    def memory_increase(self) -> int:
        """內存增長量（字節）"""
        if self.initial_memory is None or self.final_memory is None:
            return 0
        return self.final_memory - self.initial_memory
    
    @property
    def peak_increase(self) -> int:
        """峰值內存增長量（字節）"""
        if self.initial_memory is None or self.peak_memory is None:
            return 0
        return self.peak_memory - self.initial_memory
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class AsyncTestHelper:
    """異步測試輔助器"""
    
    @staticmethod
    async def wait_for_condition(
        condition: Callable[[], bool],
        timeout: float = 5.0,
        interval: float = 0.1
    ) -> bool:
        """等待條件滿足"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition():
                return True
            await asyncio.sleep(interval)
        return False
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """運行協程並設置超時"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            pytest.fail(f"操作超時 ({timeout}秒)")
    
    @staticmethod
    async def collect_async_results(async_generators: List, max_items: int = 100):
        """收集異步生成器結果"""
        results = []
        for gen in async_generators:
            count = 0
            async for item in gen:
                results.append(item)
                count += 1
                if count >= max_items:
                    break
        return results

class MockFactory:
    """模擬對象工廠"""
    
    @staticmethod
    def create_mock_response(
        status_code: int = 200,
        json_data: Optional[Dict] = None,
        text: Optional[str] = None,
        headers: Optional[Dict] = None
    ) -> Mock:
        """創建模擬HTTP響應"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = headers or {}
        
        if json_data:
            mock_response.json.return_value = json_data
        if text:
            mock_response.text = text
        
        return mock_response
    
    @staticmethod
    def create_async_mock_response(
        status_code: int = 200,
        json_data: Optional[Dict] = None,
        text: Optional[str] = None,
        headers: Optional[Dict] = None
    ) -> AsyncMock:
        """創建異步模擬HTTP響應"""
        mock_response = AsyncMock()
        mock_response.status = status_code
        mock_response.headers = headers or {}
        
        if json_data:
            mock_response.json = AsyncMock(return_value=json_data)
        if text:
            mock_response.text = AsyncMock(return_value=text)
        
        return mock_response
    
    @staticmethod
    def create_mock_database() -> Mock:
        """創建模擬數據庫"""
        mock_db = Mock()
        mock_db.connect = Mock()
        mock_db.disconnect = Mock()
        mock_db.execute = Mock()
        mock_db.fetch_all = Mock(return_value=[])
        mock_db.fetch_one = Mock(return_value=None)
        return mock_db
    
    @staticmethod
    def create_mock_cache() -> Mock:
        """創建模擬緩存"""
        cache_data = {}
        
        def mock_get(key):
            return cache_data.get(key)
        
        def mock_set(key, value, ttl=None):
            cache_data[key] = value
        
        def mock_delete(key):
            cache_data.pop(key, None)
        
        def mock_clear():
            cache_data.clear()
        
        mock_cache = Mock()
        mock_cache.get = Mock(side_effect=mock_get)
        mock_cache.set = Mock(side_effect=mock_set)
        mock_cache.delete = Mock(side_effect=mock_delete)
        mock_cache.clear = Mock(side_effect=mock_clear)
        mock_cache.exists = Mock(side_effect=lambda k: k in cache_data)
        
        return mock_cache
    
    @staticmethod
    def create_mock_browser() -> Mock:
        """創建模擬瀏覽器"""
        mock_browser = Mock()
        mock_browser.new_page = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.screenshot = AsyncMock()
        mock_page.close = AsyncMock()
        
        mock_browser.new_page.return_value = mock_page
        
        return mock_browser, mock_page

class TestAssertions:
    """測試斷言工具"""
    
    @staticmethod
    def assert_job_data_valid(job_data: Dict[str, Any]):
        """斷言職位數據有效"""
        required_fields = ['id', 'title', 'company', 'location']
        for field in required_fields:
            assert field in job_data, f"缺少必需字段: {field}"
            assert job_data[field], f"字段 {field} 不能為空"
        
        # 檢查薪資範圍
        if 'salary_min' in job_data and 'salary_max' in job_data:
            if job_data['salary_min'] and job_data['salary_max']:
                assert job_data['salary_min'] <= job_data['salary_max'], "最低薪資不能大於最高薪資"
    
    @staticmethod
    def assert_api_response_valid(response: Dict[str, Any]):
        """斷言API響應有效"""
        assert 'status' in response, "響應缺少status字段"
        assert response['status'] in ['success', 'error'], "無效的status值"
        
        if response['status'] == 'success':
            assert 'jobs' in response, "成功響應缺少jobs字段"
            assert isinstance(response['jobs'], list), "jobs字段必須是列表"
        else:
            assert 'error' in response, "錯誤響應缺少error字段"
    
    @staticmethod
    def assert_performance_acceptable(
        elapsed_time: float,
        max_time: float,
        operation: str = "操作"
    ):
        """斷言性能可接受"""
        assert elapsed_time <= max_time, f"{operation}耗時 {elapsed_time:.2f}秒，超過最大允許時間 {max_time}秒"
    
    @staticmethod
    def assert_memory_usage_reasonable(
        memory_increase: int,
        max_increase: int,
        operation: str = "操作"
    ):
        """斷言內存使用合理"""
        memory_mb = memory_increase / 1024 / 1024
        max_mb = max_increase / 1024 / 1024
        assert memory_increase <= max_increase, f"{operation}內存增長 {memory_mb:.2f}MB，超過最大允許 {max_mb:.2f}MB"
    
    @staticmethod
    def assert_error_handling(func: Callable, expected_exception: type, *args, **kwargs):
        """斷言錯誤處理"""
        with pytest.raises(expected_exception):
            func(*args, **kwargs)
    
    @staticmethod
    def assert_async_error_handling(coro, expected_exception: type):
        """斷言異步錯誤處理"""
        async def _test():
            with pytest.raises(expected_exception):
                await coro
        
        return _test()

class FileTestHelper:
    """文件測試輔助器"""
    
    @staticmethod
    @contextmanager
    def temporary_directory():
        """創建臨時目錄"""
        temp_dir = tempfile.mkdtemp()
        try:
            yield Path(temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    @contextmanager
    def temporary_file(content: str = "", suffix: str = ".txt"):
        """創建臨時文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            yield temp_path
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    @staticmethod
    def create_test_config_file(config_data: Dict[str, Any], file_path: Path):
        """創建測試配置文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    
    @staticmethod
    def compare_files(file1: Path, file2: Path) -> bool:
        """比較兩個文件是否相同"""
        if not file1.exists() or not file2.exists():
            return False
        
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            return f1.read() == f2.read()

class LogCapture:
    """日誌捕獲器"""
    
    def __init__(self, logger_name: str = None, level: int = logging.DEBUG):
        self.logger_name = logger_name
        self.level = level
        self.records = []
        self.handler = None
    
    def start(self):
        """開始捕獲日誌"""
        logger = logging.getLogger(self.logger_name)
        
        class ListHandler(logging.Handler):
            def __init__(self, records_list):
                super().__init__()
                self.records_list = records_list
            
            def emit(self, record):
                self.records_list.append(record)
        
        self.handler = ListHandler(self.records)
        self.handler.setLevel(self.level)
        logger.addHandler(self.handler)
        
        return self
    
    def stop(self):
        """停止捕獲日誌"""
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
    
    def get_messages(self, level: int = None) -> List[str]:
        """獲取日誌消息"""
        if level is None:
            return [record.getMessage() for record in self.records]
        return [record.getMessage() for record in self.records if record.levelno >= level]
    
    def has_message(self, message: str, level: int = None) -> bool:
        """檢查是否包含特定消息"""
        messages = self.get_messages(level)
        return any(message in msg for msg in messages)
    
    def clear(self):
        """清空記錄"""
        self.records.clear()
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class ConcurrencyTestHelper:
    """並發測試輔助器"""
    
    @staticmethod
    def run_concurrent_tasks(tasks: List[Callable], max_workers: int = 10) -> List[Any]:
        """運行並發任務"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(task) for task in tasks]
            results = []
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(e)
            
            return results
    
    @staticmethod
    async def run_concurrent_async_tasks(tasks: List[Callable], semaphore_limit: int = 10) -> List[Any]:
        """運行並發異步任務"""
        semaphore = asyncio.Semaphore(semaphore_limit)
        
        async def run_with_semaphore(task):
            async with semaphore:
                return await task()
        
        return await asyncio.gather(*[run_with_semaphore(task) for task in tasks], return_exceptions=True)
    
    @staticmethod
    def stress_test(func: Callable, iterations: int = 100, max_workers: int = 10) -> Dict[str, Any]:
        """壓力測試"""
        start_time = time.time()
        
        tasks = [func for _ in range(iterations)]
        results = ConcurrencyTestHelper.run_concurrent_tasks(tasks, max_workers)
        
        end_time = time.time()
        
        # 統計結果
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        return {
            'total_iterations': iterations,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / iterations,
            'total_time': end_time - start_time,
            'avg_time_per_iteration': (end_time - start_time) / iterations,
            'errors': [r for r in results if isinstance(r, Exception)]
        }

# 便捷函數
def measure_time(func: Callable, *args, **kwargs) -> tuple:
    """測量函數執行時間"""
    with TestTimer() as timer:
        result = func(*args, **kwargs)
    return result, timer.elapsed

async def measure_async_time(coro) -> tuple:
    """測量異步函數執行時間"""
    with TestTimer() as timer:
        result = await coro
    return result, timer.elapsed

def measure_memory(func: Callable, *args, **kwargs) -> tuple:
    """測量函數內存使用"""
    with MemoryMonitor() as monitor:
        result = func(*args, **kwargs)
    return result, monitor.memory_increase

def create_test_environment() -> Dict[str, Any]:
    """創建測試環境"""
    return {
        'timer': TestTimer(),
        'memory_monitor': MemoryMonitor(),
        'mock_factory': MockFactory(),
        'assertions': TestAssertions(),
        'file_helper': FileTestHelper(),
        'async_helper': AsyncTestHelper(),
        'concurrency_helper': ConcurrencyTestHelper()
    }

# 裝飾器
def timeout(seconds: float):
    """測試超時裝飾器"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                return await AsyncTestHelper.run_with_timeout(func(*args, **kwargs), seconds)
            return wrapper
        else:
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"測試超時 ({seconds}秒)")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(seconds))
                
                try:
                    return func(*args, **kwargs)
                finally:
                    signal.alarm(0)
            
            return wrapper
    return decorator

def retry(max_attempts: int = 3, delay: float = 1.0):
    """重試裝飾器"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def wrapper(*args, **kwargs):
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise
                        await asyncio.sleep(delay)
                return None
            return wrapper
        else:
            def wrapper(*args, **kwargs):
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise
                        time.sleep(delay)
                return None
            return wrapper
    return decorator

if __name__ == "__main__":
    # 示例用法
    print("測試工具模組已加載")
    
    # 測試計時器
    with TestTimer() as timer:
        time.sleep(0.1)
    print(f"計時器測試: {timer.elapsed:.3f}秒")
    
    # 測試內存監控
    with MemoryMonitor() as monitor:
        data = [i for i in range(10000)]
    print(f"內存監控測試: {monitor.memory_increase} 字節")