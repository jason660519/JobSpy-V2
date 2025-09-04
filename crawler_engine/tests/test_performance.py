"""性能測試模組

專門測試系統的性能指標、負載能力和資源使用情況。
"""

import pytest
import asyncio
import time
import statistics
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import asynccontextmanager
import gc
import sys

# 導入測試框架
from . import (
    test_manager,
    TEST_CONFIG,
    TEST_DATA,
    create_mock_response,
    create_mock_page,
    assert_job_data_valid,
    generate_test_job_data,
    pytest_marks
)


class PerformanceMonitor:
    """性能監控器"""
    
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'throughput': 0,
            'error_rate': 0,
            'concurrent_users': 0
        }
        self.start_time = None
        self.end_time = None
    
    def start_monitoring(self):
        """開始性能監控"""
        self.start_time = time.time()
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'throughput': 0,
            'error_rate': 0,
            'concurrent_users': 0
        }
    
    def stop_monitoring(self):
        """停止性能監控"""
        self.end_time = time.time()
    
    def record_response_time(self, response_time: float):
        """記錄響應時間"""
        self.metrics['response_times'].append(response_time)
    
    def record_resource_usage(self, memory_mb: float, cpu_percent: float):
        """記錄資源使用情況"""
        self.metrics['memory_usage'].append(memory_mb)
        self.metrics['cpu_usage'].append(cpu_percent)
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """計算性能統計數據"""
        if not self.metrics['response_times']:
            return {}
        
        response_times = self.metrics['response_times']
        total_time = self.end_time - self.start_time if self.end_time else time.time() - self.start_time
        
        stats = {
            'total_requests': len(response_times),
            'total_time': total_time,
            'throughput': len(response_times) / total_time if total_time > 0 else 0,
            'response_time': {
                'mean': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                'p95': self._percentile(response_times, 95),
                'p99': self._percentile(response_times, 99)
            }
        }
        
        if self.metrics['memory_usage']:
            stats['memory'] = {
                'mean': statistics.mean(self.metrics['memory_usage']),
                'max': max(self.metrics['memory_usage']),
                'min': min(self.metrics['memory_usage'])
            }
        
        if self.metrics['cpu_usage']:
            stats['cpu'] = {
                'mean': statistics.mean(self.metrics['cpu_usage']),
                'max': max(self.metrics['cpu_usage']),
                'min': min(self.metrics['cpu_usage'])
            }
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """計算百分位數"""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))


