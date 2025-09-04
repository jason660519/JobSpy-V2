"""爬蟲引擎配置管理

統一管理所有爬蟲相關的配置參數，包括AI服務、代理設置、平台配置等。
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ProcessingStrategy(Enum):
    """數據處理策略"""
    API_FIRST = "api_first"  # 優先使用官方API
    SCRAPING_FIRST = "scraping_first"  # 優先使用爬蟲
    AI_VISION_ONLY = "ai_vision_only"  # 僅使用AI視覺
    HYBRID = "hybrid"  # 混合策略


class CostTier(Enum):
    """成本控制等級"""
    FREE = "free"  # 免費模式
    BASIC = "basic"  # 基礎模式
    PREMIUM = "premium"  # 高級模式
    UNLIMITED = "unlimited"  # 無限制模式


@dataclass
class AIConfig:
    """AI服務配置"""
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = "gpt-4-vision-preview"
    max_tokens: int = 1000
    temperature: float = 0.1
    
    # 本地VLM配置
    use_local_vlm: bool = False
    local_model_path: str = ""
    
    # 成本控制
    daily_budget_usd: float = 50.0
    cost_per_request: float = 0.01
    max_requests_per_hour: int = 100


@dataclass
class ScrapingConfig:
    """爬蟲配置"""
    # 瀏覽器設置
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # 反檢測設置
    enable_stealth: bool = True
    random_delays: bool = True
    min_delay_ms: int = 1000
    max_delay_ms: int = 3000
    
    # 代理設置
    use_proxy: bool = False
    proxy_list: List[str] = field(default_factory=list)
    rotate_proxy: bool = True
    
    # 重試設置
    max_retries: int = 3
    retry_delay_ms: int = 5000
    timeout_ms: int = 30000


@dataclass
class PlatformConfig:
    """平台特定配置"""
    name: str
    base_url: str
    search_endpoint: str
    rate_limit_per_minute: int = 60
    requires_auth: bool = False
    auth_config: Dict = field(default_factory=dict)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # 平台特定的選擇器
    selectors: Dict[str, str] = field(default_factory=dict)
    
    # AI視覺分析提示
    ai_prompts: Dict[str, str] = field(default_factory=dict)


@dataclass
class StorageConfig:
    """存儲配置"""
    # 數據庫配置
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    
    # MinIO配置
    minio_endpoint: str = field(default_factory=lambda: os.getenv("MINIO_ENDPOINT", "localhost:9000"))
    minio_access_key: str = field(default_factory=lambda: os.getenv("MINIO_ACCESS_KEY", "minioadmin"))
    minio_secret_key: str = field(default_factory=lambda: os.getenv("MINIO_SECRET_KEY", "minioadmin"))
    minio_bucket: str = "crawler-data"
    
    # Redis配置
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    cache_ttl_seconds: int = 3600


@dataclass
class CrawlerConfig:
    """爬蟲引擎主配置"""
    # 基本設置
    processing_strategy: ProcessingStrategy = ProcessingStrategy.HYBRID
    cost_tier: CostTier = CostTier.BASIC
    max_concurrent_jobs: int = 5
    
    # 子配置
    ai: AIConfig = field(default_factory=AIConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # 平台配置
    platforms: Dict[str, PlatformConfig] = field(default_factory=dict)
    
    # 監控配置
    enable_monitoring: bool = True
    log_level: str = "INFO"
    metrics_endpoint: str = "/metrics"
    
    def __post_init__(self):
        """初始化後處理"""
        if not self.platforms:
            self._init_default_platforms()
    
    def _init_default_platforms(self):
        """初始化默認平台配置"""
        self.platforms = {
            "indeed": PlatformConfig(
                name="Indeed",
                base_url="https://www.indeed.com",
                search_endpoint="/jobs",
                rate_limit_per_minute=30,
                selectors={
                    "job_cards": "[data-result-id]",
                    "title": "h2 a span",
                    "company": "[data-testid='company-name']",
                    "location": "[data-testid='job-location']",
                    "salary": "[data-testid='attribute_snippet_testid']",
                    "description": "[data-testid='job-snippet']"
                },
                ai_prompts={
                    "extract_jobs": "請從這個Indeed求職頁面截圖中提取所有職位信息，包括職位名稱、公司名稱、地點、薪資和描述。"
                }
            ),
            "linkedin": PlatformConfig(
                name="LinkedIn",
                base_url="https://www.linkedin.com",
                search_endpoint="/jobs/search",
                rate_limit_per_minute=20,
                requires_auth=True,
                selectors={
                    "job_cards": ".job-search-card",
                    "title": ".base-search-card__title",
                    "company": ".base-search-card__subtitle",
                    "location": ".job-search-card__location",
                    "description": ".job-search-card__snippet"
                },
                ai_prompts={
                    "extract_jobs": "請從這個LinkedIn求職頁面截圖中提取所有職位信息，注意LinkedIn的特殊佈局格式。"
                }
            ),
            "glassdoor": PlatformConfig(
                name="Glassdoor",
                base_url="https://www.glassdoor.com",
                search_endpoint="/Job/jobs.htm",
                rate_limit_per_minute=25,
                selectors={
                    "job_cards": "[data-test='jobListing']",
                    "title": "[data-test='job-title']",
                    "company": "[data-test='employer-name']",
                    "location": "[data-test='job-location']",
                    "salary": "[data-test='detailSalary']"
                },
                ai_prompts={
                    "extract_jobs": "請從這個Glassdoor求職頁面截圖中提取所有職位信息，包括薪資範圍和公司評分。"
                }
            )
        }
    
    @classmethod
    def from_env(cls) -> 'CrawlerConfig':
        """從環境變量創建配置"""
        config = cls()
        
        # 從環境變量覆蓋配置
        if os.getenv("CRAWLER_HEADLESS"):
            config.scraping.headless = os.getenv("CRAWLER_HEADLESS").lower() == "true"
        
        if os.getenv("CRAWLER_MAX_CONCURRENT"):
            config.max_concurrent_jobs = int(os.getenv("CRAWLER_MAX_CONCURRENT"))
        
        if os.getenv("AI_DAILY_BUDGET"):
            config.ai.daily_budget_usd = float(os.getenv("AI_DAILY_BUDGET"))
        
        return config
    
    def validate(self) -> bool:
        """驗證配置有效性"""
        if not self.ai.openai_api_key and not self.ai.use_local_vlm:
            raise ValueError("必須提供OpenAI API密鑰或啟用本地VLM")
        
        if not self.storage.database_url:
            raise ValueError("必須提供數據庫連接URL")
        
        if self.max_concurrent_jobs <= 0:
            raise ValueError("並發任務數必須大於0")
        
        return True


# 全局配置實例
config = CrawlerConfig.from_env()