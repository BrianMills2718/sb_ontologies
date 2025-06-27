"""
V5.0 Database Factory Pattern
Provides unified factory for creating database adapters with configuration management
"""

import asyncio
import time
import logging
import yaml
import json
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from database_adapters import (
    DatabaseAdapter, DatabaseConfiguration, DatabaseType,
    PostgreSQLAdapter, MySQLAdapter, SQLiteAdapter
)

logger = logging.getLogger(__name__)


class DatabaseFactoryError(Exception):
    """Raised when database factory operations fail"""
    pass


class ConfigurationError(DatabaseFactoryError):
    """Raised when database configuration is invalid"""
    pass


class ConnectionPoolingStrategy(Enum):
    """Connection pooling strategies"""
    NONE = "none"
    SIMPLE = "simple"
    ADVANCED = "advanced"
    CLUSTERED = "clustered"


@dataclass
class DatabaseClusterConfiguration:
    """Configuration for database clustering"""
    cluster_name: str
    primary_config: DatabaseConfiguration
    replica_configs: List[DatabaseConfiguration]
    load_balancing_strategy: str = "round_robin"  # round_robin, least_connections, weighted
    failover_enabled: bool = True
    health_check_interval: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class FactoryConfiguration:
    """Database factory configuration"""
    default_database_type: DatabaseType = DatabaseType.POSTGRESQL
    connection_pooling: ConnectionPoolingStrategy = ConnectionPoolingStrategy.ADVANCED
    auto_reconnect: bool = True
    health_monitoring: bool = True
    performance_monitoring: bool = True
    query_logging: bool = False
    slow_query_threshold: float = 1.0
    configuration_cache_ttl: float = 300.0
    
    
class DatabaseRegistry:
    """Registry for managing database configurations and connections"""
    
    def __init__(self):
        self.configurations: Dict[str, DatabaseConfiguration] = {}
        self.cluster_configurations: Dict[str, DatabaseClusterConfiguration] = {}
        self.active_adapters: Dict[str, DatabaseAdapter] = {}
        self.adapter_statistics: Dict[str, Dict[str, Any]] = {}
        self.last_health_check: Dict[str, float] = {}
        
    def register_database(self, name: str, config: DatabaseConfiguration):
        """Register database configuration"""
        self.configurations[name] = config
        logger.info(f"Registered database configuration: {name}")
        
    def register_cluster(self, name: str, cluster_config: DatabaseClusterConfiguration):
        """Register database cluster configuration"""
        self.cluster_configurations[name] = cluster_config
        logger.info(f"Registered database cluster: {name}")
        
    def get_configuration(self, name: str) -> Optional[DatabaseConfiguration]:
        """Get database configuration by name"""
        return self.configurations.get(name)
        
    def get_cluster_configuration(self, name: str) -> Optional[DatabaseClusterConfiguration]:
        """Get cluster configuration by name"""
        return self.cluster_configurations.get(name)
        
    def list_databases(self) -> List[str]:
        """List all registered database names"""
        return list(self.configurations.keys())
        
    def list_clusters(self) -> List[str]:
        """List all registered cluster names"""
        return list(self.cluster_configurations.keys())


