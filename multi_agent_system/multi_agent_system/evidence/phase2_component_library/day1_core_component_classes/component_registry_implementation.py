#!/usr/bin/env python3
"""
Component Registry for V5.0 Validation-Driven Architecture
Implements centralized component discovery and validation with fail-hard principles
"""

from typing import Dict, Type, List, Any, Optional
import logging
from .enhanced_base import (
    EnhancedComponentBase, 
    EnhancedSource, 
    EnhancedTransformer, 
    EnhancedSink,
    ComponentValidationError,
    DependencyValidationError
)


class ComponentRegistryError(Exception):
    """Raised when component registry operations fail - no fallbacks available"""
    pass


class ComponentRegistry:
    """
    V5.0 Component Registry with Fail-Hard Validation
    
    Manages component types and validates registrations with strict validation.
    No fallback or graceful degradation - components must meet all requirements.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ComponentRegistry")
        
        # Registry of component classes
        self._component_classes: Dict[str, Type[EnhancedComponentBase]] = {}
        
        # Registry of component instances
        self._component_instances: Dict[str, EnhancedComponentBase] = {}
        
        # Component validation rules
        self._validation_rules: Dict[str, Dict[str, Any]] = {}
        
        # Register built-in component types
        self._register_builtin_components()
        
        self.logger.info("✅ Component Registry initialized with fail-hard validation")
    
    def _register_builtin_components(self) -> None:
        """Register built-in V5.0 component types"""
        
        self.register_component_class("Source", EnhancedSource)
        self.register_component_class("Transformer", EnhancedTransformer)
        self.register_component_class("Sink", EnhancedSink)
        
        self.logger.info("✅ Built-in component types registered")
    
    def register_component_class(
        self, 
        component_type: str, 
        component_class: Type[EnhancedComponentBase]
    ) -> None:
        """Register a component class with validation"""
        
        # Validate component class
        if not issubclass(component_class, EnhancedComponentBase):
            raise ComponentRegistryError(
                f"Component class '{component_class.__name__}' must inherit from EnhancedComponentBase. "
                f"V5.0 requires all components to use enhanced validation - no legacy components allowed."
            )
        
        # Check for abstract methods implementation
        try:
            # Try to get required methods
            component_class.get_required_config_fields
            component_class.get_required_dependencies
        except AttributeError:
            raise ComponentRegistryError(
                f"Component class '{component_class.__name__}' must implement required abstract methods. "
                f"V5.0 requires complete component implementation - no partial implementations allowed."
            )
        
        # Register the component class
        self._component_classes[component_type] = component_class
        
        # Initialize validation rules for this component type
        self._validation_rules[component_type] = {
            'required_config_fields': [],
            'required_dependencies': [],
            'schema_requirements': {}
        }
        
        self.logger.info(f"✅ Registered component class: {component_type}")
    
    def create_component(
        self, 
        component_type: str, 
        name: str, 
        config: Dict[str, Any]
    ) -> EnhancedComponentBase:
        """Create and validate a component instance"""
        
        # Validate component type is registered
        if component_type not in self._component_classes:
            available_types = list(self._component_classes.keys())
            raise ComponentRegistryError(
                f"Unknown component type '{component_type}'. "
                f"Available types: {available_types}. "
                f"V5.0 requires explicit component registration - no dynamic type inference."
            )
        
        # Validate component name uniqueness
        if name in self._component_instances:
            raise ComponentRegistryError(
                f"Component name '{name}' already exists. "
                f"V5.0 requires unique component names - no name conflicts allowed."
            )
        
        # Get component class
        component_class = self._component_classes[component_type]
        
        # Pre-validate configuration requirements
        self._validate_component_config(component_type, config)
        
        try:
            # Create component instance (this will trigger validation)
            component_instance = component_class(name, config)
            
            # Register the instance
            self._component_instances[name] = component_instance
            
            self.logger.info(f"✅ Created and registered component: {name} ({component_type})")
            return component_instance
            
        except Exception as e:
            raise ComponentRegistryError(
                f"Failed to create component '{name}' of type '{component_type}': {e}. "
                f"V5.0 components must initialize successfully - no partial initialization allowed."
            )
    
    def _validate_component_config(self, component_type: str, config: Dict[str, Any]) -> None:
        """Validate component configuration against type requirements"""
        
        # Get component class for validation
        component_class = self._component_classes[component_type]
        
        # Create temporary instance to get requirements (without full initialization)
        try:
            temp_instance = object.__new__(component_class)
            temp_instance.config = config
            temp_instance.name = "temp_validation"
            
            # Get required fields
            required_fields = temp_instance.get_required_config_fields()
            required_dependencies = temp_instance.get_required_dependencies()
            
        except Exception as e:
            raise ComponentRegistryError(
                f"Failed to validate component type '{component_type}' requirements: {e}"
            )
        
        # Validate required configuration fields
        missing_fields = []
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            raise ComponentRegistryError(
                f"Missing required configuration fields for {component_type}: {missing_fields}. "
                f"V5.0 requires all configuration fields - no defaults or fallbacks available."
            )
        
        # Validate component logic based on type
        self._validate_component_logic(component_type, config)
        
        self.logger.debug(f"✅ Configuration validated for {component_type}")
    
    def _validate_component_logic(self, component_type: str, config: Dict[str, Any]) -> None:
        """Validate component logic based on type-specific rules"""
        
        if component_type == "Source":
            # Sources should not have inputs
            if 'inputs' in config:
                raise ComponentRegistryError(
                    f"Source components cannot have inputs. "
                    f"Sources generate data and should only define outputs."
                )
            
            # Sources must have outputs
            if 'outputs' not in config or not config['outputs']:
                raise ComponentRegistryError(
                    f"Source components must define outputs. "
                    f"Sources must specify what data they generate."
                )
        
        elif component_type == "Transformer":
            # Transformers must have both inputs and outputs
            if 'inputs' not in config or not config['inputs']:
                raise ComponentRegistryError(
                    f"Transformer components must define inputs. "
                    f"Transformers require input data to process."
                )
            
            if 'outputs' not in config or not config['outputs']:
                raise ComponentRegistryError(
                    f"Transformer components must define outputs. "
                    f"Transformers must specify processed data outputs."
                )
        
        elif component_type == "Sink":
            # Sinks should not have outputs
            if 'outputs' in config:
                raise ComponentRegistryError(
                    f"Sink components cannot have outputs. "
                    f"Sinks consume data and should only define inputs."
                )
            
            # Sinks must have inputs
            if 'inputs' not in config or not config['inputs']:
                raise ComponentRegistryError(
                    f"Sink components must define inputs. "
                    f"Sinks must specify what data they consume."
                )
    
    def get_component(self, name: str) -> EnhancedComponentBase:
        """Get registered component instance"""
        
        if name not in self._component_instances:
            available_components = list(self._component_instances.keys())
            raise ComponentRegistryError(
                f"Component '{name}' not found. "
                f"Available components: {available_components}. "
                f"V5.0 requires explicit component registration."
            )
        
        return self._component_instances[name]
    
    def list_component_types(self) -> List[str]:
        """List all registered component types"""
        return list(self._component_classes.keys())
    
    def list_component_instances(self) -> List[str]:
        """List all registered component instances"""
        return list(self._component_instances.keys())
    
    def validate_component_dependencies(self, name: str) -> bool:
        """Validate that component dependencies are satisfied"""
        
        component = self.get_component(name)
        
        try:
            # Re-validate dependencies
            component._validate_required_dependencies()
            self.logger.info(f"✅ Dependencies validated for component: {name}")
            return True
            
        except DependencyValidationError as e:
            self.logger.error(f"❌ Dependency validation failed for {name}: {e}")
            raise ComponentRegistryError(
                f"Component '{name}' dependency validation failed: {e}"
            )
    
    def validate_all_components(self) -> Dict[str, bool]:
        """Validate all registered components"""
        
        validation_results = {}
        
        for name in self._component_instances:
            try:
                validation_results[name] = self.validate_component_dependencies(name)
            except ComponentRegistryError:
                validation_results[name] = False
        
        passed_count = sum(validation_results.values())
        total_count = len(validation_results)
        
        self.logger.info(f"Component validation complete: {passed_count}/{total_count} passed")
        
        # In V5.0, if any component fails validation, we fail hard
        if passed_count < total_count:
            failed_components = [name for name, passed in validation_results.items() if not passed]
            raise ComponentRegistryError(
                f"Component validation failed for: {failed_components}. "
                f"V5.0 requires all components to pass validation - no partial system allowed."
            )
        
        return validation_results
    
    def clear_registry(self) -> None:
        """Clear all registered components (for testing)"""
        
        self.logger.warning("Clearing component registry")
        
        self._component_instances.clear()
        # Keep component classes registered
        
        self.logger.info("✅ Component registry cleared")


# Global component registry instance
component_registry = ComponentRegistry()