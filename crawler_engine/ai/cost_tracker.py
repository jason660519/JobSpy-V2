"""成本追蹤器

監控和管理AI服務的使用成本，實現成本控制和預算管理。
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class UsageRecord:
    """使用記錄"""
    timestamp: datetime
    model: str
    tokens: int
    cost: float
    request_type: str
    platform: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class CostSummary:
    """成本摘要"""
    total_cost: float
    total_tokens: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_cost_per_request: float
    average_tokens_per_request: float
    period_start: datetime
    period_end: datetime


class CostTracker:
    """成本追蹤器
    
    監控AI服務使用成本，提供預算控制和使用統計。
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = logger.bind(component="cost_tracker")
        
        # 存儲路徑
        self.storage_path = Path(storage_path) if storage_path else Path("data/cost_tracking")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 使用記錄
        self._usage_records: List[UsageRecord] = []
        
        # 模型定價（每1K tokens的成本，USD）
        self.model_pricing = {
            "gpt-4-vision-preview": {
                "input": 0.01,
                "output": 0.03,
                "image": 0.00765  # 每張圖片的額外成本
            },
            "gpt-4-turbo": {
                "input": 0.01,
                "output": 0.03
            },
            "gpt-4": {
                "input": 0.03,
                "output": 0.06
            },
            "gpt-3.5-turbo": {
                "input": 0.0015,
                "output": 0.002
            }
        }
        
        # 成本限制（USD）
        self.daily_limit = 50.0
        self.monthly_limit = 1000.0
        self.hourly_limit = 10.0
        
        # 加載歷史記錄
        asyncio.create_task(self._load_usage_records())
    
    async def calculate_cost(self, model: str, tokens: int, 
                           has_image: bool = False, 
                           input_tokens: Optional[int] = None,
                           output_tokens: Optional[int] = None) -> float:
        """計算使用成本
        
        Args:
            model: 模型名稱
            tokens: 總token數
            has_image: 是否包含圖片
            input_tokens: 輸入token數（可選）
            output_tokens: 輸出token數（可選）
            
        Returns:
            float: 成本（USD）
        """
        try:
            if model not in self.model_pricing:
                self.logger.warning("未知模型，使用默認定價", model=model)
                model = "gpt-4-turbo"  # 使用默認模型定價
            
            pricing = self.model_pricing[model]
            cost = 0.0
            
            # 如果有具體的輸入/輸出token分布
            if input_tokens is not None and output_tokens is not None:
                cost += (input_tokens / 1000) * pricing["input"]
                cost += (output_tokens / 1000) * pricing["output"]
            else:
                # 使用總token數和平均定價
                avg_price = (pricing["input"] + pricing["output"]) / 2
                cost += (tokens / 1000) * avg_price
            
            # 圖片額外成本
            if has_image and "image" in pricing:
                cost += pricing["image"]
            
            return round(cost, 6)
            
        except Exception as e:
            self.logger.error("成本計算失敗", error=str(e))
            return 0.0
    
    async def record_usage(self, model: str, tokens: int, cost: float,
                         request_type: str, platform: Optional[str] = None,
                         success: bool = True, error_message: Optional[str] = None):
        """記錄使用情況
        
        Args:
            model: 模型名稱
            tokens: 使用的token數
            cost: 成本
            request_type: 請求類型
            platform: 平台名稱
            success: 是否成功
            error_message: 錯誤信息
        """
        try:
            record = UsageRecord(
                timestamp=datetime.now(),
                model=model,
                tokens=tokens,
                cost=cost,
                request_type=request_type,
                platform=platform,
                success=success,
                error_message=error_message
            )
            
            self._usage_records.append(record)
            
            # 異步保存記錄
            asyncio.create_task(self._save_usage_record(record))
            
            self.logger.info(
                "使用記錄已添加",
                model=model,
                tokens=tokens,
                cost=cost,
                request_type=request_type,
                success=success
            )
            
        except Exception as e:
            self.logger.error("記錄使用失敗", error=str(e))
    
    async def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """獲取指定日期的成本"""
        if date is None:
            date = datetime.now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self._calculate_cost_in_period(start_of_day, end_of_day)
    
    async def get_monthly_cost(self, date: Optional[datetime] = None) -> float:
        """獲取指定月份的成本"""
        if date is None:
            date = datetime.now()
        
        start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            end_of_month = start_of_month.replace(year=date.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=date.month + 1)
        
        return self._calculate_cost_in_period(start_of_month, end_of_month)
    
    async def get_hourly_cost(self, hour: Optional[datetime] = None) -> float:
        """獲取指定小時的成本"""
        if hour is None:
            hour = datetime.now()
        
        start_of_hour = hour.replace(minute=0, second=0, microsecond=0)
        end_of_hour = start_of_hour + timedelta(hours=1)
        
        return self._calculate_cost_in_period(start_of_hour, end_of_hour)
    
    async def check_cost_limits(self) -> Dict[str, bool]:
        """檢查成本限制
        
        Returns:
            Dict[str, bool]: 各種限制的檢查結果
        """
        daily_cost = await self.get_daily_cost()
        monthly_cost = await self.get_monthly_cost()
        hourly_cost = await self.get_hourly_cost()
        
        return {
            "daily_limit_ok": daily_cost < self.daily_limit,
            "monthly_limit_ok": monthly_cost < self.monthly_limit,
            "hourly_limit_ok": hourly_cost < self.hourly_limit,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "hourly_cost": hourly_cost,
            "daily_remaining": max(0, self.daily_limit - daily_cost),
            "monthly_remaining": max(0, self.monthly_limit - monthly_cost),
            "hourly_remaining": max(0, self.hourly_limit - hourly_cost)
        }
    
    async def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """獲取使用統計
        
        Args:
            days: 統計天數
            
        Returns:
            Dict[str, Any]: 使用統計信息
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 過濾指定期間的記錄
            period_records = [
                record for record in self._usage_records
                if start_date <= record.timestamp <= end_date
            ]
            
            if not period_records:
                return self._empty_stats(start_date, end_date)
            
            # 計算統計信息
            total_cost = sum(record.cost for record in period_records)
            total_tokens = sum(record.tokens for record in period_records)
            total_requests = len(period_records)
            successful_requests = sum(1 for record in period_records if record.success)
            failed_requests = total_requests - successful_requests
            
            # 按模型統計
            model_stats = {}
            for record in period_records:
                if record.model not in model_stats:
                    model_stats[record.model] = {
                        "requests": 0,
                        "tokens": 0,
                        "cost": 0.0
                    }
                model_stats[record.model]["requests"] += 1
                model_stats[record.model]["tokens"] += record.tokens
                model_stats[record.model]["cost"] += record.cost
            
            # 按請求類型統計
            request_type_stats = {}
            for record in period_records:
                if record.request_type not in request_type_stats:
                    request_type_stats[record.request_type] = {
                        "requests": 0,
                        "tokens": 0,
                        "cost": 0.0
                    }
                request_type_stats[record.request_type]["requests"] += 1
                request_type_stats[record.request_type]["tokens"] += record.tokens
                request_type_stats[record.request_type]["cost"] += record.cost
            
            # 按平台統計
            platform_stats = {}
            for record in period_records:
                platform = record.platform or "unknown"
                if platform not in platform_stats:
                    platform_stats[platform] = {
                        "requests": 0,
                        "tokens": 0,
                        "cost": 0.0
                    }
                platform_stats[platform]["requests"] += 1
                platform_stats[platform]["tokens"] += record.tokens
                platform_stats[platform]["cost"] += record.cost
            
            # 每日成本趨勢
            daily_costs = {}
            for record in period_records:
                date_key = record.timestamp.strftime("%Y-%m-%d")
                if date_key not in daily_costs:
                    daily_costs[date_key] = 0.0
                daily_costs[date_key] += record.cost
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "summary": {
                    "total_cost": round(total_cost, 4),
                    "total_tokens": total_tokens,
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests,
                    "success_rate": round(successful_requests / total_requests * 100, 2) if total_requests > 0 else 0,
                    "average_cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0,
                    "average_tokens_per_request": round(total_tokens / total_requests, 2) if total_requests > 0 else 0
                },
                "model_breakdown": model_stats,
                "request_type_breakdown": request_type_stats,
                "platform_breakdown": platform_stats,
                "daily_costs": daily_costs,
                "cost_limits": await self.check_cost_limits()
            }
            
        except Exception as e:
            self.logger.error("獲取使用統計失敗", error=str(e))
            return {}
    
    async def export_usage_data(self, start_date: datetime, end_date: datetime, 
                              format: str = "json") -> str:
        """導出使用數據
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            format: 導出格式 ('json', 'csv')
            
        Returns:
            str: 導出的文件路徑
        """
        try:
            # 過濾指定期間的記錄
            period_records = [
                record for record in self._usage_records
                if start_date <= record.timestamp <= end_date
            ]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "json":
                filename = f"usage_export_{timestamp}.json"
                filepath = self.storage_path / filename
                
                export_data = {
                    "export_info": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "export_timestamp": datetime.now().isoformat(),
                        "total_records": len(period_records)
                    },
                    "records": [asdict(record) for record in period_records]
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            elif format.lower() == "csv":
                import csv
                filename = f"usage_export_{timestamp}.csv"
                filepath = self.storage_path / filename
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    if period_records:
                        writer = csv.DictWriter(f, fieldnames=asdict(period_records[0]).keys())
                        writer.writeheader()
                        for record in period_records:
                            writer.writerow(asdict(record))
            
            else:
                raise ValueError(f"不支持的導出格式: {format}")
            
            self.logger.info(
                "使用數據導出完成",
                filepath=str(filepath),
                records_count=len(period_records),
                format=format
            )
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error("導出使用數據失敗", error=str(e))
            raise
    
    def _calculate_cost_in_period(self, start_time: datetime, end_time: datetime) -> float:
        """計算指定時間段內的成本"""
        return sum(
            record.cost for record in self._usage_records
            if start_time <= record.timestamp < end_time
        )
    
    def _empty_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """返回空的統計信息"""
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_cost": 0.0,
                "total_tokens": 0,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "success_rate": 0.0,
                "average_cost_per_request": 0.0,
                "average_tokens_per_request": 0.0
            },
            "model_breakdown": {},
            "request_type_breakdown": {},
            "platform_breakdown": {},
            "daily_costs": {}
        }
    
    async def _load_usage_records(self):
        """加載歷史使用記錄"""
        try:
            records_file = self.storage_path / "usage_records.json"
            if records_file.exists():
                with open(records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for record_data in data:
                    record = UsageRecord(
                        timestamp=datetime.fromisoformat(record_data["timestamp"]),
                        model=record_data["model"],
                        tokens=record_data["tokens"],
                        cost=record_data["cost"],
                        request_type=record_data["request_type"],
                        platform=record_data.get("platform"),
                        success=record_data.get("success", True),
                        error_message=record_data.get("error_message")
                    )
                    self._usage_records.append(record)
                
                self.logger.info("歷史使用記錄已加載", records_count=len(self._usage_records))
        
        except Exception as e:
            self.logger.warning("加載歷史記錄失敗", error=str(e))
    
    async def _save_usage_record(self, record: UsageRecord):
        """保存單個使用記錄"""
        try:
            records_file = self.storage_path / "usage_records.json"
            
            # 加載現有記錄
            existing_records = []
            if records_file.exists():
                with open(records_file, 'r', encoding='utf-8') as f:
                    existing_records = json.load(f)
            
            # 添加新記錄
            record_dict = asdict(record)
            record_dict["timestamp"] = record.timestamp.isoformat()
            existing_records.append(record_dict)
            
            # 保持最近1000條記錄
            if len(existing_records) > 1000:
                existing_records = existing_records[-1000:]
            
            # 保存到文件
            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump(existing_records, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error("保存使用記錄失敗", error=str(e))
    
    def set_cost_limits(self, daily: Optional[float] = None, 
                       monthly: Optional[float] = None,
                       hourly: Optional[float] = None):
        """設置成本限制"""
        if daily is not None:
            self.daily_limit = daily
        if monthly is not None:
            self.monthly_limit = monthly
        if hourly is not None:
            self.hourly_limit = hourly
        
        self.logger.info(
            "成本限制已更新",
            daily_limit=self.daily_limit,
            monthly_limit=self.monthly_limit,
            hourly_limit=self.hourly_limit
        )
    
    def update_model_pricing(self, model: str, pricing: Dict[str, float]):
        """更新模型定價"""
        self.model_pricing[model] = pricing
        self.logger.info("模型定價已更新", model=model, pricing=pricing)