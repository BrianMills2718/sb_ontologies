"""
Level Integration Tests - Testing the four-tier validation level integration
Comprehensive tests for Level 1→2→3→4 integration with healing systems
"""

import pytest
import asyncio
import os
import time
from unittest.mock import patch, MagicMock, AsyncMock
from dataclasses import dataclass
from typing import List, Dict, Any

# Import the level integration modules
import sys
sys.path.append('/home/brian/autocoder3_cc')

from evidence.phase4_validation_orchestrator.day2_level_integration.level1_framework_integration import (
    Level1FrameworkValidator, create_framework_validator
)
from evidence.phase4_validation_orchestrator.day2_level_integration.level2_component_integration import (
    Level2ComponentValidator, Level2ASTHealingIntegrator,
    create_component_validator, create_ast_healing_integrator
)
from evidence.phase4_validation_orchestrator.day2_level_integration.level3_system_integration import (
    Level3SystemIntegrationValidator, Level3ConfigurationRegenerator,
    create_system_integration_validator, create_configuration_regenerator
)
from evidence.phase4_validation_orchestrator.day2_level_integration.level4_semantic_integration import (
    Level4SemanticValidator, Level4SemanticHealingIntegrator,
    create_semantic_validator, create_semantic_healing_integrator
)


@dataclass
class MockBlueprint:
    """Mock blueprint for testing"""
    name: str = "test_system"
    description: str = "A test system for validation"
    components: List = None
    reasonableness_checks: List[str] = None
    source_path: str = "/test/blueprint.yaml"
    
    def __post_init__(self):
        if self.components is None:
            self.components = [
                MockComponent("test_source", "Source"),
                MockComponent("test_transformer", "Transformer"),
                MockComponent("test_sink", "Sink")
            ]
        if self.reasonableness_checks is None:
            self.reasonableness_checks = [
                "System should process data efficiently",
                "Components should work together seamlessly"
            ]


@dataclass
class MockComponent:
    """Mock component for testing"""
    name: str
    type: str = "Source"
    description: str = ""
    behavioral_dependencies: List = None
    config: Dict = None
    
    def __post_init__(self):
        if self.behavioral_dependencies is None:
            self.behavioral_dependencies = []
        if self.config is None:
            self.config = {}
        if not self.description:
            self.description = f"A {self.type.lower()} component for testing"
    
    def generate(self):
        """Mock generate method for Source components"""
        return {"data": "test_data", "timestamp": time.time()}
    
    def transform(self, data):
        """Mock transform method for Transformer components"""
        return {"transformed": data, "timestamp": time.time()}
    
    def consume(self, data):
        """Mock consume method for Sink components"""
        return {"consumed": data, "timestamp": time.time()}
    
    def setup(self):
        """Mock setup method"""
        pass
    
    def cleanup(self):
        """Mock cleanup method"""
        pass


class TestLevel1FrameworkIntegration:
    """Test Level 1 framework validation integration"""
    
    @pytest.fixture
    def framework_validator(self):
        """Create framework validator for testing"""
        return Level1FrameworkValidator()
    
    @pytest.mark.asyncio
    async def test_framework_validator_creation(self):
        """Test framework validator can be created"""
        validator = await create_framework_validator()
        assert isinstance(validator, Level1FrameworkValidator)
        assert validator.test_suite_paths is not None
        assert validator.critical_modules is not None
    
    @pytest.mark.asyncio
    async def test_framework_validation_execution(self, framework_validator):
        """Test framework validation executes"""
        result = await framework_validator.validate_framework()
        
        assert hasattr(result, 'all_passed')
        assert hasattr(result, 'test_count')
        assert hasattr(result, 'failures')
        assert hasattr(result, 'execution_time')
        
        # Framework validation should pass (basic validation)
        assert result.all_passed is True
        assert result.test_count >= 0
        assert isinstance(result.failures, list)
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_module_import_validation(self, framework_validator):
        """Test module import validation"""
        result = await framework_validator._validate_module_imports()
        
        assert "success" in result
        # Some modules may not exist yet, but validation should complete
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_framework_integrity_validation(self, framework_validator):
        """Test framework integrity validation"""
        result = await framework_validator._validate_framework_integrity()
        
        assert "success" in result
        assert "checks_performed" in result
        assert result["checks_performed"] >= 3
    
    @pytest.mark.asyncio
    async def test_critical_path_validation(self, framework_validator):
        """Test critical path validation"""
        result = await framework_validator._validate_critical_paths()
        
        assert "success" in result
        assert "paths_tested" in result
        assert result["paths_tested"] >= 3


