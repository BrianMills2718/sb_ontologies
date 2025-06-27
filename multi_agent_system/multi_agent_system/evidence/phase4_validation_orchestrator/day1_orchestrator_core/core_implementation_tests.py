"""
Core Implementation Tests for ValidationDrivenOrchestrator
Testing the fundamental orchestration and dependency checking functionality
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from typing import List

# Import the core implementation
import sys
sys.path.append('/home/brian/autocoder3_cc')

from blueprint_language.validation_driven_orchestrator import ValidationDrivenOrchestrator
from blueprint_language.validation_dependency_checker import ValidationDependencyChecker
from blueprint_language.validation_result_types import (
    ValidationDependencyError, ValidationLevel, FailureType,
    SystemGenerationResult, ValidationResult, ValidationFailure
)


@dataclass
class MockBlueprint:
    """Mock blueprint for testing"""
    name: str = "test_blueprint"
    components: List = None
    reasonableness_checks: List[str] = None
    source_path: str = "/test/blueprint.yaml"
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.reasonableness_checks is None:
            self.reasonableness_checks = ["System should be reasonable"]


@dataclass
class MockComponent:
    """Mock component for testing"""
    name: str
    type: str = "Source"
    behavioral_dependencies: List = None
    config: dict = None
    
    def __post_init__(self):
        if self.behavioral_dependencies is None:
            self.behavioral_dependencies = []
        if self.config is None:
            self.config = {}


class TestValidationDrivenOrchestrator:
    """Test suite for ValidationDrivenOrchestrator core functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return ValidationDrivenOrchestrator()
    
    @pytest.fixture
    def simple_blueprint(self):
        """Create simple test blueprint"""
        return MockBlueprint(
            name="simple_test",
            components=[
                MockComponent("test_source", "Source"),
                MockComponent("test_transformer", "Transformer")
            ]
        )
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator.development_mode is True
        assert isinstance(orchestrator.dependency_checker, ValidationDependencyChecker)
        assert orchestrator.level_validators is not None
        assert orchestrator.healers is not None
        assert orchestrator.phase_integrations is not None
    
    def test_level_validators_initialization(self, orchestrator):
        """Test level validators are properly initialized"""
        validators = orchestrator.level_validators
        assert "framework_validator" in validators
        assert "component_validator" in validators
        assert "integration_validator" in validators
        assert "semantic_validator" in validators
    
    def test_healers_initialization(self, orchestrator):
        """Test healers are properly initialized"""
        healers = orchestrator.healers
        assert "ast_healer" in healers
        assert "semantic_healer" in healers
        assert "config_regenerator" in healers
    
    def test_phase_integrations_initialization(self, orchestrator):
        """Test phase integrations are properly initialized"""
        integrations = orchestrator.phase_integrations
        assert "component_registry" in integrations
        assert "schema_framework" in integrations
        assert "template_system" in integrations
        assert "schema_generator" in integrations
        assert "nl_parser" in integrations


class TestValidationDependencyChecker:
    """Test suite for ValidationDependencyChecker"""
    
    @pytest.fixture
    def dependency_checker(self):
        """Create dependency checker instance for testing"""
        return ValidationDependencyChecker()
    
    @pytest.fixture
    def simple_blueprint(self):
        """Create simple test blueprint"""
        return MockBlueprint(
            name="simple_test",
            components=[
                MockComponent("test_source", "Source"),
                MockComponent("test_transformer", "Transformer")
            ]
        )
    
    @pytest.fixture
    def blueprint_with_dependencies(self):
        """Create blueprint with external dependencies"""
        service_dep = type('ServiceDep', (), {
            'service_name': 'test_api',
            'service_type': 'http_api',
            'endpoint': 'http://test.example.com/api'
        })()
        
        component = MockComponent(
            "test_component",
            behavioral_dependencies=[service_dep]
        )
        
        return MockBlueprint(
            name="dependency_test",
            components=[component]
        )
    
    @pytest.mark.asyncio
    async def test_dependency_checker_initialization(self, dependency_checker):
        """Test dependency checker initializes correctly"""
        assert dependency_checker.llm_configured is False
        assert dependency_checker.database_available is False
        assert dependency_checker.external_services == {}
        assert dependency_checker.dependency_cache == {}
    
    @pytest.mark.asyncio
    async def test_missing_llm_configuration_fails_hard(self, dependency_checker, simple_blueprint):
        """Test missing LLM configuration causes hard failure"""
        # Clear LLM environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationDependencyError) as exc_info:
                await dependency_checker.validate_all_dependencies_configured(simple_blueprint)
            
            assert "LLM" in str(exc_info.value)
            assert "OPENAI_API_KEY or ANTHROPIC_API_KEY" in str(exc_info.value)
            assert "Level 4 semantic validation" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_missing_database_configuration_fails_hard(self, dependency_checker, simple_blueprint):
        """Test missing database configuration causes hard failure"""
        # Mock LLM as available but database as missing
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True):
            with patch.object(dependency_checker, '_test_llm_connectivity') as mock_llm:
                mock_llm.return_value = {"success": True, "provider": "OpenAI"}
                
                with pytest.raises(ValidationDependencyError) as exc_info:
                    await dependency_checker.validate_all_dependencies_configured(simple_blueprint)
                
                assert "Database" in str(exc_info.value)
                assert "PostgreSQL required for Level 3" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_external_service_dependency_extraction(self, dependency_checker, blueprint_with_dependencies):
        """Test external service dependencies are properly extracted"""
        external_deps = dependency_checker._extract_external_service_dependencies(blueprint_with_dependencies)
        
        assert len(external_deps) == 1
        assert external_deps[0].service_name == "test_api"
        assert external_deps[0].service_type == "http_api"
        assert external_deps[0].endpoint == "http://test.example.com/api"
    
    @pytest.mark.asyncio
    async def test_python_version_checking(self, dependency_checker):
        """Test Python version compatibility checking"""
        python_status = await dependency_checker._check_python_version()
        
        assert python_status.name == "python"
        assert python_status.available is True  # Should pass for current Python
        assert python_status.version is not None
    
    @pytest.mark.asyncio
    async def test_framework_dependencies_checking(self, dependency_checker):
        """Test framework dependencies are checked"""
        framework_deps = await dependency_checker._check_framework_dependencies()
        
        assert "python" in framework_deps
        assert framework_deps["python"].available is True
        
        # Check for required packages
        required_packages = ["package_pydantic", "package_yaml", "package_jinja2"]
        for package in required_packages:
            assert package in framework_deps


