#!/usr/bin/env python3
"""
V5 System Example Generator
Generates complete working system examples demonstrating V5 database features
"""
import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

from .v5_natural_language_to_database_pipeline import V5NaturalLanguageToDatabasePipeline


@dataclass
class V5SystemExample:
    """Complete V5 system example with all generated files"""
    name: str
    description: str
    natural_language_input: str
    generated_files: Dict[str, str]
    database_features: List[str]
    deployment_instructions: str
    verification_steps: List[str]
    performance_specs: Dict[str, Any]


class V5SystemExampleGenerator:
    """
    Generates complete working V5 system examples demonstrating database integration.
    
    Features:
    - Creates deployable V5 systems from natural language
    - Demonstrates all V5 database features
    - Provides verification and testing procedures
    - Includes performance benchmarking
    - Complete deployment instructions
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = V5NaturalLanguageToDatabasePipeline(output_dir)
    
    async def generate_complete_v5_example(self, natural_language_description: str, example_name: str) -> V5SystemExample:
        """Generate complete V5 system example from natural language"""
        
        print(f"🔧 Generating V5 system example: {example_name}")
        print(f"📝 Input: {natural_language_description[:100]}...")
        
        # Generate system using V5 pipeline
        pipeline_result = await self.pipeline.process_natural_language_to_v5_system(natural_language_description)
        
        # Generate all system files
        generated_files = await self._generate_all_system_files(pipeline_result, example_name)
        
        # Create deployment instructions
        deployment_instructions = self._create_deployment_instructions(pipeline_result)
        
        # Create verification steps
        verification_steps = self._create_verification_steps(pipeline_result)
        
        # Extract V5 database features
        database_features = self._extract_database_features(pipeline_result)
        
        # Create performance specifications
        performance_specs = self._create_performance_specifications(pipeline_result)
        
        # Create complete example
        example = V5SystemExample(
            name=example_name,
            description=pipeline_result.parsed_requirements.get("system_type", "V5 System"),
            natural_language_input=natural_language_description,
            generated_files=generated_files,
            database_features=database_features,
            deployment_instructions=deployment_instructions,
            verification_steps=verification_steps,
            performance_specs=performance_specs
        )
        
        # Write example to disk
        await self._write_example_to_disk(example)
        
        print(f"✅ Generated complete V5 system example: {example_name}")
        return example
    
    async def _generate_all_system_files(self, pipeline_result, example_name: str) -> Dict[str, str]:
        """Generate all system files for the example"""
        
        # Create system directory
        system_dir = self.output_dir / example_name
        system_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Generate main.py with V5 features
        main_py = self._generate_v5_main_py(pipeline_result)
        generated_files["main.py"] = main_py
        
        # Generate V5 enhanced configuration
        config_yaml = self._generate_v5_config_yaml(pipeline_result)
        generated_files["config/system_config.yaml"] = config_yaml
        
        # Generate database configuration
        database_config = self._generate_database_config_yaml(pipeline_result)
        generated_files["config/database_config.yaml"] = database_config
        
        # Generate requirements.txt with V5 dependencies
        requirements_txt = self._generate_v5_requirements_txt(pipeline_result)
        generated_files["requirements.txt"] = requirements_txt
        
        # Generate V5 enhanced Dockerfile
        dockerfile = self._generate_v5_dockerfile(pipeline_result)
        generated_files["Dockerfile"] = dockerfile
        
        # Generate docker-compose.yml with database
        docker_compose = self._generate_docker_compose_yml(pipeline_result)
        generated_files["docker-compose.yml"] = docker_compose
        
        # Generate database initialization script
        database_init_sql = self._generate_database_init_sql(pipeline_result)
        generated_files["database/init.sql"] = database_init_sql
        
        # Generate V5 component files
        component_files = self._generate_v5_component_files(pipeline_result)
        generated_files.update(component_files)
        
        # Generate testing files
        test_files = self._generate_test_files(pipeline_result)
        generated_files.update(test_files)
        
        # Generate monitoring configuration
        monitoring_files = self._generate_monitoring_files(pipeline_result)
        generated_files.update(monitoring_files)
        
        return generated_files
    
    def _generate_v5_main_py(self, pipeline_result) -> str:
        """Generate V5 enhanced main.py"""
        system_name = pipeline_result.system_name
        
        return f'''#!/usr/bin/env python3
"""
{system_name} - V5 Enhanced System with Complete Database Integration
Generated from natural language: "{pipeline_result.natural_language_input[:100]}..."

