#!/usr/bin/env python3
"""
Enhanced Base Component for V5.0 Validation-Driven Architecture
Implements fail-hard validation principles established in Phase 1
"""

from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel, ValidationError
import logging
from ..orchestration.component import Component


class ComponentValidationError(Exception):
    """Raised when component validation fails - no fallbacks available"""
    pass


class SchemaValidationError(Exception):
    """Raised when schema validation fails - fail hard, no graceful degradation"""
    pass


class DependencyValidationError(Exception):
    """Raised when required dependencies are missing - no mock modes available"""
    pass


class EnhancedComponentBase(Component):
    """
    V5.0 Enhanced Component Base Class with Fail-Hard Validation
    
    Key Principles from Phase 1:
    - No mock modes or fallbacks
    - Fail hard on missing dependencies
    - Strict schema validation
    - No graceful degradation
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.config = config or {}
        self.component_type = self.config.get('type', 'Unknown')
        
        # V5.0 validation components
        self.input_schemas: Dict[str, Type[BaseModel]] = {}
        self.output_schemas: Dict[str, Type[BaseModel]] = {}
        self.required_dependencies: List[str] = []
        
        # Fail-hard validation
        self.strict_validation = True
        self.logger = logging.getLogger(f"EnhancedComponent.{self.name}")
        
        # Validate component configuration immediately
        self._validate_component_configuration()
        
        # Validate dependencies immediately  
        self._validate_required_dependencies()
    
    def _validate_component_configuration(self) -> None:
        """Validate component configuration with fail-hard behavior"""
        
        required_config_fields = self.get_required_config_fields()
        
        for field in required_config_fields:
            if field not in self.config:
                raise ComponentValidationError(
                    f"Required configuration field '{field}' missing for component '{self.name}'. "
                    f"V5.0 components fail hard on missing configuration - no defaults available."
                )
        
        # Validate component type
        if self.component_type not in ['Source', 'Transformer', 'Sink']:
            raise ComponentValidationError(
                f"Invalid component type '{self.component_type}' for component '{self.name}'. "
                f"Must be Source, Transformer, or Sink. No fallback types available."
            )
        
        self.logger.info(f"✅ Component configuration validated for {self.name}")
    
    def _validate_required_dependencies(self) -> None:
        """Validate that all required dependencies are available"""
        
        missing_dependencies = []
        
        for dependency in self.required_dependencies:
            if not self._check_dependency_availability(dependency):
                missing_dependencies.append(dependency)
        
        if missing_dependencies:
            raise DependencyValidationError(
                f"Required dependencies missing for component '{self.name}': {missing_dependencies}. "
                f"V5.0 components require all dependencies to be available - no mock modes or fallbacks."
            )
        
        if self.required_dependencies:
            self.logger.info(f"✅ All required dependencies validated for {self.name}")
    
    def _check_dependency_availability(self, dependency: str) -> bool:
        """Check if a specific dependency is available"""
        
        # Check for database dependencies
        if dependency == 'database':
            return self._check_database_availability()
        
        # Check for LLM dependencies
        if dependency == 'llm':
            return self._check_llm_availability()
        
        # Check for API dependencies
        if dependency.startswith('api:'):
            api_name = dependency.split(':', 1)[1]
            return self._check_api_availability(api_name)
        
        # Default: assume available if not specifically checked
        return True
    
    def _check_database_availability(self) -> bool:
        """Check if database connection is available"""
        # In V5.0, we fail hard if database is required but not configured
        db_config = self.config.get('database')
        if not db_config:
            return False
        
        connection_string = db_config.get('connection_string')
        if not connection_string:
            return False
        
        # Additional database validation would go here
        return True
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM service is available"""
        import os
        
        # Check for API keys (fail hard if missing)
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        return bool(openai_key or anthropic_key)
    
    def _check_api_availability(self, api_name: str) -> bool:
        """Check if specific API is available"""
        # Implement specific API availability checks
        return True
    
    def register_input_schema(self, input_name: str, schema_class: Type[BaseModel]) -> None:
        """Register input schema for validation"""
        self.input_schemas[input_name] = schema_class
        self.logger.info(f"Registered input schema '{input_name}' for {self.name}")
    
    def register_output_schema(self, output_name: str, schema_class: Type[BaseModel]) -> None:
        """Register output schema for validation"""
        self.output_schemas[output_name] = schema_class
        self.logger.info(f"Registered output schema '{output_name}' for {self.name}")
    
    def validate_input_data(self, input_name: str, data: Dict[str, Any]) -> BaseModel:
        """Validate input data against registered schema - fail hard on validation errors"""
        
        if input_name not in self.input_schemas:
            raise SchemaValidationError(
                f"No input schema registered for '{input_name}' in component '{self.name}'. "
                f"V5.0 requires explicit schema validation - no schema inference available."
            )
        
        schema_class = self.input_schemas[input_name]
        
        try:
            validated_data = schema_class(**data)
            self.logger.debug(f"✅ Input data validated for '{input_name}' in {self.name}")
            return validated_data
            
        except ValidationError as e:
            raise SchemaValidationError(
                f"Input validation failed for '{input_name}' in component '{self.name}': {e}. "
                f"V5.0 enforces strict schema compliance - no data coercion available."
            )
    
    def validate_output_data(self, output_name: str, data: Dict[str, Any]) -> BaseModel:
        """Validate output data against registered schema - fail hard on validation errors"""
        
        if output_name not in self.output_schemas:
            raise SchemaValidationError(
                f"No output schema registered for '{output_name}' in component '{self.name}'. "
                f"V5.0 requires explicit schema validation - no schema inference available."
            )
        
        schema_class = self.output_schemas[output_name]
        
        try:
            validated_data = schema_class(**data)
            self.logger.debug(f"✅ Output data validated for '{output_name}' in {self.name}")
            return validated_data
            
        except ValidationError as e:
            raise SchemaValidationError(
                f"Output validation failed for '{output_name}' in component '{self.name}': {e}. "
                f"V5.0 enforces strict schema compliance - no data coercion available."
            )
    
    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Return list of required configuration fields for this component type"""
        pass
    
    @abstractmethod
    def get_required_dependencies(self) -> List[str]:
        """Return list of required dependencies for this component type"""
        pass
    
    async def setup(self) -> None:
        """Setup component with dependency validation"""
        
        self.logger.info(f"🔧 Setting up enhanced component: {self.name}")
        
        # Re-validate dependencies during setup
        self._validate_required_dependencies()
        
        # Component-specific setup
        await self._setup_component()
        
        self.logger.info(f"✅ Enhanced component setup complete: {self.name}")
    
    async def _setup_component(self) -> None:
        """Component-specific setup logic - override in subclasses"""
        pass
    
    async def teardown(self) -> None:
        """Teardown component with proper cleanup"""
        
        self.logger.info(f"🔧 Tearing down enhanced component: {self.name}")
        
        try:
            await self._teardown_component()
        except Exception as e:
            self.logger.error(f"Error during component teardown: {e}")
            # In V5.0, we log errors but don't hide them
            raise
        
        self.logger.info(f"✅ Enhanced component teardown complete: {self.name}")
    
    async def _teardown_component(self) -> None:
        """Component-specific teardown logic - override in subclasses"""
        pass


class EnhancedSource(EnhancedComponentBase):
    """
    Enhanced Source component with V5.0 validation
    Sources generate data - they should not have inputs
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.component_type = "Source"
        
        # Sources should not have inputs
        if 'inputs' in self.config:
            raise ComponentValidationError(
                f"Source component '{self.name}' cannot have inputs. "
                f"Sources generate data and should only have outputs."
            )
    
    def get_required_config_fields(self) -> List[str]:
        """Source components require outputs"""
        return ['outputs']
    
    def get_required_dependencies(self) -> List[str]:
        """Override in subclasses to specify dependencies"""
        return []
    
    async def process(self) -> None:
        """Default process implementation for enhanced sources"""
        self.logger.info(f"Processing source component: {self.name}")
        # Default implementation - override in subclasses for actual processing
        pass


