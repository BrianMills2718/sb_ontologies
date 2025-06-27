#!/usr/bin/env python3
"""
Test Suite for Phase 2: Component Library Foundation
Validates fail-hard principles and V5.0 component functionality
"""

import pytest
import os
from typing import Dict, Any
from pydantic import BaseModel, Field

# Import Phase 2 components
from autocoder.components.enhanced_base import (
    EnhancedComponentBase,
    EnhancedSource,
    EnhancedTransformer, 
    EnhancedSink,
    ComponentValidationError,
    SchemaValidationError,
    DependencyValidationError
)

from autocoder.components.component_registry import (
    ComponentRegistry,
    ComponentRegistryError,
    component_registry
)

from autocoder.validation.schema_framework import (
    SchemaValidator,
    SchemaValidationError as SchemaFrameworkError,
    SchemaCompatibilityError,
    ComponentDataSchema,
    SourceDataSchema,
    schema_validator
)


class TestEnhancedComponentBase:
    """Test enhanced component base classes with fail-hard validation"""
    
    def test_source_component_validation(self):
        """Test that Source components validate correctly"""
        
        # Valid source configuration
        valid_config = {
            'type': 'Source',
            'outputs': [
                {'name': 'data_output', 'schema': 'SourceData'}
            ]
        }
        
        # Should create successfully
        source = EnhancedSource("test_source", valid_config)
        assert source.component_type == "Source"
        assert source.name == "test_source"
    
    def test_source_component_fails_with_inputs(self):
        """Test that Source components fail hard when given inputs"""
        
        invalid_config = {
            'type': 'Source',
            'inputs': [
                {'name': 'invalid_input', 'schema': 'SomeSchema'}
            ],
            'outputs': [
                {'name': 'data_output', 'schema': 'SourceData'}
            ]
        }
        
        # Should fail hard
        with pytest.raises(ComponentValidationError) as exc_info:
            EnhancedSource("invalid_source", invalid_config)
        
        assert "cannot have inputs" in str(exc_info.value)
    
    def test_transformer_component_validation(self):
        """Test that Transformer components validate correctly"""
        
        valid_config = {
            'type': 'Transformer',
            'inputs': [
                {'name': 'data_input', 'schema': 'InputSchema'}
            ],
            'outputs': [
                {'name': 'data_output', 'schema': 'OutputSchema'}
            ]
        }
        
        # Should create successfully
        transformer = EnhancedTransformer("test_transformer", valid_config)
        assert transformer.component_type == "Transformer"
        assert transformer.name == "test_transformer"
    
    def test_transformer_fails_without_inputs(self):
        """Test that Transformer components fail hard without inputs"""
        
        invalid_config = {
            'type': 'Transformer',
            'outputs': [
                {'name': 'data_output', 'schema': 'OutputSchema'}
            ]
        }
        
        with pytest.raises(ComponentValidationError) as exc_info:
            EnhancedTransformer("invalid_transformer", invalid_config)
        
        assert "inputs" in str(exc_info.value)
    
    def test_transformer_fails_without_outputs(self):
        """Test that Transformer components fail hard without outputs"""
        
        invalid_config = {
            'type': 'Transformer',
            'inputs': [
                {'name': 'data_input', 'schema': 'InputSchema'}
            ]
        }
        
        with pytest.raises(ComponentValidationError) as exc_info:
            EnhancedTransformer("invalid_transformer", invalid_config)
        
        assert "outputs" in str(exc_info.value)
    
    def test_sink_component_validation(self):
        """Test that Sink components validate correctly"""
        
        valid_config = {
            'type': 'Sink',
            'inputs': [
                {'name': 'data_input', 'schema': 'SinkData'}
            ]
        }
        
        # Should create successfully
        sink = EnhancedSink("test_sink", valid_config)
        assert sink.component_type == "Sink"
        assert sink.name == "test_sink"
    
    def test_sink_component_fails_with_outputs(self):
        """Test that Sink components fail hard when given outputs"""
        
        invalid_config = {
            'type': 'Sink',
            'inputs': [
                {'name': 'data_input', 'schema': 'SinkData'}
            ],
            'outputs': [
                {'name': 'invalid_output', 'schema': 'SomeSchema'}
            ]
        }
        
        with pytest.raises(ComponentValidationError) as exc_info:
            EnhancedSink("invalid_sink", invalid_config)
        
        assert "cannot have outputs" in str(exc_info.value)
    
    def test_dependency_validation_fails_hard(self):
        """Test that missing dependencies cause hard failure"""
        
        # Create a component class that requires LLM
        class LLMRequiredComponent(EnhancedSource):
            def __init__(self, name: str, config: Dict[str, Any] = None):
                super().__init__(name, config)
                # Set required dependencies after initialization
                self.required_dependencies = ['llm']
                # Trigger validation manually since it happens in __init__
                self._validate_required_dependencies()
            
            def get_required_dependencies(self):
                return ['llm']
        
        config = {
            'type': 'Source',
            'outputs': [{'name': 'output', 'schema': 'SourceData'}]
        }
        
        # Clear environment variables to simulate missing LLM
        old_openai = os.environ.get('OPENAI_API_KEY')
        old_anthropic = os.environ.get('ANTHROPIC_API_KEY')
        
        try:
            # Remove environment variables
            for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']:
                if key in os.environ:
                    del os.environ[key]
            
            # Should fail hard
            with pytest.raises(DependencyValidationError) as exc_info:
                LLMRequiredComponent("llm_component", config)
            
            assert "no mock modes" in str(exc_info.value).lower()
            
        finally:
            # Restore environment
            if old_openai:
                os.environ['OPENAI_API_KEY'] = old_openai
            if old_anthropic:
                os.environ['ANTHROPIC_API_KEY'] = old_anthropic


