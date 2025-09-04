#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段映射轉換器

提供新舊數據格式之間的字段映射和轉換功能。
支持雙向轉換、自定義映射規則和數據驗證。
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum


class MappingDirection(Enum):
    """映射方向枚舉"""
    LEGACY_TO_MODERN = "legacy_to_modern"
    MODERN_TO_LEGACY = "modern_to_legacy"
    BIDIRECTIONAL = "bidirectional"


class DataType(Enum):
    """數據類型枚舉"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    LIST = "list"
    DICT = "dict"


@dataclass
class FieldMapping:
    """字段映射配置"""
    source_field: str
    target_field: str
    data_type: DataType = DataType.STRING
    default_value: Any = ""
    transform_function: Optional[Callable] = None
    validation_function: Optional[Callable] = None
    required: bool = False
    description: str = ""


@dataclass
class MappingConfig:
    """映射配置"""
    name: str
    description: str = ""
    direction: MappingDirection = MappingDirection.BIDIRECTIONAL
    field_mappings: List[FieldMapping] = field(default_factory=list)
    custom_transformers: Dict[str, Callable] = field(default_factory=dict)
    validation_rules: Dict[str, Callable] = field(default_factory=dict)
    
    # 全局設置
    strict_mode: bool = False  # 嚴格模式：缺少必需字段時拋出異常
    ignore_unknown_fields: bool = True  # 忽略未知字段
    preserve_original: bool = False  # 保留原始數據


class FieldMapper:
    """字段映射轉換器
    
    提供靈活的字段映射和數據轉換功能。
    """
    
    def __init__(self, config: MappingConfig):
        """初始化字段映射器
        
        Args:
            config: 映射配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 構建映射索引
        self._build_mapping_index()
        
        # 註冊內置轉換器
        self._register_builtin_transformers()
    
    def _build_mapping_index(self):
        """構建映射索引以提高查找效率"""
        self.source_to_target = {}
        self.target_to_source = {}
        
        for mapping in self.config.field_mappings:
            self.source_to_target[mapping.source_field] = mapping
            if self.config.direction in [MappingDirection.BIDIRECTIONAL, MappingDirection.MODERN_TO_LEGACY]:
                self.target_to_source[mapping.target_field] = mapping
    
    def _register_builtin_transformers(self):
        """註冊內置轉換器"""
        self.builtin_transformers = {
            'to_upper': lambda x: str(x).upper() if x else "",
            'to_lower': lambda x: str(x).lower() if x else "",
            'to_title': lambda x: str(x).title() if x else "",
            'strip_whitespace': lambda x: str(x).strip() if x else "",
            'to_int': self._safe_int_convert,
            'to_float': self._safe_float_convert,
            'to_bool': self._safe_bool_convert,
            'format_date': self._format_date,
            'parse_location': self._parse_location,
            'join_list': lambda x: ', '.join(x) if isinstance(x, list) else str(x),
            'split_string': lambda x: [item.strip() for item in str(x).split(',') if item.strip()],
            'clean_description': self._clean_description,
            'standardize_job_type': self._standardize_job_type,
            'format_salary': self._format_salary
        }
    
    def transform(self, data: Dict[str, Any], direction: Optional[MappingDirection] = None) -> Dict[str, Any]:
        """執行字段映射轉換
        
        Args:
            data: 源數據字典
            direction: 轉換方向，如果為None則使用配置中的方向
            
        Returns:
            Dict[str, Any]: 轉換後的數據字典
        """
        if direction is None:
            direction = self.config.direction
        
        if direction == MappingDirection.LEGACY_TO_MODERN:
            return self._transform_legacy_to_modern(data)
        elif direction == MappingDirection.MODERN_TO_LEGACY:
            return self._transform_modern_to_legacy(data)
        else:
            raise ValueError(f"不支持的轉換方向: {direction}")
    
    def _transform_legacy_to_modern(self, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """將舊格式數據轉換為現代格式
        
        Args:
            legacy_data: 舊格式數據
            
        Returns:
            Dict[str, Any]: 現代格式數據
        """
        modern_data = {}
        
        if self.config.preserve_original:
            modern_data['_original'] = legacy_data.copy()
        
        for source_field, mapping in self.source_to_target.items():
            try:
                # 獲取源值
                source_value = legacy_data.get(source_field, mapping.default_value)
                
                # 應用轉換
                transformed_value = self._apply_transformation(source_value, mapping)
                
                # 驗證數據
                if mapping.validation_function:
                    if not mapping.validation_function(transformed_value):
                        if self.config.strict_mode:
                            raise ValueError(f"字段 {source_field} 驗證失敗")
                        else:
                            self.logger.warning(f"字段 {source_field} 驗證失敗，使用默認值")
                            transformed_value = mapping.default_value
                
                modern_data[mapping.target_field] = transformed_value
                
            except Exception as e:
                if self.config.strict_mode:
                    raise Exception(f"轉換字段 {source_field} 時發生錯誤: {e}")
                else:
                    self.logger.error(f"轉換字段 {source_field} 失敗: {e}，使用默認值")
                    modern_data[mapping.target_field] = mapping.default_value
        
        # 處理未知字段
        if not self.config.ignore_unknown_fields:
            for key, value in legacy_data.items():
                if key not in self.source_to_target:
                    modern_data[f"legacy_{key}"] = value
        
        return modern_data
    
    def _transform_modern_to_legacy(self, modern_data: Dict[str, Any]) -> Dict[str, Any]:
        """將現代格式數據轉換為舊格式
        
        Args:
            modern_data: 現代格式數據
            
        Returns:
            Dict[str, Any]: 舊格式數據
        """
        legacy_data = {}
        
        if self.config.preserve_original:
            legacy_data['_original'] = modern_data.copy()
        
        for target_field, mapping in self.target_to_source.items():
            try:
                # 獲取源值
                source_value = modern_data.get(target_field, mapping.default_value)
                
                # 應用反向轉換
                transformed_value = self._apply_reverse_transformation(source_value, mapping)
                
                legacy_data[mapping.source_field] = transformed_value
                
            except Exception as e:
                if self.config.strict_mode:
                    raise Exception(f"反向轉換字段 {target_field} 時發生錯誤: {e}")
                else:
                    self.logger.error(f"反向轉換字段 {target_field} 失敗: {e}，使用默認值")
                    legacy_data[mapping.source_field] = mapping.default_value
        
        return legacy_data
    
    def _apply_transformation(self, value: Any, mapping: FieldMapping) -> Any:
        """應用字段轉換
        
        Args:
            value: 原始值
            mapping: 字段映射配置
            
        Returns:
            Any: 轉換後的值
        """
        if value is None or value == "":
            return mapping.default_value
        
        # 應用自定義轉換函數
        if mapping.transform_function:
            value = mapping.transform_function(value)
        
        # 應用數據類型轉換
        value = self._convert_data_type(value, mapping.data_type)
        
        return value
    
    def _apply_reverse_transformation(self, value: Any, mapping: FieldMapping) -> Any:
        """應用反向轉換（用於現代格式轉舊格式）
        
        Args:
            value: 現代格式值
            mapping: 字段映射配置
            
        Returns:
            Any: 舊格式值
        """
        if value is None:
            return ""
        
        # 簡單的反向轉換邏輯
        if mapping.data_type == DataType.LIST and isinstance(value, list):
            return ', '.join(str(item) for item in value)
        elif mapping.data_type == DataType.BOOLEAN:
            return "Yes" if value else "No"
        elif mapping.data_type == DataType.DATE and hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        else:
            return str(value)
    
    def _convert_data_type(self, value: Any, data_type: DataType) -> Any:
        """轉換數據類型
        
        Args:
            value: 原始值
            data_type: 目標數據類型
            
        Returns:
            Any: 轉換後的值
        """
        try:
            if data_type == DataType.STRING:
                return str(value)
            elif data_type == DataType.INTEGER:
                return int(float(str(value))) if value else 0
            elif data_type == DataType.FLOAT:
                return float(str(value)) if value else 0.0
            elif data_type == DataType.BOOLEAN:
                return self._safe_bool_convert(value)
            elif data_type == DataType.DATE:
                return self._parse_date(value)
            elif data_type == DataType.LIST:
                if isinstance(value, list):
                    return value
                return [item.strip() for item in str(value).split(',') if item.strip()]
            elif data_type == DataType.DICT:
                if isinstance(value, dict):
                    return value
                return {}
            else:
                return value
        except Exception as e:
            self.logger.warning(f"數據類型轉換失敗: {e}，返回原值")
            return value
    
    # 內置轉換器實現
    def _safe_int_convert(self, value: Any) -> int:
        """安全的整數轉換"""
        try:
            if isinstance(value, str):
                # 移除非數字字符
                value = re.sub(r'[^\d.-]', '', value)
            return int(float(value)) if value else 0
        except (ValueError, TypeError):
            return 0
    
    def _safe_float_convert(self, value: Any) -> float:
        """安全的浮點數轉換"""
        try:
            if isinstance(value, str):
                # 移除非數字字符（保留小數點）
                value = re.sub(r'[^\d.-]', '', value)
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_bool_convert(self, value: Any) -> bool:
        """安全的布爾值轉換"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 'on', 'enabled']
        return bool(value)
    
    def _format_date(self, value: Any, format_str: str = '%Y-%m-%d') -> str:
        """格式化日期"""
        if hasattr(value, 'strftime'):
            return value.strftime(format_str)
        return str(value)
    
    def _parse_date(self, value: Any) -> Optional[datetime]:
        """解析日期字符串"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value:
            try:
                # 嘗試多種日期格式
                for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
            except Exception:
                pass
        return None
    
    def _parse_location(self, value: str) -> Dict[str, str]:
        """解析地理位置"""
        if not value:
            return {'city': '', 'state': '', 'country': ''}
        
        parts = [part.strip() for part in value.split(',')]
        result = {'city': '', 'state': '', 'country': ''}
        
        if len(parts) >= 1:
            result['city'] = parts[0]
        if len(parts) >= 2:
            result['state'] = parts[1]
        if len(parts) >= 3:
            result['country'] = parts[2]
        
        return result
    
    def _clean_description(self, value: str) -> str:
        """清理職位描述"""
        if not value:
            return ""
        
        # 移除HTML標籤
        value = re.sub(r'<[^>]+>', '', value)
        # 標準化空白字符
        value = re.sub(r'\s+', ' ', value)
        # 移除特殊字符
        value = re.sub(r'[^\w\s.,!?()-]', '', value)
        
        return value.strip()
    
    def _standardize_job_type(self, value: str) -> str:
        """標準化工作類型"""
        if not value:
            return "full-time"
        
        value = value.lower().strip()
        
        # 標準化映射
        type_mapping = {
            'full time': 'full-time',
            'fulltime': 'full-time',
            'ft': 'full-time',
            'part time': 'part-time',
            'parttime': 'part-time',
            'pt': 'part-time',
            'contractor': 'contract',
            'freelance': 'contract',
            'temp': 'temporary',
            'intern': 'internship'
        }
        
        return type_mapping.get(value, value)
    
    def _format_salary(self, value: Any) -> str:
        """格式化薪資"""
        try:
            if isinstance(value, (int, float)):
                return f"{int(value):,}"
            elif isinstance(value, str) and value.isdigit():
                return f"{int(value):,}"
            else:
                return str(value)
        except Exception:
            return str(value)
    
    def validate_mapping(self) -> List[str]:
        """驗證映射配置
        
        Returns:
            List[str]: 驗證錯誤列表
        """
        errors = []
        
        # 檢查重複的源字段
        source_fields = [mapping.source_field for mapping in self.config.field_mappings]
        duplicates = set([field for field in source_fields if source_fields.count(field) > 1])
        if duplicates:
            errors.append(f"重複的源字段: {duplicates}")
        
        # 檢查重複的目標字段
        target_fields = [mapping.target_field for mapping in self.config.field_mappings]
        duplicates = set([field for field in target_fields if target_fields.count(field) > 1])
        if duplicates:
            errors.append(f"重複的目標字段: {duplicates}")
        
        # 檢查必需字段
        required_mappings = [mapping for mapping in self.config.field_mappings if mapping.required]
        if not required_mappings and self.config.strict_mode:
            errors.append("嚴格模式下至少需要一個必需字段")
        
        return errors


# 預定義映射配置
def create_jobspy_v1_mapping() -> MappingConfig:
    """創建JobSpy v1格式映射配置
    
    Returns:
        MappingConfig: JobSpy v1映射配置
    """
    mappings = [
        FieldMapping("SITE", "platform", DataType.STRING, "seek"),
        FieldMapping("TITLE", "title", DataType.STRING, "", required=True),
        FieldMapping("COMPANY", "company", DataType.STRING, "", required=True),
        FieldMapping("CITY", "city", DataType.STRING, ""),
        FieldMapping("STATE", "state", DataType.STRING, ""),
        FieldMapping("JOB_TYPE", "job_type", DataType.STRING, "full-time"),
        FieldMapping("INTERVAL", "salary_type", DataType.STRING, "yearly"),
        FieldMapping("MIN_AMOUNT", "salary_min", DataType.INTEGER, 0),
        FieldMapping("MAX_AMOUNT", "salary_max", DataType.INTEGER, 0),
        FieldMapping("JOB_URL", "url", DataType.STRING, ""),
        FieldMapping("DESCRIPTION", "description", DataType.STRING, "")
    ]
    
    return MappingConfig(
        name="JobSpy v1 Mapping",
        description="JobSpy v1格式到現代格式的映射",
        direction=MappingDirection.BIDIRECTIONAL,
        field_mappings=mappings,
        strict_mode=False,
        ignore_unknown_fields=True
    )


def create_field_mapper(mapping_type: str = "jobspy_v1") -> FieldMapper:
    """創建字段映射器的便捷函數
    
    Args:
        mapping_type: 映射類型
        
    Returns:
        FieldMapper: 字段映射器實例
    """
    if mapping_type == "jobspy_v1":
        config = create_jobspy_v1_mapping()
    else:
        raise ValueError(f"不支持的映射類型: {mapping_type}")
    
    return FieldMapper(config)