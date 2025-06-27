#!/usr/bin/env python3
"""
SystemExecutionHarness: Universal orchestrator for component-based systems
=========================================================================

The core SystemExecutionHarness provides universal orchestration for 
component-based systems with stream-based communication, lifecycle management,
and error recovery capabilities.

Key Features:
- Component registration and lifecycle management
- Stream-based connection setup and management
- Concurrent execution using AnyIO TaskGroup
- Graceful shutdown with proper resource cleanup
- Error handling and component failure recovery
- Performance monitoring and health checks
"""

import asyncio
import anyio
from anyio.abc import TaskGroup
import time
import logging
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase6_harness.day1_harness_component.harness_component import (
    HarnessComponent, HarnessContext, StreamOperationError
)
from evidence.phase6_harness.day1_harness_component.component_status import ComponentState
from evidence.phase6_harness.day2_execution_harness.stream_manager import StreamManager, StreamManagerError


class HarnessState(Enum):
    """States of the SystemExecutionHarness"""
    CREATED = "created"
    CONFIGURED = "configured" 
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ComponentRegistration:
    """Information about a registered component"""
    name: str
    component: HarnessComponent
    registration_time: float
    start_priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    required_for: List[str] = field(default_factory=list)


@dataclass
class StreamConnection:
    """Information about a stream connection between components"""
    id: str
    from_component: str
    from_port: str
    to_component: str
    to_port: str
    buffer_size: int
    created_at: float
    stream_id: str


@dataclass
class HarnessConfiguration:
    """Configuration for the SystemExecutionHarness"""
    startup_timeout: float = 30.0
    shutdown_timeout: float = 10.0
    health_check_interval: float = 5.0
    max_startup_retries: int = 3
    component_startup_delay: float = 0.1
    stream_buffer_size: int = 100
    enable_health_monitoring: bool = True
    enable_performance_monitoring: bool = True
    log_level: str = "INFO"


class ComponentAlreadyRegisteredError(Exception):
    """Raised when attempting to register a component that already exists"""
    pass


class ComponentNotFoundError(Exception):
    """Raised when referencing a component that doesn't exist"""
    pass


class HarnessAlreadyRunningError(Exception):
    """Raised when attempting to start a harness that's already running"""
    pass


class HarnessConfigurationError(Exception):
    """Raised when harness configuration is invalid"""
    pass


class ComponentStartupError(Exception):
    """Raised when component startup fails"""
    pass


