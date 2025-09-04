import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.job_search_service import JobSearchService
from app.models.user import User

@pytest.mark.asyncio
async def test_job_search_basic(db_session: AsyncSession):
    \"\"\"Test basic job search functionality\"\"\"
    async with JobSearchService(db_session) as service:
        results = await service.search_jobs(
            query=\"python developer\",
            location=\"remote\"
        )
        
        assert results[\"total_count\"] > 0
        assert len(results[\"jobs\"]) > 0
        assert \"search_metadata\" in results

@pytest.mark.asyncio
async def test_ai_enhanced_search(db_session: AsyncSession):
    \"\"\"Test AI-enhanced search functionality\"\"\"
    async with JobSearchService(db_session) as service:
        results = await service.search_jobs(
            query=\"machine learning engineer\",
            use_ai=True
        )
        
        assert results[\"search_metadata\"][\"ai_enhancement_used\"] is True
        assert results[\"total_count\"] > 0

@pytest.mark.asyncio
async def test_search_filters(db_session: AsyncSession):
    \"\"\"Test search with filters\"\"\"
    async with JobSearchService(db_session) as service:
        results = await service.search_jobs(
            query=\"software engineer\",
            job_type=\"full-time\",
            experience_level=\"senior\",
            salary_range={\"min\": 100000, \"max\": 150000}
        )
        
        # Verify filters are applied
        for job in results[\"jobs\"][:5]:  # Check first 5 jobs
            if job.get(\"job_type\"):
                assert job[\"job_type\"].lower() == \"full-time\"
            if job.get(\"salary_range\"):
                salary = job[\"salary_range\"]
                assert salary.get(\"min\", 0) >= 100000 or salary.get(\"max\", 0) <= 150000