#!/usr/bin/env python3
"""
Phase 2 Component Library Integration Tests
Comprehensive testing of all Phase 2 components working together
"""

import unittest
import logging
import time
import tempfile
import os
import uuid
from typing import Dict, Any, List

# Import Phase 2 components
from day1_core_component_classes.component_registry_implementation import (
    ComponentRegistry, ComponentRegistryError, component_registry
)
from day1_core_component_classes.schema_framework_implementation import (
    SchemaValidator, SchemaValidationError, schema_validator,
    ComponentDataSchema, SourceDataSchema, TransformerDataSchema, SinkDataSchema
)
from component_lifecycle import (
    ComponentLifecycle, ComponentLifecycleError, ComponentSpec, 
    ComponentLifecycleState, ValidationResult, LifecycleValidationResult,
    component_lifecycle
)
from security_validation import (
    ComponentSecurityValidator, SecurityValidationError, SecurityLevel,
    SecurityIssue, SecurityIssueType, SecurityValidationResult,
    security_validator
)


class MockComponent:
    """Mock component for testing"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
    
    def get_required_config_fields(self) -> List[str]:
        return ['type', 'inputs', 'outputs']
    
    def get_required_dependencies(self) -> List[str]:
        return []


class TestComponentRegistryIntegration(unittest.TestCase):
    """Test Component Registry integration with other systems"""
    
    def setUp(self):
        """Set up test environment"""
        self.registry = ComponentRegistry()
        self.registry.clear_registry()  # Start with clean registry
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestComponentRegistry")
        
        # Track created components for cleanup
        self.created_components = []
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            # Clean up created components
            for component_name in self.created_components:
                try:
                    self.registry.unregister_component(component_name)
                except Exception:
                    pass  # Ignore cleanup errors
            
            # Clear the registry
            self.registry.clear_registry()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")
    
    def test_component_registration_and_creation(self):
        """Test component registration and creation workflow"""
        
        # Test component configuration
        config = {
            'type': 'Source',
            'outputs': [{'name': 'data_output', 'schema': 'SourceData'}]
        }
        
        # Create component with unique name
        component_name = f'test_source_{uuid.uuid4().hex[:8]}'
        component = self.registry.create_component('Source', component_name, config)
        self.created_components.append(component_name)
        
        # Verify component was created
        self.assertIsNotNone(component)
        self.assertEqual(component.name, component_name)
        
        # Verify component is registered
        registered_component = self.registry.get_component(component_name)
        self.assertEqual(component, registered_component)
        
        # Verify component types are available
        types = self.registry.list_component_types()
        self.assertIn('Source', types)
        self.assertIn('Transformer', types)
        self.assertIn('Sink', types)
        
        self.logger.info("✅ Component registration and creation test passed")
    
    def test_component_validation_integration(self):
        """Test component validation integration"""
        
        # Create valid source component
        source_config = {
            'type': 'Source',
            'outputs': [{'name': 'data_output', 'schema': 'SourceData'}]
        }
        source_name = f'valid_source_{uuid.uuid4().hex[:8]}'
        source = self.registry.create_component('Source', source_name, source_config)
        self.created_components.append(source_name)
        
        # Validate component dependencies
        result = self.registry.validate_component_dependencies(source_name)
        self.assertTrue(result)
        
        # Test invalid component configuration
        with self.assertRaises(ComponentRegistryError):
            invalid_config = {
                'type': 'Source',
                'inputs': [{'name': 'invalid_input'}]  # Sources shouldn't have inputs
            }
            self.registry.create_component('Source', 'invalid_source', invalid_config)
        
        self.logger.info("✅ Component validation integration test passed")


class TestSchemaValidationIntegration(unittest.TestCase):
    """Test Schema Validation Framework integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = SchemaValidator()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestSchemaValidation")
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            # No specific cleanup needed for schema validator
            pass
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")
    
    def test_schema_registration_and_validation(self):
        """Test schema registration and data validation"""
        
        # Test built-in schema validation
        valid_data = {
            'timestamp': time.time(),
            'component_source': 'test_component',
            'data_id': 'test_123',
            'data_type': 'test_data'
        }
        
        # Validate data against SourceData schema
        result = self.validator.validate_data('SourceData', valid_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.component_source, 'test_component')
        
        # Test invalid data
        with self.assertRaises(SchemaValidationError):
            invalid_data = {
                'timestamp': 'invalid_timestamp',  # Should be float
                'component_source': 'test_component'
                # Missing required fields
            }
            self.validator.validate_data('SourceData', invalid_data)
        
        self.logger.info("✅ Schema registration and validation test passed")
    
    def test_schema_compatibility_validation(self):
        """Test schema compatibility checking"""
        
        # Test compatible schemas
        result = self.validator.validate_schema_compatibility('SourceData', 'ComponentData')
        self.assertTrue(result)
        
        # Test identical schemas
        result = self.validator.validate_schema_compatibility('SourceData', 'SourceData')
        self.assertTrue(result)
        
        # Test incompatible schemas - should raise SchemaCompatibilityError
        from day1_core_component_classes.schema_framework_implementation import SchemaCompatibilityError
        with self.assertRaises(SchemaCompatibilityError):
            self.validator.validate_schema_compatibility('SourceData', 'UnknownSchema')
        
        self.logger.info("✅ Schema compatibility validation test passed")
    
    def test_component_schema_validation(self):
        """Test component configuration schema validation"""
        
        # Valid component configuration with schemas
        component_config = {
            'inputs': [
                {'name': 'input1', 'schema': 'ComponentData'}
            ],
            'outputs': [
                {'name': 'output1', 'schema': 'SourceData'}
            ]
        }
        
        # Validate component schemas
        result = self.validator.validate_component_schemas(component_config)
        self.assertIsNotNone(result)
        self.assertIn('input_input1', result)
        self.assertIn('output_output1', result)
        self.assertTrue(result['input_input1']['valid'])
        self.assertTrue(result['output_output1']['valid'])
        
        # Invalid component configuration
        with self.assertRaises(SchemaValidationError):
            invalid_config = {
                'outputs': [
                    {'name': 'output1', 'schema': 'NonExistentSchema'}
                ]
            }
            self.validator.validate_component_schemas(invalid_config)
        
        self.logger.info("✅ Component schema validation test passed")