class TestComponentRegistry:
    """Test component registry with fail-hard validation"""
    
    def setup_method(self):
        """Setup for each test"""
        # Create a fresh registry for testing
        self.registry = ComponentRegistry()
    
    def test_component_creation_and_registration(self):
        """Test successful component creation and registration"""
        
        config = {
            'type': 'Source',
            'outputs': [{'name': 'data', 'schema': 'SourceData'}]
        }
        
        component = self.registry.create_component("Source", "test_source", config)
        
        assert component.name == "test_source"
        assert component.component_type == "Source"
        
        # Should be retrievable from registry
        retrieved = self.registry.get_component("test_source")
        assert retrieved is component
    
    def test_duplicate_name_fails_hard(self):
        """Test that duplicate component names fail hard"""
        
        config = {
            'type': 'Source',
            'outputs': [{'name': 'data', 'schema': 'SourceData'}]
        }
        
        # Create first component
        self.registry.create_component("Source", "duplicate_name", config)
        
        # Try to create second with same name - should fail hard
        with pytest.raises(ComponentRegistryError) as exc_info:
            self.registry.create_component("Source", "duplicate_name", config)
        
        assert "already exists" in str(exc_info.value)
    
    def test_unknown_component_type_fails_hard(self):
        """Test that unknown component types fail hard"""
        
        config = {
            'type': 'UnknownType',
            'outputs': [{'name': 'data', 'schema': 'SomeSchema'}]
        }
        
        with pytest.raises(ComponentRegistryError) as exc_info:
            self.registry.create_component("UnknownType", "test_component", config)
        
        assert "Unknown component type" in str(exc_info.value)
    
    def test_invalid_component_logic_fails_hard(self):
        """Test that invalid component logic fails hard"""
        
        # Try to create Source with inputs
        invalid_config = {
            'type': 'Source',
            'inputs': [{'name': 'invalid', 'schema': 'Schema'}],
            'outputs': [{'name': 'data', 'schema': 'SourceData'}]
        }
        
        with pytest.raises(ComponentRegistryError) as exc_info:
            self.registry.create_component("Source", "invalid_source", invalid_config)
        
        assert "cannot have inputs" in str(exc_info.value)
    
    def test_missing_required_config_fails_hard(self):
        """Test that missing required configuration fails hard"""
        
        # Source without required outputs
        invalid_config = {
            'type': 'Source'
            # Missing outputs
        }
        
        with pytest.raises(ComponentRegistryError) as exc_info:
            self.registry.create_component("Source", "incomplete_source", invalid_config)
        
        assert "Missing required configuration fields" in str(exc_info.value)


