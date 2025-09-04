# Quick Start Guide - Modern JobSpy Architecture

## 🚀 **立即開始：現代化重構實施**

### **技術棧決策矩陣**

| 需求 | Flask (現狀) | FastAPI + React (推薦) | 評分 |
|------|-------------|------------------------|------|
| 開發速度 | 6/10 | 9/10 | ✅ |
| 性能 | 4/10 | 9/10 | ✅ |
| AI 整合 | 3/10 | 10/10 | ✅ |
| 可維護性 | 5/10 | 9/10 | ✅ |
| 團隊學習成本 | 9/10 | 6/10 | ⚠️ |
| 生態系統 | 7/10 | 10/10 | ✅ |

**結論**: 現代化收益遠大於學習成本，強烈建議重構。

---

## 📋 **30 天重構計劃**

### **Week 1: 環境準備**

#### Day 1-2: 新項目初始化
```bash
# 1. 創建新的項目結構
mkdir jobspy-v2
cd jobspy-v2

# 2. 初始化前端項目
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @tanstack/react-query zustand axios tailwindcss

# 3. 初始化後端項目  
cd ../
mkdir backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install fastapi uvicorn sqlalchemy asyncpg redis
```

#### Day 3-4: Docker 開發環境
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes: ["./frontend:/app"]
    
  backend:
    build: ./backend  
    ports: ["8000:8000"]
    volumes: ["./backend:/app"]
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/jobspy
      - REDIS_URL=redis://redis:6379
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: jobspy
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    
  redis:
    image: redis:7-alpine
    
volumes:
  postgres_data:
```

#### Day 5-7: 基礎 API 架構
```python
# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="JobSpy API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "JobSpy API v2"}

