"""
V5.0 Database Connection Manager with Advanced Pooling
Implements comprehensive database connection management with health checking and multi-database support
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
import weakref

logger = logging.getLogger(__name__)


@dataclass
class PoolConfiguration:
    """Connection pool configuration settings"""
    min_connections: int = 5
    max_connections: int = 20
    max_idle_time: int = 300  # seconds
    connection_timeout: int = 30  # seconds
    health_check_interval: int = 60  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class ConnectionHealth:
    """Connection health status"""
    healthy: bool
    last_check: float
    error_count: int = 0
    response_time: float = 0.0


class UnsupportedDatabaseError(Exception):
    """Raised when database type is not supported"""
    pass


class ConnectionPoolError(Exception):
    """Raised when connection pool operations fail"""
    pass


class ConnectionHealthError(Exception):
    """Raised when connection fails health check"""
    pass


class DatabaseConnection(Protocol):
    """Protocol for database connections"""
    
    async def execute(self, query: str, *args) -> Any:
        """Execute a query"""
        pass
    
    async def close(self) -> None:
        """Close the connection"""
        pass


class ManagedConnection:
    """Wrapper for database connections with metadata"""
    
    def __init__(self, connection: DatabaseConnection, connection_id: str):
        self.connection = connection
        self.connection_id = connection_id
        self.created_at = time.time()
        self.last_used = time.time()
        self.use_count = 0
        self.health = ConnectionHealth(healthy=True, last_check=time.time())
        self.in_use = False
    
    def mark_used(self):
        """Mark connection as used"""
        self.last_used = time.time()
        self.use_count += 1
    
    def is_idle_too_long(self, max_idle_time: int) -> bool:
        """Check if connection has been idle too long"""
        return (time.time() - self.last_used) > max_idle_time
    
    def needs_health_check(self, interval: int) -> bool:
        """Check if connection needs health check"""
        return (time.time() - self.health.last_check) > interval


class DatabaseConnectionManager:
    """Advanced database connection management with pooling and health checking"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.database_type = config.get("database_type", "postgresql")
        self.pool_config = self._configure_pool_settings(config.get("pool", {}))
        
        # Connection pools
        self.available_connections = asyncio.Queue()
        self.all_connections: Dict[str, ManagedConnection] = {}
        self.connection_counter = 0
        
        # Pool state
        self.pool_initialized = False
        self.shutting_down = False
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "connections_created": 0,
            "connections_destroyed": 0,
            "total_requests": 0,
            "failed_requests": 0,
            "health_check_failures": 0
        }
        
        logger.info(f"DatabaseConnectionManager initialized for {self.database_type}")
    
    def _configure_pool_settings(self, pool_config: Dict[str, Any]) -> PoolConfiguration:
        """Configure connection pool settings"""
        return PoolConfiguration(
            min_connections=pool_config.get("min_connections", 5),
            max_connections=pool_config.get("max_connections", 20),
            max_idle_time=pool_config.get("max_idle_time", 300),
            connection_timeout=pool_config.get("connection_timeout", 30),
            health_check_interval=pool_config.get("health_check_interval", 60),
            retry_attempts=pool_config.get("retry_attempts", 3),
            retry_delay=pool_config.get("retry_delay", 1.0)
        )
    
    async def initialize_pool(self):
        """Initialize connection pool based on database type"""
        if self.pool_initialized:
            logger.warning("Connection pool already initialized")
            return
        
        logger.info(f"Initializing connection pool for {self.database_type}")
        
        try:
            # Create initial connections
            for _ in range(self.pool_config.min_connections):
                connection = await self._create_connection()
                await self.available_connections.put(connection)
            
            # Start health monitoring
            self.health_check_task = asyncio.create_task(self._health_monitor())
            
            self.pool_initialized = True
            logger.info(f"Connection pool initialized with {self.pool_config.min_connections} connections")
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise ConnectionPoolError(f"Pool initialization failed: {e}")
    
    async def get_connection(self) -> ManagedConnection:
        """Get connection from pool with health checking"""
        if not self.pool_initialized:
            raise ConnectionPoolError("Connection pool not initialized")
        
        if self.shutting_down:
            raise ConnectionPoolError("Connection pool is shutting down")
        
        self.stats["total_requests"] += 1
        
        for attempt in range(self.pool_config.retry_attempts):
            try:
                # Try to get connection from pool
                try:
                    connection = await asyncio.wait_for(
                        self.available_connections.get(),
                        timeout=self.pool_config.connection_timeout
                    )
                except asyncio.TimeoutError:
                    # Pool is empty, try to create new connection if under limit
                    if len(self.all_connections) < self.pool_config.max_connections:
                        connection = await self._create_connection()
                    else:
                        raise ConnectionPoolError("Connection pool exhausted and at maximum capacity")
                
                # Health check connection
                if await self._health_check_connection(connection):
                    connection.mark_used()
                    connection.in_use = True
                    logger.debug(f"Connection {connection.connection_id} acquired")
                    return connection
                else:
                    # Connection unhealthy, destroy and retry
                    await self._destroy_connection(connection)
                    continue
                
            except Exception as e:
                logger.warning(f"Connection acquisition attempt {attempt + 1} failed: {e}")
                if attempt == self.pool_config.retry_attempts - 1:
                    self.stats["failed_requests"] += 1
                    raise ConnectionPoolError(f"Failed to acquire connection after {self.pool_config.retry_attempts} attempts: {e}")
                
                await asyncio.sleep(self.pool_config.retry_delay)
        
        raise ConnectionPoolError("Failed to acquire connection")
    
    async def release_connection(self, connection: ManagedConnection):
        """Release connection back to pool"""
        if not isinstance(connection, ManagedConnection):
            logger.error("Invalid connection type for release")
            return
        
        if connection.connection_id not in self.all_connections:
            logger.warning(f"Attempting to release unknown connection {connection.connection_id}")
            return
        
        try:
            connection.in_use = False
            
            # Check if connection should be kept or destroyed
            if (connection.is_idle_too_long(self.pool_config.max_idle_time) or 
                not connection.health.healthy or
                self.shutting_down):
                await self._destroy_connection(connection)
            else:
                await self.available_connections.put(connection)
                logger.debug(f"Connection {connection.connection_id} released to pool")
                
        except Exception as e:
            logger.error(f"Error releasing connection {connection.connection_id}: {e}")
            await self._destroy_connection(connection)
    
    async def _create_connection(self) -> ManagedConnection:
        """Create new database connection"""
        connection_id = f"conn_{self.connection_counter}"
        self.connection_counter += 1
        
        try:
            if self.database_type == "postgresql":
                raw_connection = await self._create_postgresql_connection()
            elif self.database_type == "mysql":
                raw_connection = await self._create_mysql_connection()
            elif self.database_type == "sqlite":
                raw_connection = await self._create_sqlite_connection()
            else:
                raise UnsupportedDatabaseError(f"Database type {self.database_type} not supported")
            
            managed_connection = ManagedConnection(raw_connection, connection_id)
            self.all_connections[connection_id] = managed_connection
            self.stats["connections_created"] += 1
            
            logger.debug(f"Created connection {connection_id}")
            return managed_connection
            
        except Exception as e:
            logger.error(f"Failed to create connection {connection_id}: {e}")
            raise ConnectionPoolError(f"Connection creation failed: {e}")
    
    async def _create_postgresql_connection(self):
        """Create PostgreSQL connection"""
        try:
            import asyncpg
            
            connection = await asyncpg.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
                user=self.config.get("user", "postgres"),
                password=self.config.get("password", ""),
                database=self.config.get("database", "postgres"),
                timeout=self.pool_config.connection_timeout
            )
            
            return PostgreSQLConnectionWrapper(connection)
            
        except ImportError:
            raise ConnectionPoolError("asyncpg library required for PostgreSQL connections")
        except Exception as e:
            raise ConnectionPoolError(f"PostgreSQL connection failed: {e}")
    
    async def _create_mysql_connection(self):
        """Create MySQL connection"""
        try:
            import aiomysql
            
            connection = await aiomysql.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 3306),
                user=self.config.get("user", "root"),
                password=self.config.get("password", ""),
                db=self.config.get("database", "mysql"),
                connect_timeout=self.pool_config.connection_timeout
            )
            
            return MySQLConnectionWrapper(connection)
            
        except ImportError:
            raise ConnectionPoolError("aiomysql library required for MySQL connections")
        except Exception as e:
            raise ConnectionPoolError(f"MySQL connection failed: {e}")
    
    async def _create_sqlite_connection(self):
        """Create SQLite connection"""
        try:
            import aiosqlite
            
            database_path = self.config.get("database_path", ":memory:")
            connection = await aiosqlite.connect(database_path)
            
            return SQLiteConnectionWrapper(connection)
            
        except ImportError:
            raise ConnectionPoolError("aiosqlite library required for SQLite connections")
        except Exception as e:
            raise ConnectionPoolError(f"SQLite connection failed: {e}")
    
    async def _health_check_connection(self, connection: ManagedConnection) -> bool:
        """Perform health check on connection"""
        if not connection.needs_health_check(self.pool_config.health_check_interval):
            return connection.health.healthy
        
        start_time = time.time()
        
        try:
            # Perform simple query to test connection
            await connection.connection.execute("SELECT 1")
            
            response_time = time.time() - start_time
            connection.health = ConnectionHealth(
                healthy=True,
                last_check=time.time(),
                error_count=0,
                response_time=response_time
            )
            
            return True
            
        except Exception as e:
            connection.health.error_count += 1
            connection.health.healthy = False
            connection.health.last_check = time.time()
            
            self.stats["health_check_failures"] += 1
            logger.warning(f"Health check failed for connection {connection.connection_id}: {e}")
            
            return False
    
    async def _destroy_connection(self, connection: ManagedConnection):
        """Destroy connection and remove from pool"""
        try:
            await connection.connection.close()
            
            if connection.connection_id in self.all_connections:
                del self.all_connections[connection.connection_id]
            
            self.stats["connections_destroyed"] += 1
            logger.debug(f"Destroyed connection {connection.connection_id}")
            
        except Exception as e:
            logger.error(f"Error destroying connection {connection.connection_id}: {e}")
    
    async def _health_monitor(self):
        """Background task to monitor connection health"""
        logger.info("Starting connection health monitor")
        
        while not self.shutting_down:
            try:
                # Check all connections for health
                unhealthy_connections = []
                
                for connection in self.all_connections.values():
                    if not connection.in_use and not await self._health_check_connection(connection):
                        unhealthy_connections.append(connection)
                
                # Remove unhealthy connections
                for connection in unhealthy_connections:
                    await self._destroy_connection(connection)
                
                # Ensure minimum connections
                current_count = len(self.all_connections)
                if current_count < self.pool_config.min_connections:
                    needed = self.pool_config.min_connections - current_count
                    for _ in range(needed):
                        try:
                            new_connection = await self._create_connection()
                            await self.available_connections.put(new_connection)
                        except Exception as e:
                            logger.error(f"Failed to create replacement connection: {e}")
                            break
                
                await asyncio.sleep(self.pool_config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.pool_config.health_check_interval)
        
        logger.info("Connection health monitor stopped")
    
    async def cleanup(self):
        """Clean up connection pool"""
        logger.info("Shutting down connection pool")
        
        self.shutting_down = True
        
        # Stop health monitor
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for connection in list(self.all_connections.values()):
            await self._destroy_connection(connection)
        
        # Clear queue
        while not self.available_connections.empty():
            try:
                self.available_connections.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logger.info(f"Connection pool shutdown complete. Stats: {self.stats}")
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "total_connections": len(self.all_connections),
            "available_connections": self.available_connections.qsize(),
            "connections_in_use": sum(1 for c in self.all_connections.values() if c.in_use),
            "pool_config": {
                "min_connections": self.pool_config.min_connections,
                "max_connections": self.pool_config.max_connections
            },
            "statistics": self.stats.copy()
        }