class TestComponentLifecycleIntegration(unittest.TestCase):
    """Test Component Lifecycle Management integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.lifecycle = ComponentLifecycle()
        self.registry = ComponentRegistry()
        self.registry.clear_registry()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestComponentLifecycle")
        
        # Track created components for cleanup
        self.created_components = []
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            # Clear the lifecycle first
            self.lifecycle.clear_all_components()
            
            # Clear the registry  
            self.registry.clear_registry()
            
            # Clear created components list
            self.created_components.clear()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")
    
    def test_component_creation_lifecycle(self):
        """Test complete component creation lifecycle"""
        
        # Create component specification
        spec = ComponentSpec(
            name='lifecycle_test_source',
            component_type='Source',
            config={
                'type': 'Source',
                'outputs': [{'name': 'data_output', 'schema': 'SourceData'}]
            }
        )
        
        # Create component through lifecycle
        component = self.lifecycle.create_component(spec)
        
        # Verify component was created
        self.assertIsNotNone(component)
        self.assertEqual(component.name, 'lifecycle_test_source')
        
        # Verify component state
        state = self.lifecycle.get_component_state('lifecycle_test_source')
        self.assertEqual(state, ComponentLifecycleState.ACTIVE)
        
        self.logger.info("✅ Component creation lifecycle test passed")
    
    def test_component_lifecycle_validation(self):
        """Test component lifecycle validation"""
        
        # Create component
        spec = ComponentSpec(
            name='validation_test_transformer',
            component_type='Transformer',
            config={
                'type': 'Transformer',
                'inputs': [{'name': 'data_input', 'schema': 'ComponentData'}],
                'outputs': [{'name': 'processed_output', 'schema': 'TransformerData'}]
            }
        )
        component = self.lifecycle.create_component(spec)
        
        # Validate component lifecycle
        result = self.lifecycle.validate_component_lifecycle('validation_test_transformer')
        
        # Verify validation result
        self.assertIsInstance(result, LifecycleValidationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.component_name, 'validation_test_transformer')
        self.assertIn(ComponentLifecycleState.ACTIVE, result.states_validated)
        self.assertGreater(len(result.validation_results), 0)
        
        self.logger.info("✅ Component lifecycle validation test passed")
    
    def test_component_dependency_lifecycle(self):
        """Test component dependency management in lifecycle"""
        
        # Create source component (no dependencies)
        source_spec = ComponentSpec(
            name='dep_test_source',
            component_type='Source',
            config={
                'type': 'Source',
                'outputs': [{'name': 'source_output', 'schema': 'SourceData'}]
            }
        )
        source = self.lifecycle.create_component(source_spec)
        
        # Create transformer component (depends on source)
        transformer_spec = ComponentSpec(
            name='dep_test_transformer',
            component_type='Transformer',
            config={
                'type': 'Transformer',
                'inputs': [{'name': 'transform_input', 'schema': 'SourceData'}],
                'outputs': [{'name': 'transform_output', 'schema': 'TransformerData'}]
            },
            dependencies=['dep_test_source']
        )
        transformer = self.lifecycle.create_component(transformer_spec)
        
        # Verify both components are active
        source_state = self.lifecycle.get_component_state('dep_test_source')
        transformer_state = self.lifecycle.get_component_state('dep_test_transformer')
        
        self.assertEqual(source_state, ComponentLifecycleState.ACTIVE)
        self.assertEqual(transformer_state, ComponentLifecycleState.ACTIVE)
        
        # Test dependency validation
        result = self.lifecycle.validate_component_lifecycle('dep_test_transformer')
        self.assertTrue(result.success)
        
        self.logger.info("✅ Component dependency lifecycle test passed")
    
    def test_component_teardown_lifecycle(self):
        """Test component teardown lifecycle"""
        
        # Create component
        sink_name = f'teardown_test_sink_{uuid.uuid4().hex[:8]}'
        spec = ComponentSpec(
            name=sink_name,
            component_type='Sink',
            config={
                'type': 'Sink',
                'inputs': [{'name': 'sink_input', 'schema': 'ComponentData'}]
            }
        )
        component = self.lifecycle.create_component(spec)
        
        # Verify component is active
        state = self.lifecycle.get_component_state(sink_name)
        self.assertEqual(state, ComponentLifecycleState.ACTIVE)
        
        # Teardown component
        result = self.lifecycle.teardown_component(sink_name)
        self.assertTrue(result)
        
        # Verify component is destroyed
        final_state = self.lifecycle.get_component_state(sink_name)
        self.assertEqual(final_state, ComponentLifecycleState.DESTROYED)
        
        self.logger.info("✅ Component teardown lifecycle test passed")


class TestSecurityValidationIntegration(unittest.TestCase):
    """Test Security Validation Framework integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.security_validator = ComponentSecurityValidator()
        self.registry = ComponentRegistry()
        self.registry.clear_registry()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestSecurityValidation")
        
        # Track created components for cleanup
        self.created_components = []
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            # Clean up created components
            for component_name in self.created_components:
                try:
                    self.registry.unregister_component(component_name)
                except Exception:
                    pass  # Ignore cleanup errors
            
            # Clear the registry
            self.registry.clear_registry()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")
    
    def test_component_security_validation(self):
        """Test component security validation"""
        
        # Create secure component
        secure_config = {
            'type': 'Source',
            'outputs': [{'name': 'secure_output', 'schema': 'SourceData'}],
            'input_validation': True,
            'output_encoding': True
        }
        secure_name = f'secure_source_{uuid.uuid4().hex[:8]}'
        secure_component = self.registry.create_component('Source', secure_name, secure_config)
        self.created_components.append(secure_name)
        
        # Validate security
        result = self.security_validator.validate_component_security(secure_component)
        
        # Verify security validation result
        self.assertIsInstance(result, SecurityValidationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.component_name, secure_name)
        self.assertNotEqual(result.security_level, SecurityLevel.CRITICAL)
        
        self.logger.info("✅ Component security validation test passed")
    
    def test_insecure_component_detection(self):
        """Test detection of insecure components"""
        
        # Create insecure component
        insecure_config = {
            'type': 'Source',
            'outputs': [{'name': 'insecure_output', 'schema': 'SourceData'}],
            'ssl_verify': False,  # Insecure default
            'debug': True  # Insecure in production
        }
        insecure_name = f'insecure_source_{uuid.uuid4().hex[:8]}'
        insecure_component = self.registry.create_component('Source', insecure_name, insecure_config)
        self.created_components.append(insecure_name)
        
        # Validate security
        result = self.security_validator.validate_component_security(insecure_component)
        
        # Verify security issues are detected
        self.assertIsInstance(result, SecurityValidationResult)
        self.assertGreater(len(result.issues), 0)
        
        # Check for expected security issues
        issue_types = [issue.issue_type for issue in result.issues]
        self.assertIn(SecurityIssueType.INSECURE_DEFAULTS, issue_types)
        
        self.logger.info("✅ Insecure component detection test passed")
    
    def test_security_policy_enforcement(self):
        """Test security policy enforcement"""
        
        # Create component with critical security issues
        critical_config = {
            'type': 'Source',
            'outputs': [{'name': 'critical_output', 'schema': 'SourceData'}],
            'password': 'hardcoded_secret',  # Critical: hardcoded secret
            'ssl_verify': False,  # High: insecure default
            'debug': True  # Medium: debug mode
        }
        critical_component = self.registry.create_component('Source', 'critical_source', critical_config)
        
        # Security validation should detect critical issues
        result = self.security_validator.validate_component_security(critical_component)
        
        # Verify critical security level is detected
        self.assertEqual(result.security_level, SecurityLevel.CRITICAL)
        
        # Check for hardcoded secret detection
        critical_issues = [issue for issue in result.issues if issue.severity == SecurityLevel.CRITICAL]
        self.assertGreater(len(critical_issues), 0)
        
        self.logger.info("✅ Security policy enforcement test passed")


