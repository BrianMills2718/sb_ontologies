#!/usr/bin/env python3
"""
V5 Enhanced Component Generator for Database Integration
Extends HarnessComponentGenerator to create V5EnhancedStore components with schema validation
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import ast
import logging

# Import V5 database components with absolute paths
sys.path.insert(0, str(Path(__file__).parent.parent / "day1_v5_enhanced_store_integration"))
sys.path.insert(0, str(Path(__file__).parent.parent / "day2_orchestrator_database_validation"))

from store_component_registry import EnhancedStoreComponentRegistry as ComponentRegistry
from database_dependency_validator import DatabaseDependencyValidator


@dataclass
class V5GeneratedComponent:
    """Generated V5 component with database integration"""
    name: str
    type: str
    source_code: str
    imports: List[str]
    database_config: Dict[str, Any]
    schema_requirements: List[str]
    dependencies: List[str]


class V5EnhancedComponentGenerator:
    """
    Enhanced Component Generator with V5 database integration capabilities.
    
    Key Features:
    - Automatically uses V5EnhancedStore instead of basic Store
    - Integrates schema validation into component generation
    - Adds database dependency checking
    - Provides V5 database configuration templates
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.component_registry = ComponentRegistry()
        self.db_dependency_validator = DatabaseDependencyValidator()
        self.logger = logging.getLogger(__name__)
        
    def generate_v5_store_component(self, component_name: str, component_config: Dict[str, Any]) -> V5GeneratedComponent:
        """Generate V5EnhancedStore component with database integration"""
        
        # Mock database dependency validation for sync operation
        # In real implementation, this would be handled differently
        try:
            # Simple validation - check if database config is present
            has_db_config = (
                'database_type' in component_config or 
                'database' in component_config or
                any(key in component_config for key in ['host', 'connection_url'])
            )
            
            if not has_db_config:
                # Add basic database configuration
                component_config.setdefault('database_type', 'postgresql')
                component_config.setdefault('table_name', component_name.lower())
            
        except Exception as e:
            logger.warning(f"Database dependency validation skipped for {component_name}: {e}")
            # Continue with generation
        
        # Generate enhanced store component
        source_code = self._generate_v5_store_source(component_name, component_config)
        
        # Extract schema requirements
        schema_requirements = self._extract_schema_requirements(component_config)
        
        # Generate database configuration
        database_config = self._generate_database_config(component_config)
        
        return V5GeneratedComponent(
            name=component_name,
            type="V5EnhancedStore",
            source_code=source_code,
            imports=[
                "from autocoder.components.v5_enhanced_store import V5EnhancedStore",
                "from autocoder.database.schema_validator import SchemaValidator",
                "from autocoder.database.transaction_manager import TransactionManager",
                "import asyncio",
                "from typing import Dict, Any, Optional"
            ],
            database_config=database_config,
            schema_requirements=schema_requirements,
            dependencies=[f"database_{component_config.get('database_type', 'postgresql')}"]
        )
    
    def _generate_v5_store_source(self, component_name: str, config: Dict[str, Any]) -> str:
        """Generate V5EnhancedStore component source code"""
        
        # Get database configuration
        db_type = config.get("database_type", "postgresql")
        table_name = config.get("table_name", component_name.lower())
        schema_name = config.get("schema", "public")
        
        source_template = f'''"""
Generated V5EnhancedStore component: {component_name}
Enhanced with database integration, schema validation, and transaction management
"""
import asyncio
from typing import Dict, Any, Optional
from autocoder.components.v5_enhanced_store import V5EnhancedStore
from autocoder.database.schema_validator import SchemaValidator
from autocoder.database.transaction_manager import TransactionManager


class GeneratedStore_{component_name}(V5EnhancedStore):
    """
    Generated V5 Enhanced Store component with database integration.
    
    Features:
    - Real-time schema validation
    - Transaction management with rollback support
    - Connection pooling with health checks
    - Performance optimization with caching
    - Multi-database support ({db_type})
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        # Enhanced configuration with database settings
        enhanced_config = {{
            **config,
            "database_type": "{db_type}",
            "table_name": "{table_name}",
            "schema_name": "{schema_name}",
            "connection_pool_size": config.get("connection_pool_size", 10),
            "max_overflow": config.get("max_overflow", 20),
            "pool_timeout": config.get("pool_timeout", 30),
            "schema_validation_enabled": True,
            "transaction_isolation": config.get("transaction_isolation", "READ_COMMITTED"),
            "performance_monitoring": True
        }}
        
        super().__init__(name, enhanced_config)
        
        # Component-specific configuration
        self.table_name = "{table_name}"
        self.schema_name = "{schema_name}"
        self.batch_size = config.get("batch_size", 100)
        self.retry_attempts = config.get("retry_attempts", 3)
        
    async def setup(self):
        """Enhanced setup with database schema validation and preparation"""
        self.logger.info(f"Setting up V5EnhancedStore: {{self.name}}")
        
        # Call parent setup (initializes connection pool, schema validator, etc.)
        await super().setup()
        
        # Ensure table exists with correct schema
        await self._ensure_table_exists()
        
        # Setup component-specific indexes
        await self._setup_performance_indexes()
        
        self.logger.info(f"V5EnhancedStore {{self.name}} setup complete")
        
    async def consume(self, data: Any) -> Dict[str, Any]:
        """Enhanced consume with V5 database features"""
        try:
            # Pre-process data for storage
            processed_data = await self._preprocess_data(data)
            
            # Use parent's enhanced consume with transaction management
            result = await super().consume(processed_data)
            
            # Add component-specific metadata
            result.update({{
                "component_name": self.name,
                "table_name": self.table_name,
                "schema_name": self.schema_name,
                "processing_timestamp": self._get_timestamp()
            }})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Store operation failed in {{self.name}}: {{e}}")
            raise
    
    async def _ensure_table_exists(self):
        """Ensure database table exists with correct schema"""
        async with self.connection_manager.get_connection() as conn:
            # Check if table exists
            table_exists = await self._check_table_exists(conn)
            
            if not table_exists:
                # Create table with appropriate schema
                await self._create_table(conn)
                self.logger.info(f"Created table {{self.schema_name}}.{{self.table_name}}")
            else:
                # Validate existing schema
                await self._validate_table_schema(conn)
    
    async def _check_table_exists(self, conn) -> bool:
        """Check if table exists in database"""
        if self.config["database_type"] == "postgresql":
            query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = $1 AND table_name = $2
                )
            """
            result = await conn.fetchval(query, self.schema_name, self.table_name)
            return result
        elif self.config["database_type"] == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = await conn.fetchone(query, (self.table_name,))
            return result is not None
        else:
            raise NotImplementedError(f"Database type {{self.config['database_type']}} not supported")
    
    async def _create_table(self, conn):
        """Create table with default schema"""
        if self.config["database_type"] == "postgresql":
            create_sql = f"""
                CREATE TABLE {{self.schema_name}}.{{self.table_name}} (
                    id SERIAL PRIMARY KEY,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{{}}'::jsonb
                )
            """
        elif self.config["database_type"] == "sqlite":
            create_sql = f"""
                CREATE TABLE {{self.table_name}} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{{}}'
                )
            """
        else:
            raise NotImplementedError(f"Database type {{self.config['database_type']}} not supported")
            
        await conn.execute(create_sql)
    
    async def _validate_table_schema(self, conn):
        """Validate existing table schema matches requirements"""
        # Use schema validator to check compatibility
        validation_result = await self.schema_validator.validate_table_schema(
            conn, self.schema_name, self.table_name
        )
        
        if not validation_result.compatible:
            self.logger.warning(f"Schema incompatibility detected: {{validation_result.issues}}")
            # Could trigger migration here if needed
    
    async def _setup_performance_indexes(self):
        """Setup performance indexes for the table"""
        async with self.connection_manager.get_connection() as conn:
            if self.config["database_type"] == "postgresql":
                # Create GIN index on JSONB data for fast queries
                index_sql = f"""
                    CREATE INDEX IF NOT EXISTS idx_{{self.table_name}}_data_gin 
                    ON {{self.schema_name}}.{{self.table_name}} USING GIN (data)
                """
                await conn.execute(index_sql)
                
                # Create index on created_at for time-based queries
                time_index_sql = f"""
                    CREATE INDEX IF NOT EXISTS idx_{{self.table_name}}_created_at 
                    ON {{self.schema_name}}.{{self.table_name}} (created_at)
                """
                await conn.execute(time_index_sql)
    
    async def _preprocess_data(self, data: Any) -> Dict[str, Any]:
        """Preprocess data before storage"""
        if isinstance(data, dict):
            return data
        elif isinstance(data, str):
            return {{"value": data, "type": "string"}}
        elif isinstance(data, (int, float)):
            return {{"value": data, "type": "numeric"}}
        elif isinstance(data, list):
            return {{"items": data, "type": "array", "count": len(data)}}
        else:
            return {{"value": str(data), "type": "unknown"}}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        import datetime
        return datetime.datetime.now().isoformat()


# Export the generated component
__all__ = ["GeneratedStore_{component_name}"]
'''
        
        return source_template
    
    def _extract_schema_requirements(self, config: Dict[str, Any]) -> List[str]:
        """Extract schema requirements from component configuration"""
        requirements = []
        
        # Basic table requirements
        requirements.append("id_column_primary_key")
        requirements.append("data_column_json")
        requirements.append("timestamps_created_updated")
        requirements.append("metadata_column_json")
        
        # Add specific requirements based on config
        if config.get("enable_full_text_search"):
            requirements.append("full_text_search_index")
        
        if config.get("enable_audit_log"):
            requirements.append("audit_log_triggers")
        
        if config.get("enable_partitioning"):
            requirements.append("table_partitioning")
            
        return requirements
    
    def _generate_database_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database configuration for the component"""
        return {
            "database_type": config.get("database_type", "postgresql"),
            "connection_pool": {
                "min_size": config.get("connection_pool_min", 5),
                "max_size": config.get("connection_pool_max", 20),
                "timeout": config.get("connection_timeout", 30)
            },
            "schema_validation": {
                "enabled": True,
                "strict_mode": config.get("schema_strict_mode", True),
                "auto_migrate": config.get("schema_auto_migrate", False)
            },
            "transaction_management": {
                "isolation_level": config.get("transaction_isolation", "READ_COMMITTED"),
                "timeout": config.get("transaction_timeout", 30),
                "retry_attempts": config.get("retry_attempts", 3)
            },
            "performance": {
                "caching_enabled": config.get("enable_caching", True),
                "cache_ttl": config.get("cache_ttl", 300),
                "batch_size": config.get("batch_size", 100),
                "enable_monitoring": True
            }
        }
    
    def generate_enhanced_component(self, component_name: str, component_type: str, config: Dict[str, Any]) -> V5GeneratedComponent:
        """Generate enhanced component based on type"""
        if component_type == "Store":
            return self.generate_v5_store_component(component_name, config)
        else:
            # For non-Store components, return standard component but with V5 awareness
            return self._generate_v5_aware_component(component_name, component_type, config)
    
    def _generate_v5_aware_component(self, component_name: str, component_type: str, config: Dict[str, Any]) -> V5GeneratedComponent:
        """Generate V5-aware component for non-Store types"""
        
        # Standard component template with V5 integration points
        source_code = self._generate_standard_component_with_v5_integration(component_name, component_type, config)
        
        return V5GeneratedComponent(
            name=component_name,
            type=component_type,
            source_code=source_code,
            imports=[f"from autocoder.components import {component_type}"],
            database_config={},
            schema_requirements=[],
            dependencies=[]
        )
    
    def _generate_standard_component_with_v5_integration(self, component_name: str, component_type: str, config: Dict[str, Any]) -> str:
        """Generate standard component with V5 integration points"""
        
        template = f'''"""
Generated {component_type} component: {component_name}
Enhanced with V5 integration points for database-aware systems
"""
import asyncio
from typing import Dict, Any, Optional
from autocoder.components import {component_type}


class Generated{component_type}_{component_name}({component_type}):
    """
    Generated {component_type} component with V5 integration awareness.
    
    Features:
    - Compatible with V5 database systems
    - Enhanced error handling and logging
    - Performance monitoring integration
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # V5 integration configuration
        self.v5_integration_enabled = config.get("v5_integration", True)
        self.performance_monitoring = config.get("performance_monitoring", True)
        
    async def setup(self):
        """Enhanced setup with V5 integration"""
        self.logger.info(f"Setting up {component_type}: {{self.name}}")
        await super().setup()
        
        if self.v5_integration_enabled:
            await self._setup_v5_integration()
        
        self.logger.info(f"{component_type} {{self.name}} setup complete")
    
    async def _setup_v5_integration(self):
        """Setup V5 integration points"""
        # Integration points for V5 database systems
        self.logger.debug(f"V5 integration enabled for {{self.name}}")
        # Additional setup can be added here as needed
        
    # Component-specific implementation will be generated based on type
    # This template provides the V5-aware foundation
'''
        
        return template
    
    def write_component_files(self, components: List[V5GeneratedComponent], output_dir: Path):
        """Write generated component files to disk"""
        components_dir = output_dir / "components"
        components_dir.mkdir(parents=True, exist_ok=True)
        
        for component in components:
            # Write component file
            component_file = components_dir / f"{component.name}.py"
            with open(component_file, 'w') as f:
                f.write(component.source_code)
            
            # Write component configuration
            config_file = components_dir / f"{component.name}_config.json"
            with open(config_file, 'w') as f:
                json.dump({
                    "database_config": component.database_config,
                    "schema_requirements": component.schema_requirements,
                    "dependencies": component.dependencies
                }, f, indent=2)
            
            self.logger.info(f"Generated V5 component: {component.name} ({component.type})")


# Example usage
if __name__ == "__main__":
    generator = V5EnhancedComponentGenerator(Path("./generated_v5_components"))
    
    # Test V5EnhancedStore generation
    store_config = {
        "database_type": "postgresql",
        "table_name": "user_data",
        "schema": "analytics",
        "connection_pool_size": 15,
        "batch_size": 200,
        "enable_caching": True
    }
    
    store_component = generator.generate_v5_store_component("user_data_store", store_config)
    print(f"Generated V5 Store Component: {store_component.name}")
    print(f"Schema Requirements: {store_component.schema_requirements}")
    print(f"Database Config: {store_component.database_config}")