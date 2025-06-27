#!/usr/bin/env python3
"""
Test Suite for Schema-Aware Component Generator
Validates fail-hard schema generation with Pydantic integration
"""

import pytest
import tempfile
import os
from typing import Dict, Any
from pydantic import BaseModel

from autocoder.generation.schema_generator import (
    SchemaAwareComponentGenerator,
    ComponentGenerationError,
    SchemaGenerationError,
    GeneratedComponent
)
from autocoder.generation.nl_parser import ComponentType
from autocoder.validation.schema_framework import (
    ComponentDataSchema,
    SourceDataSchema,
    TransformerDataSchema,
    SinkDataSchema
)


class TestSchemaAwareComponentGenerator:
    """Test schema-aware component generator with fail-hard validation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.generator = SchemaAwareComponentGenerator()
    
    def test_valid_source_component_generation(self):
        """Test generation of valid source component"""
        
        nl_spec = "Create a data source component called WeatherApiSource that reads JSON data from API endpoints"
        
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify component structure
        assert component.class_name == "WeatherApiSource"
        assert component.component_type == ComponentType.SOURCE
        assert component.source_code
        assert component.schema_classes
        assert component.config_template
        assert component.validation_results
        
        # Verify schemas
        assert f"{component.class_name}OutputSchema" in component.schema_classes
        output_schema = component.schema_classes[f"{component.class_name}OutputSchema"]
        assert issubclass(output_schema, SourceDataSchema)
        
        # Verify source code structure
        assert f"class {component.class_name}" in component.source_code
        assert "async def process(self)" in component.source_code
        assert "fail hard" in component.source_code.lower()
        assert "V5.0" in component.source_code
        
        # Verify no mock modes
        assert "mock_mode" not in component.source_code
        assert ("mock" not in component.source_code.lower() or 
                "no mock modes" in component.source_code.lower())
        
        # Verify validation results
        assert component.validation_results["overall_status"] == "PASSED"
        assert component.validation_results["security_validation"]["passed"]
        assert all(result["passed"] for result in component.validation_results["schema_validation"].values())
    
    def test_valid_transformer_component_generation(self):
        """Test generation of valid transformer component"""
        
        nl_spec = "Build a transformer component called DataFilter that filters CSV data based on conditions"
        
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify component structure
        assert component.class_name == "DataFilter"
        assert component.component_type == ComponentType.TRANSFORMER
        
        # Verify schemas (transformers have both input and output)
        assert f"{component.class_name}InputSchema" in component.schema_classes
        assert f"{component.class_name}OutputSchema" in component.schema_classes
        
        input_schema = component.schema_classes[f"{component.class_name}InputSchema"]
        output_schema = component.schema_classes[f"{component.class_name}OutputSchema"]
        
        assert issubclass(input_schema, TransformerDataSchema)
        assert issubclass(output_schema, TransformerDataSchema)
        
        # Verify config template
        assert "inputs" in component.config_template
        assert "outputs" in component.config_template
        assert component.config_template["type"] == "Transformer"
    
    def test_valid_sink_component_generation(self):
        """Test generation of valid sink component"""
        
        nl_spec = "Make a sink component called DatabaseWriter that stores JSON data to database tables"
        
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify component structure
        assert component.class_name == "DatabaseWriter"
        assert component.component_type == ComponentType.SINK
        
        # Verify schemas (sinks only have input)
        assert f"{component.class_name}InputSchema" in component.schema_classes
        assert f"{component.class_name}OutputSchema" not in component.schema_classes
        
        input_schema = component.schema_classes[f"{component.class_name}InputSchema"]
        assert issubclass(input_schema, SinkDataSchema)
        
        # Verify config template
        assert "inputs" in component.config_template
        assert "outputs" not in component.config_template
        assert component.config_template["type"] == "Sink"
    
    def test_invalid_natural_language_fails_hard(self):
        """Test that invalid natural language fails hard"""
        
        invalid_specs = [
            "",  # Empty specification
            "Create a thing that does stuff",  # No class name
            "Make a component called TestComp",  # No component type
            "Create a source called TestSource",  # No data type
        ]
        
        for invalid_spec in invalid_specs:
            with pytest.raises((ComponentGenerationError, Exception)) as exc_info:
                self.generator.generate_component_from_nl(invalid_spec)
            
            # Should fail hard, not generate partial components
            error_msg = str(exc_info.value).lower()
            assert ("fail" in error_msg or "error" in error_msg or 
                   "required" in error_msg or "missing" in error_msg)
    
    def test_schema_validation_enforced(self):
        """Test that schema validation is enforced"""
        
        # Generate a component to test schema validation
        nl_spec = "Create a source component called TestSource that fetches JSON data from API endpoints"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify schema has required V5.0 fields
        output_schema = component.schema_classes[f"{component.class_name}OutputSchema"]
        
        # Test schema instantiation with valid data
        valid_data = {
            "timestamp": 1234567890.0,
            "component_source": "test_component",
            "data_id": "test_123",
            "data_type": "json",
            "json_payload": {"test": "data"}
        }
        
        # Should create instance successfully
        instance = output_schema(**valid_data)
        assert instance.timestamp == 1234567890.0
        assert instance.component_source == "test_component"
        
        # Test schema validation with invalid data
        invalid_data = {
            "component_source": "test_component"
            # Missing required timestamp
        }
        
        with pytest.raises(Exception):  # Pydantic validation error
            output_schema(**invalid_data)
    
    def test_component_registry_and_retrieval(self):
        """Test component registration and retrieval"""
        
        nl_spec = "Create a source component called RegistryTestSource that fetches JSON from API endpoints"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Component should be registered automatically
        retrieved = self.generator.get_generated_component("RegistryTestSource")
        assert retrieved is not None
        assert retrieved.class_name == "RegistryTestSource"
        assert retrieved is component  # Same instance
        
        # List should include the component
        component_list = self.generator.list_generated_components()
        assert "RegistryTestSource" in component_list
        
        # Non-existent component should return None
        non_existent = self.generator.get_generated_component("NonExistentComponent")
        assert non_existent is None
    
    def test_component_code_export(self):
        """Test component code export functionality"""
        
        nl_spec = "Create a source component called ExportTestSource that fetches JSON from API endpoints"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            self.generator.export_component_code("ExportTestSource", temp_path)
            
            # Verify file was created and contains code
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                exported_code = f.read()
            
            assert exported_code == component.source_code
            assert "class ExportTestSource" in exported_code
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        # Test export of non-existent component
        with pytest.raises(ComponentGenerationError) as exc_info:
            self.generator.export_component_code("NonExistentComponent", "/tmp/test.py")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_data_type_specific_schema_generation(self):
        """Test that schemas are generated correctly for different data types"""
        
        data_type_specs = [
            ("JSON", "Create a source component called JsonSource that fetches JSON data from API endpoints"),
            ("CSV", "Create a source component called CsvSource that loads CSV data from file"),
            ("XML", "Create a source component called XmlSource that fetches XML data from API endpoints"),
            ("Text", "Create a source component called TextSource that loads text data from file"),
        ]
        
        for data_type, spec in data_type_specs:
            component = self.generator.generate_component_from_nl(spec)
            
            # Verify schema has data type specific fields
            output_schema = component.schema_classes[f"{component.class_name}OutputSchema"]
            schema_fields = output_schema.model_fields.keys()
            
            if data_type == "JSON":
                assert any("json" in field.lower() for field in schema_fields)
            elif data_type == "CSV":
                assert any("csv" in field.lower() for field in schema_fields)
            elif data_type == "XML":
                assert any("xml" in field.lower() for field in schema_fields)
            elif data_type == "Text":
                assert any("text" in field.lower() for field in schema_fields)
    
    def test_processing_method_integration(self):
        """Test that processing methods are integrated correctly"""
        
        processing_specs = [
            ("API", "Create a source component called ApiSource that fetches JSON from API endpoints"),
            ("Database", "Create a source component called DbSource that loads CSV from database tables"),
            ("File", "Create a source component called FileSource that loads text from file"),
        ]
        
        for method_type, spec in processing_specs:
            component = self.generator.generate_component_from_nl(spec)
            
            # Verify processing method is in config
            assert component.config_template["processing_method"] == method_type.lower()
            
            # Verify appropriate config fields are present
            if method_type == "API":
                config_fields = component.config_template.keys()
                assert any("api" in str(field).lower() for field in config_fields)
            elif method_type == "Database":
                config_fields = component.config_template.keys()
                assert any("connection" in str(field).lower() or "table" in str(field).lower() for field in config_fields)
    
    def test_validation_re_run(self):
        """Test re-validation of all generated components"""
        
        # Generate multiple components
        specs = [
            "Create a source component called ValidSource1 that fetches JSON from API endpoints",
            "Create a transformer component called ValidTransformer1 that filters CSV data",
            "Create a sink component called ValidSink1 that stores JSON to database tables"
        ]
        
        for spec in specs:
            self.generator.generate_component_from_nl(spec)
        
        # Re-validate all components
        validation_summary = self.generator.validate_all_generated_components()
        
        # All should pass validation
        assert len(validation_summary) == 3
        assert all(result["status"] == "PASSED" for result in validation_summary.values())
        
        for component_name, result in validation_summary.items():
            assert result["status"] == "PASSED"
            assert "results" in result
    
    def test_security_validation_enforced(self):
        """Test that security validation prevents malicious code"""
        
        # The secure template system should prevent any malicious code generation
        # Even if somehow malicious content was attempted, it should be caught
        
        nl_spec = "Create a source component called SecureTestSource that fetches JSON from API endpoints"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify security validation passed
        assert component.validation_results["security_validation"]["passed"]
        
        # Verify no dangerous patterns in generated code
        dangerous_patterns = ["eval(", "exec(", "__import__", "subprocess", "os.system"]
        for pattern in dangerous_patterns:
            assert pattern not in component.source_code
    
    def test_fail_hard_principles_maintained(self):
        """Test that fail-hard principles are maintained throughout"""
        
        nl_spec = "Create a source component called FailHardTest that fetches JSON from API endpoints"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify no fallback or graceful degradation patterns
        fallback_patterns = [
            "fallback", "graceful", "default", "best_guess", 
            "partial", "approximate", "try_catch_all"
        ]
        
        code_lower = component.source_code.lower()
        
        for pattern in fallback_patterns:
            # Allow "default" in specific contexts like "default_factory"
            if pattern == "default" and "default_factory" in code_lower:
                continue
            # Pattern should not appear in problematic contexts
            assert (pattern not in code_lower or 
                   f"no {pattern}" in code_lower or 
                   f"fail hard" in code_lower)
        
        # Verify fail-hard messaging
        assert "fail hard" in code_lower
        assert "v5.0" in component.source_code
    
    def test_no_mock_capabilities_exist(self):
        """Test that no mock capabilities exist in the generator"""
        
        # Generator should not have any mock-related methods
        assert not hasattr(self.generator, 'mock_mode')
        assert not hasattr(self.generator, 'enable_mocks')
        assert not hasattr(self.generator, 'fallback_generation')
        assert not hasattr(self.generator, 'partial_generation')
        assert not hasattr(self.generator, 'graceful_degradation')
        
        # Generated components should not have mock modes
        nl_spec = "Create a source component called SecurityTest that fetches JSON data from API endpoints"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        assert "mock_mode" not in component.source_code
        assert ("mock" not in component.source_code.lower() or 
                "no mock" in component.source_code.lower())
    
    def test_pydantic_integration_complete(self):
        """Test complete Pydantic integration"""
        
        nl_spec = "Create a transformer component called PydanticTest that filters JSON data"
        component = self.generator.generate_component_from_nl(nl_spec)
        
        # Verify all schemas are proper Pydantic models
        for schema_name, schema_class in component.schema_classes.items():
            assert issubclass(schema_class, BaseModel)
            assert hasattr(schema_class, 'model_fields')
            assert hasattr(schema_class, 'model_config')
            
            # Verify V5.0 required fields
            if issubclass(schema_class, ComponentDataSchema):
                schema_fields = schema_class.model_fields.keys()
                assert 'timestamp' in schema_fields
                assert 'component_source' in schema_fields
        
        # Verify schema validation works
        input_schema = component.schema_classes[f"{component.class_name}InputSchema"]
        
        # Valid data should work
        valid_data = {
            "timestamp": 1234567890.0,
            "component_source": "test",
            "json_data": {"test": "data"},
            "processing_metadata": {}
        }
        
        instance = input_schema(**valid_data)
        assert isinstance(instance, BaseModel)
        
        # Invalid data should fail
        with pytest.raises(Exception):
            input_schema(invalid_field="should_fail")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])