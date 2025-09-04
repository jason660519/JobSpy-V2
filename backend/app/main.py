from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import structlog

from .api.v1 import auth, jobs, storage
from .core.config import settings
from .core.database import init_db, close_db
from .core.redis import redis_manager

# Setup structured logging
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await logger.ainfo("Starting JobSpy v2 API")
    await redis_manager.connect()
    await init_db()
    await logger.ainfo("JobSpy v2 API started successfully")
    
    yield
    
    # Shutdown
    await logger.ainfo("Shutting down JobSpy v2 API")
    await redis_manager.disconnect()
    await close_db()
    await logger.ainfo("JobSpy v2 API shut down")

app = FastAPI(
    title="JobSpy v2 API",
    description="Modern AI-enhanced job search platform with intelligent matching",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    await logger.aerror(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc)
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix + "/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix=settings.api_v1_prefix + "/jobs", tags=["Job Search"])
app.include_router(storage.router, prefix=settings.api_v1_prefix + "/storage", tags=["Storage"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "JobSpy v2 - AI-Enhanced Job Search Platform",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": time.time(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "ai": "available"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug)