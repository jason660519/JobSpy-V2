"""導出配置模組

定義數據導出相關的配置參數。
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum


class ExportFormat(Enum):
    """導出格式枚舉"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PARQUET = "parquet"


@dataclass
class ExportConfig:
    """導出配置"""
    
    # 基本配置
    output_dir: Path = Path("./exports")
    file_format: ExportFormat = ExportFormat.CSV
    include_headers: bool = True
    
    # 文件命名
    filename_template: str = "{platform}_{timestamp}"
    timestamp_format: str = "%Y%m%d_%H%M%S"
    
    # CSV 特定配置
    csv_delimiter: str = ","
    csv_quotechar: str = '"'
    csv_encoding: str = "utf-8"
    
    # JSON 特定配置
    json_indent: int = 2
    json_ensure_ascii: bool = False
    
    # Excel 特定配置
    excel_sheet_name: str = "Jobs"
    excel_index: bool = False
    
    # 字段配置
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    field_mapping: Optional[Dict[str, str]] = None
    
    # 壓縮配置
    enable_compression: bool = False
    compression_format: str = "gzip"
    
    # 分割配置
    max_rows_per_file: Optional[int] = None
    enable_file_splitting: bool = False
    
    def __post_init__(self):
        """初始化後處理"""
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        
        if isinstance(self.file_format, str):
            self.file_format = ExportFormat(self.file_format)
        
        # 確保輸出目錄存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 設置默認字段映射
        if self.field_mapping is None:
            self.field_mapping = {}
        
        # 設置默認排除字段
        if self.exclude_fields is None:
            self.exclude_fields = ["processing_error", "validation_timestamp"]
    
    def get_file_extension(self) -> str:
        """獲取文件擴展名"""
        extensions = {
            ExportFormat.CSV: ".csv",
            ExportFormat.JSON: ".json",
            ExportFormat.EXCEL: ".xlsx",
            ExportFormat.PARQUET: ".parquet"
        }
        return extensions.get(self.file_format, ".csv")
    
    def generate_filename(self, platform: str, timestamp: str = None) -> str:
        """生成文件名"""
        from datetime import datetime
        
        if timestamp is None:
            timestamp = datetime.now().strftime(self.timestamp_format)
        
        filename = self.filename_template.format(
            platform=platform,
            timestamp=timestamp
        )
        
        return filename + self.get_file_extension()
    
    def get_csv_config(self) -> Dict[str, Any]:
        """獲取 CSV 配置"""
        return {
            "sep": self.csv_delimiter,
            "quotechar": self.csv_quotechar,
            "encoding": self.csv_encoding,
            "index": False,
            "header": self.include_headers
        }
    
    def get_json_config(self) -> Dict[str, Any]:
        """獲取 JSON 配置"""
        return {
            "indent": self.json_indent,
            "ensure_ascii": self.json_ensure_ascii,
            "orient": "records"
        }
    
    def get_excel_config(self) -> Dict[str, Any]:
        """獲取 Excel 配置"""
        return {
            "sheet_name": self.excel_sheet_name,
            "index": self.excel_index,
            "header": self.include_headers
        }