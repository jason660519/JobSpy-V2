"""AI視覺分析服務

基於GPT-4V的智能視覺分析，用於解析網頁截圖並提取職位信息。
"""

import asyncio
import base64
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import structlog
from openai import AsyncOpenAI
from PIL import Image
import io

from .prompt_manager import PromptManager
from .cost_tracker import CostTracker
from ..config import AIConfig

logger = structlog.get_logger(__name__)


@dataclass
class VisionAnalysisRequest:
    """視覺分析請求"""
    image_data: bytes
    analysis_type: str  # 'job_listing', 'search_results', 'job_details'
    platform: str
    search_query: Optional[str] = None
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class VisionAnalysisResult:
    """視覺分析結果"""
    success: bool
    jobs: List[Dict[str, Any]]
    confidence_score: float
    analysis_time: float
    tokens_used: int
    cost_usd: float
    error_message: Optional[str] = None
    raw_response: Optional[str] = None


class AIVisionService:
    """AI視覺分析服務
    
    使用GPT-4V分析網頁截圖，智能提取職位信息。
    """
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.logger = logger.bind(component="ai_vision_service")
        
        # 初始化OpenAI客戶端
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url
        )
        
        # 初始化組件
        self.prompt_manager = PromptManager()
        self.cost_tracker = CostTracker()
        
        # 模型配置
        self.model = config.vision_model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        
        # 圖像處理配置
        self.max_image_size = (1920, 1080)  # 最大圖像尺寸
        self.image_quality = 85  # JPEG質量
    
    async def analyze_screenshot(self, request: VisionAnalysisRequest) -> VisionAnalysisResult:
        """分析網頁截圖
        
        Args:
            request: 視覺分析請求
            
        Returns:
            VisionAnalysisResult: 分析結果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.logger.info(
                "開始視覺分析",
                analysis_type=request.analysis_type,
                platform=request.platform,
                image_size=len(request.image_data)
            )
            
            # 檢查成本限制
            if not await self._check_cost_limits():
                return VisionAnalysisResult(
                    success=False,
                    jobs=[],
                    confidence_score=0.0,
                    analysis_time=0.0,
                    tokens_used=0,
                    cost_usd=0.0,
                    error_message="已達到成本限制"
                )
            
            # 預處理圖像
            processed_image = await self._preprocess_image(request.image_data)
            
            # 生成提示詞
            prompt = await self.prompt_manager.generate_prompt(
                request.analysis_type,
                request.platform,
                request.search_query,
                request.additional_context
            )
            
            # 調用GPT-4V
            response = await self._call_gpt4v(processed_image, prompt)
            
            # 解析響應
            jobs, confidence = await self._parse_response(response.choices[0].message.content)
            
            # 計算成本
            tokens_used = response.usage.total_tokens
            cost_usd = await self.cost_tracker.calculate_cost(
                self.model, 
                tokens_used, 
                has_image=True
            )
            
            # 記錄成本
            await self.cost_tracker.record_usage(
                model=self.model,
                tokens=tokens_used,
                cost=cost_usd,
                request_type="vision_analysis"
            )
            
            analysis_time = asyncio.get_event_loop().time() - start_time
            
            result = VisionAnalysisResult(
                success=True,
                jobs=jobs,
                confidence_score=confidence,
                analysis_time=analysis_time,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                raw_response=response.choices[0].message.content
            )
            
            self.logger.info(
                "視覺分析完成",
                jobs_found=len(jobs),
                confidence=confidence,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                analysis_time=analysis_time
            )
            
            return result
            
        except Exception as e:
            analysis_time = asyncio.get_event_loop().time() - start_time
            
            self.logger.error(
                "視覺分析失敗",
                error=str(e),
                analysis_type=request.analysis_type,
                platform=request.platform
            )
            
            return VisionAnalysisResult(
                success=False,
                jobs=[],
                confidence_score=0.0,
                analysis_time=analysis_time,
                tokens_used=0,
                cost_usd=0.0,
                error_message=str(e)
            )
    
    async def analyze_job_listing(self, image_data: bytes, platform: str, 
                                search_query: str = None) -> VisionAnalysisResult:
        """分析職位列表頁面"""
        request = VisionAnalysisRequest(
            image_data=image_data,
            analysis_type="job_listing",
            platform=platform,
            search_query=search_query
        )
        return await self.analyze_screenshot(request)
    
    async def analyze_job_details(self, image_data: bytes, platform: str, 
                                job_url: str = None) -> VisionAnalysisResult:
        """分析職位詳情頁面"""
        request = VisionAnalysisRequest(
            image_data=image_data,
            analysis_type="job_details",
            platform=platform,
            additional_context={"job_url": job_url}
        )
        return await self.analyze_screenshot(request)
    
    async def analyze_search_results(self, image_data: bytes, platform: str, 
                                   search_query: str) -> VisionAnalysisResult:
        """分析搜索結果頁面"""
        request = VisionAnalysisRequest(
            image_data=image_data,
            analysis_type="search_results",
            platform=platform,
            search_query=search_query
        )
        return await self.analyze_screenshot(request)
    
    async def _preprocess_image(self, image_data: bytes) -> str:
        """預處理圖像
        
        Args:
            image_data: 原始圖像數據
            
        Returns:
            str: Base64編碼的圖像
        """
        try:
            # 打開圖像
            image = Image.open(io.BytesIO(image_data))
            
            # 轉換為RGB（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 調整大小（如果太大）
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
            
            # 壓縮圖像
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.image_quality, optimize=True)
            compressed_data = output.getvalue()
            
            # Base64編碼
            base64_image = base64.b64encode(compressed_data).decode('utf-8')
            
            self.logger.debug(
                "圖像預處理完成",
                original_size=len(image_data),
                compressed_size=len(compressed_data),
                dimensions=image.size
            )
            
            return base64_image
            
        except Exception as e:
            self.logger.error("圖像預處理失敗", error=str(e))
            raise
    
    async def _call_gpt4v(self, base64_image: str, prompt: str) -> Any:
        """調用GPT-4V API
        
        Args:
            base64_image: Base64編碼的圖像
            prompt: 提示詞
            
        Returns:
            API響應
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response
            
        except Exception as e:
            self.logger.error("GPT-4V API調用失敗", error=str(e))
            raise
    
    async def _parse_response(self, response_text: str) -> Tuple[List[Dict[str, Any]], float]:
        """解析GPT-4V響應
        
        Args:
            response_text: GPT-4V的響應文本
            
        Returns:
            Tuple[List[Dict[str, Any]], float]: 職位列表和置信度分數
        """
        try:
            # 嘗試解析JSON響應
            if response_text.strip().startswith('{') or response_text.strip().startswith('['):
                data = json.loads(response_text)
            else:
                # 如果不是純JSON，嘗試提取JSON部分
                import re
                json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(1))
                else:
                    # 如果找不到JSON，使用文本解析
                    return await self._parse_text_response(response_text)
            
            # 標準化數據格式
            if isinstance(data, dict):
                jobs = data.get('jobs', [])
                confidence = data.get('confidence', 0.8)
            elif isinstance(data, list):
                jobs = data
                confidence = 0.8
            else:
                jobs = []
                confidence = 0.0
            
            # 驗證和清理職位數據
            validated_jobs = await self._validate_jobs(jobs)
            
            return validated_jobs, confidence
            
        except json.JSONDecodeError as e:
            self.logger.warning("JSON解析失敗，嘗試文本解析", error=str(e))
            return await self._parse_text_response(response_text)
        except Exception as e:
            self.logger.error("響應解析失敗", error=str(e))
            return [], 0.0
    
    async def _parse_text_response(self, text: str) -> Tuple[List[Dict[str, Any]], float]:
        """解析文本格式的響應"""
        jobs = []
        confidence = 0.6  # 文本解析的置信度較低
        
        try:
            # 簡單的文本解析邏輯
            lines = text.split('\n')
            current_job = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_job:
                        jobs.append(current_job)
                        current_job = {}
                    continue
                
                # 嘗試識別職位信息
                if line.lower().startswith('title:') or line.lower().startswith('職位:'):
                    current_job['title'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('company:') or line.lower().startswith('公司:'):
                    current_job['company'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('location:') or line.lower().startswith('地點:'):
                    current_job['location'] = line.split(':', 1)[1].strip()
                elif line.lower().startswith('salary:') or line.lower().startswith('薪資:'):
                    current_job['salary'] = line.split(':', 1)[1].strip()
            
            # 添加最後一個職位
            if current_job:
                jobs.append(current_job)
            
        except Exception as e:
            self.logger.error("文本解析失敗", error=str(e))
        
        return jobs, confidence
    
    async def _validate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """驗證和清理職位數據"""
        validated_jobs = []
        
        for job in jobs:
            if not isinstance(job, dict):
                continue
            
            # 確保必需字段存在
            validated_job = {
                'title': job.get('title', '').strip(),
                'company': job.get('company', '').strip(),
                'location': job.get('location', '').strip(),
                'description': job.get('description', '').strip(),
                'salary': job.get('salary', '').strip(),
                'url': job.get('url', '').strip(),
                'posted_date': job.get('posted_date', '').strip(),
                'employment_type': job.get('employment_type', '').strip()
            }
            
            # 過濾空職位
            if validated_job['title'] and validated_job['company']:
                validated_jobs.append(validated_job)
        
        return validated_jobs
    
    async def _check_cost_limits(self) -> bool:
        """檢查成本限制"""
        daily_cost = await self.cost_tracker.get_daily_cost()
        monthly_cost = await self.cost_tracker.get_monthly_cost()
        
        if daily_cost >= self.config.daily_cost_limit:
            self.logger.warning("已達到每日成本限制", daily_cost=daily_cost)
            return False
        
        if monthly_cost >= self.config.monthly_cost_limit:
            self.logger.warning("已達到每月成本限制", monthly_cost=monthly_cost)
            return False
        
        return True
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """獲取使用統計"""
        return await self.cost_tracker.get_usage_stats()
    
    async def cleanup(self):
        """清理資源"""
        await self.client.close()
        self.logger.info("AI視覺服務已清理")