class TestFullSystemIntegration(unittest.TestCase):
    """Test full system integration of all Phase 2 components"""
    
    def setUp(self):
        """Set up test environment"""
        self.registry = ComponentRegistry()
        self.schema_validator = SchemaValidator()
        self.lifecycle = ComponentLifecycle(component_registry=self.registry, schema_validator=self.schema_validator)
        self.security_validator = ComponentSecurityValidator()
        
        # Clear any existing components
        self.registry.clear_registry()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestFullSystemIntegration")
        
        # Track created components for cleanup
        self.created_components = []
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            # Clear the lifecycle first
            self.lifecycle.clear_all_components()
            
            # Clear the registry
            self.registry.clear_registry()
            
            # Clear created components list
            self.created_components.clear()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")
    
    def test_complete_system_workflow(self):
        """Test complete system workflow with all components"""
        
        # Phase 1: Create data pipeline components
        
        # Source component
        source_name = f'system_data_source_{uuid.uuid4().hex[:8]}'
        source_spec = ComponentSpec(
            name=source_name,
            component_type='Source',
            config={
                'type': 'Source',
                'outputs': [{'name': 'raw_data', 'schema': 'SourceData'}],
                'input_validation': True,
                'output_encoding': True
            }
        )
        
        # Transformer component
        transformer_spec = ComponentSpec(
            name='system_data_transformer',
            component_type='Transformer',
            config={
                'type': 'Transformer',
                'inputs': [{'name': 'raw_input', 'schema': 'SourceData'}],
                'outputs': [{'name': 'processed_data', 'schema': 'TransformerData'}],
                'input_validation': True,
                'output_encoding': True
            },
            dependencies=[source_name]
        )
        
        # Sink component
        sink_spec = ComponentSpec(
            name='system_data_sink',
            component_type='Sink',
            config={
                'type': 'Sink',
                'inputs': [{'name': 'final_input', 'schema': 'TransformerData'}],
                'input_validation': True
            },
            dependencies=['system_data_transformer']
        )
        
        # Phase 2: Create components through lifecycle
        components = []
        
        source = self.lifecycle.create_component(source_spec)
        components.append(source)
        self.created_components.append(source_name)
        
        transformer_name = transformer_spec.name
        transformer = self.lifecycle.create_component(transformer_spec)
        self.created_components.append(transformer_name)
        components.append(transformer)
        
        sink_name = sink_spec.name
        sink = self.lifecycle.create_component(sink_spec)
        self.created_components.append(sink_name)
        components.append(sink)
        
        # Phase 3: Validate all components
        
        # Lifecycle validation
        for component in components:
            result = self.lifecycle.validate_component_lifecycle(component.name)
            self.assertTrue(result.success, f"Lifecycle validation failed for {component.name}")
        
        # Security validation
        for component in components:
            result = self.security_validator.validate_component_security(component)
            self.assertTrue(result.success, f"Security validation failed for {component.name}")
            self.assertNotEqual(result.security_level, SecurityLevel.CRITICAL)
        
        # Registry validation
        registry_result = self.registry.validate_all_components()
        self.assertTrue(all(registry_result.values()), "Registry validation failed")
        
        # Phase 4: Test schema compatibility
        
        # Validate source -> transformer schema compatibility
        source_output_schema = 'SourceData'
        transformer_input_schema = 'SourceData'  # Compatible
        compatibility = self.schema_validator.validate_schema_compatibility(
            source_output_schema, transformer_input_schema
        )
        self.assertTrue(compatibility)
        
        # Validate transformer -> sink schema compatibility
        transformer_output_schema = 'TransformerData'
        sink_input_schema = 'TransformerData'  # Compatible
        compatibility = self.schema_validator.validate_schema_compatibility(
            transformer_output_schema, sink_input_schema
        )
        self.assertTrue(compatibility)
        
        # Phase 5: Get system summary
        
        lifecycle_summary = self.lifecycle.get_lifecycle_summary()
        security_summary = self.security_validator.get_security_summary(components)
        
        # Verify system state
        self.assertEqual(lifecycle_summary['total_components'], 3)
        self.assertEqual(len(lifecycle_summary['active_components']), 3)
        self.assertEqual(security_summary['total_components'], 3)
        self.assertEqual(security_summary['critical_issues_count'], 0)
        
        # Phase 6: Cleanup (teardown in reverse dependency order)
        
        teardown_result = self.lifecycle.teardown_component('system_data_sink')
        self.assertTrue(teardown_result)
        
        teardown_result = self.lifecycle.teardown_component('system_data_transformer')
        self.assertTrue(teardown_result)
        
        teardown_result = self.lifecycle.teardown_component(source_name)
        self.assertTrue(teardown_result)
        
        self.logger.info("✅ Complete system workflow test passed")
    
    def test_system_error_handling(self):
        """Test system error handling and fail-hard behavior"""
        
        # Test 1: Invalid component type
        with self.assertRaises(ComponentLifecycleError):
            invalid_spec = ComponentSpec(
                name='invalid_component',
                component_type='NonExistentType',
                config={'type': 'Invalid'}
            )
            self.lifecycle.create_component(invalid_spec)
        
        # Test 2: Missing dependencies
        with self.assertRaises(ComponentLifecycleError):
            dependent_spec = ComponentSpec(
                name='dependent_component',
                component_type='Transformer',
                config={
                    'type': 'Transformer',
                    'inputs': [{'name': 'input', 'schema': 'ComponentData'}],
                    'outputs': [{'name': 'output', 'schema': 'TransformerData'}]
                },
                dependencies=['nonexistent_dependency']
            )
            self.lifecycle.create_component(dependent_spec)
        
        # Test 3: Invalid schema
        with self.assertRaises(SchemaValidationError):
            invalid_data = {
                'invalid_field': 'invalid_value'
                # Missing required fields
            }
            self.schema_validator.validate_data('SourceData', invalid_data)
        
        # Test 4: Security validation failure
        critical_config = {
            'type': 'Source',
            'outputs': [{'name': 'output', 'schema': 'SourceData'}],
            'password': 'hardcoded_secret'  # Critical security issue
        }
        critical_component = self.registry.create_component('Source', 'critical_test', critical_config)
        
        with self.assertRaises(SecurityValidationError):
            self.security_validator.enforce_security_policies(critical_component)
        
        self.logger.info("✅ System error handling test passed")
    
    def test_system_performance_benchmarks(self):
        """Test system performance benchmarks"""
        
        start_time = time.time()
        
        # Create multiple components to test performance
        components = []
        for i in range(10):
            spec = ComponentSpec(
                name=f'perf_test_source_{i}_{uuid.uuid4().hex[:8]}',
                component_type='Source',
                config={
                    'type': 'Source',
                    'outputs': [{'name': f'output_{i}', 'schema': 'SourceData'}],
                    'input_validation': True,
                    'output_encoding': True
                }
            )
            component = self.lifecycle.create_component(spec)
            components.append(component)
            self.created_components.append(spec.name)
        
        creation_time = time.time() - start_time
        
        # Validate all components
        validation_start = time.time()
        
        for component in components:
            # Lifecycle validation
            lifecycle_result = self.lifecycle.validate_component_lifecycle(component.name)
            self.assertTrue(lifecycle_result.success)
            
            # Security validation
            security_result = self.security_validator.validate_component_security(component)
            self.assertTrue(security_result.success)
        
        validation_time = time.time() - validation_start
        
        # Performance assertions
        self.assertLess(creation_time, 5.0, "Component creation should complete in <5 seconds")
        self.assertLess(validation_time, 10.0, "Component validation should complete in <10 seconds")
        
        # Cleanup
        for component in components:
            self.lifecycle.teardown_component(component.name)
        
        total_time = time.time() - start_time
        self.assertLess(total_time, 20.0, "Complete workflow should complete in <20 seconds")
        
        self.logger.info(f"✅ System performance benchmark passed (Total: {total_time:.3f}s)")


