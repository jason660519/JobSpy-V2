"""緩存管理器

提供多層級緩存管理功能，包括內存緩存、Redis緩存和文件緩存。
"""

import json
import pickle
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from abc import ABC, abstractmethod
import structlog
from enum import Enum

logger = structlog.get_logger(__name__)


class CacheLevel(Enum):
    """緩存級別"""
    MEMORY = "memory"      # 內存緩存
    REDIS = "redis"        # Redis緩存
    FILE = "file"          # 文件緩存
    HYBRID = "hybrid"      # 混合緩存


class CacheStrategy(Enum):
    """緩存策略"""
    LRU = "lru"            # 最近最少使用
    LFU = "lfu"            # 最少使用頻率
    FIFO = "fifo"          # 先進先出
    TTL = "ttl"            # 基於時間


@dataclass
class CacheConfig:
    """緩存配置"""
    level: CacheLevel = CacheLevel.MEMORY
    strategy: CacheStrategy = CacheStrategy.LRU
    max_size: int = 1000
    ttl_seconds: int = 3600
    redis_url: Optional[str] = None
    file_path: Optional[str] = None
    compression: bool = False
    serialization: str = "json"  # json, pickle
    key_prefix: str = "jobspy"
    enable_stats: bool = True


@dataclass
class CacheStats:
    """緩存統計"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    size: int = 0
    memory_usage: int = 0
    last_access: Optional[datetime] = None
    
    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """未命中率"""
        return 1.0 - self.hit_rate


@dataclass
class CacheEntry:
    """緩存條目"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: Optional[int] = None
    
    def is_expired(self) -> bool:
        """檢查是否過期"""
        if self.ttl is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl
    
    def touch(self) -> None:
        """更新訪問時間和次數"""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1


class CacheBackend(ABC):
    """緩存後端基類"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.stats = CacheStats()
        self.logger = logger.bind(backend=self.__class__.__name__)
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設置緩存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """刪除緩存值"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空緩存"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """獲取緩存大小"""
        pass
    
    def _make_key(self, key: str) -> str:
        """生成完整的緩存鍵"""
        return f"{self.config.key_prefix}:{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        if self.config.serialization == "pickle":
            return pickle.dumps(value)
        else:
            return json.dumps(value, default=str).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """反序列化值"""
        if self.config.serialization == "pickle":
            return pickle.loads(data)
        else:
            return json.loads(data.decode('utf-8'))


class MemoryCache(CacheBackend):
    """內存緩存實現"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []  # LRU順序
        self._access_frequency: Dict[str, int] = {}  # LFU頻率
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        full_key = self._make_key(key)
        
        async with self._lock:
            if full_key not in self._cache:
                self.stats.misses += 1
                return None
            
            entry = self._cache[full_key]
            
            # 檢查是否過期
            if entry.is_expired():
                await self._remove_entry(full_key)
                self.stats.misses += 1
                return None
            
            # 更新訪問信息
            entry.touch()
            self._update_access_order(full_key)
            
            self.stats.hits += 1
            self.stats.last_access = datetime.utcnow()
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設置緩存值"""
        full_key = self._make_key(key)
        ttl = ttl or self.config.ttl_seconds
        
        async with self._lock:
            # 檢查是否需要淘汰
            if len(self._cache) >= self.config.max_size and full_key not in self._cache:
                await self._evict_one()
            
            # 創建緩存條目
            entry = CacheEntry(
                key=full_key,
                value=value,
                created_at=datetime.utcnow(),
                accessed_at=datetime.utcnow(),
                ttl=ttl
            )
            
            self._cache[full_key] = entry
            self._update_access_order(full_key)
            
            self.stats.sets += 1
            self.stats.size = len(self._cache)
            
            return True
    
    async def delete(self, key: str) -> bool:
        """刪除緩存值"""
        full_key = self._make_key(key)
        
        async with self._lock:
            if full_key in self._cache:
                await self._remove_entry(full_key)
                self.stats.deletes += 1
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        full_key = self._make_key(key)
        
        async with self._lock:
            if full_key not in self._cache:
                return False
            
            entry = self._cache[full_key]
            if entry.is_expired():
                await self._remove_entry(full_key)
                return False
            
            return True
    
    async def clear(self) -> bool:
        """清空緩存"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._access_frequency.clear()
            self.stats.size = 0
            return True
    
    async def size(self) -> int:
        """獲取緩存大小"""
        return len(self._cache)
    
    async def _remove_entry(self, key: str) -> None:
        """移除緩存條目"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)
        if key in self._access_frequency:
            del self._access_frequency[key]
        self.stats.size = len(self._cache)
    
    def _update_access_order(self, key: str) -> None:
        """更新訪問順序"""
        # 更新LRU順序
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        # 更新LFU頻率
        self._access_frequency[key] = self._access_frequency.get(key, 0) + 1
    
    async def _evict_one(self) -> None:
        """淘汰一個緩存條目"""
        if not self._cache:
            return
        
        key_to_evict = None
        
        if self.config.strategy == CacheStrategy.LRU:
            # 淘汰最近最少使用的
            key_to_evict = self._access_order[0] if self._access_order else None
        
        elif self.config.strategy == CacheStrategy.LFU:
            # 淘汰使用頻率最低的
            min_frequency = min(self._access_frequency.values()) if self._access_frequency else 0
            for key, freq in self._access_frequency.items():
                if freq == min_frequency:
                    key_to_evict = key
                    break
        
        elif self.config.strategy == CacheStrategy.FIFO:
            # 淘汰最早添加的
            oldest_time = None
            for key, entry in self._cache.items():
                if oldest_time is None or entry.created_at < oldest_time:
                    oldest_time = entry.created_at
                    key_to_evict = key
        
        elif self.config.strategy == CacheStrategy.TTL:
            # 淘汰最接近過期的
            earliest_expiry = None
            for key, entry in self._cache.items():
                if entry.ttl is not None:
                    expiry_time = entry.created_at + timedelta(seconds=entry.ttl)
                    if earliest_expiry is None or expiry_time < earliest_expiry:
                        earliest_expiry = expiry_time
                        key_to_evict = key
        
        if key_to_evict:
            await self._remove_entry(key_to_evict)
            self.stats.evictions += 1
    
    async def cleanup_expired(self) -> int:
        """清理過期條目"""
        expired_keys = []
        
        async with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                await self._remove_entry(key)
        
        return len(expired_keys)


