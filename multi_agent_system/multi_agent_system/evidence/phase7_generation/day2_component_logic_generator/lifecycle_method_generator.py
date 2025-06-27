#!/usr/bin/env python3
"""
LifecycleMethodGenerator: Generates HarnessComponent lifecycle methods
======================================================================

Generates setup, cleanup, and other lifecycle methods for HarnessComponent classes
with proper resource management and stream initialization.

Key Features:
- Setup method generation with stream validation
- Cleanup method generation with resource disposal
- Error handling and recovery logic
- Component-specific initialization patterns
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

# Add evidence paths for integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from blueprint_types import ComponentLogic


class LifecycleMethodGenerator:
    """
    Generates lifecycle methods for HarnessComponent classes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("LifecycleMethodGenerator")
        
        # Component type specific setup patterns
        self.setup_patterns = {
            'api_gateway': self._generate_api_gateway_setup,
            'task_store': self._generate_task_store_setup,
            'data_processor': self._generate_data_processor_setup,
            'task_controller': self._generate_task_controller_setup
        }
        
        self.logger.info("🔄 LifecycleMethodGenerator initialized")
    
    def generate_setup_method(self, component_logic: ComponentLogic, 
                            stream_interfaces: Dict[str, List[str]]) -> str:
        """
        Generate setup method for component initialization
        
        Args:
            component_logic: Component logic definition
            stream_interfaces: Stream interface definitions
            
        Returns:
            Generated setup method code
        """
        # Get component type from processing logic
        component_type = component_logic.processing_logic.get('type', 'generic')
        
        # Generate base setup
        base_setup = self._generate_base_setup(stream_interfaces)
        
        # Generate component-specific setup
        specific_setup = ""
        if component_type in self.setup_patterns:
            specific_setup = self.setup_patterns[component_type]()
        
        # Combine initialization code if provided
        initialization_code = component_logic.initialization_code or ""
        
        setup_method = f'''
    async def _initialize_component_resources(self):
        """Initialize component-specific resources"""
        self.logger.info(f"🔧 Initializing {{self.name}} resources")
        
        try:
            {base_setup}
            
            {specific_setup}
            
            {initialization_code}
            
            self.logger.info(f"✅ {{self.name}} resources initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ {{self.name}} resource initialization failed: {{e}}")
            raise'''
        
        return setup_method
    
    def generate_cleanup_method(self, component_logic: ComponentLogic) -> str:
        """
        Generate cleanup method for resource disposal
        
        Args:
            component_logic: Component logic definition
            
        Returns:
            Generated cleanup method code
        """
        # Get component type
        component_type = component_logic.processing_logic.get('type', 'generic')
        
        # Generate component-specific cleanup
        specific_cleanup = self._generate_specific_cleanup(component_type)
        
        # Add custom cleanup code if provided
        cleanup_code = component_logic.cleanup_code or ""
        
        cleanup_method = f'''
    async def _cleanup_component_resources(self):
        """Clean up component-specific resources"""
        self.logger.info(f"🧹 Cleaning up {{self.name}} resources")
        
        try:
            {specific_cleanup}
            
            {cleanup_code}
            
            # Close any remaining resources
            if hasattr(self, 'resource_handles'):
                for handle_name, handle in self.resource_handles.items():
                    try:
                        if hasattr(handle, 'close'):
                            await handle.close()
                        elif hasattr(handle, 'disconnect'):
                            await handle.disconnect()
                        self.logger.debug(f"✅ Closed {{handle_name}}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error closing {{handle_name}}: {{e}}")
            
            self.logger.info(f"✅ {{self.name}} cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ {{self.name}} cleanup failed: {{e}}")
            # Don't re-raise cleanup errors'''
        
        return cleanup_method
    
    def _generate_base_setup(self, stream_interfaces: Dict[str, List[str]]) -> str:
        """Generate base setup code common to all components"""
        input_streams = stream_interfaces.get('input', [])
        output_streams = stream_interfaces.get('output', [])
        
        return f'''
        # Initialize stream error tracking
        self.stream_errors = {{}}
        
        # Initialize resource handles
        self.resource_handles = {{}}
        
        # Validate expected streams will be available
        self.expected_input_streams = {input_streams}
        self.expected_output_streams = {output_streams}
        
        # Initialize component state
        self.component_state = {{
            "initialized": True,
            "initialization_time": time.time(),
            "status": "ready"
        }}'''
    
    def _generate_api_gateway_setup(self) -> str:
        """Generate API gateway specific setup"""
        return '''
        # Initialize FastAPI application
        self.app = FastAPI(title=f"{self.name} API")
        
        # Setup CORS if enabled
        if self.config.get('cors_enabled', False):
            from fastapi.middleware.cors import CORSMiddleware
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Setup API routes
        await self._setup_api_routes()
        
        # Store server configuration
        self.server_config = {
            "host": self.config.get('host', '0.0.0.0'),
            "port": self.config.get('port', 8080),
            "log_level": "info"
        }'''
    
    def _generate_task_store_setup(self) -> str:
        """Generate task store specific setup"""
        return '''
        # Initialize storage backend
        storage_type = self.config.get('storage_type', 'memory')
        
        if storage_type == 'redis':
            # Setup Redis connection
            redis_config = {
                "host": self.config.get('redis_host', 'localhost'),
                "port": self.config.get('redis_port', 6379),
                "db": self.config.get('redis_db', 0)
            }
            self.redis_client = redis.Redis(**redis_config)
            self.resource_handles['redis'] = self.redis_client
            
        elif storage_type == 'memory':
            # Setup in-memory storage
            self.memory_store = {}
            
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
        
        # Initialize storage metrics
        self.storage_metrics = {
            "operations_count": 0,
            "stored_items": 0,
            "retrieved_items": 0
        }'''
    
    def _generate_data_processor_setup(self) -> str:
        """Generate data processor specific setup"""
        return '''
        # Initialize processing configuration
        self.batch_size = self.config.get('batch_size', 10)
        self.processing_interval = self.config.get('processing_interval', 1.0)
        self.processing_mode = self.config.get('processing_mode', 'async')
        
        # Initialize processing buffers
        self.processing_buffer = []
        self.processed_count = 0
        
        # Setup processing pipeline
        self.processing_pipeline = {
            "stages": [],
            "current_stage": 0,
            "processing_stats": {
                "total_processed": 0,
                "average_processing_time": 0.0,
                "error_count": 0
            }
        }'''
    
    def _generate_task_controller_setup(self) -> str:
        """Generate task controller specific setup"""
        return '''
        # Initialize task management
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 10)
        self.processing_timeout = self.config.get('processing_timeout', 30)
        
        # Initialize task tracking
        self.active_tasks = {}
        self.task_queue = []
        self.completed_tasks = {}
        
        # Initialize task statistics
        self.task_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_processing_time": 0.0
        }
        
        # Setup task processing semaphore
        self.task_semaphore = asyncio.Semaphore(self.max_concurrent_tasks)'''
    
    def _generate_specific_cleanup(self, component_type: str) -> str:
        """Generate component-specific cleanup code"""
        cleanup_patterns = {
            'api_gateway': '''
            # Cleanup API server
            if hasattr(self, 'server') and self.server:
                try:
                    self.server.shutdown()
                except:
                    pass''',
            
            'task_store': '''
            # Cleanup storage connections
            if hasattr(self, 'redis_client'):
                try:
                    await self.redis_client.close()
                except:
                    pass
            
            # Clear memory storage
            if hasattr(self, 'memory_store'):
                self.memory_store.clear()''',
            
            'data_processor': '''
            # Flush processing buffers
            if hasattr(self, 'processing_buffer'):
                self.processing_buffer.clear()
            
            # Clear processing pipeline
            if hasattr(self, 'processing_pipeline'):
                self.processing_pipeline['stages'].clear()''',
            
            'task_controller': '''
            # Cancel active tasks
            if hasattr(self, 'active_tasks'):
                for task_id, task in self.active_tasks.items():
                    try:
                        if not task.done():
                            task.cancel()
                    except:
                        pass
                self.active_tasks.clear()
            
            # Clear task queue
            if hasattr(self, 'task_queue'):
                self.task_queue.clear()'''
        }
        
        return cleanup_patterns.get(component_type, '''
            # Generic cleanup
            self.logger.debug("Performing generic component cleanup")''')
    
    def generate_health_check_method(self, component_type: str, 
                                   stream_interfaces: Dict[str, List[str]]) -> str:
        """
        Generate health check method for component monitoring
        
        Args:
            component_type: Type of component
            stream_interfaces: Stream interface definitions
            
        Returns:
            Generated health check method code
        """
        base_health_check = '''
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with component-specific metrics"""
        base_health = await super().health_check()
        
        # Add component-specific health metrics
        component_health = {
            "component_state": getattr(self, 'component_state', {}),
            "resource_status": {},
            "stream_status": self.get_stream_status() if hasattr(self, 'get_stream_status') else {},
            "processing_stats": getattr(self, 'processing_stats', {})
        }'''
        
        # Add component-specific health checks
        specific_checks = {
            'api_gateway': '''
        # API Gateway specific health
        if hasattr(self, 'app'):
            component_health["api_status"] = "ready"
        
        if hasattr(self, 'server_config'):
            component_health["server_config"] = self.server_config''',
            
            'task_store': '''
        # Task Store specific health
        if hasattr(self, 'storage_metrics'):
            component_health["storage_metrics"] = self.storage_metrics
        
        if hasattr(self, 'redis_client'):
            try:
                await self.redis_client.ping()
                component_health["redis_status"] = "connected"
            except:
                component_health["redis_status"] = "disconnected"''',
            
            'data_processor': '''
        # Data Processor specific health
        if hasattr(self, 'processing_pipeline'):
            component_health["pipeline_status"] = {
                "stages": len(self.processing_pipeline.get('stages', [])),
                "current_stage": self.processing_pipeline.get('current_stage', 0),
                "stats": self.processing_pipeline.get('processing_stats', {})
            }
        
        if hasattr(self, 'processing_buffer'):
            component_health["buffer_size"] = len(self.processing_buffer)''',
            
            'task_controller': '''
        # Task Controller specific health
        if hasattr(self, 'task_stats'):
            component_health["task_stats"] = self.task_stats
        
        if hasattr(self, 'active_tasks'):
            component_health["active_tasks_count"] = len(self.active_tasks)
        
        if hasattr(self, 'task_queue'):
            component_health["queued_tasks_count"] = len(self.task_queue)'''
        }
        
        specific_check = specific_checks.get(component_type, '''
        # Generic component health check
        component_health["generic_status"] = "operational"''')
        
        return f'''{base_health_check}
        {specific_check}
        
        # Merge with base health
        base_health.update(component_health)
        return base_health'''


# Export main class  
__all__ = ['LifecycleMethodGenerator']