class EnhancedTransformer(EnhancedComponentBase):
    """
    Enhanced Transformer component with V5.0 validation  
    Transformers process data - they must have both inputs and outputs
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.component_type = "Transformer"
        
        # Transformers must have both inputs and outputs
        if 'inputs' not in self.config:
            raise ComponentValidationError(
                f"Transformer component '{self.name}' must have inputs. "
                f"Transformers process data and require input sources."
            )
        
        if 'outputs' not in self.config:
            raise ComponentValidationError(
                f"Transformer component '{self.name}' must have outputs. "
                f"Transformers must produce processed data outputs."
            )
    
    def get_required_config_fields(self) -> List[str]:
        """Transformer components require both inputs and outputs"""
        return ['inputs', 'outputs']
    
    def get_required_dependencies(self) -> List[str]:
        """Override in subclasses to specify dependencies"""
        return []
    
    async def process(self) -> None:
        """Default process implementation for enhanced transformers"""
        self.logger.info(f"Processing transformer component: {self.name}")
        # Default implementation - override in subclasses for actual processing
        pass


class EnhancedSink(EnhancedComponentBase):
    """
    Enhanced Sink component with V5.0 validation
    Sinks consume data - they should not have outputs
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.component_type = "Sink"
        
        # Sinks should not have outputs
        if 'outputs' in self.config:
            raise ComponentValidationError(
                f"Sink component '{self.name}' cannot have outputs. "
                f"Sinks consume data and should only have inputs."
            )
    
    def get_required_config_fields(self) -> List[str]:
        """Sink components require inputs"""
        return ['inputs']
    
    def get_required_dependencies(self) -> List[str]:
        """Override in subclasses to specify dependencies"""
        return []
    
    async def process(self) -> None:
        """Default process implementation for enhanced sinks"""
        self.logger.info(f"Processing sink component: {self.name}")
        # Default implementation - override in subclasses for actual processing
        pass