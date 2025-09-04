# JobSpy v2 技術設計文檔 (TDD)

## 🏗️ 系統架構概述

### 架構原則
- **微服務化**: 模塊化設計，獨立部署
- **異步優先**: 提高響應性和吞吐量
- **AI 增強**: 智能化數據處理和用戶體驗
- **雲原生**: 容器化部署，彈性擴展
- **安全第一**: 端到端安全保護

### 技術堆疊

#### 後端 (Backend)
```
FastAPI (Python 3.11+)
├── API 框架: FastAPI + Pydantic
├── 異步處理: asyncio + aiohttp
├── 數據庫: PostgreSQL + Redis
├── AI 集成: OpenAI GPT-4V + Local VLM
├── 消息隊列: Celery + Redis
└── 部署: Docker + Gunicorn
```

#### 前端 (Frontend)
```
React 18 + TypeScript
├── 構建工具: Vite
├── 狀態管理: Zustand
├── 數據獲取: TanStack Query
├── UI 框架: Tailwind CSS + Headless UI
├── 動畫: Framer Motion
└── 測試: Vitest + Testing Library
```

#### 基礎設施 (Infrastructure)
```
容器化 & 編排
├── 開發環境: Docker Compose
├── 生產環境: Kubernetes
├── 監控: Prometheus + Grafana
├── 日誌: ELK Stack
└── CI/CD: GitHub Actions
```

## 🔄 系統架構圖

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React + TypeScript UI]
        PWA[Progressive Web App]
    end
    
    subgraph "API Gateway"
        Gateway[FastAPI Gateway]
        Auth[Authentication Service]
        RateLimit[Rate Limiting]
    end
    
    subgraph "Core Services"
        JobSearch[Job Search Service]
        AIVision[AI Vision Service]
        UserService[User Service]
        Analytics[Analytics Service]
    end
    
    subgraph "AI Layer"
        GPT4V[OpenAI GPT-4V]
        LocalVLM[Local VLM (CLIP)]
        NLP[NLP Processing]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        MinIO[(MinIO Storage)]
    end
    
    subgraph "External APIs"
        Indeed[Indeed API]
        LinkedIn[LinkedIn API]
        Glassdoor[Glassdoor API]
    end
    
    UI --> Gateway
    PWA --> Gateway
    Gateway --> Auth
    Gateway --> RateLimit
    Gateway --> JobSearch
    Gateway --> AIVision
    Gateway --> UserService
    Gateway --> Analytics
    
    JobSearch --> GPT4V
    JobSearch --> LocalVLM
    AIVision --> GPT4V
    AIVision --> LocalVLM
    
    JobSearch --> PostgreSQL
    JobSearch --> Redis
    AIVision --> MinIO
    
    JobSearch --> Indeed
    JobSearch --> LinkedIn
    JobSearch --> Glassdoor
```

## 🛠️ 核心服務設計

### 1. Job Search Service

#### 服務責任
- 統一求職搜索接口
- 多平台數據聚合
- 智能路由和負載均衡
- 搜索結果優化

#### API 設計
```python
# 搜索接口
POST /api/v1/jobs/search
{
    "query": "software engineer in taipei",
    "location": "taipei, taiwan",
    "experience_level": "mid-level",
    "salary_range": {"min": 80000, "max": 150000},
    "job_type": "full-time",
    "remote_ok": true,
    "ai_enhance": true
}

# 響應格式
{
    "jobs": [...],
    "total_count": 156,
    "search_metadata": {
        "query_analysis": {...},
        "sources_used": ["indeed", "linkedin"],
        "ai_enhancement_used": true,
        "processing_time_ms": 2340
    },
    "pagination": {...}
}
```

#### 數據模型
```python
class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    salary_range: Optional[SalaryRange]
    job_type: JobType
    experience_level: ExperienceLevel
    remote_friendly: bool
    posted_date: datetime
    source: str
    source_url: str
    ai_analysis: Optional[AIAnalysis]
```

### 2. AI Vision Service

#### 服務責任
- 網站截圖分析
- 職位信息提取
- 反機器人檢測
- 成本優化控制

#### 三層策略架構
```python
class AIVisionStrategy:
    """三層AI視覺策略"""
    
    async def analyze_page(self, url: str) -> JobExtraction:
        # Layer 1: 嘗試 API 獲取
        if api_result := await self.try_api_extraction(url):
            return api_result
            
        # Layer 2: 嘗試傳統爬蟲
        if scraping_result := await self.try_scraping(url):
            return scraping_result
            
        # Layer 3: AI 視覺分析
        return await self.ai_vision_analysis(url)
    
    async def ai_vision_analysis(self, url: str) -> JobExtraction:
        # 成本分析
        cost_estimate = await self.estimate_cost(url)
        if cost_estimate > self.max_cost_threshold:
            return await self.local_vlm_analysis(url)
        
        # 雲端 AI 分析
        return await self.cloud_vlm_analysis(url)
