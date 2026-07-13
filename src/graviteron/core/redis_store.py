import json
import logging
from typing import Dict, Any, Optional
import redis
from .omega_trace import OmegaTrace

logger = logging.getLogger("graviteron.redis_store")

class RedisTraceStore:
    """Manages persistence and caching of OmegaTrace records in Redis with automatic in-memory fallback"""

    def __init__(self, redis_url: Optional[str] = None, ttl_seconds: int = 86400):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.redis_client = None
        self.in_memory_db: Dict[str, Dict[str, Any]] = {}
        self.fallback_mode = False

        if redis_url:
            try:
                logger.info(f"Connecting to Redis at {redis_url}...")
                self.redis_client = redis.Redis.from_url(redis_url, socket_timeout=2.0)
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis successfully.")
            except Exception as e:
                logger.warning(
                    f"Redis connection failed: {e}. Falling back to in-memory trace storage."
                )
                self.fallback_mode = True
        else:
            logger.info("No Redis URL specified. Operating in local in-memory trace storage mode.")
            self.fallback_mode = True

    def put(self, trace: OmegaTrace) -> bool:
        """Store an OmegaTrace record"""
        trace_data = trace.to_dict()
        key = f"graviteron:trace:{trace.trace_id}"
        
        if self.fallback_mode or not self.redis_client:
            self.in_memory_db[trace.trace_id] = trace_data
            return True
        
        try:
            serialized = json.dumps(trace_data)
            self.redis_client.set(key, serialized, ex=self.ttl_seconds)
            return True
        except Exception as e:
            logger.error(f"Redis store failed to PUT key {key}: {e}. Retrying in-memory.")
            self.in_memory_db[trace.trace_id] = trace_data
            return True

    def get(self, trace_id: str) -> Optional[OmegaTrace]:
        """Retrieve an OmegaTrace record by ID"""
        key = f"graviteron:trace:{trace_id}"

        # Check local storage first (it might be written there if Redis failed)
        if trace_id in self.in_memory_db:
            return OmegaTrace.from_dict(self.in_memory_db[trace_id])

        if self.fallback_mode or not self.redis_client:
            return None

        try:
            data = self.redis_client.get(key)
            if not data:
                return None
            trace_dict = json.loads(data.decode("utf-8"))
            return OmegaTrace.from_dict(trace_dict)
        except Exception as e:
            logger.error(f"Redis store failed to GET key {key}: {e}.")
            return None
            
    def count(self) -> int:
        """Returns the number of traces currently tracked in this instance or Redis cluster"""
        if self.fallback_mode or not self.redis_client:
            return len(self.in_memory_db)
            
        try:
            # Note: scan/keys is slow on massive databases, but for this utility and testing it works fine
            # We prefix with graviteron:trace:*
            keys = self.redis_client.keys("graviteron:trace:*")
            return len(keys) + len(self.in_memory_db)
        except Exception as e:
            logger.error(f"Redis count keys failed: {e}.")
            return len(self.in_memory_db)
