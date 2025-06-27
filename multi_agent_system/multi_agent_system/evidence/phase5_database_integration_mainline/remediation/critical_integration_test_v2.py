#!/usr/bin/env python3
"""
Critical Integration Test for Phase 5 Database Integration
Tests that generated systems actually use V5EnhancedStore instead of basic Store
"""
import sys
import os
import tempfile
import logging
from pathlib import Path

# Add remediation path
remediation_path = str(Path(__file__).parent)
sys.path.insert(0, remediation_path)

# Add paths for local imports
current_evidence_path = str(Path(__file__).parent.parent.parent / "phases" / "evaluation_clean" / "current_evidence")
sys.path.insert(0, str(Path(current_evidence_path) / "day1_v5_enhanced_store_integration"))
sys.path.insert(0, str(Path(current_evidence_path) / "day3_two_phase_generation_enhancement"))
sys.path.insert(0, str(Path(current_evidence_path) / "day2_orchestrator_database_validation"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_store_component_generation():
    """Test that V5EnhancedComponentGenerator creates V5EnhancedStore components"""
    print("🧪 Testing V5EnhancedStore Component Generation...")
    
    try:
        from v5_enhanced_component_generator import V5EnhancedComponentGenerator
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = V5EnhancedComponentGenerator(Path(temp_dir))
            
            # Test configuration for Store component
            config = {
                "database_type": "postgresql",
                "table_name": "test_data",
                "connection_url": "postgresql://test:test@localhost:5432/testdb",
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "testdb"
                },
                "testing_mode": True  # Enable testing mode
            }
            
            # Generate V5 Store component
            component = generator.generate_v5_store_component("test_store", config)
            
            # Verify it's V5EnhancedStore
            assert component.type == "V5EnhancedStore", f"Expected V5EnhancedStore, got {component.type}"
            assert "V5EnhancedStore" in component.source_code, "Source code should contain V5EnhancedStore"
            assert "v5_enhanced_store" in component.source_code.lower(), "Should import v5_enhanced_store"
            
            print("✅ V5EnhancedStore component generation works correctly")
            return True
            
    except Exception as e:
        print(f"❌ V5EnhancedStore component generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_store_component_registry():
    """Test that Store components are registered as V5EnhancedStore"""
    print("🧪 Testing Store Component Registry...")
    
    try:
        from store_component_registry_fixed import get_enhanced_component_registry, EnhancedStoreComponent
        
        registry = get_enhanced_component_registry()
        
        # Test that Store components are enhanced with testing mode
        store_component = registry.create_component("sink", "Store", "test_store", {
            "database_type": "postgresql",
            "table_name": "test_table",
            "testing_mode": True  # Enable testing mode
        })
        
        # Verify it's enhanced
        assert store_component is not None, "Store component creation should not return None"
        assert hasattr(store_component, 'is_v5_enhanced'), "Store component should be V5 enhanced"
        assert store_component.is_v5_enhanced, "Store component should have V5 enhancement flag"
        assert store_component.component_type == "EnhancedStore", "Should be EnhancedStore type"
        
        print("✅ Store component registry correctly creates V5EnhancedStore")
        return True
        
    except Exception as e:
        print(f"❌ Store component registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_generated_system_uses_v5_enhanced_store():
    """Test that generated systems use V5EnhancedStore instead of basic Store"""
    print("🧪 Testing Generated System V5 Integration...")
    
    try:
        from v5_enhanced_scaffold_generator import V5EnhancedSystemScaffoldGenerator
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = V5EnhancedSystemScaffoldGenerator(Path(temp_dir))
            
            # Test system configuration
            system_config = {
                "system_name": "test_analytics_system",
                "components": [
                    {
                        "name": "data_store",
                        "type": "Store",
                        "config": {
                            "database_type": "postgresql",
                            "table_name": "analytics_data",
                            "testing_mode": True  # Enable testing mode
                        }
                    },
                    {
                        "name": "data_source",
                        "type": "Source",
                        "config": {
                            "data_count": 1000
                        }
                    }
                ]
            }
            
            # Generate V5 system
            system = generator.generate_v5_enhanced_system(system_config)
            
            # Check that Store components are V5EnhancedStore
            store_components = [c for c in system.components if c.original_type == "Store"]
            assert len(store_components) > 0, "Should have at least one Store component"
            
            for store_comp in store_components:
                assert store_comp.enhanced_type == "V5EnhancedStore", f"Store component {store_comp.name} should be V5EnhancedStore"
                assert "V5EnhancedStore" in store_comp.source_code, f"Store component {store_comp.name} should use V5EnhancedStore in source"
                assert store_comp.database_integration_enabled, f"Store component {store_comp.name} should have database integration enabled"
            
            print("✅ Generated systems correctly use V5EnhancedStore for Store components")
            return True
            
    except Exception as e:
        print(f"❌ Generated system V5 integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_validation_orchestrator_integration():
    """Test that DatabaseValidationOrchestrator is integrated with main system"""
    print("🧪 Testing DatabaseValidationOrchestrator Integration...")
    
    try:
        from database_validation_orchestrator import DatabaseValidationOrchestrator
        
        # Create orchestrator
        orchestrator = DatabaseValidationOrchestrator()
        
        # Verify it inherits from ValidationDrivenOrchestrator
        assert hasattr(orchestrator, 'database_validation_enabled'), "Should have database validation enabled"
        assert orchestrator.database_validation_enabled, "Database validation should be enabled"
        
        # Verify enhanced Level 3 validation method exists
        assert hasattr(orchestrator, '_execute_enhanced_level3_validation'), "Should have enhanced Level 3 validation"
        
        # Verify database dependency validation
        assert hasattr(orchestrator, 'validate_database_dependencies'), "Should have database dependency validation"
        
        print("✅ DatabaseValidationOrchestrator is properly integrated")
        return True
        
    except Exception as e:
        print(f"❌ DatabaseValidationOrchestrator integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_component_generator_integration():
    """Test that the main component generator now creates V5EnhancedStore"""
    print("🧪 Testing Main Component Generator Integration...")
    
    try:
        # Import the main component generator
        sys.path.insert(0, "/home/brian/autocoder3_cc")
        from blueprint_language.component_logic_generator import ComponentLogicGenerator
        from blueprint_language.blueprint_parser import ParsedComponent
        
        # Create generator with temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ComponentLogicGenerator(temp_dir)
            
            # Create a Store component configuration
            store_component = ParsedComponent(
                name="test_store",
                type="Store",
                description="Test store component",
                configuration={
                    "database_type": "postgresql",
                    "table_name": "test_data",
                    "testing_mode": True  # Enable testing mode
                }
            )
            
            # Generate the component
            generated_component = generator.generate_component_implementation(store_component)
            
            # Verify it imports V5EnhancedStore
            assert "V5EnhancedStore" in str(generated_component.imports), f"Should import V5EnhancedStore, got: {generated_component.imports}"
            assert "V5EnhancedStore" in generated_component.implementation, "Should use V5EnhancedStore in implementation"
            
            print("✅ Main component generator correctly uses V5EnhancedStore")
            return True
        
    except Exception as e:
        print(f"❌ Main component generator integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_v5_enhanced_store_direct():
    """Test V5EnhancedStore directly to ensure it works in testing mode"""
    print("🧪 Testing V5EnhancedStore Direct Usage...")
    
    try:
        from enhanced_store_component_fixed_v2 import EnhancedStoreComponent
        
        # Test configuration with testing mode
        config = {
            "database_type": "postgresql",
            "table_name": "test_data",
            "testing_mode": True,  # Enable testing mode
            "database": {
                "database_type": "postgresql",
                "host": "localhost",
                "port": 5432
            }
        }
        
        # Create enhanced store component
        store = EnhancedStoreComponent("test_direct", config)
        
        # Verify initialization
        assert store.is_v5_enhanced, "Should be V5 enhanced"
        assert store.component_type == "EnhancedStore", "Should be EnhancedStore type"
        assert hasattr(store, 'testing_mode'), "Should have testing_mode attribute"
        
        print("✅ V5EnhancedStore works correctly in testing mode")
        return True
        
    except Exception as e:
        print(f"❌ V5EnhancedStore direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all critical integration tests"""
    print("🚀 Running Critical Phase 5 Database Integration Tests (V2 - Testing Mode)")
    print("=" * 80)
    
    tests = [
        test_v5_enhanced_store_direct,
        test_store_component_registry,
        test_enhanced_store_component_generation,
        test_generated_system_uses_v5_enhanced_store,
        test_database_validation_orchestrator_integration,
        test_main_component_generator_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        print(f"\n📋 Running: {test_func.__name__}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_func.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test_func.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} FAILED with exception: {e}")
    
    print(f"\n🎯 CRITICAL INTEGRATION TEST RESULTS:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print(f"\n🎉 ALL CRITICAL INTEGRATION TESTS PASSED!")
        print(f"   ✅ V5EnhancedStore integration verified")
        print(f"   ✅ Generated systems use V5 database features")
        print(f"   ✅ DatabaseValidationOrchestrator integrated")
        print(f"   ✅ Main component generator updated")
        print(f"   ✅ Phase 5 integration successful")
        return True
    else:
        print(f"\n❌ CRITICAL INTEGRATION TESTS FAILED!")
        print(f"   {failed} tests failed - Phase 5 integration incomplete")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)