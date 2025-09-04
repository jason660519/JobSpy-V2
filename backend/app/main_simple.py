"""
Simplified FastAPI app for testing without database
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI(
    title="JobSpy v2 API - Simple Mode",
    description="Modern AI-enhanced job search platform (Database-free mode)",
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

class JobSearchRequest(BaseModel):
    query: str
    location: str = None
    job_type: str = None

class JobSearchResponse(BaseModel):
    jobs: list
    total_count: int
    message: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "JobSpy v2 - AI-Enhanced Job Search Platform",
        "version": "2.0.0",
        "status": "operational (simple mode)",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "mode": "simple",
        "timestamp": time.time()
    }

@app.post("/api/v1/jobs/search", response_model=JobSearchResponse)
async def search_jobs_demo(request: JobSearchRequest):
    """Demo job search endpoint"""
    # Simulate job search results
    demo_jobs = [
        {
            "id": "demo_1",
            "title": f"Senior {request.query.title()} Developer",
            "company": "Tech Innovation Corp",
            "location": request.location or "Remote",
            "salary_range": {"min": 80000, "max": 120000, "currency": "USD"},
            "job_type": request.job_type or "full-time",
            "description": f"Exciting opportunity for a {request.query} professional...",
            "source": "demo",
            "posted_date": "2024-01-01"
        },
        {
            "id": "demo_2", 
            "title": f"{request.query.title()} Specialist",
            "company": "Future Systems Ltd",
            "location": request.location or "Hybrid",
            "salary_range": {"min": 70000, "max": 100000, "currency": "USD"},
            "job_type": request.job_type or "full-time",
            "description": f"Join our team as a {request.query} expert...",
            "source": "demo",
            "posted_date": "2024-01-02"
        }
    ]
    
    return JobSearchResponse(
        jobs=demo_jobs,
        total_count=len(demo_jobs),
        message=f"Demo search results for '{request.query}'"
    )

@app.get("/api/v1/jobs/search")
async def search_jobs_demo_get(
    query: str,
    location: str = None,
    job_type: str = None
):
    """Demo job search endpoint (GET method)"""
    request = JobSearchRequest(query=query, location=location, job_type=job_type)
    return await search_jobs_demo(request)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting JobSpy v2 Backend (Simple Mode)")
    print("📡 Backend: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)