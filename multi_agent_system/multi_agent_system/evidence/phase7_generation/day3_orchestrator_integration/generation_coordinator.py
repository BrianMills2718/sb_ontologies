#!/usr/bin/env python3
"""
Generation Coordinator: Manages Two-Phase Generation Pipeline
=============================================================

Coordinates scaffold generation (Phase 1) and component generation (Phase 2)
to create complete SystemExecutionHarness deployments. Ensures proper
sequencing, dependency management, and output coordination.

Key Responsibilities:
- Coordinate scaffold + component generation sequence
- Manage inter-phase dependencies
- Handle generation output organization
- Provide unified generation interface
"""

import os
import sys
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day1_system_scaffold_generator'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day2_component_logic_generator'))

from system_scaffold_generator import SystemScaffoldGenerator, GeneratedScaffold
from harness_component_generator import HarnessComponentGenerator, GeneratedComponent

# Import blueprint types from correct locations
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day1_system_scaffold_generator'))
from blueprint_types import SystemBlueprint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../day2_component_logic_generator'))
from blueprint_types import ComponentLogic

logger = logging.getLogger(__name__)


@dataclass
class CoordinatedGenerationResult:
    """Result of coordinated two-phase generation"""
    success: bool
    scaffold_result: Optional[GeneratedScaffold] = None
    component_results: List[GeneratedComponent] = None
    total_generation_time: float = 0.0
    phase1_time: float = 0.0
    phase2_time: float = 0.0
    output_directory: Optional[str] = None
    generated_files: List[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


class GenerationCoordinator:
    """
    Coordinates two-phase generation pipeline: scaffold generation + component generation.
    
    Manages the complete pipeline from SystemBlueprint to deployable SystemExecutionHarness.
    """
    
    def __init__(self, scaffold_generator: SystemScaffoldGenerator = None,
                 component_generator: HarnessComponentGenerator = None,
                 output_base_dir: str = "generated_systems"):
        
        self.scaffold_generator = scaffold_generator or SystemScaffoldGenerator()
        self.component_generator = component_generator or HarnessComponentGenerator()
        self.output_base_dir = output_base_dir
        
        # Generation coordination state
        self.current_generation = {}
        self.generation_history = []
        
        logger.info("🎯 GenerationCoordinator initialized for two-phase pipeline")
    
    async def coordinate_full_generation(self, blueprint: SystemBlueprint, 
                                       output_dir: str = None) -> CoordinatedGenerationResult:
        """
        Coordinate complete two-phase generation pipeline.
        
        Phase 1: Generate system scaffold (main.py, config, etc.)
        Phase 2: Generate component logic (HarnessComponent classes)
        
        Args:
            blueprint: SystemBlueprint to generate from
            output_dir: Output directory for generated files
            
        Returns:
            CoordinatedGenerationResult with complete generation artifacts
        """
        start_time = time.time()
        
        try:
            # Prepare output directory
            if not output_dir:
                output_dir = self._create_output_directory(blueprint)
            os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"🚀 Starting coordinated generation for: {blueprint.description}")
            logger.info(f"📁 Output directory: {output_dir}")
            
            # Phase 1: Generate system scaffold
            logger.info("🏗️ Phase 1: Generating system scaffold")
            phase1_start = time.time()
            
            scaffold_result = await self._execute_phase1_generation(blueprint, output_dir)
            phase1_time = time.time() - phase1_start
            
            if not scaffold_result:
                return CoordinatedGenerationResult(
                    success=False,
                    phase1_time=phase1_time,
                    total_generation_time=time.time() - start_time,
                    error_message="Phase 1 scaffold generation failed",
                    output_directory=output_dir
                )
            
            logger.info(f"✅ Phase 1 completed in {phase1_time:.3f}s")
            
            # Phase 2: Generate component logic
            logger.info("🔧 Phase 2: Generating component logic")
            phase2_start = time.time()
            
            component_results = await self._execute_phase2_generation(blueprint, output_dir, scaffold_result)
            phase2_time = time.time() - phase2_start
            
            logger.info(f"✅ Phase 2 completed in {phase2_time:.3f}s - {len(component_results)} components generated")
            
            # Write generated files
            generated_files = await self._write_generation_artifacts(
                scaffold_result, component_results, output_dir
            )
            
            # Create coordination result
            total_time = time.time() - start_time
            
            result = CoordinatedGenerationResult(
                success=True,
                scaffold_result=scaffold_result,
                component_results=component_results,
                total_generation_time=total_time,
                phase1_time=phase1_time,
                phase2_time=phase2_time,
                output_directory=output_dir,
                generated_files=generated_files,
                metadata={
                    "blueprint_description": blueprint.description,
                    "components_count": len(blueprint.components),
                    "scaffold_components": len(scaffold_result.components),
                    "generated_components": len(component_results),
                    "generation_timestamp": time.time(),
                    "two_phase_pipeline": True
                }
            )
            
            # Record generation history
            self.generation_history.append(result)
            
            logger.info(f"🎉 Coordinated generation completed successfully in {total_time:.3f}s")
            logger.info(f"📦 Generated {len(generated_files)} files in {output_dir}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Coordinated generation failed: {e}")
            
            return CoordinatedGenerationResult(
                success=False,
                total_generation_time=time.time() - start_time,
                error_message=str(e),
                output_directory=output_dir
            )
    
    async def _execute_phase1_generation(self, blueprint: SystemBlueprint, 
                                       output_dir: str) -> Optional[GeneratedScaffold]:
        """Execute Phase 1: System scaffold generation"""
        try:
            logger.debug("🏗️ Executing Phase 1: System scaffold generation")
            
            # Validate blueprint for scaffold generation
            is_valid, errors = self.scaffold_generator.validate_blueprint_for_scaffold(blueprint)
            if not is_valid:
                logger.error(f"❌ Blueprint validation failed for scaffold generation: {errors}")
                return None
            
            # Generate complete scaffold
            scaffold_result = self.scaffold_generator.generate_complete_scaffold(blueprint)
            
            logger.debug(f"✅ Phase 1 generated scaffold with {len(scaffold_result.components)} components")
            return scaffold_result
            
        except Exception as e:
            logger.error(f"❌ Phase 1 generation failed: {e}")
            return None
    
    async def _execute_phase2_generation(self, blueprint: SystemBlueprint, 
                                       output_dir: str, 
                                       scaffold_result: GeneratedScaffold) -> List[GeneratedComponent]:
        """Execute Phase 2: Component logic generation"""
        try:
            logger.debug("🔧 Executing Phase 2: Component logic generation")
            
            component_results = []
            
            # Generate each component from blueprint
            for component_def in blueprint.components:
                try:
                    # Generate component using Day 2 generator
                    generated_component = self.component_generator.generate_component_from_blueprint(component_def)
                    component_results.append(generated_component)
                    
                    logger.debug(f"✅ Generated component: {generated_component.component_name}")
                    
                except Exception as comp_error:
                    logger.error(f"❌ Failed to generate component {component_def.get('name', 'unknown')}: {comp_error}")
                    # Continue with other components
                    continue
            
            logger.debug(f"✅ Phase 2 generated {len(component_results)} components")
            return component_results
            
        except Exception as e:
            logger.error(f"❌ Phase 2 generation failed: {e}")
            return []
    
    async def _write_generation_artifacts(self, scaffold_result: GeneratedScaffold,
                                        component_results: List[GeneratedComponent],
                                        output_dir: str) -> List[str]:
        """Write all generation artifacts to output directory"""
        generated_files = []
        
        try:
            logger.debug(f"📝 Writing generation artifacts to {output_dir}")
            
            # Write scaffold files
            # 1. Main.py
            main_py_path = os.path.join(output_dir, "main.py")
            with open(main_py_path, 'w') as f:
                f.write(scaffold_result.main_py_code)
            generated_files.append(main_py_path)
            
            # 2. System config
            config_py_path = os.path.join(output_dir, "system_config.py")
            with open(config_py_path, 'w') as f:
                f.write(scaffold_result.config_code)
            generated_files.append(config_py_path)
            
            # 3. Requirements.txt
            requirements_path = os.path.join(output_dir, "requirements.txt")
            with open(requirements_path, 'w') as f:
                f.write(self._generate_requirements_txt())
            generated_files.append(requirements_path)
            
            # 4. Docker file
            dockerfile_path = os.path.join(output_dir, "Dockerfile")
            with open(dockerfile_path, 'w') as f:
                f.write(self._generate_dockerfile())
            generated_files.append(dockerfile_path)
            
            # Write component files
            components_dir = os.path.join(output_dir, "components")
            os.makedirs(components_dir, exist_ok=True)
            
            # Component __init__.py
            init_py_path = os.path.join(components_dir, "__init__.py")
            with open(init_py_path, 'w') as f:
                f.write('# Generated components package\n')
            generated_files.append(init_py_path)
            
            # Individual component files
            for component in component_results:
                component_file = f"{component.component_name}.py"
                component_path = os.path.join(components_dir, component_file)
                
                with open(component_path, 'w') as f:
                    f.write(component.component_code)
                generated_files.append(component_path)
            
            # Write generation metadata
            metadata_path = os.path.join(output_dir, "generation_metadata.json")
            with open(metadata_path, 'w') as f:
                import json
                metadata = {
                    "generation_timestamp": time.time(),
                    "scaffold": {
                        "components": len(scaffold_result.components),
                        "connections": len(scaffold_result.connections),
                        "generation_time": scaffold_result.generation_time
                    },
                    "components": [
                        {
                            "name": comp.component_name,
                            "class_name": comp.class_name,
                            "business_methods": comp.business_methods
                        }
                        for comp in component_results
                    ],
                    "two_phase_pipeline": True
                }
                json.dump(metadata, f, indent=2)
            generated_files.append(metadata_path)
            
            logger.info(f"✅ Wrote {len(generated_files)} files to {output_dir}")
            return generated_files
            
        except Exception as e:
            logger.error(f"❌ Failed to write generation artifacts: {e}")
            return generated_files  # Return partial results
    
    def _create_output_directory(self, blueprint: SystemBlueprint) -> str:
        """Create output directory for generation"""
        # Create safe directory name from blueprint description
        safe_name = "".join(c for c in blueprint.description if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()[:50]
        
        timestamp = int(time.time())
        dir_name = f"{safe_name}_{timestamp}"
        
        return os.path.join(self.output_base_dir, dir_name)
    
    def _generate_requirements_txt(self) -> str:
        """Generate requirements.txt for generated system"""
        return """# Generated requirements for SystemExecutionHarness
asyncio
logging
typing
dataclasses
pathlib
json
time

# HarnessComponent dependencies
# Add these paths to evidence/phase6_harness for full functionality:
# evidence.phase6_harness.day1_harness_component.harness_component
# evidence.phase2_component_library.day1_core_component_classes.enhanced_base

# Component-specific dependencies (add as needed)
# fastapi
# uvicorn
# redis
# aiosqlite
# numpy
"""
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile for generated system"""
        return """# Generated Dockerfile for SystemExecutionHarness
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy generated system
COPY . .

# Expose default port (adjust as needed)
EXPOSE 8000

# Run the generated system
CMD ["python", "main.py"]
"""
    
    async def validate_generation_prerequisites(self, blueprint: SystemBlueprint) -> Tuple[bool, List[str]]:
        """
        Validate that all prerequisites for generation are met.
        
        Args:
            blueprint: SystemBlueprint to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate blueprint structure
        if not blueprint.description:
            errors.append("Blueprint must have a description")
        
        if not blueprint.components:
            errors.append("Blueprint must contain at least one component")
        
        # Validate each component
        for i, component in enumerate(blueprint.components):
            if not component.get('name'):
                errors.append(f"Component {i} is missing 'name' field")
            
            if not component.get('type'):
                errors.append(f"Component {i} is missing 'type' field")
        
        # Check for duplicate component names
        component_names = [comp.get('name') for comp in blueprint.components if comp.get('name')]
        if len(component_names) != len(set(component_names)):
            errors.append("Duplicate component names found")
        
        # Validate scaffold generator prerequisites
        scaffold_valid, scaffold_errors = self.scaffold_generator.validate_blueprint_for_scaffold(blueprint)
        if not scaffold_valid:
            errors.extend([f"Scaffold validation: {err}" for err in scaffold_errors])
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ Generation prerequisites validation passed")
        else:
            logger.warning(f"⚠️ Generation prerequisites validation failed: {errors}")
        
        return is_valid, errors
    
    def get_generation_history(self) -> List[CoordinatedGenerationResult]:
        """Get history of coordinated generations"""
        return self.generation_history.copy()
    
    def get_current_generation_status(self) -> Dict[str, Any]:
        """Get status of current generation if any"""
        return self.current_generation.copy()


# Export main class
__all__ = ['GenerationCoordinator', 'CoordinatedGenerationResult']