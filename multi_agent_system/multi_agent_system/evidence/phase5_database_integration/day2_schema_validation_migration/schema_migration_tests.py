"""
V5.0 Schema Validation and Migration Tests
Comprehensive test suite for schema validation, registry, and migration management
"""

import pytest
import asyncio
import time
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
import os

# Import components under test
import sys
sys.path.append('/home/brian/autocoder3_cc/evidence/phase5_database_integration/day2_schema_validation_migration')

from schema_validator import (
    SchemaValidator, SchemaValidationError, SchemaDefinition, 
    SchemaField, SchemaVersion, ValidationResult
)
from schema_registry import (
    SchemaRegistry, SchemaRegistryError, SchemaNotFoundError,
    SchemaVersionConflictError, SchemaMetadata
)
from migration_manager import (
    MigrationManager, MigrationError, MigrationStatus,
    MigrationStep, MigrationPlan, MigrationResult
)


class TestSchemaValidator:
    """Test suite for SchemaValidator"""
    
    @pytest.fixture
    def validator_config(self):
        """Configuration for schema validator testing"""
        return {
            "strict_validation": True,
            "auto_migration": False,
            "cache_enabled": True,
            "schema_version": "1.0.0"
        }
    
    @pytest.fixture
    def schema_validator(self, validator_config):
        """Create SchemaValidator instance for testing"""
        return SchemaValidator(validator_config)
    
    @pytest.fixture
    def sample_schema(self):
        """Sample schema definition for testing"""
        return SchemaDefinition(
            version=SchemaVersion("1.0.0"),
            name="test_schema",
            fields=[
                SchemaField("id", "string", required=True),
                SchemaField("name", "string", required=True, 
                           constraints={"min_length": 1, "max_length": 100}),
                SchemaField("age", "integer", required=False,
                           constraints={"min_value": 0, "max_value": 150}),
                SchemaField("email", "string", required=False,
                           constraints={"pattern": r"^[^@]+@[^@]+\.[^@]+$"}),
                SchemaField("metadata", "object", required=False)
            ]
        )
    
    def test_schema_validator_initialization(self, schema_validator, validator_config):
        """Test schema validator initialization"""
        assert schema_validator.config == validator_config
        assert schema_validator.strict_validation is True
        assert schema_validator.cache_enabled is True
        assert schema_validator.current_version is None
        assert schema_validator.active_schema is None
    
    @pytest.mark.asyncio
    async def test_schema_validator_setup(self, schema_validator):
        """Test schema validator initialization"""
        await schema_validator.initialize()
        
        assert schema_validator.schema_registry is not None
        assert schema_validator.migration_manager is not None
    
    @pytest.mark.asyncio
    async def test_validate_or_create_schema(self, schema_validator):
        """Test schema validation or creation"""
        await schema_validator.initialize()
        
        result = await schema_validator.validate_or_create_schema()
        assert result is True
        assert schema_validator.active_schema is not None
        assert schema_validator.current_version is not None
    
    @pytest.mark.asyncio
    async def test_data_validation_success(self, schema_validator):
        """Test successful data validation"""
        await schema_validator.initialize()
        await schema_validator.validate_or_create_schema()
        
        valid_data = {
            "id": "test123",
            "name": "Test User",
            "age": 25,
            "email": "test@example.com",
            "metadata": {"source": "test"}
        }
        
        result = await schema_validator.validate_data(valid_data)
        
        assert result.valid is True
        assert len(result.errors) == 0
        assert result.validated_data is not None
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_data_validation_missing_required_field(self, schema_validator):
        """Test data validation with missing required field"""
        await schema_validator.initialize()
        await schema_validator.validate_or_create_schema()
        
        invalid_data = {
            "id": "test123"
            # Missing required 'name' field
        }
        
        result = await schema_validator.validate_data(invalid_data)
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("name" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_data_validation_type_error(self, schema_validator):
        """Test data validation with type error"""
        await schema_validator.initialize()
        await schema_validator.validate_or_create_schema()
        
        invalid_data = {
            "id": "test123",
            "name": "Test User",
            "age": "not_an_integer"  # Should be integer
        }
        
        result = await schema_validator.validate_data(invalid_data)
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("age" in error for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_data_validation_constraint_violation(self, schema_validator):
        """Test data validation with constraint violation"""
        await schema_validator.initialize()
        await schema_validator.validate_or_create_schema()
        
        invalid_data = {
            "id": "test123",
            "name": "Test User",
            "age": 200,  # Violates max_value constraint
            "email": "invalid_email"  # Violates pattern constraint
        }
        
        result = await schema_validator.validate_data(invalid_data)
        
        assert result.valid is False
        assert len(result.errors) >= 2  # Age and email violations
    
    @pytest.mark.asyncio
    async def test_validation_caching(self, schema_validator):
        """Test validation result caching"""
        await schema_validator.initialize()
        await schema_validator.validate_or_create_schema()
        
        test_data = {
            "id": "test123",
            "name": "Test User"
        }
        
        # First validation
        result1 = await schema_validator.validate_data(test_data)
        
        # Second validation should use cache
        result2 = await schema_validator.validate_data(test_data)
        
        assert result1.valid == result2.valid
        assert len(schema_validator.validation_cache) > 0
    
    def test_validation_statistics(self, schema_validator):
        """Test validation statistics"""
        stats = schema_validator.get_validation_statistics()
        
        assert "current_version" in stats
        assert "active_schema" in stats
        assert "cache_size" in stats
        assert "cache_enabled" in stats
        assert "strict_validation" in stats


class TestSchemaRegistry:
    """Test suite for SchemaRegistry"""
    
    @pytest.fixture
    def temp_registry_path(self):
        """Create temporary registry path for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def registry_config(self, temp_registry_path):
        """Configuration for schema registry testing"""
        return {
            "registry_path": temp_registry_path + "/test_registry",
            "auto_backup": True,
            "max_versions": 5,
            "compression": False
        }
    
    @pytest.fixture
    def schema_registry(self, registry_config):
        """Create SchemaRegistry instance for testing"""
        return SchemaRegistry(registry_config)
    
    @pytest.fixture
    def sample_schema_definition(self):
        """Sample schema definition for registry testing"""
        return SchemaDefinition(
            version=SchemaVersion("1.0.0"),
            name="test_registry_schema",
            fields=[
                SchemaField("id", "string", required=True),
                SchemaField("data", "object", required=True)
            ]
        )
    
    def test_schema_registry_initialization(self, schema_registry, registry_config):
        """Test schema registry initialization"""
        assert schema_registry.config == registry_config
        assert schema_registry.registry_loaded is False
        assert len(schema_registry.schemas) == 0
        assert len(schema_registry.metadata) == 0
    
    @pytest.mark.asyncio
    async def test_schema_registry_setup(self, schema_registry):
        """Test schema registry setup"""
        await schema_registry.initialize()
        
        assert schema_registry.registry_loaded is True
        assert len(schema_registry.schemas) >= 1  # Default schema should be created
        assert schema_registry.active_version is not None
    
    @pytest.mark.asyncio
    async def test_register_schema(self, schema_registry, sample_schema_definition):
        """Test schema registration"""
        await schema_registry.initialize()
        
        version = "2.0.0"
        metadata = {
            "description": "Test schema registration",
            "tags": ["test", "registration"]
        }
        
        result = await schema_registry.register_schema(
            sample_schema_definition, version, metadata
        )
        
        assert result is True
        assert version in schema_registry.schemas
        assert version in schema_registry.metadata
        assert schema_registry.metadata[version].description == metadata["description"]
    
    @pytest.mark.asyncio
    async def test_get_schema(self, schema_registry, sample_schema_definition):
        """Test schema retrieval"""
        await schema_registry.initialize()
        
        version = "2.0.0"
        await schema_registry.register_schema(sample_schema_definition, version)
        
        retrieved_schema = await schema_registry.get_schema(version)
        
        assert retrieved_schema is not None
        assert retrieved_schema.name == sample_schema_definition.name
        assert str(retrieved_schema.version) == version
    
    @pytest.mark.asyncio
    async def test_get_schema_not_found(self, schema_registry):
        """Test schema retrieval with non-existent version"""
        await schema_registry.initialize()
        
        with pytest.raises(SchemaNotFoundError):
            await schema_registry.get_schema("999.0.0")
    
    @pytest.mark.asyncio
    async def test_get_current_schema(self, schema_registry):
        """Test current active schema retrieval"""
        await schema_registry.initialize()
        
        current_schema = await schema_registry.get_current_schema()
        
        assert current_schema is not None
        assert schema_registry.active_version is not None
    
    @pytest.mark.asyncio
    async def test_get_latest_schema(self, schema_registry, sample_schema_definition):
        """Test latest schema retrieval"""
        await schema_registry.initialize()
        
        # Register additional schema
        await schema_registry.register_schema(sample_schema_definition, "2.0.0")
        
        latest_schema = await schema_registry.get_latest_schema()
        
        assert latest_schema is not None
        assert str(latest_schema.version) == "2.0.0"
    
    @pytest.mark.asyncio
    async def test_set_active_version(self, schema_registry, sample_schema_definition):
        """Test setting active schema version"""
        await schema_registry.initialize()
        
        version = "2.0.0"
        await schema_registry.register_schema(sample_schema_definition, version)
        
        result = await schema_registry.set_active_version(version)
        
        assert result is True
        assert schema_registry.active_version == version
        assert schema_registry.metadata[version].is_active is True
    
    @pytest.mark.asyncio
    async def test_list_versions(self, schema_registry, sample_schema_definition):
        """Test listing schema versions"""
        await schema_registry.initialize()
        
        # Register additional schema
        await schema_registry.register_schema(sample_schema_definition, "2.0.0")
        
        versions = await schema_registry.list_versions()
        
        assert len(versions) >= 2  # Default + registered
        assert all("version" in v for v in versions)
        assert all("name" in v for v in versions)
        assert all("created_at" in v for v in versions)
    
    @pytest.mark.asyncio
    async def test_schema_version_conflict(self, schema_registry, sample_schema_definition):
        """Test schema version conflict handling"""
        await schema_registry.initialize()
        
        version = "2.0.0"
        await schema_registry.register_schema(sample_schema_definition, version)
        
        # Try to register same version again
        with pytest.raises(SchemaVersionConflictError):
            await schema_registry.register_schema(sample_schema_definition, version)
    
    @pytest.mark.asyncio
    async def test_backup_registry(self, schema_registry):
        """Test registry backup functionality"""
        await schema_registry.initialize()
        
        backup_path = await schema_registry.backup_registry()
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
    
    def test_registry_statistics(self, schema_registry):
        """Test registry statistics"""
        stats = schema_registry.get_registry_statistics()
        
        assert "total_schemas" in stats
        assert "active_version" in stats
        assert "registry_path" in stats
        assert "registry_loaded" in stats


class TestMigrationManager:
    """Test suite for MigrationManager"""
    
    @pytest.fixture
    def temp_migrations_path(self):
        """Create temporary migrations path for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def migration_config(self, temp_migrations_path):
        """Configuration for migration manager testing"""
        return {
            "migrations_path": temp_migrations_path + "/migrations",
            "backup_enabled": True,
            "dry_run_enabled": True,
            "migration_timeout": 60,
            "max_rollback_steps": 50
        }
    
    @pytest.fixture
    def migration_manager(self, migration_config):
        """Create MigrationManager instance for testing"""
        return MigrationManager(migration_config)
    
    def test_migration_manager_initialization(self, migration_manager, migration_config):
        """Test migration manager initialization"""
        assert migration_manager.config == migration_config
        assert migration_manager.backup_enabled is True
        assert migration_manager.dry_run_enabled is True
        assert len(migration_manager.migration_history) == 0
        assert migration_manager.active_migration is None
    
    @pytest.mark.asyncio
    async def test_migration_manager_setup(self, migration_manager):
        """Test migration manager setup"""
        await migration_manager.initialize()
        
        assert os.path.exists(migration_manager.migrations_path)
    
    @pytest.mark.asyncio
    async def test_migration_plan_creation(self, migration_manager):
        """Test migration plan creation"""
        await migration_manager.initialize()
        
        plan = await migration_manager._plan_migration_path("1.0.0", "1.1.0")
        
        assert plan is not None
        assert plan.from_version == "1.0.0"
        assert plan.to_version == "1.1.0"
        assert isinstance(plan.steps, list)
        assert plan.total_estimated_duration >= 0
    
    @pytest.mark.asyncio
    async def test_migration_execution_success(self, migration_manager):
        """Test successful migration execution"""
        await migration_manager.initialize()
        
        result = await migration_manager.migrate_schema("1.0.0", "1.1.0")
        
        assert result.successful is True
        assert result.from_version == "1.0.0"
        assert result.to_version == "1.1.0"
        assert result.execution_time > 0
        assert result.steps_completed >= 0
        assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_migration_same_version(self, migration_manager):
        """Test migration with same source and target version"""
        await migration_manager.initialize()
        
        result = await migration_manager.migrate_schema("1.0.0", "1.0.0")
        
        assert result.successful is True
        assert result.steps_completed == 0  # No steps needed
    
    @pytest.mark.asyncio
    async def test_concurrent_migration_prevention(self, migration_manager):
        """Test prevention of concurrent migrations"""
        await migration_manager.initialize()
        
        # Start first migration (will be simulated)
        migration_manager.active_migration = "test_migration"
        
        # Try to start second migration
        with pytest.raises(MigrationError):
            await migration_manager.migrate_schema("1.0.0", "1.1.0")
        
        # Clean up
        migration_manager.active_migration = None
    
    @pytest.mark.asyncio
    async def test_migration_history_tracking(self, migration_manager):
        """Test migration history tracking"""
        await migration_manager.initialize()
        
        # Execute migration
        await migration_manager.migrate_schema("1.0.0", "1.1.0")
        
        # Check history
        assert len(migration_manager.migration_history) > 0
        
        # Verify history record
        history_record = migration_manager.migration_history[-1]
        assert history_record.from_version == "1.0.0"
        assert history_record.to_version == "1.1.0"
        assert history_record.status == MigrationStatus.SUCCESS
    
    def test_migration_statistics(self, migration_manager):
        """Test migration statistics"""
        stats = migration_manager.get_migration_statistics()
        
        assert "total_migrations" in stats
        assert "successful_migrations" in stats
        assert "failed_migrations" in stats
        assert "success_rate" in stats
        assert "active_migration" in stats
        assert "rollback_scripts_available" in stats
    
    @pytest.mark.asyncio
    async def test_migration_step_creation(self, migration_manager):
        """Test migration step creation"""
        await migration_manager.initialize()
        
        from schema_validator import SchemaVersion
        
        steps = await migration_manager._generate_forward_migration_steps(
            SchemaVersion("1.0.0"), SchemaVersion("1.1.0")
        )
        
        assert isinstance(steps, list)
        
        for step in steps:
            assert isinstance(step, MigrationStep)
            assert step.step_id is not None
            assert step.description is not None
            assert step.forward_sql is not None
            assert step.rollback_sql is not None


class TestSchemaIntegration:
    """Integration tests for schema validation, registry, and migration"""
    
    @pytest.fixture
    def temp_integration_path(self):
        """Create temporary path for integration testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def integration_config(self, temp_integration_path):
        """Configuration for integration testing"""
        return {
            "registry_path": temp_integration_path + "/registry",
            "migrations_path": temp_integration_path + "/migrations",
            "strict_validation": True,
            "auto_migration": True,
            "cache_enabled": True,
            "backup_enabled": True
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_schema_workflow(self, integration_config):
        """Test complete end-to-end schema workflow"""
        # Initialize components
        validator = SchemaValidator(integration_config)
        registry = SchemaRegistry(integration_config)
        migration_manager = MigrationManager(integration_config)
        
        try:
            # Initialize all components
            await validator.initialize()
            await registry.initialize()
            await migration_manager.initialize()
            
            # Setup schema
            await validator.validate_or_create_schema()
            
            # Test data validation
            test_data = {
                "id": "test123",
                "timestamp": time.time(),
                "event_type": "test_event",
                "data": {"test": "value"}
            }
            
            validation_result = await validator.validate_data(test_data)
            assert validation_result.valid is True
            
            # Register new schema version
            new_schema = await registry.get_default_schema()
            new_schema.version = SchemaVersion("1.1.0")
            
            await registry.register_schema(new_schema, "1.1.0")
            
            # Test migration
            migration_result = await migration_manager.migrate_schema("1.0.0", "1.1.0")
            assert migration_result.successful is True
            
            # Verify migration in registry
            await registry.set_active_version("1.1.0")
            current_schema = await registry.get_current_schema()
            assert str(current_schema.version) == "1.1.0"
            
            print("✅ End-to-end schema workflow completed successfully")
            
        finally:
            # Cleanup
            await validator.cleanup()
            await registry.cleanup()
            await migration_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_schema_validation_with_migration(self, integration_config):
        """Test schema validation with automatic migration"""
        validator = SchemaValidator(integration_config)
        
        try:
            await validator.initialize()
            
            # Setup initial schema
            await validator.validate_or_create_schema()
            
            # Test validation works
            test_data = {"id": "test", "timestamp": time.time(), "event_type": "test", "data": {}}
            result = await validator.validate_data(test_data)
            assert result.valid is True
            
            # Get validation statistics
            stats = validator.get_validation_statistics()
            assert stats["current_version"] is not None
            
            print("✅ Schema validation with migration integration successful")
            
        finally:
            await validator.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_schema_operations(self, integration_config):
        """Test concurrent schema operations"""
        validators = [SchemaValidator(integration_config) for _ in range(3)]
        
        try:
            # Initialize all validators
            for validator in validators:
                await validator.initialize()
                await validator.validate_or_create_schema()
            
            # Test concurrent validations
            async def validate_data(validator, data_id):
                test_data = {
                    "id": f"test_{data_id}",
                    "timestamp": time.time(),
                    "event_type": "concurrent_test",
                    "data": {"data_id": data_id}
                }
                return await validator.validate_data(test_data)
            
            # Run concurrent validations
            tasks = []
            for i, validator in enumerate(validators):
                for j in range(5):
                    tasks.append(validate_data(validator, f"{i}_{j}"))
            
            results = await asyncio.gather(*tasks)
            
            # All validations should succeed
            assert all(result.valid for result in results)
            
            print(f"✅ Concurrent schema operations completed: {len(results)} validations")
            
        finally:
            for validator in validators:
                await validator.cleanup()


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v", "-s"])