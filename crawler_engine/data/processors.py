"""數據處理器

提供各種數據處理功能，包括清洗、驗證、去重、豐富化等。
"""

import re
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import structlog
from urllib.parse import urlparse
import json

from .pipeline import PipelineProcessor, PipelineStage, ProcessingResult, ProcessingStatus
from ..platforms.base import JobData

logger = structlog.get_logger(__name__)


@dataclass
class DataQualityMetrics:
    """數據質量指標"""
    completeness: float = 0.0      # 完整性
    accuracy: float = 0.0          # 準確性
    consistency: float = 0.0       # 一致性
    validity: float = 0.0          # 有效性
    uniqueness: float = 0.0        # 唯一性
    timeliness: float = 0.0        # 時效性
    overall_score: float = 0.0     # 總體評分
    
    def calculate_overall_score(self) -> float:
        """計算總體評分"""
        scores = [
            self.completeness,
            self.accuracy,
            self.consistency,
            self.validity,
            self.uniqueness,
            self.timeliness
        ]
        self.overall_score = sum(scores) / len(scores)
        return self.overall_score


class DataProcessor(PipelineProcessor):
    """數據處理器基類"""
    
    def __init__(self, stage: PipelineStage, config: Dict[str, Any] = None):
        super().__init__(stage, config)
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None
    
    async def process(self, data: Any) -> ProcessingResult:
        """處理數據
        
        Args:
            data: 輸入數據
            
        Returns:
            ProcessingResult: 處理結果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            processed_data = await self._process_data(data)
            processing_time = asyncio.get_event_loop().time() - start_time
            
            self.processed_count += 1
            
            return ProcessingResult(
                status=ProcessingStatus.COMPLETED,
                data=processed_data,
                stage=self.stage,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            self.error_count += 1
            
            self.logger.error(
                "數據處理失敗",
                stage=self.stage.value,
                error=str(e),
                data_type=type(data).__name__
            )
            
            return ProcessingResult(
                status=ProcessingStatus.FAILED,
                error=str(e),
                stage=self.stage,
                processing_time=processing_time
            )
    
    @abstractmethod
    async def _process_data(self, data: Any) -> Any:
        """處理數據的具體實現
        
        Args:
            data: 輸入數據
            
        Returns:
            Any: 處理後的數據
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取處理統計
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "success_rate": (
                self.processed_count / (self.processed_count + self.error_count)
                if (self.processed_count + self.error_count) > 0 else 0.0
            )
        }