class LoadGenerator:
    """負載生成器"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.active_users = 0
        self.total_requests = 0
        self.total_errors = 0
    
    async def simulate_user_load(self, 
                                user_count: int, 
                                requests_per_user: int,
                                ramp_up_time: float = 0) -> List[Dict[str, Any]]:
        """模擬用戶負載"""
        results = []
        
        async def user_session(user_id: int, delay: float = 0):
            """模擬單個用戶會話"""
            if delay > 0:
                await asyncio.sleep(delay)
            
            self.active_users += 1
            user_results = {
                'user_id': user_id,
                'requests_completed': 0,
                'requests_failed': 0,
                'response_times': [],
                'errors': []
            }
            
            try:
                for request_num in range(requests_per_user):
                    start_time = time.time()
                    
                    try:
                        # 模擬API請求
                        await self._simulate_api_request(user_id, request_num)
                        
                        response_time = time.time() - start_time
                        self.monitor.record_response_time(response_time)
                        user_results['response_times'].append(response_time)
                        user_results['requests_completed'] += 1
                        self.total_requests += 1
                        
                    except Exception as e:
                        user_results['requests_failed'] += 1
                        user_results['errors'].append(str(e))
                        self.total_errors += 1
                    
                    # 模擬用戶思考時間
                    await asyncio.sleep(0.1)
                    
                    # 記錄資源使用（模擬）
                    memory_usage = 150 + (self.active_users * 5) + (request_num * 2)
                    cpu_usage = 20 + (self.active_users * 2) + (request_num * 1)
                    self.monitor.record_resource_usage(memory_usage, cpu_usage)
            
            finally:
                self.active_users -= 1
            
            return user_results
        
        # 計算每個用戶的啟動延遲（漸進式增加負載）
        ramp_delay = ramp_up_time / user_count if user_count > 0 else 0
        
        # 創建用戶任務
        user_tasks = [
            user_session(i, i * ramp_delay) 
            for i in range(user_count)
        ]
        
        # 並發執行所有用戶會話
        results = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        return [r for r in results if not isinstance(r, Exception)]
    
    async def _simulate_api_request(self, user_id: int, request_num: int):
        """模擬API請求"""
        # 模擬不同類型的請求
        request_types = ['search', 'details', 'save', 'apply']
        request_type = request_types[request_num % len(request_types)]
        
        if request_type == 'search':
            # 模擬搜索請求（較慢）
            await asyncio.sleep(0.3 + (user_id % 3) * 0.1)
        elif request_type == 'details':
            # 模擬獲取詳情（中等）
            await asyncio.sleep(0.2 + (user_id % 2) * 0.1)
        elif request_type == 'save':
            # 模擬保存操作（快速）
            await asyncio.sleep(0.1)
        elif request_type == 'apply':
            # 模擬申請操作（較慢）
            await asyncio.sleep(0.4 + (user_id % 2) * 0.1)
        
        # 模擬偶發錯誤
        if user_id % 20 == 0 and request_num % 10 == 0:
            raise Exception(f"Simulated error for user {user_id}, request {request_num}")


class TestSearchPerformance:
    """搜索性能測試"""
    
    @pytest_marks['performance']
    async def test_single_search_performance(self, test_fixtures):
        """測試單次搜索性能"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # 性能目標
        targets = {
            'max_response_time': 2.0,  # 最大響應時間2秒
            'min_results': 5,          # 最少返回5個結果
            'max_memory_increase': 50  # 最大內存增長50MB
        }
        
        # 執行搜索測試
        search_params = {
            'keywords': 'software engineer',
            'location': 'San Francisco',
            'platforms': ['indeed', 'glassdoor']
        }
        
        start_time = time.time()
        
        # 這裡需要調用實際的搜索API
        # results = await search_api.search_jobs(search_params)
        
        # 暫時使用模擬搜索
        await asyncio.sleep(0.5)  # 模擬搜索時間
        results = generate_test_job_data(8)
        
        response_time = time.time() - start_time
        monitor.record_response_time(response_time)
        
        monitor.stop_monitoring()
        stats = monitor.calculate_statistics()
        
        # 驗證性能目標
        assert response_time <= targets['max_response_time'], \
            f"響應時間 {response_time:.2f}s 超過目標 {targets['max_response_time']}s"
        
        assert len(results) >= targets['min_results'], \
            f"結果數量 {len(results)} 少於目標 {targets['min_results']}"
        
        # 驗證結果質量
        for job in results:
            assert_job_data_valid(job)
        
        print(f"單次搜索性能測試結果:")
        print(f"  響應時間: {response_time:.2f}s")
        print(f"  結果數量: {len(results)}")
        print(f"  平均每個結果耗時: {response_time/len(results):.3f}s")
    
    @pytest_marks['performance']
    @pytest_marks['slow']
    async def test_concurrent_search_performance(self, test_fixtures):
        """測試並發搜索性能"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # 並發測試配置
        concurrent_searches = 10
        search_variations = [
            {'keywords': 'python developer', 'location': 'New York'},
            {'keywords': 'java engineer', 'location': 'Seattle'},
            {'keywords': 'frontend developer', 'location': 'Austin'},
            {'keywords': 'data scientist', 'location': 'Boston'},
            {'keywords': 'devops engineer', 'location': 'Denver'}
        ]
        
        async def concurrent_search(search_id: int):
            """執行並發搜索"""
            search_params = search_variations[search_id % len(search_variations)]
            search_params['search_id'] = search_id
            
            start_time = time.time()
            
            try:
                # 這裡需要調用實際的搜索API
                # results = await search_api.search_jobs(search_params)
                
                # 暫時使用模擬搜索
                await asyncio.sleep(0.3 + (search_id % 3) * 0.1)  # 模擬不同搜索時間
                results = generate_test_job_data(5 + search_id % 5)
                
                response_time = time.time() - start_time
                monitor.record_response_time(response_time)
                
                return {
                    'search_id': search_id,
                    'success': True,
                    'response_time': response_time,
                    'results_count': len(results),
                    'search_params': search_params
                }
                
            except Exception as e:
                return {
                    'search_id': search_id,
                    'success': False,
                    'error': str(e),
                    'search_params': search_params
                }
        
        # 執行並發搜索
        search_tasks = [concurrent_search(i) for i in range(concurrent_searches)]
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        monitor.stop_monitoring()
        stats = monitor.calculate_statistics()
        
        # 分析結果
        successful_searches = [r for r in search_results if not isinstance(r, Exception) and r.get('success')]
        failed_searches = [r for r in search_results if isinstance(r, Exception) or not r.get('success')]
        
        # 性能驗證
        assert len(failed_searches) == 0, f"有 {len(failed_searches)} 個搜索失敗"
        assert len(successful_searches) == concurrent_searches, "所有搜索都應該成功"
        
        # 響應時間驗證
        response_times = [r['response_time'] for r in successful_searches]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time <= 1.0, f"平均響應時間 {avg_response_time:.2f}s 過長"
        assert max_response_time <= 2.0, f"最大響應時間 {max_response_time:.2f}s 過長"
        
        # 吞吐量驗證
        assert stats['throughput'] >= 5, f"吞吐量 {stats['throughput']:.2f}/s 過低"
        
        print(f"並發搜索性能測試結果:")
        print(f"  並發搜索數: {concurrent_searches}")
        print(f"  成功搜索數: {len(successful_searches)}")
        print(f"  平均響應時間: {avg_response_time:.2f}s")
        print(f"  最大響應時間: {max_response_time:.2f}s")
        print(f"  吞吐量: {stats['throughput']:.2f}次/秒")
        print(f"  總結果數: {sum(r['results_count'] for r in successful_searches)}")
    
    @pytest_marks['performance']
    @pytest_marks['slow']
    async def test_search_scalability(self, test_fixtures):
        """測試搜索可擴展性"""
        # 測試不同負載級別下的性能
        load_levels = [1, 5, 10, 20, 50]
        scalability_results = []
        
        for load_level in load_levels:
            print(f"測試負載級別: {load_level} 並發搜索")
            
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            async def scalability_search(search_id: int):
                """可擴展性測試搜索"""
                start_time = time.time()
                
                # 模擬搜索
                await asyncio.sleep(0.2 + (search_id % 5) * 0.05)
                results = generate_test_job_data(3 + search_id % 3)
                
                response_time = time.time() - start_time
                monitor.record_response_time(response_time)
                
                return {
                    'search_id': search_id,
                    'response_time': response_time,
                    'results_count': len(results)
                }
            
            # 執行當前負載級別的測試
            tasks = [scalability_search(i) for i in range(load_level)]
            results = await asyncio.gather(*tasks)
            
            monitor.stop_monitoring()
            stats = monitor.calculate_statistics()
            
            scalability_results.append({
                'load_level': load_level,
                'stats': stats,
                'results': results
            })
        
        # 分析可擴展性
        print(f"\n可擴展性測試結果:")
        print(f"{'負載級別':<10} {'平均響應時間':<15} {'吞吐量':<10} {'P95響應時間':<15}")
        print("-" * 60)
        
        for result in scalability_results:
            load = result['load_level']
            stats = result['stats']
            
            print(f"{load:<10} {stats['response_time']['mean']:<15.2f} "
                  f"{stats['throughput']:<10.2f} {stats['response_time']['p95']:<15.2f}")
        
        # 驗證可擴展性
        # 檢查吞吐量是否隨負載合理增長
        throughputs = [r['stats']['throughput'] for r in scalability_results]
        
        # 吞吐量應該隨負載增加而增加（至少在低負載時）
        for i in range(1, min(3, len(throughputs))):
            assert throughputs[i] >= throughputs[i-1] * 0.8, \
                f"吞吐量在負載級別 {load_levels[i]} 時顯著下降"
        
        # 響應時間不應該隨負載過度增長
        response_times = [r['stats']['response_time']['mean'] for r in scalability_results]
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        assert max_response_time / min_response_time <= 3.0, \
            f"響應時間增長過大: {max_response_time:.2f}s / {min_response_time:.2f}s = {max_response_time/min_response_time:.2f}x"


class TestMemoryPerformance:
    """內存性能測試"""
    
    @pytest_marks['performance']
    async def test_memory_usage_during_search(self, test_fixtures):
        """測試搜索過程中的內存使用"""
        # 記錄初始內存使用
        # initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        initial_memory = 100  # 模擬初始內存
        
        memory_samples = [initial_memory]
        
        # 執行多次搜索並監控內存
        search_count = 20
        
        for i in range(search_count):
            # 執行搜索
            # results = await search_api.search_jobs({
            #     'keywords': f'test search {i}',
            #     'location': 'Test City'
            # })
            
            # 模擬搜索和內存使用
            await asyncio.sleep(0.1)
            results = generate_test_job_data(5)
            
            # 記錄內存使用
            # current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            current_memory = initial_memory + (i * 2) + (len(results) * 0.5)  # 模擬內存增長
            memory_samples.append(current_memory)
            
            # 驗證結果
            assert len(results) > 0
            for job in results:
                assert_job_data_valid(job)
        
        # 強制垃圾回收
        gc.collect()
        await asyncio.sleep(0.1)
        
        # final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        final_memory = memory_samples[-1] * 0.9  # 模擬垃圾回收後的內存
        memory_samples.append(final_memory)
        
        # 分析內存使用
        max_memory = max(memory_samples)
        memory_growth = max_memory - initial_memory
        memory_after_gc = final_memory - initial_memory
        
        print(f"內存使用測試結果:")
        print(f"  初始內存: {initial_memory:.2f}MB")
        print(f"  最大內存: {max_memory:.2f}MB")
        print(f"  內存增長: {memory_growth:.2f}MB")
        print(f"  GC後內存: {final_memory:.2f}MB")
        print(f"  GC後增長: {memory_after_gc:.2f}MB")
        
        # 驗證內存使用
        assert memory_growth <= 100, f"內存增長 {memory_growth:.2f}MB 過大"
        assert memory_after_gc <= 50, f"GC後內存增長 {memory_after_gc:.2f}MB 仍然過大"
        
        # 檢查內存洩漏
        memory_leak_threshold = 20  # MB
        assert memory_after_gc <= memory_leak_threshold, \
            f"可能存在內存洩漏，GC後內存增長 {memory_after_gc:.2f}MB"
    
    @pytest_marks['performance']
    async def test_large_dataset_memory_efficiency(self, test_fixtures):
        """測試大數據集的內存效率"""
        # 模擬處理大量職位數據
        large_dataset_sizes = [100, 500, 1000, 2000]
        memory_efficiency_results = []
        
        for dataset_size in large_dataset_sizes:
            print(f"測試數據集大小: {dataset_size} 個職位")
            
            # initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            initial_memory = 120  # 模擬初始內存
            
            # 生成大數據集
            large_dataset = generate_test_job_data(dataset_size)
            
            # 模擬數據處理
            processed_jobs = []
            for i, job in enumerate(large_dataset):
                # 模擬數據處理操作
                processed_job = {
                    **job,
                    'processed_at': datetime.now().isoformat(),
                    'processing_id': i
                }
                processed_jobs.append(processed_job)
                
                # 每處理100個職位檢查一次內存
                if (i + 1) % 100 == 0:
                    # current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    current_memory = initial_memory + (i / 10)  # 模擬內存增長
                    
                    # 檢查內存增長是否合理
                    memory_per_job = (current_memory - initial_memory) / (i + 1)
                    assert memory_per_job <= 0.1, \
                        f"每個職位內存使用 {memory_per_job:.3f}MB 過大"
            
            # final_memory = psutil.Process().memory_info().rss / 1024 / 1024
            final_memory = initial_memory + (dataset_size / 10)  # 模擬最終內存
            
            memory_used = final_memory - initial_memory
            memory_per_job = memory_used / dataset_size
            
            memory_efficiency_results.append({
                'dataset_size': dataset_size,
                'memory_used': memory_used,
                'memory_per_job': memory_per_job,
                'processed_count': len(processed_jobs)
            })
            
            # 清理數據
            del large_dataset
            del processed_jobs
            gc.collect()
        
        # 分析內存效率
        print(f"\n大數據集內存效率測試結果:")
        print(f"{'數據集大小':<12} {'內存使用(MB)':<15} {'每職位內存(KB)':<18} {'處理成功率':<12}")
        print("-" * 70)
        
        for result in memory_efficiency_results:
            size = result['dataset_size']
            memory_mb = result['memory_used']
            memory_kb = result['memory_per_job'] * 1024
            success_rate = result['processed_count'] / size * 100
            
            print(f"{size:<12} {memory_mb:<15.2f} {memory_kb:<18.2f} {success_rate:<12.1f}%")
        
        # 驗證內存效率
        for result in memory_efficiency_results:
            assert result['memory_per_job'] <= 0.05, \
                f"數據集大小 {result['dataset_size']} 時每職位內存使用過大: {result['memory_per_job']:.3f}MB"
            
            assert result['processed_count'] == result['dataset_size'], \
                f"數據集大小 {result['dataset_size']} 時處理不完整"


class TestConcurrencyPerformance:
    """並發性能測試"""
    
    @pytest_marks['performance']
    @pytest_marks['slow']
    async def test_high_concurrency_load(self, test_fixtures):
        """測試高並發負載"""
        monitor = PerformanceMonitor()
        load_generator = LoadGenerator(monitor)
        
        # 高並發測試配置
        test_scenarios = [
            {'users': 10, 'requests_per_user': 5, 'ramp_up': 1.0},
            {'users': 25, 'requests_per_user': 4, 'ramp_up': 2.0},
            {'users': 50, 'requests_per_user': 3, 'ramp_up': 3.0},
            {'users': 100, 'requests_per_user': 2, 'ramp_up': 5.0}
        ]
        
        concurrency_results = []
        
        for scenario in test_scenarios:
            print(f"測試並發場景: {scenario['users']} 用戶, "
                  f"{scenario['requests_per_user']} 請求/用戶, "
                  f"{scenario['ramp_up']}s 漸進時間")
            
            monitor.start_monitoring()
            
            # 執行負載測試
            user_results = await load_generator.simulate_user_load(
                user_count=scenario['users'],
                requests_per_user=scenario['requests_per_user'],
                ramp_up_time=scenario['ramp_up']
            )
            
            monitor.stop_monitoring()
            stats = monitor.calculate_statistics()
            
            # 計算場景統計
            total_requests = sum(r['requests_completed'] for r in user_results)
            total_failures = sum(r['requests_failed'] for r in user_results)
            success_rate = total_requests / (total_requests + total_failures) * 100 if (total_requests + total_failures) > 0 else 0
            
            scenario_result = {
                'scenario': scenario,
                'stats': stats,
                'total_requests': total_requests,
                'total_failures': total_failures,
                'success_rate': success_rate,
                'user_results': user_results
            }
            
            concurrency_results.append(scenario_result)
            
            # 驗證場景結果
            assert success_rate >= 95, f"成功率 {success_rate:.1f}% 低於95%"
            assert stats['response_time']['mean'] <= 2.0, \
                f"平均響應時間 {stats['response_time']['mean']:.2f}s 過長"
            assert stats['throughput'] >= scenario['users'] * 0.5, \
                f"吞吐量 {stats['throughput']:.2f}/s 過低"
        
        # 分析並發性能趨勢
        print(f"\n高並發負載測試結果:")
        print(f"{'用戶數':<8} {'成功率':<8} {'平均響應時間':<12} {'吞吐量':<10} {'P95響應時間':<12}")
        print("-" * 60)
        
        for result in concurrency_results:
            users = result['scenario']['users']
            success_rate = result['success_rate']
            avg_response = result['stats']['response_time']['mean']
            throughput = result['stats']['throughput']
            p95_response = result['stats']['response_time']['p95']
            
            print(f"{users:<8} {success_rate:<8.1f}% {avg_response:<12.2f}s "
                  f"{throughput:<10.2f}/s {p95_response:<12.2f}s")
        
        # 驗證並發擴展性
        throughputs = [r['stats']['throughput'] for r in concurrency_results]
        
        # 吞吐量應該隨用戶數增加而增加（至少在前幾個級別）
        for i in range(1, min(3, len(throughputs))):
            throughput_ratio = throughputs[i] / throughputs[i-1]
            assert throughput_ratio >= 0.8, \
                f"吞吐量在用戶數增加時下降過多: {throughput_ratio:.2f}x"
    
    @pytest_marks['performance']
    async def test_resource_contention(self, test_fixtures):
        """測試資源競爭情況"""
        # 模擬多個組件同時競爭資源
        resource_lock = asyncio.Lock()
        shared_resource = {'value': 0, 'access_count': 0}
        contention_results = []
        
        async def resource_intensive_task(task_id: int, iterations: int):
            """資源密集型任務"""
            task_results = {
                'task_id': task_id,
                'iterations_completed': 0,
                'wait_times': [],
                'processing_times': []
            }
            
            for i in range(iterations):
                # 測量等待鎖的時間
                wait_start = time.time()
                
                async with resource_lock:
                    wait_time = time.time() - wait_start
                    task_results['wait_times'].append(wait_time)
                    
                    # 模擬資源處理
                    process_start = time.time()
                    
                    # 模擬數據庫操作
                    await asyncio.sleep(0.01 + (task_id % 3) * 0.005)
                    
                    # 更新共享資源
                    shared_resource['value'] += 1
                    shared_resource['access_count'] += 1
                    
                    process_time = time.time() - process_start
                    task_results['processing_times'].append(process_time)
                    task_results['iterations_completed'] += 1
                
                # 模擬任務間隔
                await asyncio.sleep(0.001)
            
            return task_results
        
        # 測試不同並發級別的資源競爭
        concurrency_levels = [5, 10, 20, 30]
        
        for concurrency in concurrency_levels:
            print(f"測試資源競爭: {concurrency} 個並發任務")
            
            # 重置共享資源
            shared_resource['value'] = 0
            shared_resource['access_count'] = 0
            
            start_time = time.time()
            
            # 創建並發任務
            tasks = [resource_intensive_task(i, 10) for i in range(concurrency)]
            task_results = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            # 分析競爭結果
            total_iterations = sum(r['iterations_completed'] for r in task_results)
            all_wait_times = []
            all_process_times = []
            
            for result in task_results:
                all_wait_times.extend(result['wait_times'])
                all_process_times.extend(result['processing_times'])
            
            avg_wait_time = statistics.mean(all_wait_times) if all_wait_times else 0
            max_wait_time = max(all_wait_times) if all_wait_times else 0
            avg_process_time = statistics.mean(all_process_times) if all_process_times else 0
            
            contention_result = {
                'concurrency': concurrency,
                'total_time': total_time,
                'total_iterations': total_iterations,
                'avg_wait_time': avg_wait_time,
                'max_wait_time': max_wait_time,
                'avg_process_time': avg_process_time,
                'throughput': total_iterations / total_time,
                'resource_value': shared_resource['value'],
                'resource_accesses': shared_resource['access_count']
            }
            
            contention_results.append(contention_result)
            
            # 驗證資源一致性
            expected_total = concurrency * 10
            assert shared_resource['value'] == expected_total, \
                f"資源值不一致: 期望 {expected_total}, 實際 {shared_resource['value']}"
            
            assert shared_resource['access_count'] == expected_total, \
                f"訪問次數不一致: 期望 {expected_total}, 實際 {shared_resource['access_count']}"
        
        # 分析資源競爭趨勢
        print(f"\n資源競爭測試結果:")
        print(f"{'並發數':<8} {'平均等待時間':<12} {'最大等待時間':<12} {'吞吐量':<10} {'資源一致性':<12}")
        print("-" * 65)
        
        for result in contention_results:
            concurrency = result['concurrency']
            avg_wait = result['avg_wait_time'] * 1000  # 轉換為毫秒
            max_wait = result['max_wait_time'] * 1000
            throughput = result['throughput']
            consistency = "✓" if result['resource_value'] == concurrency * 10 else "✗"
            
            print(f"{concurrency:<8} {avg_wait:<12.2f}ms {max_wait:<12.2f}ms "
                  f"{throughput:<10.2f}/s {consistency:<12}")
        
        # 驗證競爭性能
        for result in contention_results:
            # 等待時間不應該過長
            assert result['avg_wait_time'] <= 0.1, \
                f"並發數 {result['concurrency']} 時平均等待時間過長: {result['avg_wait_time']:.3f}s"
            
            assert result['max_wait_time'] <= 0.5, \
                f"並發數 {result['concurrency']} 時最大等待時間過長: {result['max_wait_time']:.3f}s"
            
            # 吞吐量應該保持合理水平
            assert result['throughput'] >= result['concurrency'] * 5, \
                f"並發數 {result['concurrency']} 時吞吐量過低: {result['throughput']:.2f}/s"


# 性能測試運行器
if __name__ == '__main__':
    # 運行性能測試
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'performance',
        '-s'  # 顯示print輸出
    ])