from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ai_vision import AIVisionService
from app.core.config import settings

router = APIRouter()

@router.post("/analyze-page")
async def analyze_job_page(
    file: UploadFile = File(...),
    ai_service: AIVisionService = Depends()
):
    """Analyze job page screenshot with AI vision"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await file.read()
        result = await ai_service.analyze_job_page(image_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.get("/usage")
async def get_ai_usage():
    """Get AI service usage statistics"""
    # TODO: Implement usage tracking
    return {"daily_usage": 0, "limit": settings.max_ai_requests_per_day}