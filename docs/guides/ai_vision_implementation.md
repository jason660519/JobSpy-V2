# AI Vision-Enhanced Scraping Implementation

## 🤖 **AI 視覺辨識爬蟲引擎架構**

### **核心概念：視覺理解 + 智能爬蟲**

傳統爬蟲依賴 DOM 結構和 CSS 選擇器，容易被反爬蟲機制破解。AI 視覺辨識爬蟲模擬人眼識別，大幅提升成功率和適應性。

---

## 🔧 **技術實現架構**

### **1. AI Vision Service 核心模組**

```python
# ai_vision/core.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Union
import asyncio
import time

class ProcessingStrategy(Enum):
    API_ONLY = "api_only"      # 純雲端 API
    LOCAL_ONLY = "local_only"  # 純本地模型  
    HYBRID = "hybrid"          # 混合模式

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    apply_button_location: Optional[dict] = None
    confidence: float = 0.0

@dataclass
class VisionAnalysisResult:
    processing_time_ms: int
    confidence_score: float
    strategy_used: ProcessingStrategy
    job_listings: List[JobListing]
    page_type: str = "unknown"
    errors: List[str] = None

class AIVisionService:
    def __init__(self, config):
        self.config = config
        self.openai_client = None
        self.local_model = None
        self._initialize_clients()
    
    async def analyze_job_page(
        self,
        image_input: Union[str, bytes],
        strategy: Optional[ProcessingStrategy] = None
    ) -> VisionAnalysisResult:
        """分析求職網站頁面截圖"""
        start_time = time.time()
        
        try:
            if strategy == ProcessingStrategy.HYBRID:
                result = await self._process_hybrid(image_input)
            elif strategy == ProcessingStrategy.API_ONLY:
                result = await self._process_with_apis(image_input)
            else:
                result = await self._process_with_local_model(image_input)
                
            result.processing_time_ms = int((time.time() - start_time) * 1000)
            return result
            
        except Exception as e:
            return VisionAnalysisResult(
                processing_time_ms=int((time.time() - start_time) * 1000),
                confidence_score=0.0,
                strategy_used=strategy,
                job_listings=[],
                errors=[str(e)]
            )
```

### **2. OpenAI GPT-4 Vision 客戶端**

```python
# ai_vision/clients/openai_client.py
import openai
import json
import base64
from PIL import Image
import io

class OpenAIVisionClient:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
        self.job_analysis_prompt = """
        分析這張求職網站截圖，提取職位信息：
        1. 職位標題、公司名稱、工作地點、薪資
        2. 申請按鈕位置座標
        3. 頁面類型判斷
        
        返回JSON格式：
        {
            "job_listings": [{
                "title": "職位標題",
                "company": "公司名稱",
                "location": "地點",
                "salary": "薪資或null",
                "apply_button": {"x": 100, "y": 200, "confidence": 0.9}
            }],
            "page_type": "job_list|job_detail",
            "confidence": 0.9
        }
        """
    
    async def analyze_job_page(self, image: Image.Image) -> Dict:
        image_base64 = await self._image_to_base64(image)
        
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": self.job_analysis_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }],
            max_tokens=2000,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    async def _image_to_base64(self, image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
```

### **3. 本地 AI 模型實現**

```python
# ai_vision/models/local_models.py
import torch
from transformers import CLIPProcessor, CLIPModel
import easyocr
import cv2
import numpy as np
from PIL import Image

class LocalVisionModel:
    def __init__(self, device="cpu"):
        self.device = device
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.ocr_reader = easyocr.Reader(['en', 'zh_sim', 'zh_tra'])
        
        if device == "cuda" and torch.cuda.is_available():
            self.clip_model = self.clip_model.cuda()
    
    async def analyze_image(self, image: Image.Image) -> Dict:
        # 1. OCR 文字識別
        text_results = await self._extract_text_with_positions(image)
        
        # 2. CLIP 語義分析
        semantic_results = await self._semantic_analysis(image)
        
        # 3. 提取職位信息
        job_listings = await self._extract_job_listings(text_results, semantic_results)
        
        return {
            "job_listings": job_listings,
            "confidence": self._calculate_confidence(text_results, job_listings)
        }
    
    async def _extract_text_with_positions(self, image: Image.Image) -> List[Dict]:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        results = self.ocr_reader.readtext(opencv_image)
        
        text_data = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                text_data.append({
                    "text": text,
                    "bbox": {"x": int(x1), "y": int(y1), "width": int(x2-x1), "height": int(y2-y1)},
                    "confidence": confidence
                })
        return text_data
```

---

## 🚀 **智能爬蟲整合**

### **視覺導向爬蟲引擎**

