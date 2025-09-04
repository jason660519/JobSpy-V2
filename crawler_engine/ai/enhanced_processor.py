#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強AI處理器

提供高級AI處理功能，包括：
- 智能技能提取和分類
- 薪資預測和市場分析
- 職位等級自動識別
- 公司規模和行業分析
- 工作要求智能解析
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import Counter, defaultdict


class SkillCategory(Enum):
    """技能分類枚舉"""
    PROGRAMMING = "programming"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    DEVOPS = "devops"
    SOFT_SKILLS = "soft_skills"
    INDUSTRY_SPECIFIC = "industry_specific"
    TOOLS = "tools"
    CERTIFICATION = "certification"
    LANGUAGE = "language"


class ExperienceLevel(Enum):
    """經驗等級枚舉"""
    INTERN = "intern"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"


class CompanySize(Enum):
    """公司規模枚舉"""
    STARTUP = "startup"          # 1-50人
    SMALL = "small"              # 51-200人
    MEDIUM = "medium"            # 201-1000人
    LARGE = "large"              # 1001-5000人
    ENTERPRISE = "enterprise"    # 5000+人
    UNKNOWN = "unknown"


class Industry(Enum):
    """行業分類枚舉"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"
    MEDIA = "media"
    REAL_ESTATE = "real_estate"
    TRANSPORTATION = "transportation"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    HOSPITALITY = "hospitality"
    OTHER = "other"


@dataclass
class SkillExtraction:
    """技能提取結果"""
    skill_name: str
    category: SkillCategory
    confidence: float
    context: str
    importance_score: float
    years_required: Optional[int] = None
    proficiency_level: Optional[str] = None


@dataclass
class SalaryPrediction:
    """薪資預測結果"""
    predicted_min: float
    predicted_max: float
    confidence: float
    market_percentile: float
    factors: List[str]
    currency: str = "AUD"
    basis: str = "yearly"


@dataclass
class JobAnalysis:
    """職位分析結果"""
    experience_level: ExperienceLevel
    company_size: CompanySize
    industry: Industry
    skills: List[SkillExtraction]
    salary_prediction: Optional[SalaryPrediction]
    work_arrangement: str
    job_type: str
    urgency_level: str
    growth_potential: float
    market_demand: float
    analysis_confidence: float


@dataclass
class AIProcessingConfig:
    """AI處理配置"""
    # 技能提取
    extract_skills: bool = True
    skill_confidence_threshold: float = 0.6
    max_skills_per_job: int = 20
    
    # 薪資預測
    predict_salary: bool = True
    use_market_data: bool = True
    salary_confidence_threshold: float = 0.7
    
    # 職位分析
    analyze_experience_level: bool = True
    analyze_company_size: bool = True
    analyze_industry: bool = True
    
    # 市場分析
    calculate_market_demand: bool = True
    calculate_growth_potential: bool = True
    
    # 處理選項
    use_cached_results: bool = True
    parallel_processing: bool = False
    max_processing_time: int = 30  # 秒


class EnhancedAIProcessor:
    """增強AI處理器
    
    提供全面的AI驅動職位數據分析和增強功能。
    """
    
    def __init__(self, config: AIProcessingConfig):
        """初始化增強AI處理器
        
        Args:
            config: AI處理配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化技能數據庫
        self._init_skill_database()
        
        # 初始化薪資模型
        self._init_salary_model()
        
        # 初始化公司數據庫
        self._init_company_database()
        
        # 初始化行業分類器
        self._init_industry_classifier()
        
        # 統計信息
        self.stats = {
            'total_processed': 0,
            'skills_extracted': Counter(),
            'experience_levels': Counter(),
            'industries': Counter(),
            'processing_times': []
        }
    
    def _init_skill_database(self):
        """初始化技能數據庫"""
        self.skill_database = {
            SkillCategory.PROGRAMMING: {
                'python': {'aliases': ['python3', 'py'], 'weight': 1.0},
                'javascript': {'aliases': ['js', 'node.js', 'nodejs'], 'weight': 1.0},
                'java': {'aliases': ['jvm'], 'weight': 1.0},
                'c#': {'aliases': ['csharp', 'c-sharp', '.net'], 'weight': 1.0},
                'typescript': {'aliases': ['ts'], 'weight': 0.9},
                'go': {'aliases': ['golang'], 'weight': 0.8},
                'rust': {'aliases': [], 'weight': 0.7},
                'kotlin': {'aliases': [], 'weight': 0.7},
                'swift': {'aliases': [], 'weight': 0.7},
                'php': {'aliases': [], 'weight': 0.8},
                'ruby': {'aliases': [], 'weight': 0.7},
                'scala': {'aliases': [], 'weight': 0.6},
                'r': {'aliases': [], 'weight': 0.6},
                'matlab': {'aliases': [], 'weight': 0.5}
            },
            SkillCategory.FRAMEWORK: {
                'react': {'aliases': ['reactjs', 'react.js'], 'weight': 1.0},
                'angular': {'aliases': ['angularjs'], 'weight': 0.9},
                'vue': {'aliases': ['vue.js', 'vuejs'], 'weight': 0.8},
                'django': {'aliases': [], 'weight': 0.8},
                'flask': {'aliases': [], 'weight': 0.7},
                'spring': {'aliases': ['spring boot', 'springboot'], 'weight': 0.9},
                'express': {'aliases': ['express.js', 'expressjs'], 'weight': 0.8},
                'laravel': {'aliases': [], 'weight': 0.7},
                'rails': {'aliases': ['ruby on rails'], 'weight': 0.7},
                'asp.net': {'aliases': ['aspnet'], 'weight': 0.8}
            },
            SkillCategory.DATABASE: {
                'postgresql': {'aliases': ['postgres', 'psql'], 'weight': 1.0},
                'mysql': {'aliases': [], 'weight': 1.0},
                'mongodb': {'aliases': ['mongo'], 'weight': 0.9},
                'redis': {'aliases': [], 'weight': 0.8},
                'elasticsearch': {'aliases': ['elastic'], 'weight': 0.7},
                'oracle': {'aliases': [], 'weight': 0.8},
                'sql server': {'aliases': ['mssql', 'sqlserver'], 'weight': 0.8},
                'sqlite': {'aliases': [], 'weight': 0.6},
                'cassandra': {'aliases': [], 'weight': 0.5},
                'dynamodb': {'aliases': [], 'weight': 0.6}
            },
            SkillCategory.CLOUD: {
                'aws': {'aliases': ['amazon web services'], 'weight': 1.0},
                'azure': {'aliases': ['microsoft azure'], 'weight': 1.0},
                'gcp': {'aliases': ['google cloud', 'google cloud platform'], 'weight': 0.9},
                'docker': {'aliases': [], 'weight': 1.0},
                'kubernetes': {'aliases': ['k8s'], 'weight': 0.9},
                'terraform': {'aliases': [], 'weight': 0.8},
                'ansible': {'aliases': [], 'weight': 0.7},
                'jenkins': {'aliases': [], 'weight': 0.7},
                'gitlab ci': {'aliases': ['gitlab-ci'], 'weight': 0.6},
                'github actions': {'aliases': [], 'weight': 0.6}
            },
            SkillCategory.DEVOPS: {
                'ci/cd': {'aliases': ['continuous integration', 'continuous deployment'], 'weight': 1.0},
                'git': {'aliases': [], 'weight': 1.0},
                'linux': {'aliases': ['unix'], 'weight': 0.9},
                'bash': {'aliases': ['shell scripting'], 'weight': 0.8},
                'monitoring': {'aliases': ['observability'], 'weight': 0.8},
                'logging': {'aliases': [], 'weight': 0.7},
                'security': {'aliases': ['cybersecurity'], 'weight': 0.9},
                'networking': {'aliases': [], 'weight': 0.8}
            },
            SkillCategory.SOFT_SKILLS: {
                'leadership': {'aliases': ['team leadership'], 'weight': 1.0},
                'communication': {'aliases': [], 'weight': 1.0},
                'problem solving': {'aliases': ['problem-solving'], 'weight': 1.0},
                'teamwork': {'aliases': ['collaboration'], 'weight': 0.9},
                'project management': {'aliases': [], 'weight': 0.9},
                'agile': {'aliases': ['scrum', 'kanban'], 'weight': 0.8},
                'mentoring': {'aliases': ['coaching'], 'weight': 0.7},
                'analytical thinking': {'aliases': [], 'weight': 0.8}
            }
        }
        
        # 創建反向索引以便快速查找
        self.skill_lookup = {}
        for category, skills in self.skill_database.items():
            for skill, data in skills.items():
                self.skill_lookup[skill.lower()] = (skill, category, data['weight'])
                for alias in data['aliases']:
                    self.skill_lookup[alias.lower()] = (skill, category, data['weight'])
    
    def _init_salary_model(self):
        """初始化薪資預測模型"""
        # 基於澳大利亞市場的薪資基準（年薪，澳元）
        self.salary_benchmarks = {
            ExperienceLevel.INTERN: {'min': 25000, 'max': 35000},
            ExperienceLevel.ENTRY: {'min': 45000, 'max': 65000},
            ExperienceLevel.JUNIOR: {'min': 55000, 'max': 75000},
            ExperienceLevel.MID: {'min': 70000, 'max': 95000},
            ExperienceLevel.SENIOR: {'min': 90000, 'max': 130000},
            ExperienceLevel.LEAD: {'min': 120000, 'max': 160000},
            ExperienceLevel.PRINCIPAL: {'min': 150000, 'max': 200000},
            ExperienceLevel.DIRECTOR: {'min': 180000, 'max': 250000}
        }
        
        # 技能薪資加成係數
        self.skill_salary_multipliers = {
            'python': 1.1,
            'aws': 1.15,
            'kubernetes': 1.2,
            'machine learning': 1.25,
            'ai': 1.3,
            'blockchain': 1.2,
            'security': 1.15,
            'devops': 1.1,
            'leadership': 1.2
        }
        
        # 行業薪資調整係數
        self.industry_salary_adjustments = {
            Industry.TECHNOLOGY: 1.1,
            Industry.FINANCE: 1.15,
            Industry.CONSULTING: 1.05,
            Industry.HEALTHCARE: 1.0,
            Industry.GOVERNMENT: 0.9,
            Industry.EDUCATION: 0.85,
            Industry.NONPROFIT: 0.8
        }
    
    def _init_company_database(self):
        """初始化公司數據庫"""
        # 知名公司及其規模
        self.company_database = {
            # 大型科技公司
            'google': {'size': CompanySize.ENTERPRISE, 'industry': Industry.TECHNOLOGY},
            'microsoft': {'size': CompanySize.ENTERPRISE, 'industry': Industry.TECHNOLOGY},
            'amazon': {'size': CompanySize.ENTERPRISE, 'industry': Industry.TECHNOLOGY},
            'apple': {'size': CompanySize.ENTERPRISE, 'industry': Industry.TECHNOLOGY},
            'meta': {'size': CompanySize.ENTERPRISE, 'industry': Industry.TECHNOLOGY},
            'facebook': {'size': CompanySize.ENTERPRISE, 'industry': Industry.TECHNOLOGY},
            
            # 澳大利亞公司
            'atlassian': {'size': CompanySize.LARGE, 'industry': Industry.TECHNOLOGY},
            'canva': {'size': CompanySize.LARGE, 'industry': Industry.TECHNOLOGY},
            'seek': {'size': CompanySize.LARGE, 'industry': Industry.TECHNOLOGY},
            'realestate.com.au': {'size': CompanySize.LARGE, 'industry': Industry.REAL_ESTATE},
            'commonwealth bank': {'size': CompanySize.ENTERPRISE, 'industry': Industry.FINANCE},
            'westpac': {'size': CompanySize.ENTERPRISE, 'industry': Industry.FINANCE},
            'anz': {'size': CompanySize.ENTERPRISE, 'industry': Industry.FINANCE},
            'nab': {'size': CompanySize.ENTERPRISE, 'industry': Industry.FINANCE},
            
            # 諮詢公司
            'mckinsey': {'size': CompanySize.LARGE, 'industry': Industry.CONSULTING},
            'bcg': {'size': CompanySize.LARGE, 'industry': Industry.CONSULTING},
            'bain': {'size': CompanySize.LARGE, 'industry': Industry.CONSULTING},
            'deloitte': {'size': CompanySize.ENTERPRISE, 'industry': Industry.CONSULTING},
            'pwc': {'size': CompanySize.ENTERPRISE, 'industry': Industry.CONSULTING},
            'ey': {'size': CompanySize.ENTERPRISE, 'industry': Industry.CONSULTING},
            'kpmg': {'size': CompanySize.ENTERPRISE, 'industry': Industry.CONSULTING}
        }
        
        # 公司規模關鍵詞
        self.size_keywords = {
            CompanySize.STARTUP: ['startup', 'early stage', 'seed', 'series a'],
            CompanySize.SMALL: ['small team', 'boutique', 'growing team'],
            CompanySize.MEDIUM: ['established', 'mid-size', 'growing company'],
            CompanySize.LARGE: ['large company', 'multinational', 'global'],
            CompanySize.ENTERPRISE: ['fortune 500', 'enterprise', 'global leader', 'industry leader']
        }
    
    def _init_industry_classifier(self):
        """初始化行業分類器"""
        self.industry_keywords = {
            Industry.TECHNOLOGY: [
                'software', 'tech', 'it', 'saas', 'platform', 'app', 'digital',
                'artificial intelligence', 'machine learning', 'data science',
                'cloud', 'cybersecurity', 'fintech', 'edtech', 'healthtech'
            ],
            Industry.FINANCE: [
                'bank', 'finance', 'investment', 'trading', 'insurance',
                'wealth management', 'asset management', 'financial services',
                'credit', 'lending', 'payments', 'cryptocurrency'
            ],
            Industry.HEALTHCARE: [
                'healthcare', 'medical', 'hospital', 'pharmaceutical', 'biotech',
                'health', 'clinical', 'patient', 'therapy', 'diagnostic'
            ],
            Industry.EDUCATION: [
                'education', 'university', 'school', 'learning', 'training',
                'academic', 'research', 'student', 'teaching', 'curriculum'
            ],
            Industry.RETAIL: [
                'retail', 'ecommerce', 'shopping', 'consumer', 'brand',
                'merchandise', 'store', 'marketplace', 'fashion', 'beauty'
            ],
            Industry.CONSULTING: [
                'consulting', 'advisory', 'strategy', 'management consulting',
                'business consulting', 'transformation', 'optimization'
            ],
            Industry.GOVERNMENT: [
                'government', 'public sector', 'federal', 'state', 'council',
                'agency', 'department', 'ministry', 'public service'
            ]
        }
    
    def process_job_data(self, job_data: Dict[str, Any]) -> JobAnalysis:
        """處理單個職位數據
        
        Args:
            job_data: 職位數據
            
        Returns:
            JobAnalysis: 分析結果
        """
        start_time = datetime.now()
        
        try:
            # 1. 技能提取
            skills = []
            if self.config.extract_skills:
                skills = self._extract_skills(job_data)
            
            # 2. 經驗等級分析
            experience_level = ExperienceLevel.MID  # 默認
            if self.config.analyze_experience_level:
                experience_level = self._analyze_experience_level(job_data)
            
            # 3. 公司規模分析
            company_size = CompanySize.UNKNOWN
            if self.config.analyze_company_size:
                company_size = self._analyze_company_size(job_data)
            
            # 4. 行業分析
            industry = Industry.OTHER
            if self.config.analyze_industry:
                industry = self._analyze_industry(job_data)
            
            # 5. 薪資預測
            salary_prediction = None
            if self.config.predict_salary:
                salary_prediction = self._predict_salary(
                    job_data, experience_level, skills, industry, company_size
                )
            
            # 6. 工作安排分析
            work_arrangement = self._analyze_work_arrangement(job_data)
            
            # 7. 職位類型分析
            job_type = self._analyze_job_type(job_data)
            
            # 8. 緊急程度分析
            urgency_level = self._analyze_urgency(job_data)
            
            # 9. 成長潛力評估
            growth_potential = 0.5  # 默認
            if self.config.calculate_growth_potential:
                growth_potential = self._calculate_growth_potential(job_data, skills, industry)
            
            # 10. 市場需求評估
            market_demand = 0.5  # 默認
            if self.config.calculate_market_demand:
                market_demand = self._calculate_market_demand(skills, experience_level)
            
            # 11. 計算整體分析信心度
            analysis_confidence = self._calculate_analysis_confidence(
                skills, experience_level, company_size, industry
            )
            
            # 更新統計
            self._update_stats(skills, experience_level, industry, start_time)
            
            return JobAnalysis(
                experience_level=experience_level,
                company_size=company_size,
                industry=industry,
                skills=skills,
                salary_prediction=salary_prediction,
                work_arrangement=work_arrangement,
                job_type=job_type,
                urgency_level=urgency_level,
                growth_potential=growth_potential,
                market_demand=market_demand,
                analysis_confidence=analysis_confidence
            )
            
        except Exception as e:
            self.logger.error(f"AI處理失敗: {e}")
            return JobAnalysis(
                experience_level=ExperienceLevel.MID,
                company_size=CompanySize.UNKNOWN,
                industry=Industry.OTHER,
                skills=[],
                salary_prediction=None,
                work_arrangement="onsite",
                job_type="full-time",
                urgency_level="normal",
                growth_potential=0.5,
                market_demand=0.5,
                analysis_confidence=0.0
            )
    
    def _extract_skills(self, job_data: Dict[str, Any]) -> List[SkillExtraction]:
        """提取技能
        
        Args:
            job_data: 職位數據
            
        Returns:
            List[SkillExtraction]: 提取的技能列表
        """
        skills = []
        
        # 合併所有文本字段
        text_fields = ['title', 'description', 'requirements', 'benefits']
        combined_text = ' '.join([str(job_data.get(field, '')) for field in text_fields]).lower()
        
        # 查找技能
        found_skills = set()
        for skill_key, (skill_name, category, weight) in self.skill_lookup.items():
            if skill_key in combined_text and skill_name not in found_skills:
                # 計算上下文和重要性
                context = self._extract_skill_context(combined_text, skill_key)
                importance = self._calculate_skill_importance(skill_key, combined_text, weight)
                confidence = min(1.0, importance * weight)
                
                if confidence >= self.config.skill_confidence_threshold:
                    skills.append(SkillExtraction(
                        skill_name=skill_name,
                        category=category,
                        confidence=confidence,
                        context=context,
                        importance_score=importance
                    ))
                    found_skills.add(skill_name)
        
        # 按重要性排序並限制數量
        skills.sort(key=lambda x: x.importance_score, reverse=True)
        return skills[:self.config.max_skills_per_job]
    
    def _extract_skill_context(self, text: str, skill: str) -> str:
        """提取技能上下文
        
        Args:
            text: 文本
            skill: 技能關鍵詞
            
        Returns:
            str: 上下文
        """
        # 查找技能周圍的文本
        pattern = rf'.{{0,50}}{re.escape(skill)}.{{0,50}}'
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else ""
    
    def _calculate_skill_importance(self, skill: str, text: str, base_weight: float) -> float:
        """計算技能重要性
        
        Args:
            skill: 技能
            text: 文本
            base_weight: 基礎權重
            
        Returns:
            float: 重要性分數
        """
        # 計算出現頻率
        frequency = text.lower().count(skill.lower())
        
        # 位置權重（標題中的技能更重要）
        position_weight = 1.0
        if skill in text[:200]:  # 假設前200字符是標題和重要描述
            position_weight = 1.5
        
        # 上下文權重（必需技能 vs 優選技能）
        context_weight = 1.0
        context = self._extract_skill_context(text, skill)
        if any(word in context.lower() for word in ['required', 'must', 'essential', 'mandatory']):
            context_weight = 1.3
        elif any(word in context.lower() for word in ['preferred', 'nice to have', 'bonus']):
            context_weight = 0.8
        
        return min(1.0, (frequency * 0.3 + base_weight * 0.4 + position_weight * 0.2 + context_weight * 0.1))
    
    def _analyze_experience_level(self, job_data: Dict[str, Any]) -> ExperienceLevel:
        """分析經驗等級
        
        Args:
            job_data: 職位數據
            
        Returns:
            ExperienceLevel: 經驗等級
        """
        text = ' '.join([str(job_data.get(field, '')) for field in ['title', 'description']]).lower()
        
        # 關鍵詞匹配
        level_keywords = {
            ExperienceLevel.INTERN: ['intern', 'internship', 'student'],
            ExperienceLevel.ENTRY: ['entry', 'graduate', 'junior', 'trainee', '0-1 years', '0-2 years'],
            ExperienceLevel.JUNIOR: ['junior', '1-2 years', '1-3 years'],
            ExperienceLevel.MID: ['mid', 'intermediate', '2-5 years', '3-5 years'],
            ExperienceLevel.SENIOR: ['senior', '5+ years', '5-8 years', 'experienced'],
            ExperienceLevel.LEAD: ['lead', 'team lead', 'tech lead', 'technical lead'],
            ExperienceLevel.PRINCIPAL: ['principal', 'staff', 'architect'],
            ExperienceLevel.DIRECTOR: ['director', 'head of', 'vp', 'vice president']
        }
        
        scores = {}
        for level, keywords in level_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[level] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # 從年數推斷
        years_match = re.search(r'(\d+)\+?\s*years?', text)
        if years_match:
            years = int(years_match.group(1))
            if years <= 1:
                return ExperienceLevel.ENTRY
            elif years <= 3:
                return ExperienceLevel.JUNIOR
            elif years <= 5:
                return ExperienceLevel.MID
            elif years <= 8:
                return ExperienceLevel.SENIOR
            else:
                return ExperienceLevel.LEAD
        
        return ExperienceLevel.MID  # 默認
    
    def _analyze_company_size(self, job_data: Dict[str, Any]) -> CompanySize:
        """分析公司規模
        
        Args:
            job_data: 職位數據
            
        Returns:
            CompanySize: 公司規模
        """
        company_name = job_data.get('company', '').lower()
        
        # 檢查已知公司
        for company, info in self.company_database.items():
            if company in company_name:
                return info['size']
        
        # 檢查描述中的關鍵詞
        description = job_data.get('description', '').lower()
        for size, keywords in self.size_keywords.items():
            if any(keyword in description for keyword in keywords):
                return size
        
        return CompanySize.UNKNOWN
    
    def _analyze_industry(self, job_data: Dict[str, Any]) -> Industry:
        """分析行業
        
        Args:
            job_data: 職位數據
            
        Returns:
            Industry: 行業
        """
        text = ' '.join([
            str(job_data.get(field, '')) for field in ['company', 'title', 'description']
        ]).lower()
        
        scores = {}
        for industry, keywords in self.industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[industry] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return Industry.OTHER
    
    def _predict_salary(self, job_data: Dict[str, Any], experience_level: ExperienceLevel,
                       skills: List[SkillExtraction], industry: Industry,
                       company_size: CompanySize) -> Optional[SalaryPrediction]:
        """預測薪資
        
        Args:
            job_data: 職位數據
            experience_level: 經驗等級
            skills: 技能列表
            industry: 行業
            company_size: 公司規模
            
        Returns:
            Optional[SalaryPrediction]: 薪資預測
        """
        if experience_level not in self.salary_benchmarks:
            return None
        
        base_range = self.salary_benchmarks[experience_level]
        base_min = base_range['min']
        base_max = base_range['max']
        
        # 技能加成
        skill_multiplier = 1.0
        valuable_skills = []
        for skill in skills:
            skill_name = skill.skill_name.lower()
            if skill_name in self.skill_salary_multipliers:
                multiplier = self.skill_salary_multipliers[skill_name]
                skill_multiplier *= multiplier
                valuable_skills.append(skill_name)
        
        # 行業調整
        industry_adjustment = self.industry_salary_adjustments.get(industry, 1.0)
        
        # 公司規模調整
        size_adjustments = {
            CompanySize.STARTUP: 0.9,
            CompanySize.SMALL: 0.95,
            CompanySize.MEDIUM: 1.0,
            CompanySize.LARGE: 1.1,
            CompanySize.ENTERPRISE: 1.2
        }
        size_adjustment = size_adjustments.get(company_size, 1.0)
        
        # 計算最終薪資
        final_multiplier = skill_multiplier * industry_adjustment * size_adjustment
        predicted_min = int(base_min * final_multiplier)
        predicted_max = int(base_max * final_multiplier)
        
        # 計算信心度
        confidence_factors = [
            0.8,  # 基礎信心度
            0.1 if valuable_skills else 0.0,  # 技能匹配
            0.1 if industry != Industry.OTHER else 0.0  # 行業識別
        ]
        confidence = sum(confidence_factors)
        
        # 計算市場百分位
        market_percentile = min(95, max(5, 50 + (final_multiplier - 1) * 30))
        
        factors = []
        if skill_multiplier > 1.1:
            factors.append(f"高價值技能: {', '.join(valuable_skills)}")
        if industry_adjustment > 1.0:
            factors.append(f"高薪行業: {industry.value}")
        if size_adjustment > 1.0:
            factors.append(f"大型公司: {company_size.value}")
        
        return SalaryPrediction(
            predicted_min=predicted_min,
            predicted_max=predicted_max,
            confidence=confidence,
            market_percentile=market_percentile,
            factors=factors
        )
    
    def _analyze_work_arrangement(self, job_data: Dict[str, Any]) -> str:
        """分析工作安排
        
        Args:
            job_data: 職位數據
            
        Returns:
            str: 工作安排
        """
        text = ' '.join([str(job_data.get(field, '')) for field in ['title', 'description']]).lower()
        
        if any(word in text for word in ['remote', 'work from home', 'wfh', 'telecommute']):
            return 'remote'
        elif any(word in text for word in ['hybrid', 'flexible', 'mix of']):
            return 'hybrid'
        else:
            return 'onsite'
    
    def _analyze_job_type(self, job_data: Dict[str, Any]) -> str:
        """分析職位類型
        
        Args:
            job_data: 職位數據
            
        Returns:
            str: 職位類型
        """
        text = ' '.join([str(job_data.get(field, '')) for field in ['title', 'description']]).lower()
        
        if any(word in text for word in ['part-time', 'part time', 'casual']):
            return 'part-time'
        elif any(word in text for word in ['contract', 'contractor', 'freelance']):
            return 'contract'
        elif any(word in text for word in ['intern', 'internship']):
            return 'internship'
        else:
            return 'full-time'
    
    def _analyze_urgency(self, job_data: Dict[str, Any]) -> str:
        """分析緊急程度
        
        Args:
            job_data: 職位數據
            
        Returns:
            str: 緊急程度
        """
        text = ' '.join([str(job_data.get(field, '')) for field in ['title', 'description']]).lower()
        
        if any(word in text for word in ['urgent', 'asap', 'immediate', 'start immediately']):
            return 'urgent'
        elif any(word in text for word in ['soon', 'quickly', 'fast-paced']):
            return 'high'
        else:
            return 'normal'
    
    def _calculate_growth_potential(self, job_data: Dict[str, Any],
                                  skills: List[SkillExtraction], industry: Industry) -> float:
        """計算成長潛力
        
        Args:
            job_data: 職位數據
            skills: 技能列表
            industry: 行業
            
        Returns:
            float: 成長潛力分數 (0-1)
        """
        score = 0.5  # 基礎分數
        
        # 行業成長潛力
        industry_growth = {
            Industry.TECHNOLOGY: 0.9,
            Industry.HEALTHCARE: 0.8,
            Industry.FINANCE: 0.7,
            Industry.EDUCATION: 0.6,
            Industry.GOVERNMENT: 0.4
        }
        score += (industry_growth.get(industry, 0.5) - 0.5) * 0.3
        
        # 技能成長潛力
        high_growth_skills = ['ai', 'machine learning', 'blockchain', 'cloud', 'cybersecurity']
        skill_names = [skill.skill_name.lower() for skill in skills]
        growth_skill_count = sum(1 for skill in high_growth_skills if skill in skill_names)
        score += (growth_skill_count / len(high_growth_skills)) * 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_market_demand(self, skills: List[SkillExtraction],
                               experience_level: ExperienceLevel) -> float:
        """計算市場需求
        
        Args:
            skills: 技能列表
            experience_level: 經驗等級
            
        Returns:
            float: 市場需求分數 (0-1)
        """
        score = 0.5  # 基礎分數
        
        # 經驗等級需求
        level_demand = {
            ExperienceLevel.ENTRY: 0.6,
            ExperienceLevel.JUNIOR: 0.7,
            ExperienceLevel.MID: 0.9,
            ExperienceLevel.SENIOR: 0.8,
            ExperienceLevel.LEAD: 0.6
        }
        score += (level_demand.get(experience_level, 0.5) - 0.5) * 0.3
        
        # 高需求技能
        high_demand_skills = ['python', 'javascript', 'react', 'aws', 'docker', 'kubernetes']
        skill_names = [skill.skill_name.lower() for skill in skills]
        demand_skill_count = sum(1 for skill in high_demand_skills if skill in skill_names)
        score += (demand_skill_count / len(high_demand_skills)) * 0.2
        
        return min(1.0, max(0.0, score))
    
    def _calculate_analysis_confidence(self, skills: List[SkillExtraction],
                                     experience_level: ExperienceLevel,
                                     company_size: CompanySize,
                                     industry: Industry) -> float:
        """計算分析信心度
        
        Args:
            skills: 技能列表
            experience_level: 經驗等級
            company_size: 公司規模
            industry: 行業
            
        Returns:
            float: 信心度分數 (0-1)
        """
        confidence_factors = [
            0.2,  # 基礎信心度
            0.3 if len(skills) >= 5 else 0.1,  # 技能提取質量
            0.2 if experience_level != ExperienceLevel.MID else 0.1,  # 經驗等級識別
            0.15 if company_size != CompanySize.UNKNOWN else 0.0,  # 公司規模識別
            0.15 if industry != Industry.OTHER else 0.0  # 行業識別
        ]
        
        return sum(confidence_factors)
    
    def _update_stats(self, skills: List[SkillExtraction], experience_level: ExperienceLevel,
                     industry: Industry, start_time: datetime):
        """更新統計信息
        
        Args:
            skills: 技能列表
            experience_level: 經驗等級
            industry: 行業
            start_time: 開始時間
        """
        self.stats['total_processed'] += 1
        
        for skill in skills:
            self.stats['skills_extracted'][skill.skill_name] += 1
        
        self.stats['experience_levels'][experience_level.value] += 1
        self.stats['industries'][industry.value] += 1
        
        processing_time = (datetime.now() - start_time).total_seconds()
        self.stats['processing_times'].append(processing_time)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """獲取處理統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        avg_processing_time = (
            sum(self.stats['processing_times']) / len(self.stats['processing_times'])
            if self.stats['processing_times'] else 0
        )
        
        return {
            'total_processed': self.stats['total_processed'],
            'top_skills': dict(self.stats['skills_extracted'].most_common(10)),
            'experience_levels': dict(self.stats['experience_levels']),
            'industries': dict(self.stats['industries']),
            'average_processing_time': round(avg_processing_time, 3)
        }


def create_enhanced_ai_processor(config: Optional[AIProcessingConfig] = None) -> EnhancedAIProcessor:
    """創建增強AI處理器的便捷函數
    
    Args:
        config: AI處理配置，如果為None則使用默認配置
        
    Returns:
        EnhancedAIProcessor: 增強AI處理器實例
    """
    if config is None:
        config = AIProcessingConfig()
    
    return EnhancedAIProcessor(config)