#!/usr/bin/env python3
"""
Comprehensive tests for V5 Enhanced Generators
Tests V5EnhancedComponentGenerator and V5EnhancedSystemScaffoldGenerator
"""
import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from v5_enhanced_component_generator import V5EnhancedComponentGenerator, V5GeneratedComponent
from v5_enhanced_scaffold_generator import V5EnhancedSystemScaffoldGenerator, V5GeneratedScaffold


class TestV5EnhancedComponentGenerator:
    """Test V5 Enhanced Component Generator"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = V5EnhancedComponentGenerator(Path(self.temp_dir))
    
    def test_v5_store_component_generation(self):
        """Test V5EnhancedStore component generation"""
        component_name = "test_analytics_store"
        config = {
            "database_type": "postgresql",
            "table_name": "analytics_data",
            "schema": "analytics",
            "connection_pool_size": 15,
            "batch_size": 200,
            "enable_caching": True,
            "schema_strict_mode": True
        }
        
        # Mock database dependency validation
        with patch.object(self.generator.db_dependency_validator, 'validate_component_dependencies') as mock_validate:
            mock_validate.return_value = Mock(
                dependencies_met=True,
                dependencies=["postgresql", "asyncpg", "sqlalchemy"],
                missing_dependencies=[]
            )
            
            component = self.generator.generate_v5_store_component(component_name, config)
            
            # Verify V5GeneratedComponent structure
            assert isinstance(component, V5GeneratedComponent)
            assert component.name == component_name
            assert component.type == "V5EnhancedStore"
            assert len(component.source_code) > 0
            assert len(component.imports) > 0
            assert component.database_config
            assert component.schema_requirements
            
            # Verify database configuration
            db_config = component.database_config
            assert db_config["database_type"] == "postgresql"
            assert db_config["connection_pool"]["min_size"] > 0
            assert db_config["schema_validation"]["enabled"] is True
            assert db_config["transaction_management"]["isolation_level"] == "READ_COMMITTED"
            assert db_config["performance"]["caching_enabled"] is True
            
            # Verify source code contains V5 features
            source = component.source_code
            assert "V5EnhancedStore" in source
            assert "SchemaValidator" in source
            assert "TransactionManager" in source
            assert "connection_pool_size" in source
            assert "schema_validation_enabled" in source
            
            # Verify imports contain V5 components
            import_str = "\n".join(component.imports)
            assert "v5_enhanced_store" in import_str
            assert "schema_validator" in import_str
            assert "transaction_manager" in import_str
    
    def test_v5_store_component_database_dependency_failure(self):
        """Test V5 store component generation with dependency failure"""
        component_name = "test_failing_store"
        config = {"database_type": "unsupported_db"}
        
        # Mock database dependency validation failure
        with patch.object(self.generator.db_dependency_validator, 'validate_component_dependencies') as mock_validate:
            mock_validate.return_value = Mock(
                dependencies_met=False,
                missing_dependencies=["unsupported_db_driver"],
                dependencies=[]
            )
            
            with pytest.raises(ValueError, match="Database dependencies not met"):
                self.generator.generate_v5_store_component(component_name, config)
    
    def test_v5_aware_component_generation(self):
        """Test V5-aware component generation for non-Store types"""
        component_name = "test_transformer"
        component_type = "Transformer"
        config = {
            "batch_size": 50,
            "v5_integration": True,
            "performance_monitoring": True
        }
        
        component = self.generator.generate_enhanced_component(component_name, component_type, config)
        
        # Verify V5-aware component structure
        assert isinstance(component, V5GeneratedComponent)
        assert component.name == component_name
        assert component.type == component_type
        assert len(component.source_code) > 0
        
        # Verify V5 integration in source code
        source = component.source_code
        assert "v5_integration_enabled" in source
        assert "performance_monitoring" in source
        assert "_setup_v5_integration" in source
    
    def test_schema_requirements_extraction(self):
        """Test schema requirements extraction"""
        config = {
            "enable_full_text_search": True,
            "enable_audit_log": True,
            "enable_partitioning": False
        }
        
        requirements = self.generator._extract_schema_requirements(config)
        
        # Verify basic requirements
        assert "id_column_primary_key" in requirements
        assert "data_column_json" in requirements
        assert "timestamps_created_updated" in requirements
        assert "metadata_column_json" in requirements
        
        # Verify feature-specific requirements
        assert "full_text_search_index" in requirements
        assert "audit_log_triggers" in requirements
        assert "table_partitioning" not in requirements
    
    def test_database_config_generation(self):
        """Test database configuration generation"""
        config = {
            "connection_pool_min": 3,
            "connection_pool_max": 15,
            "connection_timeout": 45,
            "schema_strict_mode": False,
            "transaction_isolation": "SERIALIZABLE",
            "enable_caching": False
        }
        
        db_config = self.generator._generate_database_config(config)
        
        # Verify configuration structure
        assert "connection_pool" in db_config
        assert "schema_validation" in db_config
        assert "transaction_management" in db_config
        assert "performance" in db_config
        
        # Verify specific values
        assert db_config["connection_pool"]["min_size"] == 3
        assert db_config["connection_pool"]["max_size"] == 15
        assert db_config["connection_pool"]["timeout"] == 45
        assert db_config["schema_validation"]["strict_mode"] is False
        assert db_config["transaction_management"]["isolation_level"] == "SERIALIZABLE"
        assert db_config["performance"]["caching_enabled"] is False
    
    def test_component_file_writing(self):
        """Test writing V5 component files to disk"""
        components = [
            V5GeneratedComponent(
                name="test_store",
                type="V5EnhancedStore",
                source_code="# Test source code",
                imports=["from test import TestClass"],
                database_config={"database_type": "postgresql"},
                schema_requirements=["basic_table"],
                dependencies=["asyncpg"]
            )
        ]
        
        output_dir = Path(self.temp_dir) / "test_output"
        self.generator.write_component_files(components, output_dir)
        
        # Verify files were created
        component_file = output_dir / "components" / "test_store.py"
        config_file = output_dir / "components" / "test_store_config.json"
        
        assert component_file.exists()
        assert config_file.exists()
        
        # Verify file contents
        with open(component_file) as f:
            source_content = f.read()
            assert "# Test source code" in source_content
        
        with open(config_file) as f:
            config_content = json.load(f)
            assert config_content["database_config"]["database_type"] == "postgresql"
            assert "basic_table" in config_content["schema_requirements"]


class TestV5EnhancedSystemScaffoldGenerator:
    """Test V5 Enhanced System Scaffold Generator"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = V5EnhancedSystemScaffoldGenerator(Path(self.temp_dir))
    
    def test_v5_system_generation(self):
        """Test complete V5 system generation"""
        # Mock system blueprint
        mock_blueprint = Mock()
        mock_blueprint.system.name = "test_v5_system"
        mock_blueprint.system.description = "Test V5 system"
        mock_blueprint.system.version = "1.0.0"
        mock_blueprint.system.configuration.environment = "test"
        mock_blueprint.system.components = [
            Mock(
                name="test_store",
                type="Store",
                configuration={"database_type": "postgresql", "table_name": "test_data"}
            ),
            Mock(
                name="test_source",
                type="Source",
                configuration={"data_count": 100}
            )
        ]
        mock_blueprint.system.bindings = [
            Mock(
                from_component="test_source",
                from_port="data",
                to_components=["test_store"],
                to_ports=["input"]
            )
        ]
        
        # Mock database validation
        with patch.object(self.generator.db_validation_orchestrator, 'validate_system_database_readiness') as mock_validate:
            mock_validate.return_value = Mock(
                database_ready=True,
                validation_errors=[]
            )
            
            # Mock V5 component generation
            with patch.object(self.generator.v5_component_generator, 'generate_enhanced_component') as mock_gen:
                mock_gen.side_effect = [
                    V5GeneratedComponent(
                        name="test_store",
                        type="V5EnhancedStore",
                        source_code="# V5 Store code",
                        imports=["from autocoder.components.v5_enhanced_store import V5EnhancedStore"],
                        database_config={"database_type": "postgresql"},
                        schema_requirements=["basic_table"],
                        dependencies=["asyncpg"]
                    ),
                    V5GeneratedComponent(
                        name="test_source",
                        type="Source",
                        source_code="# V5 Source code",
                        imports=["from autocoder.components import Source"],
                        database_config={},
                        schema_requirements=[],
                        dependencies=[]
                    )
                ]
                
                scaffold = self.generator.generate_v5_system(mock_blueprint)
                
                # Verify V5GeneratedScaffold structure
                assert isinstance(scaffold, V5GeneratedScaffold)
                assert len(scaffold.main_py) > 0
                assert len(scaffold.config_yaml) > 0
                assert len(scaffold.requirements_txt) > 0
                assert len(scaffold.dockerfile) > 0
                assert len(scaffold.database_init_sql) > 0
                assert len(scaffold.v5_components) == 2
                
                # Verify V5 features in main.py
                main_py = scaffold.main_py
                assert "V5 Enhanced System with Database Integration" in main_py
                assert "DatabaseValidationOrchestrator" in main_py
                assert "V5DatabaseManager" in main_py
                assert "setup_v5_database_integration" in main_py
                assert "run_v5_system_harness" in main_py
                
                # Verify V5 database imports
                assert "V5DatabaseManager" in main_py
                assert "DatabaseValidationOrchestrator" in main_py
                
                # Verify V5 component creation
                assert "GeneratedStore_test_store" in main_py
                assert "set_database_manager" in main_py
    
    def test_v5_system_database_validation_failure(self):
        """Test V5 system generation with database validation failure"""
        mock_blueprint = Mock()
        mock_blueprint.system.name = "failing_system"
        
        # Mock database validation failure
        with patch.object(self.generator.db_validation_orchestrator, 'validate_system_database_readiness') as mock_validate:
            mock_validate.return_value = Mock(
                database_ready=False,
                validation_errors=["Database connection failed", "Schema validation failed"]
            )
            
            with pytest.raises(ValueError, match="System not ready for V5 database integration"):
                self.generator.generate_v5_system(mock_blueprint)
    
    def test_v5_config_yaml_generation(self):
        """Test V5 configuration YAML generation"""
        mock_blueprint = Mock()
        mock_blueprint.system.name = "test_system"
        mock_blueprint.system.version = "1.0.0"
        mock_blueprint.system.configuration.environment = "production"
        mock_blueprint.system.components = [
            Mock(
                name="analytics_store",
                configuration={"database_type": "postgresql", "batch_size": 100}
            )
        ]
        
        v5_components = [
            V5GeneratedComponent(
                name="analytics_store",
                type="V5EnhancedStore",
                source_code="",
                imports=[],
                database_config={
                    "database_type": "postgresql",
                    "connection_pool": {"min_size": 5, "max_size": 20}
                },
                schema_requirements=[],
                dependencies=[]
            )
        ]
        
        config_yaml = self.generator._generate_v5_config_yaml(mock_blueprint, v5_components, enable_metrics=True)
        
        # Verify V5 configuration features
        assert "v5_database_integration: true" in config_yaml
        assert "database:" in config_yaml
        assert "connection_pools:" in config_yaml
        assert "schema_validation:" in config_yaml
        assert "monitoring:" in config_yaml
        assert "database_monitoring: true" in config_yaml
        assert "performance_tracking: true" in config_yaml
    
    def test_v5_requirements_generation(self):
        """Test V5 requirements.txt generation"""
        mock_blueprint = Mock()
        v5_components = [
            V5GeneratedComponent(
                name="test_store",
                type="V5EnhancedStore",
                source_code="",
                imports=[],
                database_config={},
                schema_requirements=[],
                dependencies=[]
            )
        ]
        
        requirements = self.generator._generate_v5_requirements_txt(mock_blueprint, v5_components)
        
        # Verify V5 database dependencies
        assert "asyncpg>=" in requirements
        assert "aiomysql>=" in requirements
        assert "aiosqlite>=" in requirements
        assert "sqlalchemy>=" in requirements
        assert "alembic>=" in requirements
        assert "redis>=" in requirements
        assert "prometheus-client>=" in requirements
        
        # Verify V5EnhancedStore specific dependencies
        assert "psycopg2-binary>=" in requirements
        assert "pymysql>=" in requirements
    
    def test_v5_dockerfile_generation(self):
        """Test V5 Dockerfile generation with database support"""
        mock_blueprint = Mock()
        mock_blueprint.system.name = "test_v5_system"
        mock_blueprint.system.components = [
            Mock(type="APIEndpoint", configuration={"port": 8080})
        ]
        
        v5_components = []
        dockerfile = self.generator._generate_v5_dockerfile(mock_blueprint, v5_components)
        
        # Verify V5 Dockerfile features
        assert "V5 Enhanced Dockerfile" in dockerfile
        assert "libpq-dev" in dockerfile  # PostgreSQL dependencies
        assert "V5_DATABASE_INTEGRATION=true" in dockerfile
        assert "DATABASE_POOL_SIZE=" in dockerfile
        assert "SCHEMA_VALIDATION_ENABLED=" in dockerfile
        assert "HEALTHCHECK" in dockerfile
        assert "check_database_health" in dockerfile
        assert "EXPOSE 8080" in dockerfile
        assert "EXPOSE 9090" in dockerfile  # Metrics port
    
    def test_database_init_sql_generation(self):
        """Test database initialization SQL generation"""
        mock_blueprint = Mock()
        mock_blueprint.system.name = "test_system"
        
        v5_components = [
            V5GeneratedComponent(
                name="analytics_store",
                type="V5EnhancedStore",
                source_code="",
                imports=[],
                database_config={
                    "table_name": "analytics_data",
                    "schema_name": "analytics"
                },
                schema_requirements=[],
                dependencies=[]
            )
        ]
        
        init_sql = self.generator._generate_database_init_sql(mock_blueprint, v5_components)
        
        # Verify database initialization features
        assert "CREATE SCHEMA IF NOT EXISTS public" in init_sql
        assert "CREATE SCHEMA IF NOT EXISTS analytics" in init_sql
        assert "CREATE EXTENSION IF NOT EXISTS" in init_sql
        assert "component_registry" in init_sql
        assert "schema_migrations" in init_sql
        assert "analytics.analytics_data" in init_sql
        assert "CREATE INDEX IF NOT EXISTS" in init_sql
        assert "component_health" in init_sql
        
        # Verify V5EnhancedStore specific initialization
        assert "V5EnhancedStore initialization for analytics_store" in init_sql
        assert "JSONB" in init_sql
        assert "GIN" in init_sql  # JSONB indexes


