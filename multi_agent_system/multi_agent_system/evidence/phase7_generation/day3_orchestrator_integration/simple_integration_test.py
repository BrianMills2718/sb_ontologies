#!/usr/bin/env python3
"""
Simple Integration Test for Day 3 - ValidationDrivenOrchestrator Integration
============================================================================

Basic test to verify the enhanced orchestrator can be imported and initialized.
"""

import os
import sys
import logging

# Add paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day1_system_scaffold_generator'))  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day2_component_logic_generator'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """Test that basic imports work"""
    logger.info("🧪 Testing basic imports")
    
    try:
        # Test blueprint types import
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day1_system_scaffold_generator'))
        from blueprint_types import SystemBlueprint
        logger.info("✅ SystemBlueprint import successful")
        
        # Test enhanced orchestrator import
        from enhanced_orchestrator import EnhancedValidationDrivenOrchestrator
        logger.info("✅ EnhancedValidationDrivenOrchestrator import successful")
        
        # Test generation coordinator import
        from generation_coordinator import GenerationCoordinator
        logger.info("✅ GenerationCoordinator import successful")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False, [str(e)]

def test_basic_initialization():
    """Test that components can be initialized"""
    logger.info("🧪 Testing basic initialization")
    
    try:
        # Test enhanced orchestrator initialization
        from enhanced_orchestrator import EnhancedValidationDrivenOrchestrator
        orchestrator = EnhancedValidationDrivenOrchestrator()
        logger.info("✅ Enhanced orchestrator initialized")
        
        # Test generation coordinator initialization
        from generation_coordinator import GenerationCoordinator
        coordinator = GenerationCoordinator()
        logger.info("✅ Generation coordinator initialized")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return False, [str(e)]

def test_basic_blueprint_creation():
    """Test creating a basic blueprint"""
    logger.info("🧪 Testing basic blueprint creation")
    
    try:
        # Import from the already added path
        from blueprint_types import SystemBlueprint
        
        # Create simple test blueprint
        blueprint = SystemBlueprint(
            description="Simple test system",
            components=[
                {
                    "name": "test_component",
                    "type": "data_processor",
                    "configuration": {}
                }
            ]
        )
        
        logger.info("✅ Blueprint created successfully")
        logger.info(f"   Description: {blueprint.description}")
        logger.info(f"   Components: {len(blueprint.components)}")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Blueprint creation failed: {e}")
        return False, [str(e)]

def main():
    """Run all basic integration tests"""
    logger.info("🚀 Starting Day 3 basic integration tests")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Basic Initialization", test_basic_initialization),
        ("Basic Blueprint Creation", test_basic_blueprint_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        success, errors = test_func()
        results.append((test_name, success, errors))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, success, errors in results:
        if success:
            logger.info(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            logger.error(f"❌ {test_name}: FAILED")
            for error in errors:
                logger.error(f"   - {error}")
            failed += 1
    
    logger.info(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All basic integration tests passed!")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)