@app.post("/api/search")
async def search_jobs(query: str):
    # TODO: 整合現有 jobseeker 邏輯
    return {"jobs": [], "total": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **Week 2: 核心功能遷移**

#### Day 8-10: 現有代碼整合
```python
# backend/services/job_search.py
import sys
sys.path.append("../../")  # 引入現有 jobseeker 模組

from jobseeker.smart_router import smart_router
from jobseeker.model import Site

class JobSearchService:
    async def search_jobs(self, query: str, location: str = "", results_wanted: int = 20):
        """使用現有 jobseeker 邏輯的異步包裝"""
        
        # 調用現有智能路由
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            smart_router, 
            query, location, results_wanted
        )
        
        return {
            "jobs": result.combined_jobs_data.to_dict('records') if result.combined_jobs_data is not None else [],
            "total_jobs": result.total_jobs,
            "successful_sites": [agent.value for agent in result.successful_agents],
            "confidence_score": result.confidence_score
        }
```

#### Day 11-14: React 前端基礎
```typescript
// frontend/src/types/index.ts
export interface JobListing {
  title: string;
  company: string;
  location: string;
  salary?: string;
  description: string;
  job_url: string;
  site: string;
}

export interface SearchResult {
  jobs: JobListing[];
  total_jobs: number;
  successful_sites: string[];
  confidence_score: number;
}

// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export const searchJobs = async (query: string, location: string = ""): Promise<SearchResult> => {
  const response = await api.post('/search', { query, location });
  return response.data;
};

// frontend/src/components/SearchForm.tsx
import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { searchJobs } from '../services/api';

export const SearchForm: React.FC = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  
  const searchMutation = useMutation({
    mutationFn: ({ query, location }: { query: string; location: string }) =>
      searchJobs(query, location),
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    searchMutation.mutate({ query, location });
  };
  
  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-6">
      <div className="flex gap-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="搜尋職位..."
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="地點 (可選)"
          className="w-48 px-4 py-2 border rounded-lg"
        />
        <button
          type="submit"
          disabled={searchMutation.isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
        >
          {searchMutation.isLoading ? '搜尋中...' : '搜尋'}
        </button>
      </div>
      
      {searchMutation.data && (
        <div className="mt-6">
          <p>找到 {searchMutation.data.total_jobs} 個職位</p>
          {/* 職位列表組件 */}
        </div>
      )}
    </form>
  );
};
```

### **Week 3: AI 視覺整合**

#### Day 15-17: OpenAI Vision API 整合
```python
# backend/services/ai_vision.py
import openai
import base64
from PIL import Image
import io

class AIVisionService:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def analyze_job_page(self, image_data: bytes) -> dict:
        """分析求職頁面截圖"""
        
        # 轉換為 base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user", 
                "content": [
                    {"type": "text", "text": "分析這個求職網站頁面，提取職位信息和可點擊元素位置"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }],
            max_tokens=1000
        )
        
        return {"analysis": response.choices[0].message.content}

# backend/routers/ai.py
from fastapi import APIRouter, UploadFile, File
from services.ai_vision import AIVisionService
import os

router = APIRouter(prefix="/ai", tags=["AI"])
vision_service = AIVisionService(os.getenv("OPENAI_API_KEY"))

@router.post("/analyze-page")
async def analyze_page(file: UploadFile = File(...)):
    content = await file.read()
    result = await vision_service.analyze_job_page(content)
    return result
```

#### Day 18-21: 智能爬蟲引擎
```python
# backend/services/smart_scraper.py
from playwright.async_api import async_playwright
import asyncio
from .ai_vision import AIVisionService

class SmartScraper:
    def __init__(self, vision_service: AIVisionService):
        self.vision_service = vision_service
    
    async def scrape_with_vision(self, url: str) -> dict:
        """使用 AI 視覺的智能爬蟲"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url)
                
                # 截圖
                screenshot = await page.screenshot()
                
                # AI 分析
                analysis = await self.vision_service.analyze_job_page(screenshot)
                
                # TODO: 基於 AI 分析結果進行智能操作
                
                return analysis
                
            finally:
                await browser.close()
```

### **Week 4: 部署與優化**

#### Day 22-24: 生產部署配置
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# frontend/Dockerfile  
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

#### Day 25-28: 性能優化
```python
# backend/middleware/performance.py
import time
from fastapi import Request, Response
import logging

logger = logging.getLogger(__name__)

async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(f"{request.method} {request.url} - {process_time:.2f}s")
    return response

# 緩存配置
from functools import lru_cache
import redis

redis_client = redis.Redis.from_url("redis://localhost:6379")

@lru_cache(maxsize=1000)
async def cached_search(query: str, location: str):
    """緩存搜尋結果"""
    cache_key = f"search:{query}:{location}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
        
    # 執行搜尋邏輯...
    result = await search_jobs(query, location)
    
    # 緩存 1 小時
    redis_client.setex(cache_key, 3600, json.dumps(result))
    return result
```

#### Day 29-30: 監控與測試
```python
# backend/monitoring/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

def track_metrics(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='POST', endpoint='/search').inc()
            return result
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    
    return wrapper

# 健康檢查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "database": await check_database(),
            "redis": await check_redis(),
            "ai_vision": await check_ai_service()
        }
    }
```

---

## 🎯 **遷移檢查清單**

### **技術準備 ✅**
- [ ] Docker 開發環境配置完成
- [ ] FastAPI 基礎架構建立
- [ ] React TypeScript 項目初始化
- [ ] PostgreSQL 數據庫遷移
- [ ] Redis 緩存整合

### **功能遷移 ✅**  
- [ ] 現有 jobseeker 模組整合
- [ ] 智能路由系統遷移
- [ ] 用戶認證系統重構
- [ ] 搜尋結果展示優化
- [ ] CSV/JSON 導出功能

### **AI 增強 ✅**
- [ ] OpenAI Vision API 整合
- [ ] 本地 AI 模型配置
- [ ] 智能爬蟲引擎開發
- [ ] 成本控制機制
- [ ] 性能監控系統

### **部署準備 ✅**
- [ ] 生產環境 Docker 配置
- [ ] CI/CD 流水線建立
- [ ] 環境變數管理
- [ ] 監控和日誌系統
- [ ] 備份和恢復策略

---

## 💰 **成本效益預估**

### **開發投入**
- **開發時間**: 30 天全職開發
- **學習成本**: 1-2 週現代技術棧熟悉
- **總預算**: $30K-50K (含人力和工具成本)

### **預期收益**  
- **性能提升**: 5-10倍響應速度
- **開發效率**: 3倍功能開發速度
- **維護成本**: 50% 減少
- **AI 競爭優勢**: 獨特市場定位
- **擴展能力**: 支持 10倍用戶增長

### **ROI 分析**
- **短期 (6個月)**: 開發效率提升收回成本
- **中期 (1年)**: AI 功能帶來競爭優勢
- **長期 (2-3年)**: 技術領先地位確立

**建議**: 立即開始重構，技術債務清償刻不容緩，AI 整合將成為決定性競爭優勢。