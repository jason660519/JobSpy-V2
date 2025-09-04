#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強導出配置

提供靈活的導出配置功能，包括：
- 多種CSV格式變體支持
- 自定義字段選擇和映射
- 導出模板管理
- 格式驗證和優化
- 批量導出配置
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json


class ExportFormat(Enum):
    """導出格式枚舉"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    XML = "xml"
    HTML = "html"
    PARQUET = "parquet"
    JSONL = "jsonl"


class CSVVariant(Enum):
    """CSV變體枚舉"""
    STANDARD = "standard"           # 標準CSV格式
    LEGACY_V1 = "legacy_v1"         # JobSpy v1格式
    LEGACY_CUSTOM = "legacy_custom" # 自定義舊格式
    EXCEL_COMPATIBLE = "excel"      # Excel兼容格式
    GOOGLE_SHEETS = "google_sheets" # Google Sheets格式
    MINIMAL = "minimal"             # 最小字段集
    DETAILED = "detailed"           # 詳細字段集
    ANALYTICS = "analytics"         # 分析用格式


class CompressionType(Enum):
    """壓縮類型枚舉"""
    NONE = "none"
    GZIP = "gzip"
    ZIP = "zip"
    BZIP2 = "bzip2"
    XZ = "xz"


class FieldType(Enum):
    """字段類型枚舉"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    URL = "url"
    EMAIL = "email"
    JSON_ARRAY = "json_array"
    JSON_OBJECT = "json_object"


@dataclass
class FieldDefinition:
    """字段定義"""
    name: str
    display_name: str
    field_type: FieldType
    required: bool = False
    default_value: Any = None
    max_length: Optional[int] = None
    format_pattern: Optional[str] = None
    description: str = ""
    source_path: Optional[str] = None  # 源數據路徑，如 "job_data.title"
    transformer: Optional[str] = None  # 轉換函數名
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class CSVConfig:
    """CSV配置"""
    delimiter: str = ","
    quote_char: str = '"'
    escape_char: str = "\\"
    line_terminator: str = "\n"
    encoding: str = "utf-8"
    include_header: bool = True
    quote_all: bool = False
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    null_value: str = ""
    boolean_format: Dict[str, str] = field(default_factory=lambda: {"true": "True", "false": "False"})
    max_field_length: Optional[int] = None
    trim_whitespace: bool = True


@dataclass
class ExportTemplate:
    """導出模板"""
    name: str
    description: str
    format: ExportFormat
    variant: Optional[CSVVariant] = None
    fields: List[FieldDefinition] = field(default_factory=list)
    csv_config: Optional[CSVConfig] = None
    compression: CompressionType = CompressionType.NONE
    file_naming_pattern: str = "{timestamp}_{template_name}.{extension}"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BatchExportConfig:
    """批量導出配置"""
    batch_size: int = 1000
    max_file_size_mb: int = 100
    split_by_field: Optional[str] = None  # 按字段分割文件
    parallel_processing: bool = False
    max_workers: int = 4
    output_directory: str = "./exports"
    create_index_file: bool = True
    compress_individual_files: bool = False
    final_compression: CompressionType = CompressionType.NONE


@dataclass
class ValidationRule:
    """驗證規則"""
    rule_type: str  # "required", "length", "pattern", "range", "custom"
    parameters: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    severity: str = "error"  # "error", "warning", "info"


