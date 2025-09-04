# 爬蟲引擎測試框架

這是一個全面的測試框架，用於測試爬蟲引擎的各個組件和功能。

## 目錄結構

```
tests/
├── __init__.py              # 測試框架初始化
├── conftest.py              # pytest配置和全局fixtures
├── pytest.ini              # pytest配置文件
├── requirements-test.txt    # 測試依賴包
├── run_tests.py            # 測試運行腳本
├── test_data_generator.py  # 測試數據生成器
├── test_utils.py           # 測試工具和輔助函數
├── test_unit.py            # 單元測試
├── test_integration.py     # 集成測試
├── test_e2e.py            # 端到端測試
├── test_performance.py    # 性能測試
└── README.md              # 本文檔
```

## 快速開始

### 1. 安裝測試依賴

```bash
# 安裝基本測試依賴
pip install -r requirements-test.txt

# 或者安裝核心依賴
pip install pytest pytest-asyncio pytest-cov pytest-html pytest-xdist
```

### 2. 運行測試

```bash
# 使用測試運行腳本（推薦）
python run_tests.py --fast

# 或直接使用pytest
pytest
```

## 測試類型

### 單元測試 (Unit Tests)

測試單個組件或函數的功能。

```bash
# 運行所有單元測試
python run_tests.py --unit

# 或使用pytest標記
pytest -m unit
```

**覆蓋範圍：**
- 配置管理器
- 數據存儲
- AI視覺服務
- 智能爬蟲
- 平台適配器
- 監控系統
- 工具函數
- 錯誤處理

### 集成測試 (Integration Tests)

測試組件間的交互和集成。

```bash
# 運行集成測試
python run_tests.py --integration

# 或使用pytest標記
pytest -m integration
```

**覆蓋範圍：**
- 配置與環境變量集成
- 數據管道集成
- 爬蟲與存儲集成
- 監控系統集成

### 端到端測試 (E2E Tests)

測試完整的用戶場景和工作流。

```bash
# 運行端到端測試
python run_tests.py --e2e

# 或使用pytest標記
pytest -m e2e
```

**覆蓋範圍：**
- 用戶搜索場景
- 系統可靠性
- 性能基準測試

### 性能測試 (Performance Tests)

測試系統性能和負載能力。

```bash
# 運行性能測試
python run_tests.py --performance

# 或使用pytest標記
pytest -m performance
```

**覆蓋範圍：**
- 搜索性能
- 內存使用
- 並發處理

## 測試標記 (Markers)

使用pytest標記來分類和選擇測試：

```bash
# 按標記運行測試
pytest -m "unit and not slow"     # 快速單元測試
pytest -m "integration or e2e"    # 集成和端到端測試
pytest -m "performance"           # 性能測試
pytest -m "smoke"                 # 冒煙測試
pytest -m "regression"            # 回歸測試
```

**可用標記：**
- `unit` - 單元測試
- `integration` - 集成測試
- `e2e` - 端到端測試
- `performance` - 性能測試
- `slow` - 慢速測試
- `fast` - 快速測試
- `smoke` - 冒煙測試
- `regression` - 回歸測試
- `api` - API測試
- `database` - 數據庫測試
- `browser` - 瀏覽器測試
- `ai` - AI功能測試

## 測試配置

### pytest.ini

主要配置選項：

```ini
[tool:pytest]
testpaths = .
addopts = -v --strict-markers --tb=short
asyncio_mode = auto
log_cli = true
timeout = 300
```

### 環境變量

測試時會自動設置以下環境變量：

```bash
TESTING=1
LOG_LEVEL=DEBUG
CACHE_BACKEND=memory
DATABASE_URL=sqlite:///:memory:
AI_API_KEY=test_key
BROWSER_HEADLESS=true
```

## 測試數據

### 生成測試數據

```python
from test_data_generator import TestDataGenerator

# 創建生成器
generator = TestDataGenerator(seed=42)

# 生成職位數據
jobs = generator.generate_jobs(10)

# 生成公司數據
companies = generator.generate_companies(5)

# 生成用戶數據
users = generator.generate_users(3)
```

### 使用預定義數據

```python
from tests import TEST_DATA

# 使用測試配置
config = TEST_DATA['config']

# 使用測試用戶
test_user = TEST_DATA['users'][0]
```

## 測試工具

### 計時器

```python
from test_utils import TestTimer

with TestTimer() as timer:
    # 執行測試代碼
    pass

print(f"執行時間: {timer.elapsed:.3f}秒")
```

### 內存監控

```python
from test_utils import MemoryMonitor

with MemoryMonitor() as monitor:
    # 執行測試代碼
    pass

print(f"內存增長: {monitor.memory_increase} 字節")
```

### 模擬對象

```python
from test_utils import MockFactory

# 創建模擬HTTP響應
response = MockFactory.create_mock_response(
    status_code=200,
    json_data={'jobs': []}
)

# 創建模擬數據庫
db = MockFactory.create_mock_database()

# 創建模擬緩存
cache = MockFactory.create_mock_cache()
```

### 斷言工具

```python
from test_utils import TestAssertions

# 驗證職位數據
TestAssertions.assert_job_data_valid(job_data)

# 驗證API響應
TestAssertions.assert_api_response_valid(response)

# 驗證性能
TestAssertions.assert_performance_acceptable(elapsed_time, max_time=2.0)
```

