#!/usr/bin/env python3
"""
AST-Based Self-Healing System - Phase 7 Implementation
Automatically fixes component validation failures using Abstract Syntax Tree manipulation

This implements the core self-healing capability by:
1. Analyzing component validation failures
2. Generating precise AST-based fixes
3. Applying fixes automatically
4. Re-validating components after healing
5. Retrying system generation with healed components
"""
import ast
import inspect
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from tests.component_test_runner import ComponentTestResult
from blueprint_language.validation_gate import ComponentValidationGate, ValidationGateResult
from .component_name_utils import find_best_class_name_match, generate_class_name_variants


class FixType(Enum):
    """Types of fixes that can be applied"""
    ADD_MISSING_METHOD = "add_missing_method"
    CONVERT_SYNC_TO_ASYNC = "convert_sync_to_async"
    ADD_INHERITANCE = "add_inheritance"
    FIX_METHOD_SIGNATURE = "fix_method_signature"
    ADD_IMPORT = "add_import"
    FIX_SUPER_CALL = "fix_super_call"
    ADD_DOCSTRING = "add_docstring"
    FIX_CONSTRUCTOR_SIGNATURE = "fix_constructor_signature"


@dataclass
class ASTFix:
    """Represents a single AST-based fix"""
    fix_type: FixType
    target_node: Optional[ast.AST]
    target_line: Optional[int]
    target_method: Optional[str]
    fix_description: str
    new_code: str
    confidence: float  # 0.0 to 1.0


@dataclass
class HealingResult:
    """Result of applying healing to a component"""
    component_name: str
    original_file: Path
    healed_file: Path
    fixes_applied: List[ASTFix]
    healing_successful: bool
    validation_passed_after_healing: bool
    error_message: Optional[str] = None


class ComponentASTAnalyzer:
    """Analyzes component AST to identify fixable issues"""
    
    def analyze_component_failures(self, 
                                 component_file: Path, 
                                 test_result: ComponentTestResult) -> List[ASTFix]:
        """Analyze component failures and generate specific AST fixes"""
        
        fixes = []
        
        try:
            with open(component_file, 'r') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            
            # Find the component class
            component_class = self._find_component_class(tree, test_result.component_name)
            
            if not component_class:
                return fixes
            
            # Analyze contract validation failures
            if not test_result.contract_validation_passed:
                fixes.extend(self._analyze_contract_failures(component_class, test_result))
            
            # Analyze functional test failures
            if not test_result.functional_test_passed:
                fixes.extend(self._analyze_functional_failures(component_class, test_result))
        
        except Exception as e:
            logging.error(f"Error analyzing component {component_file}: {e}")
        
        return fixes
    
    # ... (rest of analyzer methods remain the same)


class SelfHealingSystem:
    """
    Main self-healing system that automatically fixes component validation failures.
    
    This implements the core self-healing loop:
    1. Run component validation
    2. If failures occur, analyze and generate fixes
    3. Apply fixes using AST manipulation
    4. Re-validate components
    5. Retry system generation if all components pass
    """
    
    def __init__(self, max_healing_attempts: int = 3):
        self.max_healing_attempts = max_healing_attempts
        self.analyzer = ComponentASTAnalyzer()
        self.code_generator = ASTCodeGenerator()
        self.validation_gate = ComponentValidationGate(strict_mode=True)
        
        # Track healing attempts per component to prevent infinite loops
        self.component_healing_attempts = {}  # component_name -> attempt_count
        self.component_code_history = {}  # component_name -> list of code versions
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SelfHealingSystem")
    
    async def heal_and_validate_components(self, 
                                         components_dir: Path,
                                         system_name: str) -> Tuple[bool, List[HealingResult]]:
        """
        Main healing loop: validate components, heal failures, re-validate.
        
        Returns:
            (healing_successful, healing_results)
        """
        
        # Reset healing counters for new session
        self.component_healing_attempts.clear()
        self.component_code_history.clear()
        
        self.logger.info(f"🔧 Starting self-healing for system '{system_name}'")
        self.logger.info(f"   Components directory: {components_dir}")
        self.logger.info(f"   Max healing attempts: {self.max_healing_attempts}")
        
        healing_results = []
        components_stuck_in_loop = set()  # Track components that are stuck
        
        for attempt in range(self.max_healing_attempts):
            self.logger.info(f"\n🔄 Healing attempt {attempt + 1}/{self.max_healing_attempts}")
            
            # Run component validation
            validation_result = await self.validation_gate.validate_components_for_system_generation(
                components_dir, system_name
            )
            
            # If validation passes, we're done
            if validation_result.can_proceed_to_generation:
                self.logger.info("✅ All components passed validation - healing successful!")
                return True, healing_results
            
            # If validation fails, attempt healing
            self.logger.info(f"🚨 {validation_result.failed_components} components failed validation")
            
            # Heal each failed component
            attempt_healing_results = await self._heal_failed_components(
                components_dir, validation_result.detailed_results
            )
            healing_results.extend(attempt_healing_results)
            
            # Check for components stuck in loops
            for result in attempt_healing_results:
                if "No progress detected" in (result.error_message or "") or \
                   "Circuit breaker activated" in (result.error_message or ""):
                    components_stuck_in_loop.add(result.component_name)
            
            # Check if any healing was applied AND made progress
            healed_components = [r for r in attempt_healing_results 
                               if r.healing_successful and r.component_name not in components_stuck_in_loop]
            
            if not healed_components:
                self.logger.error("❌ No healing could be applied or all components stuck in loops - giving up")
                self.logger.error(f"   Components stuck: {components_stuck_in_loop}")
                break
            
            # Check if we're making progress overall
            if len(components_stuck_in_loop) >= validation_result.failed_components:
                self.logger.error("❌ All failing components are stuck in healing loops - giving up")
                break
            
            self.logger.info(f"🔧 Applied healing to {len(healed_components)} components")
            self.logger.info(f"⚠️  {len(components_stuck_in_loop)} components stuck in loops")
        
        self.logger.error(f"❌ Self-healing failed after {attempt + 1} attempts")
        return False, healing_results
    
    # ... (rest of healing methods with current retry logic)