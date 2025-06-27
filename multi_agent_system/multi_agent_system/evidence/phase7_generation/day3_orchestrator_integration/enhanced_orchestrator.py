#!/usr/bin/env python3
"""
Enhanced ValidationDrivenOrchestrator with Two-Phase Generation Integration
===========================================================================

Extends the base ValidationDrivenOrchestrator to integrate scaffold and component
generation into the existing 4-tier validation pipeline. This preserves all
existing validation functionality while adding generation capabilities.

Integration Points:
- Level 1: Framework validation (unchanged)
- Level 2: Component logic validation + component generation
- Level 3: System integration + scaffold generation
- Level 4: Semantic validation (unchanged)
"""

import os
import sys
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Add paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day1_system_scaffold_generator'))  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day2_component_logic_generator'))

# Import base orchestrator
from blueprint_language.validation_driven_orchestrator import ValidationDrivenOrchestrator
from blueprint_language.validation_result_types import (
    ValidationResult, SystemGenerationResult, ValidationLevel,
    ValidationFailure, FailureType
)

# Import generation components
from system_scaffold_generator import SystemScaffoldGenerator, GeneratedScaffold
from harness_component_generator import HarnessComponentGenerator, GeneratedComponent

# Import blueprint types from correct locations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day1_system_scaffold_generator'))
from blueprint_types import SystemBlueprint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day2_component_logic_generator'))
from blueprint_types import ComponentLogic

logger = logging.getLogger(__name__)


@dataclass
class GenerationIntegratedResult:
    """Result combining validation and generation"""
    validation_result: ValidationResult
    generated_scaffold: Optional[GeneratedScaffold] = None
    generated_components: List[GeneratedComponent] = None
    generation_success: bool = False
    generation_time: float = 0.0
    generation_metadata: Dict[str, Any] = None


