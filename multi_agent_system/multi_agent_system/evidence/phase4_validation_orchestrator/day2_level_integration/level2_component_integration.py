"""
Level 2: Component Logic Validation with AST Healing Integration
Validates component logic and triggers AST healing for failures
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ComponentLogicResult:
    """Result of component logic validation"""
    passed: bool
    component_name: str
    failures: List[str]
    execution_time: float
    validation_details: Dict[str, Any] = None
    healing_candidate: bool = False


@dataclass
class ASTHealingResult:
    """Result of AST healing operation"""
    healing_successful: bool
    healed_component: Optional[Any] = None
    healing_details: Dict[str, Any] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0


class Level2ComponentValidator:
    """
    Level 2 Component Logic Validation - Integrates with Phase 2 component library
    
    Validates component logic correctness and triggers AST healing for failures
    """
    
    def __init__(self):
        self.component_registry = None
        self.schema_framework = None
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize component validation rules"""
        return {
            "source_component_rules": {
                "required_methods": ["generate", "setup"],
                "required_attributes": ["name", "config"],
                "data_output_validation": True
            },
            "transformer_component_rules": {
                "required_methods": ["transform", "setup"],
                "required_attributes": ["name", "config", "input_schema"],
                "input_output_validation": True
            },
            "sink_component_rules": {
                "required_methods": ["consume", "setup"],
                "required_attributes": ["name", "config"],
                "data_consumption_validation": True
            }
        }
    
    async def validate_component_logic(self, component) -> ComponentLogicResult:
        """
        Validate component logic using Phase 2 systems
        
        Args:
            component: Component to validate
            
        Returns:
            ComponentLogicResult with validation details
        """
        start_time = time.time()
        logger.debug(f"Starting component logic validation for {component.name}")
        
        try:
            # Initialize Phase 2 integrations if needed
            await self._ensure_phase2_integration()
            
            failures = []
            validation_details = {}
            
            # 1. Component type validation
            type_validation = await self._validate_component_type(component)
            if not type_validation["success"]:
                failures.extend(type_validation["failures"])
            validation_details["type_validation"] = type_validation
            
            # 2. Component interface validation
            interface_validation = await self._validate_component_interface(component)
            if not interface_validation["success"]:
                failures.extend(interface_validation["failures"])
            validation_details["interface_validation"] = interface_validation
            
            # 3. Component logic structure validation
            logic_validation = await self._validate_component_logic_structure(component)
            if not logic_validation["success"]:
                failures.extend(logic_validation["failures"])
            validation_details["logic_validation"] = logic_validation
            
            # 4. Component schema validation (Phase 2 integration)
            schema_validation = await self._validate_component_schema_compliance(component)
            if not schema_validation["success"]:
                failures.extend(schema_validation["failures"])
            validation_details["schema_validation"] = schema_validation
            
            # 5. Component behavioral validation
            behavioral_validation = await self._validate_component_behavior(component)
            if not behavioral_validation["success"]:
                failures.extend(behavioral_validation["failures"])
            validation_details["behavioral_validation"] = behavioral_validation
            
            # Determine if failures are healing candidates
            healing_candidate = self._is_healing_candidate(failures)
            
            result = ComponentLogicResult(
                passed=len(failures) == 0,
                component_name=component.name,
                failures=failures,
                execution_time=time.time() - start_time,
                validation_details=validation_details,
                healing_candidate=healing_candidate
            )
            
            if result.passed:
                logger.debug(f"Component {component.name} logic validation passed in {result.execution_time:.2f}s")
            else:
                logger.warning(f"Component {component.name} logic validation failed: {failures}")
            
            return result
            
        except Exception as e:
            logger.error(f"Component logic validation error for {component.name}: {e}")
            return ComponentLogicResult(
                passed=False,
                component_name=component.name,
                failures=[f"Validation exception: {e}"],
                execution_time=time.time() - start_time
            )
    
    async def _ensure_phase2_integration(self):
        """Ensure Phase 2 component systems are integrated"""
        if self.component_registry is None:
            try:
                # Import Phase 2 component registry
                from autocoder.validation.component_registry import ComponentRegistry
                self.component_registry = ComponentRegistry()
                logger.debug("Phase 2 component registry integrated")
            except ImportError:
                logger.warning("Phase 2 component registry not available - using fallback")
                self.component_registry = self._create_fallback_registry()
        
        if self.schema_framework is None:
            try:
                # Import Phase 2 schema framework
                from autocoder.validation.schema_framework import SchemaFramework
                self.schema_framework = SchemaFramework()
                logger.debug("Phase 2 schema framework integrated")
            except ImportError:
                logger.warning("Phase 2 schema framework not available - using fallback")
                self.schema_framework = self._create_fallback_schema_framework()
    
    def _create_fallback_registry(self):
        """Create fallback component registry"""
        class FallbackRegistry:
            def is_component_registered(self, component_type):
                # Accept common component types
                return component_type in ["Source", "Transformer", "Sink", "Store"]
            
            def get_component_metadata(self, component_type):
                return {"type": component_type, "validated": False}
        
        return FallbackRegistry()
    
    def _create_fallback_schema_framework(self):
        """Create fallback schema framework"""
        class FallbackSchemaFramework:
            def validate_component_schema(self, component):
                return type('Result', (), {
                    'valid': True,
                    'errors': [],
                    'warnings': ['Phase 2 schema framework not available']
                })()
        
        return FallbackSchemaFramework()
    
    async def _validate_component_type(self, component) -> Dict[str, Any]:
        """Validate component type is registered and supported"""
        try:
            component_type = getattr(component, 'type', 'Unknown')
            
            if not self.component_registry.is_component_registered(component_type):
                return {
                    "success": False,
                    "failures": [f"Component type '{component_type}' not registered in Phase 2 component registry"]
                }
            
            # Get component metadata for additional validation
            metadata = self.component_registry.get_component_metadata(component_type)
            
            return {
                "success": True,
                "component_type": component_type,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Component type validation failed: {e}"]
            }
    
    async def _validate_component_interface(self, component) -> Dict[str, Any]:
        """Validate component implements required interface"""
        try:
            component_type = getattr(component, 'type', 'Unknown')
            failures = []
            
            # Get validation rules for component type
            type_key = f"{component_type.lower()}_component_rules"
            rules = self.validation_rules.get(type_key, {})
            
            # Check required methods
            required_methods = rules.get("required_methods", [])
            for method_name in required_methods:
                if not hasattr(component, method_name):
                    failures.append(f"Component missing required method: {method_name}")
                elif not callable(getattr(component, method_name)):
                    failures.append(f"Component {method_name} is not callable")
            
            # Check required attributes
            required_attributes = rules.get("required_attributes", [])
            for attr_name in required_attributes:
                if not hasattr(component, attr_name):
                    failures.append(f"Component missing required attribute: {attr_name}")
            
            return {
                "success": len(failures) == 0,
                "failures": failures,
                "rules_applied": type_key,
                "methods_checked": len(required_methods),
                "attributes_checked": len(required_attributes)
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Component interface validation failed: {e}"]
            }
    
    async def _validate_component_logic_structure(self, component) -> Dict[str, Any]:
        """Validate component logic structure and implementation"""
        try:
            failures = []
            structure_details = {}
            
            # Check if component has implementation
            if hasattr(component, 'generate') and callable(component.generate):
                # Validate Source component logic
                logic_check = await self._validate_source_logic(component)
                if not logic_check["success"]:
                    failures.extend(logic_check["failures"])
                structure_details["source_logic"] = logic_check
                
            elif hasattr(component, 'transform') and callable(component.transform):
                # Validate Transformer component logic
                logic_check = await self._validate_transformer_logic(component)
                if not logic_check["success"]:
                    failures.extend(logic_check["failures"])
                structure_details["transformer_logic"] = logic_check
                
            elif hasattr(component, 'consume') and callable(component.consume):
                # Validate Sink component logic
                logic_check = await self._validate_sink_logic(component)
                if not logic_check["success"]:
                    failures.extend(logic_check["failures"])
                structure_details["sink_logic"] = logic_check
            
            else:
                failures.append("Component does not implement any recognized logic pattern")
            
            return {
                "success": len(failures) == 0,
                "failures": failures,
                "structure_details": structure_details
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Component logic structure validation failed: {e}"]
            }
    
    async def _validate_source_logic(self, component) -> Dict[str, Any]:
        """Validate Source component specific logic"""
        try:
            failures = []
            
            # Check if generate method is properly implemented
            import inspect
            generate_sig = inspect.signature(component.generate)
            
            # Source generate should not require input parameters (besides self)
            params = [p for name, p in generate_sig.parameters.items() if name != 'self']
            if len(params) > 0:
                failures.append("Source component generate method should not require input parameters")
            
            # Check if component has data generation logic
            if hasattr(component, 'config') and isinstance(component.config, dict):
                config = component.config
                if 'data_source' not in config and 'generation_params' not in config:
                    failures.append("Source component missing data generation configuration")
            
            return {
                "success": len(failures) == 0,
                "failures": failures,
                "signature_validated": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Source logic validation failed: {e}"]
            }
    
    async def _validate_transformer_logic(self, component) -> Dict[str, Any]:
        """Validate Transformer component specific logic"""
        try:
            failures = []
            
            # Check if transform method is properly implemented
            import inspect
            transform_sig = inspect.signature(component.transform)
            
            # Transformer transform should require input parameter
            params = [p for name, p in transform_sig.parameters.items() if name != 'self']
            if len(params) == 0:
                failures.append("Transformer component transform method should require input parameter")
            
            # Check if component has input schema definition
            if not hasattr(component, 'input_schema'):
                failures.append("Transformer component missing input_schema definition")
            
            return {
                "success": len(failures) == 0,
                "failures": failures,
                "signature_validated": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Transformer logic validation failed: {e}"]
            }
    
    async def _validate_sink_logic(self, component) -> Dict[str, Any]:
        """Validate Sink component specific logic"""
        try:
            failures = []
            
            # Check if consume method is properly implemented
            import inspect
            consume_sig = inspect.signature(component.consume)
            
            # Sink consume should require input parameter
            params = [p for name, p in consume_sig.parameters.items() if name != 'self']
            if len(params) == 0:
                failures.append("Sink component consume method should require input parameter")
            
            # Check if component has consumption configuration
            if hasattr(component, 'config') and isinstance(component.config, dict):
                config = component.config
                if 'output_target' not in config and 'storage_config' not in config:
                    failures.append("Sink component missing output/storage configuration")
            
            return {
                "success": len(failures) == 0,
                "failures": failures,
                "signature_validated": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Sink logic validation failed: {e}"]
            }
    
    async def _validate_component_schema_compliance(self, component) -> Dict[str, Any]:
        """Validate component complies with Phase 2 schema requirements"""
        try:
            # Use Phase 2 schema framework for validation
            schema_result = self.schema_framework.validate_component_schema(component)
            
            if not schema_result.valid:
                return {
                    "success": False,
                    "failures": [f"Schema validation failed: {error}" for error in schema_result.errors]
                }
            
            return {
                "success": True,
                "schema_validated": True,
                "warnings": getattr(schema_result, 'warnings', [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Schema compliance validation failed: {e}"]
            }
    
    async def _validate_component_behavior(self, component) -> Dict[str, Any]:
        """Validate component behavioral requirements"""
        try:
            failures = []
            behavioral_details = {}
            
            # Check if component has proper setup method
            if hasattr(component, 'setup') and callable(component.setup):
                try:
                    # Test setup method (should not throw for basic validation)
                    import inspect
                    setup_sig = inspect.signature(component.setup)
                    behavioral_details["setup_signature"] = str(setup_sig)
                except Exception as e:
                    failures.append(f"Component setup method validation failed: {e}")
            else:
                failures.append("Component missing setup method")
            
            # Check if component has proper error handling
            if hasattr(component, 'handle_error'):
                behavioral_details["error_handling"] = True
            else:
                # Not a failure, but note for improvement
                behavioral_details["error_handling"] = False
            
            # Check if component has cleanup method
            if hasattr(component, 'cleanup'):
                behavioral_details["cleanup_method"] = True
            else:
                behavioral_details["cleanup_method"] = False
            
            return {
                "success": len(failures) == 0,
                "failures": failures,
                "behavioral_details": behavioral_details
            }
            
        except Exception as e:
            return {
                "success": False,
                "failures": [f"Component behavioral validation failed: {e}"]
            }
    
    def _is_healing_candidate(self, failures: List[str]) -> bool:
        """Determine if validation failures are candidates for AST healing"""
        healing_indicators = [
            "missing required method",
            "method is not callable",
            "missing required attribute",
            "logic structure",
            "signature"
        ]
        
        # If any failure contains healing indicators, it's a candidate
        for failure in failures:
            for indicator in healing_indicators:
                if indicator.lower() in failure.lower():
                    return True
        
        return False


class Level2ASTHealingIntegrator:
    """
    AST Healing Integration for Level 2 component logic failures
    
    Integrates with Phase 1 AST healing system to fix component logic issues
    """
    
    def __init__(self):
        self.ast_healer = None
    
    async def heal_component_logic(self, component, validation_failures: List[str]) -> ASTHealingResult:
        """
        Heal component logic issues using AST healing
        
        Args:
            component: Component with logic issues
            validation_failures: List of validation failure messages
            
        Returns:
            ASTHealingResult with healing outcome
        """
        start_time = time.time()
        logger.info(f"Starting AST healing for component {component.name}")
        
        try:
            # Initialize AST healer if needed
            await self._ensure_ast_healer()
            
            # Convert validation failures to healing targets
            healing_targets = self._convert_failures_to_targets(validation_failures)
            
            if not healing_targets:
                return ASTHealingResult(
                    healing_successful=False,
                    error_message="No healable targets identified from validation failures",
                    execution_time=time.time() - start_time
                )
            
            # Apply AST healing (single attempt, fail hard if unsuccessful)
            healing_result = await self._apply_ast_healing(component, healing_targets)
            
            return ASTHealingResult(
                healing_successful=healing_result["success"],
                healed_component=healing_result.get("healed_component"),
                healing_details=healing_result.get("details", {}),
                error_message=healing_result.get("error"),
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"AST healing failed for component {component.name}: {e}")
            return ASTHealingResult(
                healing_successful=False,
                error_message=f"AST healing exception: {e}",
                execution_time=time.time() - start_time
            )
    
    async def _ensure_ast_healer(self):
        """Ensure AST healer is initialized"""
        if self.ast_healer is None:
            try:
                # Import Phase 1 AST healing system
                from autocoder.healing.ast_self_healing import ASTSelfHealing
                self.ast_healer = ASTSelfHealing()
                logger.debug("Phase 1 AST healer integrated")
            except ImportError:
                logger.warning("Phase 1 AST healer not available - using fallback")
                self.ast_healer = self._create_fallback_healer()
    
    def _create_fallback_healer(self):
        """Create fallback AST healer"""
        class FallbackHealer:
            async def heal_component_ast(self, component, targets):
                return {
                    "success": False,
                    "error": "AST healer not available - Phase 1 integration required"
                }
        
        return FallbackHealer()
    
    def _convert_failures_to_targets(self, validation_failures: List[str]) -> List[Dict[str, Any]]:
        """Convert validation failures to AST healing targets"""
        healing_targets = []
        
        for failure in validation_failures:
            if "missing required method" in failure.lower():
                # Extract method name and create healing target
                method_name = self._extract_method_name(failure)
                if method_name:
                    healing_targets.append({
                        "type": "missing_method",
                        "method_name": method_name,
                        "priority": "high"
                    })
            
            elif "method is not callable" in failure.lower():
                method_name = self._extract_method_name(failure)
                if method_name:
                    healing_targets.append({
                        "type": "fix_method_callable",
                        "method_name": method_name,
                        "priority": "high"
                    })
            
            elif "missing required attribute" in failure.lower():
                attr_name = self._extract_attribute_name(failure)
                if attr_name:
                    healing_targets.append({
                        "type": "missing_attribute",
                        "attribute_name": attr_name,
                        "priority": "medium"
                    })
        
        return healing_targets
    
    def _extract_method_name(self, failure_message: str) -> Optional[str]:
        """Extract method name from failure message"""
        import re
        
        # Look for patterns like "missing required method: method_name"
        pattern = r"method[:\s]+(\w+)"
        match = re.search(pattern, failure_message, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_attribute_name(self, failure_message: str) -> Optional[str]:
        """Extract attribute name from failure message"""
        import re
        
        # Look for patterns like "missing required attribute: attr_name"
        pattern = r"attribute[:\s]+(\w+)"
        match = re.search(pattern, failure_message, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None
    
    async def _apply_ast_healing(self, component, healing_targets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply AST healing to component"""
        try:
            # Use AST healer to fix component
            healing_result = await self.ast_healer.heal_component_ast(component, healing_targets)
            
            return {
                "success": healing_result.get("successful", False),
                "healed_component": healing_result.get("healed_component"),
                "details": {
                    "targets_processed": len(healing_targets),
                    "changes_applied": healing_result.get("changes_applied", []),
                    "healing_strategy": "ast_code_generation"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AST healing application failed: {e}"
            }


# Integration functions for ValidationDrivenOrchestrator
async def create_component_validator() -> Level2ComponentValidator:
    """Create and return Level 2 component validator"""
    return Level2ComponentValidator()


async def create_ast_healing_integrator() -> Level2ASTHealingIntegrator:
    """Create and return AST healing integrator"""
    return Level2ASTHealingIntegrator()


# Test harness
if __name__ == "__main__":
    async def test_component_validation():
        # Create mock component for testing
        class MockComponent:
            def __init__(self, name, component_type):
                self.name = name
                self.type = component_type
                self.config = {}
            
            def generate(self):
                return {"data": "test"}
            
            def setup(self):
                pass
        
        component = MockComponent("test_source", "Source")
        
        validator = Level2ComponentValidator()
        result = await validator.validate_component_logic(component)
        
        print(f"Component validation result: {result.passed}")
        print(f"Component: {result.component_name}")
        print(f"Execution time: {result.execution_time:.2f}s")
        
        if not result.passed:
            print("Failures:")
            for failure in result.failures:
                print(f"  - {failure}")
        
        return result
    
    asyncio.run(test_component_validation())