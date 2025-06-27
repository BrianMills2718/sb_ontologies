"""
V5.0 Performance Optimizer and Caching System
Advanced database performance optimization with intelligent caching and query optimization
"""

import asyncio
import time
import logging
import hashlib
import json
import statistics
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import weakref
from collections import OrderedDict, defaultdict

from database_adapters import DatabaseAdapter, QueryResult

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on query patterns


class QueryOptimizationLevel(Enum):
    """Query optimization levels"""
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    AGGRESSIVE = "aggressive"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: QueryResult
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update access metadata"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class QueryPattern:
    """Query execution pattern analysis"""
    query_hash: str
    query_template: str
    execution_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    last_execution: Optional[float] = None
    parameter_patterns: Dict[str, Set[Any]] = field(default_factory=lambda: defaultdict(set))
    cache_hit_rate: float = 0.0
    optimization_applied: bool = False


@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics"""
    total_queries: int = 0
    cached_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    average_query_time: float = 0.0
    total_query_time: float = 0.0
    slow_queries: int = 0
    optimized_queries: int = 0
    memory_usage_bytes: int = 0


class QueryCache:
    """Advanced query result caching system"""
    
    def __init__(
        self, 
        max_size: int = 1000,
        max_memory_mb: int = 100,
        default_ttl: Optional[float] = 3600.0,
        strategy: CacheStrategy = CacheStrategy.LRU
    ):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Cache storage
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.access_frequency: Dict[str, int] = defaultdict(int)
        
        # Statistics
        self.metrics = PerformanceMetrics()
        
        logger.info(f"Query cache initialized: {max_size} entries, {max_memory_mb}MB, {strategy.value} strategy")
    
    def _generate_cache_key(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from query and parameters"""
        # Normalize query (remove extra whitespace, case-insensitive)
        normalized_query = ' '.join(query.split()).lower()
        
        # Include parameters in key
        param_str = json.dumps(parameters or {}, sort_keys=True)
        
        # Generate hash
        key_data = f"{normalized_query}:{param_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _estimate_size(self, result: QueryResult) -> int:
        """Estimate memory size of query result"""
        size = 0
        
        # Estimate size of rows data
        if result.rows:
            # Rough estimation based on JSON serialization
            size += len(json.dumps(result.rows).encode())
        
        # Add metadata size
        if result.metadata:
            size += len(json.dumps(result.metadata).encode())
        
        # Add fixed overhead
        size += 200  # Approximate overhead for QueryResult object
        
        return size
    
    def _evict_entries(self, required_space: int = 0):
        """Evict cache entries based on strategy"""
        current_memory = sum(entry.size_bytes for entry in self.cache.values())
        
        # Check if eviction is needed
        if (len(self.cache) < self.max_size and 
            current_memory + required_space <= self.max_memory_bytes):
            return
        
        entries_to_remove = []
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used entries
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used entries
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].access_count
            )
            
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first, then oldest
            expired_entries = [
                (key, entry) for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            if expired_entries:
                sorted_entries = expired_entries
            else:
                sorted_entries = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].created_at
                )
                
        else:  # ADAPTIVE
            # Adaptive strategy based on access patterns and age
            def adaptive_score(entry):
                age_factor = time.time() - entry.created_at
                access_factor = 1.0 / max(entry.access_count, 1)
                recency_factor = time.time() - entry.last_accessed
                return age_factor + access_factor + recency_factor
            
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: adaptive_score(x[1])
            )
        
        # Remove entries until we have enough space
        freed_memory = 0
        for key, entry in sorted_entries:
            if (len(self.cache) <= self.max_size // 2 and 
                current_memory - freed_memory + required_space <= self.max_memory_bytes):
                break
            
            entries_to_remove.append(key)
            freed_memory += entry.size_bytes
        
        # Remove selected entries
        for key in entries_to_remove:
            if key in self.cache:
                del self.cache[key]
                self.access_frequency.pop(key, None)
        
        if entries_to_remove:
            logger.debug(f"Cache evicted {len(entries_to_remove)} entries, freed {freed_memory} bytes")
    
    def get(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[QueryResult]:
        """Get cached query result"""
        cache_key = self._generate_cache_key(query, parameters)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Check expiration
            if entry.is_expired():
                del self.cache[cache_key]
                self.access_frequency.pop(cache_key, None)
                self.metrics.cache_misses += 1
                return None
            
            # Update access metadata
            entry.touch()
            self.access_frequency[cache_key] += 1
            
            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self.cache.move_to_end(cache_key)
            
            self.metrics.cache_hits += 1
            self.metrics.cached_queries += 1
            
            logger.debug(f"Cache hit for query: {query[:50]}")
            return entry.value
        
        self.metrics.cache_misses += 1
        return None
    
    def put(
        self, 
        query: str, 
        result: QueryResult, 
        parameters: Optional[Dict[str, Any]] = None,
        ttl: Optional[float] = None
    ):
        """Cache query result"""
        cache_key = self._generate_cache_key(query, parameters)
        entry_size = self._estimate_size(result)
        
        # Evict entries if necessary
        self._evict_entries(entry_size)
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            value=result,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            ttl=ttl or self.default_ttl,
            size_bytes=entry_size
        )
        
        # Store in cache
        self.cache[cache_key] = entry
        self.access_frequency[cache_key] = 1
        
        # Update memory usage
        self.metrics.memory_usage_bytes = sum(entry.size_bytes for entry in self.cache.values())
        
        logger.debug(f"Cached query result: {query[:50]} ({entry_size} bytes)")
    
    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries"""
        if pattern is None:
            # Clear all
            self.cache.clear()
            self.access_frequency.clear()
            logger.info("Cache cleared completely")
        else:
            # Clear entries matching pattern
            keys_to_remove = [
                key for key in self.cache.keys()
                if pattern in key
            ]
            
            for key in keys_to_remove:
                del self.cache[key]
                self.access_frequency.pop(key, None)
            
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
        
        # Update memory usage
        self.metrics.memory_usage_bytes = sum(entry.size_bytes for entry in self.cache.values())
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.metrics.cache_hits + self.metrics.cache_misses
        hit_rate = self.metrics.cache_hits / max(total_requests, 1)
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "memory_usage_mb": self.metrics.memory_usage_bytes / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "hit_rate": hit_rate,
            "strategy": self.strategy.value,
            "total_requests": total_requests
        }


class QueryAnalyzer:
    """Analyzes query patterns and performance"""
    
    def __init__(self, slow_query_threshold: float = 1.0):
        self.slow_query_threshold = slow_query_threshold
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.execution_history: List[Tuple[str, float, bool]] = []  # (query_hash, execution_time, cached)
        
    def _normalize_query(self, query: str) -> str:
        """Normalize query to detect patterns"""
        # Remove parameter values and replace with placeholders
        normalized = query
        
        # Replace numeric literals
        import re
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        
        # Replace string literals
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        normalized = re.sub(r'"[^"]*"', '"?"', normalized)
        
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized.lower()
    
    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for query pattern"""
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def record_execution(
        self, 
        query: str, 
        execution_time: float, 
        parameters: Optional[Dict[str, Any]] = None,
        cached: bool = False
    ):
        """Record query execution for analysis"""
        query_hash = self._generate_query_hash(query)
        normalized_query = self._normalize_query(query)
        
        # Get or create pattern
        if query_hash not in self.query_patterns:
            self.query_patterns[query_hash] = QueryPattern(
                query_hash=query_hash,
                query_template=normalized_query
            )
        
        pattern = self.query_patterns[query_hash]
        
        # Update pattern statistics
        pattern.execution_count += 1
        pattern.total_execution_time += execution_time
        pattern.average_execution_time = pattern.total_execution_time / pattern.execution_count
        pattern.min_execution_time = min(pattern.min_execution_time, execution_time)
        pattern.max_execution_time = max(pattern.max_execution_time, execution_time)
        pattern.last_execution = time.time()
        
        # Record parameter patterns
        if parameters:
            for key, value in parameters.items():
                pattern.parameter_patterns[key].add(type(value).__name__)
        
        # Update cache hit rate
        if cached:
            pattern.cache_hit_rate = (pattern.cache_hit_rate * (pattern.execution_count - 1) + 1) / pattern.execution_count
        else:
            pattern.cache_hit_rate = (pattern.cache_hit_rate * (pattern.execution_count - 1)) / pattern.execution_count
        
        # Add to execution history
        self.execution_history.append((query_hash, execution_time, cached))
        
        # Keep only recent history
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
    
    def get_slow_queries(self) -> List[QueryPattern]:
        """Get queries that exceed slow query threshold"""
        return [
            pattern for pattern in self.query_patterns.values()
            if pattern.average_execution_time > self.slow_query_threshold
        ]
    
    def get_frequent_queries(self, min_executions: int = 10) -> List[QueryPattern]:
        """Get frequently executed queries"""
        return [
            pattern for pattern in self.query_patterns.values()
            if pattern.execution_count >= min_executions
        ]
    
    def get_optimization_candidates(self) -> List[QueryPattern]:
        """Get queries that would benefit from optimization"""
        candidates = []
        
        for pattern in self.query_patterns.values():
            # Consider queries that are slow OR frequent
            if (pattern.average_execution_time > self.slow_query_threshold or
                pattern.execution_count > 20):
                candidates.append(pattern)
        
        # Sort by impact (execution count * average time)
        candidates.sort(
            key=lambda p: p.execution_count * p.average_execution_time,
            reverse=True
        )
        
        return candidates
    
    def get_analyzer_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        if not self.query_patterns:
            return {
                "total_patterns": 0,
                "slow_queries": 0,
                "frequent_queries": 0,
                "average_execution_time": 0.0
            }
        
        total_executions = sum(p.execution_count for p in self.query_patterns.values())
        total_time = sum(p.total_execution_time for p in self.query_patterns.values())
        avg_time = total_time / max(total_executions, 1)
        
        slow_queries = len(self.get_slow_queries())
        frequent_queries = len(self.get_frequent_queries())
        
        return {
            "total_patterns": len(self.query_patterns),
            "total_executions": total_executions,
            "slow_queries": slow_queries,
            "frequent_queries": frequent_queries,
            "average_execution_time": avg_time,
            "optimization_candidates": len(self.get_optimization_candidates())
        }