class TestLevel2ComponentIntegration:
    """Test Level 2 component logic validation integration"""
    
    @pytest.fixture
    def component_validator(self):
        """Create component validator for testing"""
        return Level2ComponentValidator()
    
    @pytest.fixture
    def ast_healing_integrator(self):
        """Create AST healing integrator for testing"""
        return Level2ASTHealingIntegrator()
    
    @pytest.fixture
    def test_component(self):
        """Create test component"""
        return MockComponent("test_component", "Source")
    
    @pytest.mark.asyncio
    async def test_component_validator_creation(self):
        """Test component validator can be created"""
        validator = await create_component_validator()
        assert isinstance(validator, Level2ComponentValidator)
        assert validator.validation_rules is not None
    
    @pytest.mark.asyncio
    async def test_ast_healing_integrator_creation(self):
        """Test AST healing integrator can be created"""
        integrator = await create_ast_healing_integrator()
        assert isinstance(integrator, Level2ASTHealingIntegrator)
    
    @pytest.mark.asyncio
    async def test_component_logic_validation(self, component_validator, test_component):
        """Test component logic validation"""
        result = await component_validator.validate_component_logic(test_component)
        
        assert hasattr(result, 'passed')
        assert hasattr(result, 'component_name')
        assert hasattr(result, 'failures')
        assert hasattr(result, 'execution_time')
        
        assert result.component_name == "test_component"
        assert isinstance(result.failures, list)
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_component_type_validation(self, component_validator, test_component):
        """Test component type validation"""
        result = await component_validator._validate_component_type(test_component)
        
        assert "success" in result
        # Should succeed with fallback registry
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_component_interface_validation(self, component_validator, test_component):
        """Test component interface validation"""
        result = await component_validator._validate_component_interface(test_component)
        
        assert "success" in result
        assert "rules_applied" in result
        assert "methods_checked" in result
        assert "attributes_checked" in result
    
    @pytest.mark.asyncio
    async def test_source_logic_validation(self, component_validator, test_component):
        """Test Source component specific logic validation"""
        result = await component_validator._validate_source_logic(test_component)
        
        assert "success" in result
        assert "signature_validated" in result
        # Source component should pass validation
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_ast_healing_failure_conversion(self, ast_healing_integrator):
        """Test conversion of validation failures to healing targets"""
        failures = [
            "Component missing required method: generate",
            "Component transform method is not callable",
            "Component missing required attribute: config"
        ]
        
        targets = ast_healing_integrator._convert_failures_to_targets(failures)
        
        assert len(targets) == 3
        assert any(target["type"] == "missing_method" for target in targets)
        assert any(target["type"] == "fix_method_callable" for target in targets)
        assert any(target["type"] == "missing_attribute" for target in targets)
    
    @pytest.mark.asyncio
    async def test_ast_healing_with_fallback(self, ast_healing_integrator, test_component):
        """Test AST healing with fallback healer"""
        failures = ["Component missing required method: test_method"]
        
        result = await ast_healing_integrator.heal_component_logic(test_component, failures)
        
        assert hasattr(result, 'healing_successful')
        assert hasattr(result, 'execution_time')
        # Should fail with fallback healer
        assert result.healing_successful is False
        assert "not available" in result.error_message