class FileCache(CacheBackend):
    """文件緩存實現"""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self.cache_dir = Path(config.file_path or "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
    
    def _get_file_path(self, key: str) -> Path:
        """獲取緩存文件路徑"""
        # 使用哈希避免文件名問題
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"
    
    async def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        full_key = self._make_key(key)
        file_path = self._get_file_path(full_key)
        
        try:
            if not file_path.exists():
                self.stats.misses += 1
                return None
            
            # 讀取緩存文件
            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 檢查是否過期
            if 'ttl' in cache_data and cache_data['ttl'] is not None:
                created_at = cache_data['created_at']
                if (datetime.utcnow() - created_at).total_seconds() > cache_data['ttl']:
                    file_path.unlink(missing_ok=True)
                    self.stats.misses += 1
                    return None
            
            self.stats.hits += 1
            self.stats.last_access = datetime.utcnow()
            
            return cache_data['value']
            
        except Exception as e:
            self.logger.error("讀取文件緩存失敗", key=key, error=str(e))
            self.stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設置緩存值"""
        full_key = self._make_key(key)
        file_path = self._get_file_path(full_key)
        ttl = ttl or self.config.ttl_seconds
        
        try:
            cache_data = {
                'key': full_key,
                'value': value,
                'created_at': datetime.utcnow(),
                'ttl': ttl
            }
            
            # 寫入緩存文件
            with open(file_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.stats.sets += 1
            return True
            
        except Exception as e:
            self.logger.error("寫入文件緩存失敗", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """刪除緩存值"""
        full_key = self._make_key(key)
        file_path = self._get_file_path(full_key)
        
        try:
            if file_path.exists():
                file_path.unlink()
                self.stats.deletes += 1
                return True
            return False
            
        except Exception as e:
            self.logger.error("刪除文件緩存失敗", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        full_key = self._make_key(key)
        file_path = self._get_file_path(full_key)
        
        if not file_path.exists():
            return False
        
        # 檢查是否過期
        try:
            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            if 'ttl' in cache_data and cache_data['ttl'] is not None:
                created_at = cache_data['created_at']
                if (datetime.utcnow() - created_at).total_seconds() > cache_data['ttl']:
                    file_path.unlink(missing_ok=True)
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def clear(self) -> bool:
        """清空緩存"""
        try:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink(missing_ok=True)
            return True
            
        except Exception as e:
            self.logger.error("清空文件緩存失敗", error=str(e))
            return False
    
    async def size(self) -> int:
        """獲取緩存大小"""
        try:
            return len(list(self.cache_dir.glob("*.cache")))
        except Exception:
            return 0
    
    async def cleanup_expired(self) -> int:
        """清理過期文件"""
        expired_count = 0
        
        try:
            for file_path in self.cache_dir.glob("*.cache"):
                try:
                    with open(file_path, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    if 'ttl' in cache_data and cache_data['ttl'] is not None:
                        created_at = cache_data['created_at']
                        if (datetime.utcnow() - created_at).total_seconds() > cache_data['ttl']:
                            file_path.unlink(missing_ok=True)
                            expired_count += 1
                            
                except Exception:
                    # 損壞的文件也刪除
                    file_path.unlink(missing_ok=True)
                    expired_count += 1
            
            return expired_count
            
        except Exception as e:
            self.logger.error("清理過期文件緩存失敗", error=str(e))
            return 0


class CacheManager:
    """緩存管理器
    
    提供統一的緩存接口，支持多級緩存和不同的緩存策略。
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.logger = logger.bind(component="CacheManager")
        
        # 初始化緩存後端
        if config.level == CacheLevel.MEMORY:
            self.backend = MemoryCache(config)
        elif config.level == CacheLevel.FILE:
            self.backend = FileCache(config)
        elif config.level == CacheLevel.HYBRID:
            # 混合緩存：內存 + 文件
            self.memory_backend = MemoryCache(config)
            self.file_backend = FileCache(config)
            self.backend = self.memory_backend  # 主要使用內存緩存
        else:
            raise ValueError(f"不支持的緩存級別: {config.level}")
        
        # 清理任務
        self._cleanup_task = None
        self._running = False
    
    async def start(self) -> None:
        """啟動緩存管理器"""
        self._running = True
        
        # 啟動清理任務
        if self.config.ttl_seconds > 0:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info(
            "緩存管理器已啟動",
            level=self.config.level.value,
            strategy=self.config.strategy.value,
            max_size=self.config.max_size
        )
    
    async def stop(self) -> None:
        """停止緩存管理器"""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("緩存管理器已停止")
    
    async def get(self, key: str) -> Optional[Any]:
        """獲取緩存值"""
        if self.config.level == CacheLevel.HYBRID:
            # 先從內存緩存獲取
            value = await self.memory_backend.get(key)
            if value is not None:
                return value
            
            # 從文件緩存獲取
            value = await self.file_backend.get(key)
            if value is not None:
                # 回寫到內存緩存
                await self.memory_backend.set(key, value)
                return value
            
            return None
        else:
            return await self.backend.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """設置緩存值"""
        if self.config.level == CacheLevel.HYBRID:
            # 同時寫入內存和文件緩存
            memory_result = await self.memory_backend.set(key, value, ttl)
            file_result = await self.file_backend.set(key, value, ttl)
            return memory_result and file_result
        else:
            return await self.backend.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """刪除緩存值"""
        if self.config.level == CacheLevel.HYBRID:
            memory_result = await self.memory_backend.delete(key)
            file_result = await self.file_backend.delete(key)
            return memory_result or file_result
        else:
            return await self.backend.delete(key)
    
    async def exists(self, key: str) -> bool:
        """檢查鍵是否存在"""
        if self.config.level == CacheLevel.HYBRID:
            return (await self.memory_backend.exists(key) or 
                   await self.file_backend.exists(key))
        else:
            return await self.backend.exists(key)
    
    async def clear(self) -> bool:
        """清空緩存"""
        if self.config.level == CacheLevel.HYBRID:
            memory_result = await self.memory_backend.clear()
            file_result = await self.file_backend.clear()
            return memory_result and file_result
        else:
            return await self.backend.clear()
    
    async def size(self) -> int:
        """獲取緩存大小"""
        if self.config.level == CacheLevel.HYBRID:
            return await self.memory_backend.size()
        else:
            return await self.backend.size()
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """獲取緩存統計"""
        if self.config.level == CacheLevel.HYBRID:
            return {
                "memory": self.memory_backend.stats,
                "file": self.file_backend.stats
            }
        else:
            return {"main": self.backend.stats}
    
    async def _cleanup_loop(self) -> None:
        """清理循環"""
        while self._running:
            try:
                await asyncio.sleep(self.config.ttl_seconds // 4)  # 每1/4 TTL時間清理一次
                
                if self.config.level == CacheLevel.HYBRID:
                    memory_cleaned = await self.memory_backend.cleanup_expired()
                    file_cleaned = await self.file_backend.cleanup_expired()
                    total_cleaned = memory_cleaned + file_cleaned
                else:
                    if hasattr(self.backend, 'cleanup_expired'):
                        total_cleaned = await self.backend.cleanup_expired()
                    else:
                        total_cleaned = 0
                
                if total_cleaned > 0:
                    self.logger.debug(
                        "清理過期緩存項",
                        count=total_cleaned
                    )
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("緩存清理失敗", error=str(e))
    
    async def cache_function(self, 
                           func: Callable, 
                           key: str, 
                           ttl: Optional[int] = None,
                           *args, 
                           **kwargs) -> Any:
        """緩存函數結果
        
        Args:
            func: 要緩存的函數
            key: 緩存鍵
            ttl: 過期時間
            *args: 函數參數
            **kwargs: 函數關鍵字參數
            
        Returns:
            Any: 函數結果
        """
        # 檢查緩存
        cached_result = await self.get(key)
        if cached_result is not None:
            return cached_result
        
        # 執行函數
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # 緩存結果
        await self.set(key, result, ttl)
        
        return result
    
    def cache_decorator(self, 
                       key_func: Optional[Callable] = None, 
                       ttl: Optional[int] = None):
        """緩存裝飾器
        
        Args:
            key_func: 生成緩存鍵的函數
            ttl: 過期時間
            
        Returns:
            Callable: 裝飾器函數
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # 生成緩存鍵
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # 默認鍵生成策略
                    func_name = func.__name__
                    args_str = str(args) + str(sorted(kwargs.items()))
                    cache_key = f"{func_name}:{hashlib.md5(args_str.encode()).hexdigest()}"
                
                return await self.cache_function(func, cache_key, ttl, *args, **kwargs)
            
            return wrapper
        return decorator