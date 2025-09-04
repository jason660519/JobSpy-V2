#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量格式轉換工具

提供舊數據到新格式的批量遷移功能，包括：
- CSV格式轉換
- 數據清理和標準化
- 批量處理和進度追蹤
- 錯誤處理和報告
- 格式驗證和質量檢查
"""

import os
import csv
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from tqdm import tqdm

# 導入我們創建的模組
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawler_engine.data.legacy_exporter import LegacyCSVExporter, LegacyFormat
from crawler_engine.data.field_mapper import FieldMapper, MappingDirection
from crawler_engine.data.enhanced_cleaner import EnhancedDataCleaner, CleaningConfig
from crawler_engine.configuration.enhanced_export_config import (
    EnhancedExportConfig, ExportTemplate, CSVVariant, CompressionType
)


@dataclass
class MigrationConfig:
    """遷移配置"""
    source_format: str = "legacy_v1"  # 源格式
    target_format: str = "standard"   # 目標格式
    batch_size: int = 1000           # 批處理大小
    max_workers: int = 4             # 最大工作線程數
    enable_cleaning: bool = True     # 是否啟用數據清理
    enable_validation: bool = True   # 是否啟用驗證
    skip_errors: bool = True         # 是否跳過錯誤記錄
    output_directory: str = "./migrated_data"  # 輸出目錄
    backup_original: bool = True     # 是否備份原始文件
    compression: CompressionType = CompressionType.NONE  # 壓縮類型
    preserve_metadata: bool = True   # 是否保留元數據
    generate_report: bool = True     # 是否生成報告


@dataclass
class MigrationStats:
    """遷移統計"""
    total_files: int = 0
    processed_files: int = 0
    total_records: int = 0
    processed_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    cleaned_records: int = 0
    validation_errors: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FileProcessingResult:
    """文件處理結果"""
    source_file: str
    target_file: str
    success: bool
    records_processed: int
    records_successful: int
    records_failed: int
    processing_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MigrationTool:
    """批量格式轉換工具
    
    提供舊數據到新格式的批量遷移功能。
    """
    
    def __init__(self, config: MigrationConfig):
        """初始化遷移工具
        
        Args:
            config: 遷移配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stats = MigrationStats()
        
        # 初始化組件
        self.export_config = EnhancedExportConfig()
        self.field_mapper = FieldMapper()
        self.data_cleaner = EnhancedDataCleaner(CleaningConfig()) if config.enable_cleaning else None
        self.legacy_exporter = LegacyCSVExporter()
        
        # 創建輸出目錄
        Path(config.output_directory).mkdir(parents=True, exist_ok=True)
        
        # 設置日誌
        self._setup_logging()
    
    def _setup_logging(self):
        """設置日誌"""
        log_file = Path(self.config.output_directory) / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # 創建文件處理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 創建控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 設置格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加處理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
    
    def migrate_file(self, source_file: str, target_file: Optional[str] = None) -> FileProcessingResult:
        """遷移單個文件
        
        Args:
            source_file: 源文件路徑
            target_file: 目標文件路徑（可選）
            
        Returns:
            FileProcessingResult: 處理結果
        """
        start_time = datetime.now()
        
        # 生成目標文件名
        if not target_file:
            source_path = Path(source_file)
            target_file = str(Path(self.config.output_directory) / 
                            f"{source_path.stem}_migrated{source_path.suffix}")
        
        result = FileProcessingResult(
            source_file=source_file,
            target_file=target_file,
            success=False,
            records_processed=0,
            records_successful=0,
            records_failed=0,
            processing_time=0.0
        )
        
        try:
            # 備份原始文件
            if self.config.backup_original:
                self._backup_file(source_file)
            
            # 讀取源數據
            source_data = self._read_source_file(source_file)
            result.records_processed = len(source_data)
            
            # 處理數據
            processed_data = []
            for i, record in enumerate(source_data):
                try:
                    # 字段映射
                    mapped_record = self._map_fields(record)
                    
                    # 數據清理
                    if self.data_cleaner:
                        cleaned_record = self._clean_record(mapped_record)
                    else:
                        cleaned_record = mapped_record
                    
                    # 驗證數據
                    if self.config.enable_validation:
                        is_valid, validation_errors = self._validate_record(cleaned_record)
                        if not is_valid:
                            if self.config.skip_errors:
                                result.warnings.append(f"記錄 {i+1} 驗證失敗: {validation_errors}")
                                continue
                            else:
                                raise ValueError(f"記錄 {i+1} 驗證失敗: {validation_errors}")
                    
                    processed_data.append(cleaned_record)
                    result.records_successful += 1
                    
                except Exception as e:
                    result.records_failed += 1
                    error_msg = f"處理記錄 {i+1} 失敗: {str(e)}"
                    
                    if self.config.skip_errors:
                        result.errors.append(error_msg)
                        self.logger.warning(error_msg)
                    else:
                        raise Exception(error_msg)
            
            # 寫入目標文件
            self._write_target_file(processed_data, target_file)
            
            result.success = True
            self.logger.info(f"文件遷移成功: {source_file} -> {target_file}")
            
        except Exception as e:
            result.errors.append(str(e))
            self.logger.error(f"文件遷移失敗: {source_file} - {str(e)}")
        
        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def migrate_directory(self, source_directory: str, 
                         file_pattern: str = "*.csv") -> List[FileProcessingResult]:
        """遷移目錄中的所有文件
        
        Args:
            source_directory: 源目錄路徑
            file_pattern: 文件模式
            
        Returns:
            List[FileProcessingResult]: 處理結果列表
        """
        source_path = Path(source_directory)
        if not source_path.exists():
            raise ValueError(f"源目錄不存在: {source_directory}")
        
        # 查找匹配的文件
        source_files = list(source_path.glob(file_pattern))
        self.stats.total_files = len(source_files)
        
        if not source_files:
            self.logger.warning(f"在目錄 {source_directory} 中未找到匹配文件: {file_pattern}")
            return []
        
        self.logger.info(f"找到 {len(source_files)} 個文件待遷移")
        
        # 批量處理文件
        results = []
        
        if self.config.max_workers > 1:
            # 並行處理
            results = self._migrate_files_parallel(source_files)
        else:
            # 串行處理
            results = self._migrate_files_sequential(source_files)
        
        return results
    
    def migrate_batch(self, file_list: List[str]) -> List[FileProcessingResult]:
        """批量遷移文件列表
        
        Args:
            file_list: 文件路徑列表
            
        Returns:
            List[FileProcessingResult]: 處理結果列表
        """
        self.stats.total_files = len(file_list)
        
        if self.config.max_workers > 1:
            return self._migrate_files_parallel(file_list)
        else:
            return self._migrate_files_sequential(file_list)
    
    def _migrate_files_sequential(self, file_list: List[str]) -> List[FileProcessingResult]:
        """串行遷移文件"""
        results = []
        
        with tqdm(total=len(file_list), desc="遷移文件") as pbar:
            for file_path in file_list:
                result = self.migrate_file(str(file_path))
                results.append(result)
                self._update_stats(result)
                pbar.update(1)
                pbar.set_postfix({
                    '成功': self.stats.successful_records,
                    '失敗': self.stats.failed_records
                })
        
        return results
    
    def _migrate_files_parallel(self, file_list: List[str]) -> List[FileProcessingResult]:
        """並行遷移文件"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交任務
            future_to_file = {executor.submit(self.migrate_file, str(file_path)): file_path 
                            for file_path in file_list}
            
            # 處理結果
            with tqdm(total=len(file_list), desc="遷移文件") as pbar:
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                        self._update_stats(result)
                    except Exception as e:
                        self.logger.error(f"處理文件 {file_path} 時發生異常: {e}")
                        # 創建失敗結果
                        result = FileProcessingResult(
                            source_file=str(file_path),
                            target_file="",
                            success=False,
                            records_processed=0,
                            records_successful=0,
                            records_failed=0,
                            processing_time=0.0,
                            errors=[str(e)]
                        )
                        results.append(result)
                    
                    pbar.update(1)
                    pbar.set_postfix({
                        '成功': self.stats.successful_records,
                        '失敗': self.stats.failed_records
                    })
        
        return results
    
    def _read_source_file(self, file_path: str) -> List[Dict[str, Any]]:
        """讀取源文件"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.csv':
            return self._read_csv_file(file_path)
        elif file_ext == '.json':
            return self._read_json_file(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return self._read_excel_file(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def _read_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """讀取CSV文件"""
        data = []
        
        # 嘗試不同的編碼
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, newline='') as f:
                    # 檢測分隔符
                    sample = f.read(1024)
                    f.seek(0)
                    
                    delimiter = ','
                    if sample.count(';') > sample.count(','):
                        delimiter = ';'
                    elif sample.count('\t') > sample.count(','):
                        delimiter = '\t'
                    
                    reader = csv.DictReader(f, delimiter=delimiter)
                    data = list(reader)
                    break
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.warning(f"使用編碼 {encoding} 讀取文件失敗: {e}")
                continue
        
        if not data:
            raise ValueError(f"無法讀取CSV文件: {file_path}")
        
        return data
    
    def _read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """讀取JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            raise ValueError(f"不支持的JSON格式: {type(data)}")
    
    def _read_excel_file(self, file_path: str) -> List[Dict[str, Any]]:
        """讀取Excel文件"""
        df = pd.read_excel(file_path)
        return df.to_dict('records')
    
    def _write_target_file(self, data: List[Dict[str, Any]], file_path: str):
        """寫入目標文件"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.csv':
            self._write_csv_file(data, file_path)
        elif file_ext == '.json':
            self._write_json_file(data, file_path)
        elif file_ext in ['.xlsx', '.xls']:
            self._write_excel_file(data, file_path)
        else:
            raise ValueError(f"不支持的輸出格式: {file_ext}")
    
    def _write_csv_file(self, data: List[Dict[str, Any]], file_path: str):
        """寫入CSV文件"""
        if not data:
            return
        
        # 獲取目標模板配置
        template = self.export_config.get_template(self.config.target_format)
        if not template or not template.csv_config:
            # 使用默認配置
            delimiter = ','
            encoding = 'utf-8'
            include_header = True
        else:
            csv_config = template.csv_config
            delimiter = csv_config.delimiter
            encoding = csv_config.encoding
            include_header = csv_config.include_header
        
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            if data:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                
                if include_header:
                    writer.writeheader()
                
                writer.writerows(data)
    
    def _write_json_file(self, data: List[Dict[str, Any]], file_path: str):
        """寫入JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _write_excel_file(self, data: List[Dict[str, Any]], file_path: str):
        """寫入Excel文件"""
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
    
    def _map_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """映射字段"""
        # 根據配置選擇映射方向
        if self.config.source_format == "legacy_v1" and self.config.target_format == "standard":
            return self.field_mapper.convert_legacy_to_new(record)
        elif self.config.source_format == "standard" and self.config.target_format == "legacy_v1":
            return self.field_mapper.convert_new_to_legacy(record)
        else:
            # 使用通用映射
            return self.field_mapper.apply_custom_mapping(record, {})
    
    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """清理記錄"""
        if not self.data_cleaner:
            return record
        
        try:
            cleaning_result = self.data_cleaner.clean_job_data(record)
            if cleaning_result.success:
                return cleaning_result.cleaned_data
            else:
                self.logger.warning(f"數據清理失敗: {cleaning_result.errors}")
                return record
        except Exception as e:
            self.logger.warning(f"數據清理異常: {e}")
            return record
    
    def _validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """驗證記錄"""
        try:
            is_valid, errors = self.export_config.validate_data(record, self.config.target_format)
            return is_valid, errors
        except Exception as e:
            return False, [str(e)]
    
    def _backup_file(self, file_path: str):
        """備份文件"""
        try:
            source_path = Path(file_path)
            backup_dir = Path(self.config.output_directory) / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{source_path.stem}_{timestamp}{source_path.suffix}"
            
            import shutil
            shutil.copy2(file_path, backup_path)
            
            self.logger.info(f"文件備份成功: {file_path} -> {backup_path}")
            
        except Exception as e:
            self.logger.warning(f"文件備份失敗: {e}")
    
    def _update_stats(self, result: FileProcessingResult):
        """更新統計信息"""
        self.stats.processed_files += 1
        self.stats.total_records += result.records_processed
        self.stats.processed_records += result.records_processed
        self.stats.successful_records += result.records_successful
        self.stats.failed_records += result.records_failed
        
        if result.errors:
            for error in result.errors:
                self.stats.errors.append({
                    'file': result.source_file,
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })
        
        if result.warnings:
            for warning in result.warnings:
                self.stats.warnings.append({
                    'file': result.source_file,
                    'warning': warning,
                    'timestamp': datetime.now().isoformat()
                })
    
    def generate_report(self, results: List[FileProcessingResult]) -> str:
        """生成遷移報告"""
        if not self.config.generate_report:
            return ""
        
        self.stats.end_time = datetime.now()
        
        # 計算總處理時間
        if self.stats.start_time:
            total_time = (self.stats.end_time - self.stats.start_time).total_seconds()
        else:
            total_time = sum(r.processing_time for r in results)
        
        # 生成報告內容
        report_lines = [
            "# 數據遷移報告",
            f"\n## 基本信息",
            f"- 開始時間: {self.stats.start_time or '未知'}",
            f"- 結束時間: {self.stats.end_time}",
            f"- 總處理時間: {total_time:.2f} 秒",
            f"- 源格式: {self.config.source_format}",
            f"- 目標格式: {self.config.target_format}",
            f"\n## 處理統計",
            f"- 總文件數: {self.stats.total_files}",
            f"- 已處理文件: {self.stats.processed_files}",
            f"- 成功文件: {sum(1 for r in results if r.success)}",
            f"- 失敗文件: {sum(1 for r in results if not r.success)}",
            f"- 總記錄數: {self.stats.total_records}",
            f"- 成功記錄: {self.stats.successful_records}",
            f"- 失敗記錄: {self.stats.failed_records}",
            f"- 成功率: {(self.stats.successful_records / max(self.stats.total_records, 1) * 100):.2f}%"
        ]
        
        # 添加錯誤信息
        if self.stats.errors:
            report_lines.append(f"\n## 錯誤信息 ({len(self.stats.errors)} 個)")
            for i, error in enumerate(self.stats.errors[:10], 1):  # 只顯示前10個錯誤
                report_lines.append(f"{i}. 文件: {error['file']}")
                report_lines.append(f"   錯誤: {error['error']}")
                report_lines.append(f"   時間: {error['timestamp']}")
            
            if len(self.stats.errors) > 10:
                report_lines.append(f"   ... 還有 {len(self.stats.errors) - 10} 個錯誤")
        
        # 添加警告信息
        if self.stats.warnings:
            report_lines.append(f"\n## 警告信息 ({len(self.stats.warnings)} 個)")
            for i, warning in enumerate(self.stats.warnings[:5], 1):  # 只顯示前5個警告
                report_lines.append(f"{i}. 文件: {warning['file']}")
                report_lines.append(f"   警告: {warning['warning']}")
            
            if len(self.stats.warnings) > 5:
                report_lines.append(f"   ... 還有 {len(self.stats.warnings) - 5} 個警告")
        
        # 添加文件處理詳情
        report_lines.append(f"\n## 文件處理詳情")
        for result in results:
            status = "✓" if result.success else "✗"
            report_lines.append(
                f"{status} {Path(result.source_file).name} -> {Path(result.target_file).name if result.target_file else 'N/A'} "
                f"({result.records_successful}/{result.records_processed} 記錄, {result.processing_time:.2f}s)"
            )
        
        report_content = "\n".join(report_lines)
        
        # 保存報告
        report_file = Path(self.config.output_directory) / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"遷移報告已生成: {report_file}")
        return str(report_file)
    
    def run_migration(self, source_path: str, 
                     file_pattern: str = "*.csv") -> Tuple[List[FileProcessingResult], str]:
        """運行完整的遷移流程
        
        Args:
            source_path: 源路徑（文件或目錄）
            file_pattern: 文件模式（僅用於目錄）
            
        Returns:
            Tuple[List[FileProcessingResult], str]: 處理結果和報告文件路徑
        """
        self.stats.start_time = datetime.now()
        
        self.logger.info(f"開始數據遷移: {source_path}")
        self.logger.info(f"配置: {self.config.source_format} -> {self.config.target_format}")
        
        try:
            source_path_obj = Path(source_path)
            
            if source_path_obj.is_file():
                # 單文件遷移
                results = [self.migrate_file(source_path)]
            elif source_path_obj.is_dir():
                # 目錄遷移
                results = self.migrate_directory(source_path, file_pattern)
            else:
                raise ValueError(f"無效的源路徑: {source_path}")
            
            # 生成報告
            report_file = self.generate_report(results)
            
            # 輸出摘要
            successful_files = sum(1 for r in results if r.success)
            self.logger.info(f"遷移完成: {successful_files}/{len(results)} 文件成功")
            self.logger.info(f"記錄統計: {self.stats.successful_records}/{self.stats.total_records} 成功")
            
            return results, report_file
            
        except Exception as e:
            self.logger.error(f"遷移過程發生錯誤: {e}")
            raise


def create_migration_tool(source_format: str = "legacy_v1",
                         target_format: str = "standard",
                         **kwargs) -> MigrationTool:
    """創建遷移工具的便捷函數
    
    Args:
        source_format: 源格式
        target_format: 目標格式
        **kwargs: 其他配置參數
        
    Returns:
        MigrationTool: 遷移工具實例
    """
    config = MigrationConfig(
        source_format=source_format,
        target_format=target_format,
        **kwargs
    )
    return MigrationTool(config)


def main():
    """主函數 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JobSpy 數據格式遷移工具")
    parser.add_argument("source", help="源文件或目錄路徑")
    parser.add_argument("-o", "--output", default="./migrated_data", help="輸出目錄")
    parser.add_argument("-sf", "--source-format", default="legacy_v1", help="源格式")
    parser.add_argument("-tf", "--target-format", default="standard", help="目標格式")
    parser.add_argument("-p", "--pattern", default="*.csv", help="文件模式")
    parser.add_argument("-b", "--batch-size", type=int, default=1000, help="批處理大小")
    parser.add_argument("-w", "--workers", type=int, default=4, help="工作線程數")
    parser.add_argument("--no-cleaning", action="store_true", help="禁用數據清理")
    parser.add_argument("--no-validation", action="store_true", help="禁用數據驗證")
    parser.add_argument("--no-backup", action="store_true", help="禁用文件備份")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細輸出")
    
    args = parser.parse_args()
    
    # 設置日誌級別
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # 創建配置
    config = MigrationConfig(
        source_format=args.source_format,
        target_format=args.target_format,
        batch_size=args.batch_size,
        max_workers=args.workers,
        enable_cleaning=not args.no_cleaning,
        enable_validation=not args.no_validation,
        backup_original=not args.no_backup,
        output_directory=args.output
    )
    
    # 創建遷移工具
    migration_tool = MigrationTool(config)
    
    try:
        # 運行遷移
        results, report_file = migration_tool.run_migration(args.source, args.pattern)
        
        print(f"\n遷移完成!")
        print(f"報告文件: {report_file}")
        print(f"輸出目錄: {args.output}")
        
    except Exception as e:
        print(f"遷移失敗: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())