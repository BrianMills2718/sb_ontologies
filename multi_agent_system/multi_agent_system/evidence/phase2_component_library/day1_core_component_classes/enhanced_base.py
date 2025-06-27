#!/usr/bin/env python3
"""
Enhanced Base Component Classes for V5.0 Phase 2 Component Library
================================================================

Provides enhanced base component classes supporting V5.0 service types
with proper mapping to Phase 2 base types (Source, Transformer, Sink).

Key Features:
- V5.0 service type support (web_service, database, data_source, etc.)
- Phase 2 base type mapping (Source, Transformer, Sink)
- Enhanced configuration with validation
- Component lifecycle management
- Health monitoring and status tracking
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
import asyncio
import logging
import json
from pathlib import Path


@dataclass
class ComponentConfiguration:
    """Enhanced component configuration with V5.0 features"""
    name: str
    component_type: str
    service_type: str  # V5.0 service type (web_service, database, etc.)
    base_type: str     # Phase 2 base type (Source, Transformer, Sink)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    behavioral_dependencies: List[Dict[str, Any]] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    validation_config: Optional[Dict[str, Any]] = None


class ComponentValidationError(Exception):
    """Raised when component configuration validation fails"""
    pass


class ComponentInitializationError(Exception):
    """Raised when component initialization fails"""
    pass


class ComponentOperationError(Exception):
    """Raised when component operation fails"""
    pass


class EnhancedBaseComponent(ABC):
    """Enhanced base component supporting V5.0 service types and Phase 2 base types"""
    
    def __init__(self, config: ComponentConfiguration):
        self.config = config
        self.name = config.name
        self.component_type = config.component_type
        self.service_type = config.service_type
        self.base_type = config.base_type
        self.logger = logging.getLogger(f"Component.{self.name}")
        
        # V5.0 Enhanced features
        self.inputs = config.inputs
        self.outputs = config.outputs
        self.dependencies = config.dependencies
        self.behavioral_dependencies = config.behavioral_dependencies
        self.environment_variables = config.environment_variables
        self.resource_requirements = config.resource_requirements
        self.validation_config = config.validation_config
        
        # Component state management
        self.is_initialized = False
        self._is_running = False  # Use private attribute to avoid conflicts with property overrides
        self.health_status = "unknown"
        self.last_error = None
        self.initialization_time = None
        self.startup_time = None
        
        self.logger.info(f"✨ Created enhanced component '{self.name}' (service_type: {self.service_type}, base_type: {self.base_type})")
    
    @property
    def is_running(self) -> bool:
        """Check if component is running (can be overridden by subclasses)"""
        return self._is_running
    
    @is_running.setter
    def is_running(self, value: bool):
        """Set running state (can be overridden by subclasses)"""
        self._is_running = value
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize component with dependency validation"""
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Start component operation"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop component operation"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return component health status"""
        pass
    
    @abstractmethod
    async def validate_configuration(self) -> bool:
        """Validate component configuration against schema"""
        pass
    
    def get_component_info(self) -> Dict[str, Any]:
        """Return complete component information"""
        return {
            "name": self.name,
            "component_type": self.component_type,
            "service_type": self.service_type,
            "base_type": self.base_type,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "behavioral_dependencies": self.behavioral_dependencies,
            "resource_requirements": self.resource_requirements,
            "health_status": self.health_status,
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "last_error": str(self.last_error) if self.last_error else None,
            "initialization_time": self.initialization_time,
            "startup_time": self.startup_time
        }
    
    def validate_base_type(self, expected_base_type: str) -> None:
        """Validate that component has the expected base type"""
        if self.base_type != expected_base_type:
            raise ComponentValidationError(
                f"Component '{self.name}' requires base_type='{expected_base_type}', got '{self.base_type}'"
            )
    
    def validate_required_config(self, required_keys: List[str], config_dict: Dict[str, Any], config_name: str) -> None:
        """Validate that required configuration keys are present"""
        missing_keys = [key for key in required_keys if key not in config_dict]
        if missing_keys:
            raise ComponentValidationError(
                f"Component '{self.name}' missing required {config_name}: {missing_keys}"
            )
    
    def get_environment_variable(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """Get environment variable with validation"""
        import os
        
        # First check component-specific environment variables
        value = self.environment_variables.get(key)
        
        # If not found, check system environment
        if value is None:
            value = os.environ.get(key, default)
        
        # Validate if required
        if required and value is None:
            raise ComponentValidationError(
                f"Component '{self.name}' requires environment variable '{key}'"
            )
        
        return value
    
    def get_resource_requirement(self, key: str, default: Any = None, required: bool = False) -> Any:
        """Get resource requirement with validation"""
        value = self.resource_requirements.get(key, default)
        
        if required and value is None:
            raise ComponentValidationError(
                f"Component '{self.name}' requires resource requirement '{key}'"
            )
        
        return value
    
    async def safe_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute operation with error handling and logging"""
        try:
            self.logger.info(f"🔄 Starting {operation_name} for component '{self.name}'")
            result = await operation_func(*args, **kwargs)
            self.logger.info(f"✅ Completed {operation_name} for component '{self.name}'")
            return result
        except Exception as e:
            self.last_error = e
            self.health_status = "error"
            self.logger.error(f"❌ Failed {operation_name} for component '{self.name}': {e}")
            raise ComponentOperationError(f"{operation_name} failed for '{self.name}': {e}") from e
    
    def log_component_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log component metrics for monitoring"""
        metrics_with_context = {
            "component_name": self.name,
            "service_type": self.service_type,
            "base_type": self.base_type,
            "timestamp": asyncio.get_event_loop().time(),
            **metrics
        }
        self.logger.info(f"📊 Component metrics: {json.dumps(metrics_with_context)}")


class EnhancedComponentFactory:
    """Factory for creating enhanced components from configuration"""
    
    @staticmethod
    def validate_component_config(config: Dict[str, Any]) -> ComponentConfiguration:
        """Validate and convert component configuration dictionary"""
        required_fields = ["name", "service_type", "base_type"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ComponentValidationError(f"Missing required configuration fields: {missing_fields}")
        
        return ComponentConfiguration(
            name=config["name"],
            component_type=config.get("type", config["service_type"]),
            service_type=config["service_type"],
            base_type=config["base_type"],
            inputs=config.get("inputs", {}),
            outputs=config.get("outputs", {}),
            dependencies=config.get("dependencies", []),
            behavioral_dependencies=config.get("behavioral_dependencies", []),
            environment_variables=config.get("environment_variables", {}),
            resource_requirements=config.get("resource_requirements", {}),
            validation_config=config.get("validation", {})
        )
    
    @staticmethod
    def create_component(component_class: Type[EnhancedBaseComponent], config: Dict[str, Any]) -> EnhancedBaseComponent:
        """Create enhanced component instance from configuration"""
        validated_config = EnhancedComponentFactory.validate_component_config(config)
        return component_class(validated_config)


# Configuration validation utilities
class ConfigurationValidator:
    """Utilities for validating component configurations"""
    
    @staticmethod
    def validate_schema_format(schema: Dict[str, Any]) -> bool:
        """Validate that schema follows expected format"""
        if not isinstance(schema, dict):
            return False
        
        # Basic schema should have 'type' and optional 'properties'
        if "type" not in schema:
            return False
        
        return True
    
    @staticmethod
    def validate_port_range(port: int) -> bool:
        """Validate port is in acceptable range"""
        return 1024 <= port <= 65535
    
    @staticmethod
    def validate_url_format(url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


# Export main classes and functions
__all__ = [
    'ComponentConfiguration',
    'ComponentValidationError', 
    'ComponentInitializationError',
    'ComponentOperationError',
    'EnhancedBaseComponent',
    'EnhancedComponentFactory',
    'ConfigurationValidator'
]