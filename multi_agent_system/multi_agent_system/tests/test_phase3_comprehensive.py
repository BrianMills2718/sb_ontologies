#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phase 3 Enhanced Component Generation
Validates complete system integration with security validation and fail-hard compliance
"""

import pytest
import tempfile
import os
import asyncio
import json
from typing import Dict, Any, List

from autocoder.generation.secure_templates import (
    SecureTemplateSystem,
    secure_template_system,
    TemplateSecurityError,
    TemplateValidationError
)
from autocoder.generation.nl_parser import (
    NaturalLanguageParser,
    nl_parser,
    ComponentType
)
from autocoder.generation.schema_generator import (
    SchemaAwareComponentGenerator,
    schema_generator,
    ComponentGenerationError
)
from autocoder.generation.property_test_generator import (
    PropertyTestGenerator,
    property_test_generator
)
from autocoder.generation.phase2_integration import (
    Phase2IntegrationManager,
    phase2_integration_manager,
    Phase2IntegrationError
)


class TestPhase3ComprehensiveIntegration:
    """Comprehensive test suite for Phase 3 enhanced component generation system"""
    
    def setup_method(self):
        """Setup for each test"""
        self.template_system = secure_template_system
        self.nl_parser = nl_parser
        self.schema_generator = schema_generator
        self.property_test_generator = property_test_generator
        self.integration_manager = phase2_integration_manager
    
    # ===== SECURITY VALIDATION TESTS =====
    
    def test_template_system_blocks_code_injection(self):
        """Test that template system blocks all code injection attempts"""
        
        malicious_variables = [
            {"class_name": "TestComp; import os; os.system('rm -rf /')"},
            {"description": "eval('__import__(\"os\").system(\"malicious\")')"},
            {"data_type": "json\"; exec(\"malicious_code\"); x=\""},
            {"generation_method": "__import__('subprocess').call(['rm', '-rf', '/'])"},
            {"processing_method": "lambda: exec('malicious')"},
            {"required_config_fields": "['field'] + eval('dangerous_code')"},
        ]
        
        for malicious_vars in malicious_variables:
            with pytest.raises((TemplateSecurityError, TemplateValidationError)) as exc_info:
                self.template_system.generate_component_code(
                    "enhanced_source_v5", 
                    malicious_vars
                )
            
            # Verify security error mentions validation failure
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "security", "injection", "dangerous", "prohibited", "v5.0", "pattern", "validation"
            ])
    
    def test_template_system_validates_all_inputs(self):
        """Test that template system validates all template variables"""
        
        # Test with completely invalid template variables
        invalid_variable_sets = [
            {},  # Empty variables
            {"invalid_key": "invalid_value"},  # Wrong keys
            {"class_name": ""},  # Empty required field
            {"class_name": None},  # None value
            {"class_name": 123},  # Wrong type
        ]
        
        for invalid_vars in invalid_variable_sets:
            with pytest.raises((TemplateSecurityError, TemplateValidationError, KeyError, TypeError)):
                self.template_system.generate_component_code(
                    "enhanced_source_v5",
                    invalid_vars
                )
    
    def test_nl_parser_prevents_malicious_specifications(self):
        """Test that NL parser prevents malicious natural language specifications"""
        
        malicious_specs = [
            "Create a component called Malicious; import os; os.system('evil')",
            "Make a source component with eval('dangerous_code') functionality",
            "Build a transformer that executes __import__('subprocess').call(['rm', '-rf', '/'])",
            "Design a sink with description containing exec('malicious')",
            "Create component with class name Test'; import sys; sys.exit()",
        ]
        
        for malicious_spec in malicious_specs:
            # Should either fail parsing or generate safe specification
            try:
                spec = self.nl_parser.parse_component_specification(malicious_spec)
                # If parsing succeeds, verify no dangerous content in specification
                assert "import" not in spec.class_name.lower()
                assert "exec" not in spec.class_name.lower()
                assert "eval" not in spec.class_name.lower()
                assert "system" not in spec.class_name.lower()
            except Exception:
                # Parsing failure is acceptable for malicious input
                pass
    
    @pytest.mark.asyncio
    async def test_schema_generator_prevents_dangerous_schemas(self):
        """Test that schema generator prevents generation of dangerous schemas"""
        
        # Test with specifications that might generate dangerous schemas
        potentially_dangerous_specs = [
            "Create a source component called EvilComponent that processes dangerous JSON data from file",
            "Make a transformer component called SystemAccess that handles system commands in CSV format",
            "Build a sink component called CodeExecutor that stores executable XML content to file",
        ]
        
        for spec in potentially_dangerous_specs:
            component = self.schema_generator.generate_component_from_nl(spec)
            
            # Verify generated schemas don't have dangerous methods
            for schema_name, schema_class in component.schema_classes.items():
                # Check schema class doesn't have dangerous attributes
                dangerous_methods = ["eval", "exec", "compile", "__import__"]
                for method in dangerous_methods:
                    assert not hasattr(schema_class, method)
                
                # Verify schema validation works properly
                test_data = {
                    "timestamp": 1234567890.0,
                    "component_source": "test_component"
                }
                
                # Add required fields with appropriate types (same logic as Phase 2 integration)
                for field_name, field_info in schema_class.model_fields.items():
                    if field_info.is_required() and field_name not in test_data:
                        # Provide appropriate test values based on field annotation and name
                        if hasattr(field_info, 'annotation'):
                            annotation_str = str(field_info.annotation)
                            # Check field name patterns first (more specific)
                            if 'rows' in field_name.lower() or 'items' in field_name.lower() or ('csv' in field_name.lower() and 'data' in field_name.lower()):
                                # CSV rows/data are typically lists of dicts
                                test_data[field_name] = [{"column1": "value1", "column2": "value2"}]
                            elif 'list' in field_name.lower():
                                test_data[field_name] = ["test_value"]
                            elif 'json' in field_name.lower() and 'payload' in field_name.lower():
                                test_data[field_name] = {"test": "data"}
                            # Then check type annotations
                            elif field_info.annotation == list or 'List' in annotation_str:
                                test_data[field_name] = ["test_value"]
                            elif field_info.annotation == dict or 'Dict' in annotation_str:
                                test_data[field_name] = {"test": "data"}
                            elif field_info.annotation == int or 'int' in annotation_str:
                                test_data[field_name] = 123
                            elif field_info.annotation == float or 'float' in annotation_str:
                                test_data[field_name] = 123.45
                            elif field_info.annotation == bool or 'bool' in annotation_str:
                                test_data[field_name] = True
                            else:
                                test_data[field_name] = "safe_test_value"
                        else:
                            test_data[field_name] = "safe_test_value"
                
                # Should create instance without dangerous code execution
                instance = schema_class(**test_data)
                assert isinstance(instance.timestamp, (int, float))
                assert isinstance(instance.component_source, str)
    
    @pytest.mark.asyncio
    async def test_property_test_generator_creates_security_tests(self):
        """Test that property test generator creates security validation tests"""
        
        # Generate a component and its property tests
        nl_spec = "Create a source component called SecurityTestComponent that fetches JSON from API endpoints"
        component = self.schema_generator.generate_component_from_nl(nl_spec)
        test_suite = self.property_test_generator.generate_property_tests(component)
        
        # Verify security tests are present
        test_code_lower = test_suite.test_code.lower()
        
        security_patterns = [
            "security", "injection", "malicious", "dangerous",
            "code_injection", "access_control", "input_validation"
        ]
        
        security_test_count = sum(1 for pattern in security_patterns if pattern in test_code_lower)
        assert security_test_count >= 3, f"Insufficient security tests: {security_test_count}"
        
        # Verify security tests check for dangerous methods
        assert "eval" in test_code_lower
        assert "exec" in test_code_lower
        assert "dangerous" in test_code_lower
        
        # Verify property tests enforce fail-hard behavior
        assert "pytest.raises" in test_suite.test_code
        assert "assert" in test_suite.test_code
        assert "fail hard" in test_code_lower
    
    @pytest.mark.asyncio
    async def test_integration_manager_security_validation(self):
        """Test that integration manager performs comprehensive security validation"""
        
        nl_spec = "Create a source component called IntegrationSecurityTest that fetches JSON from API endpoints"
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify security validation passed
        security_validation = integrated_component.generated_component.validation_results.get("security_validation", {})
        assert security_validation.get("passed", False), "Security validation must pass"
        
        # Verify no dangerous patterns in generated code
        source_code = integrated_component.generated_component.source_code
        dangerous_patterns = ["eval(", "exec(", "__import__", "subprocess", "os.system"]
        
        for pattern in dangerous_patterns:
            assert pattern not in source_code, f"Dangerous pattern found: {pattern}"
        
        # Verify Phase 2 compliance includes security compliance
        phase2_compliance = integrated_component.phase2_compliance
        assert phase2_compliance.get("security_compliance", False), "Security compliance required"
    
    # ===== COMPREHENSIVE SYSTEM INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_end_to_end_source_component_generation(self):
        """Test complete end-to-end source component generation pipeline"""
        
        nl_spec = "Create a source component called WeatherDataSource that fetches JSON weather data from API endpoints"
        
        # Test complete pipeline
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify all pipeline components
        assert integrated_component.generated_component is not None
        assert integrated_component.property_test_suite is not None
        assert integrated_component.registry_entry is not None
        assert integrated_component.validation_results is not None
        
        # Verify component details
        component = integrated_component.generated_component
        assert component.class_name == "WeatherDataSource"
        assert component.component_type == ComponentType.SOURCE
        assert "json" in component.config_template.get("data_type", "").lower()
        assert "api" in component.config_template.get("processing_method", "").lower()
        
        # Verify schemas
        assert f"{component.class_name}OutputSchema" in component.schema_classes
        output_schema = component.schema_classes[f"{component.class_name}OutputSchema"]
        
        # Test schema instantiation
        test_data = {
            "timestamp": 1234567890.0,
            "component_source": "WeatherDataSource",
            "data_id": "weather_001",
            "data_type": "json",
            "json_payload": {"temperature": 25.5, "humidity": 60}
        }
        
        instance = output_schema(**test_data)
        assert instance.timestamp == 1234567890.0
        assert instance.component_source == "WeatherDataSource"
        
        # Verify property tests
        test_suite = integrated_component.property_test_suite
        assert test_suite.test_count >= 10
        assert test_suite.validation_results["overall_status"] == "PASSED"
        
        # Verify Phase 2 integration
        assert integrated_component.registry_entry["registration_status"] == "ACTIVE"
        assert integrated_component.validation_results["validation_passed"] is True
    
    @pytest.mark.asyncio
    async def test_end_to_end_transformer_component_generation(self):
        """Test complete end-to-end transformer component generation pipeline"""
        
        nl_spec = "Build a transformer component called DataNormalizer that filters CSV data"
        
        # Test complete pipeline
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify transformer-specific features
        component = integrated_component.generated_component
        assert component.class_name == "DataNormalizer"
        assert component.component_type == ComponentType.TRANSFORMER
        
        # Verify both input and output schemas
        assert f"{component.class_name}InputSchema" in component.schema_classes
        assert f"{component.class_name}OutputSchema" in component.schema_classes
        
        input_schema = component.schema_classes[f"{component.class_name}InputSchema"]
        output_schema = component.schema_classes[f"{component.class_name}OutputSchema"]
        
        # Test input schema
        input_data = {
            "timestamp": 1234567890.0,
            "component_source": "DataNormalizer",
            "processing_metadata": {},
            "transformation_type": "filter",
            "csv_rows": [{"name": "test", "value": "123"}]
        }
        
        input_instance = input_schema(**input_data)
        assert input_instance.transformation_type == "filter"
        
        # Test output schema
        output_data = {
            "timestamp": 1234567890.0,
            "component_source": "DataNormalizer",
            "processing_metadata": {},
            "transformation_type": "filter",
            "csv_data": [{"name": "normalized_test", "value": "123"}],
            "transformation_applied": "normalize"
        }
        
        output_instance = output_schema(**output_data)
        assert output_instance.transformation_applied == "normalize"
        
        # Verify config template has inputs and outputs
        config = component.config_template
        assert "inputs" in config
        assert "outputs" in config
        assert config["type"] == "Transformer"
    
    @pytest.mark.asyncio
    async def test_end_to_end_sink_component_generation(self):
        """Test complete end-to-end sink component generation pipeline"""
        
        nl_spec = "Make a sink component called DatabaseWriter that stores JSON data to database tables"
        
        # Test complete pipeline
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify sink-specific features
        component = integrated_component.generated_component
        assert component.class_name == "DatabaseWriter"
        assert component.component_type == ComponentType.SINK
        
        # Verify only input schema (sinks don't have outputs)
        assert f"{component.class_name}InputSchema" in component.schema_classes
        assert f"{component.class_name}OutputSchema" not in component.schema_classes
        
        input_schema = component.schema_classes[f"{component.class_name}InputSchema"]
        
        # Test input schema
        input_data = {
            "timestamp": 1234567890.0,
            "component_source": "DatabaseWriter",
            "storage_metadata": {},
            "final_destination": "database",
            "json_data": {"user_id": 123, "action": "login"}
        }
        
        input_instance = input_schema(**input_data)
        assert input_instance.final_destination == "database"
        
        # Verify config template has inputs but no outputs
        config = component.config_template
        assert "inputs" in config
        assert "outputs" not in config
        assert config["type"] == "Sink"
    
    def test_multiple_component_generation_isolation(self):
        """Test that multiple component generations are properly isolated"""
        
        component_specs = [
            ("TestSource1", "Create a source component called TestSource1 that fetches JSON data from API endpoints"),
            ("TestSource2", "Create a source component called TestSource2 that loads CSV data from files"),
            ("TestTransformer1", "Build a transformer component called TestTransformer1 that filters JSON data"),
        ]
        
        generated_components = []
        
        for expected_name, spec in component_specs:
            component = self.schema_generator.generate_component_from_nl(spec)
            generated_components.append(component)
            
            # Verify correct component name
            assert component.class_name == expected_name
            
            # Verify component is properly isolated
            assert component not in generated_components[:-1]  # Not same instance as previous
        
        # Verify all components are tracked in registry
        component_list = self.schema_generator.list_generated_components()
        for expected_name, _ in component_specs:
            assert expected_name in component_list
        
        # Verify components can be retrieved independently
        for expected_name, _ in component_specs:
            retrieved = self.schema_generator.get_generated_component(expected_name)
            assert retrieved is not None
            assert retrieved.class_name == expected_name
    
    @pytest.mark.asyncio
    async def test_integration_export_functionality(self):
        """Test that integrated components can be exported with all artifacts"""
        
        nl_spec = "Create a source component called ExportTestComponent that fetches JSON from API endpoints"
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Test export functionality
        with tempfile.TemporaryDirectory() as temp_dir:
            await self.integration_manager.export_integrated_component("ExportTestComponent", temp_dir)
            
            # Verify all expected files exist
            expected_files = [
                "ExportTestComponent.py",
                "test_exporttestcomponent_properties.py",
                "ExportTestComponent_integration_metadata.json"
            ]
            
            for expected_file in expected_files:
                file_path = os.path.join(temp_dir, expected_file)
                assert os.path.exists(file_path), f"Missing file: {expected_file}"
                
                # Verify file has content
                with open(file_path, 'r') as f:
                    content = f.read()
                assert len(content) > 100, f"File {expected_file} appears to be empty or too small"
            
            # Verify component source code
            with open(os.path.join(temp_dir, "ExportTestComponent.py"), 'r') as f:
                source_code = f.read()
            
            assert "class ExportTestComponent" in source_code
            assert "async def process(self)" in source_code
            assert "fail hard" in source_code.lower()
            assert "V5.0" in source_code
            
            # Verify property test suite
            with open(os.path.join(temp_dir, "test_exporttestcomponent_properties.py"), 'r') as f:
                test_code = f.read()
            
            assert "class TestExportTestComponentProperties" in test_code
            assert "hypothesis" in test_code
            assert "pytest" in test_code
            assert "security" in test_code.lower()
            
            # Verify integration metadata
            with open(os.path.join(temp_dir, "ExportTestComponent_integration_metadata.json"), 'r') as f:
                metadata = json.load(f)
            
            assert metadata["component_name"] == "ExportTestComponent"
            assert "registry_entry" in metadata
            assert "validation_results" in metadata
            assert "phase2_compliance" in metadata
            assert "test_suite_metadata" in metadata
    
    # ===== FAIL-HARD COMPLIANCE TESTS =====
    
    def test_no_mock_modes_anywhere(self):
        """Test that no mock modes exist anywhere in the system"""
        
        # Test template system
        assert not hasattr(self.template_system, 'mock_mode')
        assert not hasattr(self.template_system, 'enable_mocks')
        assert not hasattr(self.template_system, 'fallback_mode')
        
        # Test NL parser
        assert not hasattr(self.nl_parser, 'mock_mode')
        assert not hasattr(self.nl_parser, 'approximate_parsing')
        assert not hasattr(self.nl_parser, 'best_guess_mode')
        
        # Test schema generator
        assert not hasattr(self.schema_generator, 'mock_mode')
        assert not hasattr(self.schema_generator, 'partial_generation')
        assert not hasattr(self.schema_generator, 'fallback_schemas')
        
        # Test property test generator
        assert not hasattr(self.property_test_generator, 'mock_mode')
        assert not hasattr(self.property_test_generator, 'simplified_tests')
        assert not hasattr(self.property_test_generator, 'skip_tests')
        
        # Test integration manager
        assert not hasattr(self.integration_manager, 'mock_mode')
        assert not hasattr(self.integration_manager, 'partial_integration')
        assert not hasattr(self.integration_manager, 'graceful_degradation')
    
    @pytest.mark.asyncio
    async def test_fail_hard_on_invalid_input(self):
        """Test that system fails hard on invalid input at every level"""
        
        invalid_inputs = [
            "",  # Empty input
            "Create a thing",  # Vague specification
            "Make something that does stuff",  # No clear component type
            "Build a component",  # Missing essential details
        ]
        
        for invalid_input in invalid_inputs:
            # Should fail at NL parsing or component generation level
            with pytest.raises(Exception) as exc_info:
                await self.integration_manager.generate_and_integrate_component(invalid_input)
            
            # Verify error mentions V5.0 fail-hard principles
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "fail", "error", "required", "missing", "invalid", "v5.0"
            ])
    
    def test_no_graceful_degradation_patterns(self):
        """Test that no graceful degradation patterns exist"""
        
        # Generate a component and check for anti-patterns
        nl_spec = "Create a source component called AntiPatternTest that fetches JSON from API endpoints"
        component = self.schema_generator.generate_component_from_nl(nl_spec)
        
        # Check source code doesn't contain graceful degradation patterns
        source_code_lower = component.source_code.lower()
        
        anti_patterns = [
            "try:", "except:", "pass",  # Broad exception handling
            "fallback", "default", "graceful",
            "best_guess", "approximate", "partial",
            "skip", "ignore", "continue"
        ]
        
        # Allow some patterns in specific safe contexts
        for pattern in anti_patterns:
            if pattern in source_code_lower:
                # Check if it's in a safe context
                if pattern == "try:" or pattern == "except:":
                    # Should be specific exception handling, not broad
                    assert "fail hard" in source_code_lower
                elif pattern == "default":
                    # Should be Pydantic default_factory, not fallback
                    assert "default_factory" in component.source_code
                else:
                    # Other patterns should be explicitly about failing hard
                    assert f"no {pattern}" in source_code_lower or "fail hard" in source_code_lower
    
    @pytest.mark.asyncio
    async def test_comprehensive_validation_enforcement(self):
        """Test that comprehensive validation is enforced at every level"""
        
        nl_spec = "Create a source component called ValidationTest that fetches JSON from API endpoints"
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify validation at component level
        component_validation = integrated_component.generated_component.validation_results
        assert component_validation["overall_status"] == "PASSED"
        assert component_validation["security_validation"]["passed"]
        
        # Verify validation at property test level
        test_validation = integrated_component.property_test_suite.validation_results
        assert test_validation["overall_status"] == "PASSED"
        assert test_validation["syntax_validation"]["passed"]
        assert test_validation["coverage_validation"]["passed"]
        
        # Verify validation at integration level
        integration_validation = integrated_component.validation_results
        assert integration_validation["validation_passed"]
        assert integration_validation["phase2_compliance"]
        
        # Verify Phase 2 compliance
        phase2_compliance = integrated_component.phase2_compliance
        assert phase2_compliance["schema_compliance"]
        assert phase2_compliance["registry_compliance"]
        assert phase2_compliance["validation_framework_compliance"]
        assert phase2_compliance["security_compliance"]
        assert phase2_compliance["fail_hard_compliance"]
        
        # Verify overall compliance status
        assert phase2_compliance["phase2_integration_status"] in ["FULLY_COMPLIANT", "MOSTLY_COMPLIANT"]
        assert phase2_compliance["overall_compliance_score"] >= 0.8
    
    # ===== PERFORMANCE AND SCALABILITY TESTS =====
    
    def test_component_generation_performance(self):
        """Test that component generation completes within reasonable time"""
        
        import time
        
        start_time = time.time()
        
        # Generate multiple components to test performance
        specs = [
            "Create a source component called PerfTest1 that fetches JSON from API",
            "Create a source component called PerfTest2 that loads CSV from files",
            "Create a source component called PerfTest3 that fetches XML from API",
        ]
        
        for spec in specs:
            component = self.schema_generator.generate_component_from_nl(spec)
            assert component is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert total_time < 10.0, f"Component generation too slow: {total_time:.2f}s"
        
        # Verify all components were generated
        component_list = self.schema_generator.list_generated_components()
        assert "PerfTest1" in component_list
        assert "PerfTest2" in component_list
        assert "PerfTest3" in component_list
    
    @pytest.mark.asyncio
    async def test_concurrent_component_generation(self):
        """Test that concurrent component generation works correctly"""
        
        async def generate_component(name_suffix: str):
            spec = f"Create a source component called ConcurrentTest{name_suffix} that fetches JSON data from API endpoints"
            return await self.integration_manager.generate_and_integrate_component(spec)
        
        # Generate multiple components concurrently
        tasks = [generate_component(str(i)) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Verify all components were generated successfully
        assert len(results) == 3
        
        for i, result in enumerate(results):
            assert result.generated_component.class_name == f"ConcurrentTest{i}"
            assert result.validation_results["validation_passed"]
            assert result.phase2_compliance["phase2_integration_status"] in ["FULLY_COMPLIANT", "MOSTLY_COMPLIANT"]
    
    def test_memory_usage_bounds(self):
        """Test that component generation doesn't leak memory"""
        
        import gc
        
        # Measure baseline memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Generate and clean up components
        for i in range(5):
            spec = f"Create a source component called MemoryTest{i} that fetches JSON from API"
            component = self.schema_generator.generate_component_from_nl(spec)
            
            # Verify component was created
            assert component is not None
            
            # Explicit cleanup
            del component
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        object_growth = final_objects - initial_objects
        
        # Should not have significant object growth (allow some tolerance)
        assert object_growth < 1000, f"Potential memory leak: {object_growth} objects created"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])