#!/usr/bin/env python3
"""
HarnessComponent: Base class for all harness-compatible components
================================================================

Provides the foundational HarnessComponent class that all V5.0 components inherit from,
with integrated stream management, lifecycle control, and status tracking.

Key Features:
- Inherits from EnhancedBaseComponent for V5.0 compatibility
- AnyIO MemoryObjectStream management for communication
- Integrated ComponentStatus for lifecycle management
- Graceful shutdown and resource cleanup
- Error handling and recovery mechanisms
- Performance monitoring and metrics
"""

import asyncio
import anyio
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
from anyio.abc import TaskGroup
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from abc import abstractmethod
import uuid
import json
from dataclasses import dataclass, field

# Import the existing enhanced base component
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import (
    EnhancedBaseComponent, 
    ComponentConfiguration,
    ComponentValidationError,
    ComponentInitializationError,
    ComponentOperationError
)

from .component_status import ComponentStatus, ComponentState, InvalidStateTransitionError


@dataclass
class StreamConnection:
    """Represents a stream connection with metadata"""
    name: str
    stream_type: str  # 'send' or 'receive'
    stream: Union[MemoryObjectSendStream, MemoryObjectReceiveStream]
    connected_component: Optional[str] = None
    message_count: int = 0
    last_activity: float = field(default_factory=time.time)
    buffer_size: int = 100
    
    def record_activity(self):
        """Record stream activity"""
        self.message_count += 1
        self.last_activity = time.time()


@dataclass
class HarnessContext:
    """Context information provided by the harness"""
    harness_id: str
    component_registry: Dict[str, 'HarnessComponent']
    global_config: Dict[str, Any]
    stream_manager: Any = None
    task_group: Optional[TaskGroup] = None


class StreamOperationError(Exception):
    """Raised when stream operations fail"""
    pass