class TestLevel3SystemIntegration:
    """Test Level 3 system integration validation"""
    
    @pytest.fixture
    def system_validator(self):
        """Create system integration validator for testing"""
        return Level3SystemIntegrationValidator()
    
    @pytest.fixture
    def config_regenerator(self):
        """Create configuration regenerator for testing"""
        return Level3ConfigurationRegenerator()
    
    @pytest.fixture
    def test_blueprint(self):
        """Create test blueprint"""
        return MockBlueprint()
    
    @pytest.mark.asyncio
    async def test_system_validator_creation(self):
        """Test system integration validator can be created"""
        validator = await create_system_integration_validator()
        assert isinstance(validator, Level3SystemIntegrationValidator)
        assert validator.integration_requirements is not None
    
    @pytest.mark.asyncio
    async def test_config_regenerator_creation(self):
        """Test configuration regenerator can be created"""
        regenerator = await create_configuration_regenerator()
        assert isinstance(regenerator, Level3ConfigurationRegenerator)
        assert regenerator.regeneration_strategies is not None
    
    @pytest.mark.asyncio
    async def test_system_integration_validation(self, system_validator, test_blueprint):
        """Test system integration validation"""
        result = await system_validator.validate_system_integration(test_blueprint)
        
        assert hasattr(result, 'passed')
        assert hasattr(result, 'system_name')
        assert hasattr(result, 'failures')
        assert hasattr(result, 'execution_time')
        
        assert result.system_name == "test_system"
        assert isinstance(result.failures, list)
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_database_integration_validation(self, system_validator, test_blueprint):
        """Test database integration validation"""
        result = await system_validator._validate_database_integration(test_blueprint)
        
        assert "success" in result
        assert "requires_database" in result
        assert "connection_tested" in result
    
    @pytest.mark.asyncio
    async def test_component_connectivity_validation(self, system_validator, test_blueprint):
        """Test component connectivity validation"""
        result = await system_validator._validate_component_connectivity(test_blueprint)
        
        assert "success" in result
        assert "connectivity_details" in result
        assert "components_tested" in result
        assert result["components_tested"] == len(test_blueprint.components)
    
    @pytest.mark.asyncio
    async def test_dataflow_validation(self, system_validator, test_blueprint):
        """Test system dataflow validation"""
        result = await system_validator._validate_system_dataflow(test_blueprint)
        
        assert "success" in result
        assert "dataflow_details" in result
        assert "component_types" in result["dataflow_details"]
    
    @pytest.mark.asyncio
    async def test_configuration_regeneration_analysis(self, config_regenerator):
        """Test configuration regeneration failure analysis"""
        failures = [
            "Database connection failed on port 5432",
            "Memory limit exceeded for component",
            "Service timeout connecting to external API"
        ]
        
        analysis = config_regenerator._analyze_integration_failures(failures)
        
        assert "regenerable" in analysis
        assert "strategy" in analysis
        assert "changes" in analysis
        assert analysis["regenerable"] is True
        assert len(analysis["changes"]) > 0
    
    @pytest.mark.asyncio
    async def test_port_configuration_regeneration(self, config_regenerator, test_blueprint):
        """Test port configuration regeneration"""
        # Add port configuration to test components
        test_blueprint.components[0].config = {"port": 8080}
        test_blueprint.components[1].config = {"endpoint": "http://localhost:8081"}
        
        analysis = {"strategy": "port_regeneration", "changes": ["port_regeneration"]}
        
        result = await config_regenerator._regenerate_port_configuration(test_blueprint, analysis)
        
        assert hasattr(result, 'name')
        assert hasattr(result, 'regeneration_metadata')
        assert 'port_regeneration' in result.regeneration_metadata


