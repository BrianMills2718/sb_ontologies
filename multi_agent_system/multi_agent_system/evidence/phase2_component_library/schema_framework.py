#!/usr/bin/env python3
"""
Schema Validation Framework for V5.0 Validation-Driven Architecture
Implements Pydantic-based schema enforcement with fail-hard principles
"""

from typing import Dict, Any, Type, List, Optional, Union
from pydantic import BaseModel, ValidationError, Field
from abc import ABC, abstractmethod
import logging


class SchemaValidationError(Exception):
    """Raised when schema validation fails - no fallbacks or coercion available"""
    pass


class SchemaCompatibilityError(Exception):
    """Raised when schema compatibility checks fail - no graceful degradation"""
    pass


class SchemaRegistrationError(Exception):
    """Raised when schema registration fails - no automatic schema generation"""
    pass


# Base schema classes for V5.0 components
class ComponentDataSchema(BaseModel):
    """Base schema for all component data with V5.0 requirements"""
    
    # All component data must have these fields
    timestamp: float = Field(..., description="Data timestamp (required)")
    component_source: str = Field(..., description="Source component name (required)")
    
    model_config = {
        # Strict validation - no extra fields allowed
        "extra": "forbid",
        # Validate assignment to catch runtime changes
        "validate_assignment": True
    }


class SourceDataSchema(ComponentDataSchema):
    """Base schema for Source component outputs"""
    
    data_id: str = Field(..., description="Unique data identifier")
    data_type: str = Field(..., description="Type of generated data")


class TransformerDataSchema(ComponentDataSchema):
    """Base schema for Transformer component inputs/outputs"""
    
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    transformation_type: str = Field(..., description="Type of transformation applied")


class SinkDataSchema(ComponentDataSchema):
    """Base schema for Sink component inputs"""
    
    storage_metadata: Dict[str, Any] = Field(default_factory=dict, description="Storage metadata")
    final_destination: str = Field(..., description="Final data destination")


