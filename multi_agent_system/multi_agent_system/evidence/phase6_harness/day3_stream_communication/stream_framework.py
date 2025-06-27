#!/usr/bin/env python3
"""
StreamFramework: High-level stream abstraction for component communication
========================================================================

Provides a comprehensive high-level abstraction over AnyIO streams with
advanced messaging capabilities, error handling, and performance optimization.

Key Features:
- High-level abstraction over AnyIO MemoryObjectStreams
- Message sending/receiving with automatic serialization
- Broadcast and multicast capabilities
- Message routing and filtering
- Error handling and recovery mechanisms
- Performance monitoring and optimization
- Flow control and backpressure management
"""

import asyncio
import anyio
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
import time
import logging
from typing import Dict, List, Any, Optional, Set, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, deque

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase6_harness.day3_stream_communication.message_protocol import (
    MessageProtocol, Message, MessageType, MessageMetadata
)


class StreamState(Enum):
    """States of a stream connection"""
    CREATED = "created"
    CONNECTED = "connected"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


class FlowControlMode(Enum):
    """Flow control modes"""
    NONE = "none"
    BACKPRESSURE = "backpressure"
    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"


@dataclass
class StreamMetrics:
    """Metrics for stream performance monitoring"""
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    send_errors: int = 0
    receive_errors: int = 0
    send_times: List[float] = field(default_factory=list)
    receive_times: List[float] = field(default_factory=list)
    queue_depths: List[int] = field(default_factory=list)
    last_activity: float = field(default_factory=time.time)
    
    def record_send(self, message_size: int, send_time: float):
        """Record a successful send operation"""
        self.messages_sent += 1
        self.bytes_sent += message_size
        self.send_times.append(send_time)
        self.last_activity = time.time()
        
        # Keep only recent measurements
        if len(self.send_times) > 1000:
            self.send_times = self.send_times[-1000:]
    
    def record_receive(self, message_size: int, receive_time: float):
        """Record a successful receive operation"""
        self.messages_received += 1
        self.bytes_received += message_size
        self.receive_times.append(receive_time)
        self.last_activity = time.time()
        
        # Keep only recent measurements
        if len(self.receive_times) > 1000:
            self.receive_times = self.receive_times[-1000:]
    
    def record_queue_depth(self, depth: int):
        """Record queue depth for monitoring"""
        self.queue_depths.append(depth)
        if len(self.queue_depths) > 100:
            self.queue_depths = self.queue_depths[-100:]
    
    @property
    def average_send_time(self) -> float:
        """Get average send time in seconds"""
        return sum(self.send_times) / len(self.send_times) if self.send_times else 0.0
    
    @property
    def average_receive_time(self) -> float:
        """Get average receive time in seconds"""
        return sum(self.receive_times) / len(self.receive_times) if self.receive_times else 0.0
    
    @property
    def average_queue_depth(self) -> float:
        """Get average queue depth"""
        return sum(self.queue_depths) / len(self.queue_depths) if self.queue_depths else 0.0
    
    @property
    def throughput_messages_per_second(self) -> float:
        """Calculate throughput in messages per second"""
        if not self.send_times and not self.receive_times:
            return 0.0
        
        all_times = self.send_times + self.receive_times
        if len(all_times) < 2:
            return 0.0
        
        duration = max(all_times) - min(all_times)
        total_messages = self.messages_sent + self.messages_received
        
        return total_messages / duration if duration > 0 else 0.0


@dataclass
class StreamEndpoint:
    """Represents one end of a stream connection"""
    name: str
    component: str
    stream_type: str  # 'send' or 'receive'
    stream: Union[MemoryObjectSendStream, MemoryObjectReceiveStream]
    state: StreamState = StreamState.CREATED
    metrics: StreamMetrics = field(default_factory=StreamMetrics)
    filters: List[Callable[[Message], bool]] = field(default_factory=list)
    flow_control: FlowControlMode = FlowControlMode.BACKPRESSURE
    max_queue_size: int = 1000


class StreamOperationError(Exception):
    """Raised when stream operations fail"""
    pass


class StreamClosedError(StreamOperationError):
    """Raised when attempting to use a closed stream"""
    pass


class FlowControlError(StreamOperationError):
    """Raised when flow control limits are exceeded"""
    pass


class MessageFilterError(Exception):
    """Raised when message filtering fails"""
    pass