class TestSchemaFramework:
    """Test schema validation framework with fail-hard principles"""
    
    def setup_method(self):
        """Setup for each test"""
        # Create fresh validator for testing
        self.validator = SchemaValidator()
    
    def test_schema_registration_and_validation(self):
        """Test schema registration and data validation"""
        
        # Define test schema
        class TestDataSchema(ComponentDataSchema):
            test_field: str = Field(..., description="Test field")
            optional_field: int = Field(default=42, description="Optional field")
        
        # Register schema
        self.validator.register_schema("TestData", TestDataSchema)
        
        # Valid data
        valid_data = {
            'timestamp': 1234567890.0,
            'component_source': 'test_component',
            'test_field': 'test_value'
        }
        
        # Should validate successfully
        validated = self.validator.validate_data("TestData", valid_data)
        assert validated.test_field == 'test_value'
        assert validated.optional_field == 42
    
    def test_schema_validation_fails_hard_on_missing_fields(self):
        """Test that missing required fields cause hard failure"""
        
        class StrictSchema(ComponentDataSchema):
            required_field: str = Field(..., description="Required field")
        
        self.validator.register_schema("StrictSchema", StrictSchema)
        
        # Data missing required field
        invalid_data = {
            'timestamp': 1234567890.0,
            'component_source': 'test_component'
            # Missing required_field
        }
        
        with pytest.raises(SchemaFrameworkError) as exc_info:
            self.validator.validate_data("StrictSchema", invalid_data)
        
        assert "strict schema compliance" in str(exc_info.value)
    
    def test_unregistered_schema_fails_hard(self):
        """Test that unregistered schemas fail hard"""
        
        data = {
            'timestamp': 1234567890.0,
            'component_source': 'test_component'
        }
        
        with pytest.raises(SchemaFrameworkError) as exc_info:
            self.validator.validate_data("UnregisteredSchema", data)
        
        assert "not registered" in str(exc_info.value)
        assert "no schema inference" in str(exc_info.value)
    
    def test_schema_compatibility_validation(self):
        """Test schema compatibility validation"""
        
        class OutputSchema(ComponentDataSchema):
            output_data: str = Field(..., description="Output data")
        
        class InputSchema(ComponentDataSchema):
            output_data: str = Field(..., description="Compatible input data")
        
        self.validator.register_schema("OutputSchema", OutputSchema)
        self.validator.register_schema("InputSchema", InputSchema)
        
        # Register explicit compatibility
        self.validator.register_schema_compatibility("OutputSchema", "InputSchema")
        
        # Should validate as compatible
        is_compatible = self.validator.validate_schema_compatibility("OutputSchema", "InputSchema")
        assert is_compatible is True
    
    def test_incompatible_schemas_fail_hard(self):
        """Test that incompatible schemas fail hard"""
        
        class IncompatibleSchema1(ComponentDataSchema):
            field1: str = Field(..., description="Field 1")
        
        class IncompatibleSchema2(ComponentDataSchema):
            field2: int = Field(..., description="Field 2")
        
        self.validator.register_schema("Schema1", IncompatibleSchema1)
        self.validator.register_schema("Schema2", IncompatibleSchema2)
        
        # Should fail hard on incompatibility
        with pytest.raises(SchemaCompatibilityError) as exc_info:
            self.validator.validate_schema_compatibility("Schema1", "Schema2")
        
        assert "not compatible" in str(exc_info.value)
        assert "no automatic conversion" in str(exc_info.value)


class TestPhase2Integration:
    """Test integration of all Phase 2 components"""
    
    def test_complete_component_lifecycle(self):
        """Test complete component lifecycle with validation"""
        
        # Create registry and validator
        registry = ComponentRegistry()
        validator = SchemaValidator()
        
        # Define custom schema
        class CustomDataSchema(SourceDataSchema):
            custom_field: str = Field(..., description="Custom field")
        
        validator.register_schema("CustomData", CustomDataSchema)
        
        # Create source component
        source_config = {
            'type': 'Source',
            'outputs': [{'name': 'custom_output', 'schema': 'CustomData'}]
        }
        
        source = registry.create_component("Source", "custom_source", source_config)
        
        # Register schemas with component
        source.register_output_schema("custom_output", CustomDataSchema)
        
        # Test data validation
        test_data = {
            'timestamp': 1234567890.0,
            'component_source': 'custom_source',
            'data_id': 'test_123',
            'data_type': 'custom',
            'custom_field': 'custom_value'
        }
        
        # Should validate successfully
        validated = source.validate_output_data("custom_output", test_data)
        assert validated.custom_field == 'custom_value'
    
    def test_fail_hard_principles_maintained(self):
        """Test that fail-hard principles are maintained throughout Phase 2"""
        
        registry = ComponentRegistry()
        
        # Test 1: No mock modes anywhere
        source_config = {
            'type': 'Source',
            'outputs': [{'name': 'output', 'schema': 'SourceData'}]
        }
        
        source = registry.create_component("Source", "no_mock_source", source_config)
        
        # Should not have any mock-related attributes
        assert not hasattr(source, 'mock_mode')
        assert not hasattr(source, '_mock_data')
        assert not hasattr(source, 'enable_mock')
        
        # Test 2: Strict validation enabled
        assert source.strict_validation is True
        
        # Test 3: No fallback behaviors
        with pytest.raises(ComponentRegistryError):
            registry.create_component("InvalidType", "test", {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])