"""Seek 平台專用配置

定義 Seek 平台的所有配置參數，包括選擇器、URL 模式、ETL 設定等。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..base import PlatformConfig


@dataclass
class SeekConfig:
    """Seek 平台專用配置"""
    
    # 基本配置
    base_url: str = "https://www.seek.com.au"
    search_url: str = "https://www.seek.com.au/jobs"
    job_detail_url_pattern: str = "https://www.seek.com.au/job/{job_id}"
    
    # 搜索參數
    default_location: str = "Sydney"
    default_keywords: str = "software engineer"
    max_pages: int = 5
    jobs_per_page: int = 20
    
    # CSS 選擇器 (2025年版本)
    selectors: Dict[str, str] = field(default_factory=lambda: {
        # 職位卡片
        "job_cards": "[data-automation='normalJob']",
        "job_link": "[data-automation='jobTitle'] a",
        
        # 基本信息
        "title": "[data-automation='jobTitle'] a span",
        "company": "[data-automation='jobCompany'] a span",
        "location": "[data-automation='jobLocation'] span",
        "salary": "[data-automation='jobSalary'] span",
        "work_type": "[data-automation='jobWorkType'] span",
        "classification": "[data-automation='jobClassification'] span",
        "sub_classification": "[data-automation='jobSubClassification'] span",
        
        # 詳細頁面選擇器
        "job_description": "[data-automation='jobAdDetails']",
        "job_summary": "[data-automation='jobSummary']",
        "company_profile": "[data-automation='companyProfile']",
        "job_details_section": "[data-automation='jobDetails']",
        
        # 分頁
        "pagination": "[data-automation='page-number']",
        "next_page": "[data-automation='page-next']",
        "total_jobs": "[data-automation='totalJobsCount']",
        
        # 篩選器
        "location_filter": "[data-automation='whereField']",
        "keyword_filter": "[data-automation='whatField']",
        "search_button": "[data-automation='searchButton']"
    })
    
    # 請求配置
    request_delay: float = 2.0
    max_retries: int = 3
    timeout: int = 30
    
    # ETL 配置
    etl_config: Dict[str, any] = field(default_factory=lambda: {
        "batch_size": 10,
        "enable_ai_processing": True,
        "enable_data_cleaning": True,
        "enable_deduplication": True,
        "storage_buckets": {
            "raw_data": "seek-raw-data",
            "ai_processed": "seek-ai-processed",
            "cleaned_data": "seek-cleaned-data",
            "final_data": "seek-final-data"
        }
    })
    
    # AI 提示詞
    ai_prompts: Dict[str, str] = field(default_factory=lambda: {
        "job_extraction": """
        請從這個 Seek 職位頁面中提取以下信息：
        1. 職位標題
        2. 公司名稱
        3. 工作地點
        4. 薪資範圍
        5. 工作類型（全職/兼職/合約）
        6. 經驗要求
        7. 技能要求
        8. 工作描述
        9. 公司描述
        10. 申請截止日期
        
        請以 JSON 格式返回結果。
        """,
        
        "skill_extraction": """
        請從職位描述中提取技能要求，包括：
        1. 程式語言
        2. 框架和工具
        3. 軟技能
        4. 認證要求
        5. 經驗年數
        
        請以結構化的 JSON 格式返回。
        """,
        
        "salary_parsing": """
        請解析薪資信息，提取：
        1. 最低薪資
        2. 最高薪資
        3. 薪資類型（年薪/時薪/日薪）
        4. 貨幣單位
        5. 是否包含福利
        
        請以 JSON 格式返回。
        """
    })


def create_seek_config() -> PlatformConfig:
    """創建 Seek 平台的默認配置
    
    Returns:
        PlatformConfig: Seek 平台配置
    """
    seek_config = SeekConfig()
    
    return PlatformConfig(
        name="seek",
        base_url=seek_config.base_url,
        search_url=seek_config.search_url,
        job_detail_url_pattern=seek_config.job_detail_url_pattern,
        selectors=seek_config.selectors,
        search_delay_range=(seek_config.request_delay, seek_config.request_delay + 2),
        retry_attempts=seek_config.max_retries,
        timeout=seek_config.timeout
    )