```

#### 資源池設計
```python
class ResourcePools:
    """統一資源池管理"""
    
    def __init__(self):
        self.ua_pool = UserAgentPool()
        self.proxy_pool = ProxyPool()
        self.token_pool = TokenPool()
        self.session_pool = SessionPool()
        self.worker_pool = WorkerPool()
        self.parser_pool = ParserPool()
    
    async def get_resources(self) -> ResourceBundle:
        """獲取可用資源組合"""
        return ResourceBundle(
            user_agent=await self.ua_pool.get_random(),
            proxy=await self.proxy_pool.get_healthy(),
            token=await self.token_pool.get_valid(),
            session=await self.session_pool.get_available(),
            worker=await self.worker_pool.assign(),
            parser=await self.parser_pool.get_optimal()
        )
```

### 3. 數據庫設計

#### PostgreSQL Schema
```sql
-- 用戶表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 職位表
CREATE TABLE job_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements TEXT[],
    salary_range JSONB,
    job_type VARCHAR(50),
    experience_level VARCHAR(50),
    remote_friendly BOOLEAN DEFAULT FALSE,
    source VARCHAR(100) NOT NULL,
    source_url VARCHAR(1000),
    raw_data JSONB,
    ai_analysis JSONB,
    posted_date TIMESTAMP,
    scraped_date TIMESTAMP DEFAULT NOW(),
    INDEX idx_title_company (title, company),
    INDEX idx_location (location),
    INDEX idx_posted_date (posted_date)
);

-- 搜索記錄表
CREATE TABLE search_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    query_text TEXT NOT NULL,
    filters JSONB,
    results_count INTEGER,
    processing_time_ms INTEGER,
    ai_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI 分析緩存表
CREATE TABLE ai_analysis_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    analysis_result JSONB NOT NULL,
    cost_used DECIMAL(10,4),
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### Redis 緩存策略
```python
class CacheStrategy:
    """緩存策略配置"""
    
    CACHE_CONFIGS = {
        "job_listings": {
            "ttl": 3600,  # 1小時
            "key_pattern": "job:{source}:{job_id}"
        },
        "search_results": {
            "ttl": 1800,  # 30分鐘
            "key_pattern": "search:{query_hash}"
        },
        "ai_analysis": {
            "ttl": 86400,  # 24小時
            "key_pattern": "ai:{url_hash}"
        },
        "user_sessions": {
            "ttl": 7200,  # 2小時
            "key_pattern": "session:{user_id}"
        }
    }
```

## 🔄 API 設計規範

### RESTful API 原則
- 使用標準 HTTP 方法 (GET, POST, PUT, DELETE)
- 語義化 URL 設計
- 統一響應格式
- 適當的 HTTP 狀態碼

### API 版本控制
```python
# URL 版本控制
/api/v1/jobs/search
/api/v2/jobs/search

# Header 版本控制
API-Version: v1
Accept: application/vnd.jobspy.v1+json
```

### 統一響應格式
```python
class APIResponse(BaseModel):
    """統一 API 響應格式"""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

# 成功響應
{
    "success": true,
    "data": {...},
    "metadata": {
        "pagination": {...},
        "total_count": 100
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "123e4567-e89b-12d3-a456-426614174000"
}

# 錯誤響應
{
    "success": false,
    "error": {
        "code": "INVALID_QUERY",
        "message": "搜索查詢格式無效",
        "details": {...}
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## 🔐 安全設計

### 認證與授權
```python
# JWT Token 結構
{
    "sub": "user_id",
    "email": "user@example.com",
    "role": "premium_user",
    "permissions": ["search", "ai_enhance", "analytics"],
    "exp": 1640995200,
    "iat": 1640908800
}

# API 權限控制
@require_permission("ai_enhance")
async def ai_vision_analyze(request: AnalysisRequest):
    pass

@rate_limit("100/hour")
async def search_jobs(request: SearchRequest):
    pass
