"""
Job search service with multi-platform integration
"""
import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.redis import redis_manager, CacheKey
from ..models.job import JobListing
from ..models.search import SearchLog


class JobSearchService:
    """Core job search service with multi-platform support"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_range: Optional[Dict] = None,
        user_id: Optional[str] = None,
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        Unified job search across multiple platforms
        """
        start_time = datetime.utcnow()
        
        # Generate cache key
        search_params = {
            "query": query,
            "location": location,
            "job_type": job_type,
            "experience_level": experience_level,
            "salary_range": salary_range
        }
        cache_key = self._generate_cache_key(search_params)
        
        # Try cache first
        cached_result = await redis_manager.get(CacheKey.job_search_result(cache_key))
        if cached_result:
            return cached_result
        
        # Search all platforms in parallel
        search_tasks = [
            self._search_indeed(query, location, job_type),
            self._search_linkedin(query, location, job_type),
            self._search_glassdoor(query, location, job_type)
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine and process results
        all_jobs = []
        sources_used = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            
            all_jobs.extend(result.get('jobs', []))
            if result.get('jobs'):
                sources_used.append(['indeed', 'linkedin', 'glassdoor'][i])
        
        # Remove duplicates and rank results
        unique_jobs = self._deduplicate_jobs(all_jobs)
        ranked_jobs = self._rank_jobs(unique_jobs, query)
        
        # Apply filters
        filtered_jobs = self._apply_filters(
            ranked_jobs, 
            job_type, 
            experience_level, 
            salary_range
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Prepare response
        response = {
            "jobs": filtered_jobs[:50],  # Limit to 50 results
            "total_count": len(filtered_jobs),
            "search_metadata": {
                "query_analysis": self._analyze_query(query),
                "sources_used": sources_used,
                "ai_enhancement_used": use_ai,
                "processing_time_ms": int(processing_time)
            },
            "pagination": {
                "page": 1,
                "per_page": 50,
                "total_pages": (len(filtered_jobs) + 49) // 50
            }
        }
        
        # Cache results
        await redis_manager.set(
            CacheKey.job_search_result(cache_key),
            response,
            ttl=timedelta(hours=1)
        )
        
        # Log search
        await self._log_search(
            user_id=user_id,
            query=query,
            filters=search_params,
            results_count=len(filtered_jobs),
            processing_time_ms=int(processing_time),
            ai_used=use_ai,
            sources_used=sources_used
        )
        
        return response
    
    async def _search_indeed(
        self, 
        query: str, 
        location: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search Indeed for jobs"""
        # Placeholder for Indeed API integration
        # In real implementation, this would call Indeed's API
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "jobs": [
                {
                    "id": f"indeed_job_{i}",
                    "title": f"Software Engineer {i}",
                    "company": f"Tech Company {i}",
                    "location": location or "Remote",
                    "description": f"Job description for {query}",
                    "source": "indeed",
                    "source_url": f"https://indeed.com/job/{i}",
                    "posted_date": datetime.utcnow().isoformat(),
                    "job_type": job_type or "full-time",
                    "salary_range": {"min": 80000, "max": 120000}
                }
                for i in range(10)
            ]
        }
    
    async def _search_linkedin(
        self, 
        query: str, 
        location: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search LinkedIn for jobs"""
        # Placeholder for LinkedIn API integration
        await asyncio.sleep(0.1)  # Simulate API call
        
        return {
            "jobs": [
                {
                    "id": f"linkedin_job_{i}",
                    "title": f"Senior Developer {i}",
                    "company": f"Innovation Corp {i}",
                    "location": location or "Hybrid",
                    "description": f"LinkedIn job for {query}",
                    "source": "linkedin",
                    "source_url": f"https://linkedin.com/jobs/{i}",
                    "posted_date": datetime.utcnow().isoformat(),
                    "job_type": job_type or "full-time",
                    "salary_range": {"min": 90000, "max": 140000}
                }
                for i in range(8)
            ]
        }
    
    async def _search_glassdoor(
        self, 
        query: str, 
        location: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search Glassdoor for jobs"""
        # Placeholder for Glassdoor scraping
        await asyncio.sleep(0.1)  # Simulate scraping
        
        return {
            "jobs": [
                {
                    "id": f"glassdoor_job_{i}",
                    "title": f"Lead Engineer {i}",
                    "company": f"Growth Startup {i}",
                    "location": location or "On-site",
                    "description": f"Glassdoor opportunity for {query}",
                    "source": "glassdoor",
                    "source_url": f"https://glassdoor.com/job/{i}",
                    "posted_date": datetime.utcnow().isoformat(),
                    "job_type": job_type or "full-time",
                    "salary_range": {"min": 75000, "max": 110000}
                }
                for i in range(6)
            ]
        }
    
    def _generate_cache_key(self, params: Dict) -> str:
        """Generate cache key from search parameters"""
        params_str = str(sorted(params.items()))
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.get('title', '').lower(), job.get('company', '').lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _rank_jobs(self, jobs: List[Dict], query: str) -> List[Dict]:
        """Rank jobs based on relevance to query"""
        query_words = set(query.lower().split())
        
        for job in jobs:
            title_words = set(job.get('title', '').lower().split())
            description_words = set(job.get('description', '').lower().split())
            
            # Calculate relevance score
            title_match = len(query_words.intersection(title_words))
            description_match = len(query_words.intersection(description_words))
            
            job['relevance_score'] = title_match * 2 + description_match
        
        return sorted(jobs, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _apply_filters(
        self,
        jobs: List[Dict],
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        salary_range: Optional[Dict] = None
    ) -> List[Dict]:
        """Apply filters to job results"""
        filtered_jobs = jobs
        
        if job_type:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get('job_type', '').lower() == job_type.lower()
            ]
        
        if salary_range:
            min_salary = salary_range.get('min', 0)
            max_salary = salary_range.get('max', float('inf'))
            
            filtered_jobs = [
                job for job in filtered_jobs
                if self._salary_in_range(job.get('salary_range'), min_salary, max_salary)
            ]
        
        return filtered_jobs
    
    def _salary_in_range(
        self, 
        job_salary: Optional[Dict], 
        min_salary: int, 
        max_salary: int
    ) -> bool:
        """Check if job salary is within range"""
        if not job_salary:
            return True
        
        job_min = job_salary.get('min', 0)
        job_max = job_salary.get('max', 0)
        
        return job_min >= min_salary or job_max <= max_salary
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze search query for insights"""
        return {
            "extracted_skills": [],
            "job_level": "mid",
            "query_type": "keyword_search",
            "suggested_improvements": []
        }
    
    async def _log_search(
        self,
        user_id: Optional[str],
        query: str,
        filters: Dict,
        results_count: int,
        processing_time_ms: int,
        ai_used: bool,
        sources_used: List[str]
    ):
        """Log search for analytics"""
        search_log = SearchLog(
            user_id=user_id,
            query_text=query,
            filters=filters,
            results_count=results_count,
            processing_time_ms=processing_time_ms,
            ai_used=ai_used,
            sources_used=sources_used
        )
        
        self.db.add(search_log)
        await self.db.commit()