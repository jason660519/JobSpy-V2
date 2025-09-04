#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試數據生成器
為測試提供模擬數據和測試場景
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

class JobLevel(Enum):
    """職位級別"""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"

class JobType(Enum):
    """工作類型"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"

class Platform(Enum):
    """招聘平台"""
    INDEED = "indeed"
    LINKEDIN = "linkedin"
    GLASSDOOR = "glassdoor"
    ZIPRECRUITER = "ziprecruiter"
    MONSTER = "monster"

@dataclass
class TestJobData:
    """測試職位數據"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    company: str = ""
    location: str = ""
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    job_type: JobType = JobType.FULL_TIME
    level: JobLevel = JobLevel.MID
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    platform: Platform = Platform.INDEED
    url: str = ""
    posted_date: datetime = field(default_factory=datetime.now)
    expires_date: Optional[datetime] = None
    remote: bool = False
    visa_sponsor: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "job_type": self.job_type.value,
            "level": self.level.value,
            "description": self.description,
            "requirements": self.requirements,
            "benefits": self.benefits,
            "skills": self.skills,
            "platform": self.platform.value,
            "url": self.url,
            "posted_date": self.posted_date.isoformat(),
            "expires_date": self.expires_date.isoformat() if self.expires_date else None,
            "remote": self.remote,
            "visa_sponsor": self.visa_sponsor
        }

@dataclass
class TestCompanyData:
    """測試公司數據"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    industry: str = ""
    size: str = ""
    location: str = ""
    website: str = ""
    description: str = ""
    rating: float = 0.0
    review_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry,
            "size": self.size,
            "location": self.location,
            "website": self.website,
            "description": self.description,
            "rating": self.rating,
            "review_count": self.review_count
        }

@dataclass
class TestUserData:
    """測試用戶數據"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)
    search_history: List[str] = field(default_factory=list)
    saved_jobs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "preferences": self.preferences,
            "search_history": self.search_history,
            "saved_jobs": self.saved_jobs
        }

