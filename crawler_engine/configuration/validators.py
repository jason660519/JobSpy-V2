"""配置驗證器模組

提供各種配置項的驗證功能。
"""

import re
from typing import Any, List, Optional, Union
from pathlib import Path
from urllib.parse import urlparse


class ValidationError(Exception):
    """驗證錯誤異常"""
    pass


class ValidationRule:
    """驗證規則基類"""
    
    def __init__(self, name: str, message: str = ""):
        self.name = name
        self.message = message or f"Validation failed for {name}"
    
    def validate(self, value: Any) -> bool:
        """驗證值
        
        Args:
            value: 要驗證的值
            
        Returns:
            bool: 驗證是否通過
        """
        raise NotImplementedError


class URLValidator(ValidationRule):
    """URL驗證器"""
    
    def __init__(self, schemes: Optional[List[str]] = None):
        super().__init__("url", "Invalid URL format")
        self.schemes = schemes or ['http', 'https']
    
    def validate(self, value: Any) -> bool:
        """驗證URL格式
        
        Args:
            value: URL字符串
            
        Returns:
            bool: 是否為有效URL
        """
        if not isinstance(value, str):
            return False
        
        try:
            result = urlparse(value)
            return all([
                result.scheme in self.schemes,
                result.netloc
            ])
        except Exception:
            return False


class EmailValidator(ValidationRule):
    """郵箱驗證器"""
    
    def __init__(self):
        super().__init__("email", "Invalid email format")
        self.pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def validate(self, value: Any) -> bool:
        """驗證郵箱格式
        
        Args:
            value: 郵箱字符串
            
        Returns:
            bool: 是否為有效郵箱
        """
        if not isinstance(value, str):
            return False
        
        return bool(self.pattern.match(value))


class PortValidator(ValidationRule):
    """端口驗證器"""
    
    def __init__(self, min_port: int = 1, max_port: int = 65535):
        super().__init__("port", f"Port must be between {min_port} and {max_port}")
        self.min_port = min_port
        self.max_port = max_port
    
    def validate(self, value: Any) -> bool:
        """驗證端口號
        
        Args:
            value: 端口號
            
        Returns:
            bool: 是否為有效端口
        """
        try:
            port = int(value)
            return self.min_port <= port <= self.max_port
        except (ValueError, TypeError):
            return False


class PathValidator(ValidationRule):
    """路徑驗證器"""
    
    def __init__(self, must_exist: bool = False, must_be_dir: bool = False):
        super().__init__("path", "Invalid path")
        self.must_exist = must_exist
        self.must_be_dir = must_be_dir
    
    def validate(self, value: Any) -> bool:
        """驗證路徑
        
        Args:
            value: 路徑字符串
            
        Returns:
            bool: 是否為有效路徑
        """
        if not isinstance(value, (str, Path)):
            return False
        
        try:
            path = Path(value)
            
            if self.must_exist and not path.exists():
                return False
            
            if self.must_be_dir and path.exists() and not path.is_dir():
                return False
            
            return True
        except Exception:
            return False


class RegexValidator(ValidationRule):
    """正則表達式驗證器"""
    
    def __init__(self, pattern: str, flags: int = 0):
        super().__init__("regex", f"Value does not match pattern: {pattern}")
        self.pattern = re.compile(pattern, flags)
    
    def validate(self, value: Any) -> bool:
        """驗證正則表達式
        
        Args:
            value: 要驗證的字符串
            
        Returns:
            bool: 是否匹配模式
        """
        if not isinstance(value, str):
            return False
        
        return bool(self.pattern.match(value))


class ConfigValidator:
    """配置驗證器"""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> None:
        """添加驗證規則
        
        Args:
            rule: 驗證規則
        """
        self.rules.append(rule)
    
    def validate(self, value: Any) -> List[str]:
        """驗證值
        
        Args:
            value: 要驗證的值
            
        Returns:
            List[str]: 錯誤信息列表
        """
        errors = []
        
        for rule in self.rules:
            try:
                if not rule.validate(value):
                    errors.append(rule.message)
            except Exception as e:
                errors.append(f"Validation error in {rule.name}: {str(e)}")
        
        return errors
    
    def is_valid(self, value: Any) -> bool:
        """檢查值是否有效
        
        Args:
            value: 要驗證的值
            
        Returns:
            bool: 是否有效
        """
        return len(self.validate(value)) == 0