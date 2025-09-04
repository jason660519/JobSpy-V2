"""
Job search API endpoints
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ...core.database import get_db
from ...core.deps import get_current_active_user
from ...services.job_search_service import JobSearchService
from ...models.user import User

router = APIRouter()

class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[Dict[str, int]] = None
    use_ai: bool = True

class JobSearchResponse(BaseModel):
    jobs: list
    total_count: int
    search_metadata: dict
    pagination: dict

@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(
    search_request: JobSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for jobs across multiple platforms"""
    
    async with JobSearchService(db) as job_service:
        results = await job_service.search_jobs(
            query=search_request.query,
            location=search_request.location,
            job_type=search_request.job_type,
            experience_level=search_request.experience_level,
            salary_range=search_request.salary_range,
            user_id=current_user.id,
            use_ai=search_request.use_ai
        )
    
    return JobSearchResponse(**results)

@router.get("/search")
async def search_jobs_get(
    query: str = Query(..., description="Job search query"),
    location: Optional[str] = Query(None, description="Job location"),
    job_type: Optional[str] = Query(None, description="Job type (full-time, part-time, contract)"),
    experience_level: Optional[str] = Query(None, description="Experience level (entry, mid, senior)"),
    use_ai: bool = Query(True, description="Use AI enhancement"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for jobs using GET method"""
    
    async with JobSearchService(db) as job_service:
        results = await job_service.search_jobs(
            query=query,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            user_id=current_user.id,
            use_ai=use_ai
        )
    
    return results