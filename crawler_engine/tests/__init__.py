"""測試框架

提供全面的測試工具、夾具和實用程序，支持單元測試、集成測試和端到端測試。
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Generator
import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
import tempfile
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = structlog.get_logger(__name__)

# 測試配置
TEST_CONFIG = {
    'database': {
        'url': 'sqlite:///:memory:',
        'echo': False
    },
    'cache': {
        'backend': 'memory',
        'enabled': True
    },
    'logging': {
        'level': 'WARNING',
        'console_enabled': False,
        'file_enabled': False
    },
    'monitoring': {
        'enabled': False
    },
    'api': {
        'openai_api_key': 'test-key',
        'timeout': 5
    }
}

# 測試數據
TEST_DATA = {
    'job_listings': [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'salary': '$100,000 - $150,000',
            'description': 'We are looking for a skilled software engineer...',
            'url': 'https://example.com/job/1',
            'posted_date': '2024-01-15'
        },
        {
            'title': 'Data Scientist',
            'company': 'Data Inc',
            'location': 'New York, NY',
            'salary': '$120,000 - $180,000',
            'description': 'Join our data science team...',
            'url': 'https://example.com/job/2',
            'posted_date': '2024-01-16'
        }
    ],
    'html_samples': {
        'job_listing': '''
        <div class="job-card">
            <h2 class="job-title">Software Engineer</h2>
            <div class="company">Tech Corp</div>
            <div class="location">San Francisco, CA</div>
            <div class="salary">$100,000 - $150,000</div>
            <div class="description">We are looking for a skilled software engineer...</div>
        </div>
        ''',
        'search_results': '''
        <div class="search-results">
            <div class="job-item" data-job-id="1">
                <a href="/job/1" class="job-link">Software Engineer</a>
                <span class="company">Tech Corp</span>
            </div>
            <div class="job-item" data-job-id="2">
                <a href="/job/2" class="job-link">Data Scientist</a>
                <span class="company">Data Inc</span>
            </div>
        </div>
        '''
    },
    'api_responses': {
        'openai_vision': {
            'choices': [{
                'message': {
                    'content': '這是一個軟件工程師職位，公司是Tech Corp，位於舊金山。'
                }
            }]
        }
    }
}

# 測試夾具
@dataclass
class TestFixture:
    """測試夾具基類"""
    name: str
    description: str = ""
    setup_data: Dict[str, Any] = None
    cleanup_required: bool = True
    
    def setup(self) -> Any:
        """設置夾具"""
        pass
    
    def teardown(self) -> None:
        """清理夾具"""
        pass


class DatabaseFixture(TestFixture):
    """數據庫測試夾具"""
    
    def __init__(self):
        super().__init__(
            name="database",
            description="In-memory SQLite database for testing"
        )
        self.engine = None
        self.session = None
    
    def setup(self):
        """設置測試數據庫"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # 創建表結構
        # 這裡需要導入實際的模型類
        # Base.metadata.create_all(self.engine)
        
        return self.session
    
    def teardown(self):
        """清理數據庫"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()


class CacheFixture(TestFixture):
    """緩存測試夾具"""
    
    def __init__(self):
        super().__init__(
            name="cache",
            description="In-memory cache for testing"
        )
        self.cache = None
    
    def setup(self):
        """設置測試緩存"""
        # 這裡需要導入實際的緩存類
        # from crawler_engine.data.cache import MemoryCache
        # self.cache = MemoryCache(max_size=100)
        return self.cache
    
    def teardown(self):
        """清理緩存"""
        if self.cache:
            self.cache.clear()


class FileSystemFixture(TestFixture):
    """文件系統測試夾具"""
    
    def __init__(self):
        super().__init__(
            name="filesystem",
            description="Temporary directory for file operations"
        )
        self.temp_dir = None
    
    def setup(self):
        """設置臨時目錄"""
        self.temp_dir = tempfile.mkdtemp(prefix="crawler_test_")
        return Path(self.temp_dir)
    
    def teardown(self):
        """清理臨時目錄"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class MockAPIFixture(TestFixture):
    """模擬API測試夾具"""
    
    def __init__(self):
        super().__init__(
            name="mock_api",
            description="Mock API responses for testing"
        )
        self.mocks = {}
    
    def setup(self):
        """設置API模擬"""
        # OpenAI API模擬
        openai_mock = Mock()
        openai_mock.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response"))]
        )
        self.mocks['openai'] = openai_mock
        
        return self.mocks
    
    def teardown(self):
        """清理模擬"""
        self.mocks.clear()