```python
# scraping/vision_scraper.py
from playwright.async_api import async_playwright
import asyncio
from ai_vision.core import AIVisionService, ProcessingStrategy

class VisionEnhancedScraper:
    def __init__(self, vision_service: AIVisionService):
        self.vision_service = vision_service
        self.playwright = None
        self.browser = None
    
    async def scrape_job_site(self, url: str, search_params: Dict) -> List[Dict]:
        """使用 AI 視覺輔助的智能爬蟲"""
        
        async with async_playwright() as p:
            # 啟動瀏覽器 (反偵測配置)
            browser = await p.chromium.launch(
                headless=False,  # 開發階段可視化
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            page = await browser.new_page()
            
            # 設定人類行為模擬
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            try:
                # 1. 導航到目標頁面
                await page.goto(url, wait_until='networkidle')
                await self._random_delay(1, 3)
                
                # 2. 截圖分析
                screenshot = await page.screenshot(full_page=True)
                vision_result = await self.vision_service.analyze_job_page(
                    screenshot, 
                    strategy=ProcessingStrategy.HYBRID
                )
                
                # 3. 基於 AI 分析結果進行智能操作
                jobs_data = []
                
                for job in vision_result.job_listings:
                    if job.apply_button_location:
                        # 點擊職位詳情
                        await self._smart_click(page, job.apply_button_location)
                        await self._random_delay(2, 4)
                        
                        # 提取詳細信息
                        detail_screenshot = await page.screenshot()
                        detail_result = await self.vision_service.analyze_job_page(detail_screenshot)
                        
                        jobs_data.append({
                            "title": job.title,
                            "company": job.company,
                            "location": job.location,
                            "salary": job.salary,
                            "detailed_info": detail_result,
                            "confidence": job.confidence
                        })
                        
                        # 返回上一頁
                        await page.go_back()
                        await self._random_delay(1, 2)
                
                return jobs_data
                
            finally:
                await browser.close()
    
    async def _smart_click(self, page, location: Dict):
        """智能點擊 (模擬人類行為)"""
        x = location['x'] + location['width'] // 2
        y = location['y'] + location['height'] // 2
        
        # 滑鼠移動到目標位置
        await page.mouse.move(x, y)
        await self._random_delay(0.5, 1.5)
        
        # 點擊
        await page.mouse.click(x, y)
    
    async def _random_delay(self, min_seconds: float, max_seconds: float):
        """隨機延遲模擬人類行為"""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
```

---

## 📊 **性能監控與優化**

### **智能策略選擇**

```python
# monitoring/strategy_optimizer.py
class StrategyOptimizer:
    def __init__(self):
        self.performance_history = {}
        self.cost_tracking = {}
    
    def select_optimal_strategy(self, context: Dict) -> ProcessingStrategy:
        """基於歷史性能和成本選擇最優策略"""
        
        # 成本敏感模式
        if context.get('cost_sensitive', False):
            return ProcessingStrategy.LOCAL_ONLY
            
        # 高準確度要求
        if context.get('accuracy_critical', False):
            return ProcessingStrategy.API_ONLY
            
        # 基於網站難度
        site_difficulty = self._assess_site_difficulty(context.get('url', ''))
        
        if site_difficulty > 0.8:
            return ProcessingStrategy.API_ONLY
        elif site_difficulty > 0.5:
            return ProcessingStrategy.HYBRID
        else:
            return ProcessingStrategy.LOCAL_ONLY
    
    def _assess_site_difficulty(self, url: str) -> float:
        """評估網站爬取難度"""
        difficult_sites = [
            'linkedin.com',
            'glassdoor.com', 
            'indeed.com'
        ]
        
        for site in difficult_sites:
            if site in url:
                return 0.9
                
        return 0.3
```

### **成本控制系統**

```yaml
Cost Control Configuration:
  Daily Limits:
    OpenAI API: $50
    Google Vision: $30
    Total API Budget: $100
  
  Strategy Rules:
    - Morning Hours (8-12): Prefer API_ONLY
    - Peak Hours (12-18): Use HYBRID  
    - Night Hours (18-8): Use LOCAL_ONLY
    
  Fallback Rules:
    - If API quota exceeded: Switch to LOCAL_ONLY
    - If local model fails: Limited API usage
    - Emergency mode: Pure local processing
```

---

## 🎯 **實施優先級與時程**

### **Phase 1: 基礎 AI 整合 (4 週)**
- Week 1: OpenAI Vision API 整合
- Week 2: 本地模型配置 (CLIP + OCR)
- Week 3: 混合處理邏輯開發
- Week 4: 基礎測試和調優

### **Phase 2: 智能爬蟲開發 (6 週)**  
- Week 5-6: Playwright 整合和反偵測
- Week 7-8: 視覺導向操作邏輯
- Week 9-10: 多網站適配和測試

### **Phase 3: 優化與部署 (4 週)**
- Week 11-12: 性能優化和成本控制
- Week 13-14: 生產部署和監控

這個 AI 視覺增強方案將大幅提升 JobSpy 的爬蟲成功率和適應性，同時提供成本可控的混合處理策略。