class DatabaseFactory:
    """Factory for creating and managing database adapters"""
    
    def __init__(self, config: FactoryConfiguration = None):
        self.config = config or FactoryConfiguration()
        self.registry = DatabaseRegistry()
        
        # Adapter type mapping
        self.adapter_classes: Dict[DatabaseType, Type[DatabaseAdapter]] = {
            DatabaseType.POSTGRESQL: PostgreSQLAdapter,
            DatabaseType.MYSQL: MySQLAdapter,
            DatabaseType.SQLITE: SQLiteAdapter
        }
        
        # Connection pools
        self.connection_pools: Dict[str, Any] = {}
        
        # Monitoring
        self.factory_statistics = {
            "adapters_created": 0,
            "connections_established": 0,
            "connection_failures": 0,
            "queries_executed": 0,
            "average_query_time": 0.0
        }
        
        logger.info("Database Factory initialized")
    
    async def create_adapter(
        self, 
        database_name: str = None,
        config: DatabaseConfiguration = None,
        adapter_id: str = None
    ) -> DatabaseAdapter:
        """Create database adapter from configuration"""
        
        if config is None:
            if database_name is None:
                raise DatabaseFactoryError("Either database_name or config must be provided")
                
            config = self.registry.get_configuration(database_name)
            if config is None:
                raise DatabaseFactoryError(f"No configuration found for database: {database_name}")
        
        adapter_id = adapter_id or f"{config.database_type.value}_{int(time.time())}"
        
        try:
            # Get adapter class
            adapter_class = self.adapter_classes.get(config.database_type)
            if adapter_class is None:
                raise DatabaseFactoryError(f"Unsupported database type: {config.database_type}")
            
            # Create adapter instance
            adapter = adapter_class(config)
            
            # Connect to database
            connection_success = await adapter.connect()
            if not connection_success:
                raise DatabaseFactoryError(f"Failed to connect to database: {adapter_id}")
            
            # Register adapter
            self.registry.active_adapters[adapter_id] = adapter
            
            # Update statistics
            self.factory_statistics["adapters_created"] += 1
            self.factory_statistics["connections_established"] += 1
            
            logger.info(f"Created database adapter: {adapter_id} ({config.database_type.value})")
            return adapter
            
        except Exception as e:
            self.factory_statistics["connection_failures"] += 1
            logger.error(f"Failed to create database adapter: {e}")
            raise DatabaseFactoryError(f"Adapter creation failed: {e}")
    
    async def create_cluster_adapter(self, cluster_name: str) -> 'ClusterDatabaseAdapter':
        """Create clustered database adapter"""
        
        cluster_config = self.registry.get_cluster_configuration(cluster_name)
        if cluster_config is None:
            raise DatabaseFactoryError(f"No cluster configuration found: {cluster_name}")
        
        try:
            # Create primary adapter
            primary_adapter = await self.create_adapter(
                config=cluster_config.primary_config,
                adapter_id=f"{cluster_name}_primary"
            )
            
            # Create replica adapters
            replica_adapters = []
            for i, replica_config in enumerate(cluster_config.replica_configs):
                replica_adapter = await self.create_adapter(
                    config=replica_config,
                    adapter_id=f"{cluster_name}_replica_{i}"
                )
                replica_adapters.append(replica_adapter)
            
            # Create cluster adapter
            cluster_adapter = ClusterDatabaseAdapter(
                cluster_config=cluster_config,
                primary_adapter=primary_adapter,
                replica_adapters=replica_adapters
            )
            
            await cluster_adapter.initialize()
            
            logger.info(f"Created cluster adapter: {cluster_name}")
            return cluster_adapter
            
        except Exception as e:
            logger.error(f"Failed to create cluster adapter: {e}")
            raise DatabaseFactoryError(f"Cluster adapter creation failed: {e}")
    
    async def get_adapter(self, adapter_id: str) -> Optional[DatabaseAdapter]:
        """Get existing adapter by ID"""
        return self.registry.active_adapters.get(adapter_id)
    
    async def remove_adapter(self, adapter_id: str) -> bool:
        """Remove and disconnect adapter"""
        try:
            adapter = self.registry.active_adapters.get(adapter_id)
            if adapter:
                await adapter.disconnect()
                del self.registry.active_adapters[adapter_id]
                logger.info(f"Removed adapter: {adapter_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove adapter {adapter_id}: {e}")
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all active adapters"""
        health_results = {}
        
        for adapter_id, adapter in self.registry.active_adapters.items():
            try:
                health_status = await adapter.health_check()
                health_results[adapter_id] = health_status
                self.registry.last_health_check[adapter_id] = time.time()
                
            except Exception as e:
                logger.error(f"Health check failed for adapter {adapter_id}: {e}")
                health_results[adapter_id] = False
        
        return health_results
    
    def load_configuration_from_file(self, config_file: str):
        """Load database configurations from file"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_file}")
        
        try:
            if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
            else:
                raise ConfigurationError(f"Unsupported configuration file format: {config_path.suffix}")
            
            # Parse database configurations
            if 'databases' in config_data:
                for db_name, db_config in config_data['databases'].items():
                    self._parse_database_config(db_name, db_config)
            
            # Parse cluster configurations
            if 'clusters' in config_data:
                for cluster_name, cluster_config in config_data['clusters'].items():
                    self._parse_cluster_config(cluster_name, cluster_config)
            
            logger.info(f"Loaded configuration from: {config_file}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _parse_database_config(self, name: str, config_dict: Dict[str, Any]):
        """Parse database configuration from dictionary"""
        try:
            # Convert database type string to enum
            db_type = DatabaseType(config_dict.get('type', 'postgresql'))
            
            config = DatabaseConfiguration(
                database_type=db_type,
                host=config_dict.get('host'),
                port=config_dict.get('port'),
                database=config_dict.get('database'),
                username=config_dict.get('username'),
                password=config_dict.get('password'),
                connection_params=config_dict.get('connection_params', {}),
                pool_size=config_dict.get('pool_size', 10),
                max_connections=config_dict.get('max_connections', 20),
                connection_timeout=config_dict.get('connection_timeout', 30.0),
                query_timeout=config_dict.get('query_timeout', 60.0),
                ssl_enabled=config_dict.get('ssl_enabled', False),
                ssl_params=config_dict.get('ssl_params', {})
            )
            
            self.registry.register_database(name, config)
            
        except Exception as e:
            raise ConfigurationError(f"Invalid database configuration for {name}: {e}")
    
    def _parse_cluster_config(self, name: str, config_dict: Dict[str, Any]):
        """Parse cluster configuration from dictionary"""
        try:
            # Parse primary configuration
            primary_config_dict = config_dict['primary']
            primary_config = self._create_config_from_dict(primary_config_dict)
            
            # Parse replica configurations
            replica_configs = []
            for replica_dict in config_dict.get('replicas', []):
                replica_config = self._create_config_from_dict(replica_dict)
                replica_configs.append(replica_config)
            
            cluster_config = DatabaseClusterConfiguration(
                cluster_name=name,
                primary_config=primary_config,
                replica_configs=replica_configs,
                load_balancing_strategy=config_dict.get('load_balancing', 'round_robin'),
                failover_enabled=config_dict.get('failover_enabled', True),
                health_check_interval=config_dict.get('health_check_interval', 30.0),
                max_retries=config_dict.get('max_retries', 3),
                retry_delay=config_dict.get('retry_delay', 1.0)
            )
            
            self.registry.register_cluster(name, cluster_config)
            
        except Exception as e:
            raise ConfigurationError(f"Invalid cluster configuration for {name}: {e}")
    
    def _create_config_from_dict(self, config_dict: Dict[str, Any]) -> DatabaseConfiguration:
        """Create DatabaseConfiguration from dictionary"""
        db_type = DatabaseType(config_dict.get('type', 'postgresql'))
        
        return DatabaseConfiguration(
            database_type=db_type,
            host=config_dict.get('host'),
            port=config_dict.get('port'),
            database=config_dict.get('database'),
            username=config_dict.get('username'),
            password=config_dict.get('password'),
            connection_params=config_dict.get('connection_params', {}),
            pool_size=config_dict.get('pool_size', 10),
            max_connections=config_dict.get('max_connections', 20),
            connection_timeout=config_dict.get('connection_timeout', 30.0),
            query_timeout=config_dict.get('query_timeout', 60.0),
            ssl_enabled=config_dict.get('ssl_enabled', False),
            ssl_params=config_dict.get('ssl_params', {})
        )
    
    def get_factory_statistics(self) -> Dict[str, Any]:
        """Get factory performance statistics"""
        active_adapters = len(self.registry.active_adapters)
        
        # Aggregate adapter statistics
        total_queries = 0
        total_execution_time = 0.0
        
        for adapter in self.registry.active_adapters.values():
            adapter_stats = adapter.get_adapter_statistics()
            total_queries += adapter_stats["query_statistics"]["total_queries"]
            total_execution_time += adapter_stats["query_statistics"]["total_execution_time"]
        
        average_query_time = total_execution_time / max(total_queries, 1)
        
        return {
            "adapters_created": self.factory_statistics["adapters_created"],
            "active_adapters": active_adapters,
            "connections_established": self.factory_statistics["connections_established"],
            "connection_failures": self.factory_statistics["connection_failures"],
            "total_queries_executed": total_queries,
            "average_query_time": average_query_time,
            "registered_databases": len(self.registry.configurations),
            "registered_clusters": len(self.registry.cluster_configurations)
        }
    
    async def shutdown(self):
        """Shutdown factory and all adapters"""
        logger.info("Shutting down database factory")
        
        # Disconnect all adapters
        for adapter_id in list(self.registry.active_adapters.keys()):
            await self.remove_adapter(adapter_id)
        
        # Clear registries
        self.registry.configurations.clear()
        self.registry.cluster_configurations.clear()
        self.connection_pools.clear()
        
        logger.info("Database factory shutdown complete")


class ClusterDatabaseAdapter(DatabaseAdapter):
    """Database adapter for clustered database configurations"""
    
    def __init__(
        self, 
        cluster_config: DatabaseClusterConfiguration,
        primary_adapter: DatabaseAdapter,
        replica_adapters: List[DatabaseAdapter]
    ):
        # Use primary config for base initialization
        super().__init__(cluster_config.primary_config)
        
        self.cluster_config = cluster_config
        self.primary_adapter = primary_adapter
        self.replica_adapters = replica_adapters
        self.current_replica_index = 0
        self.failed_adapters: set = set()
        
        logger.info(f"Cluster adapter created: {cluster_config.cluster_name}")
    
    async def initialize(self):
        """Initialize cluster adapter"""
        # Start health monitoring
        if self.cluster_config.health_check_interval > 0:
            asyncio.create_task(self._health_monitoring_loop())
    
    async def connect(self) -> bool:
        """Connect - already handled by individual adapters"""
        return self.primary_adapter.state.value == "connected"
    
    async def disconnect(self) -> bool:
        """Disconnect all adapters in cluster"""
        success = True
        
        # Disconnect primary
        if not await self.primary_adapter.disconnect():
            success = False
        
        # Disconnect replicas
        for replica in self.replica_adapters:
            if not await replica.disconnect():
                success = False
        
        return success
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        transaction_id: Optional[str] = None
    ):
        """Execute query with load balancing for reads"""
        
        # Determine if query is read-only
        is_read_query = self._is_read_query(query)
        
        if is_read_query and self.replica_adapters:
            # Use replica for read queries
            adapter = self._get_next_replica()
            if adapter:
                try:
                    return await adapter.execute_query(query, parameters, transaction_id)
                except Exception as e:
                    logger.warning(f"Replica query failed, falling back to primary: {e}")
        
        # Use primary for write queries or when replicas fail
        return await self.primary_adapter.execute_query(query, parameters, transaction_id)
    
    async def execute_many(
        self, 
        query: str, 
        parameter_list: List[Dict[str, Any]],
        transaction_id: Optional[str] = None
    ):
        """Execute batch query on primary"""
        return await self.primary_adapter.execute_many(query, parameter_list, transaction_id)
    
    async def begin_transaction(
        self, 
        isolation_level: str = "READ_COMMITTED",
        read_only: bool = False,
        timeout: float = 300.0
    ) -> str:
        """Begin transaction on primary"""
        return await self.primary_adapter.begin_transaction(isolation_level, read_only, timeout)
    
    async def commit_transaction(self, transaction_id: str) -> bool:
        """Commit transaction on primary"""
        return await self.primary_adapter.commit_transaction(transaction_id)
    
    async def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback transaction on primary"""
        return await self.primary_adapter.rollback_transaction(transaction_id)
    
    async def create_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Create savepoint on primary"""
        return await self.primary_adapter.create_savepoint(transaction_id, savepoint_name)
    
    async def rollback_to_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """Rollback to savepoint on primary"""
        return await self.primary_adapter.rollback_to_savepoint(transaction_id, savepoint_name)
    
    async def health_check(self) -> bool:
        """Check health of primary adapter"""
        return await self.primary_adapter.health_check()
    
    def _is_read_query(self, query: str) -> bool:
        """Determine if query is read-only"""
        query_upper = query.strip().upper()
        read_keywords = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN']
        return any(query_upper.startswith(keyword) for keyword in read_keywords)
    
    def _get_next_replica(self) -> Optional[DatabaseAdapter]:
        """Get next replica using load balancing strategy"""
        if not self.replica_adapters:
            return None
        
        # Filter out failed adapters
        available_replicas = [
            replica for replica in self.replica_adapters 
            if id(replica) not in self.failed_adapters
        ]
        
        if not available_replicas:
            return None
        
        if self.cluster_config.load_balancing_strategy == "round_robin":
            replica = available_replicas[self.current_replica_index % len(available_replicas)]
            self.current_replica_index += 1
            return replica
        
        # Default to first available replica
        return available_replicas[0]
    
    async def _health_monitoring_loop(self):
        """Background health monitoring for cluster adapters"""
        while True:
            try:
                await asyncio.sleep(self.cluster_config.health_check_interval)
                
                # Check replica health
                for replica in self.replica_adapters:
                    try:
                        health = await replica.health_check()
                        replica_id = id(replica)
                        
                        if health:
                            # Remove from failed set if healthy
                            self.failed_adapters.discard(replica_id)
                        else:
                            # Add to failed set if unhealthy
                            self.failed_adapters.add(replica_id)
                            logger.warning(f"Replica adapter {replica_id} health check failed")
                            
                    except Exception as e:
                        logger.error(f"Health check error for replica: {e}")
                        self.failed_adapters.add(id(replica))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")