class HarnessComponent(EnhancedBaseComponent):
    """
    Base class for all harness-compatible components
    
    Provides:
    - Stream-based communication via AnyIO MemoryObjectStreams
    - Integrated lifecycle management with ComponentStatus
    - Graceful shutdown and resource cleanup
    - Error handling and recovery mechanisms
    - Performance monitoring and metrics collection
    """
    
    def __init__(self, config: ComponentConfiguration):
        super().__init__(config)
        
        # Stream management
        self.receive_streams: Dict[str, StreamConnection] = {}
        self.send_streams: Dict[str, StreamConnection] = {}
        
        # Component status integration
        self._status = ComponentStatus(self.name)
        
        # Harness integration
        self.harness_context: Optional[HarnessContext] = None
        
        # Processing control
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._processing_active = False
        
        # Performance metrics
        self.start_time: Optional[float] = None
        self.message_processing_times: List[float] = []
        self.last_heartbeat: float = time.time()
        
        # Error handling
        self.max_consecutive_errors = 5
        self.consecutive_errors = 0
        self.retry_delays = [0.1, 0.5, 1.0, 2.0, 5.0]  # Exponential backoff
        
        self.logger.info(f"🔧 HarnessComponent '{self.name}' initialized with service_type='{self.service_type}'")
    
    @property
    def status(self) -> ComponentStatus:
        """Get component status manager"""
        return self._status
    
    @property
    def current_state(self) -> ComponentState:
        """Get current component state"""
        return self._status.state
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return self._status.is_healthy
    
    @property
    def is_running(self) -> bool:
        """Check if component is running"""
        return self._status.is_running
    
    async def setup(self, harness_context: Optional[HarnessContext] = None) -> None:
        """
        Initialize component resources and prepare for operation
        
        Args:
            harness_context: Context information from the harness
        """
        try:
            self.logger.info(f"🚀 Setting up HarnessComponent '{self.name}'")
            
            # Store harness context
            self.harness_context = harness_context
            
            # Call parent setup
            await super().safe_operation("parent_setup", super().initialize)
            
            # Initialize component-specific resources
            await self._initialize_component_resources()
            
            # Transition to ready state
            await self._status.transition_to(ComponentState.READY, {
                "setup_time": time.time(),
                "harness_context_available": harness_context is not None
            })
            
            self.logger.info(f"✅ HarnessComponent '{self.name}' setup complete")
            
        except Exception as e:
            await self._status.record_error(e, {"phase": "setup"})
            self.logger.error(f"❌ Setup failed for component '{self.name}': {e}")
            raise ComponentInitializationError(f"Setup failed: {e}") from e
    
    async def _initialize_component_resources(self):
        """Initialize component-specific resources - override in subclasses"""
        # Default implementation - subclasses can override
        pass
    
    def add_receive_stream(self, name: str, stream: MemoryObjectReceiveStream, 
                          connected_component: Optional[str] = None, buffer_size: int = 100):
        """
        Add a receive stream for incoming messages
        
        Args:
            name: Stream identifier
            stream: AnyIO receive stream
            connected_component: Name of connected component (optional)
            buffer_size: Stream buffer size
        """
        if name in self.receive_streams:
            raise StreamOperationError(f"Receive stream '{name}' already exists")
        
        connection = StreamConnection(
            name=name,
            stream_type="receive",
            stream=stream,
            connected_component=connected_component,
            buffer_size=buffer_size
        )
        
        self.receive_streams[name] = connection
        self.logger.info(f"📥 Added receive stream '{name}' to component '{self.name}'")
    
    def add_send_stream(self, name: str, stream: MemoryObjectSendStream,
                       connected_component: Optional[str] = None, buffer_size: int = 100):
        """
        Add a send stream for outgoing messages
        
        Args:
            name: Stream identifier  
            stream: AnyIO send stream
            connected_component: Name of connected component (optional)
            buffer_size: Stream buffer size
        """
        if name in self.send_streams:
            raise StreamOperationError(f"Send stream '{name}' already exists")
        
        connection = StreamConnection(
            name=name,
            stream_type="send", 
            stream=stream,
            connected_component=connected_component,
            buffer_size=buffer_size
        )
        
        self.send_streams[name] = connection
        self.logger.info(f"📤 Added send stream '{name}' to component '{self.name}'")
    
    async def send_message(self, stream_name: str, message: Any, timeout: float = 5.0) -> bool:
        """
        Send message through specified stream
        
        Args:
            stream_name: Name of the send stream
            message: Message to send
            timeout: Send timeout in seconds
            
        Returns:
            bool: True if message was sent successfully
        """
        if stream_name not in self.send_streams:
            raise StreamOperationError(f"Send stream '{stream_name}' not found")
        
        connection = self.send_streams[stream_name]
        
        try:
            # Add message metadata
            enhanced_message = {
                "id": str(uuid.uuid4()),
                "sender": self.name,
                "timestamp": time.time(),
                "stream": stream_name,
                "data": message
            }
            
            # Send with timeout
            with anyio.fail_after(timeout):
                await connection.stream.send(enhanced_message)
            
            # Record activity
            connection.record_activity()
            self._status.metrics.record_message_sent()
            
            self.logger.debug(f"📤 Message sent via '{stream_name}' from '{self.name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send message via '{stream_name}': {e}")
            await self._status.record_error(e, {"operation": "send_message", "stream": stream_name})
            return False
    
    async def receive_message(self, stream_name: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Receive message from specified stream
        
        Args:
            stream_name: Name of the receive stream
            timeout: Receive timeout in seconds (None for no timeout)
            
        Returns:
            Message data if received, None if timeout or error
        """
        if stream_name not in self.receive_streams:
            raise StreamOperationError(f"Receive stream '{stream_name}' not found")
        
        connection = self.receive_streams[stream_name]
        
        try:
            # Receive with optional timeout
            if timeout:
                with anyio.fail_after(timeout):
                    message = await connection.stream.receive()
            else:
                message = await connection.stream.receive()
            
            # Record activity
            connection.record_activity()
            
            # Extract data from enhanced message
            if isinstance(message, dict) and "data" in message:
                data = message["data"]
                self.logger.debug(f"📥 Message received via '{stream_name}' at '{self.name}' from '{message.get('sender', 'unknown')}'")
            else:
                data = message
                self.logger.debug(f"📥 Raw message received via '{stream_name}' at '{self.name}'")
            
            return data
            
        except anyio.EndOfStream:
            self.logger.info(f"📥 Stream '{stream_name}' closed")
            return None
        except Exception as e:
            self.logger.error(f"❌ Failed to receive message via '{stream_name}': {e}")
            await self._status.record_error(e, {"operation": "receive_message", "stream": stream_name})
            return None
    
    async def start_processing(self) -> None:
        """Start the component's main processing loop"""
        if self._processing_active:
            self.logger.warning(f"⚠️ Processing already active for component '{self.name}'")
            return
        
        try:
            # Transition to running state
            await self._status.transition_to(ComponentState.RUNNING, {
                "start_time": time.time(),
                "processing_mode": "active"
            })
            
            self._processing_active = True
            self.start_time = time.time()
            
            # Start processing task
            self._processing_task = asyncio.create_task(self._main_processing_loop())
            
            self.logger.info(f"🏃 Started processing for component '{self.name}'")
            
        except Exception as e:
            await self._status.record_error(e, {"phase": "start_processing"})
            raise ComponentOperationError(f"Failed to start processing: {e}") from e
    
    async def _main_processing_loop(self):
        """Main processing loop - calls process() method with error handling"""
        while self._processing_active and not self._shutdown_event.is_set():
            try:
                # Reset consecutive error count on successful processing
                self.consecutive_errors = 0
                
                # Call the component's process method
                processing_start = time.time()
                await self.process()
                processing_time = time.time() - processing_start
                
                # Record processing metrics
                self.message_processing_times.append(processing_time)
                if len(self.message_processing_times) > 1000:  # Keep last 1000 measurements
                    self.message_processing_times = self.message_processing_times[-1000:]
                
                self._status.metrics.record_message_processed(processing_time)
                
                # Update heartbeat
                self.last_heartbeat = time.time()
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.001)
                
            except asyncio.CancelledError:
                self.logger.info(f"🛑 Processing cancelled for component '{self.name}'")
                break
            except Exception as e:
                self.consecutive_errors += 1
                await self._status.record_error(e, {
                    "phase": "processing_loop",
                    "consecutive_errors": self.consecutive_errors
                })
                
                # Apply exponential backoff for retries
                if self.consecutive_errors < len(self.retry_delays):
                    delay = self.retry_delays[self.consecutive_errors - 1]
                    self.logger.warning(f"⚠️ Processing error #{self.consecutive_errors} in '{self.name}', retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"❌ Max consecutive errors ({self.max_consecutive_errors}) reached in '{self.name}', stopping processing")
                    break
        
        self._processing_active = False
        self.logger.info(f"🏁 Processing loop ended for component '{self.name}'")
    
    @abstractmethod
    async def process(self) -> None:
        """
        Core processing logic - must be implemented by subclasses
        
        This method is called repeatedly in the main processing loop.
        It should handle receiving messages, processing them, and sending results.
        """
        raise NotImplementedError("Subclasses must implement process() method")
    
    async def stop_processing(self) -> None:
        """Stop the component's processing gracefully"""
        if not self._processing_active:
            self.logger.info(f"ℹ️ Processing not active for component '{self.name}'")
            return
        
        try:
            self.logger.info(f"🛑 Stopping processing for component '{self.name}'")
            
            # Signal shutdown
            self._shutdown_event.set()
            self._processing_active = False
            
            # Wait for processing task to complete
            if self._processing_task and not self._processing_task.done():
                try:
                    await asyncio.wait_for(self._processing_task, timeout=5.0)
                except asyncio.TimeoutError:
                    self.logger.warning(f"⚠️ Processing task did not complete within timeout, cancelling")
                    self._processing_task.cancel()
                    try:
                        await self._processing_task
                    except asyncio.CancelledError:
                        pass
            
            # Transition to stopping state
            await self._status.transition_to(ComponentState.STOPPING, {
                "stop_time": time.time(),
                "processing_duration": time.time() - (self.start_time or time.time())
            })
            
            self.logger.info(f"✅ Processing stopped for component '{self.name}'")
            
        except Exception as e:
            await self._status.record_error(e, {"phase": "stop_processing"})
            raise ComponentOperationError(f"Failed to stop processing: {e}") from e
    
    async def cleanup(self) -> None:
        """Clean up component resources"""
        try:
            self.logger.info(f"🧹 Cleaning up component '{self.name}'")
            
            # Stop processing if still active
            if self._processing_active:
                await self.stop_processing()
            
            # Close all send streams
            for name, connection in self.send_streams.items():
                try:
                    await connection.stream.aclose()
                    self.logger.debug(f"🔒 Closed send stream '{name}'")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error closing send stream '{name}': {e}")
            
            # Close all receive streams  
            for name, connection in self.receive_streams.items():
                try:
                    await connection.stream.aclose()
                    self.logger.debug(f"🔒 Closed receive stream '{name}'")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error closing receive stream '{name}': {e}")
            
            # Clear stream collections
            self.send_streams.clear()
            self.receive_streams.clear()
            
            # Component-specific cleanup
            await self._cleanup_component_resources()
            
            # Transition to stopped state
            await self._status.transition_to(ComponentState.STOPPED, {
                "cleanup_time": time.time(),
                "total_uptime": time.time() - (self.start_time or time.time())
            })
            
            self.logger.info(f"✅ Cleanup complete for component '{self.name}'")
            
        except Exception as e:
            await self._status.record_error(e, {"phase": "cleanup"})
            self.logger.error(f"❌ Cleanup failed for component '{self.name}': {e}")
            raise ComponentOperationError(f"Cleanup failed: {e}") from e
    
    async def _cleanup_component_resources(self):
        """Clean up component-specific resources - override in subclasses"""
        # Default implementation - subclasses can override
        pass
    
    # Required abstract methods from EnhancedBaseComponent
    async def initialize(self) -> None:
        """Initialize component (called by setup)"""
        pass
    
    async def start(self) -> None:
        """Start component (wrapper for start_processing)"""
        await self.start_processing()
    
    async def stop(self) -> None:
        """Stop component (wrapper for stop_processing)"""
        await self.stop_processing()
    
    async def health_check(self) -> Dict[str, Any]:
        """Return component health status"""
        return {
            "component": self.name,
            "healthy": self.is_healthy,
            "state": self.current_state.value,
            "processing_active": self._processing_active,
            "stream_connections": {
                "send_streams": len(self.send_streams),
                "receive_streams": len(self.receive_streams)
            },
            "performance": {
                "uptime_seconds": self._status.uptime,
                "messages_processed": self._status.metrics.total_messages_processed,
                "messages_sent": self._status.metrics.total_messages_sent,
                "average_processing_time": self._status.metrics.average_processing_time,
                "consecutive_errors": self.consecutive_errors,
                "last_heartbeat": self.last_heartbeat
            }
        }
    
    async def validate_configuration(self) -> bool:
        """Validate component configuration"""
        try:
            # Basic validation
            if not self.name:
                return False
            
            if not self.service_type:
                return False
            
            # Component-specific validation can be overridden
            return await self._validate_component_configuration()
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    async def _validate_component_configuration(self) -> bool:
        """Component-specific configuration validation - override in subclasses"""
        return True
    
    def get_stream_info(self) -> Dict[str, Any]:
        """Get information about all streams"""
        return {
            "send_streams": {
                name: {
                    "connected_to": conn.connected_component,
                    "message_count": conn.message_count,
                    "last_activity": conn.last_activity,
                    "buffer_size": conn.buffer_size
                }
                for name, conn in self.send_streams.items()
            },
            "receive_streams": {
                name: {
                    "connected_from": conn.connected_component,
                    "message_count": conn.message_count,
                    "last_activity": conn.last_activity,
                    "buffer_size": conn.buffer_size
                }
                for name, conn in self.receive_streams.items()
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        processing_times = self.message_processing_times[-100:]  # Last 100 measurements
        
        return {
            "component": self.name,
            "uptime_seconds": self._status.uptime,
            "processing_metrics": {
                "total_processed": self._status.metrics.total_messages_processed,
                "total_sent": self._status.metrics.total_messages_sent,
                "total_errors": self._status.metrics.total_errors,
                "average_processing_time": self._status.metrics.average_processing_time,
                "recent_processing_times": processing_times,
                "min_processing_time": min(processing_times) if processing_times else 0,
                "max_processing_time": max(processing_times) if processing_times else 0
            },
            "error_metrics": {
                "error_count": self._status.error_count,
                "consecutive_errors": self.consecutive_errors,
                "error_rate": self._status.metrics.total_errors / max(1, self._status.metrics.total_messages_processed),
                "recovery_attempts": self._status.recovery_attempts
            },
            "stream_metrics": {
                "total_streams": len(self.send_streams) + len(self.receive_streams),
                "send_streams": len(self.send_streams),
                "receive_streams": len(self.receive_streams),
                "total_stream_messages": sum(conn.message_count for conn in self.send_streams.values()) +
                                        sum(conn.message_count for conn in self.receive_streams.values())
            }
        }


# Export main classes
__all__ = [
    'HarnessComponent',
    'StreamConnection', 
    'HarnessContext',
    'StreamOperationError'
]