class TestPhase2ComplianceValidation(unittest.TestCase):
    """Test Phase 2 compliance with V5.0 requirements"""
    
    def setUp(self):
        """Set up test environment"""
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("TestPhase2Compliance")
        
        # Track created components for cleanup
        self.created_components = []
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            # Clean up any created components
            from component_lifecycle import component_lifecycle
            component_lifecycle.clear_all_components()
            
            # Also clear the global registry to be safe
            from day1_core_component_classes.component_registry_implementation import component_registry
            component_registry.clear_registry()
            
            # Clear created components list
            self.created_components.clear()
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")
    
    def test_no_mock_or_fallback_mechanisms(self):
        """Test that no mock or fallback mechanisms exist"""
        
        # Test 1: Component Registry fail-hard behavior
        registry = ComponentRegistry()
        
        with self.assertRaises(ComponentRegistryError):
            # Should fail hard on unknown component type
            registry.create_component('UnknownType', 'test', {})
        
        # Test 2: Schema Validator fail-hard behavior
        validator = SchemaValidator()
        
        with self.assertRaises(SchemaValidationError):
            # Should fail hard on unknown schema
            validator.validate_data('UnknownSchema', {})
        
        # Test 3: Component Lifecycle fail-hard behavior
        lifecycle = ComponentLifecycle()
        
        with self.assertRaises(ComponentLifecycleError):
            # Should fail hard on invalid component spec
            invalid_spec = ComponentSpec(
                name='',  # Invalid empty name
                component_type='Source',
                config={}
            )
            lifecycle.create_component(invalid_spec)
        
        # Test 4: Security Validator fail-hard behavior
        security_validator = ComponentSecurityValidator()
        
        # Create component with critical security issues
        critical_config = {
            'type': 'Source',
            'outputs': [{'name': 'output', 'schema': 'SourceData'}],
            'password': 'hardcoded_secret'
        }
        registry.clear_registry()
        critical_name = f'critical_test_{uuid.uuid4().hex[:8]}'
        critical_component = registry.create_component('Source', critical_name, critical_config)
        self.created_components.append(critical_name)
        
        with self.assertRaises(SecurityValidationError):
            # Should fail hard on critical security issues
            security_validator.enforce_security_policies(critical_component)
        
        self.logger.info("✅ No mock or fallback mechanisms test passed")
    
    def test_comprehensive_validation_coverage(self):
        """Test comprehensive validation coverage"""
        
        # Test that all major validation areas are covered
        registry = ComponentRegistry()
        registry.clear_registry()
        schema_validator = SchemaValidator()
        lifecycle = ComponentLifecycle(component_registry=registry, schema_validator=schema_validator)
        security_validator = ComponentSecurityValidator()
        
        # Create test component
        coverage_component_name = f'coverage_test_component_{uuid.uuid4().hex[:8]}'
        spec = ComponentSpec(
            name=coverage_component_name,
            component_type='Source',
            config={
                'type': 'Source',
                'outputs': [{'name': 'test_output', 'schema': 'SourceData'}],
                'input_validation': True,
                'output_encoding': True
            }
        )
        component = lifecycle.create_component(spec)
        self.created_components.append(coverage_component_name)
        
        # Verify all validation types work
        
        # 1. Registry validation
        registry_result = registry.validate_component_dependencies(coverage_component_name)
        self.assertTrue(registry_result)
        
        # 2. Schema validation
        test_data = {
            'timestamp': time.time(),
            'component_source': coverage_component_name,
            'data_id': 'test_123',
            'data_type': 'test_data'
        }
        schema_result = schema_validator.validate_data('SourceData', test_data)
        self.assertIsNotNone(schema_result)
        
        # 3. Lifecycle validation
        lifecycle_result = lifecycle.validate_component_lifecycle(coverage_component_name)
        self.assertTrue(lifecycle_result.success)
        
        # 4. Security validation
        security_result = security_validator.validate_component_security(component)
        self.assertTrue(security_result.success)
        
        self.logger.info("✅ Comprehensive validation coverage test passed")
    
    def test_phase2_implementation_completeness(self):
        """Test Phase 2 implementation completeness"""
        
        # Verify all required Phase 2 components exist and are functional
        
        # 1. Enhanced Component Registry
        registry = ComponentRegistry()
        self.assertIsNotNone(registry)
        
        # Verify built-in component types
        types = registry.list_component_types()
        required_types = ['Source', 'Transformer', 'Sink']
        for required_type in required_types:
            self.assertIn(required_type, types, f"Required component type '{required_type}' missing")
        
        # 2. Schema-Aware Validation Framework
        schema_validator = SchemaValidator()
        self.assertIsNotNone(schema_validator)
        
        # Verify built-in schemas
        schemas = schema_validator.list_schemas()
        required_schemas = ['ComponentData', 'SourceData', 'TransformerData', 'SinkData']
        for required_schema in required_schemas:
            self.assertIn(required_schema, schemas, f"Required schema '{required_schema}' missing")
        
        # 3. Component Lifecycle Management
        lifecycle = ComponentLifecycle()
        self.assertIsNotNone(lifecycle)
        
        # Verify lifecycle methods exist
        self.assertTrue(hasattr(lifecycle, 'create_component'))
        self.assertTrue(hasattr(lifecycle, 'validate_component_lifecycle'))
        self.assertTrue(hasattr(lifecycle, 'teardown_component'))
        
        # 4. Security Validation Framework
        security_validator = ComponentSecurityValidator()
        self.assertIsNotNone(security_validator)
        
        # Verify security validation methods exist
        self.assertTrue(hasattr(security_validator, 'validate_component_security'))
        self.assertTrue(hasattr(security_validator, 'check_security_vulnerabilities'))
        self.assertTrue(hasattr(security_validator, 'enforce_security_policies'))
        
        self.logger.info("✅ Phase 2 implementation completeness test passed")


def run_all_tests():
    """Run all Phase 2 integration tests"""
    
    # Configure detailed logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("Phase2IntegrationTests")
    logger.info("Starting Phase 2 Component Library Integration Tests")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestComponentRegistryIntegration,
        TestSchemaValidationIntegration,
        TestComponentLifecycleIntegration,
        TestSecurityValidationIntegration,
        TestFullSystemIntegration,
        TestPhase2ComplianceValidation
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Log results
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    if result.failures:
        logger.error("Test failures:")
        for test, failure in result.failures:
            logger.error(f"  {test}: {failure}")
    
    if result.errors:
        logger.error("Test errors:")
        for test, error in result.errors:
            logger.error(f"  {test}: {error}")
    
    # Return success status
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        logger.info("✅ All Phase 2 integration tests passed!")
    else:
        logger.error("❌ Some Phase 2 integration tests failed!")
    
    return success, result


if __name__ == '__main__':
    success, result = run_all_tests()
    exit(0 if success else 1)