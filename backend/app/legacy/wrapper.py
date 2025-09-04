import asyncio
from typing import Dict, List, Any
import sys
from pathlib import Path

# Import original JobSpy
original_path = Path(__file__).parent.parent / "legacy"
sys.path.insert(0, str(original_path))

from jobseeker import scrape_jobs
from jobseeker.smart_router import smart_router

class LegacyJobSearchWrapper:
    """Async wrapper for original JobSpy functionality"""
    
    async def search_jobs_async(self, query: str, location: str = "", results_wanted: int = 20) -> Dict[str, Any]:
        """Async wrapper for original job search"""
        loop = asyncio.get_event_loop()
        
        # Run original synchronous function in thread pool
        result = await loop.run_in_executor(
            None,
            lambda: smart_router(query, location, results_wanted)
        )
        
        return {
            "jobs": result.combined_jobs_data.to_dict('records') if result.combined_jobs_data is not None else [],
            "total_jobs": result.total_jobs,
            "successful_agents": [agent.value for agent in result.successful_agents],
            "confidence_score": result.confidence_score,
            "processing_time": getattr(result, 'processing_time', 0)
        }
    
    async def scrape_specific_site(self, site: str, query: str, location: str, results: int) -> List[Dict]:
        """Async wrapper for site-specific scraping"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            lambda: scrape_jobs(site, query, location, results)
        )
        
        return result.to_dict('records') if hasattr(result, 'to_dict') else []