class BrowserFixture(TestFixture):
    """瀏覽器測試夾具"""
    
    def __init__(self):
        super().__init__(
            name="browser",
            description="Playwright browser for testing"
        )
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def setup(self):
        """設置瀏覽器"""
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        return self.page
    
    async def teardown(self):
        """清理瀏覽器"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class TestManager:
    """測試管理器
    
    管理測試夾具、配置和實用程序。
    """
    
    def __init__(self):
        self.fixtures: Dict[str, TestFixture] = {}
        self.active_fixtures: Dict[str, Any] = {}
        self.logger = logger.bind(component="TestManager")
        
        # 註冊默認夾具
        self._register_default_fixtures()
    
    def _register_default_fixtures(self):
        """註冊默認夾具"""
        self.register_fixture(DatabaseFixture())
        self.register_fixture(CacheFixture())
        self.register_fixture(FileSystemFixture())
        self.register_fixture(MockAPIFixture())
        self.register_fixture(BrowserFixture())
    
    def register_fixture(self, fixture: TestFixture):
        """註冊測試夾具
        
        Args:
            fixture: 測試夾具
        """
        self.fixtures[fixture.name] = fixture
        self.logger.debug(
            "註冊測試夾具",
            name=fixture.name,
            description=fixture.description
        )
    
    def get_fixture(self, name: str) -> Optional[TestFixture]:
        """獲取測試夾具
        
        Args:
            name: 夾具名稱
            
        Returns:
            Optional[TestFixture]: 測試夾具
        """
        return self.fixtures.get(name)
    
    async def setup_fixture(self, name: str) -> Any:
        """設置測試夾具
        
        Args:
            name: 夾具名稱
            
        Returns:
            Any: 夾具實例
        """
        fixture = self.get_fixture(name)
        if not fixture:
            raise ValueError(f"Fixture '{name}' not found")
        
        try:
            if asyncio.iscoroutinefunction(fixture.setup):
                result = await fixture.setup()
            else:
                result = fixture.setup()
            
            self.active_fixtures[name] = result
            
            self.logger.debug(
                "測試夾具設置完成",
                name=name
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "測試夾具設置失敗",
                name=name,
                error=str(e)
            )
            raise
    
    async def teardown_fixture(self, name: str):
        """清理測試夾具
        
        Args:
            name: 夾具名稱
        """
        fixture = self.get_fixture(name)
        if not fixture or not fixture.cleanup_required:
            return
        
        try:
            if asyncio.iscoroutinefunction(fixture.teardown):
                await fixture.teardown()
            else:
                fixture.teardown()
            
            if name in self.active_fixtures:
                del self.active_fixtures[name]
            
            self.logger.debug(
                "測試夾具清理完成",
                name=name
            )
            
        except Exception as e:
            self.logger.error(
                "測試夾具清理失敗",
                name=name,
                error=str(e)
            )
    
    async def setup_all(self, fixture_names: List[str] = None) -> Dict[str, Any]:
        """設置所有或指定的測試夾具
        
        Args:
            fixture_names: 夾具名稱列表，如果為None則設置所有夾具
            
        Returns:
            Dict[str, Any]: 夾具實例字典
        """
        if fixture_names is None:
            fixture_names = list(self.fixtures.keys())
        
        results = {}
        for name in fixture_names:
            try:
                results[name] = await self.setup_fixture(name)
            except Exception as e:
                self.logger.error(
                    "夾具設置失敗，跳過",
                    name=name,
                    error=str(e)
                )
        
        return results
    
    async def teardown_all(self):
        """清理所有活動的測試夾具"""
        for name in list(self.active_fixtures.keys()):
            await self.teardown_fixture(name)
    
    def get_test_config(self) -> Dict[str, Any]:
        """獲取測試配置
        
        Returns:
            Dict[str, Any]: 測試配置
        """
        return TEST_CONFIG.copy()
    
    def get_test_data(self, key: str = None) -> Any:
        """獲取測試數據
        
        Args:
            key: 數據鍵，如果為None則返回所有數據
            
        Returns:
            Any: 測試數據
        """
        if key is None:
            return TEST_DATA.copy()
        return TEST_DATA.get(key)


# 全局測試管理器實例
test_manager = TestManager()


# pytest夾具
@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_fixtures():
    """設置和清理測試夾具"""
    fixtures = await test_manager.setup_all()
    yield fixtures
    await test_manager.teardown_all()


@pytest.fixture(scope="function")
async def test_database():
    """數據庫測試夾具"""
    db = await test_manager.setup_fixture("database")
    yield db
    await test_manager.teardown_fixture("database")


@pytest.fixture(scope="function")
async def test_cache():
    """緩存測試夾具"""
    cache = await test_manager.setup_fixture("cache")
    yield cache
    await test_manager.teardown_fixture("cache")


@pytest.fixture(scope="function")
async def test_filesystem():
    """文件系統測試夾具"""
    fs = await test_manager.setup_fixture("filesystem")
    yield fs
    await test_manager.teardown_fixture("filesystem")


@pytest.fixture(scope="function")
async def mock_apis():
    """模擬API測試夾具"""
    mocks = await test_manager.setup_fixture("mock_api")
    yield mocks
    await test_manager.teardown_fixture("mock_api")


@pytest.fixture(scope="function")
async def test_browser():
    """瀏覽器測試夾具"""
    browser = await test_manager.setup_fixture("browser")
    yield browser
    await test_manager.teardown_fixture("browser")


# 測試實用程序
def create_mock_response(status_code: int = 200, 
                        content: str = "",
                        headers: Dict[str, str] = None) -> Mock:
    """創建模擬HTTP響應
    
    Args:
        status_code: 狀態碼
        content: 響應內容
        headers: 響應頭
        
    Returns:
        Mock: 模擬響應對象
    """
    response = Mock()
    response.status_code = status_code
    response.text = content
    response.content = content.encode('utf-8')
    response.headers = headers or {}
    response.json.return_value = {}
    
    return response


def create_mock_page(html_content: str = "") -> Mock:
    """創建模擬頁面對象
    
    Args:
        html_content: HTML內容
        
    Returns:
        Mock: 模擬頁面對象
    """
    page = Mock()
    page.content.return_value = html_content
    page.url = "https://example.com"
    page.title.return_value = "Test Page"
    
    return page


def assert_job_data_valid(job_data: Dict[str, Any]):
    """驗證職位數據格式
    
    Args:
        job_data: 職位數據
    """
    required_fields = ['title', 'company', 'location']
    
    for field in required_fields:
        assert field in job_data, f"Missing required field: {field}"
        assert job_data[field], f"Empty required field: {field}"
    
    # 可選字段檢查
    optional_fields = ['salary', 'description', 'url', 'posted_date']
    for field in optional_fields:
        if field in job_data:
            assert isinstance(job_data[field], str), f"Field {field} should be string"


def assert_api_response_valid(response: Dict[str, Any]):
    """驗證API響應格式
    
    Args:
        response: API響應
    """
    assert 'status' in response, "Missing status field"
    assert 'data' in response, "Missing data field"
    
    if response['status'] == 'error':
        assert 'error' in response, "Missing error field for error response"


def generate_test_job_data(count: int = 1) -> List[Dict[str, Any]]:
    """生成測試職位數據
    
    Args:
        count: 生成數量
        
    Returns:
        List[Dict[str, Any]]: 職位數據列表
    """
    jobs = []
    
    for i in range(count):
        job = {
            'title': f'Test Job {i+1}',
            'company': f'Test Company {i+1}',
            'location': f'Test City {i+1}',
            'salary': f'${50000 + i*10000} - ${70000 + i*10000}',
            'description': f'This is a test job description {i+1}',
            'url': f'https://example.com/job/{i+1}',
            'posted_date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        }
        jobs.append(job)
    
    return jobs


# 測試標記
pytest_marks = {
    'unit': pytest.mark.unit,
    'integration': pytest.mark.integration,
    'e2e': pytest.mark.e2e,
    'slow': pytest.mark.slow,
    'api': pytest.mark.api,
    'database': pytest.mark.database,
    'browser': pytest.mark.browser,
    'ai': pytest.mark.ai
}


# 導出
__all__ = [
    'TestFixture',
    'DatabaseFixture',
    'CacheFixture',
    'FileSystemFixture',
    'MockAPIFixture',
    'BrowserFixture',
    'TestManager',
    'test_manager',
    'TEST_CONFIG',
    'TEST_DATA',
    'create_mock_response',
    'create_mock_page',
    'assert_job_data_valid',
    'assert_api_response_valid',
    'generate_test_job_data',
    'pytest_marks'
]