class JobDataProcessor(DataProcessor):
    """職位數據處理器
    
    專門處理JobData對象的清洗和標準化。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.CLEANING, config)
        
        # 配置選項
        self.min_title_length = config.get("min_title_length", 2) if config else 2
        self.max_title_length = config.get("max_title_length", 200) if config else 200
        self.min_description_length = config.get("min_description_length", 10) if config else 10
        self.normalize_salary = config.get("normalize_salary", True) if config else True
        self.extract_skills = config.get("extract_skills", True) if config else True
        
        # 技能關鍵詞
        self.skill_keywords = {
            "programming": [
                "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
                "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "sql"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "express",
                "laravel", "rails", "asp.net", "tensorflow", "pytorch", "keras"
            ],
            "tools": [
                "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp",
                "linux", "windows", "macos", "mysql", "postgresql", "mongodb", "redis"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving",
                "analytical", "creative", "adaptable", "detail oriented"
            ]
        }
    
    async def _process_data(self, data: JobData) -> JobData:
        """處理職位數據
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 處理後的職位數據
        """
        if not isinstance(data, JobData):
            raise ValueError(f"期望JobData類型，得到 {type(data)}")
        
        # 創建副本以避免修改原始數據
        processed_data = JobData(
            title=self._clean_title(data.title),
            company=self._clean_company(data.company),
            location=self._clean_location(data.location),
            url=data.url,
            description=self._clean_description(data.description),
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            salary_currency=data.salary_currency,
            salary_period=data.salary_period,
            job_type=self._normalize_job_type(data.job_type),
            experience_level=self._normalize_experience_level(data.experience_level),
            platform=data.platform,
            job_id=data.job_id,
            external_id=data.external_id,
            posted_date=data.posted_date,
            scraped_date=data.scraped_date,
            raw_data=data.raw_data
        )
        
        # 標準化薪資
        if self.normalize_salary:
            processed_data = self._normalize_salary(processed_data)
        
        # 提取技能
        if self.extract_skills:
            skills = self._extract_skills(processed_data.description)
            if processed_data.raw_data is None:
                processed_data.raw_data = {}
            processed_data.raw_data["extracted_skills"] = skills
        
        # 添加處理時間戳
        processed_data.raw_data["processed_at"] = datetime.utcnow().isoformat()
        
        return processed_data
    
    def _clean_title(self, title: str) -> str:
        """清洗職位標題
        
        Args:
            title: 原始標題
            
        Returns:
            str: 清洗後的標題
        """
        if not title:
            return ""
        
        # 移除多餘的空格和特殊字符
        title = re.sub(r'\s+', ' ', title.strip())
        
        # 移除HTML標籤
        title = re.sub(r'<[^>]+>', '', title)
        
        # 移除特殊符號
        title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)
        
        # 長度檢查
        if len(title) < self.min_title_length or len(title) > self.max_title_length:
            self.logger.warning(
                "職位標題長度異常",
                title=title,
                length=len(title)
            )
        
        return title
    
    def _clean_company(self, company: str) -> str:
        """清洗公司名稱
        
        Args:
            company: 原始公司名稱
            
        Returns:
            str: 清洗後的公司名稱
        """
        if not company:
            return ""
        
        # 移除多餘的空格
        company = re.sub(r'\s+', ' ', company.strip())
        
        # 移除HTML標籤
        company = re.sub(r'<[^>]+>', '', company)
        
        # 移除常見的後綴
        suffixes = [r'\s*\(.*\)$', r'\s*-.*$', r'\s*\|.*$']
        for suffix in suffixes:
            company = re.sub(suffix, '', company)
        
        return company.strip()
    
    def _clean_location(self, location: str) -> str:
        """清洗位置信息
        
        Args:
            location: 原始位置
            
        Returns:
            str: 清洗後的位置
        """
        if not location:
            return ""
        
        # 移除多餘的空格
        location = re.sub(r'\s+', ' ', location.strip())
        
        # 移除HTML標籤
        location = re.sub(r'<[^>]+>', '', location)
        
        # 標準化常見的位置格式
        location = re.sub(r'\s*,\s*', ', ', location)
        
        return location
    
    def _clean_description(self, description: str) -> str:
        """清洗職位描述
        
        Args:
            description: 原始描述
            
        Returns:
            str: 清洗後的描述
        """
        if not description:
            return ""
        
        # 移除HTML標籤但保留換行
        description = re.sub(r'<br[^>]*>', '\n', description)
        description = re.sub(r'<p[^>]*>', '\n', description)
        description = re.sub(r'</p>', '\n', description)
        description = re.sub(r'<[^>]+>', '', description)
        
        # 解碼HTML實體
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        for entity, char in html_entities.items():
            description = description.replace(entity, char)
        
        # 標準化空格和換行
        description = re.sub(r'\n\s*\n', '\n\n', description)
        description = re.sub(r'[ \t]+', ' ', description)
        
        # 移除開頭和結尾的空格
        description = description.strip()
        
        # 長度檢查
        if len(description) < self.min_description_length:
            self.logger.warning(
                "職位描述過短",
                length=len(description)
            )
        
        return description
    
    def _normalize_job_type(self, job_type: Optional[str]) -> Optional[str]:
        """標準化工作類型
        
        Args:
            job_type: 原始工作類型
            
        Returns:
            Optional[str]: 標準化的工作類型
        """
        if not job_type:
            return None
        
        job_type = job_type.lower().strip()
        
        # 標準化映射
        type_mapping = {
            "full-time": "full-time",
            "fulltime": "full-time",
            "full time": "full-time",
            "part-time": "part-time",
            "parttime": "part-time",
            "part time": "part-time",
            "contract": "contract",
            "contractor": "contract",
            "freelance": "freelance",
            "temporary": "temporary",
            "temp": "temporary",
            "internship": "internship",
            "intern": "internship"
        }
        
        return type_mapping.get(job_type, job_type)
    
    def _normalize_experience_level(self, experience_level: Optional[str]) -> Optional[str]:
        """標準化經驗水平
        
        Args:
            experience_level: 原始經驗水平
            
        Returns:
            Optional[str]: 標準化的經驗水平
        """
        if not experience_level:
            return None
        
        experience_level = experience_level.lower().strip()
        
        # 標準化映射
        level_mapping = {
            "entry": "entry",
            "entry-level": "entry",
            "junior": "entry",
            "associate": "entry",
            "mid": "mid",
            "mid-level": "mid",
            "intermediate": "mid",
            "senior": "senior",
            "senior-level": "senior",
            "lead": "senior",
            "principal": "senior",
            "executive": "executive",
            "director": "executive",
            "manager": "executive"
        }
        
        return level_mapping.get(experience_level, experience_level)
    
    def _normalize_salary(self, data: JobData) -> JobData:
        """標準化薪資信息
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 標準化薪資後的數據
        """
        if not data.salary_min and not data.salary_max:
            return data
        
        # 轉換為年薪（USD）
        if data.salary_period == "hourly" and data.salary_min:
            # 假設每年工作2080小時（40小時/週 * 52週）
            data.salary_min = int(data.salary_min * 2080)
            if data.salary_max:
                data.salary_max = int(data.salary_max * 2080)
            data.salary_period = "yearly"
        
        elif data.salary_period == "monthly" and data.salary_min:
            data.salary_min = int(data.salary_min * 12)
            if data.salary_max:
                data.salary_max = int(data.salary_max * 12)
            data.salary_period = "yearly"
        
        # 貨幣轉換（簡化版本，實際應該使用實時匯率）
        if data.salary_currency != "USD":
            conversion_rates = {
                "EUR": 1.1,
                "GBP": 1.3,
                "CAD": 0.8,
                "AUD": 0.7
            }
            
            rate = conversion_rates.get(data.salary_currency, 1.0)
            if data.salary_min:
                data.salary_min = int(data.salary_min * rate)
            if data.salary_max:
                data.salary_max = int(data.salary_max * rate)
            data.salary_currency = "USD"
        
        return data
    
    def _extract_skills(self, description: str) -> Dict[str, List[str]]:
        """從職位描述中提取技能
        
        Args:
            description: 職位描述
            
        Returns:
            Dict[str, List[str]]: 按類別分組的技能列表
        """
        if not description:
            return {}
        
        description_lower = description.lower()
        extracted_skills = {}
        
        for category, keywords in self.skill_keywords.items():
            found_skills = []
            for keyword in keywords:
                # 使用詞邊界匹配，避免部分匹配
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, description_lower):
                    found_skills.append(keyword)
            
            if found_skills:
                extracted_skills[category] = found_skills
        
        return extracted_skills


class CompanyDataProcessor(DataProcessor):
    """公司數據處理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.CLEANING, config)
    
    async def _process_data(self, data: Any) -> Any:
        """處理公司數據
        
        Args:
            data: 公司數據
            
        Returns:
            Any: 處理後的公司數據
        """
        # 實現公司數據清洗邏輯
        return data


