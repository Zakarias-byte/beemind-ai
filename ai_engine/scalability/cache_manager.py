"""
BeeMind Cache Management Module
Implements intelligent caching for models, results, and performance optimization
"""

import os
import logging
import json
import pickle
import hashlib
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
import redis
from functools import wraps
import time
import psutil
import gc

from ..exceptions import BeeMindError, handle_exception, log_operation

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
REDIS_MAX_MEMORY = os.getenv('REDIS_MAX_MEMORY', '2gb')
REDIS_MAX_MEMORY_POLICY = os.getenv('REDIS_MAX_MEMORY_POLICY', 'allkeys-lru')

class CacheManager:
    """Intelligent cache manager for BeeMind operations"""
    
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL, decode_responses=False)
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_usage': 0
        }
        
        # Configure Redis for optimal performance
        self._configure_redis()
        
        # Cache prefixes for different types
        self.prefixes = {
            'model': 'model:',
            'result': 'result:',
            'evaluation': 'eval:',
            'evolution': 'evol:',
            'metadata': 'meta:',
            'performance': 'perf:',
            'dataset': 'data:'
        }
        
        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            'model': 3600 * 24,  # 24 hours
            'result': 3600 * 6,  # 6 hours
            'evaluation': 3600 * 12,  # 12 hours
            'evolution': 3600 * 48,  # 48 hours
            'metadata': 3600 * 24 * 7,  # 7 days
            'performance': 3600 * 2,  # 2 hours
            'dataset': 3600 * 24  # 24 hours
        }
    
    def _configure_redis(self):
        """Configure Redis for optimal performance"""
        try:
            # Set memory policy
            self.redis_client.config_set('maxmemory', REDIS_MAX_MEMORY)
            self.redis_client.config_set('maxmemory-policy', REDIS_MAX_MEMORY_POLICY)
            
            # Enable compression for large objects
            self.redis_client.config_set('hash-max-ziplist-entries', 512)
            self.redis_client.config_set('hash-max-ziplist-value', 64)
            
            logger.info("Redis configured for optimal performance")
            
        except Exception as e:
            logger.warning(f"Could not configure Redis: {e}")
    
    def _generate_cache_key(self, cache_type: str, identifier: str) -> str:
        """Generate cache key with type prefix"""
        return f"{self.prefixes[cache_type]}{identifier}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for caching"""
        try:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.warning(f"Failed to serialize data with pickle, using JSON: {e}")
            return json.dumps(data, default=str).encode('utf-8')
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from cache"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Failed to deserialize with pickle, trying JSON: {e}")
            try:
                return json.loads(data.decode('utf-8'))
            except Exception as e2:
                logger.error(f"Failed to deserialize data: {e2}")
                return None
    
    @handle_exception
    def cache_model(self, model_id: str, model: Any, metadata: Dict[str, Any] = None) -> bool:
        """Cache a trained model"""
        log_operation("cache_model", {"model_id": model_id})
        
        try:
            cache_key = self._generate_cache_key('model', model_id)
            
            # Prepare model data
            model_data = {
                'model': model,
                'metadata': metadata or {},
                'cached_at': datetime.utcnow().isoformat(),
                'model_id': model_id
            }
            
            # Serialize and cache
            serialized_data = self._serialize_data(model_data)
            success = self.redis_client.setex(
                cache_key,
                self.ttl_settings['model'],
                serialized_data
            )
            
            if success:
                logger.info(f"Cached model: {model_id}")
                self.cache_stats['hits'] += 1
                return True
            else:
                logger.warning(f"Failed to cache model: {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error caching model {model_id}: {e}")
            return False
    
    @handle_exception
    def get_cached_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cached model"""
        try:
            cache_key = self._generate_cache_key('model', model_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                model_data = self._deserialize_data(cached_data)
                if model_data:
                    logger.info(f"Cache hit for model: {model_id}")
                    self.cache_stats['hits'] += 1
                    return model_data
            
            logger.info(f"Cache miss for model: {model_id}")
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached model {model_id}: {e}")
            return None
    
    @handle_exception
    def cache_evaluation_result(self, evaluation_id: str, result: Dict[str, Any]) -> bool:
        """Cache evaluation results"""
        try:
            cache_key = self._generate_cache_key('evaluation', evaluation_id)
            
            result_data = {
                'result': result,
                'cached_at': datetime.utcnow().isoformat(),
                'evaluation_id': evaluation_id
            }
            
            serialized_data = self._serialize_data(result_data)
            success = self.redis_client.setex(
                cache_key,
                self.ttl_settings['evaluation'],
                serialized_data
            )
            
            if success:
                logger.info(f"Cached evaluation result: {evaluation_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error caching evaluation result {evaluation_id}: {e}")
            return False
    
    @handle_exception
    def get_cached_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached evaluation results"""
        try:
            cache_key = self._generate_cache_key('evaluation', evaluation_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                result_data = self._deserialize_data(cached_data)
                if result_data:
                    logger.info(f"Cache hit for evaluation: {evaluation_id}")
                    self.cache_stats['hits'] += 1
                    return result_data['result']
            
            logger.info(f"Cache miss for evaluation: {evaluation_id}")
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached evaluation {evaluation_id}: {e}")
            return None
    
    @handle_exception
    def cache_evolution_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Cache evolution session data"""
        try:
            cache_key = self._generate_cache_key('evolution', session_id)
            
            session_data['cached_at'] = datetime.utcnow().isoformat()
            serialized_data = self._serialize_data(session_data)
            
            success = self.redis_client.setex(
                cache_key,
                self.ttl_settings['evolution'],
                serialized_data
            )
            
            if success:
                logger.info(f"Cached evolution session: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error caching evolution session {session_id}: {e}")
            return False
    
    @handle_exception
    def get_cached_evolution_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached evolution session"""
        try:
            cache_key = self._generate_cache_key('evolution', session_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                session_data = self._deserialize_data(cached_data)
                if session_data:
                    logger.info(f"Cache hit for evolution session: {session_id}")
                    self.cache_stats['hits'] += 1
                    return session_data
            
            logger.info(f"Cache miss for evolution session: {session_id}")
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached evolution session {session_id}: {e}")
            return None
    
    @handle_exception
    def cache_dataset_hash(self, dataset_hash: str, dataset_info: Dict[str, Any]) -> bool:
        """Cache dataset information"""
        try:
            cache_key = self._generate_cache_key('dataset', dataset_hash)
            
            dataset_info['cached_at'] = datetime.utcnow().isoformat()
            serialized_data = self._serialize_data(dataset_info)
            
            success = self.redis_client.setex(
                cache_key,
                self.ttl_settings['dataset'],
                serialized_data
            )
            
            if success:
                logger.info(f"Cached dataset info: {dataset_hash}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error caching dataset info {dataset_hash}: {e}")
            return False
    
    @handle_exception
    def get_cached_dataset_info(self, dataset_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached dataset information"""
        try:
            cache_key = self._generate_cache_key('dataset', dataset_hash)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                dataset_info = self._deserialize_data(cached_data)
                if dataset_info:
                    logger.info(f"Cache hit for dataset info: {dataset_hash}")
                    self.cache_stats['hits'] += 1
                    return dataset_info
            
            logger.info(f"Cache miss for dataset info: {dataset_hash}")
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached dataset info {dataset_hash}: {e}")
            return None
    
    @handle_exception
    def invalidate_cache(self, cache_type: str, identifier: str) -> bool:
        """Invalidate specific cache entry"""
        try:
            cache_key = self._generate_cache_key(cache_type, identifier)
            result = self.redis_client.delete(cache_key)
            
            if result > 0:
                logger.info(f"Invalidated cache: {cache_key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error invalidating cache {cache_key}: {e}")
            return False
    
    @handle_exception
    def clear_cache_type(self, cache_type: str) -> int:
        """Clear all cache entries of a specific type"""
        try:
            pattern = f"{self.prefixes[cache_type]}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries for type: {cache_type}")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing cache type {cache_type}: {e}")
            return 0
    
    @handle_exception
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and performance metrics"""
        try:
            # Get Redis info
            redis_info = self.redis_client.info()
            
            # Calculate hit rate
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            # Get memory usage
            memory_usage = psutil.virtual_memory()
            
            stats = {
                'cache_stats': self.cache_stats.copy(),
                'hit_rate': hit_rate,
                'redis_info': {
                    'used_memory': redis_info.get('used_memory', 0),
                    'used_memory_human': redis_info.get('used_memory_human', '0B'),
                    'maxmemory': redis_info.get('maxmemory', 0),
                    'maxmemory_human': redis_info.get('maxmemory_human', '0B'),
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'total_commands_processed': redis_info.get('total_commands_processed', 0),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0)
                },
                'system_memory': {
                    'total': memory_usage.total,
                    'available': memory_usage.available,
                    'percent': memory_usage.percent,
                    'used': memory_usage.used
                },
                'cache_size': {
                    'total_keys': redis_info.get('db0', {}).get('keys', 0),
                    'expires': redis_info.get('db0', {}).get('expires', 0)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    @handle_exception
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        try:
            optimization_results = {
                'memory_cleanup': False,
                'expired_keys_cleared': 0,
                'fragmentation_reduced': False
            }
            
            # Clear expired keys
            expired_keys = self.redis_client.execute_command('MEMORY PURGE')
            if expired_keys:
                optimization_results['expired_keys_cleared'] = expired_keys
            
            # Force garbage collection
            gc.collect()
            
            # Check memory usage
            memory_usage = psutil.virtual_memory()
            if memory_usage.percent > 80:
                # Clear least used cache entries
                self.clear_cache_type('result')  # Clear old results
                optimization_results['memory_cleanup'] = True
            
            logger.info("Cache optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")
            return {'error': str(e)}

# Global cache manager instance
cache_manager = CacheManager()

# Cache decorator for functions
def cache_result(cache_type: str, ttl: Optional[int] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get_cached_evaluation(cache_key)
            if cached_result is not None:
                return cached_result['result']
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.cache_evaluation_result(cache_key, result)
            
            return result
        return wrapper
    return decorator
