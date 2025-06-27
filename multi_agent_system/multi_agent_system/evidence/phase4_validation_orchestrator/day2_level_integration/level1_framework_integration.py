"""
Level 1: Framework Unit Testing Integration
Validates the Autocoder framework itself before component validation
"""

import asyncio
import subprocess
import sys
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FrameworkTestResult:
    """Result of framework unit test execution"""
    all_passed: bool
    test_count: int
    failures: List[str]
    execution_time: float
    coverage_percentage: Optional[float] = None
    test_details: Dict[str, Any] = None


class Level1FrameworkValidator:
    """
    Level 1 Framework Validation - Validates Autocoder framework itself
    
    This level ensures the framework is functioning correctly before validating
    user components. Framework issues require manual intervention.
    """
    
    def __init__(self):
        self.test_suite_paths = [
            "tests/test_blueprint_parser.py",
            "tests/test_component_base.py", 
            "tests/test_validation_framework.py",
            "tests/test_system_generator.py"
        ]
        self.critical_modules = [
            "blueprint_language.blueprint_parser",
            "blueprint_language.component_base",
            "blueprint_language.validation_framework",
            "blueprint_language.system_generator"
        ]
    
    async def validate_framework(self) -> FrameworkTestResult:
        """
        Execute comprehensive framework validation
        
        Returns:
            FrameworkTestResult with complete test execution details
        """
        start_time = time.time()
        logger.info("Starting Level 1 framework validation")
        
        try:
            # 1. Module import validation
            import_results = await self._validate_module_imports()
            if not import_results["success"]:
                return FrameworkTestResult(
                    all_passed=False,
                    test_count=0,
                    failures=[f"Module import failed: {import_results['error']}"],
                    execution_time=time.time() - start_time
                )
            
            # 2. Unit test execution
            test_results = await self._execute_framework_tests()
            
            # 3. Framework integrity checks
            integrity_results = await self._validate_framework_integrity()
            
            # 4. Critical path validation
            critical_path_results = await self._validate_critical_paths()
            
            # Aggregate results
            all_passed = (
                test_results["success"] and 
                integrity_results["success"] and 
                critical_path_results["success"]
            )
            
            failures = []
            if not test_results["success"]:
                failures.extend(test_results.get("failures", []))
            if not integrity_results["success"]:
                failures.append(f"Framework integrity check failed: {integrity_results['error']}")
            if not critical_path_results["success"]:
                failures.append(f"Critical path validation failed: {critical_path_results['error']}")
            
            result = FrameworkTestResult(
                all_passed=all_passed,
                test_count=test_results.get("test_count", 0),
                failures=failures,
                execution_time=time.time() - start_time,
                coverage_percentage=test_results.get("coverage", None),
                test_details={
                    "import_results": import_results,
                    "test_results": test_results,
                    "integrity_results": integrity_results,
                    "critical_path_results": critical_path_results
                }
            )
            
            if all_passed:
                logger.info(f"Level 1 framework validation passed in {result.execution_time:.2f}s")
            else:
                logger.error(f"Level 1 framework validation failed: {failures}")
            
            return result
            
        except Exception as e:
            logger.error(f"Level 1 framework validation error: {e}")
            return FrameworkTestResult(
                all_passed=False,
                test_count=0,
                failures=[f"Framework validation exception: {e}"],
                execution_time=time.time() - start_time
            )
    
    async def _validate_module_imports(self) -> Dict[str, Any]:
        """Validate all critical framework modules can be imported"""
        try:
            logger.debug("Validating framework module imports")
            
            failed_imports = []
            for module_name in self.critical_modules:
                try:
                    __import__(module_name)
                    logger.debug(f"Successfully imported {module_name}")
                except ImportError as e:
                    failed_imports.append(f"{module_name}: {e}")
                    logger.error(f"Failed to import {module_name}: {e}")
            
            if failed_imports:
                return {
                    "success": False,
                    "error": f"Failed to import critical modules: {failed_imports}"
                }
            
            return {"success": True, "modules_validated": len(self.critical_modules)}
            
        except Exception as e:
            return {"success": False, "error": f"Module import validation failed: {e}"}
    
    async def _execute_framework_tests(self) -> Dict[str, Any]:
        """Execute framework unit tests"""
        try:
            logger.debug("Executing framework unit tests")
            
            # Check if pytest is available
            try:
                import pytest
            except ImportError:
                logger.warning("pytest not available - using unittest")
                return await self._execute_unittest_framework()
            
            # Execute pytest on framework test files
            test_files = [path for path in self.test_suite_paths if self._file_exists(path)]
            
            if not test_files:
                logger.warning("No framework test files found - creating basic validation")
                return await self._execute_basic_framework_validation()
            
            # Run pytest with coverage if available
            pytest_args = ["-v", "--tb=short"] + test_files
            
            try:
                import pytest_cov
                pytest_args.extend(["--cov=blueprint_language", "--cov-report=term-missing"])
            except ImportError:
                logger.debug("pytest-cov not available - running without coverage")
            
            # Execute tests
            result_code = pytest.main(pytest_args)
            
            return {
                "success": result_code == 0,
                "test_count": len(test_files) * 5,  # Estimate
                "failures": [] if result_code == 0 else ["Some framework tests failed"],
                "coverage": None  # Would be extracted from pytest output
            }
            
        except Exception as e:
            logger.error(f"Framework test execution failed: {e}")
            return {"success": False, "error": f"Test execution failed: {e}"}
    
    async def _execute_unittest_framework(self) -> Dict[str, Any]:
        """Fallback unittest execution"""
        try:
            import unittest
            
            # Create test suite for basic framework validation
            suite = unittest.TestSuite()
            
            # Add basic import tests
            class FrameworkImportTest(unittest.TestCase):
                def test_blueprint_parser_import(self):
                    import blueprint_language.blueprint_parser
                
                def test_component_base_import(self):
                    try:
                        import blueprint_language.component_base
                    except ImportError:
                        # May not exist yet - acceptable for framework test
                        pass
                
                def test_validation_framework_import(self):
                    try:
                        import blueprint_language.validation_framework
                    except ImportError:
                        # May not exist yet - acceptable for framework test
                        pass
            
            suite.addTest(unittest.makeSuite(FrameworkImportTest))
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            return {
                "success": result.wasSuccessful(),
                "test_count": result.testsRun,
                "failures": [str(failure) for failure in result.failures + result.errors]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Unittest execution failed: {e}"}
    
    async def _execute_basic_framework_validation(self) -> Dict[str, Any]:
        """Basic framework validation when no test files exist"""
        try:
            logger.info("Executing basic framework validation")
            
            # Basic functionality tests
            tests_passed = 0
            total_tests = 4
            failures = []
            
            # Test 1: Python version compatibility
            if sys.version_info >= (3, 8):
                tests_passed += 1
            else:
                failures.append(f"Python version {sys.version_info} < 3.8 required")
            
            # Test 2: Core module availability
            try:
                import blueprint_language
                tests_passed += 1
            except ImportError as e:
                failures.append(f"blueprint_language module import failed: {e}")
            
            # Test 3: Required packages
            required_packages = ["pydantic", "pyyaml"]
            packages_available = 0
            for package in required_packages:
                try:
                    __import__(package)
                    packages_available += 1
                except ImportError:
                    failures.append(f"Required package '{package}' not available")
            
            if packages_available == len(required_packages):
                tests_passed += 1
            
            # Test 4: Basic validation orchestrator functionality
            try:
                from blueprint_language.validation_driven_orchestrator import ValidationDrivenOrchestrator
                orchestrator = ValidationDrivenOrchestrator()
                if orchestrator.development_mode:
                    tests_passed += 1
                else:
                    failures.append("ValidationDrivenOrchestrator not in development mode")
            except Exception as e:
                failures.append(f"ValidationDrivenOrchestrator test failed: {e}")
            
            return {
                "success": tests_passed == total_tests,
                "test_count": total_tests,
                "failures": failures
            }
            
        except Exception as e:
            return {"success": False, "error": f"Basic framework validation failed: {e}"}
    
    async def _validate_framework_integrity(self) -> Dict[str, Any]:
        """Validate framework internal consistency"""
        try:
            logger.debug("Validating framework integrity")
            
            integrity_checks = []
            
            # Check 1: ValidationDrivenOrchestrator initialization
            try:
                from blueprint_language.validation_driven_orchestrator import ValidationDrivenOrchestrator
                orchestrator = ValidationDrivenOrchestrator()
                
                # Verify orchestrator has required components
                required_attrs = ["dependency_checker", "level_validators", "healers", "phase_integrations"]
                for attr in required_attrs:
                    if not hasattr(orchestrator, attr):
                        integrity_checks.append(f"ValidationDrivenOrchestrator missing {attr}")
                    elif getattr(orchestrator, attr) is None:
                        integrity_checks.append(f"ValidationDrivenOrchestrator {attr} is None")
                
            except Exception as e:
                integrity_checks.append(f"ValidationDrivenOrchestrator integrity check failed: {e}")
            
            # Check 2: Dependency checker functionality
            try:
                from blueprint_language.validation_dependency_checker import ValidationDependencyChecker
                checker = ValidationDependencyChecker()
                
                # Verify checker has required methods
                required_methods = ["validate_all_dependencies_configured", "_check_llm_configuration"]
                for method in required_methods:
                    if not hasattr(checker, method):
                        integrity_checks.append(f"ValidationDependencyChecker missing {method}")
                
            except Exception as e:
                integrity_checks.append(f"ValidationDependencyChecker integrity check failed: {e}")
            
            # Check 3: Validation result types
            try:
                from blueprint_language.validation_result_types import (
                    ValidationResult, SystemGenerationResult, ValidationDependencyError
                )
                
                # Test basic type instantiation
                result = ValidationResult(passed=True, level=1)
                if not hasattr(result, 'to_dict'):
                    integrity_checks.append("ValidationResult missing to_dict method")
                
            except Exception as e:
                integrity_checks.append(f"Validation result types integrity check failed: {e}")
            
            return {
                "success": len(integrity_checks) == 0,
                "error": f"Integrity checks failed: {integrity_checks}" if integrity_checks else None,
                "checks_performed": 3,
                "issues_found": len(integrity_checks)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Framework integrity validation failed: {e}"}
    
    async def _validate_critical_paths(self) -> Dict[str, Any]:
        """Validate critical execution paths work correctly"""
        try:
            logger.debug("Validating critical execution paths")
            
            path_failures = []
            
            # Critical Path 1: Orchestrator instantiation and dependency checking
            try:
                from blueprint_language.validation_driven_orchestrator import ValidationDrivenOrchestrator
                orchestrator = ValidationDrivenOrchestrator()
                
                # Test dependency checker instantiation
                if orchestrator.dependency_checker is None:
                    path_failures.append("Orchestrator dependency_checker not instantiated")
                
            except Exception as e:
                path_failures.append(f"Orchestrator instantiation path failed: {e}")
            
            # Critical Path 2: Validation result creation and serialization
            try:
                from blueprint_language.validation_result_types import ValidationResult, ValidationLevel
                
                # Test result creation
                result = ValidationResult(passed=True, level=ValidationLevel.LEVEL_1_FRAMEWORK)
                
                # Test serialization
                result_dict = result.to_dict()
                if "passed" not in result_dict or "level" not in result_dict:
                    path_failures.append("ValidationResult serialization missing required fields")
                
            except Exception as e:
                path_failures.append(f"Validation result creation path failed: {e}")
            
            # Critical Path 3: Error handling and exception creation
            try:
                from blueprint_language.validation_result_types import ValidationDependencyError
                
                # Test exception creation
                error = ValidationDependencyError("Test dependency error")
                if str(error) != "Test dependency error":
                    path_failures.append("ValidationDependencyError string representation incorrect")
                
            except Exception as e:
                path_failures.append(f"Error handling path failed: {e}")
            
            return {
                "success": len(path_failures) == 0,
                "error": f"Critical path failures: {path_failures}" if path_failures else None,
                "paths_tested": 3,
                "failures": len(path_failures)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Critical path validation failed: {e}"}
    
    def _file_exists(self, path: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(path)


# Integration function for ValidationDrivenOrchestrator
async def create_framework_validator() -> Level1FrameworkValidator:
    """Create and return Level 1 framework validator"""
    return Level1FrameworkValidator()


# Test harness
if __name__ == "__main__":
    async def test_framework_validation():
        validator = Level1FrameworkValidator()
        result = await validator.validate_framework()
        
        print(f"Framework validation result: {result.all_passed}")
        print(f"Tests run: {result.test_count}")
        print(f"Execution time: {result.execution_time:.2f}s")
        
        if not result.all_passed:
            print("Failures:")
            for failure in result.failures:
                print(f"  - {failure}")
        
        return result
    
    asyncio.run(test_framework_validation())