class EnhancedValidationDrivenOrchestrator(ValidationDrivenOrchestrator):
    """
    Enhanced ValidationDrivenOrchestrator with integrated two-phase generation.
    
    Preserves all existing 4-tier validation functionality while adding:
    - Component generation during Level 2 validation
    - Scaffold generation during Level 3 validation
    - Coordinated generation pipeline
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize generation components
        self.scaffold_generator = SystemScaffoldGenerator()
        self.component_generator = HarnessComponentGenerator()
        
        # Generation coordination
        self.generation_coordinator = None
        self.generation_results = {}
        
        logger.info("✨ EnhancedValidationDrivenOrchestrator initialized with two-phase generation")
    
    async def generate_system_with_validation(self, blueprint: SystemBlueprint) -> SystemGenerationResult:
        """
        Enhanced validation-driven system generation with integrated two-phase generation.
        
        Extends the base orchestrator to include:
        - Component generation during Level 2 validation
        - Scaffold generation during Level 3 validation
        - Coordinated generation output
        
        Args:
            blueprint: SystemBlueprint to validate and generate
            
        Returns:
            SystemGenerationResult with both validation and generation results
        """
        start_time = time.time()
        validation_results = []
        generation_results = []
        
        try:
            logger.info(f"🚀 Starting enhanced validation-driven generation for: {blueprint.description}")
            
            # Initialize generation coordinator
            if not self.generation_coordinator:
                await self._initialize_generation_coordinator()
            
            # Pre-flight: Validate all dependencies (unchanged)
            await self.dependency_checker.validate_all_dependencies_configured(blueprint)
            logger.info("✅ Pre-flight dependency validation completed")
            
            # Level 1: Framework validation (unchanged)
            logger.info("🔍 Level 1: Framework validation")
            level1_result = await self._execute_level1_validation()
            validation_results.append(level1_result)
            
            if not level1_result.passed:
                return self._create_failed_result(validation_results, generation_results, start_time, 
                                                "Level 1 framework validation failed")
            
            # Level 2: Component logic validation + component generation
            logger.info("🔧 Level 2: Component logic validation + generation")
            level2_result = await self._execute_enhanced_level2_validation(blueprint, level1_result)
            validation_results.append(level2_result.validation_result)
            if level2_result.generated_components:
                generation_results.extend(level2_result.generated_components)
            
            if not level2_result.validation_result.passed:
                return self._create_failed_result(validation_results, generation_results, start_time,
                                                "Level 2 component validation failed")
            
            # Level 3: System integration + scaffold generation
            logger.info("🏗️ Level 3: System integration + scaffold generation")
            level3_result = await self._execute_enhanced_level3_validation(blueprint, level2_result.validation_result)
            validation_results.append(level3_result.validation_result)
            if level3_result.generated_scaffold:
                generation_results.append(level3_result.generated_scaffold)
            
            if not level3_result.validation_result.passed:
                return self._create_failed_result(validation_results, generation_results, start_time,
                                                "Level 3 integration validation failed")
            
            # Level 4: Semantic validation (unchanged)
            logger.info("🧠 Level 4: Semantic validation")
            level4_result = await self._execute_level4_validation(blueprint, level3_result.validation_result)
            validation_results.append(level4_result)
            
            if not level4_result.passed:
                return self._create_failed_result(validation_results, generation_results, start_time,
                                                "Level 4 semantic validation failed")
            
            # Finalize generation with both validation and generation results
            logger.info("✅ All validation levels passed - finalizing generation")
            generated_system = await self._finalize_enhanced_system_generation(
                blueprint, level4_result, generation_results
            )
            
            total_time = time.time() - start_time
            healing_applied = any(r.healing_applied for r in validation_results)
            
            result = SystemGenerationResult(
                successful=True,
                generated_system=generated_system,
                validation_levels_passed=4,
                validation_results=validation_results,
                healing_applied=healing_applied,
                total_execution_time=total_time,
                blueprint_path=getattr(blueprint, 'source_path', None),
                timestamp=time.time(),
                metadata={
                    "generation_integration": True,
                    "components_generated": len([r for r in generation_results if isinstance(r, GeneratedComponent)]),
                    "scaffold_generated": len([r for r in generation_results if isinstance(r, GeneratedScaffold)]) > 0,
                    "two_phase_pipeline": True
                }
            )
            
            logger.info(f"🎉 Enhanced system generation completed successfully in {total_time:.2f}s")
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ Enhanced system generation failed: {e}")
            
            return SystemGenerationResult(
                successful=False,
                validation_levels_passed=len([r for r in validation_results if r.passed]),
                validation_results=validation_results,
                total_execution_time=total_time,
                error_message=str(e),
                blueprint_path=getattr(blueprint, 'source_path', None),
                timestamp=time.time(),
                metadata={
                    "generation_integration": True,
                    "generation_failed": True,
                    "error_details": str(e)
                }
            )
    
    async def _execute_enhanced_level2_validation(self, blueprint: SystemBlueprint, 
                                                level1_result: ValidationResult) -> GenerationIntegratedResult:
        """
        Enhanced Level 2: Component logic validation + component generation.
        
        Integrates component generation into the validation pipeline while preserving
        all existing validation functionality and healing capabilities.
        """
        start_time = time.time()
        
        try:
            logger.debug("🔧 Starting enhanced Level 2 validation with component generation")
            
            # Execute standard Level 2 validation first
            base_validation = await super()._execute_level2_validation(blueprint, level1_result)
            
            # If validation failed and healing was not successful, don't generate
            if not base_validation.passed:
                logger.warning("⚠️ Level 2 validation failed - skipping component generation")
                return GenerationIntegratedResult(
                    validation_result=base_validation,
                    generation_success=False,
                    generation_time=time.time() - start_time
                )
            
            # Generate components for validated blueprint
            logger.info("🎯 Level 2 validation passed - generating components")
            generated_components = []
            component_generation_time = time.time()
            
            for component_def in blueprint.components:
                try:
                    # Generate component using Day 2 generator
                    generated_component = self.component_generator.generate_component_from_blueprint(component_def)
                    generated_components.append(generated_component)
                    
                    logger.debug(f"✅ Generated component: {generated_component.component_name}")
                    
                except Exception as gen_error:
                    logger.error(f"❌ Failed to generate component {component_def.get('name', 'unknown')}: {gen_error}")
                    # Don't fail validation for generation errors - log and continue
                    continue
            
            component_generation_time = time.time() - component_generation_time
            
            # Create enhanced result
            result = GenerationIntegratedResult(
                validation_result=base_validation,
                generated_components=generated_components,
                generation_success=len(generated_components) > 0,
                generation_time=component_generation_time,
                generation_metadata={
                    "components_generated": len(generated_components),
                    "generation_method": "two_phase_component_generation"
                }
            )
            
            logger.info(f"✅ Enhanced Level 2 completed: validation passed, {len(generated_components)} components generated")
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced Level 2 validation failed: {e}")
            
            # Return failed validation result
            failed_validation = ValidationResult(
                passed=False,
                level=ValidationLevel.LEVEL_2_COMPONENT_LOGIC,
                failures=[ValidationFailure(
                    component_name=None,
                    failure_type=FailureType.COMPONENT_LOGIC_ERROR,
                    error_message=f"Enhanced Level 2 validation failed: {e}",
                    level=ValidationLevel.LEVEL_2_COMPONENT_LOGIC,
                    timestamp=time.time()
                )],
                execution_time=time.time() - start_time
            )
            
            return GenerationIntegratedResult(
                validation_result=failed_validation,
                generation_success=False,
                generation_time=time.time() - start_time
            )
    
    async def _execute_enhanced_level3_validation(self, blueprint: SystemBlueprint,
                                                level2_result: ValidationResult) -> GenerationIntegratedResult:
        """
        Enhanced Level 3: System integration validation + scaffold generation.
        
        Integrates scaffold generation into the validation pipeline while preserving
        all existing validation functionality and healing capabilities.
        """
        start_time = time.time()
        
        try:
            logger.debug("🏗️ Starting enhanced Level 3 validation with scaffold generation")
            
            # Execute standard Level 3 validation first
            base_validation = await super()._execute_level3_validation(blueprint, level2_result)
            
            # If validation failed and healing was not successful, don't generate
            if not base_validation.passed:
                logger.warning("⚠️ Level 3 validation failed - skipping scaffold generation")
                return GenerationIntegratedResult(
                    validation_result=base_validation,
                    generation_success=False,
                    generation_time=time.time() - start_time
                )
            
            # Generate scaffold for validated system
            logger.info("🎯 Level 3 validation passed - generating system scaffold")
            scaffold_generation_time = time.time()
            
            try:
                # Generate complete scaffold using Day 1 generator
                generated_scaffold = self.scaffold_generator.generate_complete_scaffold(blueprint)
                
                scaffold_generation_time = time.time() - scaffold_generation_time
                
                logger.info(f"✅ System scaffold generated in {scaffold_generation_time:.3f}s")
                
                # Create enhanced result
                result = GenerationIntegratedResult(
                    validation_result=base_validation,
                    generated_scaffold=generated_scaffold,
                    generation_success=True,
                    generation_time=scaffold_generation_time,
                    generation_metadata={
                        "scaffold_components": len(generated_scaffold.components),
                        "scaffold_connections": len(generated_scaffold.connections),
                        "generation_method": "two_phase_scaffold_generation"
                    }
                )
                
                logger.info("✅ Enhanced Level 3 completed: validation passed, scaffold generated")
                return result
                
            except Exception as gen_error:
                logger.error(f"❌ Scaffold generation failed: {gen_error}")
                
                # Return validation success but generation failure
                return GenerationIntegratedResult(
                    validation_result=base_validation,
                    generation_success=False,
                    generation_time=time.time() - scaffold_generation_time,
                    generation_metadata={
                        "generation_error": str(gen_error),
                        "validation_passed": True
                    }
                )
                
        except Exception as e:
            logger.error(f"❌ Enhanced Level 3 validation failed: {e}")
            
            # Return failed validation result
            failed_validation = ValidationResult(
                passed=False,
                level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION,
                failures=[ValidationFailure(
                    component_name=None,
                    failure_type=FailureType.SYSTEM_INTEGRATION_ERROR,
                    error_message=f"Enhanced Level 3 validation failed: {e}",
                    level=ValidationLevel.LEVEL_3_SYSTEM_INTEGRATION,
                    timestamp=time.time()
                )],
                execution_time=time.time() - start_time
            )
            
            return GenerationIntegratedResult(
                validation_result=failed_validation,
                generation_success=False,
                generation_time=time.time() - start_time
            )
    
    async def _finalize_enhanced_system_generation(self, blueprint: SystemBlueprint, 
                                                 level4_result: ValidationResult,
                                                 generation_results: List[Any]) -> Dict[str, Any]:
        """
        Finalize system generation with both validation and generation artifacts.
        
        Combines the base system generation with generated components and scaffold.
        """
        try:
            logger.debug("🎯 Finalizing enhanced system generation")
            
            # Get base generated system
            base_system = await super()._finalize_system_generation(blueprint, level4_result)
            
            # Organize generation results
            generated_components = [r for r in generation_results if isinstance(r, GeneratedComponent)]
            generated_scaffolds = [r for r in generation_results if isinstance(r, GeneratedScaffold)]
            
            # Create enhanced system representation
            enhanced_system = {
                "base_system": base_system,
                "generation_artifacts": {
                    "components": {
                        "count": len(generated_components),
                        "components": [
                            {
                                "name": comp.component_name,
                                "class_name": comp.class_name,
                                "stream_interfaces": comp.stream_interfaces,
                                "business_methods": comp.business_methods,
                                "code_length": len(comp.component_code),
                                "generation_metadata": comp.generation_metadata
                            }
                            for comp in generated_components
                        ]
                    },
                    "scaffolds": {
                        "count": len(generated_scaffolds),
                        "scaffolds": [
                            {
                                "components": len(scaffold.components),
                                "connections": len(scaffold.connections),
                                "generation_time": scaffold.generation_time,
                                "main_py_length": len(scaffold.main_py_code),
                                "config_length": len(scaffold.config_code)
                            }
                            for scaffold in generated_scaffolds
                        ]
                    }
                },
                "validation_complete": True,
                "generation_complete": True,
                "two_phase_pipeline": True,
                "generation_timestamp": time.time()
            }
            
            logger.info("✅ Enhanced system generation finalized successfully")
            return enhanced_system
            
        except Exception as e:
            logger.error(f"❌ Enhanced system generation finalization failed: {e}")
            raise
    
    async def _initialize_generation_coordinator(self):
        """Initialize the generation coordinator for managing generation pipeline"""
        logger.debug("🔧 Initializing generation coordinator")
        
        try:
            # Import and initialize generation coordinator
            from .generation_coordinator import GenerationCoordinator
            
            self.generation_coordinator = GenerationCoordinator(
                scaffold_generator=self.scaffold_generator,
                component_generator=self.component_generator
            )
            
            logger.info("✅ Generation coordinator initialized")
            
        except ImportError:
            logger.warning("⚠️ GenerationCoordinator not available - using basic coordination")
            
            # Create minimal coordinator for basic functionality
            class BasicGenerationCoordinator:
                def __init__(self, scaffold_generator, component_generator):
                    self.scaffold_generator = scaffold_generator
                    self.component_generator = component_generator
                
                async def coordinate_generation(self, blueprint):
                    return {"status": "basic_coordination", "blueprint": blueprint}
            
            self.generation_coordinator = BasicGenerationCoordinator(
                self.scaffold_generator, self.component_generator
            )
    
    def _create_failed_result(self, validation_results: List[ValidationResult], 
                             generation_results: List[Any], start_time: float, 
                             error_message: str) -> SystemGenerationResult:
        """Create a failed system generation result with partial results"""
        total_time = time.time() - start_time
        healing_applied = any(r.healing_applied for r in validation_results)
        
        return SystemGenerationResult(
            successful=False,
            validation_levels_passed=len([r for r in validation_results if r.passed]),
            validation_results=validation_results,
            healing_applied=healing_applied,
            total_execution_time=total_time,
            error_message=error_message,
            timestamp=time.time(),
            metadata={
                "generation_integration": True,
                "partial_generation": len(generation_results) > 0,
                "components_generated": len([r for r in generation_results if isinstance(r, GeneratedComponent)]),
                "scaffold_generated": len([r for r in generation_results if isinstance(r, GeneratedScaffold)]) > 0
            }
        )


# Export main class
__all__ = ['EnhancedValidationDrivenOrchestrator', 'GenerationIntegratedResult']