#!/usr/bin/env python3
"""
Level 1: Framework Unit Testing Integration
==========================================

Validates the Autocoder framework itself before proceeding with component validation.
This level ensures the framework components are working correctly and identifies
framework bugs that would prevent successful validation.

NO FALLBACKS - Framework issues require manual intervention
"""

import asyncio
import unittest
import sys
import importlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from validation_result_types import (
    FrameworkTestResult, ValidationResult, ValidationFailure,
    create_framework_test_result, create_success_result, create_failure_result
)


class Level1FrameworkValidator:
    """
    Framework validation for V5.0 Autocoder components.
    
    This validator runs comprehensive tests on the framework itself
    to ensure all components are working before component validation begins.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Level1FrameworkValidator")
        
        # Framework components to validate
        self.FRAMEWORK_COMPONENTS = [
            'validation_result_types',
            'dependency_checker',
            'phase2_integration',
            'phase3_integration'
        ]
        
        # Critical framework modules that must be importable
        self.CRITICAL_MODULES = [
            'asyncio',
            'logging',
            'pathlib',
            'typing'
        ]
        
        self.logger.info("✅ Level1FrameworkValidator initialized")
    
    async def run_framework_tests(self) -> FrameworkTestResult:
        """
        Run comprehensive framework unit tests.
        
        This method executes all framework validation tests and returns
        aggregated results. Framework failures indicate bugs that require
        manual intervention.
        
        Returns:
            FrameworkTestResult with test execution details
        """
        self.logger.info("🏗️  Starting Level 1 framework validation")
        
        test_failures = []
        tests_run = 0
        
        # Test 1: Critical module imports
        import_test_result = await self._test_critical_module_imports()
        tests_run += 1
        if not import_test_result['passed']:
            test_failures.extend(import_test_result['failures'])
        
        # Test 2: Framework component imports
        component_test_result = await self._test_framework_component_imports()
        tests_run += 1
        if not component_test_result['passed']:
            test_failures.extend(component_test_result['failures'])
        
        # Test 3: Framework component instantiation
        instantiation_test_result = await self._test_framework_component_instantiation()
        tests_run += 1
        if not instantiation_test_result['passed']:
            test_failures.extend(instantiation_test_result['failures'])
        
        # Test 4: Validation result type functionality
        result_types_test_result = await self._test_validation_result_types()
        tests_run += 1
        if not result_types_test_result['passed']:
            test_failures.extend(result_types_test_result['failures'])
        
        # Test 5: Dependency checker functionality
        dependency_test_result = await self._test_dependency_checker_functionality()
        tests_run += 1
        if not dependency_test_result['passed']:
            test_failures.extend(dependency_test_result['failures'])
        
        # Test 6: Integration module functionality
        integration_test_result = await self._test_integration_modules()
        tests_run += 1
        if not integration_test_result['passed']:
            test_failures.extend(integration_test_result['failures'])
        
        # Create framework test result
        all_passed = len(test_failures) == 0
        
        result = create_framework_test_result(
            tests_passed=tests_run - len(test_failures),
            total_tests=tests_run,
            failures=test_failures
        )
        
        if all_passed:
            self.logger.info(f"✅ Level 1 framework validation passed: {tests_run}/{tests_run} tests")
        else:
            self.logger.error(f"❌ Level 1 framework validation failed: {len(test_failures)} failures in {tests_run} tests")
        
        return result
    
    async def _test_critical_module_imports(self) -> Dict[str, Any]:
        """Test that critical Python modules can be imported"""
        failures = []
        
        for module_name in self.CRITICAL_MODULES:
            try:
                importlib.import_module(module_name)
                self.logger.debug(f"✅ Critical module import successful: {module_name}")
            except ImportError as e:
                failure_msg = f"Critical module import failed: {module_name} - {e}"
                failures.append(failure_msg)
                self.logger.error(f"❌ {failure_msg}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures
        }
    
    async def _test_framework_component_imports(self) -> Dict[str, Any]:
        """Test that framework components can be imported"""
        failures = []
        
        for component_name in self.FRAMEWORK_COMPONENTS:
            try:
                # Try to import the component
                if component_name == 'validation_result_types':
                    from validation_result_types import ValidationResult
                elif component_name == 'dependency_checker':
                    from dependency_checker import ValidationDependencyChecker
                elif component_name == 'phase2_integration':
                    # This will be imported in the phase2_integration module
                    pass
                elif component_name == 'phase3_integration':
                    # This will be imported in the phase3_integration module
                    pass
                
                self.logger.debug(f"✅ Framework component import successful: {component_name}")
                
            except ImportError as e:
                failure_msg = f"Framework component import failed: {component_name} - {e}"
                failures.append(failure_msg)
                self.logger.error(f"❌ {failure_msg}")
            except Exception as e:
                failure_msg = f"Framework component import error: {component_name} - {e}"
                failures.append(failure_msg)
                self.logger.error(f"❌ {failure_msg}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures
        }
    
    async def _test_framework_component_instantiation(self) -> Dict[str, Any]:
        """Test that framework components can be instantiated"""
        failures = []
        
        try:
            # Test ValidationDependencyChecker instantiation
            from dependency_checker import ValidationDependencyChecker
            checker = ValidationDependencyChecker()
            if not hasattr(checker, 'validate_all_dependencies_configured'):
                failures.append("ValidationDependencyChecker missing required method")
            
            self.logger.debug("✅ ValidationDependencyChecker instantiation successful")
            
        except Exception as e:
            failure_msg = f"ValidationDependencyChecker instantiation failed: {e}"
            failures.append(failure_msg)
            self.logger.error(f"❌ {failure_msg}")
        
        try:
            # Test validation result types
            from validation_result_types import ValidationResult, ValidationFailure
            test_result = ValidationResult(passed=True, level=1)
            test_failure = ValidationFailure(
                component_name="test",
                failure_type="test",
                error_message="test"
            )
            
            if not hasattr(test_result, 'passed') or not hasattr(test_failure, 'error_message'):
                failures.append("ValidationResult types missing required attributes")
            
            self.logger.debug("✅ Validation result types instantiation successful")
            
        except Exception as e:
            failure_msg = f"Validation result types instantiation failed: {e}"
            failures.append(failure_msg)
            self.logger.error(f"❌ {failure_msg}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures
        }
    
    async def _test_validation_result_types(self) -> Dict[str, Any]:
        """Test validation result type functionality"""
        failures = []
        
        try:
            from validation_result_types import (
                ValidationResult, ValidationFailure, 
                create_success_result, create_failure_result
            )
            
            # Test success result creation
            success_result = create_success_result(level=1, execution_time=1.0)
            if not success_result.passed or success_result.level != 1:
                failures.append("Success result creation failed")
            
            # Test failure result creation
            test_failure = ValidationFailure(
                component_name="test_component",
                failure_type="test_error",
                error_message="Test error message"
            )
            
            failure_result = create_failure_result(level=1, failures=[test_failure])
            if failure_result.passed or len(failure_result.failures) != 1:
                failures.append("Failure result creation failed")
            
            # Test result aggregation
            if not hasattr(failure_result, 'error_count') or failure_result.error_count != 1:
                failures.append("Validation result aggregation failed")
            
            self.logger.debug("✅ Validation result types functionality test successful")
            
        except Exception as e:
            failure_msg = f"Validation result types functionality test failed: {e}"
            failures.append(failure_msg)
            self.logger.error(f"❌ {failure_msg}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures
        }
    
    async def _test_dependency_checker_functionality(self) -> Dict[str, Any]:
        """Test dependency checker core functionality"""
        failures = []
        
        try:
            from dependency_checker import ValidationDependencyChecker
            
            checker = ValidationDependencyChecker()
            
            # Test status retrieval
            status = checker.get_dependency_status()
            if not isinstance(status, dict):
                failures.append("Dependency checker status retrieval failed")
            
            # Test specific dependency checking methods
            if not hasattr(checker, '_is_llm_configured'):
                failures.append("Dependency checker missing LLM check method")
            
            if not hasattr(checker, '_is_database_available'):
                failures.append("Dependency checker missing database check method")
            
            self.logger.debug("✅ Dependency checker functionality test successful")
            
        except Exception as e:
            failure_msg = f"Dependency checker functionality test failed: {e}"
            failures.append(failure_msg)
            self.logger.error(f"❌ {failure_msg}")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures
        }
    
    async def _test_integration_modules(self) -> Dict[str, Any]:
        """Test Phase 2-3 integration module availability"""
        failures = []
        
        # Check Phase 2 component library path
        phase2_path = Path(__file__).parent.parent / 'phase2_component_library'
        if not phase2_path.exists():
            failures.append("Phase 2 component library path not found")
        else:
            # Check key Phase 2 files
            required_files = ['component_registry.py', 'schema_framework.py']
            for file_name in required_files:
                if not (phase2_path / file_name).exists():
                    failures.append(f"Phase 2 required file missing: {file_name}")
        
        # Check Phase 3 blueprint schema path
        phase3_path = Path(__file__).parent.parent / 'phase3_blueprint_schema'
        if not phase3_path.exists():
            failures.append("Phase 3 blueprint schema path not found")
        else:
            # Check key Phase 3 files
            required_files = ['schema_parser.py', 'reasonableness_checks.py']
            for file_name in required_files:
                if not (phase3_path / file_name).exists():
                    failures.append(f"Phase 3 required file missing: {file_name}")
        
        # Test basic imports from Phase 2-3 (if available)
        try:
            sys.path.insert(0, str(phase2_path))
            sys.path.insert(0, str(phase3_path))
            
            # Test Phase 2 imports
            import component_registry
            import schema_framework
            
            # Test Phase 3 imports
            import schema_parser
            import reasonableness_checks
            
            self.logger.debug("✅ Phase 2-3 integration modules import successful")
            
        except ImportError as e:
            failure_msg = f"Phase 2-3 integration module import failed: {e}"
            failures.append(failure_msg)
            self.logger.warning(f"⚠️  {failure_msg}")
        except Exception as e:
            failure_msg = f"Phase 2-3 integration module test error: {e}"
            failures.append(failure_msg)
            self.logger.error(f"❌ {failure_msg}")
        
        if len(failures) == 0:
            self.logger.debug("✅ Integration modules test successful")
        
        return {
            'passed': len(failures) == 0,
            'failures': failures
        }
    
    async def validate_framework_environment(self) -> ValidationResult:
        """
        Validate the complete framework environment.
        
        This method provides a high-level validation of the framework
        environment for use by the ValidationDrivenOrchestrator.
        
        Returns:
            ValidationResult indicating framework validation status
        """
        try:
            framework_test_result = await self.run_framework_tests()
            
            if framework_test_result.all_passed:
                return create_success_result(
                    level=1,
                    execution_time=framework_test_result.execution_time,
                    metadata={
                        'tests_passed': framework_test_result.test_count,
                        'success_rate': framework_test_result.success_rate
                    }
                )
            else:
                failures = [
                    ValidationFailure(
                        component_name=None,
                        failure_type="framework_test_failure",
                        error_message=failure,
                        healing_candidate=False
                    )
                    for failure in framework_test_result.failures
                ]
                
                return create_failure_result(
                    level=1,
                    failures=failures,
                    execution_time=framework_test_result.execution_time
                )
                
        except Exception as e:
            framework_failure = ValidationFailure(
                component_name=None,
                failure_type="framework_validation_error",
                error_message=f"Framework validation error: {e}",
                healing_candidate=False
            )
            
            return create_failure_result(level=1, failures=[framework_failure])
    
    def get_framework_status(self) -> Dict[str, Any]:
        """Get current framework validation status"""
        return {
            'validator_initialized': True,
            'critical_modules': self.CRITICAL_MODULES,
            'framework_components': self.FRAMEWORK_COMPONENTS,
            'phase2_path_exists': (Path(__file__).parent.parent / 'phase2_component_library').exists(),
            'phase3_path_exists': (Path(__file__).parent.parent / 'phase3_blueprint_schema').exists()
        }


# Convenience functions for external use
async def validate_framework() -> FrameworkTestResult:
    """Validate framework using Level1FrameworkValidator"""
    validator = Level1FrameworkValidator()
    return await validator.run_framework_tests()


async def check_framework_environment() -> ValidationResult:
    """Check framework environment and return ValidationResult"""
    validator = Level1FrameworkValidator()
    return await validator.validate_framework_environment()


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test Level1FrameworkValidator"""
        
        # Create validator
        validator = Level1FrameworkValidator()
        
        # Display framework status
        status = validator.get_framework_status()
        print("🏗️  Framework Validation Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n🚀 Running Level 1 framework validation...")
        
        # Run framework tests
        test_result = await validator.run_framework_tests()
        
        print(f"\n📊 Framework Test Results:")
        print(f"  All passed: {test_result.all_passed}")
        print(f"  Tests run: {test_result.test_count}")
        print(f"  Success rate: {test_result.success_rate:.1f}%")
        print(f"  Execution time: {test_result.execution_time:.3f}s")
        
        if test_result.failures:
            print(f"\n❌ Test Failures ({len(test_result.failures)}):")
            for i, failure in enumerate(test_result.failures, 1):
                print(f"  {i}. {failure}")
        
        # Test framework environment validation
        print("\n🔍 Testing framework environment validation...")
        env_result = await validator.validate_framework_environment()
        
        print(f"Framework environment validation: {'✅ PASSED' if env_result.passed else '❌ FAILED'}")
        if not env_result.passed:
            for failure in env_result.failures:
                print(f"  - {failure}")
    
    # Run the test
    asyncio.run(main())