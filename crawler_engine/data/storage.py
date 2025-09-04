"""存儲後端

提供多種存儲後端實現，包括數據庫、文件系統和緩存存儲。
"""

import json
import sqlite3
import asyncio
import aiofiles
import aiosqlite
from typing import Dict, List, Any, Optional, AsyncIterator, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from abc import ABC, abstractmethod
import structlog
from urllib.parse import urlparse
import pickle
import hashlib
import csv

from ..platforms.base import JobData

logger = structlog.get_logger(__name__)


@dataclass
class StorageConfig:
    """存儲配置"""
    backend_type: str  # database, file, cache
    connection_string: Optional[str] = None
    file_path: Optional[str] = None
    cache_size: int = 1000
    ttl_seconds: int = 3600
    batch_size: int = 100
    auto_commit: bool = True
    compression: bool = False
    encryption: bool = False


@dataclass
class StorageStats:
    """存儲統計"""
    total_records: int = 0
    successful_writes: int = 0
    failed_writes: int = 0
    successful_reads: int = 0
    failed_reads: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    storage_size_bytes: int = 0
    last_operation_time: Optional[datetime] = None
    
    @property
    def write_success_rate(self) -> float:
        """寫入成功率"""
        total = self.successful_writes + self.failed_writes
        return self.successful_writes / total if total > 0 else 0.0
    
    @property
    def read_success_rate(self) -> float:
        """讀取成功率"""
        total = self.successful_reads + self.failed_reads
        return self.successful_reads / total if total > 0 else 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """緩存命中率"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class StorageBackend(ABC):
    """存儲後端基類"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.stats = StorageStats()
        self.logger = logger.bind(backend=self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化存儲後端"""
        if self._initialized:
            return
        
        await self._initialize_backend()
        self._initialized = True
        self.logger.info("存儲後端已初始化")
    
    async def cleanup(self) -> None:
        """清理資源"""
        if not self._initialized:
            return
        
        await self._cleanup_backend()
        self._initialized = False
        self.logger.info("存儲後端已清理")
    
    @abstractmethod
    async def _initialize_backend(self) -> None:
        """初始化後端實現"""
        pass
    
    @abstractmethod
    async def _cleanup_backend(self) -> None:
        """清理後端實現"""
        pass
    
    @abstractmethod
    async def store(self, data: Union[JobData, List[JobData]]) -> bool:
        """存儲數據
        
        Args:
            data: 要存儲的數據
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    async def retrieve(self, query: Dict[str, Any]) -> List[JobData]:
        """檢索數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[JobData]: 檢索結果
        """
        pass
    
    @abstractmethod
    async def update(self, query: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """更新數據
        
        Args:
            query: 查詢條件
            updates: 更新內容
            
        Returns:
            int: 更新的記錄數
        """
        pass
    
    @abstractmethod
    async def delete(self, query: Dict[str, Any]) -> int:
        """刪除數據
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 刪除的記錄數
        """
        pass
    
    @abstractmethod
    async def count(self, query: Dict[str, Any] = None) -> int:
        """統計記錄數
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 記錄數
        """
        pass
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """檢查記錄是否存在
        
        Args:
            query: 查詢條件
            
        Returns:
            bool: 是否存在
        """
        count = await self.count(query)
        return count > 0
    
    def get_stats(self) -> StorageStats:
        """獲取存儲統計
        
        Returns:
            StorageStats: 統計信息
        """
        return self.stats
    
    def _update_stats(self, operation: str, success: bool) -> None:
        """更新統計信息
        
        Args:
            operation: 操作類型
            success: 是否成功
        """
        self.stats.last_operation_time = datetime.utcnow()
        
        if operation == "write":
            if success:
                self.stats.successful_writes += 1
            else:
                self.stats.failed_writes += 1
        elif operation == "read":
            if success:
                self.stats.successful_reads += 1
            else:
                self.stats.failed_reads += 1


class DatabaseStorage(StorageBackend):
    """數據庫存儲後端
    
    支持SQLite和其他SQL數據庫。
    """
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.db_path = config.database_url.replace("sqlite:///", "") if config.database_url.startswith("sqlite:///") else "jobs.db"
        self.connection = None
        self._lock = asyncio.Lock()
    
    async def _initialize_backend(self) -> None:
        """初始化數據庫"""
        # 創建數據庫表
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE,
                    external_id TEXT,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    url TEXT,
                    description TEXT,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    salary_currency TEXT,
                    salary_period TEXT,
                    job_type TEXT,
                    experience_level TEXT,
                    posted_date TIMESTAMP,
                    scraped_date TIMESTAMP,
                    raw_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 創建索引
            await db.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON jobs(job_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_platform ON jobs(platform)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_company ON jobs(company)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_location ON jobs(location)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_posted_date ON jobs(posted_date)")
            
            await db.commit()
        
        self.logger.info("數據庫已初始化", db_path=self.db_path)
    
    async def _cleanup_backend(self) -> None:
        """清理數據庫連接"""
        # SQLite連接會自動關閉
        pass
    
    async def store(self, data: Union[JobData, List[JobData]]) -> bool:
        """存儲職位數據
        
        Args:
            data: 職位數據
            
        Returns:
            bool: 是否成功
        """
        if isinstance(data, JobData):
            data = [data]
        
        try:
            async with self._lock:
                async with aiosqlite.connect(self.db_path) as db:
                    for job in data:
                        await self._insert_job(db, job)
                    
                    if self.config.auto_commit:
                        await db.commit()
            
            self.stats.total_records += len(data)
            self._update_stats("write", True)
            
            self.logger.debug(
                "職位數據已存儲",
                count=len(data)
            )
            
            return True
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "存儲職位數據失敗",
                error=str(e),
                count=len(data)
            )
            return False
    
    async def _insert_job(self, db: aiosqlite.Connection, job: JobData) -> None:
        """插入單個職位記錄
        
        Args:
            db: 數據庫連接
            job: 職位數據
        """
        raw_data_json = json.dumps(job.raw_data) if job.raw_data else None
        
        await db.execute("""
            INSERT OR REPLACE INTO jobs (
                job_id, external_id, platform, title, company, location, url,
                description, salary_min, salary_max, salary_currency, salary_period,
                job_type, experience_level, posted_date, scraped_date, raw_data,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            job.job_id,
            job.external_id,
            job.platform,
            job.title,
            job.company,
            job.location,
            job.url,
            job.description,
            job.salary_min,
            job.salary_max,
            job.salary_currency,
            job.salary_period,
            job.job_type,
            job.experience_level,
            job.posted_date,
            job.scraped_date,
            raw_data_json
        ))
    
    async def store_job(self, job_data: Dict[str, Any]) -> bool:
        """存儲單個職位數據（字典格式）
        
        Args:
            job_data: 職位數據字典
            
        Returns:
            bool: 是否成功
        """
        try:
            # 將字典轉換為 JobData 對象
            from .models import JobData
            
            job = JobData(
                job_id=job_data.get('job_id', ''),
                external_id=job_data.get('external_id', ''),
                platform=job_data.get('platform', 'seek'),
                title=job_data.get('title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                url=job_data.get('url', ''),
                description=job_data.get('description', ''),
                salary_min=job_data.get('salary_min'),
                salary_max=job_data.get('salary_max'),
                salary_currency=job_data.get('salary_currency', 'AUD'),
                salary_period=job_data.get('salary_period', 'yearly'),
                job_type=job_data.get('job_type', ''),
                experience_level=job_data.get('experience_level', ''),
                posted_date=job_data.get('posted_date'),
                scraped_date=job_data.get('scraped_date'),
                raw_data=job_data
            )
            
            # 使用現有的 store 方法
            return await self.store(job)
            
        except Exception as e:
            self.logger.error(f"存儲職位數據失敗: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """獲取數據庫統計信息
        
        Returns:
            Dict[str, Any]: 統計信息
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 獲取總記錄數
                cursor = await db.execute("SELECT COUNT(*) FROM jobs")
                total_jobs = (await cursor.fetchone())[0]
                
                # 獲取平台分布
                cursor = await db.execute("""
                    SELECT platform, COUNT(*) 
                    FROM jobs 
                    GROUP BY platform
                """)
                platform_stats = dict(await cursor.fetchall())
                
                # 獲取最新記錄時間
                cursor = await db.execute("""
                    SELECT MAX(created_at) 
                    FROM jobs
                """)
                latest_record = (await cursor.fetchone())[0]
                
                return {
                    "total_jobs": total_jobs,
                    "platform_distribution": platform_stats,
                    "latest_record": latest_record,
                    "database_path": self.db_path
                }
                
        except Exception as e:
            self.logger.error(f"獲取統計信息失敗: {e}")
            return {"error": str(e)}
    
    async def retrieve(self, query: Dict[str, Any]) -> List[JobData]:
        """檢索職位數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[JobData]: 職位列表
        """
        try:
            where_clause, params = self._build_where_clause(query)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                sql = f"""
                    SELECT * FROM jobs
                    {where_clause}
                    ORDER BY created_at DESC
                """
                
                if "limit" in query:
                    sql += f" LIMIT {query['limit']}"
                
                async with db.execute(sql, params) as cursor:
                    rows = await cursor.fetchall()
            
            jobs = []
            for row in rows:
                job = self._row_to_job_data(row)
                jobs.append(job)
            
            self._update_stats("read", True)
            
            self.logger.debug(
                "職位數據已檢索",
                count=len(jobs),
                query=query
            )
            
            return jobs
            
        except Exception as e:
            self._update_stats("read", False)
            self.logger.error(
                "檢索職位數據失敗",
                error=str(e),
                query=query
            )
            return []
    
    def _build_where_clause(self, query: Dict[str, Any]) -> tuple:
        """構建WHERE子句
        
        Args:
            query: 查詢條件
            
        Returns:
            tuple: (WHERE子句, 參數列表)
        """
        conditions = []
        params = []
        
        for key, value in query.items():
            if key in ["limit", "offset"]:
                continue
            
            if key == "platform":
                conditions.append("platform = ?")
                params.append(value)
            elif key == "company":
                conditions.append("company LIKE ?")
                params.append(f"%{value}%")
            elif key == "location":
                conditions.append("location LIKE ?")
                params.append(f"%{value}%")
            elif key == "title":
                conditions.append("title LIKE ?")
                params.append(f"%{value}%")
            elif key == "job_id":
                conditions.append("job_id = ?")
                params.append(value)
            elif key == "salary_min_gte":
                conditions.append("salary_min >= ?")
                params.append(value)
            elif key == "salary_max_lte":
                conditions.append("salary_max <= ?")
                params.append(value)
            elif key == "posted_after":
                conditions.append("posted_date >= ?")
                params.append(value)
            elif key == "posted_before":
                conditions.append("posted_date <= ?")
                params.append(value)
        
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        else:
            where_clause = ""
        
        return where_clause, params
    
    def _row_to_job_data(self, row: aiosqlite.Row) -> JobData:
        """將數據庫行轉換為JobData對象
        
        Args:
            row: 數據庫行
            
        Returns:
            JobData: 職位數據對象
        """
        raw_data = None
        if row["raw_data"]:
            try:
                raw_data = json.loads(row["raw_data"])
            except json.JSONDecodeError:
                pass
        
        return JobData(
            title=row["title"],
            company=row["company"],
            location=row["location"],
            url=row["url"],
            description=row["description"],
            salary_min=row["salary_min"],
            salary_max=row["salary_max"],
            salary_currency=row["salary_currency"],
            salary_period=row["salary_period"],
            job_type=row["job_type"],
            experience_level=row["experience_level"],
            platform=row["platform"],
            job_id=row["job_id"],
            external_id=row["external_id"],
            posted_date=datetime.fromisoformat(row["posted_date"]) if row["posted_date"] else None,
            scraped_date=datetime.fromisoformat(row["scraped_date"]) if row["scraped_date"] else None,
            raw_data=raw_data
        )
    
    async def update(self, query: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """更新職位數據
        
        Args:
            query: 查詢條件
            updates: 更新內容
            
        Returns:
            int: 更新的記錄數
        """
        try:
            where_clause, where_params = self._build_where_clause(query)
            
            set_clauses = []
            set_params = []
            
            for key, value in updates.items():
                set_clauses.append(f"{key} = ?")
                set_params.append(value)
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            
            async with self._lock:
                async with aiosqlite.connect(self.db_path) as db:
                    sql = f"""
                        UPDATE jobs
                        SET {', '.join(set_clauses)}
                        {where_clause}
                    """
                    
                    params = set_params + where_params
                    cursor = await db.execute(sql, params)
                    
                    if self.config.auto_commit:
                        await db.commit()
                    
                    updated_count = cursor.rowcount
            
            self._update_stats("write", True)
            
            self.logger.debug(
                "職位數據已更新",
                count=updated_count,
                query=query
            )
            
            return updated_count
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "更新職位數據失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def delete(self, query: Dict[str, Any]) -> int:
        """刪除職位數據
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 刪除的記錄數
        """
        try:
            where_clause, params = self._build_where_clause(query)
            
            async with self._lock:
                async with aiosqlite.connect(self.db_path) as db:
                    sql = f"DELETE FROM jobs {where_clause}"
                    cursor = await db.execute(sql, params)
                    
                    if self.config.auto_commit:
                        await db.commit()
                    
                    deleted_count = cursor.rowcount
            
            self.stats.total_records -= deleted_count
            self._update_stats("write", True)
            
            self.logger.debug(
                "職位數據已刪除",
                count=deleted_count,
                query=query
            )
            
            return deleted_count
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "刪除職位數據失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """統計職位記錄數
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 記錄數
        """
        try:
            if query:
                where_clause, params = self._build_where_clause(query)
            else:
                where_clause, params = "", []
            
            async with aiosqlite.connect(self.db_path) as db:
                sql = f"SELECT COUNT(*) FROM jobs {where_clause}"
                async with db.execute(sql, params) as cursor:
                    result = await cursor.fetchone()
                    count = result[0] if result else 0
            
            self._update_stats("read", True)
            return count
            
        except Exception as e:
            self._update_stats("read", False)
            self.logger.error(
                "統計職位記錄失敗",
                error=str(e),
                query=query
            )
            return 0


class FileStorage(StorageBackend):
    """文件存儲後端
    
    支持JSON、CSV等格式的文件存儲。
    """
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.file_path = Path(config.file_path or "jobs.json")
        self.format = self.file_path.suffix.lower()
        self._lock = asyncio.Lock()
        self._data_cache = []
    
    async def _initialize_backend(self) -> None:
        """初始化文件存儲"""
        # 確保目錄存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果文件不存在，創建空文件
        if not self.file_path.exists():
            await self._write_empty_file()
        
        # 加載現有數據
        await self._load_data()
        
        self.logger.info(
            "文件存儲已初始化",
            file_path=str(self.file_path),
            format=self.format,
            records=len(self._data_cache)
        )
    
    async def _cleanup_backend(self) -> None:
        """清理文件存儲"""
        # 確保數據已保存
        await self._save_data()
        self._data_cache.clear()
    
    async def _write_empty_file(self) -> None:
        """創建空文件"""
        if self.format == ".json":
            async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
                await f.write('[]')
        elif self.format == ".csv":
            async with aiofiles.open(self.file_path, 'w', encoding='utf-8', newline='') as f:
                # 寫入CSV頭部
                headers = [
                    'job_id', 'external_id', 'platform', 'title', 'company', 'location',
                    'url', 'description', 'salary_min', 'salary_max', 'salary_currency',
                    'salary_period', 'job_type', 'experience_level', 'posted_date',
                    'scraped_date', 'raw_data'
                ]
                await f.write(','.join(headers) + '\n')
    
    async def _load_data(self) -> None:
        """加載現有數據"""
        try:
            if self.format == ".json":
                await self._load_json_data()
            elif self.format == ".csv":
                await self._load_csv_data()
            
            self.stats.total_records = len(self._data_cache)
            
        except Exception as e:
            self.logger.error(
                "加載文件數據失敗",
                error=str(e),
                file_path=str(self.file_path)
            )
            self._data_cache = []
    
    async def _load_json_data(self) -> None:
        """加載JSON數據"""
        async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            
        if content.strip():
            data = json.loads(content)
            self._data_cache = [self._dict_to_job_data(item) for item in data]
        else:
            self._data_cache = []
    
    async def _load_csv_data(self) -> None:
        """加載CSV數據"""
        self._data_cache = []
        
        async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        if content.strip():
            lines = content.strip().split('\n')
            if len(lines) > 1:  # 跳過頭部
                reader = csv.DictReader(lines)
                for row in reader:
                    job = self._dict_to_job_data(row)
                    self._data_cache.append(job)
    
    async def _save_data(self) -> None:
        """保存數據到文件"""
        try:
            if self.format == ".json":
                await self._save_json_data()
            elif self.format == ".csv":
                await self._save_csv_data()
            
            # 更新文件大小統計
            if self.file_path.exists():
                self.stats.storage_size_bytes = self.file_path.stat().st_size
            
        except Exception as e:
            self.logger.error(
                "保存文件數據失敗",
                error=str(e),
                file_path=str(self.file_path)
            )
    
    async def _save_json_data(self) -> None:
        """保存JSON數據"""
        data = [self._job_data_to_dict(job) for job in self._data_cache]
        
        async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    
    async def _save_csv_data(self) -> None:
        """保存CSV數據"""
        if not self._data_cache:
            return
        
        # 準備CSV數據
        fieldnames = [
            'job_id', 'external_id', 'platform', 'title', 'company', 'location',
            'url', 'description', 'salary_min', 'salary_max', 'salary_currency',
            'salary_period', 'job_type', 'experience_level', 'posted_date',
            'scraped_date', 'raw_data'
        ]
        
        rows = []
        for job in self._data_cache:
            row = self._job_data_to_dict(job)
            # 確保所有字段都存在
            for field in fieldnames:
                if field not in row:
                    row[field] = ''
            rows.append(row)
        
        # 寫入CSV文件
        content = []
        content.append(','.join(fieldnames))
        
        for row in rows:
            csv_row = []
            for field in fieldnames:
                value = str(row.get(field, '')).replace('"', '""')  # 轉義雙引號
                if ',' in value or '"' in value or '\n' in value:
                    value = f'"{value}"'
                csv_row.append(value)
            content.append(','.join(csv_row))
        
        async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
            await f.write('\n'.join(content))
    
    def _job_data_to_dict(self, job: JobData) -> Dict[str, Any]:
        """將JobData轉換為字典
        
        Args:
            job: 職位數據
            
        Returns:
            Dict[str, Any]: 字典數據
        """
        data = asdict(job)
        
        # 處理日期字段
        if data['posted_date']:
            data['posted_date'] = data['posted_date'].isoformat()
        if data['scraped_date']:
            data['scraped_date'] = data['scraped_date'].isoformat()
        
        # 處理raw_data字段
        if data['raw_data']:
            data['raw_data'] = json.dumps(data['raw_data'], ensure_ascii=False)
        
        return data
    
    def _dict_to_job_data(self, data: Dict[str, Any]) -> JobData:
        """將字典轉換為JobData
        
        Args:
            data: 字典數據
            
        Returns:
            JobData: 職位數據
        """
        # 處理日期字段
        if data.get('posted_date') and isinstance(data['posted_date'], str):
            try:
                data['posted_date'] = datetime.fromisoformat(data['posted_date'])
            except ValueError:
                data['posted_date'] = None
        
        if data.get('scraped_date') and isinstance(data['scraped_date'], str):
            try:
                data['scraped_date'] = datetime.fromisoformat(data['scraped_date'])
            except ValueError:
                data['scraped_date'] = None
        
        # 處理raw_data字段
        if data.get('raw_data') and isinstance(data['raw_data'], str):
            try:
                data['raw_data'] = json.loads(data['raw_data'])
            except json.JSONDecodeError:
                data['raw_data'] = None
        
        # 處理數值字段
        for field in ['salary_min', 'salary_max']:
            if data.get(field) and isinstance(data[field], str):
                try:
                    data[field] = int(data[field])
                except ValueError:
                    data[field] = None
        
        return JobData(**data)
    
    async def store(self, data: Union[JobData, List[JobData]]) -> bool:
        """存儲職位數據
        
        Args:
            data: 職位數據
            
        Returns:
            bool: 是否成功
        """
        if isinstance(data, JobData):
            data = [data]
        
        try:
            async with self._lock:
                # 添加到緩存
                for job in data:
                    # 檢查是否已存在（基於job_id）
                    existing_index = None
                    for i, existing_job in enumerate(self._data_cache):
                        if existing_job.job_id == job.job_id:
                            existing_index = i
                            break
                    
                    if existing_index is not None:
                        # 更新現有記錄
                        self._data_cache[existing_index] = job
                    else:
                        # 添加新記錄
                        self._data_cache.append(job)
                
                # 保存到文件
                if self.config.auto_commit:
                    await self._save_data()
            
            self.stats.total_records = len(self._data_cache)
            self._update_stats("write", True)
            
            self.logger.debug(
                "職位數據已存儲到文件",
                count=len(data),
                total_records=self.stats.total_records
            )
            
            return True
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "存儲職位數據到文件失敗",
                error=str(e),
                count=len(data)
            )
            return False
    
    async def retrieve(self, query: Dict[str, Any]) -> List[JobData]:
        """檢索職位數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[JobData]: 職位列表
        """
        try:
            results = []
            
            for job in self._data_cache:
                if self._matches_query(job, query):
                    results.append(job)
            
            # 應用限制
            if "limit" in query:
                results = results[:query["limit"]]
            
            self._update_stats("read", True)
            
            self.logger.debug(
                "從文件檢索職位數據",
                count=len(results),
                query=query
            )
            
            return results
            
        except Exception as e:
            self._update_stats("read", False)
            self.logger.error(
                "從文件檢索職位數據失敗",
                error=str(e),
                query=query
            )
            return []
    
    def _matches_query(self, job: JobData, query: Dict[str, Any]) -> bool:
        """檢查職位是否匹配查詢條件
        
        Args:
            job: 職位數據
            query: 查詢條件
            
        Returns:
            bool: 是否匹配
        """
        for key, value in query.items():
            if key in ["limit", "offset"]:
                continue
            
            if key == "platform" and job.platform != value:
                return False
            elif key == "company" and value.lower() not in (job.company or "").lower():
                return False
            elif key == "location" and value.lower() not in (job.location or "").lower():
                return False
            elif key == "title" and value.lower() not in (job.title or "").lower():
                return False
            elif key == "job_id" and job.job_id != value:
                return False
            elif key == "salary_min_gte" and (job.salary_min is None or job.salary_min < value):
                return False
            elif key == "salary_max_lte" and (job.salary_max is None or job.salary_max > value):
                return False
            elif key == "posted_after" and (job.posted_date is None or job.posted_date < value):
                return False
            elif key == "posted_before" and (job.posted_date is None or job.posted_date > value):
                return False
        
        return True
    
    async def update(self, query: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """更新職位數據
        
        Args:
            query: 查詢條件
            updates: 更新內容
            
        Returns:
            int: 更新的記錄數
        """
        try:
            updated_count = 0
            
            async with self._lock:
                for i, job in enumerate(self._data_cache):
                    if self._matches_query(job, query):
                        # 更新字段
                        job_dict = asdict(job)
                        job_dict.update(updates)
                        self._data_cache[i] = JobData(**job_dict)
                        updated_count += 1
                
                # 保存到文件
                if self.config.auto_commit and updated_count > 0:
                    await self._save_data()
            
            self._update_stats("write", True)
            
            self.logger.debug(
                "文件中職位數據已更新",
                count=updated_count,
                query=query
            )
            
            return updated_count
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "更新文件中職位數據失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def delete(self, query: Dict[str, Any]) -> int:
        """刪除職位數據
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 刪除的記錄數
        """
        try:
            deleted_count = 0
            
            async with self._lock:
                # 從後往前刪除，避免索引問題
                for i in range(len(self._data_cache) - 1, -1, -1):
                    if self._matches_query(self._data_cache[i], query):
                        del self._data_cache[i]
                        deleted_count += 1
                
                # 保存到文件
                if self.config.auto_commit and deleted_count > 0:
                    await self._save_data()
            
            self.stats.total_records = len(self._data_cache)
            self._update_stats("write", True)
            
            self.logger.debug(
                "文件中職位數據已刪除",
                count=deleted_count,
                query=query
            )
            
            return deleted_count
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "刪除文件中職位數據失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """統計職位記錄數
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 記錄數
        """
        try:
            if not query:
                count = len(self._data_cache)
            else:
                count = 0
                for job in self._data_cache:
                    if self._matches_query(job, query):
                        count += 1
            
            self._update_stats("read", True)
            return count
            
        except Exception as e:
            self._update_stats("read", False)
            self.logger.error(
                "統計文件中職位記錄失敗",
                error=str(e),
                query=query
            )
            return 0


class CacheStorage(StorageBackend):
    """緩存存儲後端
    
    基於內存的高速緩存存儲。
    """
    
    def __init__(self, config: StorageConfig):
        super().__init__(config)
        self.cache_size = config.cache_size
        self.ttl_seconds = config.ttl_seconds
        self._cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self._access_order: List[str] = []  # LRU順序
        self._lock = asyncio.Lock()
    
    async def _initialize_backend(self) -> None:
        """初始化緩存"""
        self.logger.info(
            "緩存存儲已初始化",
            cache_size=self.cache_size,
            ttl_seconds=self.ttl_seconds
        )
    
    async def _cleanup_backend(self) -> None:
        """清理緩存"""
        self._cache.clear()
        self._access_order.clear()
    
    async def store(self, data: Union[JobData, List[JobData]]) -> bool:
        """存儲到緩存
        
        Args:
            data: 職位數據
            
        Returns:
            bool: 是否成功
        """
        if isinstance(data, JobData):
            data = [data]
        
        try:
            async with self._lock:
                current_time = datetime.utcnow()
                
                for job in data:
                    key = self._generate_key(job)
                    
                    # 添加到緩存
                    self._cache[key] = (job, current_time)
                    
                    # 更新訪問順序
                    if key in self._access_order:
                        self._access_order.remove(key)
                    self._access_order.append(key)
                    
                    # 檢查緩存大小限制
                    if len(self._cache) > self.cache_size:
                        await self._evict_oldest()
            
            self.stats.total_records = len(self._cache)
            self._update_stats("write", True)
            
            self.logger.debug(
                "職位數據已存儲到緩存",
                count=len(data),
                cache_size=len(self._cache)
            )
            
            return True
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "存儲職位數據到緩存失敗",
                error=str(e),
                count=len(data)
            )
            return False
    
    def _generate_key(self, job: JobData) -> str:
        """生成緩存鍵
        
        Args:
            job: 職位數據
            
        Returns:
            str: 緩存鍵
        """
        if job.job_id:
            return f"job:{job.job_id}"
        
        # 基於內容生成鍵
        content = f"{job.platform}:{job.title}:{job.company}:{job.url}"
        return f"job:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def _evict_oldest(self) -> None:
        """淘汰最舊的緩存項"""
        if not self._access_order:
            return
        
        oldest_key = self._access_order.pop(0)
        if oldest_key in self._cache:
            del self._cache[oldest_key]
    
    async def retrieve(self, query: Dict[str, Any]) -> List[JobData]:
        """從緩存檢索數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[JobData]: 職位列表
        """
        try:
            results = []
            current_time = datetime.utcnow()
            expired_keys = []
            
            async with self._lock:
                for key, (job, timestamp) in self._cache.items():
                    # 檢查是否過期
                    if (current_time - timestamp).total_seconds() > self.ttl_seconds:
                        expired_keys.append(key)
                        continue
                    
                    # 檢查是否匹配查詢
                    if self._matches_cache_query(job, query):
                        results.append(job)
                        
                        # 更新訪問順序
                        if key in self._access_order:
                            self._access_order.remove(key)
                        self._access_order.append(key)
                
                # 清理過期項
                for key in expired_keys:
                    if key in self._cache:
                        del self._cache[key]
                    if key in self._access_order:
                        self._access_order.remove(key)
            
            # 應用限制
            if "limit" in query:
                results = results[:query["limit"]]
            
            # 更新統計
            if results:
                self.stats.cache_hits += len(results)
            else:
                self.stats.cache_misses += 1
            
            self._update_stats("read", True)
            
            self.logger.debug(
                "從緩存檢索職位數據",
                count=len(results),
                query=query,
                expired_count=len(expired_keys)
            )
            
            return results
            
        except Exception as e:
            self.stats.cache_misses += 1
            self._update_stats("read", False)
            self.logger.error(
                "從緩存檢索職位數據失敗",
                error=str(e),
                query=query
            )
            return []
    
    def _matches_cache_query(self, job: JobData, query: Dict[str, Any]) -> bool:
        """檢查職位是否匹配緩存查詢條件
        
        Args:
            job: 職位數據
            query: 查詢條件
            
        Returns:
            bool: 是否匹配
        """
        # 簡化的查詢匹配邏輯
        for key, value in query.items():
            if key in ["limit", "offset"]:
                continue
            
            if key == "job_id" and job.job_id != value:
                return False
            elif key == "platform" and job.platform != value:
                return False
            elif key == "company" and value.lower() not in (job.company or "").lower():
                return False
        
        return True
    
    async def update(self, query: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """更新緩存數據
        
        Args:
            query: 查詢條件
            updates: 更新內容
            
        Returns:
            int: 更新的記錄數
        """
        try:
            updated_count = 0
            current_time = datetime.utcnow()
            
            async with self._lock:
                for key, (job, timestamp) in list(self._cache.items()):
                    if self._matches_cache_query(job, query):
                        # 更新職位數據
                        job_dict = asdict(job)
                        job_dict.update(updates)
                        updated_job = JobData(**job_dict)
                        
                        # 更新緩存
                        self._cache[key] = (updated_job, current_time)
                        updated_count += 1
            
            self._update_stats("write", True)
            
            self.logger.debug(
                "緩存中職位數據已更新",
                count=updated_count,
                query=query
            )
            
            return updated_count
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "更新緩存中職位數據失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def delete(self, query: Dict[str, Any]) -> int:
        """從緩存刪除數據
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 刪除的記錄數
        """
        try:
            deleted_count = 0
            keys_to_delete = []
            
            async with self._lock:
                for key, (job, timestamp) in self._cache.items():
                    if self._matches_cache_query(job, query):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    if key in self._cache:
                        del self._cache[key]
                    if key in self._access_order:
                        self._access_order.remove(key)
                    deleted_count += 1
            
            self.stats.total_records = len(self._cache)
            self._update_stats("write", True)
            
            self.logger.debug(
                "緩存中職位數據已刪除",
                count=deleted_count,
                query=query
            )
            
            return deleted_count
            
        except Exception as e:
            self._update_stats("write", False)
            self.logger.error(
                "刪除緩存中職位數據失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """統計緩存記錄數
        
        Args:
            query: 查詢條件
            
        Returns:
            int: 記錄數
        """
        try:
            if not query:
                count = len(self._cache)
            else:
                count = 0
                for key, (job, timestamp) in self._cache.items():
                    if self._matches_cache_query(job, query):
                        count += 1
            
            self._update_stats("read", True)
            return count
            
        except Exception as e:
            self._update_stats("read", False)
            self.logger.error(
                "統計緩存記錄失敗",
                error=str(e),
                query=query
            )
            return 0
    
    async def clear_expired(self) -> int:
        """清理過期的緩存項
        
        Returns:
            int: 清理的項目數
        """
        current_time = datetime.utcnow()
        expired_keys = []
        
        async with self._lock:
            for key, (job, timestamp) in self._cache.items():
                if (current_time - timestamp).total_seconds() > self.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
        
        self.stats.total_records = len(self._cache)
        
        self.logger.debug(
            "已清理過期緩存項",
            count=len(expired_keys),
            remaining=len(self._cache)
        )
        
        return len(expired_keys)