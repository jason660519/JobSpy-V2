#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索請求模型
定義職位搜索的參數和配置
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class SearchRequest:
    """職位搜索請求模型"""
    
    # 基本搜索參數
    query: str = ""  # 搜索關鍵詞
    location: str = ""  # 工作地點
    
    # 職位篩選參數
    job_type: Optional[str] = None  # 工作類型：full-time, part-time, contract, casual
    salary_min: Optional[int] = None  # 最低薪資
    salary_max: Optional[int] = None  # 最高薪資
    
    # 時間篩選參數
    date_posted: Optional[str] = None  # 發布時間：today, 3days, week, 2weeks, month
    
    # 排序和分頁參數
    sort_by: str = "relevance"  # 排序方式：relevance, date, salary
    page: int = 1  # 頁碼
    per_page: int = 20  # 每頁結果數
    
    # 高級篩選參數
    company: Optional[str] = None  # 公司名稱
    industry: Optional[str] = None  # 行業
    experience_level: Optional[str] = None  # 經驗要求
    
    # 元數據
    created_at: Optional[datetime] = None  # 請求創建時間
    user_agent: Optional[str] = None  # 用戶代理
    session_id: Optional[str] = None  # 會話ID
    
    # 額外參數
    extra_params: Optional[Dict[str, Any]] = None  # 額外的平台特定參數
    
    def __post_init__(self):
        """初始化後處理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        
        if self.extra_params is None:
            self.extra_params = {}
        
        # 驗證參數
        self._validate_params()
    
    def _validate_params(self):
        """驗證搜索參數"""
        # 驗證頁碼
        if self.page < 1:
            raise ValueError("頁碼必須大於 0")
        
        # 驗證每頁結果數
        if self.per_page < 1 or self.per_page > 100:
            raise ValueError("每頁結果數必須在 1-100 之間")
        
        # 驗證薪資範圍
        if self.salary_min is not None and self.salary_min < 0:
            raise ValueError("最低薪資不能為負數")
        
        if self.salary_max is not None and self.salary_max < 0:
            raise ValueError("最高薪資不能為負數")
        
        if (self.salary_min is not None and self.salary_max is not None and 
            self.salary_min > self.salary_max):
            raise ValueError("最低薪資不能大於最高薪資")
        
        # 驗證工作類型
        valid_job_types = {'full-time', 'part-time', 'contract', 'casual', 'internship'}
        if self.job_type is not None and self.job_type not in valid_job_types:
            raise ValueError(f"無效的工作類型: {self.job_type}. 有效選項: {valid_job_types}")
        
        # 驗證發布時間
        valid_date_posted = {'today', '3days', 'week', '2weeks', 'month'}
        if self.date_posted is not None and self.date_posted not in valid_date_posted:
            raise ValueError(f"無效的發布時間: {self.date_posted}. 有效選項: {valid_date_posted}")
        
        # 驗證排序方式
        valid_sort_by = {'relevance', 'date', 'salary'}
        if self.sort_by not in valid_sort_by:
            raise ValueError(f"無效的排序方式: {self.sort_by}. 有效選項: {valid_sort_by}")
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        result = {
            'query': self.query,
            'location': self.location,
            'job_type': self.job_type,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'date_posted': self.date_posted,
            'sort_by': self.sort_by,
            'page': self.page,
            'per_page': self.per_page,
            'company': self.company,
            'industry': self.industry,
            'experience_level': self.experience_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'extra_params': self.extra_params
        }
        
        # 移除 None 值
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchRequest':
        """從字典創建 SearchRequest 實例"""
        # 處理 created_at 字段
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        return cls(**data)
    
    def copy(self, **kwargs) -> 'SearchRequest':
        """創建副本並可選擇性地更新參數"""
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data)
    
    def get_cache_key(self) -> str:
        """生成用於緩存的唯一鍵"""
        # 排除時間戳和會話相關的字段
        cache_data = self.to_dict()
        exclude_fields = {'created_at', 'user_agent', 'session_id'}
        
        cache_data = {k: v for k, v in cache_data.items() if k not in exclude_fields}
        
        # 生成穩定的字符串表示
        import hashlib
        import json
        
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_str.encode('utf-8')).hexdigest()
    
    def __str__(self) -> str:
        """字符串表示"""
        parts = []
        
        if self.query:
            parts.append(f"查詢: '{self.query}'")
        
        if self.location:
            parts.append(f"地點: '{self.location}'")
        
        if self.job_type:
            parts.append(f"類型: {self.job_type}")
        
        if self.salary_min or self.salary_max:
            salary_range = []
            if self.salary_min:
                salary_range.append(f"${self.salary_min:,}")
            else:
                salary_range.append("不限")
            
            salary_range.append("-")
            
            if self.salary_max:
                salary_range.append(f"${self.salary_max:,}")
            else:
                salary_range.append("不限")
            
            parts.append(f"薪資: {' '.join(salary_range)}")
        
        parts.append(f"第 {self.page} 頁")
        
        return f"SearchRequest({', '.join(parts)})"