# Connection wrapper classes to provide consistent interface

class PostgreSQLConnectionWrapper:
    """Wrapper for PostgreSQL connections"""
    
    def __init__(self, connection):
        self.connection = connection
    
    async def execute(self, query: str, *args) -> Any:
        if args:
            return await self.connection.fetch(query, *args)
        else:
            return await self.connection.fetch(query)
    
    async def close(self) -> None:
        await self.connection.close()


class MySQLConnectionWrapper:
    """Wrapper for MySQL connections"""
    
    def __init__(self, connection):
        self.connection = connection
    
    async def execute(self, query: str, *args) -> Any:
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchall()
    
    async def close(self) -> None:
        await self.connection.ensure_closed()


class SQLiteConnectionWrapper:
    """Wrapper for SQLite connections"""
    
    def __init__(self, connection):
        self.connection = connection
    
    async def execute(self, query: str, *args) -> Any:
        if args:
            async with self.connection.execute(query, args) as cursor:
                return await cursor.fetchall()
        else:
            async with self.connection.execute(query) as cursor:
                return await cursor.fetchall()
    
    async def close(self) -> None:
        await self.connection.close()


# Test harness
if __name__ == "__main__":
    async def test_connection_manager():
        """Test connection manager functionality"""
        
        # Test with mock SQLite configuration
        config = {
            "database_type": "sqlite",
            "database_path": ":memory:",
            "pool": {
                "min_connections": 2,
                "max_connections": 5,
                "connection_timeout": 10
            }
        }
        
        manager = DatabaseConnectionManager(config)
        
        try:
            # Test pool initialization
            await manager.initialize_pool()
            print("✅ Connection pool initialized successfully")
            
            # Test connection acquisition
            conn1 = await manager.get_connection()
            print(f"✅ Connection acquired: {conn1.connection_id}")
            
            # Test health check
            healthy = await manager._health_check_connection(conn1)
            print(f"✅ Connection health check: {healthy}")
            
            # Test connection release
            await manager.release_connection(conn1)
            print("✅ Connection released successfully")
            
            # Test pool statistics
            stats = manager.get_pool_statistics()
            print(f"✅ Pool statistics: {stats}")
            
            # Test cleanup
            await manager.cleanup()
            print("✅ Connection manager cleanup successful")
            
        except Exception as e:
            print(f"❌ Connection manager test failed: {e}")
    
    asyncio.run(test_connection_manager())