class SchemaValidator:
    """
    V5.0 Schema Validator with Fail-Hard Principles
    
    Validates data against Pydantic schemas with strict enforcement.
    No schema coercion, fallbacks, or graceful degradation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SchemaValidator")
        
        # Registry of schemas by name
        self._schema_registry: Dict[str, Type[BaseModel]] = {}
        
        # Schema compatibility rules
        self._compatibility_rules: Dict[str, List[str]] = {}
        
        # Register built-in schemas
        self._register_builtin_schemas()
        
        self.logger.info("✅ Schema Validator initialized with fail-hard validation")
    
    def _register_builtin_schemas(self) -> None:
        """Register built-in V5.0 schemas"""
        
        self.register_schema("ComponentData", ComponentDataSchema)
        self.register_schema("SourceData", SourceDataSchema)
        self.register_schema("TransformerData", TransformerDataSchema)
        self.register_schema("SinkData", SinkDataSchema)
        
        self.logger.info("✅ Built-in schemas registered")
    
    def register_schema(self, schema_name: str, schema_class: Type[BaseModel]) -> None:
        """Register a schema with validation"""
        
        # Validate schema class
        if not issubclass(schema_class, BaseModel):
            raise SchemaRegistrationError(
                f"Schema '{schema_name}' must be a Pydantic BaseModel. "
                f"V5.0 requires Pydantic schemas - no custom validation frameworks allowed."
            )
        
        # Validate schema has required V5.0 fields for component data
        if issubclass(schema_class, ComponentDataSchema):
            # Component schemas must inherit from ComponentDataSchema
            required_fields = ['timestamp', 'component_source']
            schema_fields = schema_class.model_fields.keys()
            
            missing_fields = [field for field in required_fields if field not in schema_fields]
            if missing_fields:
                raise SchemaRegistrationError(
                    f"Component schema '{schema_name}' missing required V5.0 fields: {missing_fields}. "
                    f"All component schemas must include timestamp and component_source."
                )
        
        # Register the schema
        self._schema_registry[schema_name] = schema_class
        
        # Initialize compatibility rules
        self._compatibility_rules[schema_name] = []
        
        self.logger.info(f"✅ Registered schema: {schema_name}")
    
    def validate_data(self, schema_name: str, data: Dict[str, Any]) -> BaseModel:
        """Validate data against registered schema - fail hard on errors"""
        
        # Check schema is registered
        if schema_name not in self._schema_registry:
            available_schemas = list(self._schema_registry.keys())
            raise SchemaValidationError(
                f"Schema '{schema_name}' not registered. "
                f"Available schemas: {available_schemas}. "
                f"V5.0 requires explicit schema registration - no schema inference."
            )
        
        schema_class = self._schema_registry[schema_name]
        
        try:
            # Validate data against schema
            validated_data = schema_class(**data)
            
            self.logger.debug(f"✅ Data validated against schema: {schema_name}")
            return validated_data
            
        except ValidationError as e:
            # Extract detailed error information
            error_details = []
            for error in e.errors():
                field = ".".join([str(loc) for loc in error['loc']])
                message = error['msg']
                error_details.append(f"{field}: {message}")
            
            raise SchemaValidationError(
                f"Schema validation failed for '{schema_name}': {error_details}. "
                f"V5.0 enforces strict schema compliance - no data coercion or fallbacks available."
            )
    
    def validate_schema_compatibility(self, output_schema: str, input_schema: str) -> bool:
        """Validate that output schema is compatible with input schema"""
        
        # Check both schemas are registered
        for schema_name in [output_schema, input_schema]:
            if schema_name not in self._schema_registry:
                raise SchemaCompatibilityError(
                    f"Schema '{schema_name}' not registered. "
                    f"V5.0 requires all schemas to be explicitly registered."
                )
        
        # Check explicit compatibility rules first
        if input_schema in self._compatibility_rules.get(output_schema, []):
            self.logger.debug(f"✅ Schema compatibility confirmed: {output_schema} → {input_schema}")
            return True
        
        # Check if schemas are identical
        if output_schema == input_schema:
            self.logger.debug(f"✅ Schema compatibility confirmed (identical): {output_schema}")
            return True
        
        # Check if schemas are compatible by inheritance
        output_class = self._schema_registry[output_schema]
        input_class = self._schema_registry[input_schema]
        
        if issubclass(output_class, input_class):
            self.logger.debug(f"✅ Schema compatibility confirmed (inheritance): {output_schema} → {input_schema}")
            return True
        
        # In V5.0, we fail hard on incompatible schemas
        raise SchemaCompatibilityError(
            f"Schema '{output_schema}' is not compatible with '{input_schema}'. "
            f"V5.0 requires explicit schema compatibility - no automatic conversion available."
        )
    
    def register_schema_compatibility(self, output_schema: str, input_schema: str) -> None:
        """Register explicit schema compatibility rule"""
        
        # Validate both schemas exist
        for schema_name in [output_schema, input_schema]:
            if schema_name not in self._schema_registry:
                raise SchemaCompatibilityError(
                    f"Cannot register compatibility rule: schema '{schema_name}' not registered."
                )
        
        # Add compatibility rule
        if output_schema not in self._compatibility_rules:
            self._compatibility_rules[output_schema] = []
        
        if input_schema not in self._compatibility_rules[output_schema]:
            self._compatibility_rules[output_schema].append(input_schema)
        
        self.logger.info(f"✅ Registered schema compatibility: {output_schema} → {input_schema}")
    
    def get_schema_info(self, schema_name: str) -> Dict[str, Any]:
        """Get information about a registered schema"""
        
        if schema_name not in self._schema_registry:
            raise SchemaValidationError(f"Schema '{schema_name}' not registered.")
        
        schema_class = self._schema_registry[schema_name]
        
        # Extract field information
        fields_info = {}
        for field_name, field_info in schema_class.model_fields.items():
            fields_info[field_name] = {
                'type': str(field_info.annotation) if hasattr(field_info, 'annotation') else 'unknown',
                'required': field_info.is_required() if hasattr(field_info, 'is_required') else True,
                'default': field_info.default if hasattr(field_info, 'default') else None,
                'description': field_info.description if hasattr(field_info, 'description') else None
            }
        
        return {
            'schema_name': schema_name,
            'schema_class': schema_class.__name__,
            'fields': fields_info,
            'compatible_inputs': self._compatibility_rules.get(schema_name, []),
            'strict_validation': True
        }
    
    def list_schemas(self) -> List[str]:
        """List all registered schemas"""
        return list(self._schema_registry.keys())
    
    def validate_component_schemas(self, component_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all schemas referenced in component configuration"""
        
        validation_results = {}
        
        # Validate input schemas
        for input_def in component_config.get('inputs', []):
            schema_name = input_def.get('schema')
            if schema_name:
                try:
                    # Check schema is registered
                    if schema_name not in self._schema_registry:
                        raise SchemaValidationError(f"Input schema '{schema_name}' not registered")
                    
                    validation_results[f"input_{input_def['name']}"] = {
                        'schema': schema_name,
                        'valid': True
                    }
                except Exception as e:
                    validation_results[f"input_{input_def['name']}"] = {
                        'schema': schema_name,
                        'valid': False,
                        'error': str(e)
                    }
        
        # Validate output schemas
        for output_def in component_config.get('outputs', []):
            schema_name = output_def.get('schema')
            if schema_name:
                try:
                    # Check schema is registered
                    if schema_name not in self._schema_registry:
                        raise SchemaValidationError(f"Output schema '{schema_name}' not registered")
                    
                    validation_results[f"output_{output_def['name']}"] = {
                        'schema': schema_name,
                        'valid': True
                    }
                except Exception as e:
                    validation_results[f"output_{output_def['name']}"] = {
                        'schema': schema_name,
                        'valid': False,
                        'error': str(e)
                    }
        
        # Check if any validations failed
        failed_validations = [name for name, result in validation_results.items() if not result['valid']]
        
        if failed_validations:
            raise SchemaValidationError(
                f"Schema validation failed for component schemas: {failed_validations}. "
                f"V5.0 requires all component schemas to be valid - no partial validation allowed."
            )
        
        self.logger.info(f"✅ All component schemas validated: {len(validation_results)} schemas")
        return validation_results