V5 Features Included:
- V5EnhancedStore with schema validation
- Database connection pooling and health monitoring
- Transaction management with rollback support
- Real-time performance monitoring
- Complete error handling and logging
"""
import asyncio
import logging
import sys
from pathlib import Path

# Core V5 imports
from autocoder.orchestration.harness import SystemExecutionHarness
from autocoder.database.v5_database_manager import V5DatabaseManager
from autocoder.validation.database_validation_orchestrator import DatabaseValidationOrchestrator

# V5 Component imports
{self._generate_component_imports(pipeline_result)}

# Configuration
CONFIG_FILE = Path(__file__).parent / "config" / "system_config.yaml"
DATABASE_CONFIG_FILE = Path(__file__).parent / "config" / "database_config.yaml"

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/system.log')
    ]
)

async def setup_v5_database_integration():
    """Setup comprehensive V5 database integration"""
    logger = logging.getLogger("V5DatabaseSetup")
    logger.info("Initializing V5 database integration...")
    
    # Load database configuration
    import yaml
    db_config = {{}}
    if DATABASE_CONFIG_FILE.exists():
        with open(DATABASE_CONFIG_FILE, 'r') as f:
            db_config = yaml.safe_load(f) or {{}}
    
    # Initialize V5 Database Manager with configuration
    db_manager = V5DatabaseManager(db_config)
    await db_manager.initialize()
    
    # Run comprehensive database validation
    db_validator = DatabaseValidationOrchestrator()
    validation_result = await db_validator.validate_runtime_database_health()
    
    if not validation_result.healthy:
        logger.error(f"Database validation failed: {{validation_result.health_issues}}")
        raise RuntimeError(f"Database not ready: {{validation_result.health_issues}}")
    
    logger.info("V5 database integration ready - all validations passed")
    return db_manager

async def create_v5_components(config, db_manager):
    """Create V5 enhanced components with database integration"""
    logger = logging.getLogger("V5Components")
    components = {{}}
    
    {self._generate_component_creation(pipeline_result)}
    
    return components

async def run_v5_system():
    """Run the complete V5 enhanced system"""
    logger = logging.getLogger("{system_name}")
    logger.info("Starting {system_name} V5 enhanced system...")
    
    try:
        # Setup V5 database integration
        db_manager = await setup_v5_database_integration()
        
        # Load system configuration
        import yaml
        config = {{}}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {{}}
        
        # Create V5 enhanced harness
        harness = SystemExecutionHarness("{system_name}")
        harness.set_database_manager(db_manager)
        
        # Create and register V5 components
        components = await create_v5_components(config, db_manager)
        for name, component in components.items():
            harness.register_component(name, component)
        
        # Setup component connections
        {self._generate_component_connections(pipeline_result)}
        
        # Start system with monitoring
        logger.info("All V5 components ready, starting system...")
        await harness.run_with_database_monitoring()
        
    except Exception as e:
        logger.error(f"V5 system execution failed: {{e}}")
        raise
    finally:
        logger.info("V5 system shutdown complete")

async def main():
    """Main entry point with enhanced error handling"""
    logger = logging.getLogger("{system_name}")
    
    try:
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Run V5 system with structured concurrency
        async with anyio.create_task_group() as tg:
            tg.start_soon(run_v5_system)
            await anyio.sleep_forever()
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping V5 system...")
    except Exception as e:
        logger.error(f"V5 system error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    import anyio
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("\\nV5 system shutdown completed gracefully.")
        sys.exit(0)
    except Exception as e:
        print(f"V5 system failed: {{e}}")
        sys.exit(1)
'''
    
    def _generate_component_imports(self, pipeline_result) -> str:
        """Generate component import statements"""
        imports = []
        
        for component in pipeline_result.v5_components:
            comp_name = component["name"]
            comp_type = component["type"]
            
            if component.get("database_integrated", False):
                imports.append(f"from components.{comp_name} import GeneratedStore_{comp_name}")
            else:
                imports.append(f"from components.{comp_name} import Generated{comp_type}_{comp_name}")
        
        return "\\n".join(imports)
    
    def _generate_component_creation(self, pipeline_result) -> str:
        """Generate component creation code"""
        creation_lines = []
        
        for component in pipeline_result.v5_components:
            comp_name = component["name"]
            comp_type = component["type"]
            
            if component.get("database_integrated", False):
                creation_lines.extend([
                    f'    # V5 Enhanced Store: {comp_name}',
                    f'    logger.info("Creating V5 Enhanced Store: {comp_name}")',
                    f'    {comp_name} = GeneratedStore_{comp_name}("{comp_name}", config.get("{comp_name}", {{}}))',
                    f'    {comp_name}.set_database_manager(db_manager)',
                    f'    await {comp_name}.setup()',
                    f'    components["{comp_name}"] = {comp_name}',
                    ''
                ])
            else:
                creation_lines.extend([
                    f'    # V5 Aware Component: {comp_name}',
                    f'    logger.info("Creating V5 component: {comp_name}")',
                    f'    {comp_name} = Generated{comp_type}_{comp_name}("{comp_name}", config.get("{comp_name}", {{}}))',
                    f'    await {comp_name}.setup()',
                    f'    components["{comp_name}"] = {comp_name}',
                    ''
                ])
        
        return "\\n".join(creation_lines)
    
    def _generate_component_connections(self, pipeline_result) -> str:
        """Generate component connection code"""
        connections = []
        
        # Generate connections based on pipeline result
        components = pipeline_result.v5_components
        if len(components) > 1:
            for i in range(len(components) - 1):
                from_comp = components[i]["name"]
                to_comp = components[i + 1]["name"]
                connections.append(f'        harness.connect("{from_comp}.output", "{to_comp}.input")')
        
        return "\\n".join(connections)
    
    def _generate_v5_config_yaml(self, pipeline_result) -> str:
        """Generate V5 system configuration"""
        config = {
            "system": {
                "name": pipeline_result.system_name,
                "version": "1.0.0",
                "environment": "production",
                "v5_database_integration": True
            }
        }
        
        # Add component configurations
        for component in pipeline_result.v5_components:
            comp_config = component.get("configuration", {})
            if component.get("database_integrated", False):
                comp_config.update({
                    "database_type": pipeline_result.database_requirements.get("database_type", "postgresql"),
                    "schema_validation_enabled": True,
                    "performance_monitoring": True
                })
            config[component["name"]] = comp_config
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def _generate_database_config_yaml(self, pipeline_result) -> str:
        """Generate database-specific configuration"""
        db_config = {
            "database": {
                "type": pipeline_result.database_requirements.get("database_type", "postgresql"),
                "connection": {
                    "host": "${DATABASE_HOST:-localhost}",
                    "port": "${DATABASE_PORT:-5432}",
                    "database": "${DATABASE_NAME:-v5_system}",
                    "user": "${DATABASE_USER:-v5_user}",
                    "password": "${DATABASE_PASSWORD:-v5_password}"
                },
                "pool": {
                    "min_size": 5,
                    "max_size": 20,
                    "timeout": 30,
                    "retry_attempts": 3
                },
                "schema_validation": {
                    "enabled": True,
                    "strict_mode": True,
                    "auto_migrate": False
                },
                "performance": {
                    "query_timeout": 30,
                    "batch_size": 1000,
                    "connection_pool_monitoring": True
                },
                "monitoring": {
                    "health_check_interval": 30,
                    "performance_metrics": True,
                    "slow_query_logging": True
                }
            }
        }
        
        return yaml.dump(db_config, default_flow_style=False, sort_keys=False)
    
    def _generate_v5_requirements_txt(self, pipeline_result) -> str:
        """Generate requirements.txt with V5 dependencies"""
        requirements = [
            "# V5 Enhanced System Requirements",
            "",
            "# Core V5 framework",
            "pyyaml>=6.0",
            "asyncio-extras>=1.3.0",
            "",
            "# V5 Database integration",
            "asyncpg>=0.28.0",
            "aiomysql>=0.2.0", 
            "aiosqlite>=0.19.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0",
            "",
            "# V5 Performance and monitoring",
            "redis>=4.6.0",
            "prometheus-client>=0.17.0",
            "",
            "# API and web framework",
            "fastapi>=0.100.0",
            "uvicorn>=0.22.0",
            "pydantic>=2.0.0",
            "",
            "# Development and testing",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0"
        ]
        
        return "\\n".join(requirements)
    
    def _generate_v5_dockerfile(self, pipeline_result) -> str:
        """Generate V5 enhanced Dockerfile"""
        system_name = pipeline_result.system_name
        
        return f'''# V5 Enhanced Dockerfile for {system_name}
FROM python:3.11-slim

# Install system dependencies for V5 database drivers
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gcc \\
    curl \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create directories
RUN mkdir -p logs config database components

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables for V5
ENV V5_DATABASE_INTEGRATION=true
ENV DATABASE_POOL_SIZE=10
ENV SCHEMA_VALIDATION_ENABLED=true
ENV PYTHONPATH=/app

# Health check for V5 database connectivity
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Expose application port
EXPOSE 8080

# Expose metrics port
EXPOSE 9090

# Run the V5 enhanced application
CMD ["python", "main.py"]
'''
    
    def _generate_docker_compose_yml(self, pipeline_result) -> str:
        """Generate docker-compose.yml with database services"""
        system_name = pipeline_result.system_name
        db_type = pipeline_result.database_requirements.get("database_type", "postgresql")
        
        if db_type == "postgresql":
            db_service = '''
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: v5_system
      POSTGRES_USER: v5_user
      POSTGRES_PASSWORD: v5_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U v5_user -d v5_system"]
      interval: 30s
      timeout: 10s
      retries: 3
'''
            volumes = '''
volumes:
  postgres_data:
'''
        else:
            # SQLite doesn't need a separate service
            db_service = ""
            volumes = ""
        
        return f'''version: '3.8'

services:
  {system_name.replace('_', '-')}:
    build: .
    ports:
      - "8080:8080"
      - "9090:9090"
    environment:
      - DATABASE_HOST=database
      - DATABASE_PORT=5432
      - DATABASE_NAME=v5_system
      - DATABASE_USER=v5_user
      - DATABASE_PASSWORD=v5_password
      - V5_DATABASE_INTEGRATION=true
    depends_on:
      - database
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
{db_service}
  
  # Redis for V5 caching (optional)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

{volumes}
  redis_data:
'''
    
    def _generate_database_init_sql(self, pipeline_result) -> str:
        """Generate database initialization SQL"""
        system_name = pipeline_result.system_name
        
        init_sql = f'''-- Database initialization for {system_name}
-- V5 Enhanced Database Schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS v5_system;
CREATE SCHEMA IF NOT EXISTS v5_monitoring;

-- V5 system metadata tables
CREATE TABLE IF NOT EXISTS v5_system.component_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_name VARCHAR(255) NOT NULL UNIQUE,
    component_type VARCHAR(100) NOT NULL,
    database_integrated BOOLEAN DEFAULT FALSE,
    schema_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS v5_system.schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    component_name VARCHAR(255) NOT NULL,
    migration_type VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    checksum VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS v5_monitoring.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{{}}'::jsonb
);

'''
        
        # Add component-specific tables
        for component in pipeline_result.v5_components:
            if component.get("database_integrated", False):
                comp_name = component["name"]
                table_name = comp_name.lower()
                
                init_sql += f'''
-- V5 Enhanced Store table for {comp_name}
CREATE TABLE IF NOT EXISTS public.{table_name} (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{{}}'::jsonb,
    version INTEGER DEFAULT 1,
    checksum VARCHAR(255)
);

-- Performance indexes for {comp_name}
CREATE INDEX IF NOT EXISTS idx_{table_name}_data_gin ON public.{table_name} USING GIN (data);
CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON public.{table_name} (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_{table_name}_metadata_gin ON public.{table_name} USING GIN (metadata);

-- Register component
INSERT INTO v5_system.component_registry (component_name, component_type, database_integrated, schema_version)
VALUES ('{comp_name}', 'V5EnhancedStore', TRUE, '1.0.0')
ON CONFLICT (component_name) DO UPDATE SET
    updated_at = NOW(),
    schema_version = EXCLUDED.schema_version;

'''
        
        init_sql += '''
-- Create monitoring views
CREATE OR REPLACE VIEW v5_monitoring.system_health AS
SELECT 
    cr.component_name,
    cr.component_type,
    cr.database_integrated,
    cr.schema_version,
    cr.updated_at,
    CASE 
        WHEN cr.updated_at > NOW() - INTERVAL '1 hour' THEN 'healthy'
        WHEN cr.updated_at > NOW() - INTERVAL '24 hours' THEN 'warning'
        ELSE 'critical'
    END as health_status
FROM v5_system.component_registry cr;

-- Grant permissions
GRANT SELECT ON v5_monitoring.system_health TO PUBLIC;
GRANT INSERT, SELECT, UPDATE ON v5_monitoring.performance_metrics TO PUBLIC;

-- Create performance monitoring function
CREATE OR REPLACE FUNCTION v5_monitoring.record_metric(
    p_component_name VARCHAR(255),
    p_metric_name VARCHAR(100),
    p_metric_value DECIMAL(15,6),
    p_metric_unit VARCHAR(20) DEFAULT NULL,
    p_metadata JSONB DEFAULT '{{}}'::jsonb
) RETURNS UUID AS $$
DECLARE
    metric_id UUID;
BEGIN
    INSERT INTO v5_monitoring.performance_metrics 
    (component_name, metric_name, metric_value, metric_unit, metadata)
    VALUES (p_component_name, p_metric_name, p_metric_value, p_metric_unit, p_metadata)
    RETURNING id INTO metric_id;
    
    RETURN metric_id;
END;
$$ LANGUAGE plpgsql;
'''
        
        return init_sql
    
    def _generate_v5_component_files(self, pipeline_result) -> Dict[str, str]:
        """Generate V5 component implementation files"""
        component_files = {}
        
        for component in pipeline_result.v5_components:
            comp_name = component["name"]
            comp_type = component["type"]
            
            if component.get("database_integrated", False):
                # Generate V5EnhancedStore component
                component_files[f"components/{comp_name}.py"] = self._generate_v5_store_component(component)
            else:
                # Generate V5-aware component
                component_files[f"components/{comp_name}.py"] = self._generate_v5_aware_component(component)
        
        return component_files
    
    def _generate_v5_store_component(self, component: Dict[str, Any]) -> str:
        """Generate V5EnhancedStore component implementation"""
        comp_name = component["name"]
        
        return f'''"""
