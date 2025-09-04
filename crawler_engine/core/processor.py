"""結果處理器

處理爬蟲結果，包括數據清洗、去重、格式化和質量評估。
"""

import asyncio
import hashlib
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import structlog
from difflib import SequenceMatcher

logger = structlog.get_logger(__name__)


@dataclass
class JobData:
    """標準化職位數據結構"""
    # 基本信息
    title: str
    company: str
    location: str
    description: str
    
    # 詳細信息
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    employment_type: Optional[str] = None  # full-time, part-time, contract, etc.
    experience_level: Optional[str] = None  # entry, mid, senior, etc.
    
    # 技能和要求
    skills: List[str] = None
    requirements: List[str] = None
    benefits: List[str] = None
    
    # 元數據
    source_platform: str = ""
    source_url: str = ""
    posted_date: Optional[datetime] = None
    scraped_at: datetime = None
    
    # 質量評分
    quality_score: float = 0.0
    confidence_score: float = 0.0
    
    # 唯一標識
    job_id: str = ""
    content_hash: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.requirements is None:
            self.requirements = []
        if self.benefits is None:
            self.benefits = []
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
        if not self.content_hash:
            self.content_hash = self._generate_content_hash()
    
    def _generate_content_hash(self) -> str:
        """生成內容哈希用於去重"""
        content = f"{self.title}|{self.company}|{self.location}|{self.description[:500]}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class ProcessingStats:
    """處理統計信息"""
    total_jobs: int = 0
    valid_jobs: int = 0
    duplicates_removed: int = 0
    low_quality_filtered: int = 0
    processing_time: float = 0.0
    average_quality_score: float = 0.0


