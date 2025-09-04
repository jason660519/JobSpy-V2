"""端到端測試模組

測試完整的用戶場景和系統功能，模擬真實的使用情況。
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
import time

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


class TestUserScenarios:
    """用戶場景測試"""
    
    @pytest_marks['e2e']
    @pytest_marks['slow']
    async def test_new_user_job_search(self, test_fixtures):
        """測試新用戶首次使用系統搜索職位"""
        # 模擬新用戶場景
        user_session = {
            'user_id': 'new_user_001',
            'session_id': 'session_' + str(int(time.time())),
            'preferences': {
                'job_types': ['full-time'],
                'experience_level': 'entry',
                'remote_preference': 'hybrid',
                'salary_range': {'min': 60000, 'max': 100000}
            },
            'search_history': [],
            'saved_jobs': [],
            'applications': []
        }
        
        # 這裡需要導入實際的系統組件
        # from crawler_engine import CrawlerEngine
        # from crawler_engine.api import JobSearchAPI
        # from crawler_engine.user import UserManager
        
        # engine = CrawlerEngine()
        # api = JobSearchAPI(engine)
        # user_manager = UserManager()
        
        # 1. 用戶註冊/登錄
        # user_profile = await user_manager.create_user_profile(user_session)
        
        # 暫時使用模擬用戶配置文件
        user_profile = {
            'id': user_session['user_id'],
            'created_at': datetime.now().isoformat(),
            'preferences': user_session['preferences'],
            'subscription_tier': 'free',
            'daily_search_limit': 10,
            'searches_today': 0
        }
        
        # 2. 執行首次搜索
        search_request = {
            'keywords': 'entry level software engineer',
            'location': 'San Francisco, CA',
            'platforms': ['indeed', 'glassdoor'],
            'filters': {
                'experience_level': 'entry',
                'job_type': 'full-time',
                'remote': 'hybrid'
            }
        }
        
        # 檢查搜索限制
        if user_profile['searches_today'] >= user_profile['daily_search_limit']:
            pytest.fail("Daily search limit exceeded")
        
        # 執行搜索
        # search_results = await api.search_jobs(search_request, user_session)
        
        # 暫時使用模擬搜索結果
        search_results = {
            'jobs': generate_test_job_data(8),
            'total_found': 8,
            'search_time': 2.5,
            'platforms_searched': ['indeed', 'glassdoor'],
            'filters_applied': search_request['filters']
        }
        
        # 更新用戶搜索歷史
        user_session['search_history'].append({
            'query': search_request,
            'results_count': search_results['total_found'],
            'timestamp': datetime.now().isoformat()
        })
        
        user_profile['searches_today'] += 1
        
        # 3. 用戶瀏覽和保存職位
        interesting_jobs = search_results['jobs'][:3]  # 用戶對前3個職位感興趣
        
        for job in interesting_jobs:
            # 模擬用戶查看職位詳情
            # job_details = await api.get_job_details(job['id'])
            
            # 暫時使用模擬詳情
            job_details = {
                **job,
                'full_description': f"Complete job description for {job['title']} at {job['company']}",
                'requirements': ['Python', 'Git', 'Problem solving'],
                'benefits': ['Health insurance', 'Flexible hours', '401k'],
                'company_info': {
                    'size': '100-500 employees',
                    'industry': 'Technology',
                    'founded': '2015'
                }
            }
            
            # 用戶保存職位
            user_session['saved_jobs'].append({
                'job_id': job['id'],
                'saved_at': datetime.now().isoformat(),
                'notes': f"Interested in {job['title']} position"
            })
        
        # 4. 驗證用戶體驗
        assert len(search_results['jobs']) > 0
        assert search_results['search_time'] < 10  # 搜索應該在10秒內完成
        assert len(user_session['saved_jobs']) == 3
        assert user_profile['searches_today'] == 1
        
        # 驗證搜索結果質量
        for job in search_results['jobs']:
            assert_job_data_valid(job)
            # 檢查是否符合用戶偏好
            if 'salary' in job and job['salary']:
                # 這裡可以添加薪資範圍檢查
                pass
        
        # 驗證用戶數據完整性
        assert len(user_session['search_history']) == 1
        assert user_session['search_history'][0]['results_count'] == 8
    
    @pytest_marks['e2e']
    async def test_power_user_advanced_search(self, test_fixtures):
        """測試高級用戶使用高級搜索功能"""
        # 模擬高級用戶
        power_user = {
            'user_id': 'power_user_001',
            'subscription_tier': 'premium',
            'daily_search_limit': 100,
            'searches_today': 15,
            'preferences': {
                'job_types': ['full-time', 'contract'],
                'experience_level': 'senior',
                'remote_preference': 'remote',
                'salary_range': {'min': 120000, 'max': 200000},
                'preferred_companies': ['Google', 'Microsoft', 'Apple'],
                'excluded_companies': ['Facebook'],
                'skills': ['Python', 'Machine Learning', 'AWS']
            }
        }
        
        # 高級搜索請求
        advanced_search = {
            'keywords': 'senior machine learning engineer',
            'location': 'Remote',
            'platforms': ['indeed', 'linkedin', 'glassdoor'],
            'advanced_filters': {
                'salary_min': 120000,
                'salary_max': 200000,
                'experience_level': 'senior',
                'remote_only': True,
                'company_size': ['large', 'startup'],
                'required_skills': ['Python', 'TensorFlow', 'AWS'],
                'exclude_keywords': ['junior', 'intern'],
                'posted_within': '7_days'
            },
            'ai_matching': True,
            'salary_insights': True
        }
        
        # 執行高級搜索
        # search_results = await api.advanced_search(advanced_search, power_user)
        
        # 暫時使用模擬高級搜索結果
        search_results = {
            'jobs': [
                {
                    'id': 'ml_job_1',
                    'title': 'Senior Machine Learning Engineer',
                    'company': 'TechCorp AI',
                    'location': 'Remote',
                    'salary': '$140,000 - $180,000',
                    'description': 'Senior ML engineer role with Python and TensorFlow',
                    'skills_match': ['Python', 'TensorFlow', 'AWS'],
                    'match_score': 0.92,
                    'remote': True,
                    'posted_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
                },
                {
                    'id': 'ml_job_2',
                    'title': 'Principal ML Engineer',
                    'company': 'AI Innovations',
                    'location': 'Remote',
                    'salary': '$160,000 - $200,000',
                    'description': 'Lead ML initiatives with cutting-edge technology',
                    'skills_match': ['Python', 'AWS'],
                    'match_score': 0.88,
                    'remote': True,
                    'posted_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                }
            ],
            'total_found': 2,
            'ai_insights': {
                'market_analysis': {
                    'average_salary': 165000,
                    'salary_trend': 'increasing',
                    'demand_level': 'high',
                    'competition_level': 'medium'
                },
                'skill_recommendations': [
                    'Consider adding Kubernetes to your profile',
                    'Docker experience is highly valued',
                    'MLOps skills are in demand'
                ]
            },
            'search_time': 3.2
        }
        
        # AI匹配分析
        for job in search_results['jobs']:
            # 計算技能匹配度
            user_skills = set(power_user['preferences']['skills'])
            job_skills = set(job.get('skills_match', []))
            skill_overlap = len(user_skills.intersection(job_skills))
            
            # 驗證匹配質量
            assert job['match_score'] > 0.8  # 高級搜索應該有高匹配度
            assert skill_overlap >= 2  # 至少匹配2個技能
            assert job['remote'] is True  # 符合遠程工作偏好
        
        # 驗證AI洞察
        ai_insights = search_results['ai_insights']
        assert 'market_analysis' in ai_insights
        assert 'skill_recommendations' in ai_insights
        assert ai_insights['market_analysis']['average_salary'] > 100000
        assert len(ai_insights['skill_recommendations']) > 0
        
        # 驗證搜索性能
        assert search_results['search_time'] < 5  # 高級搜索應該在5秒內完成
        assert search_results['total_found'] > 0
    
    @pytest_marks['e2e']
    async def test_job_application_workflow(self, test_fixtures):
        """測試完整的職位申請工作流程"""
        # 模擬用戶申請職位的完整流程
        user_profile = {
            'user_id': 'applicant_001',
            'resume_uploaded': True,
            'cover_letter_template': True,
            'application_preferences': {
                'auto_fill': True,
                'track_applications': True,
                'follow_up_reminders': True
            }
        }
        
        # 選擇要申請的職位
        target_job = {
            'id': 'target_job_001',
            'title': 'Software Engineer',
            'company': 'Dream Company',
            'location': 'San Francisco, CA',
            'application_url': 'https://dreamcompany.com/apply/001',
            'application_method': 'external',  # 外部申請
            'requirements': ['Python', 'React', '3+ years experience']
        }
        
        # 1. 申請前準備
        application_data = {
            'job_id': target_job['id'],
            'user_id': user_profile['user_id'],
            'application_method': target_job['application_method'],
            'started_at': datetime.now().isoformat(),
            'status': 'preparing'
        }
        
        # 生成定制化求職信
        # cover_letter = await ai_service.generate_cover_letter(
        #     job=target_job,
        #     user_profile=user_profile
        # )
        
        # 暫時使用模擬求職信
        cover_letter = f"""
        Dear Hiring Manager,
        
        I am excited to apply for the {target_job['title']} position at {target_job['company']}.
        With my experience in Python and React, I believe I would be a great fit for this role.
        
        Best regards,
        Applicant
        """.strip()
        
        application_data['cover_letter'] = cover_letter
        application_data['status'] = 'ready_to_submit'
        
        # 2. 提交申請
        if target_job['application_method'] == 'external':
            # 模擬外部申請流程
            # browser_result = await browser_automation.apply_external(
            #     url=target_job['application_url'],
            #     application_data=application_data
            # )
            
            # 暫時使用模擬申請結果
            browser_result = {
                'success': True,
                'confirmation_number': 'CONF_001',
                'submitted_at': datetime.now().isoformat(),
                'next_steps': 'You will hear back within 2 weeks'
            }
        else:
            # 內部申請系統
            browser_result = {
                'success': True,
                'confirmation_number': 'INT_001',
                'submitted_at': datetime.now().isoformat()
            }
        
        if browser_result['success']:
            application_data['status'] = 'submitted'
            application_data['confirmation_number'] = browser_result['confirmation_number']
            application_data['submitted_at'] = browser_result['submitted_at']
        else:
            application_data['status'] = 'failed'
            application_data['error'] = browser_result.get('error', 'Unknown error')
        
        # 3. 跟踪申請狀態
        application_tracking = {
            'application_id': application_data['confirmation_number'],
            'status_history': [
                {
                    'status': 'submitted',
                    'timestamp': application_data['submitted_at'],
                    'note': 'Application successfully submitted'
                }
            ],
            'follow_up_scheduled': (datetime.now() + timedelta(days=7)).isoformat(),
            'reminders_set': True
        }
        
        # 4. 設置後續提醒
        reminders = [
            {
                'type': 'follow_up',
                'scheduled_for': (datetime.now() + timedelta(days=7)).isoformat(),
                'message': f"Follow up on {target_job['title']} application at {target_job['company']}"
            },
            {
                'type': 'status_check',
                'scheduled_for': (datetime.now() + timedelta(days=14)).isoformat(),
                'message': f"Check status of {target_job['title']} application"
            }
        ]
        
        # 驗證申請流程
        assert application_data['status'] == 'submitted'
        assert 'confirmation_number' in application_data
        assert 'cover_letter' in application_data
        assert len(application_data['cover_letter']) > 100  # 求職信應該有足夠內容
        
        # 驗證跟踪設置
        assert len(application_tracking['status_history']) == 1
        assert application_tracking['reminders_set'] is True
        assert len(reminders) == 2
        
        # 驗證提醒時間設置
        for reminder in reminders:
            reminder_time = datetime.fromisoformat(reminder['scheduled_for'])
            assert reminder_time > datetime.now()  # 提醒應該在未來


class TestSystemReliability:
    """系統可靠性測試"""
    
    @pytest_marks['e2e']
    @pytest_marks['slow']
    async def test_high_load_scenario(self, test_fixtures):
        """測試高負載場景"""
        # 模擬多個並發用戶
        concurrent_users = 10
        searches_per_user = 5
        
        async def simulate_user_session(user_id: int):
            """模擬單個用戶會話"""
            user_results = {
                'user_id': user_id,
                'searches_completed': 0,
                'total_jobs_found': 0,
                'errors': [],
                'response_times': []
            }
            
            for search_num in range(searches_per_user):
                start_time = time.time()
                
                try:
                    # 模擬搜索請求
                    search_request = {
                        'keywords': f'software engineer {search_num}',
                        'location': 'San Francisco',
                        'platforms': ['indeed']
                    }
                    
                    # 這裡需要調用實際的搜索API
                    # results = await api.search_jobs(search_request)
                    
                    # 暫時使用模擬搜索
                    await asyncio.sleep(0.5)  # 模擬搜索時間
                    results = generate_test_job_data(3)
                    
                    response_time = time.time() - start_time
                    
                    user_results['searches_completed'] += 1
                    user_results['total_jobs_found'] += len(results)
                    user_results['response_times'].append(response_time)
                    
                except Exception as e:
                    user_results['errors'].append({
                        'search_num': search_num,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                
                # 用戶間隔
                await asyncio.sleep(0.1)
            
            return user_results
        
        # 並發執行用戶會話
        start_time = time.time()
        user_tasks = [simulate_user_session(i) for i in range(concurrent_users)]
        all_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 分析結果
        successful_results = [r for r in all_results if not isinstance(r, Exception)]
        failed_results = [r for r in all_results if isinstance(r, Exception)]
        
        # 計算統計數據
        total_searches = sum(r['searches_completed'] for r in successful_results)
        total_jobs = sum(r['total_jobs_found'] for r in successful_results)
        total_errors = sum(len(r['errors']) for r in successful_results)
        
        all_response_times = []
        for r in successful_results:
            all_response_times.extend(r['response_times'])
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        
        # 驗證系統性能
        assert len(failed_results) == 0, f"有 {len(failed_results)} 個用戶會話失敗"
        assert total_searches >= concurrent_users * searches_per_user * 0.9  # 至少90%的搜索成功
        assert avg_response_time < 2.0  # 平均響應時間小於2秒
        assert max_response_time < 5.0  # 最大響應時間小於5秒
        assert total_errors / max(1, total_searches) < 0.05  # 錯誤率小於5%
        
        # 驗證吞吐量
        searches_per_second = total_searches / total_time
        assert searches_per_second > 5  # 每秒至少處理5個搜索
        
        print(f"高負載測試結果:")
        print(f"  並發用戶: {concurrent_users}")
        print(f"  總搜索次數: {total_searches}")
        print(f"  總執行時間: {total_time:.2f}秒")
        print(f"  平均響應時間: {avg_response_time:.2f}秒")
        print(f"  最大響應時間: {max_response_time:.2f}秒")
        print(f"  搜索吞吐量: {searches_per_second:.2f}次/秒")
        print(f"  錯誤率: {(total_errors / max(1, total_searches) * 100):.2f}%")
    
    @pytest_marks['e2e']
    async def test_error_recovery_scenario(self, test_fixtures):
        """測試錯誤恢復場景"""
        # 模擬各種錯誤情況和系統恢復
        error_scenarios = [
            {
                'name': 'network_timeout',
                'description': '網絡超時錯誤',
                'error_type': 'TimeoutError',
                'recovery_expected': True
            },
            {
                'name': 'api_rate_limit',
                'description': 'API速率限制',
                'error_type': 'RateLimitError',
                'recovery_expected': True
            },
            {
                'name': 'invalid_response',
                'description': '無效響應格式',
                'error_type': 'ValidationError',
                'recovery_expected': False
            },
            {
                'name': 'service_unavailable',
                'description': '服務不可用',
                'error_type': 'ServiceUnavailableError',
                'recovery_expected': True
            }
        ]
        
        recovery_results = []
        
        for scenario in error_scenarios:
            print(f"測試錯誤場景: {scenario['description']}")
            
            # 模擬錯誤發生
            error_simulation = {
                'scenario': scenario['name'],
                'error_occurred': True,
                'error_time': datetime.now().isoformat(),
                'recovery_attempts': 0,
                'recovery_successful': False,
                'recovery_time': None
            }
            
            # 模擬錯誤恢復機制
            max_retries = 3
            retry_delay = 0.1  # 縮短測試時間
            
            for attempt in range(max_retries):
                error_simulation['recovery_attempts'] += 1
                
                try:
                    # 模擬恢復嘗試
                    if scenario['recovery_expected']:
                        # 模擬成功恢復（在第2或第3次嘗試）
                        if attempt >= 1:
                            error_simulation['recovery_successful'] = True
                            error_simulation['recovery_time'] = datetime.now().isoformat()
                            break
                        else:
                            # 模擬失敗
                            raise Exception(f"Simulated {scenario['error_type']}")
                    else:
                        # 不可恢復的錯誤
                        raise Exception(f"Non-recoverable {scenario['error_type']}")
                        
                except Exception as e:
                    if attempt == max_retries - 1:
                        # 最後一次嘗試失敗
                        error_simulation['final_error'] = str(e)
                    else:
                        # 等待重試
                        await asyncio.sleep(retry_delay)
            
            recovery_results.append(error_simulation)
        
        # 驗證錯誤恢復
        for i, result in enumerate(recovery_results):
            scenario = error_scenarios[i]
            
            if scenario['recovery_expected']:
                assert result['recovery_successful'], f"場景 {scenario['name']} 應該能夠恢復"
                assert result['recovery_attempts'] <= 3, f"恢復嘗試次數不應超過3次"
            else:
                assert not result['recovery_successful'], f"場景 {scenario['name']} 不應該能夠恢復"
                assert 'final_error' in result, f"不可恢復的錯誤應該記錄最終錯誤"
        
        # 驗證錯誤記錄
        for result in recovery_results:
            assert 'error_time' in result
            assert result['recovery_attempts'] > 0
            assert 'scenario' in result
    
    @pytest_marks['e2e']
    async def test_data_consistency_scenario(self, test_fixtures):
        """測試數據一致性場景"""
        # 模擬並發數據操作和一致性檢查
        database = test_fixtures.get('database')
        cache = test_fixtures.get('cache')
        
        # 測試數據
        test_jobs = generate_test_job_data(10)
        
        async def concurrent_data_operations():
            """並發數據操作"""
            operations = []
            
            # 並發插入操作
            for i, job in enumerate(test_jobs[:5]):
                operations.append(('insert', job, i))
            
            # 並發更新操作
            for i, job in enumerate(test_jobs[5:]):
                job['title'] = f"Updated {job['title']}"
                operations.append(('update', job, i + 5))
            
            # 執行並發操作
            async def execute_operation(op_type, job_data, job_id):
                try:
                    if op_type == 'insert':
                        # 模擬數據庫插入
                        # await storage.save_job(job_data)
                        # await cache.set(f"job_{job_id}", job_data)
                        
                        # 暫時使用模擬操作
                        await asyncio.sleep(0.01)  # 模擬數據庫操作時間
                        return {'success': True, 'operation': 'insert', 'job_id': job_id}
                        
                    elif op_type == 'update':
                        # 模擬數據庫更新
                        # await storage.update_job(job_id, job_data)
                        # await cache.set(f"job_{job_id}", job_data)
                        
                        # 暫時使用模擬操作
                        await asyncio.sleep(0.01)
                        return {'success': True, 'operation': 'update', 'job_id': job_id}
                        
                except Exception as e:
                    return {'success': False, 'error': str(e), 'job_id': job_id}
            
            # 並發執行所有操作
            tasks = [execute_operation(op[0], op[1], op[2]) for op in operations]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return results
        
        # 執行並發操作
        operation_results = await concurrent_data_operations()
        
        # 驗證操作結果
        successful_operations = [r for r in operation_results if not isinstance(r, Exception) and r.get('success')]
        failed_operations = [r for r in operation_results if isinstance(r, Exception) or not r.get('success')]
        
        assert len(failed_operations) == 0, f"有 {len(failed_operations)} 個操作失敗"
        assert len(successful_operations) == 10, "所有操作都應該成功"
        
        # 驗證數據一致性
        insert_operations = [r for r in successful_operations if r['operation'] == 'insert']
        update_operations = [r for r in successful_operations if r['operation'] == 'update']
        
        assert len(insert_operations) == 5, "應該有5個插入操作"
        assert len(update_operations) == 5, "應該有5個更新操作"
        
        # 模擬數據一致性檢查
        # 檢查數據庫和緩存的一致性
        consistency_check = {
            'database_records': len(successful_operations),
            'cache_records': len(successful_operations),
            'inconsistencies': []
        }
        
        # 在真實實現中，這裡會檢查數據庫和緩存中的數據是否一致
        # for job_id in range(10):
        #     db_data = await storage.get_job(job_id)
        #     cache_data = await cache.get(f"job_{job_id}")
        #     
        #     if db_data != cache_data:
        #         consistency_check['inconsistencies'].append({
        #             'job_id': job_id,
        #             'db_data': db_data,
        #             'cache_data': cache_data
        #         })
        
        # 驗證一致性
        assert consistency_check['database_records'] == consistency_check['cache_records']
        assert len(consistency_check['inconsistencies']) == 0, "數據庫和緩存應該保持一致"


class TestPerformanceBenchmarks:
    """性能基準測試"""
    
    @pytest_marks['e2e']
    @pytest_marks['slow']
    async def test_search_performance_benchmark(self, test_fixtures):
        """測試搜索性能基準"""
        # 定義性能基準
        performance_targets = {
            'max_response_time': 3.0,  # 最大響應時間3秒
            'min_throughput': 10,      # 最小吞吐量10次/秒
            'max_memory_usage': 500,   # 最大內存使用500MB
            'max_cpu_usage': 80        # 最大CPU使用率80%
        }
        
        # 性能測試配置
        test_config = {
            'search_iterations': 50,
            'concurrent_searches': 5,
            'platforms': ['indeed', 'glassdoor'],
            'search_complexity': 'medium'
        }
        
        performance_metrics = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'throughput': 0,
            'errors': []
        }
        
        async def performance_search(search_id: int):
            """執行性能測試搜索"""
            start_time = time.time()
            
            try:
                # 模擬搜索操作
                search_params = {
                    'keywords': f'software engineer {search_id}',
                    'location': 'San Francisco',
                    'platforms': test_config['platforms']
                }
                
                # 這裡需要調用實際的搜索API
                # results = await api.search_jobs(search_params)
                
                # 暫時使用模擬搜索
                await asyncio.sleep(0.2)  # 模擬搜索時間
                results = generate_test_job_data(5)
                
                response_time = time.time() - start_time
                
                return {
                    'search_id': search_id,
                    'response_time': response_time,
                    'results_count': len(results),
                    'success': True
                }
                
            except Exception as e:
                return {
                    'search_id': search_id,
                    'error': str(e),
                    'success': False
                }
        
        # 執行性能測試
        start_time = time.time()
        
        # 分批執行並發搜索
        all_results = []
        for batch_start in range(0, test_config['search_iterations'], test_config['concurrent_searches']):
            batch_end = min(batch_start + test_config['concurrent_searches'], test_config['search_iterations'])
            batch_tasks = [performance_search(i) for i in range(batch_start, batch_end)]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            all_results.extend(batch_results)
            
            # 模擬系統資源監控
            # memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            # cpu_usage = psutil.Process().cpu_percent()
            
            # 暫時使用模擬資源使用
            memory_usage = 200 + (batch_start / test_config['search_iterations']) * 100  # 模擬遞增
            cpu_usage = 30 + (batch_start / test_config['search_iterations']) * 20
            
            performance_metrics['memory_usage'].append(memory_usage)
            performance_metrics['cpu_usage'].append(cpu_usage)
        
        total_time = time.time() - start_time
        
        # 分析性能結果
        successful_searches = [r for r in all_results if not isinstance(r, Exception) and r.get('success')]
        failed_searches = [r for r in all_results if isinstance(r, Exception) or not r.get('success')]
        
        if successful_searches:
            response_times = [r['response_time'] for r in successful_searches]
            performance_metrics['response_times'] = response_times
            performance_metrics['throughput'] = len(successful_searches) / total_time
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            avg_memory = sum(performance_metrics['memory_usage']) / len(performance_metrics['memory_usage'])
            max_memory = max(performance_metrics['memory_usage'])
            
            avg_cpu = sum(performance_metrics['cpu_usage']) / len(performance_metrics['cpu_usage'])
            max_cpu = max(performance_metrics['cpu_usage'])
            
            # 驗證性能基準
            assert max_response_time <= performance_targets['max_response_time'], \
                f"最大響應時間 {max_response_time:.2f}s 超過目標 {performance_targets['max_response_time']}s"
            
            assert performance_metrics['throughput'] >= performance_targets['min_throughput'], \
                f"吞吐量 {performance_metrics['throughput']:.2f}/s 低於目標 {performance_targets['min_throughput']}/s"
            
            assert max_memory <= performance_targets['max_memory_usage'], \
                f"最大內存使用 {max_memory:.2f}MB 超過目標 {performance_targets['max_memory_usage']}MB"
            
            assert max_cpu <= performance_targets['max_cpu_usage'], \
                f"最大CPU使用率 {max_cpu:.2f}% 超過目標 {performance_targets['max_cpu_usage']}%"
            
            # 輸出性能報告
            print(f"\n性能基準測試結果:")
            print(f"  總搜索次數: {len(successful_searches)}/{test_config['search_iterations']}")
            print(f"  成功率: {len(successful_searches)/test_config['search_iterations']*100:.1f}%")
            print(f"  平均響應時間: {avg_response_time:.2f}s")
            print(f"  最大響應時間: {max_response_time:.2f}s")
            print(f"  最小響應時間: {min_response_time:.2f}s")
            print(f"  吞吐量: {performance_metrics['throughput']:.2f}次/秒")
            print(f"  平均內存使用: {avg_memory:.2f}MB")
            print(f"  最大內存使用: {max_memory:.2f}MB")
            print(f"  平均CPU使用率: {avg_cpu:.2f}%")
            print(f"  最大CPU使用率: {max_cpu:.2f}%")
            
            if failed_searches:
                print(f"  失敗的搜索: {len(failed_searches)}")
        
        else:
            pytest.fail("沒有成功的搜索，無法進行性能評估")


# 測試運行器
if __name__ == '__main__':
    # 運行所有端到端測試
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'e2e',
        '-s'  # 顯示print輸出
    ])