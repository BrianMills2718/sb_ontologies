#!/usr/bin/env python3
"""
Phase 4: ValidationDrivenOrchestrator - Central Orchestration System
=====================================================================

This is the central organizing principle of V5.0 architecture implementing
fail-hard dependency checking and four-tier validation hierarchy with
seamless integration of Phase 2 component library and Phase 3 blueprint schema.

Four-Tier Validation Hierarchy:
1. Level 1: Framework Unit Testing (framework validation)
2. Level 2: Component Logic Validation + AST Healing
3. Level 3: System Integration Testing + Configuration Regeneration
4. Level 4: Semantic Validation + Semantic Healing

NO FALLBACKS - All validation must be real and must pass
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sys
import os

# Add evidence paths for Phase 2-3 integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase2_component_library'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'phase3_blueprint_schema'))

# Import validation result types
from validation_result_types import (
    ValidationResult, ValidationFailure, ValidationDependencyError,
    ValidationSequenceError, FrameworkValidationError, ComponentLogicValidationError,
    SystemIntegrationError, SemanticValidationError, OrchestratedHealingResult,
    OrchestratedRegenerationResult, SystemGenerationResult
)

# Import dependency checker
from dependency_checker import ValidationDependencyChecker

# Import four-tier validation systems
from level1_framework_integration import Level1FrameworkValidator
from level2_component_integration import Level2ComponentValidator
from level3_system_integration import Level3SystemValidator
from level4_semantic_integration import Level4SemanticValidator

# Import healing orchestration
from healing_orchestration import (
    OrchestratedASTHealer, OrchestratedSemanticHealer, OrchestratedConfigRegenerator
)

# Import Phase 2-3 integration
from phase2_integration import Phase2ComponentIntegrator
from phase3_integration import Phase3BlueprintIntegrator


@dataclass
class SystemBlueprint:
    """System blueprint representation for validation orchestration"""
    description: str
    components: List[Dict[str, Any]]
    reasonableness_checks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationExecutionResult:
    """Complete validation execution result across all four levels"""
    level1_passed: bool = False
    level2_passed: bool = False
    level3_passed: bool = False
    level4_passed: bool = False
    
    level1_result: Optional[ValidationResult] = None
    level2_result: Optional[ValidationResult] = None
    level3_result: Optional[ValidationResult] = None
    level4_result: Optional[ValidationResult] = None
    
    healing_applied: bool = False
    healing_details: Dict[str, Any] = field(default_factory=dict)
    
    total_execution_time: float = 0.0
    system_generated: bool = False
    
    @property
    def all_levels_passed(self) -> bool:
        """Check if all four validation levels passed"""
        return (self.level1_passed and self.level2_passed and 
                self.level3_passed and self.level4_passed)


class ValidationDrivenOrchestrator:
    """
    Central orchestrator implementing four-tier validation hierarchy with fail-hard principles.
    
    This is the central organizing principle of V5.0 architecture that:
    1. Orchestrates all four validation levels in sequence
    2. Integrates healing systems at appropriate levels
    3. Enforces fail-hard validation with no fallbacks
    4. Integrates seamlessly with Phase 2 component library and Phase 3 blueprint schema
    5. Provides complete validation-driven system generation pipeline
    """
    
    def __init__(self, testing_mode: bool = False):
        self.logger = logging.getLogger("ValidationDrivenOrchestrator")
        
        # Always fail hard during development - NO FALLBACKS
        self.development_mode = True
        self.testing_mode = testing_mode
        
        # Initialize dependency checker (with testing mode if specified)
        self.dependency_checker = ValidationDependencyChecker(testing_mode=testing_mode)
        
        # Initialize four-tier validation system
        self.level1_validator = Level1FrameworkValidator()
        self.level2_validator = Level2ComponentValidator()
        self.level3_validator = Level3SystemValidator()
        self.level4_validator = Level4SemanticValidator()
        
        # Initialize healing orchestration system
        self.ast_healer = OrchestratedASTHealer()
        self.semantic_healer = OrchestratedSemanticHealer()
        self.config_regenerator = OrchestratedConfigRegenerator()
        
        # Initialize Phase 2-3 integration
        self.phase2_integrator = Phase2ComponentIntegrator()
        self.phase3_integrator = Phase3BlueprintIntegrator()
        
        self.logger.info("✅ ValidationDrivenOrchestrator initialized with fail-hard validation")
    
    async def generate_system_with_validation(self, blueprint: SystemBlueprint) -> ValidationExecutionResult:
        """
        Validation-driven system generation pipeline - NO FALLBACKS
        
        This is the main orchestration method that executes all four validation levels
        in sequence with healing integration and fail-hard enforcement.
        
        Args:
            blueprint: SystemBlueprint to validate and generate
            
        Returns:
            ValidationExecutionResult with complete execution details
            
        Raises:
            ValidationDependencyError: If pre-flight dependencies are missing
            ValidationSequenceError: If validation sequence fails
        """
        start_time = time.time()
        
        self.logger.info("🚀 Starting validation-driven system generation")
        
        try:
            # ===============================
            # PRE-FLIGHT DEPENDENCY VALIDATION
            # ===============================
            self.logger.info("🔍 Phase 1: Pre-flight dependency validation")
            await self.dependency_checker.validate_all_dependencies_configured(blueprint)
            self.logger.info("✅ Pre-flight dependency validation passed")
            
            # ===============================
            # PHASE 2-3 INTEGRATION SETUP
            # ===============================
            self.logger.info("🔗 Phase 2-3: Integration setup")
            await self.phase2_integrator.integrate_with_component_library(blueprint)
            await self.phase3_integrator.integrate_with_blueprint_schema(blueprint)
            self.logger.info("✅ Phase 2-3 integration setup complete")
            
            # ===============================
            # LEVEL 1: FRAMEWORK VALIDATION
            # ===============================
            self.logger.info("🏗️  Level 1: Framework Unit Testing")
            level1_result = await self._execute_level1_validation()
            
            if not level1_result.passed:
                raise FrameworkValidationError(
                    f"Level 1 framework validation failed: {[f.error_message for f in level1_result.failures]}. "
                    f"This indicates a bug in the Autocoder framework itself."
                )
            
            self.logger.info("✅ Level 1 framework validation passed")
            
            # ===============================
            # LEVEL 2: COMPONENT LOGIC + AST HEALING
            # ===============================
            self.logger.info("🔧 Level 2: Component Logic Validation with AST Healing")
            level2_result = await self._execute_level2_validation(blueprint, level1_result)
            
            if not level2_result.passed:
                raise ComponentLogicValidationError(
                    f"Level 2 component logic validation failed: {[f.error_message for f in level2_result.failures]}"
                )
            
            self.logger.info("✅ Level 2 component logic validation passed")
            
            # ===============================
            # LEVEL 3: SYSTEM INTEGRATION + CONFIG REGEN
            # ===============================
            self.logger.info("🌐 Level 3: System Integration Testing with Configuration Regeneration")
            level3_result = await self._execute_level3_validation(blueprint, level2_result)
            
            if not level3_result.passed:
                raise SystemIntegrationError(
                    f"Level 3 system integration validation failed: {[f.error_message for f in level3_result.failures]}"
                )
            
            self.logger.info("✅ Level 3 system integration validation passed")
            
            # ===============================
            # LEVEL 4: SEMANTIC VALIDATION + SEMANTIC HEALING
            # ===============================
            self.logger.info("🧠 Level 4: Semantic Validation with Semantic Healing")
            level4_result = await self._execute_level4_validation(blueprint, level3_result)
            
            if not level4_result.passed:
                raise SemanticValidationError(
                    f"Level 4 semantic validation failed: {[f.error_message for f in level4_result.failures]}"
                )
            
            self.logger.info("✅ Level 4 semantic validation passed")
            
            # ===============================
            # SYSTEM FINALIZATION
            # ===============================
            self.logger.info("🎯 Finalizing system generation")
            system_result = await self._finalize_system_generation(blueprint, level4_result)
            
            total_time = time.time() - start_time
            
            # Create comprehensive result
            execution_result = ValidationExecutionResult(
                level1_passed=True,
                level2_passed=True,
                level3_passed=True,
                level4_passed=True,
                level1_result=level1_result,
                level2_result=level2_result,
                level3_result=level3_result,
                level4_result=level4_result,
                healing_applied=(level2_result.healing_applied or level3_result.healing_applied or level4_result.healing_applied),
                healing_details={
                    'ast_healing': level2_result.healing_applied,
                    'config_regeneration': level3_result.healing_applied,
                    'semantic_healing': level4_result.healing_applied
                },
                total_execution_time=total_time,
                system_generated=True
            )
            
            self.logger.info(f"🎉 Complete validation-driven system generation successful in {total_time:.2f}s")
            return execution_result
            
        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(f"❌ Validation-driven system generation failed after {total_time:.2f}s: {e}")
            raise
    
    async def _execute_level1_validation(self) -> ValidationResult:
        """
        Level 1: Framework Unit Testing - Validate Autocoder framework itself
        
        This level validates the framework components and infrastructure
        before proceeding with component-specific validation.
        """
        start_time = time.time()
        
        try:
            # Execute framework validation using Level 1 validator
            framework_test_results = await self.level1_validator.run_framework_tests()
            
            if not framework_test_results.all_passed:
                return ValidationResult(
                    passed=False,
                    level=1,
                    failures=[ValidationFailure(
                        component_name=None,
                        failure_type="framework_validation",
                        error_message=f"Framework validation failed: {framework_test_results.failures}",
                        healing_candidate=False  # Framework issues require manual intervention
                    )],
                    execution_time=time.time() - start_time
                )
            
            return ValidationResult(
                passed=True,
                level=1,
                execution_time=time.time() - start_time,
                metadata={"tests_passed": framework_test_results.test_count}
            )
            
        except Exception as e:
            raise FrameworkValidationError(
                f"Level 1 framework validation failed: {e}. "
                f"This indicates a bug in the Autocoder framework itself."
            )
    
    async def _execute_level2_validation(self, blueprint: SystemBlueprint, level1_result: ValidationResult) -> ValidationResult:
        """
        Level 2: Component Logic Validation with AST healing integration
        
        This level validates component logic using Phase 2 systems and applies
        AST healing when validation failures can be automatically fixed.
        """
        start_time = time.time()
        
        if not level1_result.passed:
            raise ValidationSequenceError("Level 2 cannot proceed - Level 1 validation failed")
        
        failures = []
        healing_applied = False
        
        for component in blueprint.components:
            component_name = component.get('name', 'unnamed')
            
            try:
                # Run component logic validation using Phase 2 systems
                logic_result = await self.level2_validator.validate_component_logic(component)
                
                if not logic_result.passed:
                    self.logger.warning(f"Component logic validation failed for '{component_name}', attempting AST healing")
                    
                    # Trigger AST healing for logic failures
                    healed_result = await self.ast_healer.heal_component_logic(component, logic_result.all_errors)
                    
                    if healed_result.healing_successful:
                        healing_applied = True
                        self.logger.info(f"AST healing successful for component '{component_name}'")
                        
                        # Re-validate after healing
                        retry_result = await self.level2_validator.validate_component_logic(healed_result.healed_component)
                        
                        if not retry_result.passed:
                            failures.append(ValidationFailure(
                                component_name=component_name,
                                failure_type="component_logic_healing_failed",
                                error_message=f"Component logic validation failed even after AST healing: {retry_result.all_errors}"
                            ))
                    else:
                        failures.append(ValidationFailure(
                            component_name=component_name,
                            failure_type="component_logic_validation",
                            error_message=f"Component logic validation failed and healing was unsuccessful: {logic_result.all_errors}"
                        ))
                else:
                    self.logger.debug(f"Component logic validation passed for '{component_name}'")
                    
            except Exception as e:
                failures.append(ValidationFailure(
                    component_name=component_name,
                    failure_type="component_logic_error",
                    error_message=f"Component logic validation error: {e}"
                ))
        
        return ValidationResult(
            passed=len(failures) == 0,
            level=2,
            failures=failures,
            healing_applied=healing_applied,
            execution_time=time.time() - start_time
        )
    
    async def _execute_level3_validation(self, blueprint: SystemBlueprint, level2_result: ValidationResult) -> ValidationResult:
        """
        Level 3: System Integration Testing with configuration regeneration
        
        This level validates system integration with real services and applies
        configuration regeneration when integration failures can be fixed.
        """
        start_time = time.time()
        
        if not level2_result.passed:
            raise ValidationSequenceError("Level 3 cannot proceed - Level 2 validation failed")
        
        try:
            # Run system integration tests with real services
            integration_result = await self.level3_validator.validate_system_integration(blueprint)
            
            if not integration_result.passed:
                self.logger.warning("System integration validation failed, attempting configuration regeneration")
                
                # Trigger configuration regeneration (safer than modification)
                regen_result = await self.config_regenerator.regenerate_system_configuration(
                    blueprint, integration_result.failures
                )
                
                if regen_result.regeneration_successful:
                    self.logger.info("Configuration regeneration successful")
                    
                    # Re-validate with new configuration
                    retry_result = await self.level3_validator.validate_system_integration(regen_result.updated_blueprint)
                    
                    if not retry_result.passed:
                        raise SystemIntegrationError(
                            f"Level 3 integration validation failed even after configuration regeneration: {retry_result.failures}"
                        )
                    
                    return ValidationResult(
                        passed=True,
                        level=3,
                        healing_applied=True,
                        execution_time=time.time() - start_time,
                        metadata={"configuration_regenerated": True}
                    )
                else:
                    raise SystemIntegrationError(
                        f"Level 3 integration validation failed and configuration regeneration was unsuccessful: {integration_result.failures}"
                    )
            
            return ValidationResult(
                passed=True,
                level=3,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            raise SystemIntegrationError(f"Level 3 system integration validation failed: {e}")
    
    async def _execute_level4_validation(self, blueprint: SystemBlueprint, level3_result: ValidationResult) -> ValidationResult:
        """
        Level 4: Semantic Validation with semantic healing integration
        
        This level validates system semantics using Phase 3 reasonableness checks
        and applies semantic healing when semantic issues can be automatically fixed.
        """
        start_time = time.time()
        
        if not level3_result.passed:
            raise ValidationSequenceError("Level 4 cannot proceed - Level 3 validation failed")
        
        # Fail hard if LLM not configured (already checked in pre-flight, but double-check)
        if not await self.dependency_checker._is_llm_configured():
            raise SemanticValidationError(
                "Level 4 semantic validation requires LLM configuration. "
                "Set OPENAI_API_KEY or ANTHROPIC_API_KEY. "
                "NO MOCK MODES OR FALLBACKS AVAILABLE."
            )
        
        try:
            # Use system-level reasonableness checks from blueprint
            semantic_result = await self.level4_validator.validate_system_semantics(
                blueprint, include_reasonableness_checks=True
            )
            
            if not semantic_result.passed:
                self.logger.warning("Semantic validation failed, attempting semantic healing")
                
                # Trigger semantic healing for semantic failures
                healed_result = await self.semantic_healer.heal_system_semantics(blueprint, semantic_result.failures)
                
                if healed_result.healing_successful:
                    self.logger.info("Semantic healing successful")
                    
                    # Re-validate after semantic healing
                    retry_result = await self.level4_validator.validate_system_semantics(healed_result.healed_blueprint)
                    
                    if not retry_result.passed:
                        raise SemanticValidationError(
                            f"Level 4 semantic validation failed even after semantic healing: {retry_result.failures}"
                        )
                    
                    return ValidationResult(
                        passed=True,
                        level=4,
                        healing_applied=True,
                        execution_time=time.time() - start_time,
                        metadata={"semantic_healing_applied": True}
                    )
                else:
                    raise SemanticValidationError(
                        f"Level 4 semantic validation failed and semantic healing was unsuccessful: {semantic_result.failures}"
                    )
            
            return ValidationResult(
                passed=True,
                level=4,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            # Check if this is an LLM unavailability issue
            if "LLM" in str(e) or "API" in str(e):
                raise SemanticValidationError(
                    f"Level 4 validation failed due to LLM unavailability: {e}. "
                    f"LLM must be available and responding for semantic validation."
                )
            else:
                raise SemanticValidationError(f"Level 4 semantic validation failed: {e}")
    
    async def _finalize_system_generation(self, blueprint: SystemBlueprint, level4_result: ValidationResult) -> SystemGenerationResult:
        """
        Finalize system generation after all four validation levels have passed
        
        This method performs final system generation and packaging steps.
        """
        try:
            # Generate final system configuration
            system_config = {
                'blueprint': blueprint,
                'validation_results': {
                    'level1': level4_result.metadata.get('level1_metadata', {}),
                    'level2': level4_result.metadata.get('level2_metadata', {}),
                    'level3': level4_result.metadata.get('level3_metadata', {}),
                    'level4': level4_result.metadata
                },
                'phase2_integration': await self.phase2_integrator.get_integration_summary(),
                'phase3_integration': await self.phase3_integrator.get_integration_summary()
            }
            
            # Create system generation result
            return SystemGenerationResult(
                successful=True,
                generated_system=system_config,
                validation_levels_passed=4,
                healing_applied=level4_result.healing_applied,
                execution_time=level4_result.execution_time
            )
            
        except Exception as e:
            return SystemGenerationResult(
                successful=False,
                error_message=f"System finalization failed: {e}",
                validation_levels_passed=4  # Validation passed, but finalization failed
            )
    
    async def parse_and_validate_blueprint(self, blueprint_path: str) -> SystemBlueprint:
        """
        Parse blueprint and validate against V5.0 schema requirements
        
        This method integrates with Phase 3 blueprint schema system for parsing
        and validation of blueprint files.
        """
        try:
            # Use Phase 3 integration for blueprint parsing
            parsed_blueprint = await self.phase3_integrator.parse_blueprint_file(blueprint_path)
            
            # Validate V5.0 requirements
            validation_result = await self.phase3_integrator.validate_blueprint_schema(parsed_blueprint)
            
            if not validation_result.is_valid:
                raise ValueError(f"Blueprint validation failed: {validation_result.errors}")
            
            # Convert to SystemBlueprint format
            system_blueprint = SystemBlueprint(
                description=parsed_blueprint.description,
                components=[comp.to_dict() for comp in parsed_blueprint.components],
                reasonableness_checks=parsed_blueprint.reasonableness_checks,
                metadata=parsed_blueprint.metadata
            )
            
            return system_blueprint
            
        except Exception as e:
            raise ValueError(f"Failed to parse blueprint {blueprint_path}: {e}")
    
    async def generate_complete_system(self, blueprint_path: str) -> SystemGenerationResult:
        """
        Complete validation-driven system generation pipeline
        
        This is the main entry point for end-to-end system generation from blueprint file.
        """
        try:
            self.logger.info(f"🎬 Starting complete system generation for: {blueprint_path}")
            
            # 1. Parse and validate blueprint
            blueprint = await self.parse_and_validate_blueprint(blueprint_path)
            self.logger.info("✅ Blueprint parsed and validated")
            
            # 2. Execute four-tier validation pipeline
            validation_result = await self.generate_system_with_validation(blueprint)
            
            # 3. Create final system generation result
            if validation_result.all_levels_passed and validation_result.system_generated:
                return SystemGenerationResult(
                    successful=True,
                    generated_system=validation_result,
                    validation_levels_passed=4,
                    healing_applied=validation_result.healing_applied,
                    execution_time=validation_result.total_execution_time
                )
            else:
                return SystemGenerationResult(
                    successful=False,
                    error_message="Validation pipeline did not complete successfully",
                    validation_levels_passed=sum([
                        validation_result.level1_passed,
                        validation_result.level2_passed,
                        validation_result.level3_passed,
                        validation_result.level4_passed
                    ])
                )
            
        except Exception as e:
            self.logger.error(f"❌ Complete system generation failed: {e}")
            return SystemGenerationResult(
                successful=False,
                error_message=f"System generation failed: {e}",
                validation_levels_passed=0
            )
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status and configuration"""
        return {
            'orchestrator_initialized': True,
            'development_mode': self.development_mode,
            'validation_levels': {
                'level1_framework': self.level1_validator is not None,
                'level2_component': self.level2_validator is not None,
                'level3_integration': self.level3_validator is not None,
                'level4_semantic': self.level4_validator is not None
            },
            'healing_systems': {
                'ast_healer': self.ast_healer is not None,
                'semantic_healer': self.semantic_healer is not None,
                'config_regenerator': self.config_regenerator is not None
            },
            'phase_integration': {
                'phase2_component_library': self.phase2_integrator is not None,
                'phase3_blueprint_schema': self.phase3_integrator is not None
            },
            'dependency_checker': self.dependency_checker is not None
        }


