from fastapi import APIRouter
from .jobs import router as jobs_router
from .auth import router as auth_router
from .storage import router as storage_router

api_router = APIRouter()
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(storage_router, tags=["storage"])