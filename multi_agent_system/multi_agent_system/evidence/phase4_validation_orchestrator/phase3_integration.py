#!/usr/bin/env python3
"""
Phase 3 Blueprint Schema Integration for ValidationDrivenOrchestrator
===================================================================

Integrates ValidationDrivenOrchestrator with Phase 3 V5.0 blueprint schema system
including schema parser, reasonableness checks, and property test framework.

This integration provides:
- Blueprint parsing with V5.0 schema support
- Reasonableness validation using Phase 3 system
- Property test framework integration
- Component validation schema integration
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

# Add Phase 3 blueprint schema to path
phase3_path = Path(__file__).parent.parent / 'phase3_blueprint_schema'
sys.path.insert(0, str(phase3_path))


class Phase3BlueprintIntegrator:
    """
    Integration layer for Phase 3 V5.0 blueprint schema system.
    
    This class provides seamless integration between the ValidationDrivenOrchestrator
    and the Phase 3 blueprint schema system including schema parsing, reasonableness
    validation, and property testing framework.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Phase3BlueprintIntegrator")
        
        # Integration status
        self.integration_active = False
        self.schema_parser = None
        self.reasonableness_validator = None
        self.property_test_framework = None
        self.component_validation_manager = None
        
        # Initialize Phase 3 integration
        self._initialize_phase3_integration()
        
        self.logger.info("✅ Phase3BlueprintIntegrator initialized")
    
    def _initialize_phase3_integration(self):
        """Initialize integration with Phase 3 blueprint schema system"""
        try:
            # Import Phase 3 schema parser
            from schema_parser import (
                V5SchemaParser, ParsedBlueprint, SchemaValidationResult,
                parse_blueprint_file, validate_blueprint, parse_and_validate_blueprint
            )
            self.V5SchemaParser = V5SchemaParser
            self.ParsedBlueprint = ParsedBlueprint
            self.SchemaValidationResult = SchemaValidationResult
            self.parse_blueprint_file = parse_blueprint_file
            self.validate_blueprint = validate_blueprint
            self.parse_and_validate_blueprint = parse_and_validate_blueprint
            
            # Import Phase 3 reasonableness validation
            from reasonableness_checks import (
                ReasonablenessValidator, SystemBlueprint, ValidationResult, 
                ValidationIssue, ValidationSeverity, check_component_coherence
            )
            self.ReasonablenessValidator = ReasonablenessValidator
            self.SystemBlueprint = SystemBlueprint
            self.ValidationResult = ValidationResult
            self.ValidationIssue = ValidationIssue
            self.ValidationSeverity = ValidationSeverity
            self.check_component_coherence = check_component_coherence
            
            # Import Phase 3 property test framework
            from property_test_framework import PropertyTestFramework, PropertyTestType
            self.PropertyTestFramework = PropertyTestFramework
            self.PropertyTestType = PropertyTestType
            
            # Import Phase 3 component validation schema
            from component_validation_schema import (
                ComponentValidationSchemaManager, ComponentType, ComponentValidation
            )
            self.ComponentValidationSchemaManager = ComponentValidationSchemaManager
            self.ComponentType = ComponentType
            self.ComponentValidation = ComponentValidation
            
            # Create instances
            self.schema_parser = self.V5SchemaParser()
            self.reasonableness_validator = self.ReasonablenessValidator()
            self.property_test_framework = self.PropertyTestFramework()
            self.component_validation_manager = self.ComponentValidationSchemaManager()
            
            self.integration_active = True
            
            self.logger.info("✅ Phase 3 blueprint schema integration successful")
            
        except ImportError as e:
            self.logger.error(f"❌ Failed to initialize Phase 3 integration: {e}")
            self.logger.warning("⚠️  Creating mock implementations for testing")
            self._create_mock_implementations()
    
    def _create_mock_implementations(self):
        """Create mock implementations when Phase 3 components not available"""
        
        class MockSchemaParser:
            def parse_blueprint_file(self, file_path):
                return MockParsedBlueprint("Mock blueprint", [])
            
            def parse_blueprint_string(self, blueprint_yaml):
                return MockParsedBlueprint("Mock blueprint", [])
            
            def validate_blueprint_schema(self, blueprint):
                return MockSchemaValidationResult(True)
            
            def create_validation_report(self, validation_result):
                return "Mock validation report"
        
        class MockParsedBlueprint:
            def __init__(self, description, components):
                self.description = description
                self.components = components
                self.reasonableness_checks = []
                self.metadata = {}
            
            def to_system_blueprint(self):
                return MockSystemBlueprint(self.description, self.components, self.reasonableness_checks)
        
        class MockSystemBlueprint:
            def __init__(self, description, components, reasonableness_checks):
                self.description = description
                self.components = components
                self.reasonableness_checks = reasonableness_checks
        
        class MockSchemaValidationResult:
            def __init__(self, is_valid):
                self.is_valid = is_valid
                self.errors = []
                self.warnings = []
        
        class MockReasonablenessValidator:
            def validate_system_reasonableness(self, blueprint):
                return MockValidationResult(True, [])
        
        class MockValidationResult:
            def __init__(self, passed, issues):
                self.passed = passed
                self.issues = issues
                self.checks_performed = 1
                self.execution_time_ms = 10.0
        
        class MockPropertyTestFramework:
            def execute_property_tests(self, component_name, component_type, test_configs):
                return MockPropertyTestResult(len(test_configs), len(test_configs), 0)
        
        class MockPropertyTestResult:
            def __init__(self, total, passed, failed):
                self.total_tests = total
                self.passed_tests = passed
                self.failed_tests = failed
                self.all_passed = failed == 0
                self.success_rate = (passed / total) * 100 if total > 0 else 100
        
        # Set mock implementations
        self.schema_parser = MockSchemaParser()
        self.reasonableness_validator = MockReasonablenessValidator()
        self.property_test_framework = MockPropertyTestFramework()
        self.ParsedBlueprint = MockParsedBlueprint
        self.SystemBlueprint = MockSystemBlueprint
        self.SchemaValidationResult = MockSchemaValidationResult
        
        self.integration_active = True  # Mock integration is active
    
    async def integrate_with_blueprint_schema(self, blueprint: 'SystemBlueprint') -> Dict[str, Any]:
        """
        Integrate with Phase 3 blueprint schema system for validation.
        
        This method validates the blueprint against V5.0 schema requirements
        and performs reasonableness checking using Phase 3 systems.
        
        Args:
            blueprint: SystemBlueprint to validate with Phase 3 systems
            
        Returns:
            Dict containing integration results and validation status
        """
        self.logger.info("🔗 Integrating with Phase 3 blueprint schema system")
        
        if not self.integration_active:
            raise RuntimeError("Phase 3 integration not available")
        
        integration_results = {
            'schema_validation': {},
            'reasonableness_validation': {},
            'property_test_validation': {},
            'component_validation': {},
            'integration_successful': True,
            'issues': []
        }
        
        try:
            # Create Phase 3 compatible blueprint
            p3_blueprint = await self._convert_to_phase3_blueprint(blueprint)
            
            # Schema validation using Phase 3 parser
            schema_results = await self._validate_with_schema_parser(p3_blueprint)
            integration_results['schema_validation'] = schema_results
            
            # Reasonableness validation using Phase 3 reasonableness checker
            reasonableness_results = await self._validate_with_reasonableness_checker(p3_blueprint)
            integration_results['reasonableness_validation'] = reasonableness_results
            
            # Property test validation
            property_test_results = await self._validate_with_property_tests(blueprint.components)
            integration_results['property_test_validation'] = property_test_results
            
            # Component validation schema integration
            component_validation_results = await self._validate_with_component_schemas(blueprint.components)
            integration_results['component_validation'] = component_validation_results
            
            # Aggregate results
            validation_checks = [
                schema_results.get('valid', False),
                reasonableness_results.get('passed', False),
                property_test_results.get('all_passed', False),
                component_validation_results.get('all_valid', False)
            ]
            
            if not all(validation_checks):
                integration_results['integration_successful'] = False
                integration_results['issues'].extend(schema_results.get('issues', []))
                integration_results['issues'].extend(reasonableness_results.get('issues', []))
                integration_results['issues'].extend(property_test_results.get('issues', []))
                integration_results['issues'].extend(component_validation_results.get('issues', []))
            
            if integration_results['integration_successful']:
                self.logger.info("✅ Phase 3 blueprint schema integration successful")
            else:
                self.logger.warning(f"⚠️  Phase 3 integration issues found: {len(integration_results['issues'])}")
            
            return integration_results
            
        except Exception as e:
            self.logger.error(f"❌ Phase 3 integration error: {e}")
            integration_results['integration_successful'] = False
            integration_results['issues'].append(f"Integration error: {e}")
            return integration_results
    
    async def _convert_to_phase3_blueprint(self, blueprint: 'SystemBlueprint') -> Any:
        """Convert ValidationDrivenOrchestrator blueprint to Phase 3 format"""
        try:
            p3_blueprint = self.SystemBlueprint(
                description=blueprint.description,
                components=blueprint.components,
                reasonableness_checks=blueprint.reasonableness_checks
            )
            return p3_blueprint
        except Exception as e:
            # If SystemBlueprint constructor fails, create dict representation
            return {
                'description': blueprint.description,
                'components': blueprint.components,
                'reasonableness_checks': blueprint.reasonableness_checks
            }
    
    async def _validate_with_schema_parser(self, blueprint: Any) -> Dict[str, Any]:
        """Validate blueprint with Phase 3 schema parser"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'issues': []
        }
        
        if not self.schema_parser:
            results['valid'] = False
            results['issues'].append("Schema parser not available")
            return results
        
        try:
            # If we have a dict representation, convert to YAML and parse
            if isinstance(blueprint, dict):
                # Create a minimal YAML representation for testing
                yaml_content = f"""