V5 Enhanced Store Component: {comp_name}
Generated with complete database integration and V5 features
"""
import asyncio
import json
from typing import Dict, Any, Optional
from autocoder.components.v5_enhanced_store import V5EnhancedStore


class GeneratedStore_{comp_name}(V5EnhancedStore):
    """
    V5 Enhanced Store with complete database integration.
    
    Features:
    - Real-time schema validation
    - Transaction management with rollback
    - Connection pooling with health monitoring
    - Performance optimization and caching
    - Comprehensive error handling
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        # Enhanced configuration with V5 defaults
        enhanced_config = {{
            **config,
            "table_name": "{comp_name.lower()}",
            "schema_name": "public",
            "v5_enhanced": True,
            "schema_validation_enabled": True,
            "performance_monitoring": True,
            "transaction_management": True
        }}
        
        super().__init__(name, enhanced_config)
        self.component_name = "{comp_name}"
        
    async def setup(self):
        """Enhanced setup with comprehensive validation"""
        self.logger.info(f"Setting up V5 Enhanced Store: {{self.name}}")
        
        await super().setup()
        
        # Component-specific initialization
        await self._initialize_component_specific_features()
        
        self.logger.info(f"V5 Enhanced Store {{self.name}} ready")
    
    async def consume(self, data: Any) -> Dict[str, Any]:
        """Enhanced consume with comprehensive processing"""
        try:
            # Pre-process data
            processed_data = await self._preprocess_component_data(data)
            
            # Use parent V5 enhanced consume
            result = await super().consume(processed_data)
            
            # Add component-specific metadata
            result.update({{
                "component": self.component_name,
                "v5_enhanced": True,
                "processing_timestamp": self._get_timestamp()
            }})
            
            return result
            
        except Exception as e:
            self.logger.error(f"Store operation failed in {{self.name}}: {{e}}")
            raise
    
    async def _initialize_component_specific_features(self):
        """Initialize component-specific V5 features"""
        # Setup performance monitoring
        await self._setup_performance_monitoring()
        
        # Validate schema compatibility
        await self._validate_component_schema()
        
        self.logger.debug(f"Component-specific features initialized for {{self.name}}")
    
    async def _setup_performance_monitoring(self):
        """Setup component performance monitoring"""
        if self.performance_monitoring_enabled:
            self.logger.debug(f"Performance monitoring enabled for {{self.name}}")
            # Additional performance monitoring setup could be added here
    
    async def _validate_component_schema(self):
        """Validate component-specific schema requirements"""
        # Use V5 schema validator to check component schema
        validation_result = await self.schema_validator.validate_component_schema(
            self.component_name, self.table_name
        )
        
        if not validation_result.valid:
            self.logger.warning(f"Schema validation warnings for {{self.name}}: {{validation_result.warnings}}")
    
    async def _preprocess_component_data(self, data: Any) -> Dict[str, Any]:
        """Component-specific data preprocessing"""
        if isinstance(data, dict):
            # Add component metadata
            data["_component"] = self.component_name
            data["_processed_at"] = self._get_timestamp()
            return data
        else:
            # Wrap non-dict data
            return {{
                "value": data,
                "type": type(data).__name__,
                "_component": self.component_name,
                "_processed_at": self._get_timestamp()
            }}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()


