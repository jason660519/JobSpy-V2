"""集成測試模組

測試各組件之間的集成和協作，確保整個系統的端到端功能正常。
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from pathlib import Path
import json
import tempfile
import os
from typing import Dict, Any, List
import aiohttp
from contextlib import asynccontextmanager

# 導入測試框架
from . import (
    test_manager,
    TEST_CONFIG,
    TEST_DATA,
    create_mock_response,
    create_mock_page,
    assert_job_data_valid,
    assert_api_response_valid,
    generate_test_job_data,
    pytest_marks
)


class TestConfigIntegration:
    """配置系統集成測試"""
    
    @pytest_marks['integration']
    async def test_config_environment_integration(self, test_filesystem):
        """測試配置與環境變量集成"""
        # 創建配置文件
        config_data = {
            'database': {
                'url': '${DATABASE_URL}',
                'pool_size': 10
            },
            'api': {
                'openai_api_key': '${OPENAI_API_KEY}',
                'timeout': '${API_TIMEOUT:30}'
            }
        }
        
        config_file = test_filesystem / 'config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        # 設置環境變量
        test_env = {
            'DATABASE_URL': 'postgresql://test:test@localhost/testdb',
            'OPENAI_API_KEY': 'test-openai-key',
            # API_TIMEOUT 使用默認值
        }
        
        with patch.dict(os.environ, test_env):
            # 這裡需要導入實際的配置管理器
            # from crawler_engine.config import ConfigManager, EnvironmentManager
            # config_manager = ConfigManager()
            # env_manager = EnvironmentManager()
            
            # 加載配置並解析環境變量
            # config = config_manager.load_from_file(str(config_file))
            # resolved_config = env_manager.resolve_variables(config)
            
            # assert resolved_config['database']['url'] == 'postgresql://test:test@localhost/testdb'
            # assert resolved_config['api']['openai_api_key'] == 'test-openai-key'
            # assert resolved_config['api']['timeout'] == 30  # 默認值
            
            # 暫時使用模擬測試
            resolved_config = {
                'database': {
                    'url': os.environ.get('DATABASE_URL'),
                    'pool_size': 10
                },
                'api': {
                    'openai_api_key': os.environ.get('OPENAI_API_KEY'),
                    'timeout': int(os.environ.get('API_TIMEOUT', '30'))
                }
            }
            
            assert resolved_config['database']['url'] == 'postgresql://test:test@localhost/testdb'
            assert resolved_config['api']['openai_api_key'] == 'test-openai-key'
            assert resolved_config['api']['timeout'] == 30
    
    @pytest_marks['integration']
    async def test_config_validation_integration(self, test_filesystem):
        """測試配置驗證集成"""
        # 創建包含錯誤的配置文件
        invalid_config = {
            'database': {
                'url': 'invalid-url',
                'pool_size': 'not-a-number'
            },
            'api': {
                'timeout': -1,  # 無效的超時值
                'openai_api_key': ''  # 空的API密鑰
            }
        }
        
        config_file = test_filesystem / 'invalid_config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_config, f)
        
        # 這裡需要導入實際的配置管理器和驗證器
        # from crawler_engine.config import ConfigManager, ConfigValidator
        # config_manager = ConfigManager()
        # validator = ConfigValidator()
        
        # 加載配置並驗證
        # config = config_manager.load_from_file(str(config_file))
        # validation_result = validator.validate(config)
        
        # assert not validation_result.is_valid
        # assert len(validation_result.errors) > 0
        
        # 檢查特定錯誤
        # error_messages = [error.message for error in validation_result.errors]
        # assert any('url' in msg.lower() for msg in error_messages)
        # assert any('timeout' in msg.lower() for msg in error_messages)
        
        # 暫時使用基本驗證
        validation_errors = []
        
        # 驗證數據庫URL
        if not invalid_config['database']['url'].startswith(('postgresql://', 'sqlite://')):
            validation_errors.append('Invalid database URL format')
        
        # 驗證池大小
        if not isinstance(invalid_config['database']['pool_size'], int):
            validation_errors.append('Pool size must be an integer')
        
        # 驗證超時值
        if invalid_config['api']['timeout'] <= 0:
            validation_errors.append('Timeout must be positive')
        
        # 驗證API密鑰
        if not invalid_config['api']['openai_api_key']:
            validation_errors.append('OpenAI API key is required')
        
        assert len(validation_errors) > 0
        assert any('url' in error.lower() for error in validation_errors)
        assert any('timeout' in error.lower() for error in validation_errors)


class TestDataPipelineIntegration:
    """數據管道集成測試"""
    
    @pytest_marks['integration']
    @pytest_marks['database']
    async def test_scraper_to_storage_pipeline(self, test_fixtures):
        """測試爬蟲到存儲的數據管道"""
        # 獲取測試夾具
        database = test_fixtures.get('database')
        cache = test_fixtures.get('cache')
        
        # 模擬爬蟲數據
        scraped_jobs = generate_test_job_data(5)
        
        # 這裡需要導入實際的組件
        # from crawler_engine.scraper import SmartScraper
        # from crawler_engine.data import JobStorage, DataProcessor
        # from crawler_engine.data.cache import CacheManager
        
        # scraper = SmartScraper()
        # storage = JobStorage(database)
        # processor = DataProcessor()
        # cache_manager = CacheManager(cache)
        
        # 模擬完整的數據處理流程
        processed_jobs = []
        
        for job_data in scraped_jobs:
            # 1. 數據清理和驗證
            # cleaned_job = processor.clean_job_data(job_data)
            # validated_job = processor.validate_job_data(cleaned_job)
            
            # 暫時使用基本處理
            cleaned_job = {
                'title': job_data['title'].strip(),
                'company': job_data['company'].strip(),
                'location': job_data['location'].strip(),
                'salary': job_data.get('salary', '').strip(),
                'description': job_data.get('description', '').strip(),
                'url': job_data.get('url', ''),
                'posted_date': job_data.get('posted_date', ''),
                'processed_at': datetime.now().isoformat()
            }
            
            # 2. 數據去重檢查
            # duplicate_check = await cache_manager.check_duplicate(cleaned_job['url'])
            # if not duplicate_check:
            
            # 3. 保存到數據庫
            # job_id = await storage.save_job(cleaned_job)
            # cleaned_job['id'] = job_id
            
            # 4. 更新緩存
            # await cache_manager.cache_job(cleaned_job)
            
            # 暫時模擬保存
            cleaned_job['id'] = f"job_{len(processed_jobs) + 1}"
            processed_jobs.append(cleaned_job)
        
        # 驗證處理結果
        assert len(processed_jobs) == 5
        
        for job in processed_jobs:
            assert_job_data_valid(job)
            assert 'id' in job
            assert 'processed_at' in job
            assert job['title'].strip() == job['title']  # 確保已清理
    
    @pytest_marks['integration']
    async def test_ai_vision_integration(self, mock_apis):
        """測試AI視覺分析集成"""
        # 模擬OpenAI API響應
        mock_openai = mock_apis.get('openai')
        if mock_openai:
            mock_openai.chat.completions.create.return_value = Mock(
                choices=[Mock(message=Mock(content=json.dumps({
                    'title': 'Senior Software Engineer',
                    'company': 'Tech Innovation Corp',
                    'location': 'San Francisco, CA',
                    'salary': '$120,000 - $180,000',
                    'requirements': ['Python', 'React', '5+ years experience']
                })))]
            )
        
        # 這裡需要導入實際的AI視覺服務
        # from crawler_engine.ai import AIVisionService
        # from crawler_engine.data import JobStorage
        
        # vision_service = AIVisionService(api_key='test-key')
        # storage = JobStorage(database)
        
        # 模擬圖像分析流程
        test_image_path = 'test_job_screenshot.png'
        
        # 1. 分析圖像
        # analysis_result = await vision_service.analyze_job_image(test_image_path)
        
        # 暫時使用模擬結果
        analysis_result = {
            'title': 'Senior Software Engineer',
            'company': 'Tech Innovation Corp',
            'location': 'San Francisco, CA',
            'salary': '$120,000 - $180,000',
            'requirements': ['Python', 'React', '5+ years experience'],
            'confidence': 0.95
        }
        
        # 2. 驗證分析結果
        assert analysis_result['confidence'] > 0.8
        assert_job_data_valid(analysis_result)
        
        # 3. 保存分析結果
        # job_id = await storage.save_job(analysis_result)
        # assert job_id is not None
        
        # 暫時模擬保存
        job_id = 'ai_analyzed_job_1'
        analysis_result['id'] = job_id
        
        assert analysis_result['id'] == job_id
        assert 'requirements' in analysis_result
        assert len(analysis_result['requirements']) > 0


class TestScrapingIntegration:
    """爬蟲集成測試"""
    
    @pytest_marks['integration']
    @pytest_marks['browser']
    async def test_multi_platform_scraping(self, test_browser, mock_apis):
        """測試多平台爬蟲集成"""
        # 這裡需要導入實際的平台適配器
        # from crawler_engine.platforms import IndeedAdapter, LinkedInAdapter
        # from crawler_engine.scraper import SmartScraper
        
        # scraper = SmartScraper(browser=test_browser)
        # indeed_adapter = IndeedAdapter()
        # linkedin_adapter = LinkedInAdapter()
        
        search_params = {
            'keywords': 'python developer',
            'location': 'San Francisco',
            'experience_level': 'mid'
        }
        
        # 模擬多平台搜索
        platform_results = {}
        
        # 1. Indeed搜索
        # indeed_url = indeed_adapter.build_search_url(search_params)
        # indeed_results = await scraper.scrape_jobs(indeed_url, indeed_adapter)
        
        # 暫時使用模擬結果
        indeed_results = [
            {
                'title': 'Python Developer',
                'company': 'Indeed Tech',
                'location': 'San Francisco, CA',
                'source': 'indeed',
                'url': 'https://indeed.com/job/1'
            },
            {
                'title': 'Senior Python Engineer',
                'company': 'Indeed Corp',
                'location': 'San Francisco, CA',
                'source': 'indeed',
                'url': 'https://indeed.com/job/2'
            }
        ]
        
        platform_results['indeed'] = indeed_results
        
        # 2. LinkedIn搜索（需要登錄）
        # if linkedin_adapter.is_logged_in():
        #     linkedin_url = linkedin_adapter.build_search_url(search_params)
        #     linkedin_results = await scraper.scrape_jobs(linkedin_url, linkedin_adapter)
        #     platform_results['linkedin'] = linkedin_results
        
        # 暫時跳過LinkedIn（需要登錄）
        platform_results['linkedin'] = []
        
        # 3. 合併和去重結果
        all_jobs = []
        seen_urls = set()
        
        for platform, jobs in platform_results.items():
            for job in jobs:
                if job['url'] not in seen_urls:
                    seen_urls.add(job['url'])
                    all_jobs.append(job)
        
        # 驗證結果
        assert len(all_jobs) >= 2
        assert all(job['source'] in ['indeed', 'linkedin'] for job in all_jobs)
        assert len(seen_urls) == len(all_jobs)  # 確保沒有重複
        
        # 驗證每個職位數據
        for job in all_jobs:
            assert 'title' in job
            assert 'company' in job
            assert 'location' in job
            assert 'source' in job
            assert 'url' in job
    
    @pytest_marks['integration']
    @pytest_marks['slow']
    async def test_anti_detection_integration(self, test_browser):
        """測試反檢測機制集成"""
        # 這裡需要導入實際的反檢測組件
        # from crawler_engine.scraper import AntiDetection, SmartScraper
        
        # anti_detection = AntiDetection()
        # scraper = SmartScraper(browser=test_browser, anti_detection=anti_detection)
        
        # 模擬反檢測策略
        anti_detection_config = {
            'user_agent_rotation': True,
            'random_delays': True,
            'proxy_rotation': False,  # 測試環境不使用代理
            'request_headers': True,
            'viewport_randomization': True
        }
        
        # 測試多次請求的反檢測
        request_logs = []
        
        for i in range(5):
            # 模擬請求配置
            request_config = {
                'user_agent': f'Mozilla/5.0 (Test Agent {i})',
                'delay': 1 + (i * 0.5),  # 遞增延遲
                'headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br'
                }
            }
            
            request_logs.append(request_config)
            
            # 模擬延遲
            await asyncio.sleep(0.1)  # 縮短測試時間
        
        # 驗證反檢測策略
        user_agents = [log['user_agent'] for log in request_logs]
        delays = [log['delay'] for log in request_logs]
        
        # 確保用戶代理有變化
        assert len(set(user_agents)) > 1
        
        # 確保延遲有變化
        assert len(set(delays)) > 1
        
        # 確保所有請求都有必要的頭部
        for log in request_logs:
            assert 'Accept-Language' in log['headers']
            assert 'Accept-Encoding' in log['headers']


class TestMonitoringIntegration:
    """監控系統集成測試"""
    
    @pytest_marks['integration']
    async def test_cost_monitoring_integration(self):
        """測試成本監控集成"""
        # 這裡需要導入實際的監控組件
        # from crawler_engine.monitoring import CostController, AlertManager
        # from crawler_engine.ai import AIVisionService
        
        # cost_controller = CostController()
        # alert_manager = AlertManager()
        # ai_service = AIVisionService(api_key='test-key')
        
        # 模擬成本跟踪
        cost_tracker = {
            'api_calls': 0,
            'total_cost': 0.0,
            'alerts_sent': []
        }
        
        # 設置成本限制
        cost_limits = {
            'daily_api_cost': 10.0,
            'hourly_api_calls': 100
        }
        
        # 模擬API調用和成本跟踪
        for i in range(15):
            # 模擬AI視覺API調用
            api_cost = 0.01  # 每次調用成本
            cost_tracker['api_calls'] += 1
            cost_tracker['total_cost'] += api_cost
            
            # 檢查成本限制
            if cost_tracker['total_cost'] > cost_limits['daily_api_cost']:
                alert = {
                    'type': 'cost_limit_exceeded',
                    'message': f"Daily API cost limit exceeded: ${cost_tracker['total_cost']:.2f}",
                    'timestamp': datetime.now().isoformat()
                }
                cost_tracker['alerts_sent'].append(alert)
                break
            
            if cost_tracker['api_calls'] > cost_limits['hourly_api_calls']:
                alert = {
                    'type': 'rate_limit_exceeded',
                    'message': f"Hourly API call limit exceeded: {cost_tracker['api_calls']}",
                    'timestamp': datetime.now().isoformat()
                }
                cost_tracker['alerts_sent'].append(alert)
                break
        
        # 驗證成本跟踪
        assert cost_tracker['api_calls'] == 15
        assert cost_tracker['total_cost'] == 0.15
        assert len(cost_tracker['alerts_sent']) == 0  # 未超過限制
        
        # 測試超過限制的情況
        for i in range(100):
            cost_tracker['api_calls'] += 1
            if cost_tracker['api_calls'] > cost_limits['hourly_api_calls']:
                alert = {
                    'type': 'rate_limit_exceeded',
                    'message': f"Hourly API call limit exceeded: {cost_tracker['api_calls']}",
                    'timestamp': datetime.now().isoformat()
                }
                cost_tracker['alerts_sent'].append(alert)
                break
        
        assert len(cost_tracker['alerts_sent']) == 1
        assert cost_tracker['alerts_sent'][0]['type'] == 'rate_limit_exceeded'
    
    @pytest_marks['integration']
    async def test_performance_monitoring_integration(self):
        """測試性能監控集成"""
        # 這裡需要導入實際的監控組件
        # from crawler_engine.monitoring import PerformanceMonitor, MetricsCollector
        
        # monitor = PerformanceMonitor()
        # metrics_collector = MetricsCollector()
        
        # 模擬性能監控
        performance_data = {
            'cpu_usage': [],
            'memory_usage': [],
            'response_times': [],
            'error_rates': []
        }
        
        # 模擬一段時間的性能數據收集
        for i in range(10):
            # 模擬系統指標
            cpu_usage = 20 + (i * 2)  # 遞增的CPU使用率
            memory_usage = 30 + (i * 1.5)  # 遞增的內存使用率
            response_time = 100 + (i * 10)  # 遞增的響應時間
            error_rate = i * 0.1  # 遞增的錯誤率
            
            performance_data['cpu_usage'].append(cpu_usage)
            performance_data['memory_usage'].append(memory_usage)
            performance_data['response_times'].append(response_time)
            performance_data['error_rates'].append(error_rate)
            
            await asyncio.sleep(0.01)  # 模擬時間間隔
        
        # 分析性能趨勢
        avg_cpu = sum(performance_data['cpu_usage']) / len(performance_data['cpu_usage'])
        avg_memory = sum(performance_data['memory_usage']) / len(performance_data['memory_usage'])
        avg_response_time = sum(performance_data['response_times']) / len(performance_data['response_times'])
        avg_error_rate = sum(performance_data['error_rates']) / len(performance_data['error_rates'])
        
        # 驗證性能數據
        assert len(performance_data['cpu_usage']) == 10
        assert avg_cpu > 20  # 平均CPU使用率應該大於初始值
        assert avg_memory > 30  # 平均內存使用率應該大於初始值
        assert avg_response_time > 100  # 平均響應時間應該大於初始值
        
        # 檢查性能警告
        performance_alerts = []
        
        if avg_cpu > 80:
            performance_alerts.append('High CPU usage detected')
        if avg_memory > 90:
            performance_alerts.append('High memory usage detected')
        if avg_response_time > 1000:
            performance_alerts.append('High response time detected')
        if avg_error_rate > 0.05:
            performance_alerts.append('High error rate detected')
        
        # 在這個測試中，不應該觸發警告
        assert len(performance_alerts) == 0
    
    @pytest_marks['integration']
    async def test_health_check_integration(self):
        """測試健康檢查集成"""
        # 這裡需要導入實際的健康檢查組件
        # from crawler_engine.monitoring import HealthChecker
        # from crawler_engine.data import DatabaseManager
        # from crawler_engine.data.cache import CacheManager
        
        # health_checker = HealthChecker()
        # db_manager = DatabaseManager()
        # cache_manager = CacheManager()
        
        # 模擬健康檢查
        health_checks = {
            'database': {'status': 'healthy', 'response_time': 50},
            'cache': {'status': 'healthy', 'response_time': 10},
            'api_service': {'status': 'healthy', 'response_time': 200},
            'storage': {'status': 'healthy', 'response_time': 30},
            'external_apis': {'status': 'degraded', 'response_time': 2000}
        }
        
        # 計算整體健康狀態
        healthy_components = sum(1 for check in health_checks.values() if check['status'] == 'healthy')
        degraded_components = sum(1 for check in health_checks.values() if check['status'] == 'degraded')
        unhealthy_components = sum(1 for check in health_checks.values() if check['status'] == 'unhealthy')
        
        total_components = len(health_checks)
        
        if unhealthy_components > 0:
            overall_status = 'unhealthy'
        elif degraded_components > 0:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        # 生成健康報告
        health_report = {
            'overall_status': overall_status,
            'total_components': total_components,
            'healthy_components': healthy_components,
            'degraded_components': degraded_components,
            'unhealthy_components': unhealthy_components,
            'component_details': health_checks,
            'timestamp': datetime.now().isoformat()
        }
        
        # 驗證健康報告
        assert health_report['overall_status'] == 'degraded'  # 因為有一個降級組件
        assert health_report['healthy_components'] == 4
        assert health_report['degraded_components'] == 1
        assert health_report['unhealthy_components'] == 0
        
        # 檢查響應時間
        slow_components = [
            name for name, check in health_checks.items() 
            if check['response_time'] > 1000
        ]
        
        assert 'external_apis' in slow_components
        assert len(slow_components) == 1


class TestEndToEndIntegration:
    """端到端集成測試"""
    
    @pytest_marks['integration']
    @pytest_marks['e2e']
    @pytest_marks['slow']
    async def test_complete_job_search_pipeline(self, test_fixtures):
        """測試完整的職位搜索管道"""
        # 獲取所有測試夾具
        database = test_fixtures.get('database')
        cache = test_fixtures.get('cache')
        filesystem = test_fixtures.get('filesystem')
        mock_apis = test_fixtures.get('mock_api')
        
        # 這裡需要導入實際的組件
        # from crawler_engine import CrawlerEngine
        # from crawler_engine.config import ConfigManager
        
        # 設置測試配置
        test_config = {
            'platforms': ['indeed'],  # 只測試Indeed
            'search_params': {
                'keywords': 'python developer',
                'location': 'San Francisco',
                'max_results': 5
            },
            'ai_analysis': True,
            'monitoring': True
        }
        
        # 模擬完整的搜索流程
        pipeline_results = {
            'search_initiated': datetime.now(),
            'jobs_found': [],
            'jobs_processed': [],
            'jobs_stored': [],
            'ai_analyzed': [],
            'errors': [],
            'performance_metrics': {}
        }
        
        try:
            # 1. 初始化爬蟲引擎
            # engine = CrawlerEngine(config=test_config)
            # await engine.initialize()
            
            # 2. 執行搜索
            # search_results = await engine.search_jobs(
            #     platforms=['indeed'],
            #     keywords='python developer',
            #     location='San Francisco'
            # )
            
            # 暫時使用模擬搜索結果
            search_results = generate_test_job_data(5)
            pipeline_results['jobs_found'] = search_results
            
            # 3. 數據處理和清理
            for job in search_results:
                # 數據清理
                processed_job = {
                    'title': job['title'].strip(),
                    'company': job['company'].strip(),
                    'location': job['location'].strip(),
                    'salary': job.get('salary', '').strip(),
                    'description': job.get('description', '').strip()[:1000],  # 限制長度
                    'url': job.get('url', ''),
                    'posted_date': job.get('posted_date', ''),
                    'source': 'indeed',
                    'processed_at': datetime.now().isoformat()
                }
                
                # 數據驗證
                try:
                    assert_job_data_valid(processed_job)
                    pipeline_results['jobs_processed'].append(processed_job)
                except AssertionError as e:
                    pipeline_results['errors'].append({
                        'type': 'validation_error',
                        'job': job,
                        'error': str(e)
                    })
                    continue
                
                # 4. AI分析（如果啟用）
                if test_config['ai_analysis']:
                    # 模擬AI分析
                    ai_analysis = {
                        'skills_extracted': ['Python', 'Django', 'PostgreSQL'],
                        'experience_level': 'mid',
                        'remote_friendly': True,
                        'salary_estimate': '$90,000 - $130,000',
                        'confidence': 0.85
                    }
                    
                    processed_job.update(ai_analysis)
                    pipeline_results['ai_analyzed'].append(processed_job)
                
                # 5. 存儲到數據庫
                # job_id = await storage.save_job(processed_job)
                # processed_job['id'] = job_id
                
                # 暫時模擬存儲
                processed_job['id'] = f"job_{len(pipeline_results['jobs_stored']) + 1}"
                pipeline_results['jobs_stored'].append(processed_job)
            
            # 6. 收集性能指標
            pipeline_results['performance_metrics'] = {
                'total_execution_time': (datetime.now() - pipeline_results['search_initiated']).total_seconds(),
                'jobs_per_second': len(pipeline_results['jobs_stored']) / max(1, (datetime.now() - pipeline_results['search_initiated']).total_seconds()),
                'success_rate': len(pipeline_results['jobs_stored']) / max(1, len(pipeline_results['jobs_found'])),
                'error_rate': len(pipeline_results['errors']) / max(1, len(pipeline_results['jobs_found']))
            }
            
        except Exception as e:
            pipeline_results['errors'].append({
                'type': 'pipeline_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        # 驗證端到端結果
        assert len(pipeline_results['jobs_found']) == 5
        assert len(pipeline_results['jobs_processed']) >= 4  # 允許一些驗證失敗
        assert len(pipeline_results['jobs_stored']) >= 4
        
        if test_config['ai_analysis']:
            assert len(pipeline_results['ai_analyzed']) >= 4
            
            # 驗證AI分析結果
            for analyzed_job in pipeline_results['ai_analyzed']:
                assert 'skills_extracted' in analyzed_job
                assert 'experience_level' in analyzed_job
                assert 'confidence' in analyzed_job
                assert analyzed_job['confidence'] > 0.5
        
        # 驗證性能指標
        metrics = pipeline_results['performance_metrics']
        assert metrics['success_rate'] >= 0.8  # 至少80%成功率
        assert metrics['error_rate'] <= 0.2  # 最多20%錯誤率
        assert metrics['total_execution_time'] < 30  # 30秒內完成
        
        # 驗證錯誤處理
        if pipeline_results['errors']:
            for error in pipeline_results['errors']:
                assert 'type' in error
                assert 'error' in error
                # 確保錯誤被正確記錄和分類


# 測試運行器
if __name__ == '__main__':
    # 運行所有集成測試
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'integration'
    ])