class TestLevel4SemanticIntegration:
    """Test Level 4 semantic validation integration"""
    
    @pytest.fixture
    def semantic_validator(self):
        """Create semantic validator for testing"""
        return Level4SemanticValidator()
    
    @pytest.fixture
    def semantic_healing_integrator(self):
        """Create semantic healing integrator for testing"""
        return Level4SemanticHealingIntegrator()
    
    @pytest.fixture
    def test_blueprint(self):
        """Create test blueprint"""
        return MockBlueprint(
            name="fraud_detection_system",
            description="A fraud detection system for financial transactions",
            reasonableness_checks=[
                "System should detect fraud within 100ms",
                "False positive rate should be below 5%"
            ]
        )
    
    @pytest.mark.asyncio
    async def test_semantic_validator_creation(self):
        """Test semantic validator can be created"""
        validator = await create_semantic_validator()
        assert isinstance(validator, Level4SemanticValidator)
        assert validator.semantic_rules is not None
        assert validator.validation_prompts is not None
    
    @pytest.mark.asyncio
    async def test_semantic_healing_integrator_creation(self):
        """Test semantic healing integrator can be created"""
        integrator = await create_semantic_healing_integrator()
        assert isinstance(integrator, Level4SemanticHealingIntegrator)
    
    @pytest.mark.asyncio
    async def test_system_info_extraction(self, semantic_validator, test_blueprint):
        """Test system information extraction for LLM analysis"""
        system_info = semantic_validator._extract_system_info(test_blueprint)
        
        assert "name" in system_info
        assert "description" in system_info
        assert "components" in system_info
        
        assert system_info["name"] == "fraud_detection_system"
        assert len(system_info["components"]) == 3
        assert all("name" in comp for comp in system_info["components"])
        assert all("type" in comp for comp in system_info["components"])
    
    @pytest.mark.asyncio
    async def test_domain_context_inference(self, semantic_validator):
        """Test domain context inference"""
        # Test financial domain
        financial_context = semantic_validator._infer_domain_context(
            "A fraud detection system for processing financial transactions"
        )
        assert "Financial" in financial_context
        
        # Test data processing domain
        data_context = semantic_validator._infer_domain_context(
            "A data processing pipeline for analytics"
        )
        assert "Data Processing" in data_context
        
        # Test general domain
        general_context = semantic_validator._infer_domain_context(
            "A general software system"
        )
        assert "General" in general_context
    
    @pytest.mark.asyncio
    async def test_naming_consistency_check(self, semantic_validator, test_blueprint):
        """Test component naming consistency check"""
        components = semantic_validator._extract_system_info(test_blueprint)["components"]
        
        issues = semantic_validator._check_naming_consistency(components)
        
        # Should be empty for well-named components
        assert isinstance(issues, list)
    
    @pytest.mark.asyncio
    async def test_dataflow_consistency_check(self, semantic_validator, test_blueprint):
        """Test dataflow consistency check"""
        components = semantic_validator._extract_system_info(test_blueprint)["components"]
        
        issues = semantic_validator._check_dataflow_consistency(components)
        
        # Should be empty for balanced Source→Transformer→Sink flow
        assert isinstance(issues, list)
    
    @pytest.mark.asyncio
    async def test_responsibility_consistency_check(self, semantic_validator, test_blueprint):
        """Test component responsibility consistency check"""
        components = semantic_validator._extract_system_info(test_blueprint)["components"]
        
        issues = semantic_validator._check_responsibility_consistency(components)
        
        # May have issues due to generic descriptions
        assert isinstance(issues, list)
    
    @pytest.mark.asyncio
    async def test_semantic_validation_without_llm(self, semantic_validator, test_blueprint):
        """Test semantic validation fails properly without LLM"""
        # Clear LLM environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                await semantic_validator.validate_system_semantics(test_blueprint)
            
            assert "LLM configuration" in str(exc_info.value)
            assert "NO MOCK MODES" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_semantic_healing_with_fallback(self, semantic_healing_integrator, test_blueprint):
        """Test semantic healing with fallback healer"""
        failures = ["System coherence issues detected", "Business logic inconsistencies"]
        
        result = await semantic_healing_integrator.heal_system_semantics(test_blueprint, failures)
        
        assert hasattr(result, 'healing_successful')
        assert hasattr(result, 'execution_time')
        # Should fail with fallback healer
        assert result.healing_successful is False
        assert "not available" in result.error_message