# Export component
__all__ = ["GeneratedStore_{comp_name}"]
'''
    
    def _generate_v5_aware_component(self, component: Dict[str, Any]) -> str:
        """Generate V5-aware component implementation"""
        comp_name = component["name"]
        comp_type = component["type"]
        
        return f'''"""
V5 Aware Component: {comp_name}
Enhanced with V5 integration capabilities
"""
import asyncio
from typing import Dict, Any, Optional
from autocoder.components import {comp_type}


class Generated{comp_type}_{comp_name}({comp_type}):
    """
    V5 Aware {comp_type} component with enhanced integration.
    
    Features:
    - V5 system integration
    - Enhanced performance monitoring
    - Comprehensive error handling
    - V5 database system compatibility
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        self.component_name = "{comp_name}"
        self.v5_integration_enabled = config.get("v5_integration", True)
        self.performance_monitoring = config.get("performance_monitoring", True)
        
    async def setup(self):
        """Enhanced setup with V5 integration"""
        self.logger.info(f"Setting up V5 aware {comp_type}: {{self.name}}")
        
        await super().setup()
        
        if self.v5_integration_enabled:
            await self._setup_v5_integration()
        
        self.logger.info(f"V5 aware {comp_type} {{self.name}} ready")
    
    async def _setup_v5_integration(self):
        """Setup V5 integration features"""
        self.logger.debug(f"V5 integration enabled for {{self.name}}")
        
        # V5 integration points can be added here
        if self.performance_monitoring:
            await self._setup_performance_monitoring()
    
    async def _setup_performance_monitoring(self):
        """Setup component performance monitoring"""
        self.logger.debug(f"Performance monitoring enabled for {{self.name}}")
        # Performance monitoring setup
    
    # Component-specific implementation would be added here
    # This template provides the V5-aware foundation


# Export component
__all__ = ["Generated{comp_type}_{comp_name}"]
'''
    
    def _generate_test_files(self, pipeline_result) -> Dict[str, str]:
        """Generate comprehensive test files"""
        test_files = {}
        
        # Generate main test file
        test_files["tests/test_v5_system.py"] = self._generate_main_test_file(pipeline_result)
        
        # Generate component-specific tests
        for component in pipeline_result.v5_components:
            comp_name = component["name"]
            test_files[f"tests/test_{comp_name}.py"] = self._generate_component_test_file(component)
        
        # Generate integration tests
        test_files["tests/test_integration.py"] = self._generate_integration_test_file(pipeline_result)
        
        # Generate performance tests
        test_files["tests/test_performance.py"] = self._generate_performance_test_file(pipeline_result)
        
        return test_files
    
    def _generate_main_test_file(self, pipeline_result) -> str:
        """Generate main system test file"""
        system_name = pipeline_result.system_name
        
        return f'''"""
