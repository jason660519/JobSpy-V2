"""提示詞管理器

管理和生成針對不同平台和分析類型的優化提示詞。
"""

from typing import Dict, Optional, Any
import structlog

logger = structlog.get_logger(__name__)


class PromptManager:
    """提示詞管理器
    
    為不同的視覺分析任務生成優化的提示詞。
    """
    
    def __init__(self):
        self.logger = logger.bind(component="prompt_manager")
        
        # 基礎提示詞模板
        self.base_prompts = {
            "job_listing": self._get_job_listing_prompt(),
            "job_details": self._get_job_details_prompt(),
            "search_results": self._get_search_results_prompt()
        }
        
        # 平台特定的提示詞增強
        self.platform_enhancements = {
            "indeed": self._get_indeed_enhancements(),
            "linkedin": self._get_linkedin_enhancements(),
            "glassdoor": self._get_glassdoor_enhancements(),
            "generic": self._get_generic_enhancements()
        }
    
    async def generate_prompt(self, analysis_type: str, platform: str, 
                            search_query: Optional[str] = None,
                            additional_context: Optional[Dict[str, Any]] = None) -> str:
        """生成針對特定任務的提示詞
        
        Args:
            analysis_type: 分析類型 ('job_listing', 'job_details', 'search_results')
            platform: 平台名稱 ('indeed', 'linkedin', 'glassdoor')
            search_query: 搜索查詢（可選）
            additional_context: 額外上下文信息（可選）
            
        Returns:
            str: 生成的提示詞
        """
        try:
            # 獲取基礎提示詞
            base_prompt = self.base_prompts.get(analysis_type, self.base_prompts["job_listing"])
            
            # 獲取平台特定增強
            platform_key = platform.lower() if platform.lower() in self.platform_enhancements else "generic"
            platform_enhancement = self.platform_enhancements[platform_key]
            
            # 構建完整提示詞
            prompt_parts = [
                base_prompt,
                platform_enhancement,
                self._get_output_format_instructions(),
            ]
            
            # 添加搜索查詢上下文
            if search_query:
                prompt_parts.append(f"\n搜索查詢: {search_query}")
            
            # 添加額外上下文
            if additional_context:
                context_str = self._format_additional_context(additional_context)
                if context_str:
                    prompt_parts.append(context_str)
            
            # 添加質量要求
            prompt_parts.append(self._get_quality_requirements())
            
            final_prompt = "\n\n".join(prompt_parts)
            
            self.logger.debug(
                "提示詞生成完成",
                analysis_type=analysis_type,
                platform=platform,
                prompt_length=len(final_prompt)
            )
            
            return final_prompt
            
        except Exception as e:
            self.logger.error("提示詞生成失敗", error=str(e))
            return self.base_prompts["job_listing"]  # 返回默認提示詞
    
    def _get_job_listing_prompt(self) -> str:
        """獲取職位列表分析提示詞"""
        return """
你是一個專業的職位信息提取專家。請仔細分析這張職位列表頁面的截圖，提取所有可見的職位信息。

請識別並提取以下信息：
1. 職位標題 (title)
2. 公司名稱 (company)
3. 工作地點 (location)
4. 薪資信息 (salary) - 如果可見
5. 職位描述或摘要 (description)
6. 職位鏈接 (url) - 如果可見
7. 發布日期 (posted_date) - 如果可見
8. 就業類型 (employment_type) - 全職/兼職/合同等

注意事項：
- 仔細識別每個獨立的職位條目
- 確保信息準確，不要編造不存在的信息
- 如果某些信息不可見或不清楚，請留空
- 保持原始文本的準確性，不要過度解釋
"""
    
    def _get_job_details_prompt(self) -> str:
        """獲取職位詳情分析提示詞"""
        return """
你是一個專業的職位詳情分析專家。請仔細分析這張職位詳情頁面的截圖，提取完整的職位信息。

請識別並提取以下詳細信息：
1. 職位標題 (title)
2. 公司名稱 (company)
3. 工作地點 (location)
4. 完整職位描述 (description)
5. 薪資範圍 (salary_min, salary_max, salary_currency)
6. 就業類型 (employment_type)
7. 經驗要求 (experience_level)
8. 技能要求 (skills) - 以數組形式
9. 職位要求 (requirements) - 以數組形式
10. 福利待遇 (benefits) - 以數組形式
11. 發布日期 (posted_date)
12. 申請截止日期 (application_deadline) - 如果有

特別注意：
- 職位描述應該完整且結構化
- 技能要求應該分別列出
- 薪資信息要準確識別數字和貨幣
- 日期格式要標準化
"""
    
    def _get_search_results_prompt(self) -> str:
        """獲取搜索結果分析提示詞"""
        return """
你是一個專業的搜索結果分析專家。請分析這張搜索結果頁面的截圖，提取所有相關的職位信息。

請識別並提取：
1. 搜索結果總數 (total_results) - 如果顯示
2. 當前頁面的職位列表
3. 每個職位的基本信息（標題、公司、地點、薪資等）
4. 分頁信息 (current_page, total_pages) - 如果可見
5. 篩選器狀態 (active_filters) - 如果可見
6. 排序方式 (sort_order) - 如果可見

搜索結果分析要點：
- 區分付費廣告和自然搜索結果
- 識別推薦職位和相關職位
- 注意職位的相關性評分（如果有）
- 提取可見的職位預覽信息
"""
    
    def _get_indeed_enhancements(self) -> str:
        """Indeed平台特定增強"""
        return """
針對Indeed平台的特殊識別要點：
- 注意Indeed的職位卡片布局
- 識別"Easily apply"標籤
- 區分直接雇主發布和招聘機構發布
- 注意薪資估算和實際薪資的區別
- 識別公司評分和評論數量
- 注意"Sponsored"標記的付費職位
- 提取職位的緊急程度標記
"""
    
    def _get_linkedin_enhancements(self) -> str:
        """LinkedIn平台特定增強"""
        return """
針對LinkedIn平台的特殊識別要點：
- 注意LinkedIn的職位卡片設計
- 識別"Easy Apply"按鈕
- 提取發布者信息（HR或招聘經理）
- 注意職位的申請人數統計
- 識別"Promoted"標記的推廣職位
- 提取公司關注者數量
- 注意職位的匹配度評分
- 識別遠程工作標記
"""
    
    def _get_glassdoor_enhancements(self) -> str:
        """Glassdoor平台特定增強"""
        return """
針對Glassdoor平台的特殊識別要點：
- 注意Glassdoor的職位展示格式
- 提取公司評分和評論
- 識別薪資透明度信息
- 注意面試難度評級
- 提取員工推薦率
- 識別公司文化評分
- 注意CEO支持率
- 提取工作生活平衡評分
"""
    
    def _get_generic_enhancements(self) -> str:
        """通用平台增強"""
        return """
通用職位網站識別要點：
- 仔細識別頁面布局和結構
- 注意職位信息的組織方式
- 識別可點擊的鏈接和按鈕
- 提取所有可見的元數據
- 注意廣告和實際職位的區別
- 識別分頁和導航元素
"""
    
    def _get_output_format_instructions(self) -> str:
        """獲取輸出格式說明"""
        return """
輸出格式要求：
請以JSON格式返回結果，結構如下：

```json
{
  "confidence": 0.95,
  "jobs": [
    {
      "title": "職位標題",
      "company": "公司名稱",
      "location": "工作地點",
      "description": "職位描述",
      "salary": "薪資信息",
      "salary_min": 50000,
      "salary_max": 80000,
      "salary_currency": "USD",
      "employment_type": "full-time",
      "experience_level": "mid",
      "skills": ["Python", "JavaScript", "React"],
      "requirements": ["學士學位", "3年經驗"],
      "benefits": ["健康保險", "彈性工作時間"],
      "url": "職位鏈接",
      "posted_date": "2024-01-15",
      "application_deadline": "2024-02-15"
    }
  ],
  "metadata": {
    "total_results": 150,
    "current_page": 1,
    "total_pages": 15,
    "platform": "indeed"
  }
}
```

重要提醒：
- 只返回JSON格式，不要添加其他文字說明
- 確保JSON格式正確，可以被解析
- 如果某個字段沒有信息，使用null或空字符串
- confidence值應該反映你對提取結果的信心程度（0-1之間）
"""
    
    def _get_quality_requirements(self) -> str:
        """獲取質量要求"""
        return """
質量要求：
1. 準確性：確保提取的信息與截圖中顯示的完全一致
2. 完整性：盡可能提取所有可見的相關信息
3. 一致性：使用統一的格式和命名規範
4. 可靠性：對不確定的信息標記較低的置信度
5. 結構化：按照指定的JSON格式組織數據

特殊情況處理：
- 如果圖片模糊或不清楚，降低confidence值
- 如果沒有找到任何職位信息，返回空的jobs數組
- 如果頁面是錯誤頁面或加載失敗，在metadata中說明
- 對於部分可見的信息，只提取確定的部分
"""
    
    def _format_additional_context(self, context: Dict[str, Any]) -> str:
        """格式化額外上下文信息"""
        if not context:
            return ""
        
        context_parts = ["\n額外上下文信息："]
        
        for key, value in context.items():
            if value:
                context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts) if len(context_parts) > 1 else ""
    
    def get_available_analysis_types(self) -> list:
        """獲取可用的分析類型"""
        return list(self.base_prompts.keys())
    
    def get_supported_platforms(self) -> list:
        """獲取支持的平台"""
        return list(self.platform_enhancements.keys())
    
    def update_prompt_template(self, analysis_type: str, template: str):
        """更新提示詞模板"""
        if analysis_type in self.base_prompts:
            self.base_prompts[analysis_type] = template
            self.logger.info("提示詞模板已更新", analysis_type=analysis_type)
        else:
            self.logger.warning("未知的分析類型", analysis_type=analysis_type)
    
    def add_platform_enhancement(self, platform: str, enhancement: str):
        """添加平台特定增強"""
        self.platform_enhancements[platform.lower()] = enhancement
        self.logger.info("平台增強已添加", platform=platform)