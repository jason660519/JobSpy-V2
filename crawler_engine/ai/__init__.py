"""AI視覺分析模組

提供基於GPT-4V的智能視覺分析功能，用於解析網頁截圖和提取職位信息。
"""

from .vision_service import AIVisionService
from .prompt_manager import PromptManager
from .cost_tracker import CostTracker

__all__ = [
    'AIVisionService',
    'PromptManager', 
    'CostTracker'
]

__version__ = '1.0.0'