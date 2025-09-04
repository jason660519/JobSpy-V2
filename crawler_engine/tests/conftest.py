"""pytest配置文件

定義測試環境、fixtures和全局配置。
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, List, Generator
import json
import os
from datetime import datetime, timedelta

# 導入測試框架
from . import (
    TestManager,
    TEST_CONFIG,
    TEST_DATA,
    create_mock_response,
    create_mock_page,
    generate_test_job_data
)


# pytest配置
def pytest_configure(config):
    """pytest配置"""
    # 註冊自定義標記
    config.addinivalue_line(
        "markers", "unit: 單元測試標記"
    )
    config.addinivalue_line(
        "markers", "integration: 集成測試標記"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端測試標記"
    )
    config.addinivalue_line(
        "markers", "performance: 性能測試標記"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速測試標記"
    )
    config.addinivalue_line(
        "markers", "fast: 快速測試標記"
    )
    config.addinivalue_line(
        "markers", "smoke: 冒煙測試標記"
    )
    config.addinivalue_line(
        "markers", "regression: 回歸測試標記"
    )
    config.addinivalue_line(
        "markers", "api: API測試標記"
    )
    config.addinivalue_line(
        "markers", "database: 數據庫測試標記"
    )
    config.addinivalue_line(
        "markers", "browser: 瀏覽器測試標記"
    )
    config.addinivalue_line(
        "markers", "ai: AI功能測試標記"
    )


def pytest_collection_modifyitems(config, items):
    """修改測試收集項"""
    # 為沒有標記的測試添加默認標記
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # 為慢速測試添加超時
        if item.get_closest_marker("slow"):
            item.add_marker(pytest.mark.timeout(300))  # 5分鐘超時
        elif item.get_closest_marker("performance"):
            item.add_marker(pytest.mark.timeout(600))  # 10分鐘超時
        else:
            item.add_marker(pytest.mark.timeout(60))   # 1分鐘超時


# 全局fixtures
@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """測試配置"""
    return {
        **TEST_CONFIG,
        'test_session_id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'test_start_time': datetime.now().isoformat(),
        'test_environment': 'pytest',
        'test_data_dir': tempfile.mkdtemp(prefix='crawler_test_'),
        'test_timeout': 60,
        'test_retries': 3,
        'test_parallel': True
    }


@pytest.fixture(scope="session")
def test_data() -> Dict[str, Any]:
    """測試數據"""
    return {
        **TEST_DATA,
        'generated_jobs': generate_test_job_data(50),
        'test_users': [
            {
                'id': f'test_user_{i}',
                'email': f'test{i}@example.com',
                'preferences': {
                    'job_types': ['full-time'],
                    'experience_level': 'entry' if i < 5 else 'senior',
                    'remote_preference': 'hybrid',
                    'salary_range': {'min': 50000 + i * 10000, 'max': 100000 + i * 20000}
                }
            }
            for i in range(10)
        ],
        'test_companies': [
            {
                'id': f'company_{i}',
                'name': f'Test Company {i}',
                'industry': ['Technology', 'Finance', 'Healthcare'][i % 3],
                'size': ['startup', 'medium', 'large'][i % 3],
                'location': ['San Francisco', 'New York', 'Seattle'][i % 3]
            }
            for i in range(15)
        ]
    }


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """臨時目錄"""
    temp_path = Path(tempfile.mkdtemp(prefix='crawler_test_'))
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_database(temp_dir: Path) -> Dict[str, Any]:
    """測試數據庫"""
    db_path = temp_dir / 'test.db'
    
    # 模擬數據庫配置
    db_config = {
        'type': 'sqlite',
        'path': str(db_path),
        'connection_string': f'sqlite:///{db_path}',
        'pool_size': 5,
        'max_overflow': 10,
        'echo': False
    }
    
    # 創建模擬數據庫連接
    mock_connection = Mock()
    mock_connection.execute = AsyncMock()
    mock_connection.fetch = AsyncMock()
    mock_connection.fetchone = AsyncMock()
    mock_connection.fetchall = AsyncMock()
    mock_connection.close = AsyncMock()
    
    return {
        'config': db_config,
        'connection': mock_connection,
        'path': db_path,
        'tables': ['jobs', 'users', 'applications', 'searches']
    }


@pytest.fixture
def test_cache() -> Dict[str, Any]:
    """測試緩存"""
    # 模擬內存緩存
    cache_data = {}
    
    async def cache_get(key: str):
        return cache_data.get(key)
    
    async def cache_set(key: str, value: Any, ttl: int = 3600):
        cache_data[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }
        return True
    
    async def cache_delete(key: str):
        return cache_data.pop(key, None) is not None
    
    async def cache_clear():
        cache_data.clear()
        return True
    
    mock_cache = Mock()
    mock_cache.get = cache_get
    mock_cache.set = cache_set
    mock_cache.delete = cache_delete
    mock_cache.clear = cache_clear
    mock_cache.data = cache_data
    
    return {
        'instance': mock_cache,
        'config': {
            'backend': 'memory',
            'ttl': 3600,
            'max_size': 1000
        },
        'data': cache_data
    }


@pytest.fixture
def test_browser() -> Dict[str, Any]:
    """測試瀏覽器"""
    # 創建模擬瀏覽器和頁面
    mock_page = create_mock_page()
    
    mock_browser = Mock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    mock_browser.close = AsyncMock()
    
    mock_context = Mock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    
    return {
        'browser': mock_browser,
        'context': mock_context,
        'page': mock_page,
        'config': {
            'headless': True,
            'timeout': 30000,
            'user_agent': 'Mozilla/5.0 (Test Browser)',
            'viewport': {'width': 1920, 'height': 1080}
        }
    }


@pytest.fixture
def test_api_client() -> Dict[str, Any]:
    """測試API客戶端"""
    # 模擬HTTP客戶端
    mock_session = Mock()
    
    async def mock_get(url: str, **kwargs):
        return create_mock_response({
            'status': 'success',
            'data': generate_test_job_data(5),
            'url': url
        })
    
    async def mock_post(url: str, **kwargs):
        return create_mock_response({
            'status': 'success',
            'message': 'Request processed',
            'url': url,
            'data': kwargs.get('json', {})
        })
    
    mock_session.get = mock_get
    mock_session.post = mock_post
    mock_session.put = mock_post
    mock_session.delete = mock_post
    mock_session.close = AsyncMock()
    
    return {
        'session': mock_session,
        'base_url': 'https://api.test.com',
        'headers': {
            'User-Agent': 'Test Client',
            'Accept': 'application/json'
        },
        'timeout': 30
    }


@pytest.fixture
def test_ai_service() -> Dict[str, Any]:
    """測試AI服務"""
    # 模擬AI服務
    mock_ai = Mock()
    
    async def mock_analyze_image(image_data: bytes):
        return {
            'text_content': 'Sample extracted text from image',
            'job_details': {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'salary': '$120,000 - $150,000'
            },
            'confidence': 0.95
        }
    
    async def mock_generate_cover_letter(job_data: Dict, user_profile: Dict):
        return f"""
        Dear Hiring Manager,
        
        I am excited to apply for the {job_data.get('title', 'position')} role at {job_data.get('company', 'your company')}.
        
        Best regards,
        {user_profile.get('name', 'Applicant')}
        """.strip()
    
    async def mock_extract_job_data(html_content: str):
        return {
            'title': 'Extracted Job Title',
            'company': 'Extracted Company',
            'location': 'Extracted Location',
            'description': 'Extracted job description',
            'requirements': ['Python', 'JavaScript', 'SQL'],
            'benefits': ['Health insurance', 'Remote work', '401k']
        }
    
    mock_ai.analyze_image = mock_analyze_image
    mock_ai.generate_cover_letter = mock_generate_cover_letter
    mock_ai.extract_job_data = mock_extract_job_data
    
    return {
        'service': mock_ai,
        'config': {
            'api_key': 'test_api_key',
            'model': 'gpt-4-vision-preview',
            'max_tokens': 4000,
            'temperature': 0.1
        },
        'usage_stats': {
            'requests_made': 0,
            'tokens_used': 0,
            'cost_usd': 0.0
        }
    }


@pytest.fixture
def test_monitoring() -> Dict[str, Any]:
    """測試監控服務"""
    # 模擬監控組件
    metrics = {
        'requests_total': 0,
        'requests_success': 0,
        'requests_failed': 0,
        'response_time_avg': 0.0,
        'memory_usage_mb': 100.0,
        'cpu_usage_percent': 10.0
    }
    
    alerts = []
    health_checks = {
        'database': 'healthy',
        'cache': 'healthy',
        'api': 'healthy',
        'browser': 'healthy'
    }
    
    def record_metric(name: str, value: float):
        metrics[name] = value
    
    def create_alert(level: str, message: str):
        alert = {
            'id': len(alerts) + 1,
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'active'
        }
        alerts.append(alert)
        return alert
    
    def update_health(component: str, status: str):
        health_checks[component] = status
    
    mock_monitoring = Mock()
    mock_monitoring.record_metric = record_metric
    mock_monitoring.create_alert = create_alert
    mock_monitoring.update_health = update_health
    mock_monitoring.get_metrics = lambda: metrics.copy()
    mock_monitoring.get_alerts = lambda: alerts.copy()
    mock_monitoring.get_health = lambda: health_checks.copy()
    
    return {
        'service': mock_monitoring,
        'metrics': metrics,
        'alerts': alerts,
        'health_checks': health_checks
    }


@pytest.fixture
def test_fixtures(test_config: Dict[str, Any],
                 test_data: Dict[str, Any],
                 test_database: Dict[str, Any],
                 test_cache: Dict[str, Any],
                 test_browser: Dict[str, Any],
                 test_api_client: Dict[str, Any],
                 test_ai_service: Dict[str, Any],
                 test_monitoring: Dict[str, Any],
                 temp_dir: Path) -> Dict[str, Any]:
    """組合所有測試fixtures"""
    return {
        'config': test_config,
        'data': test_data,
        'database': test_database,
        'cache': test_cache,
        'browser': test_browser,
        'api_client': test_api_client,
        'ai_service': test_ai_service,
        'monitoring': test_monitoring,
        'temp_dir': temp_dir
    }


@pytest.fixture
def test_manager(test_fixtures: Dict[str, Any]) -> TestManager:
    """測試管理器"""
    manager = TestManager()
    
    # 註冊所有測試fixtures
    for name, fixture in test_fixtures.items():
        manager.register_fixture(name, fixture)
    
    return manager


# 測試輔助函數
@pytest.fixture
def assert_helpers():
    """斷言輔助函數"""
    def assert_job_valid(job: Dict[str, Any]):
        """驗證職位數據有效性"""
        required_fields = ['id', 'title', 'company', 'location']
        for field in required_fields:
            assert field in job, f"職位數據缺少必需字段: {field}"
            assert job[field], f"職位數據字段 {field} 不能為空"
        
        if 'salary' in job and job['salary']:
            assert isinstance(job['salary'], (str, dict)), "薪資信息格式不正確"
        
        if 'posted_date' in job and job['posted_date']:
            # 驗證日期格式
            try:
                datetime.fromisoformat(job['posted_date'].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"職位發布日期格式不正確: {job['posted_date']}")
    
    def assert_api_response_valid(response: Dict[str, Any]):
        """驗證API響應有效性"""
        assert 'status' in response, "API響應缺少status字段"
        assert response['status'] in ['success', 'error'], "API響應status值無效"
        
        if response['status'] == 'error':
            assert 'error' in response or 'message' in response, "錯誤響應缺少錯誤信息"
        else:
            assert 'data' in response, "成功響應缺少data字段"
    
    def assert_performance_acceptable(response_time: float, max_time: float = 2.0):
        """驗證性能可接受"""
        assert response_time <= max_time, \
            f"響應時間 {response_time:.2f}s 超過最大允許時間 {max_time}s"
    
    def assert_memory_usage_reasonable(memory_mb: float, max_memory: float = 500.0):
        """驗證內存使用合理"""
        assert memory_mb <= max_memory, \
            f"內存使用 {memory_mb:.2f}MB 超過最大允許 {max_memory}MB"
    
    return {
        'assert_job_valid': assert_job_valid,
        'assert_api_response_valid': assert_api_response_valid,
        'assert_performance_acceptable': assert_performance_acceptable,
        'assert_memory_usage_reasonable': assert_memory_usage_reasonable
    }


# 測試數據生成器
@pytest.fixture
def data_generators():
    """數據生成器"""
    def generate_search_query(complexity: str = 'simple') -> Dict[str, Any]:
        """生成搜索查詢"""
        base_query = {
            'keywords': 'software engineer',
            'location': 'San Francisco, CA',
            'platforms': ['indeed']
        }
        
        if complexity == 'complex':
            base_query.update({
                'filters': {
                    'experience_level': 'senior',
                    'salary_min': 120000,
                    'remote': True,
                    'company_size': 'large'
                },
                'sort_by': 'relevance',
                'limit': 50
            })
        
        return base_query
    
    def generate_user_profile(user_type: str = 'standard') -> Dict[str, Any]:
        """生成用戶配置文件"""
        base_profile = {
            'id': f'user_{datetime.now().timestamp()}',
            'email': 'test@example.com',
            'preferences': {
                'job_types': ['full-time'],
                'experience_level': 'mid',
                'remote_preference': 'hybrid'
            }
        }
        
        if user_type == 'premium':
            base_profile.update({
                'subscription_tier': 'premium',
                'daily_search_limit': 100,
                'ai_features_enabled': True
            })
        elif user_type == 'enterprise':
            base_profile.update({
                'subscription_tier': 'enterprise',
                'daily_search_limit': 1000,
                'ai_features_enabled': True,
                'team_features_enabled': True
            })
        
        return base_profile
    
    return {
        'generate_search_query': generate_search_query,
        'generate_user_profile': generate_user_profile,
        'generate_job_data': generate_test_job_data
    }


# 清理函數
@pytest.fixture(autouse=True)
def cleanup_after_test(test_fixtures: Dict[str, Any]):
    """測試後清理"""
    yield
    
    # 清理緩存
    if 'cache' in test_fixtures:
        cache = test_fixtures['cache']['instance']
        if hasattr(cache, 'clear'):
            asyncio.create_task(cache.clear())
    
    # 清理監控數據
    if 'monitoring' in test_fixtures:
        monitoring = test_fixtures['monitoring']
        monitoring['metrics'].clear()
        monitoring['alerts'].clear()
    
    # 清理臨時文件
    if 'temp_dir' in test_fixtures:
        temp_dir = test_fixtures['temp_dir']
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


# 測試會話清理
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_session(test_config: Dict[str, Any]):
    """測試會話清理"""
    yield
    
    # 清理測試數據目錄
    test_data_dir = test_config.get('test_data_dir')
    if test_data_dir and os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir, ignore_errors=True)
    
    print(f"\n測試會話結束: {test_config.get('test_session_id')}")
    print(f"測試開始時間: {test_config.get('test_start_time')}")
    print(f"測試結束時間: {datetime.now().isoformat()}")