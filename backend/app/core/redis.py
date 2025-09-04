"""
Redis configuration and caching utilities
"""
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio import Redis

from .config import settings


class RedisManager:
    """Redis connection and caching manager"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis"""
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=False,
            max_connections=20,
        )
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis with automatic deserialization"""
        if not self.redis:
            return None
        
        value = await self.redis.get(key)
        if value is None:
            return None
        
        try:
            # Try JSON first (for simple data types)
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            try:
                # Fallback to pickle for complex objects
                return pickle.loads(value)
            except (pickle.PickleError, TypeError):
                # Return as string if all else fails
                return value.decode() if isinstance(value, bytes) else value
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in Redis with automatic serialization"""
        if not self.redis:
            return False
        
        # Serialize value
        try:
            # Try JSON first for simple types
            serialized = json.dumps(value)
        except (TypeError, ValueError):
            # Use pickle for complex objects
            serialized = pickle.dumps(value)
        
        # Set with optional TTL
        if ttl:
            return await self.redis.setex(key, ttl, serialized)
        else:
            return await self.redis.set(key, serialized)
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.redis:
            return False
        
        result = await self.redis.delete(key)
        return result > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.redis:
            return False
        
        return await self.redis.exists(key)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in Redis"""
        if not self.redis:
            return 0
        
        return await self.redis.incrby(key, amount)
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration for a key"""
        if not self.redis:
            return False
        
        return await self.redis.expire(key, ttl)

# Global Redis manager instance
redis_manager = RedisManager()

async def get_redis() -> RedisManager:
    """Dependency to get Redis manager"""
    return redis_manager


class CacheKey:
    """Cache key constants and generators"""
    
    # Job search cache keys
    JOB_SEARCH_RESULT = "job_search:{query_hash}"
    JOB_DETAIL = "job:{job_id}"
    
    # User cache keys
    USER_SESSION = "user_session:{user_id}"
    USER_PROFILE = "user_profile:{user_id}"
    
    # AI cache keys
    AI_ANALYSIS = "ai_analysis:{url_hash}"
    AI_COST_DAILY = "ai_cost:{date}"
    
    # Rate limiting keys
    RATE_LIMIT_USER = "rate_limit:user:{user_id}"
    RATE_LIMIT_IP = "rate_limit:ip:{ip_address}"
    
    @staticmethod
    def job_search_result(query_hash: str) -> str:
        return f"job_search:{query_hash}"
    
    @staticmethod
    def user_session(user_id: str) -> str:
        return f"user_session:{user_id}"
    
    @staticmethod
    def ai_analysis(url_hash: str) -> str:
        return f"ai_analysis:{url_hash}"
    
    @staticmethod
    def rate_limit_user(user_id: str) -> str:
        return f"rate_limit:user:{user_id}"