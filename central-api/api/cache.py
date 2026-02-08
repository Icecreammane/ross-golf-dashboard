"""
Caching layer with Redis fallback to in-memory
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional
import redis

logger = logging.getLogger(__name__)


class CacheBackend:
    """Abstract cache backend"""
    
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        raise NotImplementedError
    
    def clear(self) -> bool:
        raise NotImplementedError


class RedisCache(CacheBackend):
    """Redis cache backend"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis cache connected: {host}:{port}")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            serialized = json.dumps(value)
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis CLEAR error: {e}")
            return False


class InMemoryCache(CacheBackend):
    """In-memory cache backend (fallback)"""
    
    def __init__(self):
        self.cache = {}
        logger.info("In-memory cache initialized (Redis unavailable)")
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, expires_at = self.cache[key]
            if datetime.now() < expires_at:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expires_at)
        return True
    
    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        self.cache.clear()
        return True


class Cache:
    """Unified cache interface"""
    
    def __init__(self, redis_enabled: bool = True, redis_host: str = 'localhost', 
                 redis_port: int = 6379, redis_db: int = 0, default_ttl: int = 300):
        self.default_ttl = default_ttl
        
        if redis_enabled:
            try:
                self.backend = RedisCache(redis_host, redis_port, redis_db)
                self.using_redis = True
            except Exception as e:
                logger.warning(f"Falling back to in-memory cache: {e}")
                self.backend = InMemoryCache()
                self.using_redis = False
        else:
            self.backend = InMemoryCache()
            self.using_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        return self.backend.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if ttl is None:
            ttl = self.default_ttl
        return self.backend.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        return self.backend.delete(key)
    
    def clear(self) -> bool:
        return self.backend.clear()
    
    def is_redis(self) -> bool:
        return self.using_redis
