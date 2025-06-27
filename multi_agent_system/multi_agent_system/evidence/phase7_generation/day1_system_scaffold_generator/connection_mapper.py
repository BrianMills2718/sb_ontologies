#!/usr/bin/env python3
"""
ConnectionMapper: Maps SystemBlueprint component bindings to SystemExecutionHarness stream connections
=======================================================================================================

Derives stream connections from blueprint component bindings, converting blueprint-level
component communication definitions into harness-compatible stream connections.

Key Features:
- Maps blueprint bindings to harness stream connections
- Validates connection consistency
- Generates connection metadata
- Supports multiple connection patterns
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import SystemBlueprint


@dataclass
class StreamConnection:
    """Represents a stream connection between components"""
    source: str  # Format: "component_name.port_name"
    target: str  # Format: "component_name.port_name"
    buffer_size: int
    connection_type: str
    metadata: Dict[str, Any]
    
    @property
    def source_component(self) -> str:
        """Get source component name"""
        return self.source.split('.')[0]
    
    @property
    def source_port(self) -> str:
        """Get source port name"""
        return self.source.split('.', 1)[1] if '.' in self.source else 'output'
    
    @property
    def target_component(self) -> str:
        """Get target component name"""
        return self.target.split('.')[0]
    
    @property
    def target_port(self) -> str:
        """Get target port name"""
        return self.target.split('.', 1)[1] if '.' in self.target else 'input'


class ConnectionMapper:
    """
    Maps SystemBlueprint component bindings to SystemExecutionHarness stream connections.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ConnectionMapper")
        
        # Default port mappings for common component types
        self.default_ports = {
            'api_gateway': {
                'input': ['requests', 'incoming'],
                'output': ['responses', 'outgoing']
            },
            'task_controller': {
                'input': ['process_request', 'commands'],
                'output': ['store_operation', 'responses']
            },
            'task_store': {
                'input': ['execute', 'store_commands'],
                'output': ['responses', 'store_data']
            },
            'data_processor': {
                'input': ['data_input', 'process'],
                'output': ['processed_data', 'results']
            },
            'web_service': {
                'input': ['requests'],
                'output': ['responses']
            },
            'database': {
                'input': ['queries'],
                'output': ['results']
            }
        }
        
        self.logger.info("🗺️ ConnectionMapper initialized")
    
    def derive_connections(self, blueprint: SystemBlueprint) -> List[StreamConnection]:
        """
        Derive stream connections from blueprint component bindings.
        
        Blueprint Binding Example:
        ```yaml
        components:
          api_gateway:
            bindings:
              - source: "request_input"
                target: "task_controller.process_request"
          task_controller:
            bindings:
              - source: "store_operation"  
                target: "task_store.execute"
        ```
        
        Generated Connections:
        ```python
        harness.connect('api_gateway.request_input', 'task_controller.process_request')
        harness.connect('task_controller.store_operation', 'task_store.execute')
        ```
        
        Args:
            blueprint: SystemBlueprint containing component bindings
            
        Returns:
            List of StreamConnection objects
        """
        self.logger.info("🗺️ Deriving stream connections from blueprint")
        
        connections = []
        
        try:
            # Process explicit bindings from blueprint
            explicit_connections = self._process_explicit_bindings(blueprint)
            connections.extend(explicit_connections)
            
            # Generate implicit connections based on component types and dependencies
            implicit_connections = self._generate_implicit_connections(blueprint)
            connections.extend(implicit_connections)
            
            # Validate connections
            validated_connections = self._validate_connections(connections, blueprint)
            
            self.logger.info(f"✅ Derived {len(validated_connections)} stream connections")
            return validated_connections
            
        except Exception as e:
            self.logger.error(f"❌ Failed to derive connections: {e}")
            raise
    
    def _process_explicit_bindings(self, blueprint: SystemBlueprint) -> List[StreamConnection]:
        """Process explicit bindings defined in blueprint components"""
        connections = []
        
        for component in blueprint.components:
            component_name = component.get('name', 'unnamed')
            bindings = component.get('bindings', [])
            
            for binding in bindings:
                source_endpoint = f"{component_name}.{binding['source']}"
                target_endpoint = binding['target']
                
                # Handle target format (may or may not include component name)
                if '.' not in target_endpoint:
                    # Need to infer target component from dependencies
                    target_component = self._infer_target_component(component_name, target_endpoint, blueprint)
                    if target_component:
                        target_endpoint = f"{target_component}.{target_endpoint}"
                
                connection = StreamConnection(
                    source=source_endpoint,
                    target=target_endpoint,
                    buffer_size=binding.get('buffer_size', 100),
                    connection_type=binding.get('type', 'data_stream'),
                    metadata={
                        'binding_type': 'explicit',
                        'component': component_name,
                        'original_binding': binding
                    }
                )
                
                connections.append(connection)
        
        return connections
    
    def _generate_implicit_connections(self, blueprint: SystemBlueprint) -> List[StreamConnection]:
        """Generate implicit connections based on component dependencies"""
        connections = []
        
        # Build component map
        components_by_name = {comp.get('name'): comp for comp in blueprint.components}
        
        for component in blueprint.components:
            component_name = component.get('name', 'unnamed')
            component_type = component.get('type', 'generic')
            dependencies = component.get('dependencies', [])
            
            for dependency in dependencies:
                dep_name = dependency.get('component_name') if isinstance(dependency, dict) else str(dependency)
                
                if dep_name in components_by_name:
                    dep_component = components_by_name[dep_name]
                    dep_type = dep_component.get('type', 'generic')
                    
                    # Generate connections based on component types
                    implicit_connection = self._create_implicit_connection(
                        component_name, component_type, dep_name, dep_type
                    )
                    
                    if implicit_connection:
                        connections.append(implicit_connection)
        
        return connections
    
    def _create_implicit_connection(self, source_comp: str, source_type: str, 
                                  target_comp: str, target_type: str) -> Optional[StreamConnection]:
        """Create implicit connection between two components based on their types"""
        
        # Define common connection patterns
        connection_patterns = {
            ('api_gateway', 'task_controller'): ('requests', 'input'),
            ('task_controller', 'task_store'): ('store_commands', 'input'),
            ('task_store', 'task_controller'): ('responses', 'store_data'),
            ('task_controller', 'api_gateway'): ('responses', 'responses'),
            ('web_service', 'database'): ('queries', 'input'),
            ('database', 'web_service'): ('results', 'output'),
            ('data_processor', 'task_store'): ('processed_data', 'input')
        }
        
        pattern_key = (source_type, target_type)
        if pattern_key in connection_patterns:
            source_port, target_port = connection_patterns[pattern_key]
            
            return StreamConnection(
                source=f"{source_comp}.{source_port}",
                target=f"{target_comp}.{target_port}",
                buffer_size=100,
                connection_type='data_stream',
                metadata={
                    'binding_type': 'implicit',
                    'pattern': pattern_key,
                    'auto_generated': True
                }
            )
        
        return None
    
    def _infer_target_component(self, source_component: str, target_port: str, 
                              blueprint: SystemBlueprint) -> Optional[str]:
        """Infer target component from dependencies and component types"""
        
        # Get source component info
        source_comp_info = None
        for comp in blueprint.components:
            if comp.get('name') == source_component:
                source_comp_info = comp
                break
        
        if not source_comp_info:
            return None
        
        # Check dependencies first
        dependencies = source_comp_info.get('dependencies', [])
        if dependencies:
            # Use first dependency as target
            first_dep = dependencies[0]
            if isinstance(first_dep, dict):
                return first_dep.get('component_name')
            else:
                return str(first_dep)
        
        # Fallback: try to match by port name and component type
        for comp in blueprint.components:
            comp_name = comp.get('name')
            comp_type = comp.get('type', 'generic')
            
            if comp_name != source_component:
                # Check if this component type typically accepts this port
                if self._component_accepts_port(comp_type, target_port):
                    return comp_name
        
        return None
    
    def _component_accepts_port(self, component_type: str, port_name: str) -> bool:
        """Check if a component type typically accepts a given port"""
        
        if component_type in self.default_ports:
            input_ports = self.default_ports[component_type].get('input', [])
            return port_name in input_ports
        
        # Default acceptance patterns
        common_input_ports = ['input', 'process', 'execute', 'store', 'handle']
        return port_name in common_input_ports
    
    def _validate_connections(self, connections: List[StreamConnection], 
                            blueprint: SystemBlueprint) -> List[StreamConnection]:
        """Validate and deduplicate connections"""
        
        valid_connections = []
        seen_connections = set()
        component_names = {comp.get('name') for comp in blueprint.components}
        
        for connection in connections:
            # Create connection signature for deduplication
            connection_signature = (connection.source, connection.target)
            
            if connection_signature in seen_connections:
                self.logger.debug(f"Skipping duplicate connection: {connection.source} → {connection.target}")
                continue
            
            # Validate component names exist
            if connection.source_component not in component_names:
                self.logger.warning(f"Source component not found: {connection.source_component}")
                continue
            
            if connection.target_component not in component_names:
                self.logger.warning(f"Target component not found: {connection.target_component}")
                continue
            
            # Validate no self-connections
            if connection.source_component == connection.target_component:
                self.logger.warning(f"Skipping self-connection: {connection.source}")
                continue
            
            seen_connections.add(connection_signature)
            valid_connections.append(connection)
        
        return valid_connections
    
    def get_connection_summary(self, connections: List[StreamConnection]) -> Dict[str, Any]:
        """Get summary information about connections"""
        
        if not connections:
            return {"total_connections": 0}
        
        components = set()
        connection_types = set()
        buffer_sizes = []
        
        for conn in connections:
            components.add(conn.source_component)
            components.add(conn.target_component)
            connection_types.add(conn.connection_type)
            buffer_sizes.append(conn.buffer_size)
        
        return {
            "total_connections": len(connections),
            "components_involved": len(components),
            "connection_types": list(connection_types),
            "average_buffer_size": sum(buffer_sizes) / len(buffer_sizes) if buffer_sizes else 0,
            "connection_details": [
                {
                    "source": conn.source,
                    "target": conn.target,
                    "type": conn.connection_type
                }
                for conn in connections
            ]
        }
    
    def visualize_connections(self, connections: List[StreamConnection]) -> str:
        """Generate a text visualization of connections"""
        
        if not connections:
            return "No connections to visualize"
        
        lines = ["Connection Graph:", "=" * 50]
        
        for conn in connections:
            arrow = "──→" if conn.connection_type == 'data_stream' else "━━→"
            line = f"{conn.source} {arrow} {conn.target}"
            lines.append(line)
        
        return "\n".join(lines)


# Export main class  
__all__ = ['ConnectionMapper', 'StreamConnection']