class PerformanceOptimizer:
    """Database performance optimizer with caching and query optimization"""
    
    def __init__(
        self,
        cache_config: Optional[Dict[str, Any]] = None,
        optimization_level: QueryOptimizationLevel = QueryOptimizationLevel.INTERMEDIATE,
        slow_query_threshold: float = 1.0
    ):
        # Initialize cache
        cache_config = cache_config or {}
        self.cache = QueryCache(
            max_size=cache_config.get("max_size", 1000),
            max_memory_mb=cache_config.get("max_memory_mb", 100),
            default_ttl=cache_config.get("default_ttl", 3600.0),
            strategy=CacheStrategy(cache_config.get("strategy", "lru"))
        )
        
        # Initialize analyzer
        self.analyzer = QueryAnalyzer(slow_query_threshold)
        
        self.optimization_level = optimization_level
        self.optimized_adapters: Set[weakref.ref] = set()
        
        # Performance tracking
        self.total_optimization_time_saved = 0.0
        self.optimizations_applied = 0
        
        logger.info(f"Performance optimizer initialized with {optimization_level.value} optimization level")
    
    async def execute_optimized_query(
        self,
        adapter: DatabaseAdapter,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[float] = None,
        force_cache: bool = False
    ) -> QueryResult:
        """Execute query with optimization and caching"""
        
        start_time = time.time()
        
        # Check cache first (unless it's a write operation)
        if self._is_cacheable_query(query) or force_cache:
            cached_result = self.cache.get(query, parameters)
            if cached_result is not None:
                # Record cache hit
                execution_time = time.time() - start_time
                self.analyzer.record_execution(query, execution_time, parameters, cached=True)
                
                logger.debug(f"Query served from cache: {query[:50]}")
                return cached_result
        
        # Apply query optimizations
        optimized_query = self._optimize_query(query, parameters)
        
        # Execute query
        try:
            result = await adapter.execute_query(optimized_query, parameters)
            execution_time = time.time() - start_time
            
            # Record execution
            self.analyzer.record_execution(query, execution_time, parameters, cached=False)
            
            # Cache result if successful and cacheable
            if result.success and (self._is_cacheable_query(query) or force_cache):
                self.cache.put(query, result, parameters, cache_ttl)
            
            # Update performance metrics
            if optimized_query != query:
                self.optimizations_applied += 1
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.analyzer.record_execution(query, execution_time, parameters, cached=False)
            raise
    
    def _is_cacheable_query(self, query: str) -> bool:
        """Determine if query results can be cached"""
        query_upper = query.strip().upper()
        
        # Only cache SELECT queries
        if not query_upper.startswith('SELECT'):
            return False
        
        # Don't cache queries with non-deterministic functions
        non_deterministic = ['NOW()', 'CURRENT_TIMESTAMP', 'RAND()', 'RANDOM()']
        for func in non_deterministic:
            if func in query_upper:
                return False
        
        return True
    
    def _optimize_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Apply query optimizations based on optimization level"""
        
        if self.optimization_level == QueryOptimizationLevel.NONE:
            return query
        
        optimized = query
        
        if self.optimization_level in (QueryOptimizationLevel.BASIC, QueryOptimizationLevel.INTERMEDIATE, QueryOptimizationLevel.AGGRESSIVE):
            # Basic optimizations
            optimized = self._apply_basic_optimizations(optimized)
        
        if self.optimization_level in (QueryOptimizationLevel.INTERMEDIATE, QueryOptimizationLevel.AGGRESSIVE):
            # Intermediate optimizations
            optimized = self._apply_intermediate_optimizations(optimized)
        
        if self.optimization_level == QueryOptimizationLevel.AGGRESSIVE:
            # Aggressive optimizations
            optimized = self._apply_aggressive_optimizations(optimized)
        
        return optimized
    
    def _apply_basic_optimizations(self, query: str) -> str:
        """Apply basic query optimizations"""
        import re
        
        optimized = query
        
        # Remove unnecessary whitespace
        optimized = re.sub(r'\s+', ' ', optimized.strip())
        
        # Optimize SELECT * to specific columns where possible
        # This would require schema knowledge in a real implementation
        
        return optimized
    
    def _apply_intermediate_optimizations(self, query: str) -> str:
        """Apply intermediate query optimizations"""
        import re
        
        optimized = query
        
        # Convert EXISTS to JOIN where appropriate
        # This is a simplified example
        if 'EXISTS' in optimized.upper():
            # In a real implementation, this would be more sophisticated
            pass
        
        # Optimize ORDER BY with LIMIT
        if 'ORDER BY' in optimized.upper() and 'LIMIT' in optimized.upper():
            # Could suggest index optimizations
            pass
        
        return optimized
    
    def _apply_aggressive_optimizations(self, query: str) -> str:
        """Apply aggressive query optimizations"""
        optimized = query
        
        # Force index hints (database-specific)
        # Convert subqueries to JOINs where possible
        # Apply query rewriting techniques
        
        return optimized
    
    def optimize_adapter(self, adapter: DatabaseAdapter):
        """Apply performance optimizations to database adapter"""
        
        # Store weak reference to avoid circular references
        adapter_ref = weakref.ref(adapter)
        self.optimized_adapters.add(adapter_ref)
        
        # Wrap adapter's execute_query method
        original_execute = adapter.execute_query
        
        async def optimized_execute(query: str, parameters: Optional[Dict[str, Any]] = None, transaction_id: Optional[str] = None):
            if transaction_id is not None:
                # Don't cache transactional queries
                return await original_execute(query, parameters, transaction_id)
            else:
                # Call the optimizer directly without going through the adapter to avoid recursion
                return await self._execute_with_optimization(original_execute, query, parameters)
        
        adapter.execute_query = optimized_execute
        
        logger.info(f"Performance optimization applied to adapter: {adapter.connection_id}")
    
    async def _execute_with_optimization(
        self,
        original_execute_func,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Execute query with optimization using the original function to avoid recursion"""
        start_time = time.time()
        
        # Check cache first (unless it's a write operation)
        if self._is_cacheable_query(query):
            cached_result = self.cache.get(query, parameters)
            if cached_result is not None:
                # Record cache hit
                execution_time = time.time() - start_time
                self.analyzer.record_execution(query, execution_time, parameters, cached=True)
                
                logger.debug(f"Query served from cache: {query[:50]}")
                return cached_result
        
        # Apply query optimizations
        optimized_query = self._optimize_query(query, parameters)
        
        # Execute query using original function
        try:
            result = await original_execute_func(optimized_query, parameters)
            execution_time = time.time() - start_time
            
            # Record execution
            self.analyzer.record_execution(query, execution_time, parameters, cached=False)
            
            # Cache result if successful and cacheable
            if result.success and self._is_cacheable_query(query):
                self.cache.put(query, result, parameters)
            
            # Update performance metrics
            if optimized_query != query:
                self.optimizations_applied += 1
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.analyzer.record_execution(query, execution_time, parameters, cached=False)
            raise
    
    def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries"""
        self.cache.invalidate(pattern)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        cache_stats = self.cache.get_cache_statistics()
        analyzer_stats = self.analyzer.get_analyzer_statistics()
        
        # Calculate time saved through caching
        time_saved = cache_stats["cache_hits"] * analyzer_stats.get("average_execution_time", 0)
        
        return {
            "cache_statistics": cache_stats,
            "query_analysis": analyzer_stats,
            "optimization_statistics": {
                "optimizations_applied": self.optimizations_applied,
                "optimization_level": self.optimization_level.value,
                "optimized_adapters": len(self.optimized_adapters),
                "estimated_time_saved_seconds": time_saved
            },
            "slow_queries": [
                {
                    "query_template": pattern.query_template[:100],
                    "execution_count": pattern.execution_count,
                    "average_time": pattern.average_execution_time,
                    "total_time": pattern.total_execution_time
                }
                for pattern in self.analyzer.get_slow_queries()[:10]
            ],
            "optimization_candidates": [
                {
                    "query_template": pattern.query_template[:100],
                    "execution_count": pattern.execution_count,
                    "average_time": pattern.average_execution_time,
                    "impact_score": pattern.execution_count * pattern.average_execution_time
                }
                for pattern in self.analyzer.get_optimization_candidates()[:10]
            ]
        }


# Test harness
if __name__ == "__main__":
    async def test_performance_optimizer():
        """Test performance optimizer functionality"""
        
        print("🔧 Testing Performance Optimizer...")
        
        # Create mock adapter
        class MockAdapter:
            def __init__(self):
                self.connection_id = "mock_adapter"
                
            async def execute_query(self, query, parameters=None, transaction_id=None):
                # Simulate execution time
                await asyncio.sleep(0.01)
                return QueryResult(
                    success=True,
                    rows_affected=1,
                    rows=[{"id": 1, "name": "test"}],
                    execution_time=0.01
                )
        
        # Create optimizer
        optimizer = PerformanceOptimizer(
            cache_config={
                "max_size": 100,
                "max_memory_mb": 10,
                "strategy": "lru"
            },
            optimization_level=QueryOptimizationLevel.INTERMEDIATE
        )
        
        adapter = MockAdapter()
        
        try:
            # Test query optimization
            print("  Testing query optimization...")
            optimizer.optimize_adapter(adapter)
            
            # Test queries
            test_queries = [
                "SELECT * FROM users WHERE id = %(user_id)s",
                "SELECT name, email FROM users WHERE created_at > %(date)s",
                "INSERT INTO users (name, email) VALUES (%(name)s, %(email)s)",
                "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
            ]
            
            # Execute queries multiple times to test caching
            for query in test_queries:
                for i in range(3):
                    result = await optimizer.execute_optimized_query(
                        adapter, 
                        query, 
                        {"user_id": 1, "date": "2023-01-01", "name": "John", "email": "john@example.com"}
                    )
                    print(f"    Query {i+1}: {'✅' if result.success else '❌'}")
            
            # Test cache statistics
            print("  Testing cache functionality...")
            cache_stats = optimizer.cache.get_cache_statistics()
            print(f"    Cache hit rate: {cache_stats['hit_rate']:.2%}")
            print(f"    Cache size: {cache_stats['cache_size']}")
            
            # Test query analysis
            print("  Testing query analysis...")
            analyzer_stats = optimizer.analyzer.get_analyzer_statistics()
            print(f"    Query patterns: {analyzer_stats['total_patterns']}")
            print(f"    Total executions: {analyzer_stats['total_executions']}")
            
            # Test performance report
            print("  Testing performance report...")
            report = optimizer.get_performance_report()
            print(f"    Optimizations applied: {report['optimization_statistics']['optimizations_applied']}")
            print(f"    Estimated time saved: {report['optimization_statistics']['estimated_time_saved_seconds']:.3f}s")
            
            # Test cache invalidation
            print("  Testing cache invalidation...")
            optimizer.invalidate_cache()
            cache_stats_after = optimizer.cache.get_cache_statistics()
            print(f"    Cache size after invalidation: {cache_stats_after['cache_size']}")
            
            print("✅ Performance optimizer testing complete!")
            
        except Exception as e:
            print(f"❌ Performance optimizer test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_performance_optimizer())