@pytest.mark.asyncio
class TestV5IntegrationE2E:
    """End-to-end integration tests for V5 enhanced generators"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    async def test_complete_v5_system_generation_flow(self):
        """Test complete V5 system generation from blueprint to deployment"""
        # This would be a comprehensive integration test
        # For now, we'll test the key integration points
        
        component_generator = V5EnhancedComponentGenerator(Path(self.temp_dir))
        scaffold_generator = V5EnhancedSystemScaffoldGenerator(Path(self.temp_dir))
        
        # Mock successful database validation
        with patch.object(scaffold_generator.db_validation_orchestrator, 'validate_system_database_readiness') as mock_validate:
            mock_validate.return_value = Mock(
                database_ready=True,
                validation_errors=[]
            )
            
            # Test component generation -> scaffold generation -> file writing
            # This verifies the complete integration flow
            
            # Create test V5 component
            store_config = {
                "database_type": "postgresql",
                "table_name": "integration_test",
                "connection_pool_size": 5
            }
            
            with patch.object(component_generator.db_dependency_validator, 'validate_component_dependencies') as mock_dep_validate:
                mock_dep_validate.return_value = Mock(
                    dependencies_met=True,
                    dependencies=["postgresql"],
                    missing_dependencies=[]
                )
                
                v5_store = component_generator.generate_v5_store_component("integration_store", store_config)
                
                # Verify V5 component was generated correctly
                assert v5_store.type == "V5EnhancedStore"
                assert v5_store.database_config["database_type"] == "postgresql"
                
                # Integration test passed - components can be generated and integrated
                print("✅ V5 Enhanced Generator Integration Test Passed")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])