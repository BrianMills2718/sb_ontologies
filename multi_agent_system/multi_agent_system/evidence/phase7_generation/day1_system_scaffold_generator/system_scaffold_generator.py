#!/usr/bin/env python3
"""
SystemScaffoldGenerator: Generates main.py files with SystemExecutionHarness setup
================================================================================

Transforms SystemBlueprint component definitions into harness-based orchestration code.
This is Phase 1 of the two-phase generation pipeline.

Key Features:
- Generates main.py with SystemExecutionHarness initialization
- Converts blueprint components to harness component registration
- Derives stream connections from blueprint bindings
- Creates deployment-ready harness systems
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import SystemBlueprint
from harness_template_engine import HarnessTemplateEngine
from connection_mapper import ConnectionMapper


@dataclass
class ComponentInfo:
    """Information about a component for scaffold generation"""
    name: str
    class_name: str
    component_type: str
    config: Dict[str, Any]
    dependencies: List[str]
    import_path: str


@dataclass
class GeneratedScaffold:
    """Results of scaffold generation"""
    main_py_code: str
    config_code: str
    components: List[ComponentInfo]
    connections: List[Dict[str, Any]]
    imports: List[str]
    generation_time: float


class SystemScaffoldGenerator:
    """
    Generates main.py files with SystemExecutionHarness setup from SystemBlueprint.
    
    Transforms blueprint component definitions into harness-based orchestration code.
    """
    
    def __init__(self, template_engine: Optional[HarnessTemplateEngine] = None):
        self.template_engine = template_engine or HarnessTemplateEngine()
        self.connection_mapper = ConnectionMapper()
        self.logger = logging.getLogger("SystemScaffoldGenerator")
        
        # Component type mapping
        self.component_type_mapping = {
            "api_gateway": "APIGateway",
            "task_controller": "TaskController", 
            "task_store": "TaskStore",
            "data_processor": "DataProcessor",
            "web_service": "WebService",
            "database": "DatabaseService",
            "cache": "CacheService",
            "queue": "QueueService"
        }
        
        self.logger.info("✨ SystemScaffoldGenerator initialized")
    
    def generate_main_py(self, blueprint: SystemBlueprint) -> str:
        """
        Generate main.py with SystemExecutionHarness setup.
        
        Transforms blueprint component definitions into harness-based orchestration code.
        
        Args:
            blueprint: SystemBlueprint containing component definitions
            
        Returns:
            Generated main.py code string
        """
        self.logger.info(f"🚀 Generating main.py for blueprint: {blueprint.description}")
        
        try:
            # Extract components from blueprint
            components = self._extract_components(blueprint)
            
            # Generate component imports
            imports = self._generate_component_imports(components)
            
            # Generate component registration code
            registration_code = self._generate_component_registration(components)
            
            # Generate stream connections from blueprint bindings
            connections = self.connection_mapper.derive_connections(blueprint)
            connection_code = self._generate_connection_code(connections)
            
            # Generate complete main.py
            main_py_code = self.template_engine.render_main_template(
                imports=imports,
                registration_code=registration_code,
                connection_code=connection_code,
                config=getattr(blueprint, 'config', {})
            )
            
            self.logger.info(f"✅ Generated main.py with {len(components)} components and {len(connections)} connections")
            return main_py_code
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate main.py: {e}")
            raise
    
    def generate_config_file(self, blueprint: SystemBlueprint) -> str:
        """
        Generate configuration file for the harness system.
        
        Args:
            blueprint: SystemBlueprint containing configuration
            
        Returns:
            Generated configuration code
        """
        self.logger.info("📋 Generating system configuration")
        
        try:
            config_template = '''#!/usr/bin/env python3
"""
Generated System Configuration
Generated from: {description}
"""

import os
from typing import Dict, Any

# System configuration
SYSTEM_CONFIG = {{
    "harness": {{
        "startup_timeout": 30.0,
        "shutdown_timeout": 10.0,
        "health_check_interval": 5.0,
        "stream_buffer_size": 100,
        "enable_health_monitoring": True,
        "enable_performance_monitoring": True,
        "log_level": "INFO"
    }},
    "components": {component_configs},
    "metadata": {metadata}
}}

def get_config() -> Dict[str, Any]:
    """Get system configuration"""
    return SYSTEM_CONFIG.copy()

def get_component_config(component_name: str) -> Dict[str, Any]:
    """Get configuration for specific component"""
    return SYSTEM_CONFIG.get("components", {{}}).get(component_name, {{}})
'''
            
            # Extract component configurations
            component_configs = {}
            for component in blueprint.components:
                component_name = component.get('name', 'unnamed')
                component_configs[component_name] = component.get('configuration', {})
            
            config_code = config_template.format(
                description=blueprint.description,
                component_configs=self._format_dict_for_code(component_configs),
                metadata=self._format_dict_for_code(getattr(blueprint, 'metadata', {}))
            )
            
            self.logger.info(f"✅ Generated configuration for {len(component_configs)} components")
            return config_code
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate config: {e}")
            raise
    
    def generate_complete_scaffold(self, blueprint: SystemBlueprint) -> GeneratedScaffold:
        """
        Generate complete scaffold including main.py, config, and metadata.
        
        Args:
            blueprint: SystemBlueprint to generate scaffold from
            
        Returns:
            GeneratedScaffold with all generated artifacts
        """
        import time
        
        start_time = time.time()
        self.logger.info(f"🏗️ Generating complete scaffold for: {blueprint.description}")
        
        try:
            # Generate main components
            main_py_code = self.generate_main_py(blueprint)
            config_code = self.generate_config_file(blueprint)
            
            # Extract component information
            components = self._extract_components(blueprint)
            
            # Generate connections
            connections = self.connection_mapper.derive_connections(blueprint)
            
            # Generate imports
            imports = self._generate_component_imports(components)
            
            generation_time = time.time() - start_time
            
            scaffold = GeneratedScaffold(
                main_py_code=main_py_code,
                config_code=config_code,
                components=components,
                connections=[conn.__dict__ for conn in connections],
                imports=imports,
                generation_time=generation_time
            )
            
            self.logger.info(f"✅ Complete scaffold generated in {generation_time:.3f}s")
            return scaffold
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate complete scaffold: {e}")
            raise
    
    def _extract_components(self, blueprint: SystemBlueprint) -> List[ComponentInfo]:
        """Extract component information from blueprint"""
        components = []
        
        for component_def in blueprint.components:
            component_name = component_def.get('name', 'unnamed')
            component_type = component_def.get('type', 'generic')
            
            # Map component type to class name
            class_name = self.component_type_mapping.get(component_type, 
                                                       self._capitalize_component_type(component_type))
            
            # Extract dependencies
            dependencies = []
            for dep in component_def.get('dependencies', []):
                if isinstance(dep, dict):
                    dependencies.append(dep.get('component_name', ''))
                else:
                    dependencies.append(str(dep))
            
            # Generate import path
            import_path = f"components.{component_name}"
            
            component_info = ComponentInfo(
                name=component_name,
                class_name=class_name,
                component_type=component_type,
                config=component_def.get('configuration', {}),
                dependencies=dependencies,
                import_path=import_path
            )
            
            components.append(component_info)
        
        return components
    
    def _generate_component_imports(self, components: List[ComponentInfo]) -> List[str]:
        """Generate import statements for components"""
        imports = []
        
        for component in components:
            import_statement = f"from {component.import_path} import {component.class_name}"
            imports.append(import_statement)
        
        return imports
    
    def _generate_component_registration(self, components: List[ComponentInfo]) -> str:
        """Generate component registration code"""
        registration_lines = []
        
        for component in components:
            # Generate configuration
            config_dict = self._format_dict_for_code(component.config)
            
            # Generate registration line
            registration_line = f'''
        # Register {component.name} component
        {component.name}_config = {config_dict}
        {component.name}_component = {component.class_name}({component.name}_config)
        harness.register_component('{component.name}', {component.name}_component)'''
            
            registration_lines.append(registration_line)
        
        return '\n'.join(registration_lines)
    
    def _generate_connection_code(self, connections: List[Any]) -> str:
        """Generate stream connection code"""
        if not connections:
            return "        # No stream connections configured"
        
        connection_lines = []
        connection_lines.append("        # Stream connections")
        
        for connection in connections:
            connection_line = f"        harness.connect('{connection.source}', '{connection.target}')"
            connection_lines.append(connection_line)
        
        return '\n'.join(connection_lines)
    
    def _capitalize_component_type(self, component_type: str) -> str:
        """Convert component type to class name format"""
        # Convert snake_case to PascalCase
        words = component_type.replace('-', '_').split('_')
        return ''.join(word.capitalize() for word in words)
    
    def _format_dict_for_code(self, data: Dict[str, Any]) -> str:
        """Format dictionary for code generation"""
        if not data:
            return "{}"
        
        import json
        # Use JSON serialization for basic formatting
        return json.dumps(data, indent=4)
    
    def validate_blueprint_for_scaffold(self, blueprint: SystemBlueprint) -> Tuple[bool, List[str]]:
        """
        Validate blueprint for scaffold generation requirements.
        
        Args:
            blueprint: SystemBlueprint to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check blueprint has components
        if not blueprint.components:
            errors.append("Blueprint must contain at least one component")
        
        # Check each component has required fields
        for i, component in enumerate(blueprint.components):
            if not component.get('name'):
                errors.append(f"Component {i} is missing 'name' field")
            
            if not component.get('type'):
                errors.append(f"Component {i} is missing 'type' field")
            
            # Check for duplicate component names
            component_names = [comp.get('name') for comp in blueprint.components]
            if len(component_names) != len(set(component_names)):
                errors.append("Duplicate component names found")
        
        # Check blueprint has description
        if not blueprint.description:
            errors.append("Blueprint must have a description")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("✅ Blueprint validation passed for scaffold generation")
        else:
            self.logger.warning(f"⚠️ Blueprint validation failed: {errors}")
        
        return is_valid, errors


# Export main class
__all__ = ['SystemScaffoldGenerator', 'GeneratedScaffold', 'ComponentInfo']