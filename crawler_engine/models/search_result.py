#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索結果模型
定義職位搜索結果的數據結構
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .job_data import JobData
from .search_request import SearchRequest


@dataclass
class SearchResult:
    """職位搜索結果模型"""
    
    # 搜索結果基本信息
    jobs: List[JobData] = field(default_factory=list)  # 職位列表
    total_results: int = 0  # 總結果數
    current_page: int = 1  # 當前頁碼
    total_pages: int = 0  # 總頁數
    per_page: int = 20  # 每頁結果數
    
    # 搜索狀態
    success: bool = True  # 搜索是否成功
    error_message: Optional[str] = None  # 錯誤信息
    warning_messages: List[str] = field(default_factory=list)  # 警告信息
    
    # 搜索元數據
    search_request: Optional[SearchRequest] = None  # 原始搜索請求
    search_time: Optional[datetime] = None  # 搜索時間
    execution_time: float = 0.0  # 執行時間（秒）
    
    # 平台信息
    source_platform: str = ""  # 來源平台
    platform_url: str = ""  # 平台搜索URL
    
    # 統計信息
    scraped_count: int = 0  # 實際爬取的職位數
    failed_count: int = 0  # 爬取失敗的職位數
    duplicate_count: int = 0  # 重複職位數
    
    # 分頁信息
    has_next_page: bool = False  # 是否有下一頁
    has_previous_page: bool = False  # 是否有上一頁
    next_page_url: Optional[str] = None  # 下一頁URL
    previous_page_url: Optional[str] = None  # 上一頁URL
    
    # 額外數據
    extra_data: Dict[str, Any] = field(default_factory=dict)  # 額外的平台特定數據
    
    def __post_init__(self):
        """初始化後處理"""
        if self.search_time is None:
            self.search_time = datetime.now()
        
        # 計算分頁信息
        self._calculate_pagination()
        
        # 更新統計信息
        self._update_statistics()
    
    def _calculate_pagination(self):
        """計算分頁信息"""
        if self.per_page > 0 and self.total_results > 0:
            self.total_pages = (self.total_results + self.per_page - 1) // self.per_page
            self.has_next_page = self.current_page < self.total_pages
            self.has_previous_page = self.current_page > 1
        else:
            self.total_pages = 0
            self.has_next_page = False
            self.has_previous_page = False
    
    def _update_statistics(self):
        """更新統計信息"""
        self.scraped_count = len(self.jobs)
        
        # 檢查重複職位（基於URL或job_id）
        seen_urls = set()
        seen_job_ids = set()
        duplicates = 0
        
        for job in self.jobs:
            if job.url and job.url in seen_urls:
                duplicates += 1
            elif job.job_id and job.job_id in seen_job_ids:
                duplicates += 1
            else:
                if job.url:
                    seen_urls.add(job.url)
                if job.job_id:
                    seen_job_ids.add(job.job_id)
        
        self.duplicate_count = duplicates
    
    def add_job(self, job: JobData):
        """添加職位到結果中"""
        if job:
            self.jobs.append(job)
            self._update_statistics()
    
    def add_jobs(self, jobs: List[JobData]):
        """批量添加職位"""
        if jobs:
            self.jobs.extend(jobs)
            self._update_statistics()
    
    def add_warning(self, message: str):
        """添加警告信息"""
        if message and message not in self.warning_messages:
            self.warning_messages.append(message)
    
    def set_error(self, error_message: str):
        """設置錯誤信息"""
        self.success = False
        self.error_message = error_message
    
    def get_unique_jobs(self) -> List[JobData]:
        """獲取去重後的職位列表"""
        seen_urls = set()
        seen_job_ids = set()
        unique_jobs = []
        
        for job in self.jobs:
            is_duplicate = False
            
            if job.url and job.url in seen_urls:
                is_duplicate = True
            elif job.job_id and job.job_id in seen_job_ids:
                is_duplicate = True
            
            if not is_duplicate:
                unique_jobs.append(job)
                if job.url:
                    seen_urls.add(job.url)
                if job.job_id:
                    seen_job_ids.add(job.job_id)
        
        return unique_jobs
    
    def get_jobs_by_company(self, company_name: str) -> List[JobData]:
        """根據公司名稱篩選職位"""
        return [job for job in self.jobs if job.company.lower() == company_name.lower()]
    
    def get_jobs_by_location(self, location: str) -> List[JobData]:
        """根據地點篩選職位"""
        return [job for job in self.jobs if location.lower() in job.location.lower()]
    
    def get_jobs_with_salary(self) -> List[JobData]:
        """獲取有薪資信息的職位"""
        return [job for job in self.jobs if job.has_salary_info()]
    
    def get_recent_jobs(self, days: int = 7) -> List[JobData]:
        """獲取最近發布的職位"""
        return [job for job in self.jobs if job.is_recent(days)]
    
    def get_success_rate(self) -> float:
        """獲取成功率"""
        total_attempts = self.scraped_count + self.failed_count
        if total_attempts == 0:
            return 0.0
        return (self.scraped_count / total_attempts) * 100
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """獲取摘要統計信息"""
        return {
            'total_results': self.total_results,
            'scraped_count': self.scraped_count,
            'failed_count': self.failed_count,
            'duplicate_count': self.duplicate_count,
            'success_rate': self.get_success_rate(),
            'execution_time': self.execution_time,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'has_next_page': self.has_next_page,
            'unique_jobs_count': len(self.get_unique_jobs()),
            'jobs_with_salary_count': len(self.get_jobs_with_salary()),
            'recent_jobs_count': len(self.get_recent_jobs())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'jobs': [job.to_dict() for job in self.jobs],
            'total_results': self.total_results,
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'per_page': self.per_page,
            'success': self.success,
            'error_message': self.error_message,
            'warning_messages': self.warning_messages,
            'search_request': self.search_request.to_dict() if self.search_request else None,
            'search_time': self.search_time.isoformat() if self.search_time else None,
            'execution_time': self.execution_time,
            'source_platform': self.source_platform,
            'platform_url': self.platform_url,
            'scraped_count': self.scraped_count,
            'failed_count': self.failed_count,
            'duplicate_count': self.duplicate_count,
            'has_next_page': self.has_next_page,
            'has_previous_page': self.has_previous_page,
            'next_page_url': self.next_page_url,
            'previous_page_url': self.previous_page_url,
            'extra_data': self.extra_data,
            'summary_stats': self.get_summary_stats()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchResult':
        """從字典創建 SearchResult 實例"""
        # 處理 jobs 字段
        if 'jobs' in data:
            data['jobs'] = [JobData.from_dict(job_data) for job_data in data['jobs']]
        
        # 處理 search_request 字段
        if 'search_request' in data and data['search_request']:
            data['search_request'] = SearchRequest.from_dict(data['search_request'])
        
        # 處理日期字段
        if 'search_time' in data and isinstance(data['search_time'], str):
            try:
                data['search_time'] = datetime.fromisoformat(data['search_time'])
            except ValueError:
                data['search_time'] = None
        
        # 移除摘要統計信息（會自動計算）
        data.pop('summary_stats', None)
        
        # 處理列表字段
        if 'warning_messages' not in data:
            data['warning_messages'] = []
        
        # 處理字典字段
        if 'extra_data' not in data:
            data['extra_data'] = {}
        
        return cls(**data)
    
    @classmethod
    def create_empty(cls, search_request: Optional[SearchRequest] = None) -> 'SearchResult':
        """創建空的搜索結果"""
        return cls(
            jobs=[],
            total_results=0,
            success=True,
            search_request=search_request,
            search_time=datetime.now()
        )
    
    @classmethod
    def create_error(cls, error_message: str, search_request: Optional[SearchRequest] = None) -> 'SearchResult':
        """創建錯誤的搜索結果"""
        result = cls.create_empty(search_request)
        result.set_error(error_message)
        return result
    
    def __str__(self) -> str:
        """字符串表示"""
        if not self.success:
            return f"SearchResult(失敗: {self.error_message})"
        
        return (f"SearchResult({self.scraped_count}/{self.total_results} 職位, "
                f"第 {self.current_page}/{self.total_pages} 頁, "
                f"{self.execution_time:.2f}s)")
    
    def __len__(self) -> int:
        """返回職位數量"""
        return len(self.jobs)
    
    def __iter__(self):
        """迭代職位"""
        return iter(self.jobs)
    
    def __getitem__(self, index):
        """根據索引獲取職位"""
        return self.jobs[index]