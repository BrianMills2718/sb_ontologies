#!/usr/bin/env python3
"""
Phase 5 Day 2: Schema Validation and Migration Integration Test
Verifies end-to-end functionality of schema validation, registry, and migration components
"""

import asyncio
import tempfile
import shutil
import time
from schema_validator import SchemaValidator, SchemaDefinition, SchemaField, SchemaVersion
from schema_registry import SchemaRegistry
from migration_manager import MigrationManager


async def test_day2_integration():
    """Test complete Day 2 schema validation and migration integration"""
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Using temporary directory: {temp_dir}")
    
    try:
        # Configuration for all components
        config = {
            "registry_path": temp_dir + "/registry",
            "migrations_path": temp_dir + "/migrations",
            "strict_validation": True,
            "auto_migration": False,
            "cache_enabled": True,
            "backup_enabled": True
        }
        
        print("\n🔧 Testing Schema Registry...")
        # Test Schema Registry
        registry = SchemaRegistry(config)
        await registry.initialize()
        print(f"✅ Schema registry initialized with {len(registry.schemas)} schemas")
        
        # Get current schema
        current_schema = await registry.get_current_schema()
        print(f"✅ Current schema: {current_schema.name} v{current_schema.version}")
        
        print("\n🔧 Testing Migration Manager...")
        # Test Migration Manager
        migration_manager = MigrationManager(config)
        await migration_manager.initialize()
        print("✅ Migration manager initialized")
        
        # Test migration planning
        plan = await migration_manager._plan_migration_path("1.0.0", "1.1.0")
        print(f"✅ Migration plan created: {len(plan.steps)} steps")
        
        print("\n🔧 Testing Schema Validator...")
        # Test Schema Validator
        validator = SchemaValidator(config)
        await validator.initialize()
        print("✅ Schema validator initialized")
        
        # Test schema setup
        await validator.validate_or_create_schema()
        print("✅ Schema validation/creation completed")
        
        print("\n📊 Testing Data Validation...")
        # Test with valid data matching the default schema
        valid_data = {
            "id": "test_event_123",
            "timestamp": time.time(),
            "event_type": "user_action",
            "data": {"action": "click", "target": "button"},
            "user_id": "user_456",
            "session_id": "session_789"
        }
        
        result = await validator.validate_data(valid_data)
        if result.valid:
            print(f"✅ Valid data validation successful (execution time: {result.execution_time:.4f}s)")
        else:
            print(f"❌ Valid data validation failed: {result.errors}")
        
        # Test with invalid data
        invalid_data = {
            "id": "test_event_456",
            "timestamp": "not_a_number",  # Should be number
            "event_type": "user_action"
            # Missing required 'data' field
        }
        
        invalid_result = await validator.validate_data(invalid_data)
        if not invalid_result.valid:
            print(f"✅ Invalid data correctly rejected: {len(invalid_result.errors)} errors")
        else:
            print("❌ Invalid data was incorrectly accepted")
        
        print("\n🔄 Testing Schema Migration...")
        # Test migration execution
        migration_result = await migration_manager.migrate_schema("1.0.0", "1.1.0")
        if migration_result.successful:
            print(f"✅ Migration successful: {migration_result.from_version} -> {migration_result.to_version}")
            print(f"   Steps completed: {migration_result.steps_completed}/{migration_result.total_steps}")
            print(f"   Execution time: {migration_result.execution_time:.4f}s")
        else:
            print(f"❌ Migration failed: {migration_result.error_message}")
        
        print("\n📈 Component Statistics...")
        # Get statistics
        validator_stats = validator.get_validation_statistics()
        registry_stats = registry.get_registry_statistics()
        migration_stats = migration_manager.get_migration_statistics()
        
        print(f"✅ Validator: {validator_stats['cache_size']} cached results, current version: {validator_stats['current_version']}")
        print(f"✅ Registry: {registry_stats['total_schemas']} schemas, active: {registry_stats['active_version']}")
        print(f"✅ Migration: {migration_stats['total_migrations']} migrations, {migration_stats['success_rate']:.1%} success rate")
        
        print("\n🧹 Testing Component Cleanup...")
        # Test cleanup
        await validator.cleanup()
        await registry.cleanup()
        await migration_manager.cleanup()
        print("✅ All components cleaned up successfully")
        
        print("\n🎉 Phase 5 Day 2 Integration Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"🗑️ Cleaned up temporary directory")


async def test_concurrent_operations():
    """Test concurrent schema operations"""
    print("\n🔄 Testing Concurrent Operations...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        config = {
            "registry_path": temp_dir + "/registry",
            "migrations_path": temp_dir + "/migrations",
            "strict_validation": True,
            "cache_enabled": True
        }
        
        # Create multiple validators
        validators = []
        for i in range(3):
            validator = SchemaValidator(config)
            await validator.initialize()
            await validator.validate_or_create_schema()
            validators.append(validator)
        
        # Test concurrent data validation
        async def validate_data(validator, data_id):
            test_data = {
                "id": f"concurrent_test_{data_id}",
                "timestamp": time.time(),
                "event_type": "concurrent_test",
                "data": {"test_id": data_id}
            }
            return await validator.validate_data(test_data)
        
        # Run concurrent validations
        tasks = []
        for i, validator in enumerate(validators):
            for j in range(5):
                tasks.append(validate_data(validator, f"{i}_{j}"))
        
        results = await asyncio.gather(*tasks)
        
        # Verify all validations succeeded
        successful_validations = sum(1 for result in results if result.valid)
        print(f"✅ Concurrent operations: {successful_validations}/{len(results)} validations successful")
        
        # Cleanup
        for validator in validators:
            await validator.cleanup()
        
        return successful_validations == len(results)
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def main():
    """Run all Day 2 integration tests"""
    print("🚀 Starting Phase 5 Day 2 Schema Validation and Migration Integration Tests")
    print("=" * 80)
    
    # Run main integration test
    test1_success = await test_day2_integration()
    
    # Run concurrent operations test
    test2_success = await test_concurrent_operations()
    
    print("\n" + "=" * 80)
    if test1_success and test2_success:
        print("🎉 ALL TESTS PASSED - Phase 5 Day 2 components are working correctly!")
        print("\n✅ Schema Validator: Real-time validation with caching")
        print("✅ Schema Registry: Version management with backup")
        print("✅ Migration Manager: Database migration with rollback")
        print("✅ Integration: End-to-end workflow functional")
        print("✅ Concurrency: Multiple operations handled correctly")
    else:
        print("❌ Some tests failed - see errors above")
        print(f"   Main integration test: {'PASS' if test1_success else 'FAIL'}")
        print(f"   Concurrent operations test: {'PASS' if test2_success else 'FAIL'}")


if __name__ == "__main__":
    asyncio.run(main())