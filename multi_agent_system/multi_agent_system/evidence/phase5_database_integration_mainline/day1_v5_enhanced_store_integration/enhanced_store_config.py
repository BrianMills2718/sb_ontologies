"""
Enhanced Store Configuration Management
Manages database configuration for V5EnhancedStore components with connection pooling,
schema validation, and performance optimization settings.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class IsolationLevel(Enum):
    """Transaction isolation levels"""
    READ_UNCOMMITTED = "READ_UNCOMMITTED"
    READ_COMMITTED = "READ_COMMITTED"
    REPEATABLE_READ = "REPEATABLE_READ"
    SERIALIZABLE = "SERIALIZABLE"


@dataclass
class ConnectionPoolConfig:
    """Connection pool configuration"""
    min_connections: int = 1
    max_connections: int = 10
    connection_timeout: int = 30
    idle_timeout: int = 300
    max_lifetime: int = 3600
    health_check_interval: int = 60


@dataclass
class SchemaValidationConfig:
    """Schema validation configuration"""
    enabled: bool = True
    auto_migrate: bool = True
    strict_validation: bool = True
    schema_version: str = "1.0.0"
    migration_timeout: int = 300
    backup_before_migration: bool = True


@dataclass
class TransactionConfig:
    """Transaction management configuration"""
    default_isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
    timeout: int = 30
    auto_rollback: bool = True
    retry_on_conflict: bool = True
    max_retries: int = 3


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    caching_enabled: bool = True
    cache_enabled: bool = True  # Alias for compatibility
    cache_size: int = 1000
    cache_ttl: int = 300
    query_optimization: bool = True
    connection_preallocation: bool = True
    batch_size: int = 100
    pool_size: int = 10  # Alias for compatibility


@dataclass
class V5EnhancedStoreConfig:
    """Complete V5 Enhanced Store configuration"""
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    connection_url: Optional[str] = None
    host: str = "localhost"
    port: int = 5432
    database: str = "autocoder_db"
    username: str = "autocoder"
    password: str = "password"
    table_name: str = "enhanced_store"
    
    # V5 Feature configurations
    connection_pool: ConnectionPoolConfig = field(default_factory=ConnectionPoolConfig)
    schema_validation: SchemaValidationConfig = field(default_factory=SchemaValidationConfig)
    transactions: TransactionConfig = field(default_factory=TransactionConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Additional settings
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    monitoring_enabled: bool = True
    debug_logging: bool = False


class EnhancedStoreConfigManager:
    """
    Configuration manager for V5EnhancedStore components.
    
    Handles configuration validation, environment variable integration,
    and configuration merging for enhanced store components.
    """
    
    def __init__(self):
        self.default_configs = {}
        self.environment_overrides = {}
        
        # Load environment variables
        self._load_environment_overrides()
        
        logger.info("EnhancedStoreConfigManager initialized")
    
    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        env_mappings = {
            'AUTOCODER_DB_TYPE': ('database_type', str),
            'AUTOCODER_DB_HOST': ('host', str),
            'AUTOCODER_DB_PORT': ('port', int),
            'AUTOCODER_DB_NAME': ('database', str),
            'AUTOCODER_DB_USER': ('username', str),
            'AUTOCODER_DB_PASSWORD': ('password', str),
            'AUTOCODER_DB_URL': ('connection_url', str),
            'AUTOCODER_DB_SSL': ('ssl_enabled', bool),
            'AUTOCODER_DB_POOL_SIZE': ('connection_pool.max_connections', int),
            'AUTOCODER_DB_POOL_TIMEOUT': ('connection_pool.connection_timeout', int),
            'AUTOCODER_SCHEMA_AUTO_MIGRATE': ('schema_validation.auto_migrate', bool),
            'AUTOCODER_CACHE_ENABLED': ('performance.caching_enabled', bool),
            'AUTOCODER_CACHE_SIZE': ('performance.cache_size', int),
            'AUTOCODER_DEBUG_LOGGING': ('debug_logging', bool)
        }
        
        for env_var, (config_path, config_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if config_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif config_type == int:
                        value = int(value)
                    
                    self._set_nested_config(self.environment_overrides, config_path, value)
                    logger.debug(f"Environment override: {config_path} = {value}")
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")
    
    def _set_nested_config(self, config_dict: Dict[str, Any], path: str, value: Any):
        """Set nested configuration value using dot notation"""
        keys = path.split('.')
        current_dict = config_dict
        
        for key in keys[:-1]:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]
        
        current_dict[keys[-1]] = value
    
    def create_config(self, component_name: str, base_config: Dict[str, Any]) -> V5EnhancedStoreConfig:
        """
        Create V5EnhancedStore configuration from base configuration.
        
        Args:
            component_name: Name of the store component
            base_config: Base configuration dictionary from blueprint
            
        Returns:
            V5EnhancedStoreConfig: Complete configuration for V5EnhancedStore
        """
        logger.debug(f"Creating V5EnhancedStore config for {component_name}")
        
        # Start with default configuration
        config_dict = self._get_default_config_dict()
        
        # Apply base configuration
        config_dict = self._merge_configs(config_dict, base_config)
        
        # Apply environment overrides
        config_dict = self._merge_configs(config_dict, self.environment_overrides)
        
        # Apply component-specific overrides if available
        component_overrides = self.default_configs.get(component_name, {})
        config_dict = self._merge_configs(config_dict, component_overrides)
        
        # Validate and normalize configuration
        config_dict = self._validate_and_normalize(config_dict)
        
        # Create V5EnhancedStoreConfig object
        try:
            config = self._dict_to_config(config_dict)
            logger.info(f"V5EnhancedStore config created for {component_name}: {config.database_type.value}://{config.host}:{config.port}/{config.database}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to create V5EnhancedStore config for {component_name}: {e}")
            raise ValueError(f"Invalid configuration for {component_name}: {e}")
    
    def _get_default_config_dict(self) -> Dict[str, Any]:
        """Get default configuration as dictionary"""
        return {
            "database_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "autocoder_db",
            "username": "autocoder",
            "password": "password",
            "table_name": "enhanced_store",
            "connection_pool": {
                "min_connections": 1,
                "max_connections": 10,
                "connection_timeout": 30,
                "idle_timeout": 300,
                "max_lifetime": 3600,
                "health_check_interval": 60
            },
            "schema_validation": {
                "enabled": True,
                "auto_migrate": True,
                "strict_validation": True,
                "schema_version": "1.0.0",
                "migration_timeout": 300,
                "backup_before_migration": True
            },
            "transactions": {
                "default_isolation_level": "READ_COMMITTED",
                "timeout": 30,
                "auto_rollback": True,
                "retry_on_conflict": True,
                "max_retries": 3
            },
            "performance": {
                "caching_enabled": True,
                "cache_size": 1000,
                "cache_ttl": 300,
                "query_optimization": True,
                "connection_preallocation": True,
                "batch_size": 100
            },
            "ssl_enabled": False,
            "monitoring_enabled": True,
            "debug_logging": False
        }
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_and_normalize(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize configuration values"""
        normalized = config_dict.copy()
        
        # Normalize database type
        if isinstance(normalized.get('database_type'), str):
            try:
                normalized['database_type'] = DatabaseType(normalized['database_type'].lower())
            except ValueError:
                logger.warning(f"Invalid database_type: {normalized['database_type']}, using postgresql")
                normalized['database_type'] = DatabaseType.POSTGRESQL
        
        # Ensure required fields are present
        required_fields = ['host', 'port', 'database', 'username', 'password']
        for field in required_fields:
            if field not in normalized:
                raise ValueError(f"Required field '{field}' missing from configuration")
        
        # Validate port
        if not isinstance(normalized['port'], int) or normalized['port'] <= 0:
            raise ValueError(f"Invalid port: {normalized['port']}")
        
        # Build connection URL if not provided
        if not normalized.get('connection_url'):
            db_type = normalized['database_type']
            if isinstance(db_type, DatabaseType):
                db_type = db_type.value
            
            normalized['connection_url'] = (
                f"{db_type}://{normalized['username']}:{normalized['password']}"
                f"@{normalized['host']}:{normalized['port']}/{normalized['database']}"
            )
        
        # Validate nested configurations
        self._validate_connection_pool_config(normalized.get('connection_pool', {}))
        self._validate_schema_validation_config(normalized.get('schema_validation', {}))
        self._validate_transaction_config(normalized.get('transactions', {}))
        self._validate_performance_config(normalized.get('performance', {}))
        
        return normalized
    
    def _validate_connection_pool_config(self, pool_config: Dict[str, Any]):
        """Validate connection pool configuration"""
        if pool_config.get('max_connections', 0) <= 0:
            raise ValueError("max_connections must be positive")
        
        if pool_config.get('min_connections', 0) < 0:
            raise ValueError("min_connections must be non-negative")
        
        if pool_config.get('min_connections', 0) > pool_config.get('max_connections', 10):
            raise ValueError("min_connections cannot exceed max_connections")
    
    def _validate_schema_validation_config(self, schema_config: Dict[str, Any]):
        """Validate schema validation configuration"""
        if schema_config.get('migration_timeout', 0) <= 0:
            raise ValueError("migration_timeout must be positive")
    
    def _validate_transaction_config(self, tx_config: Dict[str, Any]):
        """Validate transaction configuration"""
        if tx_config.get('timeout', 0) <= 0:
            raise ValueError("transaction timeout must be positive")
        
        if tx_config.get('max_retries', 0) < 0:
            raise ValueError("max_retries must be non-negative")
        
        # Normalize isolation level
        isolation = tx_config.get('default_isolation_level')
        if isinstance(isolation, str):
            try:
                tx_config['default_isolation_level'] = IsolationLevel(isolation.upper())
            except ValueError:
                logger.warning(f"Invalid isolation level: {isolation}, using READ_COMMITTED")
                tx_config['default_isolation_level'] = IsolationLevel.READ_COMMITTED
    
    def _validate_performance_config(self, perf_config: Dict[str, Any]):
        """Validate performance configuration"""
        if perf_config.get('cache_size', 0) <= 0:
            raise ValueError("cache_size must be positive")
        
        if perf_config.get('cache_ttl', 0) <= 0:
            raise ValueError("cache_ttl must be positive")
        
        if perf_config.get('batch_size', 0) <= 0:
            raise ValueError("batch_size must be positive")
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> V5EnhancedStoreConfig:
        """Convert configuration dictionary to V5EnhancedStoreConfig object"""
        
        # Create nested configuration objects
        connection_pool = ConnectionPoolConfig(**config_dict.get('connection_pool', {}))
        schema_validation = SchemaValidationConfig(**config_dict.get('schema_validation', {}))
        
        # Handle transaction config with enum conversion
        tx_config = config_dict.get('transactions', {})
        if isinstance(tx_config.get('default_isolation_level'), str):
            tx_config['default_isolation_level'] = IsolationLevel(tx_config['default_isolation_level'].upper())
        transactions = TransactionConfig(**tx_config)
        
        performance = PerformanceConfig(**config_dict.get('performance', {}))
        
        # Create main config object, filtering out invalid keys
        valid_config_keys = {
            'database_type', 'connection_url', 'host', 'port', 'database', 
            'username', 'password', 'table_name', 'ssl_enabled', 'ssl_cert_path',
            'monitoring_enabled', 'debug_logging'
        }
        
        main_config = {
            key: value for key, value in config_dict.items()
            if key not in ['connection_pool', 'schema_validation', 'transactions', 'performance']
            and key in valid_config_keys
        }
        
        return V5EnhancedStoreConfig(
            connection_pool=connection_pool,
            schema_validation=schema_validation,
            transactions=transactions,
            performance=performance,
            **main_config
        )
    
    def register_component_config(self, component_name: str, config_overrides: Dict[str, Any]):
        """Register component-specific configuration overrides"""
        self.default_configs[component_name] = config_overrides
        logger.info(f"Registered config overrides for component: {component_name}")
    
    def get_config_template(self) -> Dict[str, Any]:
        """Get configuration template for documentation/examples"""
        return {
            "database": {
                "database_type": "postgresql",  # postgresql, mysql, sqlite
                "host": "localhost",
                "port": 5432,
                "database": "autocoder_db",
                "username": "autocoder",
                "password": "password",
                "connection_url": "postgresql://autocoder:password@localhost:5432/autocoder_db",
                "table_name": "enhanced_store",
                "ssl_enabled": False
            },
            "connection_pool": {
                "min_connections": 1,
                "max_connections": 10,
                "connection_timeout": 30,
                "idle_timeout": 300,
                "max_lifetime": 3600,
                "health_check_interval": 60
            },
            "schema_validation": {
                "enabled": True,
                "auto_migrate": True,
                "strict_validation": True,
                "schema_version": "1.0.0",
                "migration_timeout": 300,
                "backup_before_migration": True
            },
            "transactions": {
                "default_isolation_level": "READ_COMMITTED",
                "timeout": 30,
                "auto_rollback": True,
                "retry_on_conflict": True,
                "max_retries": 3
            },
            "performance": {
                "caching_enabled": True,
                "cache_size": 1000,
                "cache_ttl": 300,
                "query_optimization": True,
                "connection_preallocation": True,
                "batch_size": 100
            },
            "monitoring_enabled": True,
            "debug_logging": False
        }