class SalaryDataProcessor(DataProcessor):
    """薪資數據處理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.CLEANING, config)
    
    async def _process_data(self, data: Any) -> Any:
        """處理薪資數據
        
        Args:
            data: 薪資數據
            
        Returns:
            Any: 處理後的薪資數據
        """
        # 實現薪資數據清洗邏輯
        return data


class DuplicateRemover(DataProcessor):
    """去重處理器
    
    基於多種策略識別和移除重複的職位數據。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.DEDUPLICATION, config)
        
        # 去重策略配置
        self.strategies = config.get("strategies", ["url", "content"]) if config else ["url", "content"]
        self.similarity_threshold = config.get("similarity_threshold", 0.8) if config else 0.8
        
        # 已見過的數據緩存
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()
        self.seen_content: List[Tuple[str, str]] = []  # (hash, content)
    
    async def _process_data(self, data: JobData) -> JobData:
        """去重處理
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 去重後的數據
        """
        if not isinstance(data, JobData):
            raise ValueError(f"期望JobData類型，得到 {type(data)}")
        
        # URL去重
        if "url" in self.strategies and data.url:
            if data.url in self.seen_urls:
                raise ValueError(f"重複的URL: {data.url}")
            self.seen_urls.add(data.url)
        
        # 內容去重
        if "content" in self.strategies:
            content_hash = self._calculate_content_hash(data)
            if content_hash in self.seen_hashes:
                raise ValueError(f"重複的內容哈希: {content_hash}")
            self.seen_hashes.add(content_hash)
        
        # 相似性去重
        if "similarity" in self.strategies:
            if self._is_similar_content(data):
                raise ValueError("發現相似內容")
        
        return data
    
    def _calculate_content_hash(self, data: JobData) -> str:
        """計算內容哈希
        
        Args:
            data: 職位數據
            
        Returns:
            str: 內容哈希
        """
        # 組合關鍵字段
        content_parts = [
            data.title or "",
            data.company or "",
            data.location or "",
            (data.description or "")[:500]  # 只取前500字符
        ]
        
        content = "|".join(content_parts).lower()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _is_similar_content(self, data: JobData) -> bool:
        """檢查內容相似性
        
        Args:
            data: 職位數據
            
        Returns:
            bool: 是否存在相似內容
        """
        current_content = f"{data.title} {data.company} {data.description}".lower()
        
        for _, existing_content in self.seen_content:
            similarity = self._calculate_similarity(current_content, existing_content)
            if similarity > self.similarity_threshold:
                return True
        
        # 添加到已見內容
        content_hash = self._calculate_content_hash(data)
        self.seen_content.append((content_hash, current_content))
        
        # 限制緩存大小
        if len(self.seen_content) > 10000:
            self.seen_content = self.seen_content[-5000:]
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """計算文本相似性（簡化版本）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似性分數（0-1）
        """
        # 簡化的Jaccard相似性
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def clear_cache(self) -> None:
        """清空緩存"""
        self.seen_urls.clear()
        self.seen_hashes.clear()
        self.seen_content.clear()
        self.logger.debug("去重緩存已清空")


