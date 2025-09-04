#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向後兼容的CSV導出器

支持舊專案格式的CSV導出，確保與舊系統的兼容性。
提供字段映射和格式轉換功能。
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..models.job_data import JobData
from .exporter import ExportConfig, ExportFormat


class LegacyFormat(Enum):
    """舊格式類型枚舉"""
    JOBSPY_V1 = "jobspy_v1"  # 舊JobSpy格式
    CUSTOM_LEGACY = "custom_legacy"  # 自定義舊格式


@dataclass
class LegacyExportConfig:
    """舊格式導出配置"""
    format_type: LegacyFormat = LegacyFormat.JOBSPY_V1
    output_path: Optional[str] = None
    encoding: str = "utf-8"
    delimiter: str = ","
    include_header: bool = True
    date_format: str = "%Y-%m-%d"
    empty_value: str = ""
    
    # 字段映射配置
    custom_field_mapping: Optional[Dict[str, str]] = None
    include_description: bool = True
    max_description_length: int = 1000


class LegacyCSVExporter:
    """向後兼容的CSV導出器
    
    支持多種舊格式的CSV導出，包括：
    - JobSpy v1 格式
    - 自定義舊格式
    """
    
    # JobSpy v1 格式字段映射
    JOBSPY_V1_FIELD_MAPPING = {
        "SITE": "platform",
        "TITLE": "title",
        "COMPANY": "company",
        "CITY": "city",
        "STATE": "state",
        "JOB_TYPE": "job_type",
        "INTERVAL": "salary_type",
        "MIN_AMOUNT": "salary_min",
        "MAX_AMOUNT": "salary_max",
        "JOB_URL": "url",
        "DESCRIPTION": "description"
    }
    
    # JobSpy v1 字段順序
    JOBSPY_V1_FIELD_ORDER = [
        "SITE", "TITLE", "COMPANY", "CITY", "STATE", 
        "JOB_TYPE", "INTERVAL", "MIN_AMOUNT", "MAX_AMOUNT", 
        "JOB_URL", "DESCRIPTION"
    ]
    
    def __init__(self, config: LegacyExportConfig):
        """初始化舊格式CSV導出器
        
        Args:
            config: 舊格式導出配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 根據格式類型設置字段映射
        if config.format_type == LegacyFormat.JOBSPY_V1:
            self.field_mapping = self.JOBSPY_V1_FIELD_MAPPING
            self.field_order = self.JOBSPY_V1_FIELD_ORDER
        elif config.format_type == LegacyFormat.CUSTOM_LEGACY:
            self.field_mapping = config.custom_field_mapping or {}
            self.field_order = list(self.field_mapping.keys())
        else:
            raise ValueError(f"不支持的舊格式類型: {config.format_type}")
    
    def export_jobs(self, jobs: List[Union[JobData, Dict[str, Any]]], output_path: Optional[str] = None) -> str:
        """導出職位數據為舊格式CSV
        
        Args:
            jobs: 職位數據列表
            output_path: 輸出文件路徑，如果為None則使用配置中的路徑
            
        Returns:
            str: 導出文件路徑
        """
        if not jobs:
            self.logger.warning("沒有職位數據可導出")
            return ""
        
        # 確定輸出路徑
        if output_path is None:
            if self.config.output_path:
                output_path = self.config.output_path
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"legacy_jobs_export_{timestamp}.csv"
        
        # 確保輸出目錄存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_file, 'w', newline='', encoding=self.config.encoding) as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=self.field_order,
                    delimiter=self.config.delimiter,
                    quoting=csv.QUOTE_MINIMAL
                )
                
                # 寫入標題行
                if self.config.include_header:
                    writer.writeheader()
                
                # 轉換並寫入數據
                for job in jobs:
                    legacy_row = self._convert_to_legacy_format(job)
                    writer.writerow(legacy_row)
            
            self.logger.info(f"成功導出 {len(jobs)} 條職位數據到舊格式CSV: {output_file}")
            return str(output_file)
            
        except Exception as e:
            self.logger.error(f"導出舊格式CSV失敗: {e}")
            raise
    
    def _convert_to_legacy_format(self, job: Union[JobData, Dict[str, Any]]) -> Dict[str, str]:
        """將職位數據轉換為舊格式
        
        Args:
            job: 職位數據（JobData對象或字典）
            
        Returns:
            Dict[str, str]: 舊格式的職位數據
        """
        # 如果是JobData對象，轉換為字典
        if isinstance(job, JobData):
            job_dict = self._jobdata_to_dict(job)
        else:
            job_dict = job
        
        legacy_row = {}
        
        for legacy_field, modern_field in self.field_mapping.items():
            value = self._extract_field_value(job_dict, modern_field)
            legacy_row[legacy_field] = self._format_field_value(legacy_field, value)
        
        return legacy_row
    
    def _jobdata_to_dict(self, job_data: JobData) -> Dict[str, Any]:
        """將JobData對象轉換為字典
        
        Args:
            job_data: JobData對象
            
        Returns:
            Dict[str, Any]: 職位數據字典
        """
        job_dict = {
            "platform": "seek",  # 默認平台
            "title": job_data.title,
            "company": job_data.company,
            "location": job_data.location,
            "url": job_data.url,
            "description": job_data.description,
            "job_type": job_data.job_type.value if job_data.job_type else "",
            "salary_min": job_data.salary_min or 0,
            "salary_max": job_data.salary_max or 0,
            "salary_type": job_data.salary_type.value if job_data.salary_type else "yearly",
            "posted_date": job_data.posted_date.strftime(self.config.date_format) if job_data.posted_date else ""
        }
        
        # 解析地理位置
        if job_data.location:
            city, state = self._parse_location(job_data.location)
            job_dict["city"] = city
            job_dict["state"] = state
        else:
            job_dict["city"] = ""
            job_dict["state"] = ""
        
        return job_dict
    
    def _extract_field_value(self, job_dict: Dict[str, Any], field_path: str) -> Any:
        """從職位數據字典中提取字段值
        
        Args:
            job_dict: 職位數據字典
            field_path: 字段路徑（支持點號分隔的嵌套路徑）
            
        Returns:
            Any: 字段值
        """
        if '.' in field_path:
            # 處理嵌套字段
            keys = field_path.split('.')
            value = job_dict
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return self.config.empty_value
            return value
        else:
            return job_dict.get(field_path, self.config.empty_value)
    
    def _format_field_value(self, field_name: str, value: Any) -> str:
        """格式化字段值
        
        Args:
            field_name: 字段名稱
            value: 原始值
            
        Returns:
            str: 格式化後的字符串值
        """
        if value is None or value == "":
            return self.config.empty_value
        
        # 特殊字段處理
        if field_name == "DESCRIPTION" and self.config.include_description:
            # 限制描述長度並清理格式
            description = str(value).replace('\n', ' ').replace('\r', ' ')
            if len(description) > self.config.max_description_length:
                description = description[:self.config.max_description_length] + "..."
            return description
        elif field_name in ["MIN_AMOUNT", "MAX_AMOUNT"]:
            # 處理薪資數值
            try:
                return str(int(float(value))) if value else "0"
            except (ValueError, TypeError):
                return "0"
        else:
            return str(value)
    
    def _parse_location(self, location: str) -> tuple[str, str]:
        """解析地理位置字符串
        
        Args:
            location: 地理位置字符串
            
        Returns:
            tuple[str, str]: (城市, 州/省)
        """
        if not location:
            return "", ""
        
        # 常見的地理位置格式處理
        location = location.strip()
        
        # 格式: "City, State" 或 "City, Country"
        if ',' in location:
            parts = [part.strip() for part in location.split(',')]
            if len(parts) >= 2:
                return parts[0], parts[1]
            else:
                return parts[0], ""
        
        # 格式: "City State" (空格分隔)
        parts = location.split()
        if len(parts) >= 2:
            # 假設最後一個詞是州/省
            city = ' '.join(parts[:-1])
            state = parts[-1]
            return city, state
        
        # 只有城市名稱
        return location, ""
    
    def get_field_mapping(self) -> Dict[str, str]:
        """獲取當前的字段映射
        
        Returns:
            Dict[str, str]: 字段映射字典
        """
        return self.field_mapping.copy()
    
    def get_supported_fields(self) -> List[str]:
        """獲取支持的舊格式字段列表
        
        Returns:
            List[str]: 字段名稱列表
        """
        return self.field_order.copy()


def create_legacy_exporter(format_type: LegacyFormat = LegacyFormat.JOBSPY_V1, 
                          output_path: Optional[str] = None,
                          **kwargs) -> LegacyCSVExporter:
    """創建舊格式CSV導出器的便捷函數
    
    Args:
        format_type: 舊格式類型
        output_path: 輸出文件路徑
        **kwargs: 其他配置參數
        
    Returns:
        LegacyCSVExporter: 舊格式CSV導出器實例
    """
    config = LegacyExportConfig(
        format_type=format_type,
        output_path=output_path,
        **kwargs
    )
    return LegacyCSVExporter(config)


# 便捷函數
def export_to_legacy_csv(jobs: List[Union[JobData, Dict[str, Any]]], 
                         output_path: str,
                         format_type: LegacyFormat = LegacyFormat.JOBSPY_V1) -> str:
    """快速導出職位數據為舊格式CSV
    
    Args:
        jobs: 職位數據列表
        output_path: 輸出文件路徑
        format_type: 舊格式類型
        
    Returns:
        str: 導出文件路徑
    """
    exporter = create_legacy_exporter(format_type, output_path)
    return exporter.export_jobs(jobs, output_path)