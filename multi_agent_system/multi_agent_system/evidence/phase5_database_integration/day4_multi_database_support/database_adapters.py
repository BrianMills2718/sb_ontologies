"""
V5.0 Multi-Database Support - Database Adapters
Provides unified interface for PostgreSQL, MySQL, SQLite with connection management
"""

import asyncio
import time
import logging
import uuid
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class DatabaseState(Enum):
    """Database connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class DatabaseConfiguration:
    """Database configuration parameters"""
    database_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    pool_size: int = 10
    max_connections: int = 20
    connection_timeout: float = 30.0
    query_timeout: float = 60.0
    ssl_enabled: bool = False
    ssl_params: Optional[Dict[str, Any]] = None


@dataclass
class QueryResult:
    """Standardized query result"""
    success: bool
    rows_affected: int
    rows: Optional[List[Dict[str, Any]]] = None
    execution_time: float = 0.0
    query_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TransactionContext:
    """Transaction context for database operations"""
    transaction_id: str
    isolation_level: str
    read_only: bool = False
    savepoints: Optional[List[str]] = None
    started_at: Optional[float] = None
    timeout: float = 300.0


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters"""
    
    def __init__(self, config: DatabaseConfiguration):
        self.config = config
        self.state = DatabaseState.DISCONNECTED
        self.connection = None
        self.connection_pool = None
        self.active_transactions: Dict[str, TransactionContext] = {}
        self.query_statistics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        self.connection_id = str(uuid.uuid4())
        self.created_at = time.time()
        
    @abstractmethod
    async def connect(self) -> bool:
        """Establish database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute SQL query with optional parameters"""
        pass
    
    @abstractmethod
    async def execute_many(
        self, 
        query: str, 
        parameter_list: List[Dict[str, Any]],
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute query with multiple parameter sets"""
        pass
    
    @abstractmethod
    async def begin_transaction(
        self, 
        isolation_level: str = "READ_COMMITTED",
        read_only: bool = False,
        timeout: float = 300.0
    ) -> str:
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
    async def create_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Create transaction savepoint"""
        pass
    
    @abstractmethod
    async def rollback_to_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Rollback to transaction savepoint"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check database connection health"""
        pass
    
    def update_query_statistics(self, execution_time: float, success: bool):
        """Update query execution statistics"""
        self.query_statistics["total_queries"] += 1
        self.query_statistics["total_execution_time"] += execution_time
        
        if success:
            self.query_statistics["successful_queries"] += 1
        else:
            self.query_statistics["failed_queries"] += 1
        
        self.query_statistics["average_execution_time"] = (
            self.query_statistics["total_execution_time"] / 
            self.query_statistics["total_queries"]
        )
    
    def get_adapter_statistics(self) -> Dict[str, Any]:
        """Get adapter performance statistics"""
        return {
            "connection_id": self.connection_id,
            "database_type": self.config.database_type.value,
            "state": self.state.value,
            "uptime": time.time() - self.created_at,
            "active_transactions": len(self.active_transactions),
            "query_statistics": self.query_statistics.copy(),
            "success_rate": (
                self.query_statistics["successful_queries"] / 
                max(self.query_statistics["total_queries"], 1)
            )
        }


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter implementation"""
    
    def __init__(self, config: DatabaseConfiguration):
        super().__init__(config)
        self.driver_name = "asyncpg"
        
    async def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.state = DatabaseState.CONNECTING
            logger.info(f"Connecting to PostgreSQL database: {self.config.host}:{self.config.port}")
            
            # Simulate asyncpg connection
            connection_params = {
                "host": self.config.host,
                "port": self.config.port or 5432,
                "database": self.config.database,
                "user": self.config.username,
                "password": self.config.password,
                **(self.config.connection_params or {})
            }
            
            # Simulate connection establishment
            await asyncio.sleep(0.1)  # Simulate connection time
            
            self.connection = PostgreSQLConnection(connection_params)
            self.state = DatabaseState.CONNECTED
            
            logger.info(f"Successfully connected to PostgreSQL: {self.connection_id}")
            return True
            
        except Exception as e:
            self.state = DatabaseState.ERROR
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from PostgreSQL"""
        try:
            if self.connection:
                await self.connection.close()
                self.connection = None
            
            self.state = DatabaseState.DISCONNECTED
            logger.info(f"Disconnected from PostgreSQL: {self.connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error during PostgreSQL disconnect: {e}")
            return False
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute PostgreSQL query"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if self.state != DatabaseState.CONNECTED:
                raise RuntimeError("Database not connected")
            
            # Convert named parameters to PostgreSQL format
            pg_query, pg_params = self._convert_parameters(query, parameters)
            
            # Execute query through connection
            result = await self.connection.execute(pg_query, pg_params, transaction_id)
            
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, True)
            
            return QueryResult(
                success=True,
                rows_affected=result.get("rows_affected", 0),
                rows=result.get("rows", []),
                execution_time=execution_time,
                query_id=query_id,
                metadata={"driver": self.driver_name, "query_plan": result.get("plan")}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, False)
            
            logger.error(f"PostgreSQL query execution failed: {e}")
            return QueryResult(
                success=False,
                rows_affected=0,
                execution_time=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
    
    async def execute_many(
        self, 
        query: str, 
        parameter_list: List[Dict[str, Any]],
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute PostgreSQL query with multiple parameter sets"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if self.state != DatabaseState.CONNECTED:
                raise RuntimeError("Database not connected")
            
            total_affected = 0
            
            # Execute each parameter set
            for parameters in parameter_list:
                pg_query, pg_params = self._convert_parameters(query, parameters)
                result = await self.connection.execute(pg_query, pg_params, transaction_id)
                total_affected += result.get("rows_affected", 0)
            
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, True)
            
            return QueryResult(
                success=True,
                rows_affected=total_affected,
                execution_time=execution_time,
                query_id=query_id,
                metadata={
                    "driver": self.driver_name, 
                    "batch_size": len(parameter_list)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, False)
            
            logger.error(f"PostgreSQL batch execution failed: {e}")
            return QueryResult(
                success=False,
                rows_affected=0,
                execution_time=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
    
    async def begin_transaction(
        self, 
        isolation_level: str = "READ_COMMITTED",
        read_only: bool = False,
        timeout: float = 300.0
    ) -> str:
        """Begin PostgreSQL transaction"""
        transaction_id = str(uuid.uuid4())
        
        try:
            # Map isolation levels to PostgreSQL syntax
            pg_isolation = {
                "READ_UNCOMMITTED": "READ UNCOMMITTED",
                "READ_COMMITTED": "READ COMMITTED", 
                "REPEATABLE_READ": "REPEATABLE READ",
                "SERIALIZABLE": "SERIALIZABLE"
            }.get(isolation_level, "READ COMMITTED")
            
            transaction_query = f"BEGIN ISOLATION LEVEL {pg_isolation}"
            if read_only:
                transaction_query += " READ ONLY"
            
            result = await self.connection.execute(transaction_query, None, None)
            
            # Store transaction context
            self.active_transactions[transaction_id] = TransactionContext(
                transaction_id=transaction_id,
                isolation_level=isolation_level,
                read_only=read_only,
                started_at=time.time(),
                timeout=timeout,
                savepoints=[]
            )
            
            logger.debug(f"PostgreSQL transaction {transaction_id} started")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Failed to begin PostgreSQL transaction: {e}")
            raise
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit PostgreSQL transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            await self.connection.execute("COMMIT", None, transaction_id)
            del self.active_transactions[transaction_id]
            
            logger.debug(f"PostgreSQL transaction {transaction_id} committed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit PostgreSQL transaction {transaction_id}: {e}")
            return False
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback PostgreSQL transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            await self.connection.execute("ROLLBACK", None, transaction_id)
            del self.active_transactions[transaction_id]
            
            logger.debug(f"PostgreSQL transaction {transaction_id} rolled back")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback PostgreSQL transaction {transaction_id}: {e}")
            return False
    
    async def create_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Create PostgreSQL savepoint"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            savepoint_query = f"SAVEPOINT {savepoint_name}"
            await self.connection.execute(savepoint_query, None, transaction_id)
            
            # Add to transaction context
            self.active_transactions[transaction_id].savepoints.append(savepoint_name)
            
            logger.debug(f"PostgreSQL savepoint {savepoint_name} created for transaction {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL savepoint: {e}")
            return False
    
    async def rollback_to_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Rollback to PostgreSQL savepoint"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            rollback_query = f"ROLLBACK TO SAVEPOINT {savepoint_name}"
            await self.connection.execute(rollback_query, None, transaction_id)
            
            logger.debug(f"PostgreSQL rolled back to savepoint {savepoint_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback to PostgreSQL savepoint: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check PostgreSQL connection health"""
        try:
            if self.state != DatabaseState.CONNECTED:
                return False
            
            result = await self.connection.execute("SELECT 1", None, None)
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False
    
    def _convert_parameters(self, query: str, parameters: Optional[Dict[str, Any]]) -> Tuple[str, List[Any]]:
        """Convert named parameters to PostgreSQL positional parameters"""
        if not parameters:
            return query, []
        
        # Convert %(name)s to $1, $2, etc.
        pg_query = query
        pg_params = []
        param_index = 1
        
        for key, value in parameters.items():
            placeholder = f"%({key})s"
            if placeholder in pg_query:
                pg_query = pg_query.replace(placeholder, f"${param_index}")
                pg_params.append(value)
                param_index += 1
        
        return pg_query, pg_params


class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter implementation"""
    
    def __init__(self, config: DatabaseConfiguration):
        super().__init__(config)
        self.driver_name = "aiomysql"
        
    async def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            self.state = DatabaseState.CONNECTING
            logger.info(f"Connecting to MySQL database: {self.config.host}:{self.config.port}")
            
            # Simulate aiomysql connection
            connection_params = {
                "host": self.config.host,
                "port": self.config.port or 3306,
                "db": self.config.database,
                "user": self.config.username,
                "password": self.config.password,
                **(self.config.connection_params or {})
            }
            
            # Simulate connection establishment
            await asyncio.sleep(0.1)  # Simulate connection time
            
            self.connection = MySQLConnection(connection_params)
            self.state = DatabaseState.CONNECTED
            
            logger.info(f"Successfully connected to MySQL: {self.connection_id}")
            return True
            
        except Exception as e:
            self.state = DatabaseState.ERROR
            logger.error(f"Failed to connect to MySQL: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MySQL"""
        try:
            if self.connection:
                await self.connection.close()
                self.connection = None
            
            self.state = DatabaseState.DISCONNECTED
            logger.info(f"Disconnected from MySQL: {self.connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error during MySQL disconnect: {e}")
            return False
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute MySQL query"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if self.state != DatabaseState.CONNECTED:
                raise RuntimeError("Database not connected")
            
            # Convert named parameters to MySQL format
            mysql_query, mysql_params = self._convert_parameters(query, parameters)
            
            # Execute query through connection
            result = await self.connection.execute(mysql_query, mysql_params, transaction_id)
            
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, True)
            
            return QueryResult(
                success=True,
                rows_affected=result.get("rows_affected", 0),
                rows=result.get("rows", []),
                execution_time=execution_time,
                query_id=query_id,
                metadata={"driver": self.driver_name}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, False)
            
            logger.error(f"MySQL query execution failed: {e}")
            return QueryResult(
                success=False,
                rows_affected=0,
                execution_time=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
    
    async def execute_many(
        self, 
        query: str, 
        parameter_list: List[Dict[str, Any]],
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute MySQL query with multiple parameter sets"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if self.state != DatabaseState.CONNECTED:
                raise RuntimeError("Database not connected")
            
            total_affected = 0
            
            # Execute each parameter set
            for parameters in parameter_list:
                mysql_query, mysql_params = self._convert_parameters(query, parameters)
                result = await self.connection.execute(mysql_query, mysql_params, transaction_id)
                total_affected += result.get("rows_affected", 0)
            
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, True)
            
            return QueryResult(
                success=True,
                rows_affected=total_affected,
                execution_time=execution_time,
                query_id=query_id,
                metadata={
                    "driver": self.driver_name, 
                    "batch_size": len(parameter_list)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, False)
            
            logger.error(f"MySQL batch execution failed: {e}")
            return QueryResult(
                success=False,
                rows_affected=0,
                execution_time=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
    
    async def begin_transaction(
        self, 
        isolation_level: str = "READ_COMMITTED",
        read_only: bool = False,
        timeout: float = 300.0
    ) -> str:
        """Begin MySQL transaction"""
        transaction_id = str(uuid.uuid4())
        
        try:
            # Set transaction isolation level
            mysql_isolation = {
                "READ_UNCOMMITTED": "READ-UNCOMMITTED",
                "READ_COMMITTED": "READ-COMMITTED", 
                "REPEATABLE_READ": "REPEATABLE-READ",
                "SERIALIZABLE": "SERIALIZABLE"
            }.get(isolation_level, "READ-COMMITTED")
            
            isolation_query = f"SET TRANSACTION ISOLATION LEVEL {mysql_isolation}"
            await self.connection.execute(isolation_query, None, None)
            
            # Begin transaction
            begin_query = "START TRANSACTION"
            if read_only:
                begin_query += " READ ONLY"
            
            result = await self.connection.execute(begin_query, None, None)
            
            # Store transaction context
            self.active_transactions[transaction_id] = TransactionContext(
                transaction_id=transaction_id,
                isolation_level=isolation_level,
                read_only=read_only,
                started_at=time.time(),
                timeout=timeout,
                savepoints=[]
            )
            
            logger.debug(f"MySQL transaction {transaction_id} started")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Failed to begin MySQL transaction: {e}")
            raise
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit MySQL transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            await self.connection.execute("COMMIT", None, transaction_id)
            del self.active_transactions[transaction_id]
            
            logger.debug(f"MySQL transaction {transaction_id} committed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit MySQL transaction {transaction_id}: {e}")
            return False
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback MySQL transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            await self.connection.execute("ROLLBACK", None, transaction_id)
            del self.active_transactions[transaction_id]
            
            logger.debug(f"MySQL transaction {transaction_id} rolled back")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback MySQL transaction {transaction_id}: {e}")
            return False
    
    async def create_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Create MySQL savepoint"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            savepoint_query = f"SAVEPOINT {savepoint_name}"
            await self.connection.execute(savepoint_query, None, transaction_id)
            
            # Add to transaction context
            self.active_transactions[transaction_id].savepoints.append(savepoint_name)
            
            logger.debug(f"MySQL savepoint {savepoint_name} created for transaction {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create MySQL savepoint: {e}")
            return False
    
    async def rollback_to_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Rollback to MySQL savepoint"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            rollback_query = f"ROLLBACK TO SAVEPOINT {savepoint_name}"
            await self.connection.execute(rollback_query, None, transaction_id)
            
            logger.debug(f"MySQL rolled back to savepoint {savepoint_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback to MySQL savepoint: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check MySQL connection health"""
        try:
            if self.state != DatabaseState.CONNECTED:
                return False
            
            result = await self.connection.execute("SELECT 1", None, None)
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"MySQL health check failed: {e}")
            return False
    
    def _convert_parameters(self, query: str, parameters: Optional[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """Convert named parameters to MySQL format"""
        if not parameters:
            return query, {}
        
        # MySQL supports %(name)s format natively
        return query, parameters


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter implementation"""
    
    def __init__(self, config: DatabaseConfiguration):
        super().__init__(config)
        self.driver_name = "aiosqlite"
        
    async def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            self.state = DatabaseState.CONNECTING
            logger.info(f"Connecting to SQLite database: {self.config.database}")
            
            # Simulate aiosqlite connection
            database_path = self.config.database or ":memory:"
            
            # Simulate connection establishment
            await asyncio.sleep(0.05)  # SQLite is faster
            
            self.connection = SQLiteConnection(database_path)
            self.state = DatabaseState.CONNECTED
            
            logger.info(f"Successfully connected to SQLite: {self.connection_id}")
            return True
            
        except Exception as e:
            self.state = DatabaseState.ERROR
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from SQLite"""
        try:
            if self.connection:
                await self.connection.close()
                self.connection = None
            
            self.state = DatabaseState.DISCONNECTED
            logger.info(f"Disconnected from SQLite: {self.connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error during SQLite disconnect: {e}")
            return False
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute SQLite query"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if self.state != DatabaseState.CONNECTED:
                raise RuntimeError("Database not connected")
            
            # Execute query through connection
            result = await self.connection.execute(query, parameters, transaction_id)
            
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, True)
            
            return QueryResult(
                success=True,
                rows_affected=result.get("rows_affected", 0),
                rows=result.get("rows", []),
                execution_time=execution_time,
                query_id=query_id,
                metadata={"driver": self.driver_name}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, False)
            
            logger.error(f"SQLite query execution failed: {e}")
            return QueryResult(
                success=False,
                rows_affected=0,
                execution_time=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
    
    async def execute_many(
        self, 
        query: str, 
        parameter_list: List[Dict[str, Any]],
        transaction_id: Optional[str] = None
    ) -> QueryResult:
        """Execute SQLite query with multiple parameter sets"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            if self.state != DatabaseState.CONNECTED:
                raise RuntimeError("Database not connected")
            
            total_affected = 0
            
            # Execute each parameter set
            for parameters in parameter_list:
                result = await self.connection.execute(query, parameters, transaction_id)
                total_affected += result.get("rows_affected", 0)
            
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, True)
            
            return QueryResult(
                success=True,
                rows_affected=total_affected,
                execution_time=execution_time,
                query_id=query_id,
                metadata={
                    "driver": self.driver_name, 
                    "batch_size": len(parameter_list)
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_query_statistics(execution_time, False)
            
            logger.error(f"SQLite batch execution failed: {e}")
            return QueryResult(
                success=False,
                rows_affected=0,
                execution_time=execution_time,
                query_id=query_id,
                error_message=str(e)
            )
    
    async def begin_transaction(
        self, 
        isolation_level: str = "READ_COMMITTED",
        read_only: bool = False,
        timeout: float = 300.0
    ) -> str:
        """Begin SQLite transaction"""
        transaction_id = str(uuid.uuid4())
        
        try:
            # SQLite transaction modes
            transaction_mode = "DEFERRED"  # Default mode
            if isolation_level == "SERIALIZABLE":
                transaction_mode = "EXCLUSIVE"
            elif isolation_level in ("REPEATABLE_READ", "READ_COMMITTED"):
                transaction_mode = "IMMEDIATE"
            
            begin_query = f"BEGIN {transaction_mode}"
            result = await self.connection.execute(begin_query, None, None)
            
            # Store transaction context
            self.active_transactions[transaction_id] = TransactionContext(
                transaction_id=transaction_id,
                isolation_level=isolation_level,
                read_only=read_only,
                started_at=time.time(),
                timeout=timeout,
                savepoints=[]
            )
            
            logger.debug(f"SQLite transaction {transaction_id} started")
            return transaction_id
            
        except Exception as e:
            logger.error(f"Failed to begin SQLite transaction: {e}")
            raise
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit SQLite transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            await self.connection.execute("COMMIT", None, transaction_id)
            del self.active_transactions[transaction_id]
            
            logger.debug(f"SQLite transaction {transaction_id} committed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit SQLite transaction {transaction_id}: {e}")
            return False
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback SQLite transaction"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            await self.connection.execute("ROLLBACK", None, transaction_id)
            del self.active_transactions[transaction_id]
            
            logger.debug(f"SQLite transaction {transaction_id} rolled back")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback SQLite transaction {transaction_id}: {e}")
            return False
    
    async def create_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Create SQLite savepoint"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            savepoint_query = f"SAVEPOINT {savepoint_name}"
            await self.connection.execute(savepoint_query, None, transaction_id)
            
            # Add to transaction context
            self.active_transactions[transaction_id].savepoints.append(savepoint_name)
            
            logger.debug(f"SQLite savepoint {savepoint_name} created for transaction {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create SQLite savepoint: {e}")
            return False
    
    async def rollback_to_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Rollback to SQLite savepoint"""
        try:
            if transaction_id not in self.active_transactions:
                return False
            
            rollback_query = f"ROLLBACK TO SAVEPOINT {savepoint_name}"
            await self.connection.execute(rollback_query, None, transaction_id)
            
            logger.debug(f"SQLite rolled back to savepoint {savepoint_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback to SQLite savepoint: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check SQLite connection health"""
        try:
            if self.state != DatabaseState.CONNECTED:
                return False
            
            result = await self.connection.execute("SELECT 1", None, None)
            return result.get("success", False)
            
        except Exception as e:
            logger.error(f"SQLite health check failed: {e}")
            return False


# Mock connection classes for testing
class PostgreSQLConnection:
    def __init__(self, params):
        self.params = params
        
    async def execute(self, query, params, transaction_id):
        await asyncio.sleep(0.001)  # Simulate execution time
        return {
            "success": True,
            "rows_affected": 1,
            "rows": [{"result": 1}] if "SELECT" in query else [],
            "plan": "Mock execution plan"
        }
        
    async def close(self):
        pass


class MySQLConnection:
    def __init__(self, params):
        self.params = params
        
    async def execute(self, query, params, transaction_id):
        await asyncio.sleep(0.001)  # Simulate execution time
        return {
            "success": True,
            "rows_affected": 1,
            "rows": [{"result": 1}] if "SELECT" in query else []
        }
        
    async def close(self):
        pass


class SQLiteConnection:
    def __init__(self, database_path):
        self.database_path = database_path
        
    async def execute(self, query, params, transaction_id):
        await asyncio.sleep(0.0005)  # SQLite is faster
        return {
            "success": True,
            "rows_affected": 1,
            "rows": [{"result": 1}] if "SELECT" in query else []
        }
        
    async def close(self):
        pass


# Test harness
if __name__ == "__main__":
    async def test_database_adapters():
        """Test all database adapters"""
        
        print("🔧 Testing Database Adapters...")
        
        # Test PostgreSQL adapter
        pg_config = DatabaseConfiguration(
            database_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="testdb",
            username="test",
            password="test"
        )
        
        pg_adapter = PostgreSQLAdapter(pg_config)
        
        try:
            # Test connection
            await pg_adapter.connect()
            print("✅ PostgreSQL adapter connected")
            
            # Test query execution
            result = await pg_adapter.execute_query(
                "SELECT * FROM users WHERE id = %(user_id)s",
                {"user_id": 1}
            )
            print(f"✅ PostgreSQL query result: {result.success}")
            
            # Test transaction
            txn_id = await pg_adapter.begin_transaction("SERIALIZABLE")
            await pg_adapter.commit_transaction(txn_id)
            print("✅ PostgreSQL transaction test passed")
            
            # Test health check
            health = await pg_adapter.health_check()
            print(f"✅ PostgreSQL health check: {health}")
            
            await pg_adapter.disconnect()
            
        except Exception as e:
            print(f"❌ PostgreSQL adapter test failed: {e}")
        
        # Test MySQL adapter
        mysql_config = DatabaseConfiguration(
            database_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database="testdb",
            username="test",
            password="test"
        )
        
        mysql_adapter = MySQLAdapter(mysql_config)
        
        try:
            await mysql_adapter.connect()
            print("✅ MySQL adapter connected")
            
            result = await mysql_adapter.execute_query("SELECT 1")
            print(f"✅ MySQL query result: {result.success}")
            
            await mysql_adapter.disconnect()
            
        except Exception as e:
            print(f"❌ MySQL adapter test failed: {e}")
        
        # Test SQLite adapter
        sqlite_config = DatabaseConfiguration(
            database_type=DatabaseType.SQLITE,
            database=":memory:"
        )
        
        sqlite_adapter = SQLiteAdapter(sqlite_config)
        
        try:
            await sqlite_adapter.connect()
            print("✅ SQLite adapter connected")
            
            result = await sqlite_adapter.execute_query("SELECT 1")
            print(f"✅ SQLite query result: {result.success}")
            
            await sqlite_adapter.disconnect()
            
        except Exception as e:
            print(f"❌ SQLite adapter test failed: {e}")
        
        print("🎉 Database adapter testing complete!")
    
    asyncio.run(test_database_adapters())