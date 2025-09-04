"""數據模型定義

定義用於 ETL pipeline 的數據模型和結構
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class JobStatus(Enum):
    """職位狀態枚舉"""
    ACTIVE = "active"
    EXPIRED = "expired"
    FILLED = "filled"
    DRAFT = "draft"


class ExperienceLevel(Enum):
    """經驗等級枚舉"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class WorkMode(Enum):
    """工作模式枚舉"""
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class JobType(Enum):
    """工作類型枚舉"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


@dataclass
class RawJobData:
    """原始職位數據模型
    
    用於存儲從網站爬取的原始數據
    """
    platform: str
    job_id: str
    url: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    posted_date: Optional[str] = None
    description: Optional[str] = None
    company_url: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    raw_html: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'platform': self.platform,
            'job_id': self.job_id,
            'url': self.url,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'job_type': self.job_type,
            'posted_date': self.posted_date,
            'description': self.description,
            'company_url': self.company_url,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'raw_html': self.raw_html,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class ProcessedJobData:
    """處理後的職位數據模型
    
    用於存儲 AI 處理後的結構化數據
    """
    platform: str
    job_id: str
    url: str
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    job_type: Optional[JobType] = None
    posted_date: Optional[datetime] = None
    description: str = ""
    skills: List[str] = field(default_factory=list)
    experience_level: Optional[ExperienceLevel] = None
    education_requirement: Optional[str] = None
    work_mode: Optional[WorkMode] = None
    company_url: Optional[str] = None
    benefits: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    confidence: float = 0.0
    processed_at: datetime = field(default_factory=datetime.now)
    ai_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'platform': self.platform,
            'job_id': self.job_id,
            'url': self.url,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'job_type': self.job_type.value if self.job_type else None,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'description': self.description,
            'skills': self.skills,
            'experience_level': self.experience_level.value if self.experience_level else None,
            'education_requirement': self.education_requirement,
            'work_mode': self.work_mode.value if self.work_mode else None,
            'company_url': self.company_url,
            'benefits': self.benefits,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'confidence': self.confidence,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'ai_metadata': self.ai_metadata
        }
    
    def to_json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class CleanedJobData:
    """清理後的職位數據模型
    
    用於存儲標準化和清理後的數據
    """
    platform: str
    job_id: str
    url: str
    title: str
    company: str
    location: str
    normalized_location: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "AUD"
    job_type: JobType = JobType.FULL_TIME
    posted_date: Optional[datetime] = None
    description: str = ""
    skills: List[str] = field(default_factory=list)
    normalized_skills: List[str] = field(default_factory=list)
    experience_level: Optional[ExperienceLevel] = None
    education_requirement: Optional[str] = None
    work_mode: WorkMode = WorkMode.ONSITE
    company_url: Optional[str] = None
    benefits: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    status: JobStatus = JobStatus.ACTIVE
    confidence: float = 0.0
    cleaned_at: datetime = field(default_factory=datetime.now)
    data_quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'platform': self.platform,
            'job_id': self.job_id,
            'url': self.url,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'normalized_location': self.normalized_location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'job_type': self.job_type.value,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'description': self.description,
            'skills': self.skills,
            'normalized_skills': self.normalized_skills,
            'experience_level': self.experience_level.value if self.experience_level else None,
            'education_requirement': self.education_requirement,
            'work_mode': self.work_mode.value,
            'company_url': self.company_url,
            'benefits': self.benefits,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'status': self.status.value,
            'confidence': self.confidence,
            'cleaned_at': self.cleaned_at.isoformat() if self.cleaned_at else None,
            'data_quality_score': self.data_quality_score
        }
    
    def to_json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class PipelineMetrics:
    """Pipeline 執行指標"""
    stage: str
    start_time: datetime
    end_time: Optional[datetime] = None
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """計算執行時間（秒）"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        if self.records_processed == 0:
            return 0.0
        return self.records_successful / self.records_processed
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'stage': self.stage,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'records_processed': self.records_processed,
            'records_successful': self.records_successful,
            'records_failed': self.records_failed,
            'success_rate': self.success_rate,
            'errors': self.errors,
            'metadata': self.metadata
        }


@dataclass
class ProcessedCompanyData:
    """處理後的公司數據模型"""
    company_id: str
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None
    processed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'company_id': self.company_id,
            'name': self.name,
            'industry': self.industry,
            'size': self.size,
            'location': self.location,
            'website': self.website,
            'description': self.description,
            'logo_url': self.logo_url,
            'founded_year': self.founded_year,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


@dataclass
class ProcessedSalaryData:
    """處理後的薪資數據模型"""
    job_id: str
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "AUD"
    period: str = "annual"  # annual, monthly, weekly, hourly
    is_negotiable: bool = False
    benefits: List[str] = field(default_factory=list)
    processed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'job_id': self.job_id,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'currency': self.currency,
            'period': self.period,
            'is_negotiable': self.is_negotiable,
            'benefits': self.benefits,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


@dataclass
class DataQualityMetrics:
    """數據質量指標模型"""
    completeness_score: float = 0.0  # 完整性分數 (0-1)
    accuracy_score: float = 0.0      # 準確性分數 (0-1)
    consistency_score: float = 0.0   # 一致性分數 (0-1)
    validity_score: float = 0.0      # 有效性分數 (0-1)
    overall_score: float = 0.0       # 總體質量分數 (0-1)
    missing_fields: List[str] = field(default_factory=list)
    invalid_fields: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'completeness_score': self.completeness_score,
            'accuracy_score': self.accuracy_score,
            'consistency_score': self.consistency_score,
            'validity_score': self.validity_score,
            'overall_score': self.overall_score,
            'missing_fields': self.missing_fields,
            'invalid_fields': self.invalid_fields,
            'warnings': self.warnings,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


@dataclass
class ProcessingResult:
    """處理結果模型"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class SearchCriteria:
    """搜索條件模型"""
    keywords: List[str] = field(default_factory=list)
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    work_mode: Optional[WorkMode] = None
    posted_within_days: Optional[int] = None
    company: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'keywords': self.keywords,
            'location': self.location,
            'job_type': self.job_type.value if self.job_type else None,
            'experience_level': self.experience_level.value if self.experience_level else None,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'work_mode': self.work_mode.value if self.work_mode else None,
            'posted_within_days': self.posted_within_days,
            'company': self.company,
            'skills': self.skills
        }