class DataValidator(DataProcessor):
    """數據驗證器
    
    驗證數據的完整性、有效性和一致性。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.VALIDATION, config)
        
        # 驗證規則配置
        self.required_fields = config.get("required_fields", ["title", "company"]) if config else ["title", "company"]
        self.validate_urls = config.get("validate_urls", True) if config else True
        self.validate_salary = config.get("validate_salary", True) if config else True
        self.validate_dates = config.get("validate_dates", True) if config else True
    
    async def _process_data(self, data: JobData) -> JobData:
        """驗證數據
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 驗證後的數據
        """
        if not isinstance(data, JobData):
            raise ValueError(f"期望JobData類型，得到 {type(data)}")
        
        errors = []
        
        # 必填字段驗證
        for field in self.required_fields:
            value = getattr(data, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"必填字段 {field} 為空")
        
        # URL驗證
        if self.validate_urls and data.url:
            if not self._is_valid_url(data.url):
                errors.append(f"無效的URL: {data.url}")
        
        # 薪資驗證
        if self.validate_salary:
            salary_errors = self._validate_salary(data)
            errors.extend(salary_errors)
        
        # 日期驗證
        if self.validate_dates:
            date_errors = self._validate_dates(data)
            errors.extend(date_errors)
        
        if errors:
            raise ValueError(f"數據驗證失敗: {'; '.join(errors)}")
        
        # 計算數據質量指標
        quality_metrics = self._calculate_quality_metrics(data)
        if data.raw_data is None:
            data.raw_data = {}
        data.raw_data["quality_metrics"] = quality_metrics.__dict__
        
        return data
    
    def _is_valid_url(self, url: str) -> bool:
        """驗證URL有效性
        
        Args:
            url: URL字符串
            
        Returns:
            bool: 是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _validate_salary(self, data: JobData) -> List[str]:
        """驗證薪資數據
        
        Args:
            data: 職位數據
            
        Returns:
            List[str]: 錯誤列表
        """
        errors = []
        
        # 薪資範圍驗證
        if data.salary_min is not None and data.salary_max is not None:
            if data.salary_min > data.salary_max:
                errors.append("最低薪資不能大於最高薪資")
        
        # 薪資合理性驗證
        if data.salary_min is not None:
            if data.salary_min < 0:
                errors.append("薪資不能為負數")
            elif data.salary_min > 1000000:  # 假設最高年薪100萬
                errors.append("薪資過高，可能有誤")
        
        # 貨幣和週期一致性
        if (data.salary_min or data.salary_max) and not data.salary_currency:
            errors.append("有薪資信息但缺少貨幣類型")
        
        return errors
    
    def _validate_dates(self, data: JobData) -> List[str]:
        """驗證日期數據
        
        Args:
            data: 職位數據
            
        Returns:
            List[str]: 錯誤列表
        """
        errors = []
        now = datetime.utcnow()
        
        # 發布日期驗證
        if data.posted_date:
            if data.posted_date > now:
                errors.append("發布日期不能是未來時間")
            elif data.posted_date < now - timedelta(days=365):
                errors.append("發布日期過於久遠")
        
        # 爬取日期驗證
        if data.scraped_date:
            if data.scraped_date > now + timedelta(minutes=5):  # 允許5分鐘時差
                errors.append("爬取日期不能是未來時間")
        
        # 日期邏輯驗證
        if data.posted_date and data.scraped_date:
            if data.posted_date > data.scraped_date:
                errors.append("發布日期不能晚於爬取日期")
        
        return errors
    
    def _calculate_quality_metrics(self, data: JobData) -> DataQualityMetrics:
        """計算數據質量指標
        
        Args:
            data: 職位數據
            
        Returns:
            DataQualityMetrics: 質量指標
        """
        metrics = DataQualityMetrics()
        
        # 完整性評分
        total_fields = 10  # 主要字段數量
        filled_fields = 0
        
        if data.title: filled_fields += 1
        if data.company: filled_fields += 1
        if data.location: filled_fields += 1
        if data.description: filled_fields += 1
        if data.salary_min or data.salary_max: filled_fields += 1
        if data.job_type: filled_fields += 1
        if data.experience_level: filled_fields += 1
        if data.posted_date: filled_fields += 1
        if data.url: filled_fields += 1
        if data.job_id: filled_fields += 1
        
        metrics.completeness = filled_fields / total_fields
        
        # 準確性評分（基於格式正確性）
        accuracy_score = 0.0
        accuracy_checks = 0
        
        if data.url:
            accuracy_checks += 1
            if self._is_valid_url(data.url):
                accuracy_score += 1
        
        if data.salary_min is not None:
            accuracy_checks += 1
            if data.salary_min >= 0:
                accuracy_score += 1
        
        metrics.accuracy = accuracy_score / accuracy_checks if accuracy_checks > 0 else 1.0
        
        # 一致性評分
        metrics.consistency = 1.0  # 簡化實現
        
        # 有效性評分
        metrics.validity = 1.0 if not self._validate_salary(data) and not self._validate_dates(data) else 0.5
        
        # 唯一性評分
        metrics.uniqueness = 1.0  # 由去重處理器處理
        
        # 時效性評分
        if data.posted_date:
            days_old = (datetime.utcnow() - data.posted_date).days
            metrics.timeliness = max(0.0, 1.0 - days_old / 30)  # 30天內為滿分
        else:
            metrics.timeliness = 0.5  # 無日期信息
        
        # 計算總體評分
        metrics.calculate_overall_score()
        
        return metrics


