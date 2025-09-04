#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲配置模組
定義爬蟲相關的配置參數
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import os


@dataclass
class ScrapingConfig:
    """爬蟲配置類"""
    
    # 基本配置
    max_workers: int = 5  # 最大並發數
    request_delay: float = 1.0  # 請求間隔（秒）
    timeout: int = 30  # 請求超時時間（秒）
    max_retries: int = 3  # 最大重試次數
    
    # User-Agent 配置
    user_agents: List[str] = None
    rotate_user_agent: bool = True
    
    # 代理配置
    proxies: List[str] = None
    use_proxy: bool = False
    proxy_rotation: bool = True
    
    # 請求頭配置
    default_headers: Dict[str, str] = None
    
    # 爬蟲限制
    max_pages: int = 10  # 最大爬取頁數
    max_jobs_per_page: int = 50  # 每頁最大職位數
    max_total_jobs: int = 500  # 最大總職位數
    
    # 錯誤處理
    ignore_ssl_errors: bool = True
    handle_cloudflare: bool = True
    handle_captcha: bool = False
    
    # 緩存配置
    enable_cache: bool = True
    cache_duration: int = 3600  # 緩存持續時間（秒）
    
    # 日誌配置
    log_requests: bool = True
    log_responses: bool = False
    log_errors: bool = True
    
    def __post_init__(self):
        """初始化後處理"""
        if self.user_agents is None:
            self.user_agents = self._get_default_user_agents()
        
        if self.default_headers is None:
            self.default_headers = self._get_default_headers()
        
        if self.proxies is None:
            self.proxies = []
    
    def _get_default_user_agents(self) -> List[str]:
        """獲取默認 User-Agent 列表"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    def _get_default_headers(self) -> Dict[str, str]:
        """獲取默認請求頭"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_random_user_agent(self) -> str:
        """獲取隨機 User-Agent"""
        import random
        return random.choice(self.user_agents)
    
    def get_random_proxy(self) -> Optional[str]:
        """獲取隨機代理"""
        if not self.use_proxy or not self.proxies:
            return None
        
        import random
        return random.choice(self.proxies)
    
    def get_request_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """獲取請求頭"""
        headers = self.default_headers.copy()
        
        if self.rotate_user_agent:
            headers['User-Agent'] = self.get_random_user_agent()
        
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'max_workers': self.max_workers,
            'request_delay': self.request_delay,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'user_agents': self.user_agents,
            'rotate_user_agent': self.rotate_user_agent,
            'proxies': self.proxies,
            'use_proxy': self.use_proxy,
            'proxy_rotation': self.proxy_rotation,
            'default_headers': self.default_headers,
            'max_pages': self.max_pages,
            'max_jobs_per_page': self.max_jobs_per_page,
            'max_total_jobs': self.max_total_jobs,
            'ignore_ssl_errors': self.ignore_ssl_errors,
            'handle_cloudflare': self.handle_cloudflare,
            'handle_captcha': self.handle_captcha,
            'enable_cache': self.enable_cache,
            'cache_duration': self.cache_duration,
            'log_requests': self.log_requests,
            'log_responses': self.log_responses,
            'log_errors': self.log_errors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapingConfig':
        """從字典創建配置"""
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """從環境變量創建配置"""
        return cls(
            max_workers=int(os.getenv('SCRAPING_MAX_WORKERS', '5')),
            request_delay=float(os.getenv('SCRAPING_REQUEST_DELAY', '1.0')),
            timeout=int(os.getenv('SCRAPING_TIMEOUT', '30')),
            max_retries=int(os.getenv('SCRAPING_MAX_RETRIES', '3')),
            rotate_user_agent=os.getenv('SCRAPING_ROTATE_USER_AGENT', 'true').lower() == 'true',
            use_proxy=os.getenv('SCRAPING_USE_PROXY', 'false').lower() == 'true',
            proxy_rotation=os.getenv('SCRAPING_PROXY_ROTATION', 'true').lower() == 'true',
            max_pages=int(os.getenv('SCRAPING_MAX_PAGES', '10')),
            max_jobs_per_page=int(os.getenv('SCRAPING_MAX_JOBS_PER_PAGE', '50')),
            max_total_jobs=int(os.getenv('SCRAPING_MAX_TOTAL_JOBS', '500')),
            ignore_ssl_errors=os.getenv('SCRAPING_IGNORE_SSL_ERRORS', 'true').lower() == 'true',
            handle_cloudflare=os.getenv('SCRAPING_HANDLE_CLOUDFLARE', 'true').lower() == 'true',
            handle_captcha=os.getenv('SCRAPING_HANDLE_CAPTCHA', 'false').lower() == 'true',
            enable_cache=os.getenv('SCRAPING_ENABLE_CACHE', 'true').lower() == 'true',
            cache_duration=int(os.getenv('SCRAPING_CACHE_DURATION', '3600')),
            log_requests=os.getenv('SCRAPING_LOG_REQUESTS', 'true').lower() == 'true',
            log_responses=os.getenv('SCRAPING_LOG_RESPONSES', 'false').lower() == 'true',
            log_errors=os.getenv('SCRAPING_LOG_ERRORS', 'true').lower() == 'true'
        )


# 預定義配置
DEFAULT_SCRAPING_CONFIG = ScrapingConfig()

FAST_SCRAPING_CONFIG = ScrapingConfig(
    max_workers=10,
    request_delay=0.5,
    timeout=15,
    max_retries=2,
    max_pages=5
)

CONSERVATIVE_SCRAPING_CONFIG = ScrapingConfig(
    max_workers=2,
    request_delay=2.0,
    timeout=60,
    max_retries=5,
    max_pages=20
)

PRODUCTION_SCRAPING_CONFIG = ScrapingConfig(
    max_workers=8,
    request_delay=1.5,
    timeout=45,
    max_retries=4,
    max_pages=15,
    use_proxy=True,
    handle_cloudflare=True,
    enable_cache=True
)


def get_scraping_config(config_name: str = 'default') -> ScrapingConfig:
    """根據名稱獲取爬蟲配置"""
    configs = {
        'default': DEFAULT_SCRAPING_CONFIG,
        'fast': FAST_SCRAPING_CONFIG,
        'conservative': CONSERVATIVE_SCRAPING_CONFIG,
        'production': PRODUCTION_SCRAPING_CONFIG
    }
    
    return configs.get(config_name, DEFAULT_SCRAPING_CONFIG)


def create_custom_scraping_config(**kwargs) -> ScrapingConfig:
    """創建自定義爬蟲配置"""
    base_config = DEFAULT_SCRAPING_CONFIG.to_dict()
    base_config.update(kwargs)
    return ScrapingConfig.from_dict(base_config)