# Test harness
if __name__ == "__main__":
    async def test_database_factory():
        """Test database factory functionality"""
        
        print("🔧 Testing Database Factory...")
        
        # Create factory
        factory_config = FactoryConfiguration(
            default_database_type=DatabaseType.POSTGRESQL,
            auto_reconnect=True,
            health_monitoring=True
        )
        
        factory = DatabaseFactory(factory_config)
        
        try:
            # Test database registration
            pg_config = DatabaseConfiguration(
                database_type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=5432,
                database="testdb",
                username="test",
                password="test"
            )
            
            factory.registry.register_database("test_pg", pg_config)
            print("✅ Database configuration registered")
            
            # Test adapter creation
            adapter = await factory.create_adapter("test_pg")
            print(f"✅ Database adapter created: {adapter.connection_id}")
            
            # Test query execution
            result = await adapter.execute_query("SELECT 1")
            print(f"✅ Query executed: {result.success}")
            
            # Test health check
            health_results = await factory.health_check_all()
            print(f"✅ Health check results: {health_results}")
            
            # Test statistics
            stats = factory.get_factory_statistics()
            print(f"✅ Factory statistics: {stats}")
            
            # Test configuration from dictionary
            config_dict = {
                "databases": {
                    "mysql_test": {
                        "type": "mysql",
                        "host": "localhost",
                        "port": 3306,
                        "database": "testdb",
                        "username": "test",
                        "password": "test",
                        "pool_size": 5
                    }
                }
            }
            
            factory._parse_database_config("mysql_from_dict", config_dict["databases"]["mysql_test"])
            print("✅ Configuration parsing from dictionary")
            
            # Test cluster configuration
            cluster_config = DatabaseClusterConfiguration(
                cluster_name="test_cluster",
                primary_config=pg_config,
                replica_configs=[pg_config],  # Using same config for testing
                load_balancing_strategy="round_robin"
            )
            
            factory.registry.register_cluster("test_cluster", cluster_config)
            
            cluster_adapter = await factory.create_cluster_adapter("test_cluster")
            print("✅ Cluster adapter created")
            
            # Test cluster query
            cluster_result = await cluster_adapter.execute_query("SELECT 1")
            print(f"✅ Cluster query executed: {cluster_result.success}")
            
            # Test shutdown
            await factory.shutdown()
            print("✅ Factory shutdown successful")
            
        except Exception as e:
            print(f"❌ Database factory test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_database_factory())