class DataEnricher(DataProcessor):
    """數據豐富化處理器
    
    通過外部API或規則增強數據內容。
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(PipelineStage.ENRICHMENT, config)
        
        # 豐富化配置
        self.enable_location_enrichment = config.get("enable_location_enrichment", True) if config else True
        self.enable_company_enrichment = config.get("enable_company_enrichment", True) if config else True
        self.enable_salary_enrichment = config.get("enable_salary_enrichment", True) if config else True
    
    async def _process_data(self, data: JobData) -> JobData:
        """豐富化數據
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 豐富化後的數據
        """
        if not isinstance(data, JobData):
            raise ValueError(f"期望JobData類型，得到 {type(data)}")
        
        enriched_data = data
        
        # 位置信息豐富化
        if self.enable_location_enrichment and data.location:
            enriched_data = await self._enrich_location(enriched_data)
        
        # 公司信息豐富化
        if self.enable_company_enrichment and data.company:
            enriched_data = await self._enrich_company(enriched_data)
        
        # 薪資信息豐富化
        if self.enable_salary_enrichment:
            enriched_data = await self._enrich_salary(enriched_data)
        
        return enriched_data
    
    async def _enrich_location(self, data: JobData) -> JobData:
        """豐富化位置信息
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 豐富化後的數據
        """
        # 實現位置信息豐富化邏輯
        # 例如：解析城市、州、國家，添加經緯度等
        
        if data.raw_data is None:
            data.raw_data = {}
        
        # 簡化實現：解析位置組件
        location_parts = data.location.split(',')
        if len(location_parts) >= 2:
            data.raw_data["city"] = location_parts[0].strip()
            data.raw_data["state_country"] = location_parts[1].strip()
        
        return data
    
    async def _enrich_company(self, data: JobData) -> JobData:
        """豐富化公司信息
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 豐富化後的數據
        """
        # 實現公司信息豐富化邏輯
        # 例如：添加公司規模、行業、評分等
        
        if data.raw_data is None:
            data.raw_data = {}
        
        # 簡化實現：基於公司名稱推斷信息
        company_lower = data.company.lower()
        
        # 識別知名公司
        tech_companies = ["google", "microsoft", "apple", "amazon", "facebook", "meta"]
        if any(company in company_lower for company in tech_companies):
            data.raw_data["company_type"] = "tech_giant"
            data.raw_data["estimated_size"] = "large"
        
        return data
    
    async def _enrich_salary(self, data: JobData) -> JobData:
        """豐富化薪資信息
        
        Args:
            data: 職位數據
            
        Returns:
            JobData: 豐富化後的數據
        """
        # 實現薪資信息豐富化邏輯
        # 例如：基於職位和位置估算薪資範圍
        
        if data.raw_data is None:
            data.raw_data = {}
        
        # 簡化實現：基於職位標題估算薪資等級
        title_lower = data.title.lower()
        
        if "senior" in title_lower or "lead" in title_lower:
            data.raw_data["salary_level"] = "senior"
        elif "junior" in title_lower or "entry" in title_lower:
            data.raw_data["salary_level"] = "junior"
        else:
            data.raw_data["salary_level"] = "mid"
        
        return data