class EnhancedExportConfig:
    """增強導出配置管理器
    
    提供靈活的導出配置管理功能。
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化增強導出配置
        
        Args:
            config_file: 配置文件路徑
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        
        # 初始化預定義模板
        self.templates: Dict[str, ExportTemplate] = {}
        self._init_predefined_templates()
        
        # 初始化字段轉換器
        self._init_field_transformers()
        
        # 初始化驗證器
        self._init_validators()
        
        # 加載配置文件
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
    
    def _init_predefined_templates(self):
        """初始化預定義模板"""
        # 標準JobSpy v2模板
        self.templates["standard"] = ExportTemplate(
            name="standard",
            description="標準JobSpy v2導出格式",
            format=ExportFormat.CSV,
            variant=CSVVariant.STANDARD,
            fields=[
                FieldDefinition("id", "ID", FieldType.STRING, required=True),
                FieldDefinition("title", "職位標題", FieldType.STRING, required=True, max_length=200),
                FieldDefinition("company", "公司名稱", FieldType.STRING, required=True, max_length=100),
                FieldDefinition("location", "工作地點", FieldType.STRING, max_length=100),
                FieldDefinition("city", "城市", FieldType.STRING, max_length=50),
                FieldDefinition("state", "州/省", FieldType.STRING, max_length=50),
                FieldDefinition("country", "國家", FieldType.STRING, max_length=50),
                FieldDefinition("description", "職位描述", FieldType.STRING, max_length=5000),
                FieldDefinition("requirements", "職位要求", FieldType.STRING, max_length=3000),
                FieldDefinition("benefits", "福利待遇", FieldType.STRING, max_length=2000),
                FieldDefinition("salary_min", "最低薪資", FieldType.INTEGER),
                FieldDefinition("salary_max", "最高薪資", FieldType.INTEGER),
                FieldDefinition("salary_currency", "薪資貨幣", FieldType.STRING, max_length=10),
                FieldDefinition("job_type", "工作類型", FieldType.STRING, max_length=20),
                FieldDefinition("work_arrangement", "工作安排", FieldType.STRING, max_length=20),
                FieldDefinition("experience_level", "經驗要求", FieldType.STRING, max_length=20),
                FieldDefinition("skills", "技能要求", FieldType.JSON_ARRAY),
                FieldDefinition("url", "職位鏈接", FieldType.URL, required=True),
                FieldDefinition("posted_date", "發布日期", FieldType.DATE),
                FieldDefinition("scraped_at", "抓取時間", FieldType.DATETIME, required=True)
            ],
            csv_config=CSVConfig()
        )
        
        # Legacy v1兼容模板
        self.templates["legacy_v1"] = ExportTemplate(
            name="legacy_v1",
            description="JobSpy v1兼容格式",
            format=ExportFormat.CSV,
            variant=CSVVariant.LEGACY_V1,
            fields=[
                FieldDefinition("SITE", "網站", FieldType.STRING, required=True, default_value="seek"),
                FieldDefinition("TITLE", "職位標題", FieldType.STRING, required=True, source_path="title"),
                FieldDefinition("COMPANY", "公司", FieldType.STRING, required=True, source_path="company"),
                FieldDefinition("CITY", "城市", FieldType.STRING, source_path="city"),
                FieldDefinition("STATE", "州", FieldType.STRING, source_path="state"),
                FieldDefinition("JOB_TYPE", "工作類型", FieldType.STRING, source_path="job_type"),
                FieldDefinition("INTERVAL", "薪資週期", FieldType.STRING, default_value="yearly"),
                FieldDefinition("MIN_AMOUNT", "最低薪資", FieldType.INTEGER, source_path="salary_min"),
                FieldDefinition("MAX_AMOUNT", "最高薪資", FieldType.INTEGER, source_path="salary_max"),
                FieldDefinition("JOB_URL", "職位鏈接", FieldType.URL, required=True, source_path="url"),
                FieldDefinition("DESCRIPTION", "描述", FieldType.STRING, source_path="description", max_length=1000)
            ],
            csv_config=CSVConfig(encoding="utf-8-sig")  # Excel兼容的BOM
        )
        
        # 最小字段模板
        self.templates["minimal"] = ExportTemplate(
            name="minimal",
            description="最小字段集合",
            format=ExportFormat.CSV,
            variant=CSVVariant.MINIMAL,
            fields=[
                FieldDefinition("title", "職位", FieldType.STRING, required=True),
                FieldDefinition("company", "公司", FieldType.STRING, required=True),
                FieldDefinition("location", "地點", FieldType.STRING),
                FieldDefinition("salary_range", "薪資", FieldType.STRING, transformer="format_salary_range"),
                FieldDefinition("url", "鏈接", FieldType.URL, required=True)
            ],
            csv_config=CSVConfig()
        )
        
        # 詳細分析模板
        self.templates["analytics"] = ExportTemplate(
            name="analytics",
            description="數據分析用詳細格式",
            format=ExportFormat.CSV,
            variant=CSVVariant.ANALYTICS,
            fields=[
                FieldDefinition("id", "ID", FieldType.STRING, required=True),
                FieldDefinition("title", "職位標題", FieldType.STRING, required=True),
                FieldDefinition("company", "公司名稱", FieldType.STRING, required=True),
                FieldDefinition("industry", "行業", FieldType.STRING),
                FieldDefinition("company_size", "公司規模", FieldType.STRING),
                FieldDefinition("location_standardized", "標準化地點", FieldType.STRING),
                FieldDefinition("experience_level", "經驗等級", FieldType.STRING),
                FieldDefinition("skills_count", "技能數量", FieldType.INTEGER, transformer="count_skills"),
                FieldDefinition("top_skills", "主要技能", FieldType.STRING, transformer="format_top_skills"),
                FieldDefinition("salary_predicted_min", "預測最低薪資", FieldType.INTEGER),
                FieldDefinition("salary_predicted_max", "預測最高薪資", FieldType.INTEGER),
                FieldDefinition("market_demand_score", "市場需求分數", FieldType.FLOAT),
                FieldDefinition("growth_potential_score", "成長潛力分數", FieldType.FLOAT),
                FieldDefinition("data_quality_score", "數據質量分數", FieldType.FLOAT),
                FieldDefinition("language_detected", "檢測語言", FieldType.STRING),
                FieldDefinition("work_arrangement", "工作安排", FieldType.STRING),
                FieldDefinition("urgency_level", "緊急程度", FieldType.STRING),
                FieldDefinition("posted_date", "發布日期", FieldType.DATE),
                FieldDefinition("scraped_at", "抓取時間", FieldType.DATETIME)
            ],
            csv_config=CSVConfig()
        )
        
        # Excel兼容模板
        self.templates["excel_compatible"] = ExportTemplate(
            name="excel_compatible",
            description="Excel兼容格式",
            format=ExportFormat.CSV,
            variant=CSVVariant.EXCEL_COMPATIBLE,
            fields=self.templates["standard"].fields.copy(),
            csv_config=CSVConfig(
                encoding="utf-8-sig",  # BOM for Excel
                delimiter=",",
                quote_all=True,
                date_format="%d/%m/%Y",
                datetime_format="%d/%m/%Y %H:%M"
            )
        )
    
    def _init_field_transformers(self):
        """初始化字段轉換器"""
        self.transformers = {
            "format_salary_range": self._format_salary_range,
            "count_skills": self._count_skills,
            "format_top_skills": self._format_top_skills,
            "truncate_description": self._truncate_description,
            "normalize_location": self._normalize_location,
            "format_boolean": self._format_boolean,
            "format_date": self._format_date,
            "clean_html": self._clean_html,
            "extract_domain": self._extract_domain
        }
    
    def _init_validators(self):
        """初始化驗證器"""
        self.validators = {
            "required": self._validate_required,
            "length": self._validate_length,
            "pattern": self._validate_pattern,
            "range": self._validate_range,
            "url": self._validate_url,
            "email": self._validate_email
        }
    
    def create_template(self, template: ExportTemplate) -> bool:
        """創建新模板
        
        Args:
            template: 導出模板
            
        Returns:
            bool: 是否創建成功
        """
        try:
            # 驗證模板
            if not self._validate_template(template):
                return False
            
            template.updated_at = datetime.now()
            self.templates[template.name] = template
            
            self.logger.info(f"創建模板成功: {template.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"創建模板失敗: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[ExportTemplate]:
        """獲取模板
        
        Args:
            name: 模板名稱
            
        Returns:
            Optional[ExportTemplate]: 模板對象
        """
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板名稱
        
        Returns:
            List[str]: 模板名稱列表
        """
        return list(self.templates.keys())
    
    def update_template(self, name: str, updates: Dict[str, Any]) -> bool:
        """更新模板
        
        Args:
            name: 模板名稱
            updates: 更新內容
            
        Returns:
            bool: 是否更新成功
        """
        if name not in self.templates:
            self.logger.error(f"模板不存在: {name}")
            return False
        
        try:
            template = self.templates[name]
            
            # 更新字段
            for key, value in updates.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = datetime.now()
            
            # 重新驗證
            if not self._validate_template(template):
                return False
            
            self.logger.info(f"更新模板成功: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新模板失敗: {e}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """刪除模板
        
        Args:
            name: 模板名稱
            
        Returns:
            bool: 是否刪除成功
        """
        if name in self.templates:
            del self.templates[name]
            self.logger.info(f"刪除模板成功: {name}")
            return True
        else:
            self.logger.error(f"模板不存在: {name}")
            return False
    
    def create_custom_template(self, name: str, base_template: str,
                             field_modifications: Dict[str, Any]) -> Optional[ExportTemplate]:
        """基於現有模板創建自定義模板
        
        Args:
            name: 新模板名稱
            base_template: 基礎模板名稱
            field_modifications: 字段修改
            
        Returns:
            Optional[ExportTemplate]: 新模板
        """
        if base_template not in self.templates:
            self.logger.error(f"基礎模板不存在: {base_template}")
            return None
        
        try:
            # 複製基礎模板
            base = self.templates[base_template]
            new_template = ExportTemplate(
                name=name,
                description=field_modifications.get('description', f"基於{base_template}的自定義模板"),
                format=field_modifications.get('format', base.format),
                variant=field_modifications.get('variant', base.variant),
                fields=base.fields.copy(),
                csv_config=base.csv_config,
                compression=field_modifications.get('compression', base.compression),
                file_naming_pattern=field_modifications.get('file_naming_pattern', base.file_naming_pattern)
            )
            
            # 應用字段修改
            if 'add_fields' in field_modifications:
                new_template.fields.extend(field_modifications['add_fields'])
            
            if 'remove_fields' in field_modifications:
                remove_names = set(field_modifications['remove_fields'])
                new_template.fields = [f for f in new_template.fields if f.name not in remove_names]
            
            if 'modify_fields' in field_modifications:
                field_map = {f.name: f for f in new_template.fields}
                for field_name, modifications in field_modifications['modify_fields'].items():
                    if field_name in field_map:
                        field = field_map[field_name]
                        for key, value in modifications.items():
                            if hasattr(field, key):
                                setattr(field, key, value)
            
            # 創建模板
            if self.create_template(new_template):
                return new_template
            
        except Exception as e:
            self.logger.error(f"創建自定義模板失敗: {e}")
        
        return None
    
    def get_export_config(self, template_name: str, 
                         batch_config: Optional[BatchExportConfig] = None) -> Dict[str, Any]:
        """獲取完整的導出配置
        
        Args:
            template_name: 模板名稱
            batch_config: 批量配置
            
        Returns:
            Dict[str, Any]: 導出配置
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"模板不存在: {template_name}")
        
        config = {
            'template': template,
            'batch_config': batch_config or BatchExportConfig(),
            'transformers': self.transformers,
            'validators': self.validators
        }
        
        return config
    
    def validate_data(self, data: Dict[str, Any], template_name: str) -> Tuple[bool, List[str]]:
        """驗證數據
        
        Args:
            data: 數據
            template_name: 模板名稱
            
        Returns:
            Tuple[bool, List[str]]: 驗證結果和錯誤信息
        """
        template = self.get_template(template_name)
        if not template:
            return False, [f"模板不存在: {template_name}"]
        
        errors = []
        
        for field in template.fields:
            value = data.get(field.name)
            
            # 驗證必需字段
            if field.required and (value is None or value == ""):
                errors.append(f"必需字段缺失: {field.name}")
                continue
            
            # 跳過空值的其他驗證
            if value is None or value == "":
                continue
            
            # 長度驗證
            if field.max_length and isinstance(value, str) and len(value) > field.max_length:
                errors.append(f"字段 {field.name} 長度超限: {len(value)} > {field.max_length}")
            
            # 類型驗證
            if not self._validate_field_type(value, field.field_type):
                errors.append(f"字段 {field.name} 類型錯誤: 期望 {field.field_type.value}")
            
            # 自定義驗證規則
            for rule in field.validation_rules:
                if not self._apply_validation_rule(value, rule, field):
                    errors.append(f"字段 {field.name} 驗證失敗: {rule}")
        
        return len(errors) == 0, errors
    
    def transform_data(self, data: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """轉換數據
        
        Args:
            data: 原始數據
            template_name: 模板名稱
            
        Returns:
            Dict[str, Any]: 轉換後的數據
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"模板不存在: {template_name}")
        
        transformed = {}
        
        for field in template.fields:
            # 獲取源值
            if field.source_path:
                value = self._get_nested_value(data, field.source_path)
            else:
                value = data.get(field.name)
            
            # 使用默認值
            if value is None and field.default_value is not None:
                value = field.default_value
            
            # 應用轉換器
            if field.transformer and field.transformer in self.transformers:
                try:
                    value = self.transformers[field.transformer](value, field, data)
                except Exception as e:
                    self.logger.warning(f"轉換器 {field.transformer} 失敗: {e}")
            
            # 格式化值
            value = self._format_field_value(value, field, template.csv_config)
            
            transformed[field.name] = value
        
        return transformed
    
    def save_config(self, file_path: str) -> bool:
        """保存配置到文件
        
        Args:
            file_path: 文件路徑
            
        Returns:
            bool: 是否保存成功
        """
        try:
            config_data = {
                'templates': {},
                'version': '1.0',
                'created_at': datetime.now().isoformat()
            }
            
            # 序列化模板
            for name, template in self.templates.items():
                config_data['templates'][name] = self._serialize_template(template)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"配置保存成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置保存失敗: {e}")
            return False
    
    def load_config(self, file_path: str) -> bool:
        """從文件加載配置
        
        Args:
            file_path: 文件路徑
            
        Returns:
            bool: 是否加載成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 反序列化模板
            for name, template_data in config_data.get('templates', {}).items():
                template = self._deserialize_template(template_data)
                if template:
                    self.templates[name] = template
            
            self.logger.info(f"配置加載成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置加載失敗: {e}")
            return False
    
    # 私有方法
    
    def _validate_template(self, template: ExportTemplate) -> bool:
        """驗證模板"""
        if not template.name:
            self.logger.error("模板名稱不能為空")
            return False
        
        if not template.fields:
            self.logger.error("模板必須包含至少一個字段")
            return False
        
        # 檢查字段名稱重複
        field_names = [f.name for f in template.fields]
        if len(field_names) != len(set(field_names)):
            self.logger.error("模板包含重複的字段名稱")
            return False
        
        return True
    
    def _validate_field_type(self, value: Any, field_type: FieldType) -> bool:
        """驗證字段類型"""
        if value is None:
            return True
        
        try:
            if field_type == FieldType.STRING:
                return isinstance(value, str)
            elif field_type == FieldType.INTEGER:
                return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
            elif field_type == FieldType.FLOAT:
                float(value)
                return True
            elif field_type == FieldType.BOOLEAN:
                return isinstance(value, bool) or str(value).lower() in ['true', 'false', '1', '0']
            elif field_type == FieldType.URL:
                return isinstance(value, str) and (value.startswith('http://') or value.startswith('https://'))
            elif field_type == FieldType.EMAIL:
                return isinstance(value, str) and '@' in value
            else:
                return True
        except:
            return False
    
    def _apply_validation_rule(self, value: Any, rule: str, field: FieldDefinition) -> bool:
        """應用驗證規則"""
        # 簡化的驗證規則實現
        return True
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """獲取嵌套值"""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _format_field_value(self, value: Any, field: FieldDefinition, csv_config: CSVConfig) -> str:
        """格式化字段值"""
        if value is None:
            return csv_config.null_value
        
        if field.field_type == FieldType.DATE and isinstance(value, datetime):
            return value.strftime(csv_config.date_format)
        elif field.field_type == FieldType.DATETIME and isinstance(value, datetime):
            return value.strftime(csv_config.datetime_format)
        elif field.field_type == FieldType.BOOLEAN:
            bool_val = bool(value)
            return csv_config.boolean_format["true" if bool_val else "false"]
        elif field.field_type == FieldType.JSON_ARRAY and isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
        elif field.field_type == FieldType.JSON_OBJECT and isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        else:
            result = str(value)
            
            # 應用長度限制
            if field.max_length and len(result) > field.max_length:
                result = result[:field.max_length-3] + "..."
            
            # 清理空白字符
            if csv_config.trim_whitespace:
                result = result.strip()
            
            return result
    
    def _serialize_template(self, template: ExportTemplate) -> Dict[str, Any]:
        """序列化模板"""
        return {
            'name': template.name,
            'description': template.description,
            'format': template.format.value,
            'variant': template.variant.value if template.variant else None,
            'compression': template.compression.value,
            'file_naming_pattern': template.file_naming_pattern,
            'metadata': template.metadata,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat(),
            'fields': [self._serialize_field(f) for f in template.fields],
            'csv_config': self._serialize_csv_config(template.csv_config) if template.csv_config else None
        }
    
    def _serialize_field(self, field: FieldDefinition) -> Dict[str, Any]:
        """序列化字段"""
        return {
            'name': field.name,
            'display_name': field.display_name,
            'field_type': field.field_type.value,
            'required': field.required,
            'default_value': field.default_value,
            'max_length': field.max_length,
            'format_pattern': field.format_pattern,
            'description': field.description,
            'source_path': field.source_path,
            'transformer': field.transformer,
            'validation_rules': field.validation_rules
        }
    
    def _serialize_csv_config(self, config: CSVConfig) -> Dict[str, Any]:
        """序列化CSV配置"""
        return {
            'delimiter': config.delimiter,
            'quote_char': config.quote_char,
            'escape_char': config.escape_char,
            'line_terminator': config.line_terminator,
            'encoding': config.encoding,
            'include_header': config.include_header,
            'quote_all': config.quote_all,
            'date_format': config.date_format,
            'datetime_format': config.datetime_format,
            'null_value': config.null_value,
            'boolean_format': config.boolean_format,
            'max_field_length': config.max_field_length,
            'trim_whitespace': config.trim_whitespace
        }
    
    def _deserialize_template(self, data: Dict[str, Any]) -> Optional[ExportTemplate]:
        """反序列化模板"""
        try:
            fields = [self._deserialize_field(f) for f in data.get('fields', [])]
            csv_config = None
            if data.get('csv_config'):
                csv_config = self._deserialize_csv_config(data['csv_config'])
            
            return ExportTemplate(
                name=data['name'],
                description=data['description'],
                format=ExportFormat(data['format']),
                variant=CSVVariant(data['variant']) if data.get('variant') else None,
                fields=fields,
                csv_config=csv_config,
                compression=CompressionType(data.get('compression', 'none')),
                file_naming_pattern=data.get('file_naming_pattern', '{timestamp}_{template_name}.{extension}'),
                metadata=data.get('metadata', {}),
                created_at=datetime.fromisoformat(data['created_at']),
                updated_at=datetime.fromisoformat(data['updated_at'])
            )
        except Exception as e:
            self.logger.error(f"反序列化模板失敗: {e}")
            return None
    
    def _deserialize_field(self, data: Dict[str, Any]) -> FieldDefinition:
        """反序列化字段"""
        return FieldDefinition(
            name=data['name'],
            display_name=data['display_name'],
            field_type=FieldType(data['field_type']),
            required=data.get('required', False),
            default_value=data.get('default_value'),
            max_length=data.get('max_length'),
            format_pattern=data.get('format_pattern'),
            description=data.get('description', ''),
            source_path=data.get('source_path'),
            transformer=data.get('transformer'),
            validation_rules=data.get('validation_rules', [])
        )
    
    def _deserialize_csv_config(self, data: Dict[str, Any]) -> CSVConfig:
        """反序列化CSV配置"""
        return CSVConfig(
            delimiter=data.get('delimiter', ','),
            quote_char=data.get('quote_char', '"'),
            escape_char=data.get('escape_char', '\\'),
            line_terminator=data.get('line_terminator', '\n'),
            encoding=data.get('encoding', 'utf-8'),
            include_header=data.get('include_header', True),
            quote_all=data.get('quote_all', False),
            date_format=data.get('date_format', '%Y-%m-%d'),
            datetime_format=data.get('datetime_format', '%Y-%m-%d %H:%M:%S'),
            null_value=data.get('null_value', ''),
            boolean_format=data.get('boolean_format', {'true': 'True', 'false': 'False'}),
            max_field_length=data.get('max_field_length'),
            trim_whitespace=data.get('trim_whitespace', True)
        )
    
    # 轉換器實現
    
    def _format_salary_range(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """格式化薪資範圍"""
        min_sal = data.get('salary_min')
        max_sal = data.get('salary_max')
        currency = data.get('salary_currency', 'AUD')
        
        if min_sal and max_sal:
            return f"{currency} {min_sal:,} - {max_sal:,}"
        elif min_sal:
            return f"{currency} {min_sal:,}+"
        elif max_sal:
            return f"Up to {currency} {max_sal:,}"
        else:
            return "Negotiable"
    
    def _count_skills(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> int:
        """計算技能數量"""
        skills = data.get('skills', [])
        if isinstance(skills, list):
            return len(skills)
        elif isinstance(skills, str):
            return len(skills.split(',')) if skills else 0
        else:
            return 0
    
    def _format_top_skills(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """格式化主要技能"""
        skills = data.get('skills', [])
        if isinstance(skills, list):
            # 假設技能是字典列表，包含名稱和重要性
            if skills and isinstance(skills[0], dict):
                sorted_skills = sorted(skills, key=lambda x: x.get('importance_score', 0), reverse=True)
                return ', '.join([skill.get('skill_name', '') for skill in sorted_skills[:5]])
            else:
                return ', '.join(skills[:5])
        elif isinstance(skills, str):
            skill_list = skills.split(',')
            return ', '.join(skill_list[:5])
        else:
            return ''
    
    def _truncate_description(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """截斷描述"""
        if not value:
            return ''
        
        text = str(value)
        max_length = field.max_length or 500
        
        if len(text) <= max_length:
            return text
        else:
            return text[:max_length-3] + '...'
    
    def _normalize_location(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """標準化位置"""
        if not value:
            return ''
        
        # 簡單的位置標準化
        location = str(value).strip()
        location = re.sub(r'\s+', ' ', location)  # 標準化空白字符
        return location.title()  # 首字母大寫
    
    def _format_boolean(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """格式化布爾值"""
        if value is None:
            return ''
        
        bool_val = bool(value)
        return 'Yes' if bool_val else 'No'
    
    def _format_date(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """格式化日期"""
        if not value:
            return ''
        
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')
        elif isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            except:
                return value
        else:
            return str(value)
    
    def _clean_html(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """清理HTML標籤"""
        if not value:
            return ''
        
        text = str(value)
        # 簡單的HTML標籤移除
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_domain(self, value: Any, field: FieldDefinition, data: Dict[str, Any]) -> str:
        """提取域名"""
        if not value:
            return ''
        
        url = str(value)
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1) if match else url
    
    # 驗證器實現
    
    def _validate_required(self, value: Any, rule: ValidationRule) -> bool:
        """驗證必需字段"""
        return value is not None and value != ''
    
    def _validate_length(self, value: Any, rule: ValidationRule) -> bool:
        """驗證長度"""
        if not isinstance(value, str):
            return True
        
        min_length = rule.parameters.get('min', 0)
        max_length = rule.parameters.get('max', float('inf'))
        
        return min_length <= len(value) <= max_length
    
    def _validate_pattern(self, value: Any, rule: ValidationRule) -> bool:
        """驗證模式"""
        if not isinstance(value, str):
            return True
        
        pattern = rule.parameters.get('pattern')
        if not pattern:
            return True
        
        return bool(re.match(pattern, value))
    
    def _validate_range(self, value: Any, rule: ValidationRule) -> bool:
        """驗證範圍"""
        try:
            num_value = float(value)
            min_val = rule.parameters.get('min', float('-inf'))
            max_val = rule.parameters.get('max', float('inf'))
            return min_val <= num_value <= max_val
        except:
            return False
    
    def _validate_url(self, value: Any, rule: ValidationRule) -> bool:
        """驗證URL"""
        if not isinstance(value, str):
            return False
        
        return value.startswith(('http://', 'https://'))
    
    def _validate_email(self, value: Any, rule: ValidationRule) -> bool:
        """驗證郵箱"""
        if not isinstance(value, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))


def create_enhanced_export_config(config_file: Optional[str] = None) -> EnhancedExportConfig:
    """創建增強導出配置的便捷函數
    
    Args:
        config_file: 配置文件路徑
        
    Returns:
        EnhancedExportConfig: 增強導出配置實例
    """
    return EnhancedExportConfig(config_file)