class DataCleaner:
    """數據清洗器"""
    
    def __init__(self):
        self.logger = logger.bind(component="data_cleaner")
        
        # 常見的垃圾詞彙
        self.spam_keywords = {
            "urgent", "immediate", "asap", "work from home guaranteed",
            "make money fast", "no experience required", "easy money"
        }
        
        # 技能關鍵詞模式
        self.skill_patterns = [
            r'\b(?:python|java|javascript|react|angular|vue|node\.?js)\b',
            r'\b(?:sql|mysql|postgresql|mongodb|redis)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes)\b',
            r'\b(?:git|github|gitlab|jenkins|ci/cd)\b'
        ]
    
    async def clean_job_data(self, job: JobData) -> JobData:
        """清洗單個職位數據"""
        try:
            # 清洗文本字段
            job.title = self._clean_text(job.title)
            job.company = self._clean_text(job.company)
            job.location = self._clean_text(job.location)
            job.description = self._clean_description(job.description)
            
            # 提取技能
            job.skills = self._extract_skills(job.description)
            
            # 標準化薪資
            job.salary_min, job.salary_max = self._normalize_salary(
                job.salary_min, job.salary_max
            )
            
            # 標準化就業類型
            job.employment_type = self._normalize_employment_type(job.employment_type)
            
            # 標準化經驗等級
            job.experience_level = self._normalize_experience_level(job.description)
            
            return job
            
        except Exception as e:
            self.logger.error("數據清洗失敗", job_id=job.job_id, error=str(e))
            return job
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""
        
        # 移除多餘空白
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\-.,()&]', '', text)
        
        return text
    
    def _clean_description(self, description: str) -> str:
        """清洗職位描述"""
        if not description:
            return ""
        
        # 基本清洗
        description = self._clean_text(description)
        
        # 移除重複段落
        paragraphs = description.split('\n')
        unique_paragraphs = []
        seen = set()
        
        for para in paragraphs:
            para = para.strip()
            if para and para not in seen:
                unique_paragraphs.append(para)
                seen.add(para)
        
        return '\n'.join(unique_paragraphs)
    
    def _extract_skills(self, description: str) -> List[str]:
        """從描述中提取技能"""
        skills = set()
        description_lower = description.lower()
        
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, description_lower, re.IGNORECASE)
            skills.update(matches)
        
        return list(skills)
    
    def _normalize_salary(self, min_sal: Optional[float], 
                         max_sal: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
        """標準化薪資"""
        if min_sal and max_sal and min_sal > max_sal:
            min_sal, max_sal = max_sal, min_sal
        
        # 過濾異常值
        if min_sal and (min_sal < 1000 or min_sal > 1000000):
            min_sal = None
        if max_sal and (max_sal < 1000 or max_sal > 1000000):
            max_sal = None
        
        return min_sal, max_sal
    
    def _normalize_employment_type(self, emp_type: Optional[str]) -> Optional[str]:
        """標準化就業類型"""
        if not emp_type:
            return None
        
        emp_type_lower = emp_type.lower()
        
        if any(word in emp_type_lower for word in ['full', 'permanent']):
            return 'full-time'
        elif any(word in emp_type_lower for word in ['part', 'temporary']):
            return 'part-time'
        elif any(word in emp_type_lower for word in ['contract', 'freelance']):
            return 'contract'
        elif 'intern' in emp_type_lower:
            return 'internship'
        
        return emp_type
    
    def _normalize_experience_level(self, description: str) -> Optional[str]:
        """從描述中推斷經驗等級"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['senior', 'lead', 'principal', '5+ years', '7+ years']):
            return 'senior'
        elif any(word in description_lower for word in ['mid', 'intermediate', '2-5 years', '3+ years']):
            return 'mid'
        elif any(word in description_lower for word in ['junior', 'entry', 'graduate', '0-2 years']):
            return 'entry'
        
        return None


class QualityAssessor:
    """質量評估器"""
    
    def __init__(self):
        self.logger = logger.bind(component="quality_assessor")
        
        # 質量評估權重
        self.weights = {
            'title_quality': 0.2,
            'company_quality': 0.15,
            'description_quality': 0.3,
            'location_quality': 0.1,
            'salary_quality': 0.1,
            'completeness': 0.15
        }
    
    async def assess_quality(self, job: JobData) -> float:
        """評估職位數據質量"""
        try:
            scores = {
                'title_quality': self._assess_title_quality(job.title),
                'company_quality': self._assess_company_quality(job.company),
                'description_quality': self._assess_description_quality(job.description),
                'location_quality': self._assess_location_quality(job.location),
                'salary_quality': self._assess_salary_quality(job.salary_min, job.salary_max),
                'completeness': self._assess_completeness(job)
            }
            
            # 計算加權平均分
            total_score = sum(
                score * self.weights[key] 
                for key, score in scores.items()
            )
            
            return min(max(total_score, 0.0), 1.0)
            
        except Exception as e:
            self.logger.error("質量評估失敗", job_id=job.job_id, error=str(e))
            return 0.0
    
    def _assess_title_quality(self, title: str) -> float:
        """評估標題質量"""
        if not title:
            return 0.0
        
        score = 0.5  # 基礎分
        
        # 長度檢查
        if 10 <= len(title) <= 100:
            score += 0.2
        
        # 包含技術關鍵詞
        tech_keywords = ['developer', 'engineer', 'analyst', 'manager', 'specialist']
        if any(keyword in title.lower() for keyword in tech_keywords):
            score += 0.2
        
        # 避免垃圾詞彙
        spam_words = ['urgent', 'immediate', 'asap']
        if not any(word in title.lower() for word in spam_words):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_company_quality(self, company: str) -> float:
        """評估公司名稱質量"""
        if not company:
            return 0.0
        
        score = 0.5
        
        # 長度檢查
        if 2 <= len(company) <= 50:
            score += 0.3
        
        # 避免通用詞彙
        generic_words = ['company', 'corp', 'inc', 'ltd']
        if not all(word in company.lower() for word in generic_words):
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_description_quality(self, description: str) -> float:
        """評估描述質量"""
        if not description:
            return 0.0
        
        score = 0.2  # 基礎分
        
        # 長度檢查
        if 100 <= len(description) <= 5000:
            score += 0.3
        
        # 結構化程度
        if '\n' in description or '•' in description or '-' in description:
            score += 0.2
        
        # 包含關鍵信息
        key_sections = ['responsibility', 'requirement', 'skill', 'experience']
        if any(section in description.lower() for section in key_sections):
            score += 0.2
        
        # 避免重複內容
        words = description.split()
        unique_words = set(words)
        if len(unique_words) / len(words) > 0.7:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_location_quality(self, location: str) -> float:
        """評估位置質量"""
        if not location:
            return 0.0
        
        score = 0.5
        
        # 長度檢查
        if 3 <= len(location) <= 100:
            score += 0.3
        
        # 包含城市/州/國家信息
        if ',' in location or any(word in location.lower() for word in ['remote', 'hybrid']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_salary_quality(self, min_sal: Optional[float], 
                              max_sal: Optional[float]) -> float:
        """評估薪資質量"""
        if not min_sal and not max_sal:
            return 0.3  # 沒有薪資信息不算完全失敗
        
        score = 0.5
        
        # 有薪資範圍
        if min_sal and max_sal:
            score += 0.3
            
            # 薪資範圍合理
            if max_sal > min_sal and (max_sal - min_sal) / min_sal <= 1.0:
                score += 0.2
        
        return min(score, 1.0)
    
    def _assess_completeness(self, job: JobData) -> float:
        """評估數據完整性"""
        fields = [
            job.title, job.company, job.location, job.description,
            job.employment_type, job.source_url
        ]
        
        filled_fields = sum(1 for field in fields if field)
        completeness = filled_fields / len(fields)
        
        return completeness


class DuplicateDetector:
    """重複檢測器"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.logger = logger.bind(component="duplicate_detector")
        self._seen_hashes: Set[str] = set()
        self._job_signatures: List[Tuple[str, str]] = []  # (job_id, signature)
    
    async def detect_duplicates(self, jobs: List[JobData]) -> List[JobData]:
        """檢測並移除重複職位"""
        unique_jobs = []
        duplicates_count = 0
        
        for job in jobs:
            if await self._is_duplicate(job):
                duplicates_count += 1
                continue
            
            unique_jobs.append(job)
            self._add_job_signature(job)
        
        self.logger.info(
            "重複檢測完成", 
            total_jobs=len(jobs),
            unique_jobs=len(unique_jobs),
            duplicates_removed=duplicates_count
        )
        
        return unique_jobs
    
    async def _is_duplicate(self, job: JobData) -> bool:
        """檢查是否為重複職位"""
        # 基於內容哈希的快速檢查
        if job.content_hash in self._seen_hashes:
            return True
        
        # 基於相似度的檢查
        job_signature = self._generate_signature(job)
        
        for existing_id, existing_signature in self._job_signatures:
            similarity = SequenceMatcher(None, job_signature, existing_signature).ratio()
            if similarity >= self.similarity_threshold:
                return True
        
        return False
    
    def _add_job_signature(self, job: JobData):
        """添加職位簽名"""
        self._seen_hashes.add(job.content_hash)
        signature = self._generate_signature(job)
        self._job_signatures.append((job.job_id, signature))
        
        # 限制內存使用
        if len(self._job_signatures) > 10000:
            self._job_signatures = self._job_signatures[-5000:]
    
    def _generate_signature(self, job: JobData) -> str:
        """生成職位簽名用於相似度比較"""
        return f"{job.title.lower()}|{job.company.lower()}|{job.location.lower()}"


class ResultProcessor:
    """結果處理器主類"""
    
    def __init__(self, quality_threshold: float = 0.6):
        self.quality_threshold = quality_threshold
        self.logger = logger.bind(component="result_processor")
        
        # 初始化組件
        self.cleaner = DataCleaner()
        self.quality_assessor = QualityAssessor()
        self.duplicate_detector = DuplicateDetector()
    
    async def process_results(self, raw_jobs: List[Dict[str, Any]]) -> Tuple[List[JobData], ProcessingStats]:
        """處理爬蟲結果
        
        Args:
            raw_jobs: 原始職位數據列表
            
        Returns:
            Tuple[List[JobData], ProcessingStats]: 處理後的職位數據和統計信息
        """
        start_time = asyncio.get_event_loop().time()
        
        stats = ProcessingStats(total_jobs=len(raw_jobs))
        
        self.logger.info("開始處理爬蟲結果", total_jobs=len(raw_jobs))
        
        try:
            # 1. 轉換為標準格式
            jobs = await self._convert_to_job_data(raw_jobs)
            
            # 2. 數據清洗
            cleaned_jobs = await self._clean_jobs(jobs)
            
            # 3. 質量評估
            quality_jobs = await self._assess_quality(cleaned_jobs)
            
            # 4. 過濾低質量數據
            filtered_jobs = await self._filter_by_quality(quality_jobs)
            stats.low_quality_filtered = len(quality_jobs) - len(filtered_jobs)
            
            # 5. 去重
            unique_jobs = await self.duplicate_detector.detect_duplicates(filtered_jobs)
            stats.duplicates_removed = len(filtered_jobs) - len(unique_jobs)
            
            # 6. 最終統計
            stats.valid_jobs = len(unique_jobs)
            stats.processing_time = asyncio.get_event_loop().time() - start_time
            
            if unique_jobs:
                stats.average_quality_score = sum(job.quality_score for job in unique_jobs) / len(unique_jobs)
            
            self.logger.info(
                "結果處理完成",
                **asdict(stats)
            )
            
            return unique_jobs, stats
            
        except Exception as e:
            self.logger.error("結果處理失敗", error=str(e))
            raise
    
    async def _convert_to_job_data(self, raw_jobs: List[Dict[str, Any]]) -> List[JobData]:
        """轉換原始數據為JobData格式"""
        jobs = []
        
        for i, raw_job in enumerate(raw_jobs):
            try:
                job = JobData(
                    job_id=raw_job.get('id', f'job_{i}'),
                    title=raw_job.get('title', ''),
                    company=raw_job.get('company', ''),
                    location=raw_job.get('location', ''),
                    description=raw_job.get('description', ''),
                    salary_min=raw_job.get('salary_min'),
                    salary_max=raw_job.get('salary_max'),
                    salary_currency=raw_job.get('salary_currency', 'USD'),
                    employment_type=raw_job.get('employment_type'),
                    source_platform=raw_job.get('source_platform', ''),
                    source_url=raw_job.get('source_url', ''),
                    posted_date=raw_job.get('posted_date')
                )
                jobs.append(job)
                
            except Exception as e:
                self.logger.warning("轉換職位數據失敗", index=i, error=str(e))
                continue
        
        return jobs
    
    async def _clean_jobs(self, jobs: List[JobData]) -> List[JobData]:
        """清洗職位數據"""
        cleaned_jobs = []
        
        # 並發清洗
        tasks = [self.cleaner.clean_job_data(job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, JobData):
                cleaned_jobs.append(result)
            else:
                self.logger.warning("數據清洗失敗", error=str(result))
        
        return cleaned_jobs
    
    async def _assess_quality(self, jobs: List[JobData]) -> List[JobData]:
        """評估數據質量"""
        # 並發質量評估
        tasks = [self.quality_assessor.assess_quality(job) for job in jobs]
        quality_scores = await asyncio.gather(*tasks, return_exceptions=True)
        
        for job, score in zip(jobs, quality_scores):
            if isinstance(score, float):
                job.quality_score = score
            else:
                job.quality_score = 0.0
        
        return jobs
    
    async def _filter_by_quality(self, jobs: List[JobData]) -> List[JobData]:
        """根據質量閾值過濾數據"""
        return [job for job in jobs if job.quality_score >= self.quality_threshold]