class TestDataGenerator:
    """測試數據生成器"""
    
    # 預定義數據
    JOB_TITLES = [
        "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Machine Learning Engineer", "QA Engineer", "UX Designer", "UI Designer",
        "Technical Writer", "Business Analyst", "Project Manager", "Scrum Master",
        "Database Administrator", "System Administrator", "Security Engineer",
        "Mobile Developer", "Game Developer", "AI Researcher", "Cloud Architect"
    ]
    
    COMPANIES = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla",
        "Spotify", "Uber", "Airbnb", "Stripe", "Slack", "Zoom", "Dropbox",
        "GitHub", "GitLab", "Atlassian", "Salesforce", "Oracle", "IBM",
        "Adobe", "Nvidia", "Intel", "AMD", "Qualcomm", "Cisco", "VMware"
    ]
    
    LOCATIONS = [
        "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
        "Boston, MA", "Los Angeles, CA", "Chicago, IL", "Denver, CO",
        "Atlanta, GA", "Miami, FL", "Portland, OR", "San Diego, CA",
        "Remote", "Hybrid", "Multiple Locations"
    ]
    
    SKILLS = [
        "Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript",
        "React", "Vue.js", "Angular", "Node.js", "Django", "Flask", "FastAPI",
        "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Docker", "Kubernetes",
        "AWS", "GCP", "Azure", "Terraform", "Jenkins", "Git", "Linux",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
        "NumPy", "Scikit-learn", "SQL", "NoSQL", "GraphQL", "REST API",
        "Microservices", "Agile", "Scrum", "DevOps", "CI/CD"
    ]
    
    INDUSTRIES = [
        "Technology", "Finance", "Healthcare", "E-commerce", "Gaming",
        "Education", "Media", "Transportation", "Real Estate", "Energy",
        "Retail", "Manufacturing", "Consulting", "Government", "Non-profit"
    ]
    
    COMPANY_SIZES = [
        "1-10 employees", "11-50 employees", "51-200 employees",
        "201-500 employees", "501-1000 employees", "1001-5000 employees",
        "5001-10000 employees", "10000+ employees"
    ]
    
    BENEFITS = [
        "Health Insurance", "Dental Insurance", "Vision Insurance",
        "401(k) Matching", "Flexible PTO", "Remote Work", "Flexible Hours",
        "Stock Options", "Bonus", "Professional Development", "Gym Membership",
        "Free Lunch", "Commuter Benefits", "Parental Leave", "Life Insurance"
    ]
    
    def __init__(self, seed: Optional[int] = None):
        """初始化生成器"""
        if seed:
            random.seed(seed)
    
    def generate_job(self, **kwargs) -> TestJobData:
        """生成單個職位數據"""
        job = TestJobData(
            title=kwargs.get('title', random.choice(self.JOB_TITLES)),
            company=kwargs.get('company', random.choice(self.COMPANIES)),
            location=kwargs.get('location', random.choice(self.LOCATIONS)),
            salary_min=kwargs.get('salary_min', random.randint(50000, 120000)),
            salary_max=kwargs.get('salary_max', random.randint(120000, 200000)),
            job_type=kwargs.get('job_type', random.choice(list(JobType))),
            level=kwargs.get('level', random.choice(list(JobLevel))),
            platform=kwargs.get('platform', random.choice(list(Platform))),
            remote=kwargs.get('remote', random.choice([True, False])),
            visa_sponsor=kwargs.get('visa_sponsor', random.choice([True, False]))
        )
        
        # 生成描述
        job.description = self._generate_job_description(job.title, job.company)
        
        # 生成技能要求
        job.skills = random.sample(self.SKILLS, random.randint(3, 8))
        
        # 生成要求
        job.requirements = self._generate_requirements(job.level)
        
        # 生成福利
        job.benefits = random.sample(self.BENEFITS, random.randint(3, 6))
        
        # 生成URL
        job.url = f"https://{job.platform.value}.com/job/{job.id}"
        
        # 生成日期
        job.posted_date = datetime.now() - timedelta(days=random.randint(0, 30))
        job.expires_date = job.posted_date + timedelta(days=random.randint(30, 90))
        
        return job
    
    def generate_jobs(self, count: int, **kwargs) -> List[TestJobData]:
        """生成多個職位數據"""
        return [self.generate_job(**kwargs) for _ in range(count)]
    
    def generate_company(self, **kwargs) -> TestCompanyData:
        """生成公司數據"""
        company = TestCompanyData(
            name=kwargs.get('name', random.choice(self.COMPANIES)),
            industry=kwargs.get('industry', random.choice(self.INDUSTRIES)),
            size=kwargs.get('size', random.choice(self.COMPANY_SIZES)),
            location=kwargs.get('location', random.choice(self.LOCATIONS)),
            rating=kwargs.get('rating', round(random.uniform(3.0, 5.0), 1)),
            review_count=kwargs.get('review_count', random.randint(10, 1000))
        )
        
        # 生成網站
        company.website = f"https://www.{company.name.lower().replace(' ', '')}.com"
        
        # 生成描述
        company.description = self._generate_company_description(company.name, company.industry)
        
        return company
    
    def generate_companies(self, count: int, **kwargs) -> List[TestCompanyData]:
        """生成多個公司數據"""
        return [self.generate_company(**kwargs) for _ in range(count)]
    
    def generate_user(self, **kwargs) -> TestUserData:
        """生成用戶數據"""
        username = kwargs.get('username', self._generate_username())
        user = TestUserData(
            username=username,
            email=kwargs.get('email', f"{username}@example.com"),
            preferences=kwargs.get('preferences', self._generate_user_preferences()),
            search_history=kwargs.get('search_history', self._generate_search_history()),
            saved_jobs=kwargs.get('saved_jobs', [])
        )
        
        return user
    
    def generate_users(self, count: int, **kwargs) -> List[TestUserData]:
        """生成多個用戶數據"""
        return [self.generate_user(**kwargs) for _ in range(count)]
    
    def generate_search_query(self) -> Dict[str, Any]:
        """生成搜索查詢"""
        return {
            "keywords": random.choice(self.JOB_TITLES),
            "location": random.choice(self.LOCATIONS),
            "job_type": random.choice(list(JobType)).value,
            "level": random.choice(list(JobLevel)).value,
            "remote": random.choice([True, False, None]),
            "salary_min": random.choice([None, 50000, 70000, 100000]),
            "salary_max": random.choice([None, 120000, 150000, 200000])
        }
    
    def generate_api_response(self, jobs: List[TestJobData]) -> Dict[str, Any]:
        """生成API響應數據"""
        return {
            "status": "success",
            "total": len(jobs),
            "page": 1,
            "per_page": len(jobs),
            "jobs": [job.to_dict() for job in jobs],
            "timestamp": datetime.now().isoformat(),
            "query_time": round(random.uniform(0.1, 2.0), 3)
        }
    
    def generate_error_response(self, error_type: str = "validation") -> Dict[str, Any]:
        """生成錯誤響應數據"""
        error_messages = {
            "validation": "Invalid search parameters",
            "rate_limit": "Rate limit exceeded",
            "server_error": "Internal server error",
            "not_found": "No jobs found",
            "timeout": "Request timeout"
        }
        
        return {
            "status": "error",
            "error": {
                "type": error_type,
                "message": error_messages.get(error_type, "Unknown error"),
                "code": random.randint(400, 500)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_job_description(self, title: str, company: str) -> str:
        """生成職位描述"""
        templates = [
            f"We are looking for a talented {title} to join our team at {company}. "
            f"You will be responsible for developing and maintaining high-quality software solutions.",
            f"{company} is seeking an experienced {title} to help build the next generation of our products. "
            f"This role offers exciting opportunities to work with cutting-edge technologies.",
            f"Join {company} as a {title} and make a significant impact on our growing platform. "
            f"We offer a collaborative environment and opportunities for professional growth."
        ]
        return random.choice(templates)
    
    def _generate_company_description(self, name: str, industry: str) -> str:
        """生成公司描述"""
        templates = [
            f"{name} is a leading company in the {industry} industry, "
            f"committed to innovation and excellence.",
            f"Founded with a mission to transform the {industry} sector, "
            f"{name} continues to push boundaries and deliver exceptional results.",
            f"{name} specializes in {industry} solutions and has been "
            f"serving customers worldwide for many years."
        ]
        return random.choice(templates)
    
    def _generate_requirements(self, level: JobLevel) -> List[str]:
        """生成職位要求"""
        base_requirements = [
            "Bachelor's degree in Computer Science or related field",
            "Strong problem-solving skills",
            "Excellent communication skills",
            "Team collaboration experience"
        ]
        
        level_requirements = {
            JobLevel.ENTRY: ["0-2 years of experience", "Eagerness to learn"],
            JobLevel.MID: ["3-5 years of experience", "Proven track record"],
            JobLevel.SENIOR: ["5+ years of experience", "Leadership experience"],
            JobLevel.LEAD: ["7+ years of experience", "Team leadership"],
            JobLevel.MANAGER: ["8+ years of experience", "Management experience"],
            JobLevel.DIRECTOR: ["10+ years of experience", "Strategic thinking"],
            JobLevel.EXECUTIVE: ["15+ years of experience", "Executive leadership"]
        }
        
        requirements = base_requirements.copy()
        requirements.extend(level_requirements.get(level, []))
        
        return requirements
    
    def _generate_username(self) -> str:
        """生成用戶名"""
        adjectives = ["cool", "smart", "fast", "bright", "clever", "quick", "sharp"]
        nouns = ["coder", "dev", "engineer", "programmer", "builder", "maker", "creator"]
        
        return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(100, 999)}"
    
    def _generate_user_preferences(self) -> Dict[str, Any]:
        """生成用戶偏好"""
        return {
            "preferred_locations": random.sample(self.LOCATIONS, random.randint(1, 3)),
            "preferred_job_types": [random.choice(list(JobType)).value],
            "preferred_levels": [random.choice(list(JobLevel)).value],
            "salary_expectation": {
                "min": random.randint(60000, 100000),
                "max": random.randint(120000, 180000)
            },
            "remote_preference": random.choice(["required", "preferred", "no_preference"]),
            "skills": random.sample(self.SKILLS, random.randint(5, 10))
        }
    
    def _generate_search_history(self) -> List[str]:
        """生成搜索歷史"""
        return [random.choice(self.JOB_TITLES) for _ in range(random.randint(3, 10))]
    
    def save_to_file(self, data: Any, filename: str) -> None:
        """保存數據到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            if isinstance(data, list):
                json.dump([item.to_dict() if hasattr(item, 'to_dict') else item for item in data], f, indent=2, ensure_ascii=False)
            else:
                json.dump(data.to_dict() if hasattr(data, 'to_dict') else data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str) -> Any:
        """從文件加載數據"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

# 便捷函數
def create_test_jobs(count: int = 10, **kwargs) -> List[TestJobData]:
    """創建測試職位數據"""
    generator = TestDataGenerator()
    return generator.generate_jobs(count, **kwargs)

def create_test_companies(count: int = 5, **kwargs) -> List[TestCompanyData]:
    """創建測試公司數據"""
    generator = TestDataGenerator()
    return generator.generate_companies(count, **kwargs)

def create_test_users(count: int = 3, **kwargs) -> List[TestUserData]:
    """創建測試用戶數據"""
    generator = TestDataGenerator()
    return generator.generate_users(count, **kwargs)

def create_mock_api_response(job_count: int = 10) -> Dict[str, Any]:
    """創建模擬API響應"""
    generator = TestDataGenerator()
    jobs = generator.generate_jobs(job_count)
    return generator.generate_api_response(jobs)

if __name__ == "__main__":
    # 示例用法
    generator = TestDataGenerator(seed=42)
    
    # 生成測試數據
    jobs = generator.generate_jobs(5)
    companies = generator.generate_companies(3)
    users = generator.generate_users(2)
    
    print(f"生成了 {len(jobs)} 個職位")
    print(f"生成了 {len(companies)} 個公司")
    print(f"生成了 {len(users)} 個用戶")
    
    # 保存到文件
    generator.save_to_file(jobs, "test_jobs.json")
    generator.save_to_file(companies, "test_companies.json")
    generator.save_to_file(users, "test_users.json")
    
    print("測試數據已保存到文件")