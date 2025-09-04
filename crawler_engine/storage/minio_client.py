#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinIO 客戶端模組

提供與 MinIO 對象存儲的交互功能，包括文件上傳、下載、刪除等操作。
"""

import json
import logging
from datetime import datetime
from io import BytesIO
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = Exception

from ..config import StorageConfig

logger = logging.getLogger(__name__)

class MinIOClient:
    """
    MinIO 客戶端類
    
    提供與 MinIO 對象存儲的交互功能。
    """
    
    def __init__(self, config: StorageConfig):
        """
        初始化 MinIO 客戶端
        
        Args:
            config: 存儲配置
        """
        self.config = config
        self.client = None
        
        if not MINIO_AVAILABLE:
            logger.warning("MinIO 庫未安裝，將使用本地文件存儲")
            return
            
        try:
            # 初始化 MinIO 客戶端
            self.client = Minio(
                endpoint=config.minio_endpoint,
                access_key=config.minio_access_key,
                secret_key=config.minio_secret_key,
                secure=config.minio_secure
            )
            logger.info(f"MinIO 客戶端初始化成功: {config.minio_endpoint}")
        except Exception as e:
            logger.error(f"MinIO 客戶端初始化失敗: {str(e)}")
            self.client = None
    
    def _ensure_bucket_exists(self, bucket_name: str) -> bool:
        """
        確保存儲桶存在
        
        Args:
            bucket_name: 存儲桶名稱
            
        Returns:
            bool: 是否成功
        """
        if not self.client:
            return False
            
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"創建存儲桶: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"存儲桶操作失敗: {str(e)}")
            return False
    
    def upload_json(self, bucket_name: str, object_name: str, data: Dict[str, Any]) -> bool:
        """
        上傳 JSON 數據
        
        Args:
            bucket_name: 存儲桶名稱
            object_name: 對象名稱
            data: 要上傳的數據
            
        Returns:
            bool: 是否成功
        """
        if not self.client:
            # 回退到本地文件存儲
            return self._save_to_local_file(bucket_name, object_name, data)
            
        try:
            # 確保存儲桶存在
            if not self._ensure_bucket_exists(bucket_name):
                return False
            
            # 將數據轉換為 JSON 字符串
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            json_bytes = json_data.encode('utf-8')
            
            # 上傳到 MinIO
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=BytesIO(json_bytes),
                length=len(json_bytes),
                content_type='application/json'
            )
            
            logger.info(f"成功上傳 JSON 到 MinIO: {bucket_name}/{object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"上傳 JSON 到 MinIO 失敗: {str(e)}")
            # 回退到本地文件存儲
            return self._save_to_local_file(bucket_name, object_name, data)
    
    def download_json(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        """
        下載 JSON 數據
        
        Args:
            bucket_name: 存儲桶名稱
            object_name: 對象名稱
            
        Returns:
            Optional[Dict[str, Any]]: 下載的數據，失敗時返回 None
        """
        if not self.client:
            # 回退到本地文件讀取
            return self._load_from_local_file(bucket_name, object_name)
            
        try:
            # 從 MinIO 下載
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            # 解析 JSON
            json_data = json.loads(data.decode('utf-8'))
            logger.info(f"成功從 MinIO 下載 JSON: {bucket_name}/{object_name}")
            return json_data
            
        except S3Error as e:
            logger.error(f"從 MinIO 下載 JSON 失敗: {str(e)}")
            # 回退到本地文件讀取
            return self._load_from_local_file(bucket_name, object_name)
    
    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """
        列出存儲桶中的對象
        
        Args:
            bucket_name: 存儲桶名稱
            prefix: 對象名稱前綴
            
        Returns:
            List[str]: 對象名稱列表
        """
        if not self.client:
            # 回退到本地文件列表
            return self._list_local_files(bucket_name, prefix)
            
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"列出 MinIO 對象失敗: {str(e)}")
            return self._list_local_files(bucket_name, prefix)
    
    def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """
        刪除對象
        
        Args:
            bucket_name: 存儲桶名稱
            object_name: 對象名稱
            
        Returns:
            bool: 是否成功
        """
        if not self.client:
            # 回退到本地文件刪除
            return self._delete_local_file(bucket_name, object_name)
            
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"成功從 MinIO 刪除對象: {bucket_name}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"從 MinIO 刪除對象失敗: {str(e)}")
            return self._delete_local_file(bucket_name, object_name)
    
    def _save_to_local_file(self, bucket_name: str, object_name: str, data: Dict[str, Any]) -> bool:
        """
        保存到本地文件（回退方案）
        
        Args:
            bucket_name: 存儲桶名稱（用作目錄名）
            object_name: 對象名稱（用作文件名）
            data: 要保存的數據
            
        Returns:
            bool: 是否成功
        """
        try:
            # 創建本地存儲目錄
            local_dir = Path("data") / bucket_name
            local_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            file_path = local_dir / object_name
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存到本地文件: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存到本地文件失敗: {str(e)}")
            return False
    
    def _load_from_local_file(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        """
        從本地文件加載（回退方案）
        
        Args:
            bucket_name: 存儲桶名稱（用作目錄名）
            object_name: 對象名稱（用作文件名）
            
        Returns:
            Optional[Dict[str, Any]]: 加載的數據，失敗時返回 None
        """
        try:
            file_path = Path("data") / bucket_name / object_name
            
            if not file_path.exists():
                logger.warning(f"本地文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"成功從本地文件加載: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"從本地文件加載失敗: {str(e)}")
            return None
    
    def _list_local_files(self, bucket_name: str, prefix: str = "") -> List[str]:
        """
        列出本地文件（回退方案）
        
        Args:
            bucket_name: 存儲桶名稱（用作目錄名）
            prefix: 文件名前綴
            
        Returns:
            List[str]: 文件名列表
        """
        try:
            local_dir = Path("data") / bucket_name
            
            if not local_dir.exists():
                return []
            
            files = []
            for file_path in local_dir.iterdir():
                if file_path.is_file() and file_path.name.startswith(prefix):
                    files.append(file_path.name)
            
            return files
            
        except Exception as e:
            logger.error(f"列出本地文件失敗: {str(e)}")
            return []
    
    def _delete_local_file(self, bucket_name: str, object_name: str) -> bool:
        """
        刪除本地文件（回退方案）
        
        Args:
            bucket_name: 存儲桶名稱（用作目錄名）
            object_name: 對象名稱（用作文件名）
            
        Returns:
            bool: 是否成功
        """
        try:
            file_path = Path("data") / bucket_name / object_name
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"成功刪除本地文件: {file_path}")
                return True
            else:
                logger.warning(f"本地文件不存在: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"刪除本地文件失敗: {str(e)}")
            return False
    
    def get_object_info(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取對象信息
        
        Args:
            bucket_name: 存儲桶名稱
            object_name: 對象名稱
            
        Returns:
            Optional[Dict[str, Any]]: 對象信息，失敗時返回 None
        """
        if not self.client:
            # 回退到本地文件信息
            return self._get_local_file_info(bucket_name, object_name)
            
        try:
            stat = self.client.stat_object(bucket_name, object_name)
            return {
                'size': stat.size,
                'last_modified': stat.last_modified,
                'etag': stat.etag,
                'content_type': stat.content_type
            }
        except S3Error as e:
            logger.error(f"獲取 MinIO 對象信息失敗: {str(e)}")
            return self._get_local_file_info(bucket_name, object_name)
    
    def _get_local_file_info(self, bucket_name: str, object_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取本地文件信息（回退方案）
        
        Args:
            bucket_name: 存儲桶名稱（用作目錄名）
            object_name: 對象名稱（用作文件名）
            
        Returns:
            Optional[Dict[str, Any]]: 文件信息，失敗時返回 None
        """
        try:
            file_path = Path("data") / bucket_name / object_name
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'content_type': 'application/json'
            }
            
        except Exception as e:
            logger.error(f"獲取本地文件信息失敗: {str(e)}")
            return None