from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="JobSpy v2 API",
    description="Modern AI-enhanced job search platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路徑 - API 狀態檢查"""
    return {
        "message": "JobSpy v2 API is running",
        "version": "2.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-04T17:00:00Z"
    }

@app.get("/api/v1/jobs")
async def get_jobs():
    """獲取職位列表"""
    return {
        "jobs": [
            {
                "id": 1,
                "title": "Frontend Developer",
                "company": "Tech Corp",
                "location": "台北市",
                "salary": "60,000 - 80,000",
                "description": "負責前端開發工作"
            },
            {
                "id": 2,
                "title": "Backend Developer",
                "company": "Software Inc",
                "location": "新北市",
                "salary": "70,000 - 90,000",
                "description": "負責後端 API 開發"
            }
        ],
        "total": 2
    }

@app.post("/api/v1/search")
async def search_jobs(query: dict):
    """搜索職位"""
    return {
        "query": query,
        "results": [
            {
                "id": 1,
                "title": "Software Engineer",
                "company": "Example Corp",
                "location": "台北市",
                "match_score": 0.95
            }
        ],
        "total": 1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