class SystemExecutionHarness:
    """
    Universal orchestrator for component-based systems
    
    Provides:
    - Component registration and lifecycle management
    - Stream-based communication setup and management
    - Concurrent execution with proper error handling
    - Health monitoring and performance tracking
    - Graceful shutdown with resource cleanup
    """
    
    def __init__(self, config: Optional[HarnessConfiguration] = None):
        self.config = config or HarnessConfiguration()
        self.harness_id = str(uuid.uuid4())
        
        # State management
        self.state = HarnessState.CREATED
        self.creation_time = time.time()
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        
        # Component management
        self.components: Dict[str, ComponentRegistration] = {}
        self.stream_connections: Dict[str, StreamConnection] = {}
        
        # Stream management
        self.stream_manager = StreamManager(default_buffer_size=self.config.stream_buffer_size)
        
        # Execution management
        self.task_group: Optional[TaskGroup] = None
        self.component_tasks: Dict[str, asyncio.Task] = {}
        self.running = False
        
        # Monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.last_health_check: float = 0
        self.component_health_status: Dict[str, Dict[str, Any]] = {}
        
        # Error tracking
        self.startup_errors: List[str] = []
        self.runtime_errors: List[str] = []
        self.failed_components: Set[str] = set()
        
        # Performance tracking
        self.performance_metrics = {
            "total_messages_processed": 0,
            "total_startup_time": 0,
            "average_component_startup_time": 0,
            "peak_memory_usage": 0
        }
        
        # Logging
        self.logger = logging.getLogger(f"SystemExecutionHarness.{self.harness_id[:8]}")
        self.logger.info(f"✨ SystemExecutionHarness created with ID: {self.harness_id[:8]}")
        
        # Setup logging level
        if hasattr(logging, self.config.log_level):
            self.logger.setLevel(getattr(logging, self.config.log_level))
    
    def register_component(self, name: str, component: HarnessComponent, 
                          start_priority: int = 0, dependencies: Optional[List[str]] = None):
        """
        Register a component with the harness
        
        Args:
            name: Unique name for the component
            component: HarnessComponent instance
            start_priority: Priority for startup order (higher = later)
            dependencies: List of component names this component depends on
            
        Raises:
            ComponentAlreadyRegisteredError: If component name already exists
        """
        if name in self.components:
            raise ComponentAlreadyRegisteredError(f"Component '{name}' already registered")
        
        if not isinstance(component, HarnessComponent):
            raise HarnessConfigurationError(f"Component '{name}' must be a HarnessComponent instance")
        
        registration = ComponentRegistration(
            name=name,
            component=component,
            registration_time=time.time(),
            start_priority=start_priority,
            dependencies=dependencies or []
        )
        
        self.components[name] = registration
        
        # Update dependency tracking
        for dependency in registration.dependencies:
            if dependency in self.components:
                self.components[dependency].required_for.append(name)
        
        self.logger.info(f"📝 Registered component '{name}' with priority {start_priority}")
        
        # Update harness state
        if self.state == HarnessState.CREATED:
            self.state = HarnessState.CONFIGURED
    
    def unregister_component(self, name: str):
        """
        Unregister a component from the harness
        
        Args:
            name: Name of the component to unregister
            
        Raises:
            ComponentNotFoundError: If component doesn't exist
        """
        if name not in self.components:
            raise ComponentNotFoundError(f"Component '{name}' not found")
        
        if self.running:
            raise HarnessAlreadyRunningError("Cannot unregister components while harness is running")
        
        # Remove from dependency lists
        registration = self.components[name]
        for dependency in registration.dependencies:
            if dependency in self.components:
                self.components[dependency].required_for.remove(name)
        
        del self.components[name]
        self.logger.info(f"📝 Unregistered component '{name}'")
    
    def connect(self, from_output: str, to_input: str, buffer_size: Optional[int] = None):
        """
        Create stream-based connection between components
        
        Args:
            from_output: Source in format "component_name.port_name"
            to_input: Destination in format "component_name.port_name"
            buffer_size: Buffer size for the stream (uses default if None)
            
        Raises:
            ComponentNotFoundError: If referenced components don't exist
            HarnessConfigurationError: If connection format is invalid
        """
        # Parse connection strings
        try:
            from_component, from_port = from_output.split(".", 1)
            to_component, to_port = to_input.split(".", 1)
        except ValueError:
            raise HarnessConfigurationError(
                f"Invalid connection format. Use 'component.port' format. Got: '{from_output}' -> '{to_input}'"
            )
        
        # Validate components exist
        if from_component not in self.components:
            raise ComponentNotFoundError(f"Source component '{from_component}' not found")
        
        if to_component not in self.components:
            raise ComponentNotFoundError(f"Target component '{to_component}' not found")
        
        # Create stream
        buffer_size = buffer_size or self.config.stream_buffer_size
        send_stream, receive_stream = self.stream_manager.create_stream(
            buffer_size=buffer_size,
            source_component=from_component,
            target_component=to_component
        )
        
        # Connect streams to components
        from_comp = self.components[from_component].component
        to_comp = self.components[to_component].component
        
        from_comp.add_send_stream(from_port, send_stream, to_component)
        to_comp.add_receive_stream(to_port, receive_stream, from_component)
        
        # Track connection
        connection_id = str(uuid.uuid4())
        connection = StreamConnection(
            id=connection_id,
            from_component=from_component,
            from_port=from_port,
            to_component=to_component,
            to_port=to_port,
            buffer_size=buffer_size,
            created_at=time.time(),
            stream_id=""  # Stream manager handles IDs internally
        )
        
        self.stream_connections[connection_id] = connection
        
        self.logger.info(f"🔗 Connected {from_component}.{from_port} → {to_component}.{to_port} (buffer: {buffer_size})")
    
    def disconnect(self, connection_id: str):
        """
        Remove a stream connection
        
        Args:
            connection_id: ID of the connection to remove
            
        Raises:
            ComponentNotFoundError: If connection ID doesn't exist
        """
        if connection_id not in self.stream_connections:
            raise ComponentNotFoundError(f"Connection '{connection_id}' not found")
        
        if self.running:
            raise HarnessAlreadyRunningError("Cannot disconnect streams while harness is running")
        
        connection = self.stream_connections[connection_id]
        del self.stream_connections[connection_id]
        
        self.logger.info(f"🔗 Disconnected {connection.from_component}.{connection.from_port} → {connection.to_component}.{connection.to_port}")
    
    async def run(self):
        """
        Start all components and run the harness
        
        Raises:
            HarnessAlreadyRunningError: If harness is already running
            ComponentStartupError: If component startup fails
        """
        if self.running:
            raise HarnessAlreadyRunningError("Harness is already running")
        
        self.logger.info(f"🚀 Starting SystemExecutionHarness with {len(self.components)} components")
        
        try:
            self.state = HarnessState.STARTING
            self.start_time = time.time()
            self.running = True
            
            # Create harness context for components
            context = HarnessContext(
                harness_id=self.harness_id,
                component_registry={name: reg.component for name, reg in self.components.items()},
                global_config={
                    "harness_config": self.config,
                    "stream_manager": self.stream_manager,
                    "start_time": self.start_time
                }
            )
            
            async with anyio.create_task_group() as tg:
                self.task_group = tg
                
                # Setup all components first
                await self._setup_all_components(context)
                
                # Start components in dependency order
                await self._start_components_ordered()
                
                # Start monitoring if enabled
                if self.config.enable_health_monitoring:
                    tg.start_soon(self._health_monitoring_loop)
                
                # Update state
                self.state = HarnessState.RUNNING
                startup_time = time.time() - self.start_time
                self.performance_metrics["total_startup_time"] = startup_time
                
                self.logger.info(f"✅ SystemExecutionHarness started successfully in {startup_time:.3f}s")
                
                # Wait for shutdown signal or error
                await self._run_until_stopped()
                
        except Exception as e:
            self.state = HarnessState.ERROR
            self.runtime_errors.append(f"Harness execution error: {e}")
            self.logger.error(f"❌ Harness execution failed: {e}")
            raise ComponentStartupError(f"Harness execution failed: {e}") from e
        finally:
            await self._cleanup_execution()
    
    async def _setup_all_components(self, context: HarnessContext):
        """Setup all registered components concurrently"""
        self.logger.info(f"🔧 Setting up {len(self.components)} components")
        
        setup_tasks = []
        for name, registration in self.components.items():
            setup_tasks.append(
                asyncio.create_task(
                    self._setup_component_with_timeout(name, registration.component, context),
                    name=f"setup_{name}"
                )
            )
        
        # Wait for all setups to complete
        setup_results = await asyncio.gather(*setup_tasks, return_exceptions=True)
        
        # Check for setup failures
        failed_setups = []
        for i, result in enumerate(setup_results):
            if isinstance(result, Exception):
                component_name = list(self.components.keys())[i]
                failed_setups.append(f"{component_name}: {result}")
                self.failed_components.add(component_name)
        
        if failed_setups:
            error_msg = f"Component setup failures: {failed_setups}"
            self.startup_errors.append(error_msg)
            raise ComponentStartupError(error_msg)
        
        self.logger.info("✅ All components setup completed successfully")
    
    async def _setup_component_with_timeout(self, name: str, component: HarnessComponent, context: HarnessContext):
        """Setup a single component with timeout"""
        try:
            with anyio.fail_after(self.config.startup_timeout):
                await component.setup(context)
            self.logger.debug(f"✅ Component '{name}' setup completed")
        except Exception as e:
            self.logger.error(f"❌ Component '{name}' setup failed: {e}")
            raise ComponentStartupError(f"Setup failed for component '{name}': {e}") from e
    
    async def _start_components_ordered(self):
        """Start components in dependency order with priorities"""
        self.logger.info("🚀 Starting components in dependency order")
        
        # Calculate startup order considering dependencies and priorities
        startup_order = self._calculate_startup_order()
        
        startup_times = []
        for name in startup_order:
            if name in self.failed_components:
                continue
                
            registration = self.components[name]
            component = registration.component
            
            try:
                # Start component with timeout
                start_time = time.time()
                
                with anyio.fail_after(self.config.startup_timeout):
                    await component.start_processing()
                
                startup_time = time.time() - start_time
                startup_times.append(startup_time)
                
                self.logger.info(f"✅ Component '{name}' started in {startup_time:.3f}s")
                
                # Small delay between component starts
                await asyncio.sleep(self.config.component_startup_delay)
                
            except Exception as e:
                self.failed_components.add(name)
                error_msg = f"Failed to start component '{name}': {e}"
                self.startup_errors.append(error_msg)
                self.logger.error(f"❌ {error_msg}")
                raise ComponentStartupError(error_msg) from e
        
        # Update performance metrics
        if startup_times:
            self.performance_metrics["average_component_startup_time"] = sum(startup_times) / len(startup_times)
        
        self.logger.info(f"✅ All {len(startup_order)} components started successfully")
    
    def _calculate_startup_order(self) -> List[str]:
        """Calculate the order to start components based on dependencies and priorities"""
        # Topological sort with priority consideration
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(name: str):
            if name in temp_visited:
                raise HarnessConfigurationError(f"Circular dependency detected involving component '{name}'")
            
            if name not in visited:
                temp_visited.add(name)
                
                # Visit dependencies first
                registration = self.components[name]
                for dependency in registration.dependencies:
                    if dependency in self.components:
                        visit(dependency)
                
                temp_visited.remove(name)
                visited.add(name)
                order.append(name)
        
        # Sort components by priority (lower priority = start first)
        component_names = sorted(
            self.components.keys(),
            key=lambda name: self.components[name].start_priority
        )
        
        # Visit all components
        for name in component_names:
            if name not in visited:
                visit(name)
        
        return order
    
    async def _run_until_stopped(self):
        """Run until stop is requested or error occurs"""
        try:
            # Create component processing tasks
            for name, registration in self.components.items():
                if name not in self.failed_components:
                    task = asyncio.create_task(
                        self._monitor_component_processing(name, registration.component),
                        name=f"process_{name}"
                    )
                    self.component_tasks[name] = task
            
            # Wait for stop signal or all tasks to complete
            if self.component_tasks:
                await asyncio.gather(*self.component_tasks.values(), return_exceptions=True)
            
        except Exception as e:
            self.runtime_errors.append(f"Runtime error: {e}")
            self.logger.error(f"❌ Runtime error: {e}")
            raise
    
    async def _monitor_component_processing(self, name: str, component: HarnessComponent):
        """Monitor a component's processing with error handling"""
        try:
            # Component is already started, just wait for completion
            while component.is_running and self.running:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.failed_components.add(name)
            self.runtime_errors.append(f"Component '{name}' processing error: {e}")
            self.logger.error(f"❌ Component '{name}' processing failed: {e}")
            # Don't re-raise to prevent stopping other components
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop"""
        self.logger.debug("🏥 Starting health monitoring loop")
        
        while self.running and self.state == HarnessState.RUNNING:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                self.logger.warning(f"⚠️ Health monitoring error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _perform_health_check(self):
        """Perform health check on all components and streams"""
        current_time = time.time()
        
        # Skip if too recent
        if current_time - self.last_health_check < self.config.health_check_interval:
            return
        
        self.logger.debug("🏥 Performing system health check")
        
        # Check component health
        healthy_components = 0
        for name, registration in self.components.items():
            try:
                health = await registration.component.health_check()
                self.component_health_status[name] = health
                
                if health.get("healthy", False):
                    healthy_components += 1
                else:
                    self.logger.warning(f"⚠️ Component '{name}' reports unhealthy: {health}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Health check failed for component '{name}': {e}")
                self.component_health_status[name] = {"healthy": False, "error": str(e)}
        
        # Check stream health
        stream_health = await self.stream_manager.health_check_streams()
        
        self.last_health_check = current_time
        
        # Log summary
        total_components = len(self.components)
        component_health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 100
        
        if component_health_percentage < 100 or stream_health.get("unhealthy_streams", 0) > 0:
            self.logger.warning(
                f"⚠️ Health check: {healthy_components}/{total_components} components healthy ({component_health_percentage:.1f}%), "
                f"{stream_health.get('unhealthy_streams', 0)} unhealthy streams"
            )
        else:
            self.logger.debug(f"✅ Health check: All systems healthy")
    
    async def stop(self):
        """
        Gracefully stop the harness and all components
        """
        if not self.running:
            self.logger.info("ℹ️ Harness is not running")
            return
        
        self.logger.info("🛑 Stopping SystemExecutionHarness")
        self.state = HarnessState.STOPPING
        self.stop_time = time.time()
        self.running = False
        
        try:
            # Stop all components gracefully
            await self._stop_all_components()
            
            # Cancel monitoring tasks
            if self.health_check_task and not self.health_check_task.done():
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel component processing tasks
            for name, task in self.component_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.state = HarnessState.STOPPED
            stop_duration = time.time() - self.stop_time
            
            self.logger.info(f"✅ SystemExecutionHarness stopped successfully in {stop_duration:.3f}s")
            
        except Exception as e:
            self.state = HarnessState.ERROR
            self.logger.error(f"❌ Error during harness stop: {e}")
            raise
    
    async def _stop_all_components(self):
        """Stop all components in reverse dependency order"""
        self.logger.info("🛑 Stopping all components")
        
        # Calculate stop order (reverse of start order)
        stop_order = list(reversed(self._calculate_startup_order()))
        
        # Stop components with timeout
        for name in stop_order:
            if name not in self.failed_components:
                registration = self.components[name]
                component = registration.component
                
                try:
                    with anyio.fail_after(self.config.shutdown_timeout):
                        await component.stop_processing()
                    
                    self.logger.debug(f"✅ Component '{name}' stopped")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error stopping component '{name}': {e}")
    
    async def _cleanup_execution(self):
        """Clean up execution resources"""
        self.logger.info("🧹 Cleaning up harness resources")
        
        try:
            # Cleanup all components
            cleanup_tasks = []
            for name, registration in self.components.items():
                cleanup_tasks.append(
                    asyncio.create_task(
                        self._cleanup_component_with_timeout(name, registration.component),
                        name=f"cleanup_{name}"
                    )
                )
            
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            # Close all streams
            await self.stream_manager.close_all_streams()
            
            # Clear task references
            self.component_tasks.clear()
            self.task_group = None
            
            self.logger.info("✅ Harness cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
    
    async def _cleanup_component_with_timeout(self, name: str, component: HarnessComponent):
        """Cleanup a single component with timeout"""
        try:
            with anyio.fail_after(self.config.shutdown_timeout):
                await component.cleanup()
            self.logger.debug(f"✅ Component '{name}' cleanup completed")
        except Exception as e:
            self.logger.warning(f"⚠️ Component '{name}' cleanup failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive harness status"""
        current_time = time.time()
        
        return {
            "harness_id": self.harness_id,
            "state": self.state.value,
            "running": self.running,
            "uptime_seconds": current_time - (self.start_time or current_time),
            "components": {
                "total": len(self.components),
                "healthy": len([name for name, health in self.component_health_status.items() 
                              if health.get("healthy", False)]),
                "failed": len(self.failed_components),
                "failed_list": list(self.failed_components)
            },
            "streams": {
                "total_connections": len(self.stream_connections),
                "stream_statistics": self.stream_manager.get_stream_statistics()
            },
            "performance": self.performance_metrics,
            "errors": {
                "startup_errors": len(self.startup_errors),
                "runtime_errors": len(self.runtime_errors),
                "recent_startup_errors": self.startup_errors[-5:],
                "recent_runtime_errors": self.runtime_errors[-5:]
            },
            "last_health_check": self.last_health_check,
            "configuration": {
                "startup_timeout": self.config.startup_timeout,
                "shutdown_timeout": self.config.shutdown_timeout,
                "health_check_interval": self.config.health_check_interval,
                "stream_buffer_size": self.config.stream_buffer_size
            }
        }
    
    def get_component_info(self, name: str) -> Dict[str, Any]:
        """Get detailed information about a specific component"""
        if name not in self.components:
            raise ComponentNotFoundError(f"Component '{name}' not found")
        
        registration = self.components[name]
        component = registration.component
        
        return {
            "name": name,
            "registration": {
                "registration_time": registration.registration_time,
                "start_priority": registration.start_priority,
                "dependencies": registration.dependencies,
                "required_for": registration.required_for
            },
            "component_info": component.get_component_info(),
            "health_status": self.component_health_status.get(name, {}),
            "stream_info": component.get_stream_info(),
            "performance_metrics": component.get_performance_metrics(),
            "is_failed": name in self.failed_components,
            "has_processing_task": name in self.component_tasks
        }
    
    def list_components(self) -> List[str]:
        """Get list of all registered component names"""
        return list(self.components.keys())
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """Get list of all stream connections"""
        return [
            {
                "id": conn.id,
                "from": f"{conn.from_component}.{conn.from_port}",
                "to": f"{conn.to_component}.{conn.to_port}",
                "buffer_size": conn.buffer_size,
                "created_at": conn.created_at
            }
            for conn in self.stream_connections.values()
        ]


# Export main classes
__all__ = [
    'SystemExecutionHarness',
    'HarnessConfiguration',
    'HarnessState',
    'ComponentRegistration',
    'StreamConnection',
    'ComponentAlreadyRegisteredError',
    'ComponentNotFoundError', 
    'HarnessAlreadyRunningError',
    'HarnessConfigurationError',
    'ComponentStartupError'
]