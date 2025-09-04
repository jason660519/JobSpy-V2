"""配置驗證器

提供配置數據的驗證規則、檢查機制和自動修復功能。
"""

import re
import json
from typing import Dict, Any, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import ipaddress
from urllib.parse import urlparse
import structlog
from datetime import datetime
import threading

logger = structlog.get_logger(__name__)


class ValidationType(Enum):
    """驗證類型"""
    REQUIRED = "required"
    TYPE = "type"
    RANGE = "range"
    PATTERN = "pattern"
    ENUM = "enum"
    LENGTH = "length"
    URL = "url"
    EMAIL = "email"
    IP = "ip"
    PORT = "port"
    PATH = "path"
    CUSTOM = "custom"


class ValidationLevel(Enum):
    """驗證級別"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """驗證結果"""
    valid: bool
    level: ValidationLevel
    message: str
    field_path: str
    value: Any = None
    expected: Any = None
    suggestion: Optional[str] = None
    auto_fix: Optional[Any] = None
    
    def __str__(self) -> str:
        return f"[{self.level.value.upper()}] {self.field_path}: {self.message}"


@dataclass
class ValidationRule:
    """驗證規則"""
    name: str
    validation_type: ValidationType
    level: ValidationLevel = ValidationLevel.ERROR
    message: str = ""
    
    # 類型驗證
    expected_type: Optional[Type] = None
    
    # 範圍驗證
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    
    # 長度驗證
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    # 模式驗證
    pattern: Optional[str] = None
    
    # 枚舉驗證
    allowed_values: Optional[List[Any]] = None
    
    # 自定義驗證
    custom_validator: Optional[Callable[[Any], bool]] = None
    
    # 自動修復
    auto_fix_enabled: bool = False
    auto_fix_function: Optional[Callable[[Any], Any]] = None
    
    def __post_init__(self):
        if not self.message:
            self.message = self._generate_default_message()
    
    def _generate_default_message(self) -> str:
        """生成默認錯誤消息"""
        if self.validation_type == ValidationType.REQUIRED:
            return "Field is required"
        elif self.validation_type == ValidationType.TYPE:
            return f"Expected type {self.expected_type.__name__ if self.expected_type else 'unknown'}"
        elif self.validation_type == ValidationType.RANGE:
            return f"Value must be between {self.min_value} and {self.max_value}"
        elif self.validation_type == ValidationType.LENGTH:
            return f"Length must be between {self.min_length} and {self.max_length}"
        elif self.validation_type == ValidationType.PATTERN:
            return f"Value must match pattern: {self.pattern}"
        elif self.validation_type == ValidationType.ENUM:
            return f"Value must be one of: {self.allowed_values}"
        elif self.validation_type == ValidationType.URL:
            return "Value must be a valid URL"
        elif self.validation_type == ValidationType.EMAIL:
            return "Value must be a valid email address"
        elif self.validation_type == ValidationType.IP:
            return "Value must be a valid IP address"
        elif self.validation_type == ValidationType.PORT:
            return "Value must be a valid port number (1-65535)"
        elif self.validation_type == ValidationType.PATH:
            return "Value must be a valid file path"
        else:
            return "Validation failed"


@dataclass
class ValidationSchema:
    """驗證模式"""
    name: str
    description: str = ""
    rules: Dict[str, List[ValidationRule]] = field(default_factory=dict)
    nested_schemas: Dict[str, 'ValidationSchema'] = field(default_factory=dict)
    
    def add_rule(self, field_path: str, rule: ValidationRule) -> None:
        """添加驗證規則
        
        Args:
            field_path: 字段路徑（支持點號分隔的嵌套路徑）
            rule: 驗證規則
        """
        if field_path not in self.rules:
            self.rules[field_path] = []
        self.rules[field_path].append(rule)
    
    def add_nested_schema(self, field_path: str, schema: 'ValidationSchema') -> None:
        """添加嵌套模式
        
        Args:
            field_path: 字段路徑
            schema: 嵌套模式
        """
        self.nested_schemas[field_path] = schema
    
    def get_rules(self, field_path: str) -> List[ValidationRule]:
        """獲取字段的驗證規則
        
        Args:
            field_path: 字段路徑
            
        Returns:
            List[ValidationRule]: 驗證規則列表
        """
        return self.rules.get(field_path, [])


class ConfigValidator:
    """配置驗證器
    
    提供配置數據的驗證、自動修復和建議功能。
    """
    
    def __init__(self):
        self.logger = logger.bind(component="ConfigValidator")
        
        # 驗證模式
        self._schemas: Dict[str, ValidationSchema] = {}
        
        # 內置驗證器
        self._builtin_validators = {
            ValidationType.URL: self._validate_url,
            ValidationType.EMAIL: self._validate_email,
            ValidationType.IP: self._validate_ip,
            ValidationType.PORT: self._validate_port,
            ValidationType.PATH: self._validate_path
        }
        
        # 線程鎖
        self._lock = threading.RLock()
        
        # 初始化內置模式
        self._init_builtin_schemas()
    
    def _init_builtin_schemas(self) -> None:
        """初始化內置驗證模式"""
        # 數據庫配置模式
        db_schema = ValidationSchema(
            name="database",
            description="Database configuration validation"
        )
        
        # 數據庫URL
        db_schema.add_rule("url", ValidationRule(
            name="db_url_required",
            validation_type=ValidationType.REQUIRED,
            message="Database URL is required"
        ))
        
        db_schema.add_rule("url", ValidationRule(
            name="db_url_format",
            validation_type=ValidationType.URL,
            message="Database URL must be valid"
        ))
        
        # 連接池大小
        db_schema.add_rule("pool_size", ValidationRule(
            name="pool_size_range",
            validation_type=ValidationType.RANGE,
            min_value=1,
            max_value=100,
            level=ValidationLevel.WARNING,
            message="Pool size should be between 1 and 100"
        ))
        
        self.register_schema(db_schema)
        
        # API配置模式
        api_schema = ValidationSchema(
            name="api",
            description="API configuration validation"
        )
        
        # API密鑰
        api_schema.add_rule("key", ValidationRule(
            name="api_key_required",
            validation_type=ValidationType.REQUIRED,
            message="API key is required"
        ))
        
        api_schema.add_rule("key", ValidationRule(
            name="api_key_length",
            validation_type=ValidationType.LENGTH,
            min_length=10,
            level=ValidationLevel.WARNING,
            message="API key should be at least 10 characters"
        ))
        
        # 超時設置
        api_schema.add_rule("timeout", ValidationRule(
            name="timeout_range",
            validation_type=ValidationType.RANGE,
            min_value=1,
            max_value=300,
            level=ValidationLevel.WARNING,
            message="Timeout should be between 1 and 300 seconds"
        ))
        
        # 重試次數
        api_schema.add_rule("max_retries", ValidationRule(
            name="retries_range",
            validation_type=ValidationType.RANGE,
            min_value=0,
            max_value=10,
            level=ValidationLevel.WARNING,
            message="Max retries should be between 0 and 10"
        ))
        
        self.register_schema(api_schema)
        
        # 爬蟲配置模式
        crawler_schema = ValidationSchema(
            name="crawler",
            description="Crawler configuration validation"
        )
        
        # 並發數
        crawler_schema.add_rule("max_concurrent", ValidationRule(
            name="concurrent_range",
            validation_type=ValidationType.RANGE,
            min_value=1,
            max_value=50,
            level=ValidationLevel.WARNING,
            message="Max concurrent should be between 1 and 50"
        ))
        
        # 延遲設置
        crawler_schema.add_rule("delay", ValidationRule(
            name="delay_range",
            validation_type=ValidationType.RANGE,
            min_value=0,
            max_value=60,
            level=ValidationLevel.WARNING,
            message="Delay should be between 0 and 60 seconds"
        ))
        
        # User-Agent
        crawler_schema.add_rule("user_agent", ValidationRule(
            name="user_agent_length",
            validation_type=ValidationType.LENGTH,
            min_length=10,
            level=ValidationLevel.WARNING,
            message="User agent should be at least 10 characters"
        ))
        
        self.register_schema(crawler_schema)
    
    def register_schema(self, schema: ValidationSchema) -> None:
        """註冊驗證模式
        
        Args:
            schema: 驗證模式
        """
        with self._lock:
            self._schemas[schema.name] = schema
            
            self.logger.info(
                "註冊驗證模式",
                name=schema.name,
                rules_count=len(schema.rules),
                nested_count=len(schema.nested_schemas)
            )
    
    def get_schema(self, name: str) -> Optional[ValidationSchema]:
        """獲取驗證模式
        
        Args:
            name: 模式名稱
            
        Returns:
            Optional[ValidationSchema]: 驗證模式
        """
        return self._schemas.get(name)
    
    def validate(self, 
                data: Dict[str, Any],
                schema_name: Optional[str] = None,
                schema: Optional[ValidationSchema] = None) -> List[ValidationResult]:
        """驗證配置數據
        
        Args:
            data: 配置數據
            schema_name: 模式名稱
            schema: 驗證模式（優先於schema_name）
            
        Returns:
            List[ValidationResult]: 驗證結果列表
        """
        if schema is None:
            if schema_name:
                schema = self.get_schema(schema_name)
                if not schema:
                    return [ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        message=f"Schema '{schema_name}' not found",
                        field_path="_schema"
                    )]
            else:
                return [ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    message="No schema provided for validation",
                    field_path="_schema"
                )]
        
        results = []
        
        # 驗證規則
        for field_path, rules in schema.rules.items():
            field_value = self._get_nested_value(data, field_path)
            
            for rule in rules:
                result = self._validate_rule(field_path, field_value, rule)
                if result:
                    results.append(result)
        
        # 驗證嵌套模式
        for field_path, nested_schema in schema.nested_schemas.items():
            nested_data = self._get_nested_value(data, field_path)
            if isinstance(nested_data, dict):
                nested_results = self.validate(nested_data, schema=nested_schema)
                # 更新字段路徑
                for result in nested_results:
                    result.field_path = f"{field_path}.{result.field_path}"
                results.extend(nested_results)
        
        self.logger.debug(
            "配置驗證完成",
            schema=schema.name,
            total_results=len(results),
            errors=len([r for r in results if r.level == ValidationLevel.ERROR]),
            warnings=len([r for r in results if r.level == ValidationLevel.WARNING])
        )
        
        return results
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """獲取嵌套字段值
        
        Args:
            data: 數據字典
            field_path: 字段路徑（點號分隔）
            
        Returns:
            Any: 字段值
        """
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _validate_rule(self, 
                      field_path: str,
                      value: Any,
                      rule: ValidationRule) -> Optional[ValidationResult]:
        """驗證單個規則
        
        Args:
            field_path: 字段路徑
            value: 字段值
            rule: 驗證規則
            
        Returns:
            Optional[ValidationResult]: 驗證結果
        """
        try:
            # 必需字段驗證
            if rule.validation_type == ValidationType.REQUIRED:
                if value is None or value == "":
                    return ValidationResult(
                        valid=False,
                        level=rule.level,
                        message=rule.message,
                        field_path=field_path,
                        value=value
                    )
            
            # 如果值為空且不是必需字段，跳過其他驗證
            if value is None or value == "":
                return None
            
            # 類型驗證
            if rule.validation_type == ValidationType.TYPE:
                if rule.expected_type and not isinstance(value, rule.expected_type):
                    auto_fix = None
                    if rule.auto_fix_enabled:
                        try:
                            auto_fix = rule.expected_type(value)
                        except (ValueError, TypeError):
                            pass
                    
                    return ValidationResult(
                        valid=False,
                        level=rule.level,
                        message=rule.message,
                        field_path=field_path,
                        value=value,
                        expected=rule.expected_type,
                        auto_fix=auto_fix
                    )
            
            # 範圍驗證
            elif rule.validation_type == ValidationType.RANGE:
                if isinstance(value, (int, float)):
                    if rule.min_value is not None and value < rule.min_value:
                        return ValidationResult(
                            valid=False,
                            level=rule.level,
                            message=rule.message,
                            field_path=field_path,
                            value=value,
                            expected=f">= {rule.min_value}",
                            auto_fix=rule.min_value if rule.auto_fix_enabled else None
                        )
                    
                    if rule.max_value is not None and value > rule.max_value:
                        return ValidationResult(
                            valid=False,
                            level=rule.level,
                            message=rule.message,
                            field_path=field_path,
                            value=value,
                            expected=f"<= {rule.max_value}",
                            auto_fix=rule.max_value if rule.auto_fix_enabled else None
                        )
            
            # 長度驗證
            elif rule.validation_type == ValidationType.LENGTH:
                if hasattr(value, '__len__'):
                    length = len(value)
                    if rule.min_length is not None and length < rule.min_length:
                        return ValidationResult(
                            valid=False,
                            level=rule.level,
                            message=rule.message,
                            field_path=field_path,
                            value=value,
                            expected=f"length >= {rule.min_length}"
                        )
                    
                    if rule.max_length is not None and length > rule.max_length:
                        auto_fix = None
                        if rule.auto_fix_enabled and isinstance(value, str):
                            auto_fix = value[:rule.max_length]
                        
                        return ValidationResult(
                            valid=False,
                            level=rule.level,
                            message=rule.message,
                            field_path=field_path,
                            value=value,
                            expected=f"length <= {rule.max_length}",
                            auto_fix=auto_fix
                        )
            
            # 模式驗證
            elif rule.validation_type == ValidationType.PATTERN:
                if rule.pattern and isinstance(value, str):
                    if not re.match(rule.pattern, value):
                        return ValidationResult(
                            valid=False,
                            level=rule.level,
                            message=rule.message,
                            field_path=field_path,
                            value=value,
                            expected=f"pattern: {rule.pattern}"
                        )
            
            # 枚舉驗證
            elif rule.validation_type == ValidationType.ENUM:
                if rule.allowed_values and value not in rule.allowed_values:
                    return ValidationResult(
                        valid=False,
                        level=rule.level,
                        message=rule.message,
                        field_path=field_path,
                        value=value,
                        expected=rule.allowed_values
                    )
            
            # 內置驗證器
            elif rule.validation_type in self._builtin_validators:
                validator = self._builtin_validators[rule.validation_type]
                if not validator(value):
                    return ValidationResult(
                        valid=False,
                        level=rule.level,
                        message=rule.message,
                        field_path=field_path,
                        value=value
                    )
            
            # 自定義驗證
            elif rule.validation_type == ValidationType.CUSTOM:
                if rule.custom_validator and not rule.custom_validator(value):
                    auto_fix = None
                    if rule.auto_fix_enabled and rule.auto_fix_function:
                        try:
                            auto_fix = rule.auto_fix_function(value)
                        except Exception:
                            pass
                    
                    return ValidationResult(
                        valid=False,
                        level=rule.level,
                        message=rule.message,
                        field_path=field_path,
                        value=value,
                        auto_fix=auto_fix
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(
                "驗證規則執行失敗",
                field_path=field_path,
                rule_name=rule.name,
                error=str(e)
            )
            
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"Validation error: {str(e)}",
                field_path=field_path,
                value=value
            )
    
    def _validate_url(self, value: Any) -> bool:
        """驗證URL格式"""
        if not isinstance(value, str):
            return False
        
        try:
            result = urlparse(value)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _validate_email(self, value: Any) -> bool:
        """驗證郵箱格式"""
        if not isinstance(value, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, value) is not None
    
    def _validate_ip(self, value: Any) -> bool:
        """驗證IP地址格式"""
        if not isinstance(value, str):
            return False
        
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    
    def _validate_port(self, value: Any) -> bool:
        """驗證端口號"""
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        
        return isinstance(value, int) and 1 <= value <= 65535
    
    def _validate_path(self, value: Any) -> bool:
        """驗證文件路徑"""
        if not isinstance(value, str):
            return False
        
        try:
            Path(value)
            return True
        except Exception:
            return False
    
    def auto_fix(self, 
                data: Dict[str, Any],
                results: List[ValidationResult]) -> Dict[str, Any]:
        """自動修復配置數據
        
        Args:
            data: 原始數據
            results: 驗證結果
            
        Returns:
            Dict[str, Any]: 修復後的數據
        """
        fixed_data = data.copy()
        fixed_count = 0
        
        for result in results:
            if result.auto_fix is not None:
                self._set_nested_value(fixed_data, result.field_path, result.auto_fix)
                fixed_count += 1
                
                self.logger.info(
                    "自動修復字段",
                    field_path=result.field_path,
                    old_value=result.value,
                    new_value=result.auto_fix
                )
        
        self.logger.info(
            "自動修復完成",
            fixed_count=fixed_count,
            total_issues=len(results)
        )
        
        return fixed_data
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any) -> None:
        """設置嵌套字段值
        
        Args:
            data: 數據字典
            field_path: 字段路徑（點號分隔）
            value: 字段值
        """
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def generate_report(self, results: List[ValidationResult]) -> str:
        """生成驗證報告
        
        Args:
            results: 驗證結果
            
        Returns:
            str: 驗證報告
        """
        if not results:
            return "✅ All validations passed!"
        
        errors = [r for r in results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in results if r.level == ValidationLevel.WARNING]
        infos = [r for r in results if r.level == ValidationLevel.INFO]
        
        report = []
        report.append("📋 Configuration Validation Report")
        report.append("=" * 40)
        report.append(f"Total Issues: {len(results)}")
        report.append(f"Errors: {len(errors)}")
        report.append(f"Warnings: {len(warnings)}")
        report.append(f"Info: {len(infos)}")
        report.append("")
        
        if errors:
            report.append("❌ ERRORS:")
            for result in errors:
                report.append(f"  • {result}")
                if result.suggestion:
                    report.append(f"    💡 Suggestion: {result.suggestion}")
            report.append("")
        
        if warnings:
            report.append("⚠️  WARNINGS:")
            for result in warnings:
                report.append(f"  • {result}")
                if result.suggestion:
                    report.append(f"    💡 Suggestion: {result.suggestion}")
            report.append("")
        
        if infos:
            report.append("ℹ️  INFO:")
            for result in infos:
                report.append(f"  • {result}")
            report.append("")
        
        # 自動修復建議
        auto_fixable = [r for r in results if r.auto_fix is not None]
        if auto_fixable:
            report.append("🔧 Auto-fixable Issues:")
            for result in auto_fixable:
                report.append(f"  • {result.field_path}: {result.value} → {result.auto_fix}")
            report.append("")
        
        return "\n".join(report)
    
    def create_rule_builder(self) -> 'ValidationRuleBuilder':
        """創建規則構建器
        
        Returns:
            ValidationRuleBuilder: 規則構建器
        """
        return ValidationRuleBuilder()
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        total_rules = 0
        total_nested = 0
        
        for schema in self._schemas.values():
            total_rules += sum(len(rules) for rules in schema.rules.values())
            total_nested += len(schema.nested_schemas)
        
        return {
            'total_schemas': len(self._schemas),
            'total_rules': total_rules,
            'total_nested_schemas': total_nested,
            'builtin_validators': len(self._builtin_validators),
            'schemas': {
                name: {
                    'rules_count': sum(len(rules) for rules in schema.rules.values()),
                    'nested_count': len(schema.nested_schemas)
                }
                for name, schema in self._schemas.items()
            }
        }


class ValidationRuleBuilder:
    """驗證規則構建器
    
    提供流暢的API來構建驗證規則。
    """
    
    def __init__(self):
        self._rule = ValidationRule(
            name="",
            validation_type=ValidationType.REQUIRED
        )
    
    def name(self, name: str) -> 'ValidationRuleBuilder':
        """設置規則名稱"""
        self._rule.name = name
        return self
    
    def required(self, message: str = "") -> 'ValidationRuleBuilder':
        """設置為必需字段"""
        self._rule.validation_type = ValidationType.REQUIRED
        if message:
            self._rule.message = message
        return self
    
    def type_check(self, expected_type: Type, message: str = "") -> 'ValidationRuleBuilder':
        """設置類型檢查"""
        self._rule.validation_type = ValidationType.TYPE
        self._rule.expected_type = expected_type
        if message:
            self._rule.message = message
        return self
    
    def range_check(self, min_val: Union[int, float] = None, 
                   max_val: Union[int, float] = None,
                   message: str = "") -> 'ValidationRuleBuilder':
        """設置範圍檢查"""
        self._rule.validation_type = ValidationType.RANGE
        self._rule.min_value = min_val
        self._rule.max_value = max_val
        if message:
            self._rule.message = message
        return self
    
    def length_check(self, min_len: int = None, 
                    max_len: int = None,
                    message: str = "") -> 'ValidationRuleBuilder':
        """設置長度檢查"""
        self._rule.validation_type = ValidationType.LENGTH
        self._rule.min_length = min_len
        self._rule.max_length = max_len
        if message:
            self._rule.message = message
        return self
    
    def pattern_check(self, pattern: str, message: str = "") -> 'ValidationRuleBuilder':
        """設置模式檢查"""
        self._rule.validation_type = ValidationType.PATTERN
        self._rule.pattern = pattern
        if message:
            self._rule.message = message
        return self
    
    def enum_check(self, allowed_values: List[Any], message: str = "") -> 'ValidationRuleBuilder':
        """設置枚舉檢查"""
        self._rule.validation_type = ValidationType.ENUM
        self._rule.allowed_values = allowed_values
        if message:
            self._rule.message = message
        return self
    
    def url_check(self, message: str = "") -> 'ValidationRuleBuilder':
        """設置URL檢查"""
        self._rule.validation_type = ValidationType.URL
        if message:
            self._rule.message = message
        return self
    
    def email_check(self, message: str = "") -> 'ValidationRuleBuilder':
        """設置郵箱檢查"""
        self._rule.validation_type = ValidationType.EMAIL
        if message:
            self._rule.message = message
        return self
    
    def custom_check(self, validator: Callable[[Any], bool], 
                    message: str = "") -> 'ValidationRuleBuilder':
        """設置自定義檢查"""
        self._rule.validation_type = ValidationType.CUSTOM
        self._rule.custom_validator = validator
        if message:
            self._rule.message = message
        return self
    
    def level(self, level: ValidationLevel) -> 'ValidationRuleBuilder':
        """設置驗證級別"""
        self._rule.level = level
        return self
    
    def auto_fix(self, fix_function: Callable[[Any], Any] = None) -> 'ValidationRuleBuilder':
        """啟用自動修復"""
        self._rule.auto_fix_enabled = True
        if fix_function:
            self._rule.auto_fix_function = fix_function
        return self
    
    def build(self) -> ValidationRule:
        """構建驗證規則"""
        if not self._rule.name:
            self._rule.name = f"{self._rule.validation_type.value}_rule"
        
        return self._rule