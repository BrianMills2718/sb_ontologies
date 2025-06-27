"""
V5.0 Connection Pool Manager
Advanced connection pooling with health monitoring and distributed transaction support
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import weakref
from contextlib import asynccontextmanager
import statistics

logger = logging.getLogger(__name__)


class ConnectionPoolError(Exception):
    """Raised when connection pool operations fail"""
    pass


class ConnectionError(Exception):
    """Raised when individual connection operations fail"""
    pass


class ConnectionTimeoutError(ConnectionPoolError):
    """Raised when connection acquisition times out"""
    pass


class ConnectionState(Enum):
    """Connection state enumeration"""
    IDLE = "idle"
    ACTIVE = "active"
    TESTING = "testing"
    INVALID = "invalid"
    CLOSED = "closed"


class PoolState(Enum):
    """Connection pool state enumeration"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


@dataclass
class ConnectionMetrics:
    """Connection usage and performance metrics"""
    connection_id: str
    created_at: float
    last_used_at: float
    usage_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    total_response_time: float = 0.0
    state: ConnectionState = ConnectionState.IDLE
    transaction_id: Optional[str] = None


@dataclass
class PoolMetrics:
    """Connection pool metrics and statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    invalid_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_wait_time: float = 0.0
    avg_response_time: float = 0.0
    peak_usage: int = 0
    uptime: float = 0.0


class DatabaseConnection(ABC):
    """Abstract database connection interface"""
    
    def __init__(self, connection_id: str, config: Dict[str, Any]):
        self.connection_id = connection_id
        self.config = config
        self.state = ConnectionState.IDLE
        self.created_at = time.time()
        self.last_used_at = time.time()
        self.current_transaction_id: Optional[str] = None
        self._connection = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute database query"""
        pass
    
    @abstractmethod
    async def begin_transaction(self, transaction_id: str) -> bool:
        """Begin database transaction"""
        pass
    
    @abstractmethod
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit database transaction"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback database transaction"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check connection health"""
        pass
    
    def is_available(self) -> bool:
        """Check if connection is available for use"""
        return self.state == ConnectionState.IDLE and self.current_transaction_id is None
    
    def mark_active(self, transaction_id: Optional[str] = None):
        """Mark connection as active"""
        self.state = ConnectionState.ACTIVE
        self.current_transaction_id = transaction_id
        self.last_used_at = time.time()
    
    def mark_idle(self):
        """Mark connection as idle"""
        self.state = ConnectionState.IDLE
        self.current_transaction_id = None
        self.last_used_at = time.time()
    
    def mark_invalid(self):
        """Mark connection as invalid"""
        self.state = ConnectionState.INVALID


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection implementation"""
    
    async def connect(self) -> bool:
        """Establish PostgreSQL connection"""
        try:
            # Simulate PostgreSQL connection
            logger.debug(f"Connecting PostgreSQL connection {self.connection_id}")
            await asyncio.sleep(0.01)  # Simulate connection time
            self._connection = {"type": "postgresql", "connected": True}
            self.state = ConnectionState.IDLE
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            self.state = ConnectionState.INVALID
            return False
    
    async def disconnect(self) -> bool:
        """Close PostgreSQL connection"""
        try:
            if self._connection:
                self._connection = None
            self.state = ConnectionState.CLOSED
            logger.debug(f"Disconnected PostgreSQL connection {self.connection_id}")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL disconnect failed: {e}")
            return False
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute PostgreSQL query"""
        if self.state != ConnectionState.ACTIVE:
            raise ConnectionError(f"Connection {self.connection_id} not active")
        
        try:
            # Simulate query execution
            logger.debug(f"Executing PostgreSQL query: {query[:50]}...")
            await asyncio.sleep(0.005)  # Simulate query time
            return {"rows_affected": 1, "data": [{"id": 1, "result": "success"}]}
        except Exception as e:
            logger.error(f"PostgreSQL query execution failed: {e}")
            raise ConnectionError(f"Query execution failed: {e}")
    
    async def begin_transaction(self, transaction_id: str) -> bool:
        """Begin PostgreSQL transaction"""
        try:
            logger.debug(f"Beginning PostgreSQL transaction {transaction_id}")
            await asyncio.sleep(0.001)
            return True
        except Exception as e:
            logger.error(f"PostgreSQL begin transaction failed: {e}")
            return False
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit PostgreSQL transaction"""
        try:
            logger.debug(f"Committing PostgreSQL transaction {transaction_id}")
            await asyncio.sleep(0.002)
            return True
        except Exception as e:
            logger.error(f"PostgreSQL commit failed: {e}")
            return False
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback PostgreSQL transaction"""
        try:
            logger.debug(f"Rolling back PostgreSQL transaction {transaction_id}")
            await asyncio.sleep(0.002)
            return True
        except Exception as e:
            logger.error(f"PostgreSQL rollback failed: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check PostgreSQL connection health"""
        try:
            if not self._connection or not self._connection.get("connected"):
                return False
            
            # Simulate health check query
            await asyncio.sleep(0.001)
            return True
        except Exception as e:
            logger.warning(f"PostgreSQL health check failed: {e}")
            return False


