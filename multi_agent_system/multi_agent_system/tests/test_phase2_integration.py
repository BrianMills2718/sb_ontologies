#!/usr/bin/env python3
"""
Test Suite for Phase 2 Integration Manager
Validates integration between Phase 3 generation and Phase 2 systems
"""

import pytest
import tempfile
import os
import asyncio
from typing import Dict, Any

from autocoder.generation.phase2_integration import (
    Phase2IntegrationManager,
    IntegratedGeneratedComponent,
    Phase2IntegrationError
)
from autocoder.generation.schema_generator import GeneratedComponent
from autocoder.generation.nl_parser import ComponentType
from autocoder.validation.schema_framework import ComponentDataSchema


class TestPhase2IntegrationManager:
    """Test Phase 2 integration manager with fail-hard validation"""
    
    def setup_method(self):
        """Setup for each test"""
        self.integration_manager = Phase2IntegrationManager()
    
    @pytest.mark.asyncio
    async def test_successful_component_integration(self):
        """Test successful end-to-end component integration"""
        
        nl_spec = "Create a source component called IntegratedTestSource that fetches JSON data from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify integrated component structure
        assert isinstance(integrated_component, IntegratedGeneratedComponent)
        assert integrated_component.generated_component.class_name == "IntegratedTestSource"
        assert integrated_component.generated_component.component_type == ComponentType.SOURCE
        
        # Verify property test suite
        assert integrated_component.property_test_suite is not None
        assert integrated_component.property_test_suite.test_count >= 10
        assert integrated_component.property_test_suite.validation_results["overall_status"] == "PASSED"
        
        # Verify registry integration
        assert integrated_component.registry_entry["registration_status"] == "ACTIVE"
        assert integrated_component.registry_entry["phase2_registry_compliance"] is True
        
        # Verify validation results
        assert integrated_component.validation_results["validation_passed"] is True
        assert integrated_component.validation_results["phase2_compliance"] is True
        
        # Verify Phase 2 compliance
        assert integrated_component.phase2_compliance["phase2_integration_status"] == "FULLY_COMPLIANT"
        assert integrated_component.phase2_compliance["overall_compliance_score"] >= 0.95
    
    @pytest.mark.asyncio
    async def test_transformer_component_integration(self):
        """Test transformer component integration with input/output schemas"""
        
        nl_spec = "Build a transformer component called DataProcessor that filters CSV data based on conditions"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify transformer-specific integration
        assert integrated_component.generated_component.component_type == ComponentType.TRANSFORMER
        
        # Verify both input and output schemas
        schemas = integrated_component.generated_component.schema_classes
        assert any("Input" in name for name in schemas.keys())
        assert any("Output" in name for name in schemas.keys())
        
        # Verify schema relationships validation
        relationship_validation = integrated_component.validation_results.get("schema_relationships", {})
        assert relationship_validation.get("input_output_compatibility", False)
        assert relationship_validation.get("component_type_alignment", False)
        assert relationship_validation.get("phase2_schema_inheritance", False)
    
    @pytest.mark.asyncio
    async def test_sink_component_integration(self):
        """Test sink component integration with input-only schemas"""
        
        nl_spec = "Make a sink component called DataStore that stores JSON data to database tables"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify sink-specific integration
        assert integrated_component.generated_component.component_type == ComponentType.SINK
        
        # Verify only input schema
        schemas = integrated_component.generated_component.schema_classes
        assert any("Input" in name for name in schemas.keys())
        assert not any("Output" in name for name in schemas.keys())
        
        # Verify config template structure
        config = integrated_component.generated_component.config_template
        assert "inputs" in config
        assert "outputs" not in config
    
    @pytest.mark.asyncio
    async def test_schema_validation_with_phase2_framework(self):
        """Test schema validation against Phase 2 framework"""
        
        nl_spec = "Create a source component called SchemaTestSource that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify all schemas pass Phase 2 validation
        schema_validation = integrated_component.validation_results.get("schema_validation", {})
        
        for schema_name, result in schema_validation.items():
            if isinstance(result, dict) and "phase2_compatible" in result:
                assert result["phase2_compatible"] is True
                assert result["validation_passed"] is True
                assert result["compliance_score"] >= 0.9
        
        # Verify schemas inherit from Phase 2 base classes
        for schema_name, schema_class in integrated_component.generated_component.schema_classes.items():
            assert issubclass(schema_class, ComponentDataSchema)
            
            # Verify required Phase 2 fields
            schema_fields = schema_class.model_fields.keys()
            assert 'timestamp' in schema_fields
            assert 'component_source' in schema_fields
    
    @pytest.mark.asyncio
    async def test_component_registry_integration(self):
        """Test component registration with Phase 2 registry"""
        
        nl_spec = "Create a source component called RegistryTestSource that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify component is registered
        assert integrated_component.registry_entry["registration_status"] == "ACTIVE"
        assert "registration_id" in integrated_component.registry_entry
        assert "registration_timestamp" in integrated_component.registry_entry
        
        # Verify component can be retrieved from registry
        retrieved_component = await self.integration_manager.component_registry.get_component("RegistryTestSource")
        assert retrieved_component is not None
        
        # Verify registry metadata
        registry_metadata = integrated_component.registry_entry["registry_metadata"]
        assert registry_metadata is not None
        
        # Verify registration data completeness
        registration_data = registry_metadata.get("registration_data", {})
        assert registration_data.get("component_name") == "RegistryTestSource"
        assert registration_data.get("component_type") == "source"
        assert "schema_definitions" in registration_data
        assert "config_template" in registration_data
    
    @pytest.mark.asyncio
    async def test_property_test_phase2_compliance(self):
        """Test property test suite meets Phase 2 requirements"""
        
        nl_spec = "Create a source component called PropertyTestSource that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify property test compliance
        test_validation = integrated_component.validation_results.get("property_test_validation", {})
        
        assert test_validation.get("test_count_adequate", False)
        assert test_validation.get("coverage_adequate", False)
        assert test_validation.get("fail_hard_tests_present", False)
        assert test_validation.get("phase2_integration_tests", False)
        assert test_validation.get("security_tests_present", False)
        assert test_validation.get("compliance_score", 0.0) >= 0.8
        
        # Verify test suite contains Phase 2 integration patterns
        test_code = integrated_component.property_test_suite.test_code.lower()
        phase2_patterns = ["componentdataschema", "componentregistry", "validationframework"]
        assert any(pattern in test_code for pattern in phase2_patterns)
    
    @pytest.mark.asyncio
    async def test_validation_framework_integration(self):
        """Test integration with Phase 2 validation framework"""
        
        nl_spec = "Create a source component called ValidationTestSource that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify validation framework results
        validation_results = integrated_component.validation_results
        
        assert validation_results["validation_passed"] is True
        assert validation_results["phase2_compliance"] is True
        assert validation_results["validation_score"] >= 0.95
        
        # Verify no warnings or errors in strict mode
        assert not validation_results.get("warnings", [])
        assert not validation_results.get("errors", [])
        
        # Verify rule results
        rule_results = validation_results.get("rule_results", {})
        assert rule_results  # Should have rule validation results
    
    @pytest.mark.asyncio
    async def test_integration_completeness_validation(self):
        """Test integration completeness validation"""
        
        nl_spec = "Create a source component called CompletenessTestSource that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify all integration aspects are complete
        assert integrated_component.generated_component is not None
        assert integrated_component.property_test_suite is not None
        assert integrated_component.registry_entry["registration_status"] == "ACTIVE"
        assert integrated_component.validation_results["validation_passed"] is True
        assert integrated_component.phase2_compliance["phase2_integration_status"] == "FULLY_COMPLIANT"
        
        # Verify test count is adequate
        assert integrated_component.property_test_suite.test_count >= 10
        
        # Verify no security violations
        security_validation = integrated_component.generated_component.validation_results.get("security_validation", {})
        assert security_validation.get("passed", False)
    
    @pytest.mark.asyncio
    async def test_invalid_component_fails_integration(self):
        """Test that invalid components fail integration hard"""
        
        invalid_specs = [
            "",  # Empty specification
            "Create a thing that does stuff",  # No clear component specification
            "Make a component called TestComp",  # Missing component type and data type
        ]
        
        for invalid_spec in invalid_specs:
            with pytest.raises((Phase2IntegrationError, Exception)) as exc_info:
                await self.integration_manager.generate_and_integrate_component(invalid_spec)
            
            # Should fail hard, not partial integration
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in [
                "fail", "error", "required", "missing", "invalid", "v5.0"
            ])
    
    @pytest.mark.asyncio
    async def test_component_retrieval_and_listing(self):
        """Test component retrieval and listing functionality"""
        
        # Generate multiple components
        specs = [
            "Create a source component called RetrievalTest1 that fetches JSON from API endpoints",
            "Build a transformer component called RetrievalTest2 that filters CSV data",
            "Make a sink component called RetrievalTest3 that stores JSON to database tables"
        ]
        
        for spec in specs:
            await self.integration_manager.generate_and_integrate_component(spec)
        
        # Test component retrieval
        component1 = self.integration_manager.get_integrated_component("RetrievalTest1")
        assert component1 is not None
        assert component1.generated_component.class_name == "RetrievalTest1"
        
        # Test component listing
        component_list = self.integration_manager.list_integrated_components()
        assert len(component_list) >= 3
        assert "RetrievalTest1" in component_list
        assert "RetrievalTest2" in component_list
        assert "RetrievalTest3" in component_list
        
        # Test non-existent component
        non_existent = self.integration_manager.get_integrated_component("NonExistent")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_integration_re_validation(self):
        """Test re-validation of all integrated components"""
        
        # Generate multiple components
        specs = [
            "Create a source component called RevalidTest1 that fetches JSON from API endpoints",
            "Build a transformer component called RevalidTest2 that filters CSV data"
        ]
        
        for spec in specs:
            await self.integration_manager.generate_and_integrate_component(spec)
        
        # Re-validate all integrations
        validation_summary = await self.integration_manager.validate_all_integrations()
        
        # All should pass re-validation
        assert len(validation_summary) >= 2
        
        for component_name, result in validation_summary.items():
            assert result["status"] == "PASSED"
            assert result["compliance_score"] >= 0.95
            assert result["phase2_status"] == "FULLY_COMPLIANT"
    
    @pytest.mark.asyncio
    async def test_integrated_component_export(self):
        """Test export of integrated component with all artifacts"""
        
        nl_spec = "Create a source component called ExportTestSource that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Export to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            await self.integration_manager.export_integrated_component("ExportTestSource", temp_dir)
            
            # Verify all files were created
            expected_files = [
                "ExportTestSource.py",
                "test_exporttestsource_properties.py",
                "ExportTestSource_integration_metadata.json"
            ]
            
            for expected_file in expected_files:
                file_path = os.path.join(temp_dir, expected_file)
                assert os.path.exists(file_path), f"Missing file: {expected_file}"
            
            # Verify component source code
            with open(os.path.join(temp_dir, "ExportTestSource.py"), 'r') as f:
                source_code = f.read()
            assert "class ExportTestSource" in source_code
            assert "async def process(self)" in source_code
            
            # Verify property test suite
            with open(os.path.join(temp_dir, "test_exporttestsource_properties.py"), 'r') as f:
                test_code = f.read()
            assert "class TestExportTestSourceProperties" in test_code
            assert "hypothesis" in test_code
            
            # Verify integration metadata
            import json
            with open(os.path.join(temp_dir, "ExportTestSource_integration_metadata.json"), 'r') as f:
                metadata = json.load(f)
            
            assert metadata["component_name"] == "ExportTestSource"
            assert "registry_entry" in metadata
            assert "validation_results" in metadata
            assert "phase2_compliance" in metadata
    
    @pytest.mark.asyncio
    async def test_export_non_existent_component_fails(self):
        """Test export of non-existent component fails hard"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(Phase2IntegrationError) as exc_info:
                await self.integration_manager.export_integrated_component("NonExistentComponent", temp_dir)
            
            assert "not found" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_fail_hard_principles_maintained(self):
        """Test that fail-hard principles are maintained throughout integration"""
        
        nl_spec = "Create a source component called FailHardIntegrationTest that fetches JSON from API endpoints"
        
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify fail-hard principles in generated code
        source_code = integrated_component.generated_component.source_code.lower()
        assert "fail hard" in source_code
        assert "v5.0" in integrated_component.generated_component.source_code
        
        # Verify no fallback patterns
        assert "fallback" not in source_code
        assert "graceful" not in source_code
        assert "best_guess" not in source_code
        
        # Verify no mock capabilities
        assert "mock_mode" not in source_code
        assert ("mock" not in source_code or "no mock" in source_code)
        
        # Verify property tests enforce fail-hard
        test_code = integrated_component.property_test_suite.test_code.lower()
        assert "fail hard" in test_code
        assert "pytest.raises" in test_code
        assert "assert" in test_code
        
        # Verify Phase 2 compliance enforces fail-hard
        assert integrated_component.phase2_compliance["fail_hard_compliance"] is True
        assert integrated_component.phase2_compliance["phase2_integration_status"] == "FULLY_COMPLIANT"
    
    @pytest.mark.asyncio
    async def test_no_partial_integration_allowed(self):
        """Test that partial integration is not allowed"""
        
        # This test verifies that if any part of integration fails,
        # the entire integration fails (no partial components)
        
        nl_spec = "Create a source component called NoPartialTest that fetches JSON from API endpoints"
        
        # Generate component successfully
        integrated_component = await self.integration_manager.generate_and_integrate_component(nl_spec)
        
        # Verify complete integration (not partial)
        assert integrated_component.generated_component is not None
        assert integrated_component.property_test_suite is not None
        assert integrated_component.registry_entry is not None
        assert integrated_component.validation_results is not None
        assert integrated_component.phase2_compliance is not None
        
        # Verify all compliance checks passed
        compliance = integrated_component.phase2_compliance
        assert compliance["schema_compliance"] is True
        assert compliance["registry_compliance"] is True
        assert compliance["validation_framework_compliance"] is True
        assert compliance["property_test_compliance"] is True
        assert compliance["security_compliance"] is True
        assert compliance["fail_hard_compliance"] is True
        assert compliance["overall_compliance_score"] >= 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])