class StreamFramework:
    """
    High-level stream abstraction for component communication
    
    Provides:
    - Message sending/receiving with automatic serialization
    - Broadcast and multicast capabilities
    - Message routing and filtering
    - Error handling and recovery
    - Performance monitoring and optimization
    """
    
    def __init__(self, 
                 enable_metrics: bool = True,
                 default_timeout: float = 5.0,
                 max_retries: int = 3,
                 retry_delay: float = 0.1):
        
        self.message_protocol = MessageProtocol()
        self.enable_metrics = enable_metrics
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Stream management
        self.endpoints: Dict[str, StreamEndpoint] = {}
        self.connections: Dict[str, Tuple[str, str]] = {}  # connection_id -> (send_endpoint, receive_endpoint)
        
        # Routing and filtering
        self.message_routes: Dict[str, List[str]] = defaultdict(list)  # source -> [targets]
        self.global_filters: List[Callable[[Message], bool]] = []
        
        # Performance monitoring
        self.total_messages_routed = 0
        self.routing_errors = 0
        self.filter_errors = 0
        
        # Flow control
        self.pending_sends: Dict[str, deque] = defaultdict(deque)
        self.backpressure_events: Dict[str, asyncio.Event] = {}
        
        # Error handling
        self.error_handlers: Dict[str, Callable[[Exception, str], None]] = {}
        self.failed_endpoints: Set[str] = set()
        
        # Logging
        self.logger = logging.getLogger("StreamFramework")
        self.logger.info(f"✨ StreamFramework initialized (metrics: {enable_metrics}, timeout: {default_timeout}s)")
    
    def register_endpoint(self, 
                         name: str,
                         component: str,
                         stream: Union[MemoryObjectSendStream, MemoryObjectReceiveStream],
                         flow_control: FlowControlMode = FlowControlMode.BACKPRESSURE,
                         max_queue_size: int = 1000) -> str:
        """
        Register a stream endpoint
        
        Args:
            name: Unique name for the endpoint
            component: Component that owns this endpoint
            stream: AnyIO stream object
            flow_control: Flow control mode
            max_queue_size: Maximum queue size for flow control
            
        Returns:
            Endpoint ID for reference
        """
        if name in self.endpoints:
            raise StreamOperationError(f"Endpoint '{name}' already registered")
        
        # Determine stream type
        stream_type = "send" if isinstance(stream, MemoryObjectSendStream) else "receive"
        
        endpoint = StreamEndpoint(
            name=name,
            component=component,
            stream_type=stream_type,
            stream=stream,
            flow_control=flow_control,
            max_queue_size=max_queue_size
        )
        
        endpoint.state = StreamState.CONNECTED
        self.endpoints[name] = endpoint
        
        # Initialize flow control
        if flow_control != FlowControlMode.NONE:
            self.backpressure_events[name] = asyncio.Event()
            self.backpressure_events[name].set()  # Start ready
        
        self.logger.info(f"📍 Registered {stream_type} endpoint '{name}' for component '{component}'")
        return name
    
    def unregister_endpoint(self, name: str):
        """Unregister a stream endpoint"""
        if name not in self.endpoints:
            raise StreamOperationError(f"Endpoint '{name}' not found")
        
        endpoint = self.endpoints[name]
        endpoint.state = StreamState.CLOSING
        
        # Clean up flow control
        if name in self.backpressure_events:
            del self.backpressure_events[name]
        
        if name in self.pending_sends:
            del self.pending_sends[name]
        
        # Remove from routes
        self.message_routes = {k: [ep for ep in v if ep != name] 
                              for k, v in self.message_routes.items()}
        
        # Mark as closed
        endpoint.state = StreamState.CLOSED
        del self.endpoints[name]
        
        self.logger.info(f"📍 Unregistered endpoint '{name}'")
    
    def create_route(self, source: str, targets: List[str]):
        """
        Create a message route from source to multiple targets
        
        Args:
            source: Source endpoint name
            targets: List of target endpoint names
        """
        if source not in self.endpoints:
            raise StreamOperationError(f"Source endpoint '{source}' not found")
        
        for target in targets:
            if target not in self.endpoints:
                raise StreamOperationError(f"Target endpoint '{target}' not found")
        
        self.message_routes[source] = targets
        self.logger.info(f"🛤️ Created route: {source} → {targets}")
    
    def add_filter(self, endpoint: str, filter_func: Callable[[Message], bool]):
        """
        Add a message filter to an endpoint
        
        Args:
            endpoint: Endpoint name
            filter_func: Function that returns True if message should be processed
        """
        if endpoint not in self.endpoints:
            raise StreamOperationError(f"Endpoint '{endpoint}' not found")
        
        self.endpoints[endpoint].filters.append(filter_func)
        self.logger.info(f"🔍 Added filter to endpoint '{endpoint}'")
    
    def add_global_filter(self, filter_func: Callable[[Message], bool]):
        """Add a global message filter"""
        self.global_filters.append(filter_func)
        self.logger.info("🔍 Added global message filter")
    
    async def send_message(self, 
                          endpoint: str,
                          payload: Any,
                          message_type: MessageType = MessageType.DATA,
                          recipient: Optional[str] = None,
                          timeout: Optional[float] = None,
                          priority: int = 0) -> bool:
        """
        Send message through specified endpoint
        
        Args:
            endpoint: Endpoint name
            payload: Message payload
            message_type: Type of message
            recipient: Recipient component name
            timeout: Send timeout (uses default if None)
            priority: Message priority
            
        Returns:
            True if message was sent successfully
        """
        if endpoint not in self.endpoints:
            raise StreamOperationError(f"Endpoint '{endpoint}' not found")
        
        endpoint_obj = self.endpoints[endpoint]
        
        if endpoint_obj.stream_type != "send":
            raise StreamOperationError(f"Endpoint '{endpoint}' is not a send endpoint")
        
        if endpoint_obj.state != StreamState.CONNECTED:
            raise StreamClosedError(f"Endpoint '{endpoint}' is not connected")
        
        if endpoint in self.failed_endpoints:
            raise StreamOperationError(f"Endpoint '{endpoint}' has failed")
        
        timeout = timeout or self.default_timeout
        
        try:
            # Create message
            message = self.message_protocol.create_message(
                payload=payload,
                message_type=message_type,
                sender=endpoint_obj.component,
                recipient=recipient,
                priority=priority
            )
            
            # Apply filters
            if not await self._apply_filters(message, endpoint):
                self.logger.debug(f"🔍 Message filtered out at endpoint '{endpoint}'")
                return False
            
            # Check flow control
            await self._check_flow_control(endpoint)
            
            # Serialize message
            start_time = time.time()
            serialized = self.message_protocol.serialize(message)
            
            # Send with timeout and retries
            success = await self._send_with_retries(endpoint_obj, serialized, timeout)
            
            if success:
                # Update metrics
                send_time = time.time() - start_time
                if self.enable_metrics:
                    endpoint_obj.metrics.record_send(len(serialized), send_time)
                
                # Handle routing
                await self._route_message(endpoint, message)
                
                self.logger.debug(f"📤 Message sent via '{endpoint}': {message.metadata.id[:8]}")
                return True
            else:
                return False
                
        except Exception as e:
            if self.enable_metrics:
                endpoint_obj.metrics.send_errors += 1
            
            # Handle error
            await self._handle_error(e, endpoint)
            self.logger.error(f"❌ Failed to send message via '{endpoint}': {e}")
            return False
    
    async def receive_message(self, 
                             endpoint: str,
                             timeout: Optional[float] = None) -> Optional[Message]:
        """
        Receive message from specified endpoint
        
        Args:
            endpoint: Endpoint name
            timeout: Receive timeout (uses default if None)
            
        Returns:
            Received Message or None if timeout/error
        """
        if endpoint not in self.endpoints:
            raise StreamOperationError(f"Endpoint '{endpoint}' not found")
        
        endpoint_obj = self.endpoints[endpoint]
        
        if endpoint_obj.stream_type != "receive":
            raise StreamOperationError(f"Endpoint '{endpoint}' is not a receive endpoint")
        
        if endpoint_obj.state != StreamState.CONNECTED:
            raise StreamClosedError(f"Endpoint '{endpoint}' is not connected")
        
        if endpoint in self.failed_endpoints:
            raise StreamOperationError(f"Endpoint '{endpoint}' has failed")
        
        timeout = timeout or self.default_timeout
        
        try:
            start_time = time.time()
            
            # Receive with timeout
            if timeout:
                with anyio.fail_after(timeout):
                    serialized = await endpoint_obj.stream.receive()
            else:
                serialized = await endpoint_obj.stream.receive()
            
            # Deserialize message
            message = self.message_protocol.deserialize(serialized)
            
            # Apply filters
            if not await self._apply_filters(message, endpoint):
                self.logger.debug(f"🔍 Message filtered out at endpoint '{endpoint}'")
                return None
            
            # Update metrics
            receive_time = time.time() - start_time
            if self.enable_metrics:
                endpoint_obj.metrics.record_receive(len(serialized), receive_time)
            
            self.logger.debug(f"📥 Message received via '{endpoint}': {message.metadata.id[:8]}")
            return message
            
        except anyio.EndOfStream:
            self.logger.info(f"📥 Stream '{endpoint}' closed")
            endpoint_obj.state = StreamState.CLOSED
            return None
        except Exception as e:
            if self.enable_metrics:
                endpoint_obj.metrics.receive_errors += 1
            
            await self._handle_error(e, endpoint)
            self.logger.error(f"❌ Failed to receive message via '{endpoint}': {e}")
            return None
    
    async def broadcast_message(self, 
                               endpoints: List[str],
                               payload: Any,
                               message_type: MessageType = MessageType.DATA,
                               timeout: Optional[float] = None) -> List[bool]:
        """
        Broadcast message to multiple endpoints
        
        Args:
            endpoints: List of endpoint names
            payload: Message payload
            message_type: Type of message
            timeout: Send timeout
            
        Returns:
            List of success flags for each endpoint
        """
        self.logger.info(f"📡 Broadcasting message to {len(endpoints)} endpoints")
        
        # Send to all endpoints concurrently
        send_tasks = []
        for endpoint in endpoints:
            if endpoint in self.endpoints and self.endpoints[endpoint].stream_type == "send":
                task = asyncio.create_task(
                    self.send_message(endpoint, payload, message_type, timeout=timeout),
                    name=f"broadcast_{endpoint}"
                )
                send_tasks.append(task)
            else:
                self.logger.warning(f"⚠️ Invalid endpoint for broadcast: '{endpoint}'")
                send_tasks.append(asyncio.create_task(asyncio.coroutine(lambda: False)()))
        
        # Wait for all sends to complete
        results = await asyncio.gather(*send_tasks, return_exceptions=True)
        
        # Convert exceptions to False
        success_flags = []
        for result in results:
            if isinstance(result, Exception):
                success_flags.append(False)
            else:
                success_flags.append(result)
        
        successful = sum(success_flags)
        self.logger.info(f"📡 Broadcast completed: {successful}/{len(endpoints)} successful")
        
        return success_flags
    
    async def _apply_filters(self, message: Message, endpoint: str) -> bool:
        """Apply message filters"""
        try:
            # Apply global filters
            for filter_func in self.global_filters:
                if not filter_func(message):
                    return False
            
            # Apply endpoint-specific filters
            endpoint_obj = self.endpoints[endpoint]
            for filter_func in endpoint_obj.filters:
                if not filter_func(message):
                    return False
            
            return True
            
        except Exception as e:
            self.filter_errors += 1
            self.logger.error(f"❌ Filter error on endpoint '{endpoint}': {e}")
            raise MessageFilterError(f"Filter failed: {e}") from e
    
    async def _check_flow_control(self, endpoint: str):
        """Check and handle flow control"""
        endpoint_obj = self.endpoints[endpoint]
        
        if endpoint_obj.flow_control == FlowControlMode.NONE:
            return
        
        # Check queue size
        pending_count = len(self.pending_sends[endpoint])
        
        if self.enable_metrics:
            endpoint_obj.metrics.record_queue_depth(pending_count)
        
        if pending_count >= endpoint_obj.max_queue_size:
            if endpoint_obj.flow_control == FlowControlMode.BACKPRESSURE:
                # Wait for backpressure to clear
                if endpoint in self.backpressure_events:
                    await self.backpressure_events[endpoint].wait()
            elif endpoint_obj.flow_control == FlowControlMode.DROP_OLDEST:
                # Drop oldest message
                if self.pending_sends[endpoint]:
                    self.pending_sends[endpoint].popleft()
            elif endpoint_obj.flow_control == FlowControlMode.DROP_NEWEST:
                # Don't add new message
                raise FlowControlError(f"Queue full on endpoint '{endpoint}', dropping message")
    
    async def _send_with_retries(self, 
                                endpoint: StreamEndpoint,
                                data: bytes,
                                timeout: float) -> bool:
        """Send with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                with anyio.fail_after(timeout):
                    await endpoint.stream.send(data)
                return True
                
            except Exception as e:
                if attempt < self.max_retries:
                    self.logger.warning(f"⚠️ Send attempt {attempt + 1} failed for '{endpoint.name}', retrying: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    self.logger.error(f"❌ All send attempts failed for '{endpoint.name}': {e}")
                    return False
        
        return False
    
    async def _route_message(self, source: str, message: Message):
        """Handle message routing"""
        if source in self.message_routes:
            targets = self.message_routes[source]
            if targets:
                self.total_messages_routed += 1
                
                # Route to all targets
                route_tasks = []
                for target in targets:
                    if target in self.endpoints and self.endpoints[target].stream_type == "send":
                        task = asyncio.create_task(
                            self.send_message(target, message.payload, message.metadata.type),
                            name=f"route_{source}_{target}"
                        )
                        route_tasks.append(task)
                
                if route_tasks:
                    await asyncio.gather(*route_tasks, return_exceptions=True)
    
    async def _handle_error(self, error: Exception, endpoint: str):
        """Handle endpoint errors"""
        if endpoint in self.error_handlers:
            try:
                self.error_handlers[endpoint](error, endpoint)
            except Exception as e:
                self.logger.error(f"❌ Error handler failed for '{endpoint}': {e}")
        
        # Mark endpoint as failed for severe errors
        if isinstance(error, (StreamClosedError, anyio.EndOfStream)):
            self.failed_endpoints.add(endpoint)
            if endpoint in self.endpoints:
                self.endpoints[endpoint].state = StreamState.ERROR
    
    def set_error_handler(self, endpoint: str, handler: Callable[[Exception, str], None]):
        """Set custom error handler for an endpoint"""
        self.error_handlers[endpoint] = handler
        self.logger.info(f"🔧 Set error handler for endpoint '{endpoint}'")
    
    def get_endpoint_metrics(self, endpoint: str) -> Dict[str, Any]:
        """Get metrics for a specific endpoint"""
        if endpoint not in self.endpoints:
            raise StreamOperationError(f"Endpoint '{endpoint}' not found")
        
        endpoint_obj = self.endpoints[endpoint]
        metrics = endpoint_obj.metrics
        
        return {
            "endpoint": endpoint,
            "component": endpoint_obj.component,
            "type": endpoint_obj.stream_type,
            "state": endpoint_obj.state.value,
            "messages_sent": metrics.messages_sent,
            "messages_received": metrics.messages_received,
            "bytes_sent": metrics.bytes_sent,
            "bytes_received": metrics.bytes_received,
            "send_errors": metrics.send_errors,
            "receive_errors": metrics.receive_errors,
            "average_send_time_ms": metrics.average_send_time * 1000,
            "average_receive_time_ms": metrics.average_receive_time * 1000,
            "average_queue_depth": metrics.average_queue_depth,
            "throughput_msg_per_sec": metrics.throughput_messages_per_second,
            "last_activity": metrics.last_activity
        }
    
    def get_framework_metrics(self) -> Dict[str, Any]:
        """Get overall framework metrics"""
        total_endpoints = len(self.endpoints)
        active_endpoints = len([ep for ep in self.endpoints.values() 
                               if ep.state == StreamState.CONNECTED])
        failed_endpoints = len(self.failed_endpoints)
        
        # Aggregate metrics
        total_messages_sent = sum(ep.metrics.messages_sent for ep in self.endpoints.values())
        total_messages_received = sum(ep.metrics.messages_received for ep in self.endpoints.values())
        total_bytes_sent = sum(ep.metrics.bytes_sent for ep in self.endpoints.values())
        total_bytes_received = sum(ep.metrics.bytes_received for ep in self.endpoints.values())
        
        return {
            "endpoints": {
                "total": total_endpoints,
                "active": active_endpoints,
                "failed": failed_endpoints,
                "health_percentage": (active_endpoints / total_endpoints * 100) if total_endpoints > 0 else 100
            },
            "messages": {
                "total_sent": total_messages_sent,
                "total_received": total_messages_received,
                "total_routed": self.total_messages_routed,
                "routing_errors": self.routing_errors
            },
            "data_transfer": {
                "total_bytes_sent": total_bytes_sent,
                "total_bytes_received": total_bytes_received,
                "total_bytes_transferred": total_bytes_sent + total_bytes_received
            },
            "filtering": {
                "global_filters": len(self.global_filters),
                "filter_errors": self.filter_errors
            },
            "routing": {
                "total_routes": len(self.message_routes),
                "routes": dict(self.message_routes)
            },
            "protocol_metrics": self.message_protocol.get_performance_metrics()
        }
    
    def get_endpoint_list(self) -> List[Dict[str, Any]]:
        """Get list of all endpoints with basic info"""
        return [
            {
                "name": name,
                "component": ep.component,
                "type": ep.stream_type,
                "state": ep.state.value,
                "flow_control": ep.flow_control.value,
                "max_queue_size": ep.max_queue_size,
                "filters": len(ep.filters)
            }
            for name, ep in self.endpoints.items()
        ]


# Export main classes
__all__ = [
    'StreamFramework',
    'StreamEndpoint',
    'StreamMetrics',
    'StreamState',
    'FlowControlMode',
    'StreamOperationError',
    'StreamClosedError',
    'FlowControlError',
    'MessageFilterError'
]