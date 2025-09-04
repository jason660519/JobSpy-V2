#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 處理器模組

提供使用 AI 模型處理和解析爬取數據的功能。
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from ..config import AIConfig
from .cost_tracker import CostTracker
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class AIProcessor:
    """
    AI 處理器類
    
    使用 OpenAI API 處理和解析爬取的職位數據。
    """
    
    def __init__(self, config: AIConfig):
        """
        初始化 AI 處理器
        
        Args:
            config: AI 配置
        """
        self.config = config
        self.cost_tracker = CostTracker()
        self.prompt_manager = PromptManager()
        
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI 庫未安裝，AI 處理功能將被禁用")
            return
            
        # 設置 OpenAI API
        if config.openai_api_key:
            openai.api_key = config.openai_api_key
            logger.info("OpenAI API 初始化成功")
        else:
            logger.warning("未提供 OpenAI API 密鑰，AI 處理功能將被禁用")
    
    def process_job_data(self, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        處理原始職位數據
        
        Args:
            raw_jobs: 原始職位數據列表
            
        Returns:
            List[Dict[str, Any]]: 處理後的職位數據列表
        """
        if not OPENAI_AVAILABLE or not self.config.openai_api_key:
            logger.warning("AI 處理功能不可用，返回原始數據")
            return self._fallback_processing(raw_jobs)
        
        processed_jobs = []
        
        for i, job in enumerate(raw_jobs):
            try:
                logger.info(f"正在處理職位 {i+1}/{len(raw_jobs)}: {job.get('title', 'Unknown')}")
                
                # 使用 AI 處理單個職位
                processed_job = self._process_single_job(job)
                
                if processed_job:
                    processed_jobs.append(processed_job)
                else:
                    # 如果 AI 處理失敗，使用回退處理
                    fallback_job = self._fallback_process_single_job(job)
                    processed_jobs.append(fallback_job)
                    
            except Exception as e:
                logger.error(f"處理職位時發生錯誤: {str(e)}")
                # 使用回退處理
                fallback_job = self._fallback_process_single_job(job)
                processed_jobs.append(fallback_job)
        
        logger.info(f"AI 處理完成，處理了 {len(processed_jobs)} 個職位")
        return processed_jobs
    
    def _process_single_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        使用 AI 處理單個職位
        
        Args:
            job: 原始職位數據
            
        Returns:
            Optional[Dict[str, Any]]: 處理後的職位數據，失敗時返回 None
        """
        try:
            # 構建提示詞
            prompt = self.prompt_manager.get_job_processing_prompt(job)
            
            # 調用 OpenAI API
            response = openai.ChatCompletion.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的職位數據分析師，負責解析和標準化職位信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # 記錄成本
            self.cost_tracker.track_api_call(
                model=self.config.model_name,
                input_tokens=response['usage']['prompt_tokens'],
                output_tokens=response['usage']['completion_tokens']
            )
            
            # 解析響應
            ai_response = response['choices'][0]['message']['content']
            processed_data = json.loads(ai_response)
            
            # 添加處理元數據
            processed_data['ai_processed'] = True
            processed_data['processed_at'] = datetime.now().isoformat()
            processed_data['model_used'] = self.config.model_name
            
            return processed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"AI 響應 JSON 解析失敗: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"AI 處理失敗: {str(e)}")
            return None
    
    async def process_text(self, text: str, prompt: str) -> Dict[str, Any]:
        """
        處理文本數據
        
        Args:
            text: 要處理的文本
            prompt: AI 提示詞
            
        Returns:
            Dict[str, Any]: AI 處理結果
        """
        if not OPENAI_AVAILABLE or not self.config.openai_api_key:
            logger.warning("AI 處理功能不可用，返回原始文本")
            return {"original_text": text, "ai_processed": False}
        
        try:
            # 調用 OpenAI API
            response = openai.ChatCompletion.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的數據分析師，負責解析和結構化文本數據。請以 JSON 格式返回結果。"},
                    {"role": "user", "content": f"{prompt}\n\n文本內容：\n{text}"}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # 記錄成本
            self.cost_tracker.track_api_call(
                model=self.config.model_name,
                input_tokens=response['usage']['prompt_tokens'],
                output_tokens=response['usage']['completion_tokens']
            )
            
            # 解析響應
            ai_response = response['choices'][0]['message']['content']
            
            try:
                processed_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # 如果不是有效的 JSON，返回原始響應
                processed_data = {"ai_response": ai_response}
            
            # 添加處理元數據
            processed_data['ai_processed'] = True
            processed_data['processed_at'] = datetime.now().isoformat()
            processed_data['model_used'] = self.config.model_name
            
            return processed_data
            
        except Exception as e:
            logger.error(f"AI 文本處理失敗: {str(e)}")
            return {"original_text": text, "ai_processed": False, "error": str(e)}
    
    def _fallback_processing(self, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        回退處理方案（不使用 AI）
        
        Args:
            raw_jobs: 原始職位數據列表
            
        Returns:
            List[Dict[str, Any]]: 處理後的職位數據列表
        """
        logger.info("使用回退處理方案")
        
        processed_jobs = []
        for job in raw_jobs:
            processed_job = self._fallback_process_single_job(job)
            processed_jobs.append(processed_job)
        
        return processed_jobs
    
    def _fallback_process_single_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        回退處理單個職位（不使用 AI）
        
        Args:
            job: 原始職位數據
            
        Returns:
            Dict[str, Any]: 處理後的職位數據
        """
        # 基本數據清理和標準化
        processed_job = {
            'id': job.get('id', ''),
            'title': self._clean_text(job.get('title', '')),
            'company': self._clean_text(job.get('company', '')),
            'location': self._clean_text(job.get('location', '')),
            'description': self._clean_text(job.get('description', '')),
            'salary': self._clean_text(job.get('salary', '')),
            'job_type': self._clean_text(job.get('job_type', '')),
            'posted_date': job.get('posted_date', ''),
            'url': job.get('url', ''),
            
            # 添加處理元數據
            'ai_processed': False,
            'processed_at': datetime.now().isoformat(),
            'processing_method': 'fallback',
            
            # 保留原始數據
            'raw_data': job
        }
        
        return processed_job
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本數據
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理後的文本
        """
        if not isinstance(text, str):
            return str(text) if text is not None else ''
        
        # 移除多餘的空白字符
        text = ' '.join(text.split())
        
        # 移除特殊字符（保留基本標點）
        # 這裡可以根據需要添加更多清理規則
        
        return text.strip()
    
    def extract_skills(self, job_description: str) -> List[str]:
        """
        從職位描述中提取技能
        
        Args:
            job_description: 職位描述
            
        Returns:
            List[str]: 提取的技能列表
        """
        if not OPENAI_AVAILABLE or not self.config.openai_api_key:
            return self._fallback_extract_skills(job_description)
        
        try:
            prompt = self.prompt_manager.get_skill_extraction_prompt(job_description)
            
            response = openai.ChatCompletion.create(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "你是一個專業的技能提取專家，負責從職位描述中識別相關技能。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # 記錄成本
            self.cost_tracker.track_api_call(
                model=self.config.model_name,
                input_tokens=response['usage']['prompt_tokens'],
                output_tokens=response['usage']['completion_tokens']
            )
            
            # 解析技能列表
            skills_text = response['choices'][0]['message']['content']
            skills = json.loads(skills_text)
            
            return skills if isinstance(skills, list) else []
            
        except Exception as e:
            logger.error(f"AI 技能提取失敗: {str(e)}")
            return self._fallback_extract_skills(job_description)
    
    def _fallback_extract_skills(self, job_description: str) -> List[str]:
        """
        回退技能提取方案
        
        Args:
            job_description: 職位描述
            
        Returns:
            List[str]: 提取的技能列表
        """
        # 簡單的關鍵詞匹配
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go',
            'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
            'Git', 'Jenkins', 'CI/CD', 'Agile', 'Scrum'
        ]
        
        found_skills = []
        description_lower = job_description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """
        獲取成本摘要
        
        Returns:
            Dict[str, Any]: 成本摘要
        """
        return self.cost_tracker.get_summary()
    
    def reset_cost_tracking(self):
        """
        重置成本追蹤
        """
        self.cost_tracker.reset()