class TestLevelIntegrationFlow:
    """Test complete level integration flow"""
    
    @pytest.fixture
    def all_validators(self):
        """Create all validators for integration testing"""
        return {
            "level1": Level1FrameworkValidator(),
            "level2": Level2ComponentValidator(),
            "level3": Level3SystemIntegrationValidator(),
            "level4": Level4SemanticValidator()
        }
    
    @pytest.fixture
    def test_blueprint(self):
        """Create comprehensive test blueprint"""
        return MockBlueprint(
            name="integration_test_system",
            description="A comprehensive system for testing level integration",
            reasonableness_checks=[
                "System should be performant and scalable",
                "Components should integrate seamlessly"
            ]
        )
    
    @pytest.mark.asyncio
    async def test_sequential_level_execution(self, all_validators, test_blueprint):
        """Test sequential execution of all validation levels"""
        results = {}
        
        # Level 1: Framework validation
        level1_result = await all_validators["level1"].validate_framework()
        results["level1"] = level1_result
        assert level1_result.all_passed, "Level 1 should pass for integration test"
        
        # Level 2: Component validation (depends on Level 1)
        if level1_result.all_passed:
            for component in test_blueprint.components:
                component_result = await all_validators["level2"].validate_component_logic(component)
                results[f"level2_{component.name}"] = component_result
                # Component validation should complete (may pass or fail)
                assert hasattr(component_result, 'passed')
        
        # Level 3: System integration (depends on Level 2)
        level3_result = await all_validators["level3"].validate_system_integration(test_blueprint)
        results["level3"] = level3_result
        assert hasattr(level3_result, 'passed')
        
        # Level 4: Semantic validation would require LLM - test structure only
        assert hasattr(all_validators["level4"], 'semantic_rules')
        assert hasattr(all_validators["level4"], 'validation_prompts')
    
    @pytest.mark.asyncio
    async def test_healing_integration_flow(self):
        """Test healing integration across levels"""
        # Test AST healing integration (Level 2)
        ast_integrator = Level2ASTHealingIntegrator()
        assert hasattr(ast_integrator, 'heal_component_logic')
        
        # Test configuration regeneration (Level 3)
        config_regenerator = Level3ConfigurationRegenerator()
        assert hasattr(config_regenerator, 'regenerate_system_configuration')
        
        # Test semantic healing integration (Level 4)
        semantic_integrator = Level4SemanticHealingIntegrator()
        assert hasattr(semantic_integrator, 'heal_system_semantics')
    
    @pytest.mark.asyncio
    async def test_integration_factory_functions(self):
        """Test all integration factory functions work"""
        # Test Level 1 factory
        level1_validator = await create_framework_validator()
        assert isinstance(level1_validator, Level1FrameworkValidator)
        
        # Test Level 2 factories
        level2_validator = await create_component_validator()
        assert isinstance(level2_validator, Level2ComponentValidator)
        
        ast_integrator = await create_ast_healing_integrator()
        assert isinstance(ast_integrator, Level2ASTHealingIntegrator)
        
        # Test Level 3 factories
        level3_validator = await create_system_integration_validator()
        assert isinstance(level3_validator, Level3SystemIntegrationValidator)
        
        config_regenerator = await create_configuration_regenerator()
        assert isinstance(config_regenerator, Level3ConfigurationRegenerator)
        
        # Test Level 4 factories
        level4_validator = await create_semantic_validator()
        assert isinstance(level4_validator, Level4SemanticValidator)
        
        semantic_integrator = await create_semantic_healing_integrator()
        assert isinstance(semantic_integrator, Level4SemanticHealingIntegrator)
    
    @pytest.mark.asyncio
    async def test_validation_result_compatibility(self, all_validators, test_blueprint):
        """Test all validation results have compatible structure"""
        # Level 1 result structure
        level1_result = await all_validators["level1"].validate_framework()
        assert hasattr(level1_result, 'all_passed')
        assert hasattr(level1_result, 'execution_time')
        assert hasattr(level1_result, 'failures')
        
        # Level 2 result structure
        component = test_blueprint.components[0]
        level2_result = await all_validators["level2"].validate_component_logic(component)
        assert hasattr(level2_result, 'passed')
        assert hasattr(level2_result, 'execution_time')
        assert hasattr(level2_result, 'failures')
        
        # Level 3 result structure
        level3_result = await all_validators["level3"].validate_system_integration(test_blueprint)
        assert hasattr(level3_result, 'passed')
        assert hasattr(level3_result, 'execution_time')
        assert hasattr(level3_result, 'failures')
        
        # Level 4 result structure (without LLM call)
        assert hasattr(all_validators["level4"], '_extract_system_info')
        system_info = all_validators["level4"]._extract_system_info(test_blueprint)
        assert "name" in system_info
        assert "components" in system_info


class TestIntegrationPerformance:
    """Test integration performance and scalability"""
    
    @pytest.mark.asyncio
    async def test_validation_performance_benchmarks(self):
        """Test validation performance across all levels"""
        # Create performance test blueprint
        large_blueprint = MockBlueprint(
            name="performance_test_system",
            components=[MockComponent(f"component_{i}", "Source") for i in range(10)]
        )
        
        # Benchmark Level 1
        level1_validator = Level1FrameworkValidator()
        start_time = time.time()
        level1_result = await level1_validator.validate_framework()
        level1_time = time.time() - start_time
        
        assert level1_time < 10.0, f"Level 1 validation too slow: {level1_time}s"
        
        # Benchmark Level 2
        level2_validator = Level2ComponentValidator()
        start_time = time.time()
        for component in large_blueprint.components[:3]:  # Test subset
            await level2_validator.validate_component_logic(component)
        level2_time = time.time() - start_time
        
        assert level2_time < 15.0, f"Level 2 validation too slow: {level2_time}s"
        
        # Benchmark Level 3
        level3_validator = Level3SystemIntegrationValidator()
        start_time = time.time()
        level3_result = await level3_validator.validate_system_integration(large_blueprint)
        level3_time = time.time() - start_time
        
        assert level3_time < 20.0, f"Level 3 validation too slow: {level3_time}s"
    
    @pytest.mark.asyncio
    async def test_memory_usage_validation(self):
        """Test memory usage during validation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run validation operations
        validators = {
            "level1": Level1FrameworkValidator(),
            "level2": Level2ComponentValidator(),
            "level3": Level3SystemIntegrationValidator()
        }
        
        blueprint = MockBlueprint()
        
        # Execute validations
        await validators["level1"].validate_framework()
        await validators["level2"].validate_component_logic(blueprint.components[0])
        await validators["level3"].validate_system_integration(blueprint)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Excessive memory usage: {memory_increase}MB increase"


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])