```

### 數據保護
```python
class DataProtection:
    """數據保護策略"""
    
    @staticmethod
    def encrypt_pii(data: str) -> str:
        """加密個人識別信息"""
        return fernet.encrypt(data.encode()).decode()
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """哈希敏感數據"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def anonymize_logs(log_data: dict) -> dict:
        """日誌數據匿名化"""
        return {k: "***" if k in PII_FIELDS else v 
                for k, v in log_data.items()}
```

## 📊 監控與日誌

### 性能監控指標
```python
class Metrics:
    """性能監控指標"""
    
    # 業務指標
    SEARCH_REQUESTS_TOTAL = Counter("search_requests_total")
    AI_ANALYSIS_REQUESTS = Counter("ai_analysis_requests_total")
    JOB_EXTRACTION_SUCCESS_RATE = Gauge("job_extraction_success_rate")
    
    # 技術指標
    API_RESPONSE_TIME = Histogram("api_response_time_seconds")
    DATABASE_QUERY_TIME = Histogram("database_query_time_seconds")
    CACHE_HIT_RATE = Gauge("cache_hit_rate")
    
    # 資源指標
    ACTIVE_SESSIONS = Gauge("active_sessions")
    AI_TOKENS_USED = Counter("ai_tokens_used_total")
    PROXY_POOL_HEALTH = Gauge("proxy_pool_health_score")
```

### 結構化日誌
```python
import structlog

logger = structlog.get_logger()

# 業務事件日誌
await logger.ainfo(
    "job_search_completed",
    user_id=user.id,
    query=search_query,
    results_count=len(results),
    processing_time_ms=processing_time,
    ai_enhanced=ai_used,
    sources_used=sources
)

# 錯誤日誌
await logger.aerror(
    "ai_analysis_failed",
    url=target_url,
    error_type=error.__class__.__name__,
    error_message=str(error),
    fallback_used=True
)
```

## 🚀 部署與擴展

### 容器化配置
```dockerfile
# 多階段構建
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY ./app /app
WORKDIR /app
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
```

### Kubernetes 部署
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jobspy-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jobspy-backend
  template:
    metadata:
      labels:
        app: jobspy-backend
    spec:
      containers:
      - name: backend
        image: jobspy/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: jobspy-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### 自動擴展策略
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: jobspy-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: jobspy-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🧪 測試策略

### 測試金字塔
```python
# 單元測試 (70%)
class TestJobSearchService:
    async def test_search_with_valid_query(self):
        service = JobSearchService()
        results = await service.search("python developer")
        assert len(results) > 0
        assert all(result.title for result in results)

# 集成測試 (20%)
class TestAPIIntegration:
    async def test_end_to_end_search_flow(self):
        async with AsyncClient() as client:
            response = await client.post("/api/v1/jobs/search", json={
                "query": "software engineer",
                "location": "taipei"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

# E2E 測試 (10%)
class TestUserJourney:
    def test_complete_user_search_journey(self):
        # 使用 Playwright 進行端到端測試
        pass
```

### 性能測試
```python
# 負載測試
import asyncio
import aiohttp
from locust import HttpUser, task

class JobSearchUser(HttpUser):
    @task
    def search_jobs(self):
        self.client.post("/api/v1/jobs/search", json={
            "query": "software engineer",
            "location": "taiwan"
        })
```

## 📋 開發工作流

### Git 工作流
```bash
# 功能分支開發
git checkout -b feature/ai-vision-service
git commit -m "feat: implement AI vision analysis"
git push origin feature/ai-vision-service

# Pull Request 審查
# CI/CD 自動測試
# 代碼合併到 main
```

### CI/CD 流水線
```yaml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=app
    - name: Run linting
      run: |
        black --check app/
        isort --check-only app/
        mypy app/

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        kubectl apply -f k8s/
        kubectl rollout status deployment/jobspy-backend
```

## 🎯 性能優化策略

### 數據庫優化
```sql
-- 索引優化
CREATE INDEX CONCURRENTLY idx_job_listings_search 
ON job_listings USING GIN (
    to_tsvector('english', title || ' ' || description)
);

-- 分區表
CREATE TABLE job_listings_2024 PARTITION OF job_listings
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 緩存策略
```python
class MultiLevelCache:
    """多級緩存策略"""
    
    def __init__(self):
        self.l1_cache = {}  # 內存緩存
        self.l2_cache = redis_client  # Redis 緩存
        self.l3_cache = postgresql  # 數據庫
    
    async def get(self, key: str):
        # L1: 內存緩存
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2: Redis 緩存
        if value := await self.l2_cache.get(key):
            self.l1_cache[key] = value
            return value
        
        # L3: 數據庫查詢
        value = await self.l3_cache.get(key)
        if value:
            await self.l2_cache.set(key, value, ttl=3600)
            self.l1_cache[key] = value
        
        return value
```

### 異步處理優化
```python
class OptimizedJobSearch:
    """優化的異步求職搜索"""
    
    async def parallel_search(self, query: str, sources: List[str]):
        """並行搜索多個來源"""
        tasks = [
            self.search_source(query, source) 
            for source in sources
        ]
        
        # 使用 asyncio.gather 並行執行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾異常結果
        valid_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        return self.merge_and_dedupe(valid_results)
```

這個技術設計文檔提供了 JobSpy v2 的完整技術架構和實現策略。接下來我們可以創建具體的開發路線圖和原型驗證計劃。你希望我繼續創建開發路線圖還是有其他特定的技術細節需要討論？