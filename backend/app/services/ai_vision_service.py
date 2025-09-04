"""
AI Vision service with OpenAI GPT-4V and local VLM backup
"""
import asyncio
import hashlib
import base64
from io import BytesIO
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
from PIL import Image
import openai

from ..core.config import settings
from ..core.redis import redis_manager, CacheKey
from ..models.ai import AIAnalysisCache, AIUsageStats


class AIVisionService:
    """AI Vision analysis service with cost optimization"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.max_cost_threshold = settings.max_ai_cost_per_day
        
    async def analyze_job_page(
        self,
        url: str,
        fallback_to_local: bool = True
    ) -> Dict[str, Any]:
        """
        Three-layer analysis strategy:
        1. Try API extraction
        2. Try traditional scraping
        3. AI vision analysis (with cost control)
        """
        
        # Layer 1: Try API extraction
        api_result = await self._try_api_extraction(url)
        if api_result:
            return {
                "success": True,
                "method": "api",
                "data": api_result,
                "cost": 0.0
            }
        
        # Layer 2: Try traditional scraping
        scraping_result = await self._try_scraping(url)
        if scraping_result:
            return {
                "success": True,
                "method": "scraping",
                "data": scraping_result,
                "cost": 0.0
            }
        
        # Layer 3: AI vision analysis
        return await self._ai_vision_analysis(url, fallback_to_local)
    
    async def _try_api_extraction(self, url: str) -> Optional[Dict[str, Any]]:
        """Try to extract job data using official APIs"""
        # Check if URL is from a platform with API support
        if "indeed.com" in url:
            return await self._extract_indeed_api(url)
        elif "linkedin.com" in url:
            return await self._extract_linkedin_api(url)
        
        return None
    
    async def _try_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """Try traditional web scraping methods"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_job_html(html)
        except Exception:
            pass
        
        return None
    
    async def _ai_vision_analysis(
        self, 
        url: str, 
        fallback_to_local: bool = True
    ) -> Dict[str, Any]:
        """AI vision analysis with cost control"""
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Check cache first
        cached_result = await redis_manager.get(CacheKey.ai_analysis(url_hash))
        if cached_result:
            return cached_result
        
        # Check daily cost limit
        daily_cost = await self._get_daily_ai_cost()
        if daily_cost >= self.max_cost_threshold:
            if fallback_to_local:
                return await self._local_vlm_analysis(url)
            else:
                return {
                    "success": False,
                    "error": "Daily AI cost limit exceeded",
                    "cost": 0.0
                }
        
        # Estimate cost before proceeding
        estimated_cost = await self._estimate_analysis_cost(url)
        if daily_cost + estimated_cost > self.max_cost_threshold:
            if fallback_to_local:
                return await self._local_vlm_analysis(url)
            else:
                return {
                    "success": False,
                    "error": "Analysis would exceed daily cost limit",
                    "cost": 0.0
                }
        
        # Proceed with cloud AI analysis
        return await self._cloud_ai_analysis(url, url_hash)
    
    async def _cloud_ai_analysis(self, url: str, url_hash: str) -> Dict[str, Any]:
        """Perform cloud AI analysis using OpenAI GPT-4V"""
        try:
            # Take screenshot
            screenshot = await self._take_screenshot(url)
            if not screenshot:
                return {
                    "success": False,
                    "error": "Failed to take screenshot",
                    "cost": 0.0
                }
            
            # Encode image
            image_base64 = base64.b64encode(screenshot).decode('utf-8')
            
            # Prepare prompt for job extraction
            prompt = """
            Analyze this job posting page and extract the following information in JSON format:
            {
                "job_title": "exact job title",
                "company": "company name",
                "location": "job location",
                "job_type": "full-time/part-time/contract",
                "experience_level": "entry/mid/senior",
                "salary_range": {"min": number, "max": number, "currency": "USD"},
                "requirements": ["list", "of", "requirements"],
                "skills": ["list", "of", "skills"],
                "description": "job description summary",
                "benefits": ["list", "of", "benefits"],
                "remote_friendly": true/false
            }
            
            If any information is not visible or available, use null for that field.
            """
            
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=settings.openai_max_tokens
            )
            
            # Extract and parse result
            analysis_text = response.choices[0].message.content
            
            # Calculate cost (estimate based on tokens)
            cost = self._calculate_cost(response.usage)
            
            # Parse JSON from response
            import json
            try:
                job_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback: extract JSON from text
                job_data = self._extract_json_from_text(analysis_text)
            
            result = {
                "success": True,
                "method": "ai_vision_cloud",
                "data": job_data,
                "cost": cost,
                "model": settings.openai_model,
                "confidence": 0.9  # High confidence for GPT-4V
            }
            
            # Cache result
            await redis_manager.set(
                CacheKey.ai_analysis(url_hash),
                result,
                ttl=timedelta(hours=24)
            )
            
            # Update daily cost
            await self._update_daily_cost(cost)
            
            # Store in database
            await self._store_analysis_result(url, url_hash, result)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI analysis failed: {str(e)}",
                "cost": 0.0
            }
    
    async def _local_vlm_analysis(self, url: str) -> Dict[str, Any]:
        """Local VLM analysis as backup (using CLIP or similar)"""
        # Placeholder for local VLM implementation
        # In real implementation, this would use a local vision model
        await asyncio.sleep(1)  # Simulate processing time
        
        return {
            "success": True,
            "method": "ai_vision_local",
            "data": {
                "job_title": "Extracted via local VLM",
                "company": "Local Analysis",
                "confidence": "medium"
            },
            "cost": 0.0,
            "model": "local_clip",
            "confidence": 0.7  # Lower confidence for local model
        }
    
    async def _take_screenshot(self, url: str) -> Optional[bytes]:
        """Take screenshot of webpage"""
        # Placeholder for screenshot functionality
        # In real implementation, use selenium, playwright, or similar
        try:
            # Create a simple placeholder image
            img = Image.new('RGB', (1920, 1080), color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
        except Exception:
            return None
    
    async def _estimate_analysis_cost(self, url: str) -> float:
        """Estimate cost of AI analysis"""
        # GPT-4V pricing estimate (approximate)
        base_cost = 0.01  # Base cost for image analysis
        text_cost = 0.03  # Additional cost for text processing
        return base_cost + text_cost
    
    async def _get_daily_ai_cost(self) -> float:
        """Get current daily AI cost"""
        today = datetime.utcnow().date().isoformat()
        cost_key = f"ai_cost:{today}"
        
        daily_cost = await redis_manager.get(cost_key)
        return float(daily_cost) if daily_cost else 0.0
    
    async def _update_daily_cost(self, cost: float):
        """Update daily AI cost counter"""
        today = datetime.utcnow().date().isoformat()
        cost_key = f"ai_cost:{today}"
        
        await redis_manager.increment(cost_key, int(cost * 10000))  # Store as cents
        await redis_manager.expire(cost_key, timedelta(days=1))
    
    def _calculate_cost(self, usage) -> float:
        """Calculate actual cost from OpenAI usage"""
        # GPT-4V pricing (approximate)
        input_cost_per_token = 0.01 / 1000
        output_cost_per_token = 0.03 / 1000
        
        input_cost = usage.prompt_tokens * input_cost_per_token
        output_cost = usage.completion_tokens * output_cost_per_token
        
        return input_cost + output_cost
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from AI response text"""
        import re
        import json
        
        # Try to find JSON in the text
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Fallback to basic extraction
        return {
            "job_title": "Could not extract",
            "company": "Could not extract",
            "raw_response": text
        }
    
    async def _store_analysis_result(
        self, 
        url: str, 
        url_hash: str, 
        result: Dict[str, Any]
    ):
        """Store analysis result in database"""
        # This would store in AIAnalysisCache model
        pass
    
    # Platform-specific API extraction methods
    async def _extract_indeed_api(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract job data using Indeed API"""
        # Placeholder for Indeed API integration
        return None
    
    async def _extract_linkedin_api(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract job data using LinkedIn API"""
        # Placeholder for LinkedIn API integration
        return None
    
    def _parse_job_html(self, html: str) -> Optional[Dict[str, Any]]:
        """Parse job information from HTML"""
        # Placeholder for HTML parsing logic
        return None