#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
職位數據模型
定義職位信息的數據結構
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobType(Enum):
    """工作類型枚舉"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    CASUAL = "casual"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class SalaryType(Enum):
    """薪資類型枚舉"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class JobData:
    """職位數據模型"""
    
    # 基本信息
    title: str = ""  # 職位標題
    company: str = ""  # 公司名稱
    location: str = ""  # 工作地點
    url: str = ""  # 職位詳情頁面URL
    
    # 職位詳情
    description: str = ""  # 職位描述
    requirements: str = ""  # 職位要求
    benefits: str = ""  # 福利待遇
    
    # 工作類型和時間
    job_type: Optional[JobType] = None  # 工作類型
    work_arrangement: Optional[str] = None  # 工作安排：remote, hybrid, onsite
    
    # 薪資信息
    salary_min: Optional[float] = None  # 最低薪資
    salary_max: Optional[float] = None  # 最高薪資
    salary_type: Optional[SalaryType] = None  # 薪資類型
    salary_currency: str = "AUD"  # 薪資貨幣
    salary_text: str = ""  # 原始薪資文本
    
    # 公司信息
    company_size: Optional[str] = None  # 公司規模
    industry: Optional[str] = None  # 行業
    company_logo: Optional[str] = None  # 公司logo URL
    company_description: Optional[str] = None  # 公司描述
    
    # 職位元數據
    posted_date: Optional[datetime] = None  # 發布日期
    closing_date: Optional[datetime] = None  # 截止日期
    application_count: Optional[int] = None  # 申請人數
    views_count: Optional[int] = None  # 瀏覽次數
    
    # 技能和標籤
    skills: List[str] = field(default_factory=list)  # 技能要求
    tags: List[str] = field(default_factory=list)  # 標籤
    categories: List[str] = field(default_factory=list)  # 分類
    
    # 聯繫信息
    contact_email: Optional[str] = None  # 聯繫郵箱
    contact_phone: Optional[str] = None  # 聯繫電話
    recruiter_name: Optional[str] = None  # 招聘人員姓名
    
    # 爬蟲元數據
    source_platform: str = ""  # 來源平台
    job_id: str = ""  # 平台內部職位ID
    scraped_at: Optional[datetime] = None  # 爬取時間
    last_updated: Optional[datetime] = None  # 最後更新時間
    
    # AI 處理結果
    ai_summary: Optional[str] = None  # AI 生成的摘要
    ai_score: Optional[float] = None  # AI 評分
    ai_tags: List[str] = field(default_factory=list)  # AI 生成的標籤
    
    # 額外數據
    extra_data: Dict[str, Any] = field(default_factory=dict)  # 額外的平台特定數據
    
    def __post_init__(self):
        """初始化後處理"""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
        
        if self.last_updated is None:
            self.last_updated = self.scraped_at
        
        # 生成唯一ID（如果沒有提供job_id）
        if not self.job_id and self.url:
            import hashlib
            self.job_id = hashlib.md5(self.url.encode('utf-8')).hexdigest()[:12]
    
    def get_salary_range_text(self) -> str:
        """獲取薪資範圍文本"""
        if not self.salary_min and not self.salary_max:
            return self.salary_text or "薪資面議"
        
        parts = []
        
        if self.salary_min:
            parts.append(f"{self.salary_currency} {self.salary_min:,.0f}")
        
        if self.salary_max:
            if parts:
                parts.append("-")
            parts.append(f"{self.salary_currency} {self.salary_max:,.0f}")
        
        if self.salary_type:
            type_map = {
                SalaryType.HOURLY: "每小時",
                SalaryType.DAILY: "每日",
                SalaryType.WEEKLY: "每週",
                SalaryType.MONTHLY: "每月",
                SalaryType.YEARLY: "每年"
            }
            parts.append(type_map.get(self.salary_type, ""))
        
        return " ".join(parts)
    
    def get_job_type_text(self) -> str:
        """獲取工作類型文本"""
        if not self.job_type:
            return "未指定"
        
        type_map = {
            JobType.FULL_TIME: "全職",
            JobType.PART_TIME: "兼職",
            JobType.CONTRACT: "合約",
            JobType.CASUAL: "臨時",
            JobType.INTERNSHIP: "實習",
            JobType.TEMPORARY: "臨時"
        }
        
        return type_map.get(self.job_type, str(self.job_type.value))
    
    def get_work_arrangement_text(self) -> str:
        """獲取工作安排文本"""
        if not self.work_arrangement:
            return "未指定"
        
        arrangement_map = {
            "remote": "遠程工作",
            "hybrid": "混合工作",
            "onsite": "現場工作"
        }
        
        return arrangement_map.get(self.work_arrangement.lower(), self.work_arrangement)
    
    def add_skill(self, skill: str):
        """添加技能"""
        if skill and skill not in self.skills:
            self.skills.append(skill)
    
    def add_tag(self, tag: str):
        """添加標籤"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def add_category(self, category: str):
        """添加分類"""
        if category and category not in self.categories:
            self.categories.append(category)
    
    def is_recent(self, days: int = 7) -> bool:
        """檢查是否為最近發布的職位"""
        if not self.posted_date:
            return False
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.posted_date >= cutoff_date
    
    def has_salary_info(self) -> bool:
        """檢查是否有薪資信息"""
        return bool(self.salary_min or self.salary_max or self.salary_text)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        result = {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'url': self.url,
            'description': self.description,
            'requirements': self.requirements,
            'benefits': self.benefits,
            'job_type': self.job_type.value if self.job_type else None,
            'work_arrangement': self.work_arrangement,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_type': self.salary_type.value if self.salary_type else None,
            'salary_currency': self.salary_currency,
            'salary_text': self.salary_text,
            'company_size': self.company_size,
            'industry': self.industry,
            'company_logo': self.company_logo,
            'company_description': self.company_description,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'closing_date': self.closing_date.isoformat() if self.closing_date else None,
            'application_count': self.application_count,
            'views_count': self.views_count,
            'skills': self.skills,
            'tags': self.tags,
            'categories': self.categories,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'recruiter_name': self.recruiter_name,
            'source_platform': self.source_platform,
            'job_id': self.job_id,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'ai_summary': self.ai_summary,
            'ai_score': self.ai_score,
            'ai_tags': self.ai_tags,
            'extra_data': self.extra_data
        }
        
        # 移除 None 值
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobData':
        """從字典創建 JobData 實例"""
        # 處理枚舉字段
        if 'job_type' in data and isinstance(data['job_type'], str):
            try:
                data['job_type'] = JobType(data['job_type'])
            except ValueError:
                data['job_type'] = None
        
        if 'salary_type' in data and isinstance(data['salary_type'], str):
            try:
                data['salary_type'] = SalaryType(data['salary_type'])
            except ValueError:
                data['salary_type'] = None
        
        # 處理日期字段
        date_fields = ['posted_date', 'closing_date', 'scraped_at', 'last_updated']
        for field_name in date_fields:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    data[field_name] = None
        
        # 處理列表字段
        list_fields = ['skills', 'tags', 'categories', 'ai_tags']
        for field_name in list_fields:
            if field_name not in data:
                data[field_name] = []
        
        # 處理字典字段
        if 'extra_data' not in data:
            data['extra_data'] = {}
        
        return cls(**data)
    
    def __str__(self) -> str:
        """字符串表示"""
        parts = []
        
        if self.title:
            parts.append(f"'{self.title}'")
        
        if self.company:
            parts.append(f"@ {self.company}")
        
        if self.location:
            parts.append(f"in {self.location}")
        
        if self.job_type:
            parts.append(f"({self.get_job_type_text()})")
        
        return f"JobData({' '.join(parts)})"