# Global configuration manager instance
_config_manager = None

def get_config_manager() -> EnhancedStoreConfigManager:
    """Get the global enhanced store configuration manager"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = EnhancedStoreConfigManager()
    
    return _config_manager


def create_v5_store_config(component_name: str, base_config: Dict[str, Any]) -> V5EnhancedStoreConfig:
    """Create V5EnhancedStore configuration from base configuration"""
    manager = get_config_manager()
    return manager.create_config(component_name, base_config)


# Test harness
if __name__ == "__main__":
    def test_enhanced_store_config():
        """Test Enhanced Store Configuration Management"""
        
        print("Testing Enhanced Store Configuration Management...")
        
        # Create configuration manager
        manager = EnhancedStoreConfigManager()
        
        # Test basic configuration creation
        base_config = {
            "database_type": "postgresql",
            "host": "db.example.com",
            "port": 5432,
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass",
            "table_name": "test_store"
        }
        
        try:
            config = manager.create_config("test_store", base_config)
            
            print("✅ Configuration created successfully")
            print(f"   Database Type: {config.database_type.value}")
            print(f"   Connection: {config.host}:{config.port}/{config.database}")
            print(f"   Pool Size: {config.connection_pool.max_connections}")
            print(f"   Schema Validation: {config.schema_validation.enabled}")
            print(f"   Caching: {config.performance.caching_enabled}")
            
            # Test configuration template
            template = manager.get_config_template()
            print(f"✅ Configuration template generated: {len(template)} sections")
            
            # Test environment override simulation
            manager.environment_overrides = {
                "database_type": "mysql",
                "connection_pool": {"max_connections": 20}
            }
            
            override_config = manager.create_config("override_test", base_config)
            print(f"✅ Environment override test: DB type = {override_config.database_type.value}")
            
            # Test global config manager
            global_manager = get_config_manager()
            print(f"✅ Global config manager: {type(global_manager).__name__}")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🎉 Enhanced Store Configuration test completed!")
    
    test_enhanced_store_config()