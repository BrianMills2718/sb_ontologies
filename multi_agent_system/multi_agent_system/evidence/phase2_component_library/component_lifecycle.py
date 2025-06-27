#!/usr/bin/env python3
"""
Component Lifecycle Management for V5.0 Validation-Driven Architecture
Implements complete component creation, validation, and teardown with fail-hard principles
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import logging
import time
import uuid
from enum import Enum

# Import from existing Phase 2 components
from day1_core_component_classes.component_registry_implementation import (
    ComponentRegistry, ComponentRegistryError, component_registry
)
from day1_core_component_classes.schema_framework_implementation import (
    SchemaValidator, SchemaValidationError, schema_validator
)


class ComponentLifecycleState(Enum):
    """Component lifecycle states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    VALIDATING = "validating"
    VALIDATED = "validated"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"


class ComponentLifecycleError(Exception):
    """Raised when component lifecycle operations fail - no fallbacks available"""
    pass


@dataclass
class ComponentSpec:
    """Specification for component creation"""
    name: str
    component_type: str
    config: Dict[str, Any]
    dependencies: List[str] = None
    schema_requirements: Dict[str, str] = None
    lifecycle_hooks: Dict[str, str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.schema_requirements is None:
            self.schema_requirements = {}
        if self.lifecycle_hooks is None:
            self.lifecycle_hooks = {}


@dataclass
class ValidationResult:
    """Result of component validation"""
    success: bool
    component_name: str
    validation_type: str
    errors: List[str] = None
    warnings: List[str] = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class LifecycleValidationResult:
    """Result of complete lifecycle validation"""
    success: bool
    component_name: str
    states_validated: List[ComponentLifecycleState]
    failed_state: Optional[ComponentLifecycleState] = None
    validation_results: List[ValidationResult] = None
    total_execution_time: float = 0.0
    
    def __post_init__(self):
        if self.validation_results is None:
            self.validation_results = []


class ComponentLifecycle:
    """
    V5.0 Component Lifecycle Management with Fail-Hard Principles
    
    Manages complete component lifecycle from creation to destruction.
    No fallback mechanisms or graceful degradation - all operations must succeed.
    """
    
    def __init__(self, component_registry: ComponentRegistry = None, schema_validator: SchemaValidator = None):
        self.logger = logging.getLogger("ComponentLifecycle")
        
        # Use provided instances, create new ones if none provided
        if component_registry is not None:
            self.component_registry = component_registry
        else:
            from day1_core_component_classes.component_registry_implementation import ComponentRegistry
            self.component_registry = ComponentRegistry()
            
        if schema_validator is not None:
            self.schema_validator = schema_validator
        else:
            from day1_core_component_classes.schema_framework_implementation import SchemaValidator
            self.schema_validator = SchemaValidator()
        
        # Track component states
        self._component_states: Dict[str, ComponentLifecycleState] = {}
        
        # Track component dependencies
        self._component_dependencies: Dict[str, Set[str]] = {}
        
        # Track component creation order for proper teardown
        self._creation_order: List[str] = []
        
        # Track active validation sessions
        self._active_validations: Dict[str, str] = {}
        
        self.logger.info("✅ Component Lifecycle Manager initialized with fail-hard validation")
    
    def create_component(self, component_spec: ComponentSpec) -> Any:
        """Create component with full lifecycle validation"""
        
        component_name = component_spec.name
        start_time = time.time()
        
        self.logger.info(f"Creating component: {component_name} ({component_spec.component_type})")
        
        try:
            # Phase 1: Pre-creation validation (before setting state)
            self._validate_creation_preconditions(component_spec)
            
            # Set initial state only after validation passes
            self._component_states[component_name] = ComponentLifecycleState.UNINITIALIZED
            
            # Phase 2: Initialize component
            self._component_states[component_name] = ComponentLifecycleState.INITIALIZING
            component = self._initialize_component(component_spec)
            self._component_states[component_name] = ComponentLifecycleState.INITIALIZED
            
            # Phase 3: Validate component
            self._component_states[component_name] = ComponentLifecycleState.VALIDATING
            self._validate_component_post_creation(component_spec, component)
            self._component_states[component_name] = ComponentLifecycleState.VALIDATED
            
            # Phase 4: Activate component
            self._activate_component(component_name, component)
            self._component_states[component_name] = ComponentLifecycleState.ACTIVE
            
            # Track creation
            self._creation_order.append(component_name)
            
            execution_time = time.time() - start_time
            self.logger.info(f"✅ Component created successfully: {component_name} ({execution_time:.3f}s)")
            
            return component
            
        except Exception as e:
            # Set error state
            self._component_states[component_name] = ComponentLifecycleState.ERROR
            
            # Clean up partial creation
            self._cleanup_failed_creation(component_name)
            
            raise ComponentLifecycleError(
                f"Failed to create component '{component_name}': {e}. "
                f"V5.0 requires complete component creation - no partial components allowed."
            )
    
    def _validate_creation_preconditions(self, component_spec: ComponentSpec) -> None:
        """Validate preconditions for component creation"""
        
        # Validate component specification
        if not component_spec.name:
            raise ComponentLifecycleError("Component name cannot be empty")
        
        if not component_spec.component_type:
            raise ComponentLifecycleError("Component type cannot be empty")
        
        if not component_spec.config:
            raise ComponentLifecycleError("Component config cannot be empty")
        
        # Validate component name uniqueness
        if component_spec.name in self._component_states:
            raise ComponentLifecycleError(
                f"Component '{component_spec.name}' already exists. "
                f"V5.0 requires unique component names."
            )
        
        # Validate component type is registered
        available_types = self.component_registry.list_component_types()
        if component_spec.component_type not in available_types:
            raise ComponentLifecycleError(
                f"Component type '{component_spec.component_type}' not registered. "
                f"Available types: {available_types}"
            )
        
        # Validate dependencies exist
        for dependency in component_spec.dependencies:
            if dependency not in self._component_states:
                raise ComponentLifecycleError(
                    f"Dependency '{dependency}' not found for component '{component_spec.name}'"
                )
            
            # Dependency must be active
            if self._component_states[dependency] != ComponentLifecycleState.ACTIVE:
                raise ComponentLifecycleError(
                    f"Dependency '{dependency}' is not in ACTIVE state (current: {self._component_states[dependency]})"
                )
        
        # Validate schema requirements
        for schema_name in component_spec.schema_requirements.values():
            available_schemas = self.schema_validator.list_schemas()
            if schema_name not in available_schemas:
                raise ComponentLifecycleError(
                    f"Required schema '{schema_name}' not registered. "
                    f"Available schemas: {available_schemas}"
                )
        
        self.logger.debug(f"✅ Pre-creation validation passed for: {component_spec.name}")
    
    def _initialize_component(self, component_spec: ComponentSpec) -> Any:
        """Initialize component using component registry"""
        
        try:
            # Create component through registry (this handles validation)
            component = self.component_registry.create_component(
                component_spec.component_type,
                component_spec.name,
                component_spec.config
            )
            
            # Track dependencies
            self._component_dependencies[component_spec.name] = set(component_spec.dependencies)
            
            return component
            
        except ComponentRegistryError as e:
            raise ComponentLifecycleError(f"Component initialization failed: {e}")
    
    def _validate_component_post_creation(self, component_spec: ComponentSpec, component: Any) -> None:
        """Validate component after creation"""
        
        # Validate component schemas if specified
        if component_spec.schema_requirements:
            self.schema_validator.validate_component_schemas(component_spec.config)
        
        # Validate component dependencies
        self.component_registry.validate_component_dependencies(component_spec.name)
        
        # Validate component state consistency
        if not hasattr(component, 'name') or component.name != component_spec.name:
            raise ComponentLifecycleError(
                f"Component name mismatch: expected '{component_spec.name}', got '{getattr(component, 'name', 'None')}'"
            )
        
        if not hasattr(component, 'config'):
            raise ComponentLifecycleError(f"Component '{component_spec.name}' missing config attribute")
        
        self.logger.debug(f"✅ Post-creation validation passed for: {component_spec.name}")
    
    def _activate_component(self, component_name: str, component: Any) -> None:
        """Activate component (final lifecycle step)"""
        
        # Component is now ready for use
        # In a full implementation, this might start background processes, open connections, etc.
        
        self.logger.debug(f"✅ Component activated: {component_name}")
    
    def validate_component_lifecycle(self, component_name: str) -> LifecycleValidationResult:
        """Validate component through complete lifecycle"""
        
        start_time = time.time()
        
        self.logger.info(f"Validating lifecycle for component: {component_name}")
        
        # Check component exists
        if component_name not in self._component_states:
            raise ComponentLifecycleError(f"Component '{component_name}' not found in lifecycle tracking")
        
        # Get component
        component = self.component_registry.get_component(component_name)
        
        validation_results = []
        states_validated = []
        
        try:
            # Validate initialization state
            init_result = self._validate_initialization_state(component_name, component)
            validation_results.append(init_result)
            states_validated.append(ComponentLifecycleState.INITIALIZED)
            
            if not init_result.success:
                raise ComponentLifecycleError(f"Initialization validation failed: {init_result.errors}")
            
            # Validate active state
            active_result = self._validate_active_state(component_name, component)
            validation_results.append(active_result)
            states_validated.append(ComponentLifecycleState.ACTIVE)
            
            if not active_result.success:
                raise ComponentLifecycleError(f"Active state validation failed: {active_result.errors}")
            
            # Validate dependencies
            deps_result = self._validate_dependencies_state(component_name, component)
            validation_results.append(deps_result)
            
            if not deps_result.success:
                raise ComponentLifecycleError(f"Dependencies validation failed: {deps_result.errors}")
            
            total_time = time.time() - start_time
            
            self.logger.info(f"✅ Lifecycle validation passed for: {component_name} ({total_time:.3f}s)")
            
            return LifecycleValidationResult(
                success=True,
                component_name=component_name,
                states_validated=states_validated,
                validation_results=validation_results,
                total_execution_time=total_time
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            
            # Determine which state failed
            failed_state = None
            if not states_validated:
                failed_state = ComponentLifecycleState.INITIALIZED
            elif ComponentLifecycleState.INITIALIZED in states_validated and ComponentLifecycleState.ACTIVE not in states_validated:
                failed_state = ComponentLifecycleState.ACTIVE
            else:
                failed_state = ComponentLifecycleState.VALIDATED
            
            self.logger.error(f"❌ Lifecycle validation failed for {component_name}: {e}")
            
            return LifecycleValidationResult(
                success=False,
                component_name=component_name,
                states_validated=states_validated,
                failed_state=failed_state,
                validation_results=validation_results,
                total_execution_time=total_time
            )
    
    def _validate_initialization_state(self, component_name: str, component: Any) -> ValidationResult:
        """Validate component initialization state"""
        
        start_time = time.time()
        errors = []
        
        # Check basic attributes
        if not hasattr(component, 'name'):
            errors.append("Component missing 'name' attribute")
        elif component.name != component_name:
            errors.append(f"Component name mismatch: expected '{component_name}', got '{component.name}'")
        
        if not hasattr(component, 'config'):
            errors.append("Component missing 'config' attribute")
        
        # Check required methods exist
        required_methods = ['get_required_config_fields', 'get_required_dependencies']
        for method in required_methods:
            if not hasattr(component, method):
                errors.append(f"Component missing required method: {method}")
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            success=len(errors) == 0,
            component_name=component_name,
            validation_type="initialization",
            errors=errors,
            execution_time=execution_time
        )
    
    def _validate_active_state(self, component_name: str, component: Any) -> ValidationResult:
        """Validate component active state"""
        
        start_time = time.time()
        errors = []
        
        # Check component state
        current_state = self._component_states.get(component_name)
        if current_state != ComponentLifecycleState.ACTIVE:
            errors.append(f"Component not in ACTIVE state: {current_state}")
        
        # Check component is registered
        try:
            registered_component = self.component_registry.get_component(component_name)
            if registered_component != component:
                errors.append("Component not properly registered")
        except ComponentRegistryError as e:
            errors.append(f"Component registration error: {e}")
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            success=len(errors) == 0,
            component_name=component_name,
            validation_type="active_state",
            errors=errors,
            execution_time=execution_time
        )
    
    def _validate_dependencies_state(self, component_name: str, component: Any) -> ValidationResult:
        """Validate component dependencies state"""
        
        start_time = time.time()
        errors = []
        
        # Check all dependencies are still active
        dependencies = self._component_dependencies.get(component_name, set())
        for dependency in dependencies:
            if dependency not in self._component_states:
                errors.append(f"Dependency '{dependency}' no longer tracked")
            elif self._component_states[dependency] != ComponentLifecycleState.ACTIVE:
                errors.append(f"Dependency '{dependency}' not in ACTIVE state: {self._component_states[dependency]}")
        
        # Validate dependencies through registry
        try:
            self.component_registry.validate_component_dependencies(component_name)
        except ComponentRegistryError as e:
            errors.append(f"Registry dependency validation failed: {e}")
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            success=len(errors) == 0,
            component_name=component_name,
            validation_type="dependencies",
            errors=errors,
            execution_time=execution_time
        )
    
    def teardown_component(self, component_name: str) -> bool:
        """Clean component teardown with validation"""
        
        self.logger.info(f"Tearing down component: {component_name}")
        
        try:
            # Check component exists
            if component_name not in self._component_states:
                raise ComponentLifecycleError(f"Component '{component_name}' not found")
            
            # Check no other components depend on this one
            dependents = self._find_dependent_components(component_name)
            if dependents:
                raise ComponentLifecycleError(
                    f"Cannot teardown component '{component_name}' - other components depend on it: {dependents}. "
                    f"V5.0 requires dependency order for teardown."
                )
            
            # Set stopping state
            self._component_states[component_name] = ComponentLifecycleState.STOPPING
            
            # Remove from component registry
            # Note: ComponentRegistry doesn't have a remove method in the current implementation
            # In a full implementation, we would remove it here
            
            # Remove from tracking
            self._component_states[component_name] = ComponentLifecycleState.STOPPED
            del self._component_dependencies[component_name]
            
            if component_name in self._creation_order:
                self._creation_order.remove(component_name)
            
            # Mark as destroyed
            self._component_states[component_name] = ComponentLifecycleState.DESTROYED
            
            self.logger.info(f"✅ Component teardown completed: {component_name}")
            return True
            
        except Exception as e:
            # Set error state
            self._component_states[component_name] = ComponentLifecycleState.ERROR
            
            self.logger.error(f"❌ Component teardown failed for {component_name}: {e}")
            raise ComponentLifecycleError(f"Component teardown failed: {e}")
    
    def _find_dependent_components(self, component_name: str) -> List[str]:
        """Find components that depend on the given component"""
        
        dependents = []
        for comp_name, dependencies in self._component_dependencies.items():
            if component_name in dependencies:
                dependents.append(comp_name)
        
        return dependents
    
    def _cleanup_failed_creation(self, component_name: str) -> None:
        """Clean up after failed component creation"""
        
        try:
            # Remove from tracking
            if component_name in self._component_states:
                del self._component_states[component_name]
            
            if component_name in self._component_dependencies:
                del self._component_dependencies[component_name]
            
            if component_name in self._creation_order:
                self._creation_order.remove(component_name)
            
            self.logger.debug(f"Cleaned up failed creation for: {component_name}")
            
        except Exception as e:
            self.logger.warning(f"Error during cleanup for {component_name}: {e}")
    
    def get_component_state(self, component_name: str) -> ComponentLifecycleState:
        """Get current component state"""
        
        if component_name not in self._component_states:
            raise ComponentLifecycleError(f"Component '{component_name}' not tracked")
        
        return self._component_states[component_name]
    
    def list_components_by_state(self, state: ComponentLifecycleState) -> List[str]:
        """List components in a specific state"""
        
        return [name for name, comp_state in self._component_states.items() if comp_state == state]
    
    def get_lifecycle_summary(self) -> Dict[str, Any]:
        """Get summary of all component lifecycles"""
        
        state_counts = {}
        for state in ComponentLifecycleState:
            state_counts[state.value] = len(self.list_components_by_state(state))
        
        return {
            'total_components': len(self._component_states),
            'state_distribution': state_counts,
            'creation_order': self._creation_order.copy(),
            'active_components': self.list_components_by_state(ComponentLifecycleState.ACTIVE)
        }
    
    def destroy_component(self, component_spec: 'ComponentSpec') -> bool:
        """Destroy a component by spec (alias for teardown_component)"""
        return self.teardown_component(component_spec.name)
    
    def clear_all_components(self) -> None:
        """Clear all component tracking (for testing)"""
        
        self.logger.warning("Clearing all component lifecycle tracking")
        
        try:
            # First teardown all active components
            active_components = list(self._component_states.keys())
            for component_name in active_components:
                try:
                    self.teardown_component(component_name)
                except Exception as e:
                    self.logger.warning(f"Error tearing down {component_name}: {e}")
            
            # Clear all tracking dictionaries
            self._component_states.clear()
            self._component_dependencies.clear()
            self._creation_order.clear()
            
            # Clear the component registry as well
            self.component_registry.clear_registry()
            
            self.logger.info("✅ All component lifecycle tracking cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing component lifecycle tracking: {e}")
            # Don't raise error during cleanup
            pass


# Global component lifecycle manager instance
component_lifecycle = ComponentLifecycle()