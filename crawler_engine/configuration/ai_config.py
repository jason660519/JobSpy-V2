"""AI 配置模組

定義 AI 處理相關的配置參數。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class AIConfig:
    """AI 處理配置"""
    
    # OpenAI 配置
    openai_api_key: str = ""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.1
    
    # 處理配置
    enable_ai_processing: bool = True
    batch_size: int = 5
    max_retries: int = 3
    timeout: int = 30
    
    # 成本控制
    max_cost_per_request: float = 0.1
    daily_cost_limit: float = 10.0
    
    # 提示詞配置
    custom_prompts: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """初始化後處理"""
        if self.custom_prompts is None:
            self.custom_prompts = {}
    
    @property
    def is_enabled(self) -> bool:
        """檢查 AI 功能是否啟用"""
        return self.enable_ai_processing and bool(self.openai_api_key)
    
    def get_openai_config(self) -> Dict[str, Any]:
        """獲取 OpenAI 配置"""
        return {
            "api_key": self.openai_api_key,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout
        }