class ConnectionPool:
    """Advanced connection pool with health monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Pool configuration
        self.min_connections = config.get("min_connections", 5)
        self.max_connections = config.get("max_connections", 20)
        self.connection_timeout = config.get("connection_timeout", 30.0)
        self.idle_timeout = config.get("idle_timeout", 300.0)  # 5 minutes
        self.health_check_interval = config.get("health_check_interval", 60.0)  # 1 minute
        self.max_connection_age = config.get("max_connection_age", 3600.0)  # 1 hour
        self.database_type = config.get("database_type", "postgresql")
        
        # Pool state
        self.state = PoolState.INITIALIZING
        self.connections: Dict[str, DatabaseConnection] = {}
        self.connection_metrics: Dict[str, ConnectionMetrics] = {}
        self.pool_metrics = PoolMetrics()
        self.wait_queue: List[asyncio.Future] = []
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._started_at = time.time()
        
        logger.info(f"Connection pool initialized: {self.min_connections}-{self.max_connections} connections")
    
    async def initialize(self):
        """Initialize connection pool"""
        logger.info("Initializing connection pool")
        
        try:
            # Create minimum connections
            for i in range(self.min_connections):
                connection = await self._create_connection()
                if connection:
                    await self._add_connection(connection)
            
            # Start background tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.state = PoolState.ACTIVE
            self.pool_metrics.uptime = time.time() - self._started_at
            
            logger.info(f"Connection pool initialized with {len(self.connections)} connections")
            
        except Exception as e:
            self.state = PoolState.DEGRADED
            logger.error(f"Connection pool initialization failed: {e}")
            raise ConnectionPoolError(f"Pool initialization failed: {e}")
    
    async def acquire_connection(self, transaction_id: Optional[str] = None, timeout: Optional[float] = None) -> DatabaseConnection:
        """Acquire connection from pool"""
        if self.state == PoolState.SHUTDOWN:
            raise ConnectionPoolError("Connection pool is shutdown")
        
        start_time = time.time()
        timeout = timeout or self.connection_timeout
        
        try:
            # Try to find available connection
            connection = await self._get_available_connection(transaction_id)
            
            if connection:
                wait_time = time.time() - start_time
                await self._update_pool_metrics(wait_time, True)
                return connection
            
            # Create new connection if under limit
            if len(self.connections) < self.max_connections:
                connection = await self._create_connection()
                if connection:
                    await self._add_connection(connection)
                    connection.mark_active(transaction_id)
                    
                    wait_time = time.time() - start_time
                    await self._update_pool_metrics(wait_time, True)
                    return connection
            
            # Wait for available connection
            future = asyncio.Future()
            self.wait_queue.append(future)
            
            try:
                connection = await asyncio.wait_for(future, timeout=timeout - (time.time() - start_time))
                connection.mark_active(transaction_id)
                
                wait_time = time.time() - start_time
                await self._update_pool_metrics(wait_time, True)
                return connection
                
            except asyncio.TimeoutError:
                if future in self.wait_queue:
                    self.wait_queue.remove(future)
                raise ConnectionTimeoutError(f"Connection acquisition timed out after {timeout}s")
            
        except Exception as e:
            await self._update_pool_metrics(time.time() - start_time, False)
            raise
    
    async def release_connection(self, connection: DatabaseConnection):
        """Release connection back to pool"""
        try:
            connection.mark_idle()
            
            # Update connection metrics
            if connection.connection_id in self.connection_metrics:
                metrics = self.connection_metrics[connection.connection_id]
                metrics.usage_count += 1
                metrics.last_used_at = time.time()
                metrics.state = ConnectionState.IDLE
                metrics.transaction_id = None
            
            # Notify waiting clients
            if self.wait_queue:
                future = self.wait_queue.pop(0)
                if not future.cancelled():
                    future.set_result(connection)
            
            logger.debug(f"Released connection {connection.connection_id}")
            
        except Exception as e:
            logger.error(f"Connection release failed: {e}")
            connection.mark_invalid()
    
    @asynccontextmanager
    async def connection(self, transaction_id: Optional[str] = None, timeout: Optional[float] = None):
        """Context manager for automatic connection management"""
        connection = await self.acquire_connection(transaction_id, timeout)
        
        try:
            yield connection
        finally:
            await self.release_connection(connection)
    
    async def _get_available_connection(self, transaction_id: Optional[str] = None) -> Optional[DatabaseConnection]:
        """Get available connection from pool"""
        for connection in self.connections.values():
            if connection.is_available():
                # Check if connection is still healthy
                if await connection.health_check():
                    connection.mark_active(transaction_id)
                    return connection
                else:
                    # Mark as invalid and continue
                    connection.mark_invalid()
        
        return None
    
    async def _create_connection(self) -> Optional[DatabaseConnection]:
        """Create new database connection"""
        try:
            connection_id = str(uuid.uuid4())
            
            if self.database_type == "postgresql":
                connection = PostgreSQLConnection(connection_id, self.config)
            else:
                raise ValueError(f"Unsupported database type: {self.database_type}")
            
            if await connection.connect():
                return connection
            else:
                return None
                
        except Exception as e:
            logger.error(f"Connection creation failed: {e}")
            return None
    
    async def _add_connection(self, connection: DatabaseConnection):
        """Add connection to pool"""
        self.connections[connection.connection_id] = connection
        
        # Initialize metrics
        self.connection_metrics[connection.connection_id] = ConnectionMetrics(
            connection_id=connection.connection_id,
            created_at=connection.created_at,
            last_used_at=connection.last_used_at,
            state=connection.state
        )
        
        # Update pool metrics
        self.pool_metrics.total_connections = len(self.connections)
        self._update_connection_counts()
        
        logger.debug(f"Added connection {connection.connection_id} to pool")
    
    async def _remove_connection(self, connection_id: str):
        """Remove connection from pool"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            await connection.disconnect()
            
            del self.connections[connection_id]
            del self.connection_metrics[connection_id]
            
            # Update pool metrics
            self.pool_metrics.total_connections = len(self.connections)
            self._update_connection_counts()
            
            logger.debug(f"Removed connection {connection_id} from pool")
    
    def _update_connection_counts(self):
        """Update connection count metrics"""
        self.pool_metrics.active_connections = sum(
            1 for conn in self.connections.values()
            if conn.state == ConnectionState.ACTIVE
        )
        self.pool_metrics.idle_connections = sum(
            1 for conn in self.connections.values()
            if conn.state == ConnectionState.IDLE
        )
        self.pool_metrics.invalid_connections = sum(
            1 for conn in self.connections.values()
            if conn.state == ConnectionState.INVALID
        )
        
        # Update peak usage
        self.pool_metrics.peak_usage = max(
            self.pool_metrics.peak_usage,
            self.pool_metrics.active_connections
        )
    
    async def _update_pool_metrics(self, wait_time: float, success: bool):
        """Update pool-level metrics"""
        self.pool_metrics.total_requests += 1
        
        if success:
            self.pool_metrics.successful_requests += 1
        else:
            self.pool_metrics.failed_requests += 1
        
        # Update average wait time
        total_wait_time = self.pool_metrics.avg_wait_time * (self.pool_metrics.total_requests - 1)
        self.pool_metrics.avg_wait_time = (total_wait_time + wait_time) / self.pool_metrics.total_requests
        
        self.pool_metrics.uptime = time.time() - self._started_at
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while self.state != PoolState.SHUTDOWN:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all connections"""
        logger.debug("Performing connection health checks")
        
        invalid_connections = []
        
        for connection_id, connection in self.connections.items():
            if connection.state != ConnectionState.ACTIVE:  # Don't check active connections
                try:
                    connection.state = ConnectionState.TESTING
                    healthy = await connection.health_check()
                    
                    if healthy:
                        connection.state = ConnectionState.IDLE
                    else:
                        connection.mark_invalid()
                        invalid_connections.append(connection_id)
                        
                except Exception as e:
                    logger.warning(f"Health check failed for connection {connection_id}: {e}")
                    connection.mark_invalid()
                    invalid_connections.append(connection_id)
        
        # Remove invalid connections
        for connection_id in invalid_connections:
            await self._remove_connection(connection_id)
        
        # Ensure minimum connections
        while len(self.connections) < self.min_connections:
            connection = await self._create_connection()
            if connection:
                await self._add_connection(connection)
            else:
                break  # Can't create connections, pool is degraded
        
        # Update pool state
        if len(self.connections) < self.min_connections:
            self.state = PoolState.DEGRADED
        elif self.state == PoolState.DEGRADED and len(self.connections) >= self.min_connections:
            self.state = PoolState.ACTIVE
        
        self._update_connection_counts()
    
    async def _cleanup_loop(self):
        """Background cleanup loop for idle and old connections"""
        while self.state != PoolState.SHUTDOWN:
            try:
                await asyncio.sleep(self.idle_timeout / 4)  # Check every quarter of idle timeout
                await self._cleanup_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_connections(self):
        """Cleanup idle and old connections"""
        current_time = time.time()
        connections_to_remove = []
        
        for connection_id, connection in self.connections.items():
            # Skip active connections
            if connection.state == ConnectionState.ACTIVE:
                continue
            
            # Remove old connections
            if current_time - connection.created_at > self.max_connection_age:
                connections_to_remove.append(connection_id)
                continue
            
            # Remove idle connections if we have more than minimum
            if (connection.state == ConnectionState.IDLE and 
                current_time - connection.last_used_at > self.idle_timeout and
                len(self.connections) > self.min_connections):
                connections_to_remove.append(connection_id)
        
        # Remove selected connections
        for connection_id in connections_to_remove:
            await self._remove_connection(connection_id)
        
        if connections_to_remove:
            logger.debug(f"Cleaned up {len(connections_to_remove)} connections")
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics"""
        self._update_connection_counts()
        
        # Connection metrics statistics
        if self.connection_metrics:
            response_times = [
                metrics.avg_response_time for metrics in self.connection_metrics.values()
                if metrics.avg_response_time > 0
            ]
            
            avg_response_time = statistics.mean(response_times) if response_times else 0.0
        else:
            avg_response_time = 0.0
        
        return {
            "pool_state": self.state.value,
            "total_connections": self.pool_metrics.total_connections,
            "active_connections": self.pool_metrics.active_connections,
            "idle_connections": self.pool_metrics.idle_connections,
            "invalid_connections": self.pool_metrics.invalid_connections,
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
            "total_requests": self.pool_metrics.total_requests,
            "successful_requests": self.pool_metrics.successful_requests,
            "failed_requests": self.pool_metrics.failed_requests,
            "success_rate": self.pool_metrics.successful_requests / max(self.pool_metrics.total_requests, 1),
            "avg_wait_time": self.pool_metrics.avg_wait_time,
            "avg_response_time": avg_response_time,
            "peak_usage": self.pool_metrics.peak_usage,
            "uptime": self.pool_metrics.uptime,
            "queue_length": len(self.wait_queue)
        }
    
    async def shutdown(self):
        """Shutdown connection pool"""
        logger.info("Shutting down connection pool")
        
        self.state = PoolState.SHUTDOWN
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel waiting requests
        for future in self.wait_queue:
            if not future.cancelled():
                future.cancel()
        self.wait_queue.clear()
        
        # Close all connections
        for connection_id in list(self.connections.keys()):
            await self._remove_connection(connection_id)
        
        logger.info("Connection pool shutdown complete")