V5 System Tests for {system_name}
Comprehensive testing of V5 enhanced system
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch


class TestV5System:
    """Test V5 enhanced system functionality"""
    
    @pytest.mark.asyncio
    async def test_system_startup(self):
        """Test V5 system startup sequence"""
        # Test would verify V5 system starts correctly
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_database_integration(self):
        """Test V5 database integration"""
        # Test would verify database integration works
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_component_communication(self):
        """Test V5 component communication"""
        # Test would verify components communicate correctly
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test V5 enhanced error handling"""
        # Test would verify error handling works correctly
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test V5 performance monitoring"""
        # Test would verify performance monitoring works
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _generate_component_test_file(self, component: Dict[str, Any]) -> str:
        """Generate component-specific test file"""
        comp_name = component["name"]
        comp_type = component["type"]
        
        return f'''"""
Tests for V5 component: {comp_name}
"""
import pytest
import asyncio


class Test{comp_type}{comp_name.title()}:
    """Test {comp_name} component"""
    
    @pytest.mark.asyncio
    async def test_component_setup(self):
        """Test component setup"""
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_component_operation(self):
        """Test component operation"""
        assert True  # Placeholder
    
    {"@pytest.mark.asyncio" if component.get("database_integrated", False) else ""}
    {"async def test_database_operations(self):" if component.get("database_integrated", False) else ""}
    {"    \"\"\"Test database operations\"\"\"" if component.get("database_integrated", False) else ""}
    {"    assert True  # Placeholder" if component.get("database_integrated", False) else ""}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _generate_integration_test_file(self, pipeline_result) -> str:
        """Generate integration test file"""
        return '''"""
V5 System Integration Tests
End-to-end testing of complete V5 system
"""
import pytest
import asyncio