class TestValidationResultTypes:
    """Test suite for validation result types"""
    
    def test_validation_failure_creation(self):
        """Test ValidationFailure creation and serialization"""
        failure = ValidationFailure(
            component_name="test_component",
            failure_type=FailureType.COMPONENT_LOGIC_VALIDATION,
            error_message="Test validation failure",
            healing_candidate=True,
            level=ValidationLevel.LEVEL_2_COMPONENT_LOGIC
        )
        
        assert failure.component_name == "test_component"
        assert failure.failure_type == FailureType.COMPONENT_LOGIC_VALIDATION
        assert failure.healing_candidate is True
        assert failure.level == ValidationLevel.LEVEL_2_COMPONENT_LOGIC
        
        # Test serialization
        failure_dict = failure.to_dict()
        assert failure_dict["component_name"] == "test_component"
        assert failure_dict["failure_type"] == "component_logic_validation"
        assert failure_dict["healing_candidate"] is True
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and properties"""
        failures = [
            ValidationFailure(
                component_name="test_component",
                failure_type=FailureType.COMPONENT_LOGIC_VALIDATION,
                error_message="Test failure"
            )
        ]
        
        result = ValidationResult(
            passed=False,
            level=ValidationLevel.LEVEL_2_COMPONENT_LOGIC,
            failures=failures,
            healing_applied=True,
            execution_time=1.5
        )
        
        assert result.passed is False
        assert result.level == ValidationLevel.LEVEL_2_COMPONENT_LOGIC
        assert len(result.failures) == 1
        assert result.healing_applied is True
        assert result.execution_time == 1.5
        
        # Test serialization
        result_dict = result.to_dict()
        assert result_dict["passed"] is False
        assert result_dict["level"] == 2
        assert len(result_dict["failures"]) == 1
    
    def test_system_generation_result_properties(self):
        """Test SystemGenerationResult properties"""
        # Create validation results for all levels
        level1_result = ValidationResult(
            passed=True,
            level=ValidationLevel.LEVEL_1_FRAMEWORK
        )
        level2_result = ValidationResult(
            passed=True,
            level=ValidationLevel.LEVEL_2_COMPONENT_LOGIC
        )
        level3_result = ValidationResult(
            passed=True,
            level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION
        )
        level4_result = ValidationResult(
            passed=True,
            level=ValidationLevel.LEVEL_4_SEMANTIC_VALIDATION
        )
        
        system_result = SystemGenerationResult(
            successful=True,
            generated_system={"test": "system"},
            validation_levels_passed=4,
            validation_results=[level1_result, level2_result, level3_result, level4_result]
        )
        
        # Test level-specific properties
        assert system_result.level1_passed is True
        assert system_result.level2_passed is True
        assert system_result.level3_passed is True
        assert system_result.level4_passed is True
        assert system_result.all_levels_passed is True
        assert system_result.system_generated is True
        
        # Test serialization
        system_dict = system_result.to_dict()
        assert system_dict["successful"] is True
        assert system_dict["all_levels_passed"] is True
        assert system_dict["system_generated"] is True


class TestIntegrationScenarios:
    """Test integration scenarios between orchestrator and dependency checker"""
    
    @pytest.mark.asyncio
    async def test_complete_dependency_validation_success(self):
        """Test complete dependency validation with all dependencies available"""
        orchestrator = ValidationDrivenOrchestrator()
        blueprint = MockBlueprint()
        
        # Mock all dependencies as available
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test_key",
            "DATABASE_URL": "postgresql://test:test@localhost:5432/test"
        }):
            with patch.object(orchestrator.dependency_checker, '_test_llm_connectivity') as mock_llm:
                mock_llm.return_value = {"success": True, "provider": "OpenAI"}
                
                with patch.object(orchestrator.dependency_checker, '_test_database_connectivity') as mock_db:
                    mock_db.return_value = {"success": True, "version": "PostgreSQL 14.0"}
                    
                    # Should not raise exception
                    await orchestrator.dependency_checker.validate_all_dependencies_configured(blueprint)
    
    @pytest.mark.asyncio
    async def test_dependency_validation_failure_propagation(self):
        """Test dependency validation failures properly propagate"""
        orchestrator = ValidationDrivenOrchestrator()
        blueprint = MockBlueprint()
        
        # Clear all environment variables to force failure
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValidationDependencyError) as exc_info:
                await orchestrator.dependency_checker.validate_all_dependencies_configured(blueprint)
            
            error_message = str(exc_info.value)
            assert "Cannot proceed with validation" in error_message
            assert "missing required dependencies" in error_message
            assert "LLM" in error_message
            assert "Database" in error_message


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])