class SchemaFramework:
    """
    Schema-Aware Validation Framework for V5.0 Components
    
    Integrates with component validation to provide schema-aware component validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SchemaFramework") 
        self.schema_validator = SchemaValidator()
        
        self.logger.info("✅ Schema Framework initialized")
    
    def validate_component_schema(self, component) -> Dict[str, Any]:
        """Validate component against its schema definition"""
        
        try:
            # Get component configuration
            component_config = component.config if hasattr(component, 'config') else {}
            
            # Validate component schemas
            schema_results = self.schema_validator.validate_component_schemas(component_config)
            
            return {
                'valid': True,
                'component_name': getattr(component, 'name', 'unknown'),
                'schema_results': schema_results,
                'validated_schemas': len(schema_results)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'component_name': getattr(component, 'name', 'unknown'),
                'error': str(e),
                'schema_results': {}
            }
    
    def validate_component_interfaces(self, component) -> Dict[str, Any]:
        """Validate component interface contracts"""
        
        try:
            component_config = component.config if hasattr(component, 'config') else {}
            
            interface_results = {
                'inputs_valid': True,
                'outputs_valid': True,
                'interface_errors': []
            }
            
            # Validate input interfaces
            for input_def in component_config.get('inputs', []):
                if 'schema' in input_def:
                    schema_name = input_def['schema']
                    if schema_name not in self.schema_validator._schema_registry:
                        interface_results['inputs_valid'] = False
                        interface_results['interface_errors'].append(
                            f"Input '{input_def['name']}' references unknown schema '{schema_name}'"
                        )
            
            # Validate output interfaces  
            for output_def in component_config.get('outputs', []):
                if 'schema' in output_def:
                    schema_name = output_def['schema']
                    if schema_name not in self.schema_validator._schema_registry:
                        interface_results['outputs_valid'] = False
                        interface_results['interface_errors'].append(
                            f"Output '{output_def['name']}' references unknown schema '{schema_name}'"
                        )
            
            return {
                'valid': interface_results['inputs_valid'] and interface_results['outputs_valid'],
                'component_name': getattr(component, 'name', 'unknown'),
                'interface_validation': interface_results
            }
            
        except Exception as e:
            return {
                'valid': False,
                'component_name': getattr(component, 'name', 'unknown'),
                'error': str(e)
            }
    
    def validate_component_dependencies(self, component) -> Dict[str, Any]:
        """Validate component dependency requirements"""
        
        try:
            # Get component dependencies
            dependencies = []
            if hasattr(component, 'get_required_dependencies'):
                dependencies = component.get_required_dependencies()
            
            dependency_results = {
                'dependencies_validated': len(dependencies),
                'dependency_errors': []
            }
            
            # For now, just ensure dependencies are defined
            # In full implementation, this would validate actual dependency availability
            for dep in dependencies:
                if not dep or not isinstance(dep, str):
                    dependency_results['dependency_errors'].append(
                        f"Invalid dependency specification: {dep}"
                    )
            
            return {
                'valid': len(dependency_results['dependency_errors']) == 0,
                'component_name': getattr(component, 'name', 'unknown'),
                'dependency_validation': dependency_results
            }
            
        except Exception as e:
            return {
                'valid': False,
                'component_name': getattr(component, 'name', 'unknown'),
                'error': str(e)
            }


# Global schema validator instance
schema_validator = SchemaValidator()

# Global schema framework instance  
schema_framework = SchemaFramework()