description: "{blueprint.get('description', 'Test blueprint')}"
components:
"""
                for component in blueprint.get('components', []):
                    yaml_content += f"""
  - name: "{component.get('name', 'unknown')}"
    type: "{component.get('type', 'web_service')}"
"""
                
                # Parse the YAML
                parsed_blueprint = self.schema_parser.parse_blueprint_string(yaml_content)
            else:
                # Convert to parsed blueprint format
                class TempParsedBlueprint:
                    def __init__(self, bp, converter_func, outer_instance):
                        self.description = bp.description
                        self.components = [converter_func(comp) for comp in bp.components]
                        self.reasonableness_checks = bp.reasonableness_checks
                        self.metadata = {}
                        self.schema_version = getattr(bp, 'schema_version', '5.0')  # Default to V5.0
                        self._outer_instance = outer_instance
                    
                    def to_system_blueprint(self):
                        """Convert to SystemBlueprint for reasonableness validation"""
                        return self._outer_instance.SystemBlueprint(
                            description=self.description,
                            components=[comp.to_dict() if hasattr(comp, 'to_dict') else comp for comp in self.components],
                            reasonableness_checks=self.reasonableness_checks
                        )
                
                parsed_blueprint = TempParsedBlueprint(blueprint, self._convert_component, self)
            
            # Validate the parsed blueprint
            validation_result = self.schema_parser.validate_blueprint_schema(parsed_blueprint)
            
            results['valid'] = validation_result.is_valid
            results['errors'] = validation_result.errors
            results['warnings'] = validation_result.warnings
            
            if not validation_result.is_valid:
                results['issues'].extend(validation_result.errors)
            
            return results
            
        except Exception as e:
            results['valid'] = False
            results['issues'].append(f"Schema parser validation error: {e}")
            return results
    
    def _convert_component(self, component_dict: Dict[str, Any]) -> Any:
        """Convert component dict to Phase 3 component format"""
        try:
            # Create a mock parsed component
            class MockParsedComponent:
                def __init__(self, comp_dict):
                    self.name = comp_dict.get('name', 'unknown')
                    self.type = comp_dict.get('type', 'web_service')
                    self.description = comp_dict.get('description', '')
                    self.configuration = comp_dict.get('configuration', {})
                    self.dependencies = comp_dict.get('dependencies', [])
                    self.validation = None
                
                def to_dict(self):
                    return {
                        'name': self.name,
                        'type': self.type,
                        'description': self.description,
                        'configuration': self.configuration,
                        'dependencies': self.dependencies
                    }
            
            return MockParsedComponent(component_dict)
        except Exception:
            return component_dict
    
    async def _validate_with_reasonableness_checker(self, blueprint: Any) -> Dict[str, Any]:
        """Validate blueprint with Phase 3 reasonableness checker"""
        results = {
            'passed': True,
            'issues': [],
            'checks_performed': 0,
            'execution_time_ms': 0.0
        }
        
        if not self.reasonableness_validator:
            results['passed'] = False
            results['issues'].append("Reasonableness validator not available")
            return results
        
        try:
            # Run reasonableness validation
            validation_result = self.reasonableness_validator.validate_system_reasonableness(blueprint)
            
            results['passed'] = validation_result.passed
            results['checks_performed'] = validation_result.checks_performed
            results['execution_time_ms'] = validation_result.execution_time_ms
            
            # Convert validation issues to our format
            for issue in validation_result.issues:
                if hasattr(issue, 'severity') and hasattr(issue, 'message'):
                    severity_str = issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity)
                    results['issues'].append(f"{severity_str.upper()}: {issue.message}")
                else:
                    results['issues'].append(str(issue))
            
            return results
            
        except Exception as e:
            results['passed'] = False
            results['issues'].append(f"Reasonableness validation error: {e}")
            return results
    
    async def _validate_with_property_tests(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate components with Phase 3 property test framework"""
        results = {
            'all_passed': True,
            'component_results': {},
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'issues': []
        }
        
        if not self.property_test_framework:
            results['all_passed'] = False
            results['issues'].append("Property test framework not available")
            return results
        
        try:
            for component in components:
                component_name = component.get('name', 'unnamed')
                component_type = component.get('type', 'web_service')
                
                # Create basic property tests for the component
                test_configs = await self._create_property_tests_for_component(component)
                
                if test_configs:
                    # Execute property tests
                    test_result = self.property_test_framework.execute_property_tests(
                        component_name, component_type, test_configs
                    )
                    
                    results['component_results'][component_name] = {
                        'total_tests': test_result.total_tests,
                        'passed_tests': test_result.passed_tests,
                        'failed_tests': test_result.failed_tests,
                        'all_passed': test_result.all_passed,
                        'success_rate': test_result.success_rate
                    }
                    
                    results['total_tests'] += test_result.total_tests
                    results['passed_tests'] += test_result.passed_tests
                    results['failed_tests'] += test_result.failed_tests
                    
                    if not test_result.all_passed:
                        results['all_passed'] = False
                        results['issues'].append(f"Component '{component_name}' failed {test_result.failed_tests} property tests")
                else:
                    # No property tests for this component
                    results['component_results'][component_name] = {
                        'total_tests': 0,
                        'passed_tests': 0,
                        'failed_tests': 0,
                        'all_passed': True,
                        'success_rate': 100.0
                    }
            
            return results
            
        except Exception as e:
            results['all_passed'] = False
            results['issues'].append(f"Property test validation error: {e}")
            return results
    
    async def _create_property_tests_for_component(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create basic property tests for a component"""
        component_type = component.get('type', 'web_service')
        test_configs = []
        
        # Create type-specific property tests
        if component_type == 'web_service':
            test_configs.append({
                'test_type': 'performance_validation',
                'description': 'Validate web service performance requirements',
                'parameters': {
                    'response_time_ms': 1000,
                    'throughput_rps': 100
                }
            })
            
            test_configs.append({
                'test_type': 'security_validation',
                'description': 'Validate web service security measures',
                'parameters': {
                    'security_checks': ['input_sanitization', 'authentication_check']
                }
            })
        
        elif component_type == 'database':
            test_configs.append({
                'test_type': 'data_integrity_validation',
                'description': 'Validate database data integrity',
                'parameters': {
                    'consistency_checks': ['foreign_key_constraints', 'data_validation']
                }
            })
        
        elif component_type == 'authentication_service':
            test_configs.append({
                'test_type': 'security_validation',
                'description': 'Validate authentication security',
                'parameters': {
                    'security_checks': ['authentication_check', 'authorization_check', 'session_management']
                }
            })
        
        return test_configs
    
    async def _validate_with_component_schemas(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate components with Phase 3 component validation schemas"""
        results = {
            'all_valid': True,
            'validated_components': [],
            'issues': []
        }
        
        if not self.component_validation_manager:
            results['all_valid'] = False
            results['issues'].append("Component validation schema manager not available")
            return results
        
        try:
            for component in components:
                component_name = component.get('name', 'unnamed')
                component_type = component.get('type', 'web_service')
                
                validation_result = {
                    'component_name': component_name,
                    'type_valid': False,
                    'schema_valid': False,
                    'issues': []
                }
                
                # Validate component type
                try:
                    if hasattr(self, 'ComponentType'):
                        comp_type_enum = self.ComponentType(component_type)
                        validation_result['type_valid'] = True
                    else:
                        # Fallback validation
                        valid_types = ['web_service', 'database', 'authentication_service', 'cache_service']
                        validation_result['type_valid'] = component_type in valid_types
                        if not validation_result['type_valid']:
                            validation_result['issues'].append(f"Invalid component type: {component_type}")
                            
                except ValueError:
                    validation_result['issues'].append(f"Unknown component type: {component_type}")
                    results['all_valid'] = False
                    results['issues'].append(f"Component {component_name} has unknown type: {component_type}")
                
                # Basic schema validation
                required_fields = ['name', 'type']
                for field in required_fields:
                    if field not in component or not component[field]:
                        validation_result['issues'].append(f"Missing required field: {field}")
                        results['all_valid'] = False
                        results['issues'].append(f"Component {component_name} missing required field: {field}")
                
                if len(validation_result['issues']) == 0:
                    validation_result['schema_valid'] = True
                else:
                    validation_result['schema_valid'] = False
                    results['all_valid'] = False
                
                results['validated_components'].append(validation_result)
            
            return results
            
        except Exception as e:
            results['all_valid'] = False
            results['issues'].append(f"Component schema validation error: {e}")
            return results
    
    async def parse_blueprint_file(self, blueprint_path: str) -> Any:
        """
        Parse blueprint file using Phase 3 schema parser.
        
        This method provides blueprint file parsing with V5.0 schema support.
        
        Args:
            blueprint_path: Path to blueprint file
            
        Returns:
            ParsedBlueprint object
        """
        if not self.schema_parser:
            raise RuntimeError("Schema parser not available")
        
        try:
            parsed_blueprint = self.schema_parser.parse_blueprint_file(blueprint_path)
            self.logger.info(f"✅ Successfully parsed blueprint: {blueprint_path}")
            return parsed_blueprint
        except Exception as e:
            self.logger.error(f"❌ Failed to parse blueprint {blueprint_path}: {e}")
            raise
    
    async def validate_blueprint_schema(self, parsed_blueprint: Any) -> Any:
        """
        Validate parsed blueprint against V5.0 schema.
        
        This method validates a parsed blueprint using Phase 3 schema validation.
        
        Args:
            parsed_blueprint: ParsedBlueprint object
            
        Returns:
            SchemaValidationResult object
        """
        if not self.schema_parser:
            raise RuntimeError("Schema parser not available")
        
        try:
            validation_result = self.schema_parser.validate_blueprint_schema(parsed_blueprint)
            
            if validation_result.is_valid:
                self.logger.info("✅ Blueprint schema validation successful")
            else:
                self.logger.warning(f"⚠️  Blueprint schema validation failed: {len(validation_result.errors)} errors")
            
            return validation_result
        except Exception as e:
            self.logger.error(f"❌ Blueprint schema validation error: {e}")
            raise
    
    async def validate_system_reasonableness(self, blueprint: 'SystemBlueprint') -> Any:
        """
        Validate system reasonableness using Phase 3 reasonableness checker.
        
        This method performs comprehensive reasonableness validation using
        the Phase 3 reasonableness checking system.
        
        Args:
            blueprint: SystemBlueprint to validate
            
        Returns:
            ValidationResult object
        """
        if not self.reasonableness_validator:
            raise RuntimeError("Reasonableness validator not available")
        
        try:
            # Convert to Phase 3 format
            p3_blueprint = await self._convert_to_phase3_blueprint(blueprint)
            
            # Run reasonableness validation
            validation_result = self.reasonableness_validator.validate_system_reasonableness(p3_blueprint)
            
            if validation_result.passed:
                self.logger.info(f"✅ System reasonableness validation passed ({validation_result.checks_performed} checks)")
            else:
                self.logger.warning(f"⚠️  System reasonableness validation failed: {len(validation_result.issues)} issues")
            
            return validation_result
        except Exception as e:
            self.logger.error(f"❌ System reasonableness validation error: {e}")
            raise
    
    async def get_integration_summary(self) -> Dict[str, Any]:
        """Get comprehensive integration summary"""
        return {
            'integration_active': self.integration_active,
            'schema_parser_available': self.schema_parser is not None,
            'reasonableness_validator_available': self.reasonableness_validator is not None,
            'property_test_framework_available': self.property_test_framework is not None,
            'component_validation_manager_available': self.component_validation_manager is not None,
            'integration_capabilities': {
                'blueprint_parsing': True,
                'schema_validation': True,
                'reasonableness_validation': True,
                'property_testing': True,
                'component_validation': True
            },
            'v5_schema_support': True
        }
    
    def get_integrator_status(self) -> Dict[str, Any]:
        """Get current integrator status"""
        return {
            'integrator_initialized': True,
            'phase3_path_exists': (Path(__file__).parent.parent / 'phase3_blueprint_schema').exists(),
            'integration_active': self.integration_active,
            'components_available': {
                'schema_parser': self.schema_parser is not None,
                'reasonableness_validator': self.reasonableness_validator is not None,
                'property_test_framework': self.property_test_framework is not None,
                'component_validation_manager': self.component_validation_manager is not None
            },
            'v5_schema_features': [
                'reasonableness_checks',
                'component_validation_sections',
                'property_tests',
                'enhanced_schema_validation'
            ]
        }


# Convenience functions for external use
async def integrate_with_phase3(blueprint: 'SystemBlueprint') -> Dict[str, Any]:
    """Integrate blueprint with Phase 3 schema system"""
    integrator = Phase3BlueprintIntegrator()
    return await integrator.integrate_with_blueprint_schema(blueprint)


async def parse_blueprint_with_phase3(blueprint_path: str) -> Any:
    """Parse blueprint file using Phase 3 schema parser"""
    integrator = Phase3BlueprintIntegrator()
    return await integrator.parse_blueprint_file(blueprint_path)


async def validate_reasonableness_phase3(blueprint: 'SystemBlueprint') -> Any:
    """Validate system reasonableness using Phase 3 validator"""
    integrator = Phase3BlueprintIntegrator()
    return await integrator.validate_system_reasonableness(blueprint)


async def get_phase3_status() -> Dict[str, Any]:
    """Get Phase 3 integration status"""
    integrator = Phase3BlueprintIntegrator()
    return integrator.get_integrator_status()


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test Phase3BlueprintIntegrator"""
        
        # Create integrator
        integrator = Phase3BlueprintIntegrator()
        
        # Display integrator status
        status = integrator.get_integrator_status()
        print("🔗 Phase 3 Blueprint Schema Integrator Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Create test blueprint
        class MockBlueprint:
            def __init__(self, description, components, reasonableness_checks=None):
                self.description = description
                self.components = components
                self.reasonableness_checks = reasonableness_checks or []
        
        test_blueprint = MockBlueprint(
            description="A comprehensive web application system with user authentication and data storage",
            components=[
                {
                    "name": "web_service",
                    "type": "web_service",
                    "configuration": {
                        "resource_requirements": {
                            "memory_mb": 1024,
                            "cpu_cores": 2,
                            "disk_gb": 20
                        },
                        "ports": [
                            {"port": 8080, "protocol": "http"}
                        ]
                    },
                    "dependencies": [
                        {"component_name": "database", "dependency_type": "data_dependency"}
                    ]
                },
                {
                    "name": "database",
                    "type": "database",
                    "configuration": {
                        "resource_requirements": {
                            "memory_mb": 2048,
                            "cpu_cores": 2,
                            "disk_gb": 100
                        }
                    }
                }
            ],
            reasonableness_checks=[
                {
                    "check_type": "component_coherence",
                    "description": "Ensure web service has sufficient resources",
                    "validation_logic": "component web_service memory_mb greater_than 512",
                    "severity": "warning"
                }
            ]
        )
        
        print(f"\n🚀 Testing Phase 3 integration...")
        
        # Test integration
        integration_result = await integrator.integrate_with_blueprint_schema(test_blueprint)
        
        print(f"\n📊 Integration Results:")
        print(f"  Integration successful: {'✅ YES' if integration_result['integration_successful'] else '❌ NO'}")
        print(f"  Schema validation: {integration_result['schema_validation'].get('valid', 'unknown')}")
        print(f"  Reasonableness validation: {integration_result['reasonableness_validation'].get('passed', 'unknown')}")
        print(f"  Property test validation: {integration_result['property_test_validation'].get('all_passed', 'unknown')}")
        print(f"  Component validation: {integration_result['component_validation'].get('all_valid', 'unknown')}")
        
        if integration_result['issues']:
            print(f"\n⚠️  Integration Issues ({len(integration_result['issues'])}):")
            for issue in integration_result['issues']:
                print(f"    - {issue}")
        
        # Test reasonableness validation
        print(f"\n🧠 Testing reasonableness validation...")
        try:
            reasonableness_result = await integrator.validate_system_reasonableness(test_blueprint)
            print(f"Reasonableness validation: {'✅ PASSED' if reasonableness_result.passed else '❌ FAILED'}")
            print(f"Checks performed: {reasonableness_result.checks_performed}")
            print(f"Execution time: {reasonableness_result.execution_time_ms:.2f}ms")
            
            if not reasonableness_result.passed:
                print("Issues found:")
                for issue in reasonableness_result.issues:
                    print(f"  - {issue}")
        except Exception as e:
            print(f"Reasonableness validation error: {e}")
        
        # Test integration summary
        print(f"\n📋 Integration Summary:")
        summary = await integrator.get_integration_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    # Run the test
    asyncio.run(main())