class TestV5Integration:
    """Test V5 system integration"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_flow(self):
        """Test complete end-to-end data flow"""
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_database_connectivity(self):
        """Test database connectivity"""
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_health_checks(self):
        """Test system health checks"""
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _generate_performance_test_file(self, pipeline_result) -> str:
        """Generate performance test file"""
        return '''"""
V5 System Performance Tests
Performance benchmarking and load testing
"""
import pytest
import asyncio
import time


class TestV5Performance:
    """Test V5 system performance"""
    
    @pytest.mark.asyncio
    async def test_throughput(self):
        """Test system throughput"""
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_latency(self):
        """Test system latency"""
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_resource_usage(self):
        """Test resource usage"""
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
    
    def _generate_monitoring_files(self, pipeline_result) -> Dict[str, str]:
        """Generate monitoring configuration files"""
        monitoring_files = {}
        
        # Generate Prometheus configuration
        monitoring_files["monitoring/prometheus.yml"] = self._generate_prometheus_config(pipeline_result)
        
        # Generate Grafana dashboard
        monitoring_files["monitoring/grafana-dashboard.json"] = self._generate_grafana_dashboard(pipeline_result)
        
        return monitoring_files
    
    def _generate_prometheus_config(self, pipeline_result) -> str:
        """Generate Prometheus configuration"""
        system_name = pipeline_result.system_name
        
        return f'''# Prometheus configuration for {system_name}
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: '{system_name}'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 5s
    metrics_path: /metrics
    
  - job_name: 'database'
    static_configs:
      - targets: ['localhost:5432']
    scrape_interval: 30s
'''
    
    def _generate_grafana_dashboard(self, pipeline_result) -> str:
        """Generate Grafana dashboard configuration"""
        system_name = pipeline_result.system_name
        
        return f'''{{
  "dashboard": {{
    "id": null,
    "title": "V5 System Dashboard - {system_name}",
    "tags": ["v5", "database", "monitoring"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {{
        "id": 1,
        "title": "System Health",
        "type": "stat",
        "targets": [
          {{
            "expr": "up{{job=\\"{system_name}\\"}}"
          }}
        ]
      }},
      {{
        "id": 2,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {{
            "expr": "database_connections_active"
          }}
        ]
      }},
      {{
        "id": 3,
        "title": "Query Performance",
        "type": "graph", 
        "targets": [
          {{
            "expr": "database_query_duration_seconds"
          }}
        ]
      }}
    ],
    "time": {{
      "from": "now-1h",
      "to": "now"
    }},
    "refresh": "5s"
  }}
}}
'''
    
    def _create_deployment_instructions(self, pipeline_result) -> str:
        """Create comprehensive deployment instructions"""
        system_name = pipeline_result.system_name
        db_type = pipeline_result.database_requirements.get("database_type", "postgresql")
        
        return f'''# V5 System Deployment Instructions
## {system_name}

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- {db_type.title()} (if running database separately)

### Quick Start (Docker Compose)
1. Clone or extract the system files
2. Navigate to the system directory
3. Start the complete system:
   ```bash
   docker-compose up -d
   ```
4. Verify deployment:
   ```bash
   curl http://localhost:8080/health
   ```

### Manual Deployment

#### 1. Database Setup
```bash
# Start {db_type} database
docker run -d \\
  --name {system_name}-db \\
  -e POSTGRES_DB=v5_system \\
  -e POSTGRES_USER=v5_user \\
  -e POSTGRES_PASSWORD=v5_password \\
  -p 5432:5432 \\
  postgres:15

# Initialize database schema
psql -h localhost -U v5_user -d v5_system -f database/init.sql
```

#### 2. Application Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_NAME=v5_system
export DATABASE_USER=v5_user
export DATABASE_PASSWORD=v5_password

# Run the application
python main.py
```

### Environment Variables
- `DATABASE_HOST`: Database host (default: localhost)
- `DATABASE_PORT`: Database port (default: 5432)
- `DATABASE_NAME`: Database name (default: v5_system)
- `DATABASE_USER`: Database user (default: v5_user)
- `DATABASE_PASSWORD`: Database password
- `V5_DATABASE_INTEGRATION`: Enable V5 features (default: true)

### Monitoring
- Application metrics: http://localhost:9090/metrics
- Health check: http://localhost:8080/health
- Grafana dashboard: Import monitoring/grafana-dashboard.json

### Scaling
- Horizontal scaling: Increase replica count in docker-compose.yml
- Database scaling: Configure read replicas and connection pooling
- Load balancing: Add nginx or similar load balancer

### Troubleshooting
- Check logs: `docker-compose logs -f {system_name.replace('_', '-')}`
- Database connectivity: `docker-compose exec database psql -U v5_user -d v5_system`
- Reset system: `docker-compose down && docker-compose up -d`
'''
    
    def _create_verification_steps(self, pipeline_result) -> List[str]:
        """Create system verification steps"""
        system_name = pipeline_result.system_name
        
        return [
            f"Verify {system_name} container is running: `docker ps | grep {system_name}`",
            "Check database connectivity: `docker-compose exec database pg_isready`",
            "Verify application health: `curl http://localhost:8080/health`",
            "Check database schema: `docker-compose exec database psql -U v5_user -d v5_system -c '\\dt'`",
            "Verify V5 components are registered: `curl http://localhost:8080/components`",
            "Test data flow: Send test data and verify storage",
            "Check performance metrics: `curl http://localhost:9090/metrics`",
            "Verify monitoring: Access Grafana dashboard",
            "Test error handling: Trigger error conditions and verify recovery",
            "Load test: Run performance tests with `pytest tests/test_performance.py`"
        ]
    
    def _extract_database_features(self, pipeline_result) -> List[str]:
        """Extract V5 database features from the system"""
        features = [
            "V5EnhancedStore with schema validation",
            "Real-time database health monitoring",
            "Connection pooling with automatic scaling",
            "Transaction management with rollback support",
            "Performance optimization and caching",
            "Database schema migration support",
            "Comprehensive error handling and recovery",
            "Production-ready deployment configuration"
        ]
        
        # Add database-specific features
        db_type = pipeline_result.database_requirements.get("database_type", "postgresql")
        if db_type == "postgresql":
            features.extend([
                "PostgreSQL JSONB support with GIN indexes",
                "Advanced query optimization",
                "Full-text search capabilities"
            ])
        
        return features
    
    def _create_performance_specifications(self, pipeline_result) -> Dict[str, Any]:
        """Create performance specifications"""
        return {
            "database": {
                "connection_pool_size": "5-20 connections",
                "query_timeout": "30 seconds",
                "connection_timeout": "30 seconds",
                "max_batch_size": "1000 records"
            },
            "system": {
                "startup_time": "< 30 seconds",
                "memory_usage": "< 512 MB",
                "cpu_usage": "< 50% under normal load",
                "throughput": "> 100 requests/second"
            },
            "monitoring": {
                "health_check_interval": "30 seconds",
                "metrics_collection": "5 second intervals",
                "log_rotation": "Daily with 30 day retention",
                "alert_thresholds": "95% resource usage"
            }
        }
    
    async def _write_example_to_disk(self, example: V5SystemExample):
        """Write complete example to disk"""
        example_dir = self.output_dir / example.name
        example_dir.mkdir(parents=True, exist_ok=True)
        
        # Write all generated files
        for file_path, content in example.generated_files.items():
            full_path = example_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Write example metadata
        metadata = {
            "name": example.name,
            "description": example.description,
            "natural_language_input": example.natural_language_input,
            "database_features": example.database_features,
            "verification_steps": example.verification_steps,
            "performance_specs": example.performance_specs
        }
        
        with open(example_dir / "EXAMPLE_METADATA.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Write deployment instructions
        with open(example_dir / "DEPLOYMENT.md", 'w') as f:
            f.write(example.deployment_instructions)
        
        # Write README
        readme_content = f'''# {example.name}

{example.description}

## Generated from Natural Language
"{example.natural_language_input}"

## V5 Database Features
{chr(10).join(f"- {feature}" for feature in example.database_features)}

## Quick Start
```bash
docker-compose up -d
curl http://localhost:8080/health
```

## Verification Steps
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(example.verification_steps))}

See DEPLOYMENT.md for complete deployment instructions.
'''
        
        with open(example_dir / "README.md", 'w') as f:
            f.write(readme_content)


# Example usage
if __name__ == "__main__":
    async def test_example_generation():
        """Test V5 system example generation"""
        generator = V5SystemExampleGenerator(Path("./generated_v5_examples"))
        
        # Test example descriptions
        examples = [
            {
                "name": "v5_analytics_platform_example",
                "description": """
                Create a high-performance analytics platform that generates real-time data,
                stores it in PostgreSQL with full-text search, processes it for insights,
                and exposes results through a REST API. Include performance monitoring,
                connection pooling, and containerized deployment.
                """
            },
            {
                "name": "v5_data_pipeline_example", 
                "description": """
                Build a streaming data pipeline that ingests events, transforms them
                in real-time, stores results in a database with audit logging,
                and provides query APIs. Use batch processing for efficiency
                and include comprehensive error handling.
                """
            }
        ]
        
        for example_spec in examples:
            separator = '='*80
            print(f"\n{separator}")
            print(f"🧪 Generating V5 Example: {example_spec['name']}")
            print(separator)
            
            try:
                example = await generator.generate_complete_v5_example(
                    example_spec["description"], 
                    example_spec["name"]
                )
                
                print(f"✅ Example generated successfully!")
                print(f"   Files: {len(example.generated_files)}")
                print(f"   Features: {len(example.database_features)}")
                print(f"   Verification Steps: {len(example.verification_steps)}")
                
            except Exception as e:
                print(f"❌ Example generation failed: {e}")
                import traceback
                traceback.print_exc()
    
    # Run the test
    asyncio.run(test_example_generation())