"""數據導出模組

提供各種格式的數據導出功能
"""

import csv
import json
import pandas as pd
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import logging

from .models import CleanedJobData, ProcessedJobData, ProcessedCompanyData


class ExportFormat(Enum):
    """導出格式枚舉"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PARQUET = "parquet"


@dataclass
class ExportConfig:
    """導出配置"""
    format: ExportFormat
    output_path: str
    include_headers: bool = True
    encoding: str = "utf-8"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    include_metadata: bool = False
    compress: bool = False
    chunk_size: Optional[int] = None
    

class DataExporter:
    """數據導出器
    
    支持多種格式的數據導出功能
    """
    
    def __init__(self, config: ExportConfig):
        """初始化導出器
        
        Args:
            config: 導出配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def export_jobs(self, jobs: List[Union[CleanedJobData, ProcessedJobData]]) -> str:
        """導出職位數據
        
        Args:
            jobs: 職位數據列表
            
        Returns:
            str: 導出文件路徑
        """
        try:
            # 轉換為字典格式
            job_dicts = [job.to_dict() for job in jobs]
            
            # 根據格式選擇導出方法
            if self.config.format == ExportFormat.CSV:
                return await self._export_to_csv(job_dicts)
            elif self.config.format == ExportFormat.JSON:
                return await self._export_to_json(job_dicts)
            elif self.config.format == ExportFormat.EXCEL:
                return await self._export_to_excel(job_dicts)
            elif self.config.format == ExportFormat.PARQUET:
                return await self._export_to_parquet(job_dicts)
            else:
                raise ValueError(f"不支持的導出格式: {self.config.format}")
                
        except Exception as e:
            self.logger.error(f"導出職位數據失敗: {e}")
            raise
    
    async def export_companies(self, companies: List[ProcessedCompanyData]) -> str:
        """導出公司數據
        
        Args:
            companies: 公司數據列表
            
        Returns:
            str: 導出文件路徑
        """
        try:
            # 轉換為字典格式
            company_dicts = [company.to_dict() for company in companies]
            
            # 根據格式選擇導出方法
            if self.config.format == ExportFormat.CSV:
                return await self._export_to_csv(company_dicts, "companies")
            elif self.config.format == ExportFormat.JSON:
                return await self._export_to_json(company_dicts, "companies")
            elif self.config.format == ExportFormat.EXCEL:
                return await self._export_to_excel(company_dicts, "companies")
            elif self.config.format == ExportFormat.PARQUET:
                return await self._export_to_parquet(company_dicts, "companies")
            else:
                raise ValueError(f"不支持的導出格式: {self.config.format}")
                
        except Exception as e:
            self.logger.error(f"導出公司數據失敗: {e}")
            raise
    
    async def _export_to_csv(self, data: List[Dict[str, Any]], prefix: str = "jobs") -> str:
        """導出為 CSV 格式
        
        Args:
            data: 要導出的數據
            prefix: 文件名前綴
            
        Returns:
            str: 導出文件路徑
        """
        if not data:
            raise ValueError("沒有數據可導出")
        
        # 生成文件路徑
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"
        output_path = Path(self.config.output_path) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入 CSV 文件
        with open(output_path, 'w', newline='', encoding=self.config.encoding) as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if self.config.include_headers:
                    writer.writeheader()
                
                # 分塊寫入（如果配置了塊大小）
                if self.config.chunk_size:
                    for i in range(0, len(data), self.config.chunk_size):
                        chunk = data[i:i + self.config.chunk_size]
                        writer.writerows(chunk)
                else:
                    writer.writerows(data)
        
        self.logger.info(f"CSV 導出完成: {output_path}")
        return str(output_path)
    
    async def _export_to_json(self, data: List[Dict[str, Any]], prefix: str = "jobs") -> str:
        """導出為 JSON 格式
        
        Args:
            data: 要導出的數據
            prefix: 文件名前綴
            
        Returns:
            str: 導出文件路徑
        """
        # 生成文件路徑
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        output_path = Path(self.config.output_path) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 準備導出數據
        export_data = {
            "data": data,
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_records": len(data),
                "format": "json"
            } if self.config.include_metadata else None
        }
        
        if not self.config.include_metadata:
            export_data = data
        
        # 寫入 JSON 文件
        with open(output_path, 'w', encoding=self.config.encoding) as jsonfile:
            json.dump(export_data, jsonfile, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"JSON 導出完成: {output_path}")
        return str(output_path)
    
    async def _export_to_excel(self, data: List[Dict[str, Any]], prefix: str = "jobs") -> str:
        """導出為 Excel 格式
        
        Args:
            data: 要導出的數據
            prefix: 文件名前綴
            
        Returns:
            str: 導出文件路徑
        """
        if not data:
            raise ValueError("沒有數據可導出")
        
        # 生成文件路徑
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.xlsx"
        output_path = Path(self.config.output_path) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 轉換為 DataFrame
        df = pd.DataFrame(data)
        
        # 寫入 Excel 文件
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # 添加元數據工作表（如果配置了）
            if self.config.include_metadata:
                metadata_df = pd.DataFrame([
                    {"屬性": "導出時間", "值": datetime.now().strftime(self.config.date_format)},
                    {"屬性": "記錄總數", "值": len(data)},
                    {"屬性": "格式", "值": "Excel"},
                    {"屬性": "編碼", "值": self.config.encoding}
                ])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        self.logger.info(f"Excel 導出完成: {output_path}")
        return str(output_path)
    
    async def _export_to_parquet(self, data: List[Dict[str, Any]], prefix: str = "jobs") -> str:
        """導出為 Parquet 格式
        
        Args:
            data: 要導出的數據
            prefix: 文件名前綴
            
        Returns:
            str: 導出文件路徑
        """
        if not data:
            raise ValueError("沒有數據可導出")
        
        # 生成文件路徑
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.parquet"
        output_path = Path(self.config.output_path) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 轉換為 DataFrame 並寫入 Parquet
        df = pd.DataFrame(data)
        df.to_parquet(output_path, compression='snappy' if self.config.compress else None)
        
        self.logger.info(f"Parquet 導出完成: {output_path}")
        return str(output_path)
    
    async def export_summary_report(self, jobs: List[CleanedJobData]) -> str:
        """導出摘要報告
        
        Args:
            jobs: 職位數據列表
            
        Returns:
            str: 報告文件路徑
        """
        try:
            # 生成摘要統計
            summary = self._generate_summary_stats(jobs)
            
            # 生成文件路徑
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_summary_report_{timestamp}.json"
            output_path = Path(self.config.output_path) / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 寫入報告
            with open(output_path, 'w', encoding=self.config.encoding) as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"摘要報告導出完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"導出摘要報告失敗: {e}")
            raise
    
    def _generate_summary_stats(self, jobs: List[CleanedJobData]) -> Dict[str, Any]:
        """生成摘要統計
        
        Args:
            jobs: 職位數據列表
            
        Returns:
            Dict[str, Any]: 摘要統計數據
        """
        if not jobs:
            return {"total_jobs": 0, "message": "沒有職位數據"}
        
        # 基本統計
        total_jobs = len(jobs)
        platforms = list(set(job.platform for job in jobs))
        locations = list(set(job.normalized_location for job in jobs if job.normalized_location))
        companies = list(set(job.company for job in jobs))
        
        # 職位類型統計
        job_types = {}
        for job in jobs:
            job_type = job.job_type.value if job.job_type else "unknown"
            job_types[job_type] = job_types.get(job_type, 0) + 1
        
        # 經驗等級統計
        experience_levels = {}
        for job in jobs:
            level = job.experience_level.value if job.experience_level else "unknown"
            experience_levels[level] = experience_levels.get(level, 0) + 1
        
        # 薪資統計
        salaries = [job.salary_min for job in jobs if job.salary_min]
        salary_stats = {}
        if salaries:
            salary_stats = {
                "min": min(salaries),
                "max": max(salaries),
                "avg": sum(salaries) / len(salaries),
                "count": len(salaries)
            }
        
        # 技能統計
        all_skills = []
        for job in jobs:
            all_skills.extend(job.normalized_skills)
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # 排序技能（按出現頻率）
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_jobs": total_jobs,
            "platforms": platforms,
            "unique_companies": len(companies),
            "unique_locations": len(locations),
            "job_type_distribution": job_types,
            "experience_level_distribution": experience_levels,
            "salary_statistics": salary_stats,
            "top_skills": dict(top_skills),
            "data_quality": {
                "jobs_with_salary": len([j for j in jobs if j.salary_min]),
                "jobs_with_skills": len([j for j in jobs if j.normalized_skills]),
                "average_quality_score": sum(j.data_quality_score for j in jobs) / len(jobs)
            }
        }