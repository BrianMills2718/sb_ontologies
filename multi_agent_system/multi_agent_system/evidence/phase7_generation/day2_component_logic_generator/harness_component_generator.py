#!/usr/bin/env python3
"""
HarnessComponentGenerator: Generates HarnessComponent-based component code
=========================================================================

Phase 2 of the two-phase generation pipeline - generates HarnessComponent-based
component classes from ComponentLogic definitions with stream I/O and lifecycle methods.

Key Features:
- Generates HarnessComponent subclasses with proper inheritance
- Creates stream-based I/O handling code
- Generates lifecycle methods (setup/process/cleanup)
- Converts business logic to harness-compatible methods
- Handles error handling and recovery
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import ComponentLogic
from stream_io_templates import StreamIOTemplateEngine
from lifecycle_method_generator import LifecycleMethodGenerator


@dataclass
class GeneratedComponent:
    """Result of component generation"""
    component_name: str
    class_name: str
    component_code: str
    imports: List[str]
    dependencies: List[str]
    stream_interfaces: Dict[str, List[str]]
    business_methods: List[str]
    generation_metadata: Dict[str, Any]


class HarnessComponentGenerator:
    """
    Generates HarnessComponent-based component code from ComponentLogic definitions.
    """
    
    def __init__(self):
        self.template_engine = StreamIOTemplateEngine()
        self.lifecycle_generator = LifecycleMethodGenerator()
        self.logger = logging.getLogger("HarnessComponentGenerator")
        
        # Component type templates
        self.component_templates = self._load_component_templates()
        
        # Default stream interfaces for component types
        self.default_stream_interfaces = {
            'api_gateway': {
                'input': ['requests', 'incoming'],
                'output': ['responses', 'outgoing']
            },
            'task_controller': {
                'input': ['input', 'commands'],
                'output': ['store_commands', 'responses', 'process_requests']
            },
            'task_store': {
                'input': ['input', 'store_commands'],
                'output': ['responses', 'store_data']
            },
            'data_processor': {
                'input': ['input', 'process'],
                'output': ['processed_data', 'results']
            }
        }
        
        self.logger.info("🔧 HarnessComponentGenerator initialized")
    
    def generate_component(self, component_name: str, component_logic: ComponentLogic, 
                         component_type: str, config: Dict[str, Any] = None) -> GeneratedComponent:
        """
        Generate HarnessComponent class from ComponentLogic.
        
        Transforms function-based component logic into HarnessComponent class
        with stream-based communication and proper lifecycle management.
        
        Args:
            component_name: Name of the component
            component_logic: ComponentLogic definition with business methods
            component_type: Type of component
            config: Component configuration
            
        Returns:
            GeneratedComponent with complete class code
        """
        self.logger.info(f"🔧 Generating component: {component_name} ({component_type})")
        
        try:
            config = config or {}
            
            # Generate class definition
            class_name = self._get_class_name(component_name, component_type)
            class_def = self._generate_class_definition(class_name, component_type)
            
            # Generate imports
            imports = self._generate_imports(component_type)
            
            # Determine stream interfaces
            stream_interfaces = self._determine_stream_interfaces(component_type, component_logic)
            
            # Generate lifecycle methods
            init_method = self._generate_init_method(component_name, component_type, config)
            setup_method = self.lifecycle_generator.generate_setup_method(component_logic, stream_interfaces)
            process_method = self._generate_process_method(component_logic, stream_interfaces)
            cleanup_method = self.lifecycle_generator.generate_cleanup_method(component_logic)
            
            # Generate business logic methods
            business_methods = self._generate_business_logic_methods(component_logic)
            
            # Generate stream helper methods
            stream_helpers = self.template_engine.generate_stream_helper_methods(stream_interfaces)
            
            # Assemble complete component
            component_code = self._assemble_component_code(
                imports=imports,
                class_def=class_def,
                init_method=init_method,
                setup_method=setup_method,
                process_method=process_method,
                cleanup_method=cleanup_method,
                business_methods=business_methods,
                stream_helpers=stream_helpers
            )
            
            # Extract dependencies
            dependencies = self._extract_dependencies(component_logic, config)
            
            # Create result
            generated = GeneratedComponent(
                component_name=component_name,
                class_name=class_name,
                component_code=component_code,
                imports=imports,
                dependencies=dependencies,
                stream_interfaces=stream_interfaces,
                business_methods=[method['name'] for method in component_logic.business_methods],
                generation_metadata={
                    'component_type': component_type,
                    'generation_timestamp': self._get_timestamp(),
                    'stream_count': len(stream_interfaces.get('input', [])) + len(stream_interfaces.get('output', [])),
                    'business_method_count': len(component_logic.business_methods)
                }
            )
            
            self.logger.info(f"✅ Generated component {class_name} with {len(business_methods)} business methods")
            return generated
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate component {component_name}: {e}")
            raise
    
    def generate_component_from_blueprint(self, component_def: Dict[str, Any]) -> GeneratedComponent:
        """
        Generate component from blueprint component definition.
        
        Args:
            component_def: Component definition from blueprint
            
        Returns:
            GeneratedComponent
        """
        component_name = component_def.get('name', 'unnamed')
        component_type = component_def.get('type', 'generic')
        config = component_def.get('configuration', {})
        
        # Create ComponentLogic from blueprint
        component_logic = self._create_component_logic_from_blueprint(component_def)
        
        return self.generate_component(component_name, component_logic, component_type, config)
    
    def _get_class_name(self, component_name: str, component_type: str) -> str:
        """Generate class name from component name and type"""
        # Convert snake_case to PascalCase but preserve underscores for test compatibility
        words = component_name.replace('-', '_').split('_')
        return '_'.join(word.capitalize() for word in words)
    
    def _generate_class_definition(self, class_name: str, component_type: str) -> str:
        """Generate class definition line"""
        return f'''class {class_name}(HarnessComponent):
    """
    Generated {component_type} component
    
    Auto-generated by V5.0 Two-Phase Generation Pipeline
    Extends HarnessComponent for stream-based communication
    """'''
    
    def _generate_imports(self, component_type: str) -> List[str]:
        """Generate import statements for component"""
        base_imports = [
            "import asyncio",
            "import logging", 
            "import time",
            "import json",
            "from typing import Dict, Any, Optional, List",
            "",
            "# Import HarnessComponent base class",
            "from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent",
            "from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration"
        ]
        
        # Add component-specific imports
        if component_type == 'api_gateway':
            base_imports.extend([
                "from fastapi import FastAPI, HTTPException",
                "import uvicorn"
            ])
        elif component_type == 'task_store':
            base_imports.extend([
                "import redis.asyncio as redis",
                "import json"
            ])
        elif component_type == 'data_processor':
            base_imports.extend([
                "import numpy as np",
                "from datetime import datetime"
            ])
        
        return base_imports
    
    def _determine_stream_interfaces(self, component_type: str, component_logic: ComponentLogic) -> Dict[str, List[str]]:
        """Determine stream interfaces for component"""
        # Start with defaults for component type
        interfaces = self.default_stream_interfaces.get(component_type, {
            'input': ['input'],
            'output': ['output'] 
        }).copy()
        
        # Add interfaces from component logic
        if component_logic.stream_handlers:
            for stream_name, handler in component_logic.stream_handlers.items():
                if handler.get('direction') == 'input':
                    if stream_name not in interfaces.get('input', []):
                        interfaces.setdefault('input', []).append(stream_name)
                elif handler.get('direction') == 'output':
                    if stream_name not in interfaces.get('output', []):
                        interfaces.setdefault('output', []).append(stream_name)
        
        return interfaces
    
    def _generate_init_method(self, component_name: str, component_type: str, config: Dict[str, Any]) -> str:
        """Generate __init__ method"""
        return f'''
    def __init__(self, config: Dict[str, Any]):
        """Initialize {component_name} component"""
        component_config = ComponentConfiguration(
            name="{component_name}",
            service_type="{component_type}",
            **config
        )
        
        super().__init__(component_config)
        
        # Component-specific initialization
        self.config = config
        self.processing_stats = {{
            "messages_processed": 0,
            "processing_time_total": 0.0,
            "errors_count": 0
        }}
        
        self.logger.info(f"🔧 {{self.name}} ({component_type}) initialized")'''
    
    def _generate_process_method(self, component_logic: ComponentLogic, stream_interfaces: Dict[str, List[str]]) -> str:
        """Generate main process method with stream handling"""
        input_streams = stream_interfaces.get('input', [])
        output_streams = stream_interfaces.get('output', [])
        
        # Generate stream receive code
        receive_code = self.template_engine.generate_stream_receive_code(input_streams)
        
        # Generate business logic integration
        business_logic_code = self._generate_business_logic_integration(component_logic)
        
        # Generate stream send code
        send_code = self.template_engine.generate_stream_send_code(output_streams)
        
        process_method = f'''
    async def process(self):
        """Main processing loop with stream handling"""
        try:
            {receive_code}
            
        except Exception as e:
            self.logger.error(f"❌ Processing error in {{self.name}}: {{e}}")
            await self.handle_processing_error(e)
    
    async def process_message(self, message_data: Any) -> Optional[Dict[str, Any]]:
        """Process individual message"""
        start_time = time.time()
        
        try:
            # Business logic processing
            {business_logic_code}
            
            # Update statistics
            processing_time = time.time() - start_time
            self.processing_stats["messages_processed"] += 1
            self.processing_stats["processing_time_total"] += processing_time
            
            return result
            
        except Exception as e:
            self.processing_stats["errors_count"] += 1
            self.logger.error(f"❌ Message processing error: {{e}}")
            raise
    
    async def send_result(self, result: Dict[str, Any]):
        """Send processing result to appropriate output streams"""
        {send_code}
    
    async def handle_processing_error(self, error: Exception):
        """Handle processing errors with recovery"""
        self.logger.warning(f"⚠️ Handling processing error: {{error}}")
        
        # Error recovery logic
        await asyncio.sleep(0.1)  # Brief pause before retry'''
        
        return process_method
    
    def _generate_business_logic_integration(self, component_logic: ComponentLogic) -> str:
        """Generate business logic integration code"""
        if not component_logic.business_methods:
            return '''
            # Default processing - pass through message
            result = {
                "status": "processed",
                "data": message_data,
                "timestamp": time.time(),
                "component": self.name
            }'''
        
        # Generate calls to business methods
        business_calls = []
        for method in component_logic.business_methods:
            method_name = method.get('name', 'process_data')
            business_calls.append(f"result = await self.{method_name}(message_data)")
        
        return '\n            '.join(business_calls)
    
    def _generate_business_logic_methods(self, component_logic: ComponentLogic) -> List[str]:
        """Generate business logic methods from ComponentLogic"""
        methods = []
        
        for method_def in component_logic.business_methods:
            method_name = method_def.get('name', 'business_method')
            method_description = method_def.get('description', 'Business logic method')
            method_logic = method_def.get('logic', 'return {"status": "processed", "data": data}')
            
            method_code = f'''
    async def {method_name}(self, data: Any) -> Dict[str, Any]:
        """
        {method_description}
        Generated from ComponentLogic definition
        """
        try:
            # Business logic implementation
            {method_logic}
            
        except Exception as e:
            self.logger.error(f"❌ Business method {method_name} error: {{e}}")
            raise'''
            
            methods.append(method_code)
        
        # Add default methods if none provided
        if not methods:
            methods.append('''
    async def process_data(self, data: Any) -> Dict[str, Any]:
        """Default data processing method"""
        return {
            "status": "processed",
            "data": data,
            "timestamp": time.time(),
            "component": self.name
        }''')
        
        return methods
    
    def _assemble_component_code(self, imports: List[str], class_def: str, init_method: str,
                                setup_method: str, process_method: str, cleanup_method: str,
                                business_methods: List[str], stream_helpers: List[str]) -> str:
        """Assemble complete component code"""
        
        code_parts = [
            '#!/usr/bin/env python3',
            '"""',
            'Generated HarnessComponent',
            'Auto-generated by V5.0 Two-Phase Generation Pipeline',
            '"""',
            '',
            # Imports
            '\n'.join(imports),
            '',
            '',
            # Class definition
            class_def,
            '',
            # Methods
            init_method,
            '',
            setup_method,
            '',
            process_method,
            '',
            cleanup_method,
            '',
            # Business methods
            '\n'.join(business_methods),
            '',
            # Stream helpers
            '\n'.join(stream_helpers)
        ]
        
        return '\n'.join(code_parts)
    
    def _create_component_logic_from_blueprint(self, component_def: Dict[str, Any]) -> ComponentLogic:
        """Create ComponentLogic from blueprint component definition"""
        component_type = component_def.get('type', 'generic')
        
        # Generate default business methods based on component type
        default_methods = self._get_default_business_methods(component_type)
        
        return ComponentLogic(
            business_methods=default_methods,
            processing_logic={
                'type': component_type,
                'mode': 'async'
            },
            stream_handlers={},
            initialization_code=None,
            cleanup_code=None
        )
    
    def _get_default_business_methods(self, component_type: str) -> List[Dict[str, Any]]:
        """Get default business methods for component type"""
        method_templates = {
            'api_gateway': [
                {
                    'name': 'handle_request',
                    'description': 'Handle incoming HTTP request',
                    'logic': '''
            # Extract request data
            request_data = data.get('request', {})
            method = request_data.get('method', 'GET')
            path = request_data.get('path', '/')
            
            # Process request
            if method == 'GET' and path.startswith('/tasks'):
                result = {"status": "success", "data": [], "method": method}
            elif method == 'POST' and path.startswith('/tasks'):
                result = {"status": "created", "data": request_data.get('body', {})}
            else:
                result = {"status": "not_found", "error": f"Path {path} not found"}
            
            return result'''
                }
            ],
            'task_controller': [
                {
                    'name': 'process_task_request',
                    'description': 'Process task management request',
                    'logic': '''
            request_type = data.get('type', 'unknown')
            
            if request_type == 'create_task':
                task_data = data.get('data', {})
                result = {
                    "status": "processing",
                    "task_id": f"task_{int(time.time())}",
                    "data": task_data
                }
            elif request_type == 'get_tasks':
                result = {"status": "fetching", "query": data.get('query', {})}
            else:
                result = {"status": "error", "message": f"Unknown request type: {request_type}"}
            
            return result'''
                }
            ],
            'task_store': [
                {
                    'name': 'store_task_data',
                    'description': 'Store task data',
                    'logic': '''
            operation = data.get('operation', 'store')
            task_data = data.get('data', {})
            
            if operation == 'store':
                # Simulate storing data
                result = {
                    "status": "stored", 
                    "id": task_data.get('task_id', 'unknown'),
                    "timestamp": time.time()
                }
            elif operation == 'retrieve':
                # Simulate retrieving data  
                result = {
                    "status": "retrieved",
                    "data": {"task_id": "sample", "title": "Sample Task"},
                    "timestamp": time.time()
                }
            else:
                result = {"status": "error", "message": f"Unknown operation: {operation}"}
                
            return result'''
                }
            ],
            'data_processor': [
                {
                    'name': 'process_data',
                    'description': 'Process and transform data',
                    'logic': '''
            # Data transformation logic
            processed_data = data.copy() if isinstance(data, dict) else {"raw_data": data}
            
            # Add processing metadata
            processed_data.update({
                "processed": True,
                "processing_timestamp": time.time(),
                "processor": self.name
            })
            
            # Simulate data enrichment
            if "title" in processed_data:
                processed_data["title_length"] = len(str(processed_data["title"]))
            
            result = {
                "status": "processed",
                "data": processed_data
            }
            
            return result'''
                }
            ]
        }
        
        return method_templates.get(component_type, [
            {
                'name': 'process_data',
                'description': 'Generic data processing',
                'logic': 'return {"status": "processed", "data": data, "timestamp": time.time()}'
            }
        ])
    
    def _extract_dependencies(self, component_logic: ComponentLogic, config: Dict[str, Any]) -> List[str]:
        """Extract component dependencies"""
        dependencies = []
        
        # Check config for dependencies
        if 'dependencies' in config:
            dependencies.extend(config['dependencies'])
        
        # Check processing logic for dependencies
        if component_logic.processing_logic.get('requires_database'):
            dependencies.append('database')
        
        if component_logic.processing_logic.get('requires_cache'):
            dependencies.append('cache')
        
        return list(set(dependencies))  # Remove duplicates
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _load_component_templates(self) -> Dict[str, str]:
        """Load component type templates"""
        # Component-specific template overrides
        return {
            'api_gateway': 'FastAPI-based API gateway',
            'task_controller': 'Task management controller',
            'task_store': 'Task data storage component',
            'data_processor': 'Data processing and transformation'
        }


# Export main class
__all__ = ['HarnessComponentGenerator', 'GeneratedComponent']