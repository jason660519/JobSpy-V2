"""存儲管理 API 端點

提供 MinIO 存儲服務的管理和監控接口。
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.storage_service import get_storage_service, StorageService
from app.core.minio_client import get_minio_client, MinIOClient

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["storage"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_storage_stats(
    storage_service: StorageService = Depends(get_storage_service)
) -> Dict[str, Any]:
    """獲取存儲統計信息
    
    Returns:
        Dict[str, Any]: 存儲統計信息，包括各 bucket 的對象數量和大小
    """
    try:
        stats = await storage_service.get_storage_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error("獲取存儲統計失敗", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"獲取存儲統計失敗: {str(e)}"
        )

@router.get("/buckets", response_model=Dict[str, Any])
async def list_buckets(
    minio_client: MinIOClient = Depends(get_minio_client)
) -> Dict[str, Any]:
    """列出所有 MinIO buckets
    
    Returns:
        Dict[str, Any]: bucket 列表和配置信息
    """
    try:
        bucket_info = {
            "buckets": minio_client.buckets,
            "endpoint": minio_client.endpoint,
            "secure": minio_client.secure
        }
        
        return {
            "success": True,
            "data": bucket_info
        }
    except Exception as e:
        logger.error("列出 buckets 失敗", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"列出 buckets 失敗: {str(e)}"
        )

@router.get("/buckets/{bucket_name}/objects", response_model=Dict[str, Any])
async def list_bucket_objects(
    bucket_name: str,
    prefix: str = "",
    limit: int = 100,
    minio_client: MinIOClient = Depends(get_minio_client)
) -> Dict[str, Any]:
    """列出指定 bucket 中的對象
    
    Args:
        bucket_name: bucket 名稱
        prefix: 對象名稱前綴過濾
        limit: 返回對象數量限制
        
    Returns:
        Dict[str, Any]: 對象列表
    """
    try:
        # 驗證 bucket 名稱
        valid_buckets = list(minio_client.buckets.values())
        if bucket_name not in valid_buckets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無效的 bucket 名稱: {bucket_name}"
            )
        
        objects = await minio_client.list_objects(bucket_name, prefix, limit)
        
        return {
            "success": True,
            "data": {
                "bucket_name": bucket_name,
                "prefix": prefix,
                "objects": objects,
                "count": len(objects)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("列出對象失敗", bucket_name=bucket_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"列出對象失敗: {str(e)}"
        )

@router.delete("/buckets/{bucket_name}/objects/{object_name:path}", response_model=Dict[str, Any])
async def delete_object(
    bucket_name: str,
    object_name: str,
    minio_client: MinIOClient = Depends(get_minio_client)
) -> Dict[str, Any]:
    """刪除指定對象
    
    Args:
        bucket_name: bucket 名稱
        object_name: 對象名稱
        
    Returns:
        Dict[str, Any]: 刪除結果
    """
    try:
        # 驗證 bucket 名稱
        valid_buckets = list(minio_client.buckets.values())
        if bucket_name not in valid_buckets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"無效的 bucket 名稱: {bucket_name}"
            )
        
        success = await minio_client.delete_object(bucket_name, object_name)
        
        if success:
            return {
                "success": True,
                "message": f"對象 {object_name} 已成功刪除"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刪除對象失敗"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("刪除對象失敗", bucket_name=bucket_name, object_name=object_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刪除對象失敗: {str(e)}"
        )

@router.post("/test-pipeline", response_model=Dict[str, Any])
async def test_data_pipeline(
    storage_service: StorageService = Depends(get_storage_service),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """測試完整的數據管道
    
    創建測試數據並執行完整的存儲流程：原始數據 -> AI 處理 -> 清理 -> 數據庫
    
    Returns:
        Dict[str, Any]: 測試結果
    """
    try:
        # 創建測試數據
        test_raw_data = b'{"test": "raw scraping data", "jobs": [{"title": "Test Job", "company": "Test Company"}]}'
        test_ai_data = {
            "jobs": [
                {
                    "title": "Software Engineer",
                    "company": "Test Company",
                    "location": "Taipei, Taiwan",
                    "description": "Test job description",
                    "salary_range": "50000-80000"
                }
            ],
            "metadata": {
                "processed_at": "2024-01-20T10:00:00Z",
                "ai_model": "gpt-4-vision"
            }
        }
        test_cleaned_data = {
            "jobs": [
                {
                    "title": "Software Engineer",
                    "company": "Test Company",
                    "location": "Taipei, Taiwan",
                    "description": "Test job description",
                    "salary_min": 50000,
                    "salary_max": 80000,
                    "url": "https://example.com/job/1",
                    "site": "test_site",
                    "date_posted": "2024-01-20",
                    "job_type": "full_time"
                }
            ]
        }
        
        # 執行完整數據管道
        result = await storage_service.complete_data_pipeline(
            site_name="test_site",
            search_query="software engineer",
            raw_data=test_raw_data,
            ai_processed_data=test_ai_data,
            cleaned_data=test_cleaned_data,
            db=db,
            metadata={"test": True}
        )
        
        return {
            "success": True,
            "message": "數據管道測試成功",
            "data": result
        }
        
    except Exception as e:
        logger.error("數據管道測試失敗", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"數據管道測試失敗: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, Any])
async def storage_health_check(
    minio_client: MinIOClient = Depends(get_minio_client)
) -> Dict[str, Any]:
    """存儲服務健康檢查
    
    Returns:
        Dict[str, Any]: 健康狀態信息
    """
    try:
        # 檢查 MinIO 連接
        bucket_stats = await minio_client.get_bucket_stats()
        
        return {
            "success": True,
            "status": "healthy",
            "minio_endpoint": minio_client.endpoint,
            "buckets_available": len(bucket_stats),
            "buckets": list(minio_client.buckets.keys())
        }
        
    except Exception as e:
        logger.error("存儲健康檢查失敗", error=str(e))
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }