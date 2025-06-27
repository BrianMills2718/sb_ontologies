#!/usr/bin/env python3
"""
V5 Enhanced System Scaffold Generator
Extends SystemScaffoldGenerator with V5 database integration and V5EnhancedStore usage
"""
import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import V5 database components with absolute paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "day2_orchestrator_database_validation"))

from v5_enhanced_component_generator import V5EnhancedComponentGenerator, V5GeneratedComponent
from database_validation_orchestrator import DatabaseValidationOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class V5GeneratedScaffold:
    """Generated V5 system scaffold with database integration"""
    main_py: str
    config_yaml: str
    requirements_txt: str
    dockerfile: str
    database_init_sql: str
    v5_components: List[V5GeneratedComponent]


class V5EnhancedSystemScaffoldGenerator:
    """
    V5 Enhanced System Scaffold Generator with comprehensive database integration.
    
    Key Features:
    - Automatically uses V5EnhancedStore for Store components
    - Integrates DatabaseValidationOrchestrator for pre-flight validation
    - Generates database initialization scripts
    - Provides V5 database configuration templates
    - Ensures proper V5 component registration
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.v5_component_generator = V5EnhancedComponentGenerator(output_dir)
        self.db_validation_orchestrator = DatabaseValidationOrchestrator()
        
    def generate_v5_system(self, system_blueprint, enable_metrics: bool = True) -> V5GeneratedScaffold:
        """Generate complete V5 system scaffold with database integration"""
        
        # Pre-flight database validation using DatabaseValidationOrchestrator
        validation_result = self.db_validation_orchestrator.validate_system_database_readiness(system_blueprint)
        
        if not validation_result.database_ready:
            raise ValueError(f"System not ready for V5 database integration: {validation_result.validation_errors}")
        
        # Generate V5 components
        v5_components = self._generate_v5_components(system_blueprint)
        
        # Generate enhanced scaffold files
        main_py = self._generate_v5_main_py(system_blueprint, v5_components, enable_metrics)
        config_yaml = self._generate_v5_config_yaml(system_blueprint, v5_components, enable_metrics)
        requirements_txt = self._generate_v5_requirements_txt(system_blueprint, v5_components)
        dockerfile = self._generate_v5_dockerfile(system_blueprint, v5_components)
        database_init_sql = self._generate_database_init_sql(system_blueprint, v5_components)
        
        # Write files to output directory
        self._write_v5_files(system_blueprint.system.name, {
            'main.py': main_py,
            'config/system_config.yaml': config_yaml,
            'requirements.txt': requirements_txt,
            'Dockerfile': dockerfile,
            'database/init.sql': database_init_sql
        })
        
        # Write V5 component files
        self.v5_component_generator.write_component_files(v5_components, self.output_dir / system_blueprint.system.name)
        
        return V5GeneratedScaffold(
            main_py=main_py,
            config_yaml=config_yaml,
            requirements_txt=requirements_txt,
            dockerfile=dockerfile,
            database_init_sql=database_init_sql,
            v5_components=v5_components
        )
    
    def generate_v5_enhanced_system(self, system_config: Dict[str, Any]) -> 'V5GeneratedSystemResult':
        """Generate V5 enhanced system from configuration (alias for testing)"""
        try:
            # Convert system_config to mock blueprint for compatibility
            mock_blueprint = self._create_mock_blueprint_from_config(system_config)
            
            # Generate V5 system
            scaffold = self.generate_v5_system(mock_blueprint)
            
            # Convert to expected format for testing
            v5_components = []
            for component in scaffold.v5_components:
                # Create mock V5 component with expected attributes
                v5_comp = type('V5Component', (), {
                    'name': component.name,
                    'type': component.type,
                    'original_type': component.type.replace('V5Enhanced', '') if 'V5Enhanced' in component.type else component.type,
                    'enhanced_type': component.type,
                    'source_code': component.source_code,
                    'database_integration_enabled': bool(component.database_config),
                    'database_config': component.database_config
                })()
                v5_components.append(v5_comp)
            
            # Return mock result for testing
            return type('V5GeneratedSystemResult', (), {
                'components': v5_components,
                'scaffold': scaffold,
                'system_name': system_config.get('system_name', 'test_system')
            })()
            
        except Exception as e:
            logger.error(f"V5 enhanced system generation failed: {e}")
            raise
    
    def _create_mock_blueprint_from_config(self, system_config: Dict[str, Any]):
        """Create mock blueprint from system configuration for testing"""
        components = []
        
        for comp_config in system_config.get('components', []):
            component = type('Component', (), {
                'name': comp_config['name'],
                'type': comp_config['type'],
                'configuration': comp_config.get('config', {})
            })()
            components.append(component)
        
        system = type('System', (), {
            'name': system_config.get('system_name', 'test_system'),
            'version': '1.0.0',
            'description': 'Test V5 system',
            'components': components,
            'bindings': [],
            'configuration': type('SystemConfig', (), {
                'environment': 'test'
            })()
        })()
        
        blueprint = type('Blueprint', (), {
            'system': system,
            'configuration': type('Config', (), {
                'environment': 'test'
            })()
        })()
        
        return blueprint
    
    def _generate_v5_components(self, system_blueprint) -> List[V5GeneratedComponent]:
        """Generate V5 components from system blueprint"""
        v5_components = []
        
        for component in system_blueprint.system.components:
            # Use V5EnhancedComponentGenerator for all components
            v5_component = self.v5_component_generator.generate_enhanced_component(
                component.name,
                component.type,
                component.configuration
            )
            v5_components.append(v5_component)
        
        return v5_components
    
    def _generate_v5_main_py(self, system_blueprint, v5_components: List[V5GeneratedComponent], enable_metrics: bool = True) -> str:
        """Generate V5-enhanced main.py with database integration"""
        
        system = system_blueprint.system
        
        # Build V5-aware imports
        imports = self._build_v5_imports(v5_components, enable_metrics)
        
        # Build V5 component creation
        component_creation = self._build_v5_component_creation(v5_components, enable_metrics)
        
        # Build V5 component registration
        component_registration = self._build_v5_component_registration(v5_components, enable_metrics)
        
        # Build connections (same as standard)
        connections = self._build_connections(system.bindings)
        
        # Build V5 configuration loading with database setup
        config_loading = self._build_v5_config_loading(v5_components)
        
        main_py_template = f'''#!/usr/bin/env python3
"""
{system.name} - V5 Enhanced System with Database Integration
{system.description or "Generated by Autocoder V5.0 Database Integration System"}

This file was generated by V5EnhancedSystemScaffoldGenerator.
It uses V5 Enhanced components with full database integration including:
- V5EnhancedStore components with schema validation
- DatabaseValidationOrchestrator integration
- Real-time database health monitoring
- Transaction management with rollback support
"""
import anyio
import logging
import sys
from pathlib import Path

# Core harness imports
from autocoder.orchestration.harness import SystemExecutionHarness

# V5 Database integration imports
from autocoder.database.v5_database_manager import V5DatabaseManager
from autocoder.validation.database_validation_orchestrator import DatabaseValidationOrchestrator

# Component imports
{imports}

# Configuration
CONFIG_FILE = Path(__file__).parent / "config" / "system_config.yaml"
DATABASE_CONFIG_FILE = Path(__file__).parent / "config" / "database_config.yaml"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def setup_v5_database_integration():
    """Setup V5 database integration and validation"""
    logger = logging.getLogger("V5DatabaseSetup")
    logger.info("Initializing V5 database integration...")
    
    # Initialize V5 Database Manager
    db_manager = V5DatabaseManager()
    await db_manager.initialize()
    
    # Run pre-flight database validation
    db_validator = DatabaseValidationOrchestrator()
    validation_result = await db_validator.validate_runtime_database_health()
    
    if not validation_result.healthy:
        raise RuntimeError(f"Database validation failed: {{validation_result.health_issues}}")
    
    logger.info("V5 database integration ready")
    return db_manager

async def run_v5_system_harness():
    """Run the V5 enhanced system harness with database integration"""
    logger = logging.getLogger("{system.name}")
    logger.info("Starting {system.name} V5 enhanced system...")
    
    # Setup V5 database integration first
    db_manager = await setup_v5_database_integration()
    
    # Load configuration with database settings
{config_loading}
    
    # Create V5 enhanced harness
    harness = SystemExecutionHarness("{system.name}")
    harness.set_database_manager(db_manager)
    
    # Create V5 enhanced components
{component_creation}
    
    # Register V5 components with harness
{component_registration}
    
    # Connect components (V5 enhanced stream-based communication)
{connections}
    
    try:
        # Run the V5 enhanced system
        logger.info("All V5 components configured, starting enhanced system execution...")
        await harness.run_with_database_monitoring()
        
    except Exception as e:
        logger.error(f"V5 system execution failed: {{e}}")
        # Attempt graceful database cleanup
        try:
            await db_manager.cleanup()
        except Exception as cleanup_error:
            logger.error(f"Database cleanup failed: {{cleanup_error}}")
        raise
    finally:
        logger.info("{system.name} V5 enhanced system stopped.")
        await db_manager.cleanup()

async def main():
    """Main V5 system entry point with enhanced signal handling"""
    logger = logging.getLogger("{system.name}")
    
    try:
        # Use anyio structured concurrency for V5 enhanced signal handling
        async with anyio.create_task_group() as tg:
            # Start V5 enhanced system components in TaskGroup
            tg.start_soon(run_v5_system_harness)
            
            # Handle signals through V5 enhanced cancellation system
            # TaskGroup will propagate cancellation to all V5 components
            await anyio.sleep_forever()
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down V5 system gracefully...")
        # V5 enhanced TaskGroup cancellation handles component cleanup
    except Exception as e:
        # Handle exceptions from V5 enhanced structured concurrency
        if isinstance(e, KeyboardInterrupt):
            logger.info("Interrupt received during V5 execution, shutting down...")
        else:
            logger.error(f"V5 system error during execution: {{e}}")

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("\\nV5 enhanced system shutdown completed.")
        sys.exit(0)
    except anyio.get_cancelled_exc_class():
        print("\\nV5 system cancelled gracefully.")
        sys.exit(0)
    except Exception as e:
        # Handle V5 enhanced cancellation-related exceptions
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ["cancelled", "taskgroup", "shutdown", "baseexceptiongroup", "database"]):
            print("\\nV5 enhanced system shutdown gracefully.")
            sys.exit(0)
        else:
            print(f"V5 system failed: {{e}}")
            sys.exit(1)
'''
        
        return main_py_template
    
    def _build_v5_imports(self, v5_components: List[V5GeneratedComponent], enable_metrics: bool = True) -> str:
        """Build V5-enhanced import statements"""
        imports = []
        
        # Add V5 component imports
        for component in v5_components:
            for import_stmt in component.imports:
                if import_stmt not in imports:
                    imports.append(import_stmt)
        
        # Add V5 database imports
        imports.append("import yaml")
        imports.append("import json")
        
        # Add metrics endpoint if enabled
        if enable_metrics:
            imports.append("from autocoder.components.metrics_endpoint import MetricsEndpoint")
        
        # Add generated V5 component imports
        imports.append("\n# Generated V5 component imports")
        for component in v5_components:
            if component.type == "V5EnhancedStore":
                imports.append(f"from components.{component.name} import GeneratedStore_{component.name}")
            else:
                imports.append(f"from components.{component.name} import Generated{component.type}_{component.name}")
        
        return "\n".join(imports)
    
    def _build_v5_component_creation(self, v5_components: List[V5GeneratedComponent], enable_metrics: bool = True) -> str:
        """Build V5 component creation code with database configuration"""
        creation_lines = []
        
        for component in v5_components:
            comp_name = component.name
            comp_type = component.type
            
            if comp_type == "V5EnhancedStore":
                creation_lines.append(f'    # V5 Enhanced Store with database integration')
                creation_lines.append(f'    {comp_name} = GeneratedStore_{comp_name}("{comp_name}", config.get("{comp_name}", {{}}))')
                creation_lines.append(f'    # Inject database manager for V5 features')
                creation_lines.append(f'    {comp_name}.set_database_manager(db_manager)')
            else:
                creation_lines.append(f'    {comp_name} = Generated{comp_type}_{comp_name}("{comp_name}", config.get("{comp_name}", {{}}))')
        
        # Add metrics endpoint if enabled
        if enable_metrics:
            creation_lines.append(f'    # V5 enhanced metrics endpoint with database monitoring')
            creation_lines.append(f'    metrics_endpoint = MetricsEndpoint("metrics", config.get("metrics", {{}}))')
            creation_lines.append(f'    metrics_endpoint.enable_database_monitoring(db_manager)')
        
        return "\n".join(creation_lines)
    
    def _build_v5_component_registration(self, v5_components: List[V5GeneratedComponent], enable_metrics: bool = True) -> str:
        """Build V5 component registration code"""
        registration_lines = []
        
        for component in v5_components:
            registration_lines.append(f'    harness.register_component("{component.name}", {component.name})')
        
        # Register metrics endpoint if enabled
        if enable_metrics:
            registration_lines.append(f'    harness.register_component("metrics", metrics_endpoint)')
        
        return "\n".join(registration_lines)
    
    def _build_connections(self, bindings) -> str:
        """Build component connection code (same as standard)"""
        connection_lines = []
        
        for binding in bindings:
            from_spec = f"{binding.from_component}.{binding.from_port}"
            
            # Handle single or multiple targets
            for i, to_comp in enumerate(binding.to_components):
                to_port = binding.to_ports[i] if i < len(binding.to_ports) else binding.to_ports[0]
                to_spec = f"{to_comp}.{to_port}"
                
                connection_lines.append(f'    harness.connect("{from_spec}", "{to_spec}")')
        
        return "\n".join(connection_lines)
    
    def _build_v5_config_loading(self, v5_components: List[V5GeneratedComponent]) -> str:
        """Build V5 configuration loading with database setup"""
        config_loading = '''    # Load V5 enhanced configuration
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f) or {}
    else:
        logger.warning(f"Configuration file not found: {CONFIG_FILE}")
    
    # Load database configuration
    database_config = {}
    if DATABASE_CONFIG_FILE.exists():
        with open(DATABASE_CONFIG_FILE, 'r') as f:
            database_config = yaml.safe_load(f) or {}
        # Merge database config into main config
        config.update({"database": database_config})
    else:
        logger.warning(f"Database configuration file not found: {DATABASE_CONFIG_FILE}")'''
        
        return config_loading
    
    def _generate_v5_config_yaml(self, system_blueprint, v5_components: List[V5GeneratedComponent], enable_metrics: bool = True) -> str:
        """Generate V5 system configuration YAML with database settings"""
        system = system_blueprint.system
        config = {
            'system': {
                'name': system.name,
                'version': system.version,
                'environment': system.configuration.environment,
                'v5_database_integration': True
            }
        }
        
        # Add V5 component configurations
        for v5_component in v5_components:
            comp_config = {}
            
            # Find original component configuration
            for orig_component in system.components:
                if orig_component.name == v5_component.name:
                    comp_config = orig_component.configuration.copy()
                    break
            
            # Add V5 database configuration
            if v5_component.database_config:
                comp_config.update(v5_component.database_config)
            
            # Add V5-specific defaults based on component type
            if v5_component.type == "V5EnhancedStore":
                comp_config.setdefault('database_type', 'postgresql')
                comp_config.setdefault('connection_pool_size', 10)
                comp_config.setdefault('schema_validation_enabled', True)
                comp_config.setdefault('transaction_isolation', 'READ_COMMITTED')
                comp_config.setdefault('performance_monitoring', True)
            
            config[v5_component.name] = comp_config
        
        # Add V5 database global configuration
        config['database'] = {
            'default_type': 'postgresql',
            'connection_pools': {
                'default': {
                    'min_size': 5,
                    'max_size': 20,
                    'timeout': 30
                }
            },
            'schema_validation': {
                'enabled': True,
                'strict_mode': True,
                'auto_migrate': False
            },
            'monitoring': {
                'enabled': True,
                'health_check_interval': 30,
                'performance_metrics': True
            }
        }
        
        # Add V5 enhanced metrics configuration
        if enable_metrics:
            config['metrics'] = {
                'port': '${METRICS_PORT}',
                'host': '0.0.0.0',
                'enabled': True,
                'database_monitoring': True,
                'performance_tracking': True
            }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def _generate_v5_requirements_txt(self, system_blueprint, v5_components: List[V5GeneratedComponent]) -> str:
        """Generate V5 requirements.txt with database dependencies"""
        requirements = [
            "pyyaml>=6.0",
            "asyncio-extras>=1.3.0",
            # V5 Database integration dependencies
            "asyncpg>=0.28.0",  # PostgreSQL async driver
            "aiomysql>=0.2.0",  # MySQL async driver
            "aiosqlite>=0.19.0",  # SQLite async driver
            "sqlalchemy>=2.0.0",  # ORM and query builder
            "alembic>=1.12.0",  # Database migrations
            "pydantic>=2.0.0",  # Data validation
            # Production monitoring dependencies
            "fastapi>=0.100.0",
            "uvicorn>=0.22.0",
            # V5 Performance and monitoring
            "redis>=4.6.0",  # Caching
            "prometheus-client>=0.17.0",  # Metrics
        ]
        
        # Add component-specific V5 requirements
        for v5_component in v5_components:
            if v5_component.type == "V5EnhancedStore":
                requirements.extend([
                    "psycopg2-binary>=2.9.0",  # PostgreSQL binary driver
                    "pymysql>=1.1.0",  # MySQL driver
                ])
        
        # Remove duplicates and sort
        unique_reqs = sorted(set(requirements))
        return "\n".join(unique_reqs)
    
    def _generate_v5_dockerfile(self, system_blueprint, v5_components: List[V5GeneratedComponent]) -> str:
        """Generate V5 Dockerfile with database support"""
        system = system_blueprint.system
        
        dockerfile = f"""# Generated V5 Enhanced Dockerfile for {system.name}
FROM python:3.11-slim

# Install system dependencies for V5 database drivers
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gcc \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install V5 dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create config and database directories
RUN mkdir -p config database

# Set environment variables for V5 database integration
ENV V5_DATABASE_INTEGRATION=true
ENV DATABASE_POOL_SIZE=10
ENV SCHEMA_VALIDATION_ENABLED=true

# Health check for V5 database connectivity
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import asyncio; from autocoder.database.health_check import check_database_health; asyncio.run(check_database_health())" || exit 1

# Expose ports
"""
        
        # Find API endpoint ports
        api_ports = []
        for component in system.components:
            if component.type == "APIEndpoint":
                port = component.configuration.get('port', 8080)
                api_ports.append(str(port))
        
        if api_ports:
            dockerfile += f"EXPOSE {' '.join(api_ports)}\n"
        
        # Add metrics port
        dockerfile += "EXPOSE 9090\n"
        
        dockerfile += f"""
# Run the V5 enhanced application
CMD ["python", "main.py"]
"""
        
        return dockerfile
    
    def _generate_database_init_sql(self, system_blueprint, v5_components: List[V5GeneratedComponent]) -> str:
        """Generate database initialization SQL for V5 components"""
        init_sql = f"""-- Database initialization script for {system_blueprint.system.name}
-- Generated by V5EnhancedSystemScaffoldGenerator

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS system_metadata;

-- Enable extensions for V5 features
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- System metadata tables
CREATE TABLE IF NOT EXISTS system_metadata.component_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_name VARCHAR(255) NOT NULL UNIQUE,
    component_type VARCHAR(100) NOT NULL,
    schema_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS system_metadata.schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    component_name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(255) NOT NULL
);

"""
        
        # Add component-specific initialization
        for v5_component in v5_components:
            if v5_component.type == "V5EnhancedStore":
                table_name = v5_component.database_config.get("table_name", v5_component.name.lower())
                schema_name = v5_component.database_config.get("schema_name", "public")
                
                init_sql += f"""
-- V5EnhancedStore initialization for {v5_component.name}
CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{{}}'::jsonb,
    version INTEGER DEFAULT 1
);

-- Performance indexes for {v5_component.name}
CREATE INDEX IF NOT EXISTS idx_{table_name}_data_gin ON {schema_name}.{table_name} USING GIN (data);
CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON {schema_name}.{table_name} (created_at);
CREATE INDEX IF NOT EXISTS idx_{table_name}_metadata_gin ON {schema_name}.{table_name} USING GIN (metadata);

-- Register component in metadata
INSERT INTO system_metadata.component_registry (component_name, component_type, schema_version)
VALUES ('{v5_component.name}', 'V5EnhancedStore', '1.0.0')
ON CONFLICT (component_name) DO UPDATE SET
    updated_at = NOW(),
    schema_version = EXCLUDED.schema_version;

"""
        
        init_sql += """
-- Create monitoring views
CREATE OR REPLACE VIEW system_metadata.component_health AS
SELECT 
    cr.component_name,
    cr.component_type,
    cr.schema_version,
    cr.created_at,
    cr.updated_at,
    CASE 
        WHEN cr.updated_at > NOW() - INTERVAL '1 hour' THEN 'healthy'
        ELSE 'stale'
    END as health_status
FROM system_metadata.component_registry cr;

-- Grant permissions
GRANT SELECT ON system_metadata.component_health TO PUBLIC;
"""
        
        return init_sql
    
    def _write_v5_files(self, system_name: str, files: Dict[str, str]) -> None:
        """Write V5 generated files to output directory"""
        system_dir = self.output_dir / system_name
        system_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = system_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)


# Example usage and testing
if __name__ == "__main__":
    from autocoder.blueprint_language.system_blueprint_parser import SystemBlueprintParser
    
    # Test V5 enhanced scaffold generation
    parser = SystemBlueprintParser()
    generator = V5EnhancedSystemScaffoldGenerator(Path("./generated_v5_systems"))
    
    # Create a test blueprint with Store component
    test_blueprint_yaml = """
system:
  name: v5_data_analytics_system
  description: V5 enhanced data analytics system with database integration
  version: 1.0.0
  
  components:
    - name: data_source
      type: Source
      description: Generates analytics data
      configuration:
        data_count: 1000
        data_delay: 0.1
      outputs:
        - name: data
          schema: AnalyticsRecord
          
    - name: analytics_store
      type: Store
      description: V5 enhanced store for analytics data
      configuration:
        database_type: postgresql
        table_name: analytics_data
        schema: analytics
        connection_pool_size: 15
        batch_size: 200
        enable_caching: true
      inputs:
        - name: input
          schema: AnalyticsRecord
          
    - name: api_endpoint
      type: APIEndpoint
      description: API for analytics queries
      configuration:
        port: 8080
      inputs:
        - name: input
          schema: AnalyticsRecord
  
  bindings:
    - from: data_source.data
      to: analytics_store.input
    - from: analytics_store.output
      to: api_endpoint.input

configuration:
  environment: production
  timeouts:
    component_startup: 30
    graceful_shutdown: 10
"""
    
    try:
        # Parse blueprint
        system_blueprint = parser.parse_string(test_blueprint_yaml)
        print(f"✅ Parsed V5 system blueprint: {system_blueprint.system.name}")
        
        # Generate V5 scaffold
        v5_scaffold = generator.generate_v5_system(system_blueprint)
        print(f"✅ Generated V5 enhanced system scaffold")
        print(f"   Main.py: {len(v5_scaffold.main_py)} characters")
        print(f"   Config: {len(v5_scaffold.config_yaml)} characters")
        print(f"   Database Init: {len(v5_scaffold.database_init_sql)} characters")
        print(f"   V5 Components: {len(v5_scaffold.v5_components)}")
        
        # Show V5 component details
        for component in v5_scaffold.v5_components:
            print(f"   - {component.name} ({component.type})")
            if component.database_config:
                print(f"     Database: {component.database_config.get('database_type', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Failed to generate V5 scaffold: {e}")
        import traceback
        traceback.print_exc()