# Test harness
if __name__ == "__main__":
    async def test_connection_pool():
        """Test connection pool functionality"""
        
        config = {
            "min_connections": 3,
            "max_connections": 10,
            "connection_timeout": 5.0,
            "idle_timeout": 30.0,
            "health_check_interval": 10.0,
            "max_connection_age": 60.0,
            "database_type": "postgresql"
        }
        
        pool = ConnectionPool(config)
        
        try:
            print("🔧 Testing Connection Pool...")
            
            # Initialize pool
            await pool.initialize()
            print(f"✅ Pool initialized with {len(pool.connections)} connections")
            
            # Test connection acquisition
            async with pool.connection() as conn:
                print(f"✅ Acquired connection: {conn.connection_id}")
                
                # Test query execution
                result = await conn.execute("SELECT 1")
                print(f"✅ Query executed: {result}")
            
            print("✅ Connection released automatically")
            
            # Test multiple concurrent connections
            print("\n🔄 Testing Concurrent Connections...")
            
            async def use_connection(conn_num):
                async with pool.connection() as conn:
                    await asyncio.sleep(0.1)  # Simulate work
                    return f"Connection {conn_num} completed"
            
            # Run concurrent connections
            tasks = [use_connection(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            print(f"✅ Concurrent connections completed: {len(results)}")
            
            # Test transaction support
            print("\n🔄 Testing Transaction Support...")
            
            async with pool.connection(transaction_id="tx123") as conn:
                await conn.begin_transaction("tx123")
                print("✅ Transaction started")
                
                await conn.execute("INSERT INTO users VALUES (1, 'test')")
                print("✅ Transaction operation executed")
                
                await conn.commit_transaction("tx123")
                print("✅ Transaction committed")
            
            # Test pool statistics
            print("\n📊 Testing Pool Statistics...")
            stats = pool.get_pool_statistics()
            print(f"✅ Pool statistics: {stats}")
            
            # Test pool shutdown
            await pool.shutdown()
            print("✅ Pool shutdown successful")
            
        except Exception as e:
            print(f"❌ Connection pool test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_connection_pool())