## 覆蓋率報告

### 生成覆蓋率報告

```bash
# HTML報告
python run_tests.py --coverage

# 或使用pytest
pytest --cov=crawler_engine --cov-report=html

# 查看報告
open htmlcov/index.html
```

### 覆蓋率目標

- **總體覆蓋率**: ≥ 85%
- **核心模組**: ≥ 90%
- **工具函數**: ≥ 95%

## 並行測試

### 使用pytest-xdist

```bash
# 自動檢測CPU核心數
python run_tests.py --parallel

# 或指定進程數
pytest -n 4

# 按測試文件分發
pytest -n auto --dist=loadfile
```

## 測試報告

### HTML報告

```bash
# 生成HTML測試報告
python run_tests.py --html-report

# 或使用pytest
pytest --html=report.html --self-contained-html
```

### JUnit XML報告

```bash
# 生成JUnit XML報告（用於CI/CD）
pytest --junitxml=report.xml
```

### JSON報告

```bash
# 生成JSON報告
pytest --json-report --json-report-file=report.json
```

## 持續集成

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r crawler_engine/tests/requirements-test.txt
    
    - name: Run tests
      run: |
        cd crawler_engine/tests
        python run_tests.py --all --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### GitLab CI

```yaml
stages:
  - test

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r crawler_engine/tests/requirements-test.txt
    - cd crawler_engine/tests
    - python run_tests.py --all --coverage
  artifacts:
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## 調試測試

### 運行特定測試

```bash
# 運行特定測試文件
pytest test_unit.py

# 運行特定測試類
pytest test_unit.py::TestConfigManager

# 運行特定測試方法
pytest test_unit.py::TestConfigManager::test_load_config

# 使用關鍵字過濾
pytest -k "config and not slow"
```

### 詳細輸出

```bash
# 詳細輸出
pytest -v

# 顯示本地變量
pytest -l

# 顯示完整回溯
pytest --tb=long

# 在第一個失敗時停止
pytest -x

# 顯示最慢的10個測試
pytest --durations=10
```

### 調試模式

```bash
# 進入調試器
pytest --pdb

# 在失敗時進入調試器
pytest --pdb-trace

# 使用ipdb
pytest --pdbcls=IPython.terminal.debugger:Pdb
```

## 性能分析

### 基準測試

```python
import pytest

def test_search_performance(benchmark):
    result = benchmark(search_function, "python developer")
    assert len(result) > 0
```

### 內存分析

```bash
# 使用memory-profiler
pytest --profile

# 生成內存使用圖
mprof run pytest test_performance.py
mprof plot
```

### CPU分析

```bash
# 使用py-spy
py-spy record -o profile.svg -- python -m pytest
```

## 最佳實踐

### 測試命名

- 使用描述性的測試名稱
- 遵循 `test_<功能>_<場景>_<期望結果>` 格式
- 例如：`test_config_load_invalid_file_raises_error`

### 測試結構

```python
def test_feature():
    # Arrange - 準備測試數據
    config = create_test_config()
    
    # Act - 執行被測試的操作
    result = config.load_from_file("test.json")
    
    # Assert - 驗證結果
    assert result is not None
    assert result.get("key") == "value"
```

### 測試隔離

- 每個測試應該獨立運行
- 使用fixtures提供測試數據
- 清理測試產生的副作用

### 模擬外部依賴

- 模擬網絡請求
- 模擬數據庫操作
- 模擬文件系統操作
- 模擬時間和隨機數

### 測試數據管理

- 使用工廠模式生成測試數據
- 避免硬編碼測試數據
- 使用參數化測試覆蓋多種場景

## 故障排除

### 常見問題

1. **測試超時**
   ```bash
   # 增加超時時間
   pytest --timeout=600
   ```

2. **內存不足**
   ```bash
   # 減少並行進程數
   pytest -n 2
   ```

3. **依賴衝突**
   ```bash
   # 使用虛擬環境
   python -m venv test_env
   source test_env/bin/activate  # Linux/Mac
   test_env\Scripts\activate     # Windows
   ```

4. **瀏覽器測試失敗**
   ```bash
   # 安裝瀏覽器
   playwright install
   ```

### 日誌調試

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 或在測試中
def test_with_logging(caplog):
    with caplog.at_level(logging.DEBUG):
        # 測試代碼
        pass
    
    assert "expected message" in caplog.text
```

## 貢獻指南

### 添加新測試

1. 確定測試類型（單元/集成/端到端/性能）
2. 選擇合適的測試文件
3. 編寫測試函數
4. 添加適當的標記
5. 更新文檔

### 測試審查清單

- [ ] 測試名稱清晰描述
- [ ] 測試覆蓋正常和異常情況
- [ ] 使用適當的斷言
- [ ] 測試獨立且可重複
- [ ] 添加必要的標記
- [ ] 性能測試有明確的基準
- [ ] 文檔已更新

## 聯繫方式

如有問題或建議，請：

1. 查看現有的issue
2. 創建新的issue
3. 提交pull request
4. 聯繫維護團隊

---

**注意**: 這個測試框架正在持續開發中，某些功能可能還未完全實現。請參考最新的代碼和文檔。