# Convenience functions for external use
async def create_orchestrator() -> ValidationDrivenOrchestrator:
    """Create and initialize ValidationDrivenOrchestrator"""
    orchestrator = ValidationDrivenOrchestrator()
    return orchestrator


async def generate_system_from_blueprint(blueprint_path: str) -> SystemGenerationResult:
    """Generate system from blueprint file using ValidationDrivenOrchestrator"""
    orchestrator = await create_orchestrator()
    return await orchestrator.generate_complete_system(blueprint_path)


# Main execution for testing
if __name__ == "__main__":
    async def main():
        """Test ValidationDrivenOrchestrator with example data"""
        
        # Create test orchestrator
        orchestrator = ValidationDrivenOrchestrator()
        
        # Display orchestrator status
        status = orchestrator.get_orchestrator_status()
        print("🎭 ValidationDrivenOrchestrator Status:")
        for category, details in status.items():
            print(f"  {category}: {details}")
        
        # Create test blueprint
        test_blueprint = SystemBlueprint(
            description="Test web application system for ValidationDrivenOrchestrator testing",
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
                            {"port": 8080, "protocol": "http", "description": "Web server port"}
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
        
        print("\n🚀 Testing ValidationDrivenOrchestrator...")
        
        try:
            # Test system generation
            result = await orchestrator.generate_system_with_validation(test_blueprint)
            
            print(f"\n✅ Validation-driven system generation completed:")
            print(f"  Level 1 passed: {result.level1_passed}")
            print(f"  Level 2 passed: {result.level2_passed}")
            print(f"  Level 3 passed: {result.level3_passed}")
            print(f"  Level 4 passed: {result.level4_passed}")
            print(f"  All levels passed: {result.all_levels_passed}")
            print(f"  Healing applied: {result.healing_applied}")
            print(f"  Total execution time: {result.total_execution_time:.2f}s")
            print(f"  System generated: {result.system_generated}")
            
        except Exception as e:
            print(f"\n❌ Validation-driven system generation failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the test
    asyncio.run(main())