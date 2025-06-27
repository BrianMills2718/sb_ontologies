#!/usr/bin/env python3
"""
StreamManager: AnyIO stream lifecycle and health management
=========================================================

Manages AnyIO MemoryObjectStream creation, monitoring, and cleanup for the
SystemExecutionHarness architecture with comprehensive tracking and statistics.

Key Features:
- Stream creation with buffer size configuration
- Health monitoring and statistics collection
- Resource cleanup and leak prevention
- Performance metrics and monitoring
- Stream lifecycle tracking
"""

import asyncio
import anyio
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
import time
import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field
from collections import defaultdict
import weakref


class StreamInfo(NamedTuple):
    """Information about a managed stream"""
    id: str
    send_stream: MemoryObjectSendStream
    receive_stream: MemoryObjectReceiveStream
    created_at: float
    buffer_size: int
    source_component: Optional[str] = None
    target_component: Optional[str] = None


@dataclass
class StreamStatistics:
    """Statistics for stream usage and performance"""
    total_created: int = 0
    total_closed: int = 0
    active_count: int = 0
    peak_active_count: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_bytes_transferred: int = 0
    average_buffer_utilization: float = 0.0
    stream_creation_times: List[float] = field(default_factory=list)
    stream_lifetimes: List[float] = field(default_factory=list)
    
    def update_creation_time(self, creation_time: float):
        """Update stream creation timing statistics"""
        self.stream_creation_times.append(creation_time)
        # Keep only last 1000 measurements
        if len(self.stream_creation_times) > 1000:
            self.stream_creation_times = self.stream_creation_times[-1000:]
    
    def update_lifetime(self, lifetime: float):
        """Update stream lifetime statistics"""
        self.stream_lifetimes.append(lifetime)
        # Keep only last 1000 measurements
        if len(self.stream_lifetimes) > 1000:
            self.stream_lifetimes = self.stream_lifetimes[-1000:]
    
    @property
    def average_creation_time(self) -> float:
        """Get average stream creation time"""
        return sum(self.stream_creation_times) / len(self.stream_creation_times) if self.stream_creation_times else 0.0
    
    @property
    def average_lifetime(self) -> float:
        """Get average stream lifetime"""
        return sum(self.stream_lifetimes) / len(self.stream_lifetimes) if self.stream_lifetimes else 0.0


class StreamManagerError(Exception):
    """Base exception for StreamManager errors"""
    pass


class StreamCreationError(StreamManagerError):
    """Raised when stream creation fails"""
    pass


class StreamNotFoundError(StreamManagerError):
    """Raised when a stream is not found"""
    pass


class StreamHealthError(StreamManagerError):
    """Raised when stream health check fails"""
    pass


class StreamManager:
    """
    Manages AnyIO stream lifecycle and health monitoring
    
    Provides:
    - Stream creation with tracking and configuration
    - Health monitoring and statistics collection
    - Resource cleanup and leak prevention
    - Performance metrics and optimization
    """
    
    def __init__(self, default_buffer_size: int = 100):
        self.default_buffer_size = default_buffer_size
        self.active_streams: Dict[str, StreamInfo] = {}
        self.statistics = StreamStatistics()
        
        # Health monitoring
        self.health_check_interval = 30.0  # seconds
        self.last_health_check = time.time()
        self.unhealthy_streams: List[str] = []
        
        # Performance tracking
        self.buffer_utilization_history: Dict[str, List[float]] = defaultdict(list)
        self.message_flow_rates: Dict[str, float] = {}
        
        # Cleanup tracking
        self._cleanup_refs: List[weakref.ref] = []
        
        # Logging
        self.logger = logging.getLogger(f"StreamManager")
        self.logger.info("✨ StreamManager initialized with default buffer size: %d", default_buffer_size)
    
    def create_stream(self, 
                     buffer_size: Optional[int] = None,
                     source_component: Optional[str] = None,
                     target_component: Optional[str] = None) -> Tuple[MemoryObjectSendStream, MemoryObjectReceiveStream]:
        """
        Create new memory object stream pair with tracking
        
        Args:
            buffer_size: Buffer size for the stream (uses default if None)
            source_component: Name of the component that will send to this stream
            target_component: Name of the component that will receive from this stream
            
        Returns:
            Tuple of (send_stream, receive_stream)
            
        Raises:
            StreamCreationError: If stream creation fails
        """
        if buffer_size is None:
            buffer_size = self.default_buffer_size
        
        try:
            creation_start = time.time()
            
            # Create the stream pair
            send_stream, receive_stream = anyio.create_memory_object_stream(buffer_size)
            
            creation_time = time.time() - creation_start
            
            # Generate unique stream ID
            stream_id = str(uuid.uuid4())
            
            # Create stream info
            stream_info = StreamInfo(
                id=stream_id,
                send_stream=send_stream,
                receive_stream=receive_stream,
                created_at=time.time(),
                buffer_size=buffer_size,
                source_component=source_component,
                target_component=target_component
            )
            
            # Store stream info
            self.active_streams[stream_id] = stream_info
            
            # Update statistics
            self.statistics.total_created += 1
            self.statistics.active_count += 1
            self.statistics.peak_active_count = max(self.statistics.peak_active_count, self.statistics.active_count)
            self.statistics.update_creation_time(creation_time)
            
            # Setup cleanup tracking
            self._setup_stream_cleanup(stream_id, send_stream, receive_stream)
            
            self.logger.info(
                "📤📥 Created stream %s: %s → %s (buffer: %d, creation time: %.3fms)",
                stream_id[:8], source_component or "unknown", target_component or "unknown", 
                buffer_size, creation_time * 1000
            )
            
            return send_stream, receive_stream
            
        except Exception as e:
            self.logger.error("❌ Failed to create stream: %s", e)
            raise StreamCreationError(f"Stream creation failed: {e}") from e
    
    def _setup_stream_cleanup(self, stream_id: str, send_stream: MemoryObjectSendStream, receive_stream: MemoryObjectReceiveStream):
        """Setup automatic cleanup when streams are garbage collected"""
        def cleanup_callback(ref):
            if stream_id in self.active_streams:
                self._mark_stream_closed(stream_id)
        
        # Create weak references with cleanup callback
        send_ref = weakref.ref(send_stream, cleanup_callback)
        receive_ref = weakref.ref(receive_stream, cleanup_callback)
        
        self._cleanup_refs.extend([send_ref, receive_ref])
    
    def _mark_stream_closed(self, stream_id: str):
        """Mark a stream as closed and update statistics"""
        if stream_id in self.active_streams:
            stream_info = self.active_streams[stream_id]
            lifetime = time.time() - stream_info.created_at
            
            # Update statistics
            self.statistics.total_closed += 1
            self.statistics.active_count -= 1
            self.statistics.update_lifetime(lifetime)
            
            # Remove from active streams
            del self.active_streams[stream_id]
            
            self.logger.debug(
                "🔒 Stream %s closed (lifetime: %.2fs, %s → %s)",
                stream_id[:8], lifetime, 
                stream_info.source_component or "unknown",
                stream_info.target_component or "unknown"
            )
    
    async def close_stream(self, stream_id: str):
        """
        Explicitly close a stream by ID
        
        Args:
            stream_id: ID of the stream to close
            
        Raises:
            StreamNotFoundError: If stream ID is not found
        """
        if stream_id not in self.active_streams:
            raise StreamNotFoundError(f"Stream {stream_id} not found")
        
        stream_info = self.active_streams[stream_id]
        
        try:
            # Close both ends of the stream
            await stream_info.send_stream.aclose()
            await stream_info.receive_stream.aclose()
            
            self.logger.info("🔒 Explicitly closed stream %s", stream_id[:8])
            
        except Exception as e:
            self.logger.warning("⚠️ Error closing stream %s: %s", stream_id[:8], e)
        finally:
            # Mark as closed regardless
            self._mark_stream_closed(stream_id)
    
    async def close_all_streams(self):
        """Close all managed streams"""
        self.logger.info("🔒 Closing all %d active streams", len(self.active_streams))
        
        # Get list of stream IDs to avoid modification during iteration
        stream_ids = list(self.active_streams.keys())
        
        # Close streams concurrently
        close_tasks = []
        for stream_id in stream_ids:
            close_tasks.append(asyncio.create_task(self.close_stream(stream_id)))
        
        # Wait for all closes to complete
        if close_tasks:
            try:
                await asyncio.gather(*close_tasks, return_exceptions=True)
            except Exception as e:
                self.logger.error("❌ Error during bulk stream closure: %s", e)
        
        # Clean up weak references
        self._cleanup_refs.clear()
        
        self.logger.info("✅ All streams closed")
    
    def get_stream_info(self, stream_id: str) -> StreamInfo:
        """
        Get information about a specific stream
        
        Args:
            stream_id: ID of the stream
            
        Returns:
            StreamInfo object
            
        Raises:
            StreamNotFoundError: If stream ID is not found
        """
        if stream_id not in self.active_streams:
            raise StreamNotFoundError(f"Stream {stream_id} not found")
        
        return self.active_streams[stream_id]
    
    def get_stream_statistics(self) -> Dict[str, Any]:
        """Get comprehensive stream statistics"""
        return {
            "total_created": self.statistics.total_created,
            "total_closed": self.statistics.total_closed,
            "active_count": self.statistics.active_count,
            "peak_active_count": self.statistics.peak_active_count,
            "total_messages_sent": self.statistics.total_messages_sent,
            "total_messages_received": self.statistics.total_messages_received,
            "total_bytes_transferred": self.statistics.total_bytes_transferred,
            "average_buffer_utilization": self.statistics.average_buffer_utilization,
            "average_creation_time": self.statistics.average_creation_time,
            "average_lifetime": self.statistics.average_lifetime,
            "unhealthy_streams": len(self.unhealthy_streams),
            "memory_usage": {
                "active_stream_count": len(self.active_streams),
                "cleanup_references": len(self._cleanup_refs)
            }
        }
    
    def get_active_streams_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all active streams"""
        summary = []
        current_time = time.time()
        
        for stream_id, stream_info in self.active_streams.items():
            lifetime = current_time - stream_info.created_at
            
            summary.append({
                "id": stream_id,
                "source_component": stream_info.source_component,
                "target_component": stream_info.target_component,
                "buffer_size": stream_info.buffer_size,
                "lifetime_seconds": lifetime,
                "created_at": stream_info.created_at,
                "is_healthy": stream_id not in self.unhealthy_streams
            })
        
        return summary
    
    async def health_check_streams(self) -> Dict[str, Any]:
        """
        Perform health check on all active streams
        
        Returns:
            Health check results
        """
        current_time = time.time()
        
        # Skip if health check too recent
        if current_time - self.last_health_check < self.health_check_interval:
            return {"skipped": True, "reason": "too_recent"}
        
        self.logger.debug("🏥 Performing health check on %d active streams", len(self.active_streams))
        
        healthy_count = 0
        unhealthy_count = 0
        self.unhealthy_streams.clear()
        
        for stream_id, stream_info in self.active_streams.items():
            try:
                # Check if streams are still valid
                is_healthy = await self._check_stream_health(stream_info)
                
                if is_healthy:
                    healthy_count += 1
                else:
                    unhealthy_count += 1
                    self.unhealthy_streams.append(stream_id)
                    
            except Exception as e:
                self.logger.warning("⚠️ Health check failed for stream %s: %s", stream_id[:8], e)
                unhealthy_count += 1
                self.unhealthy_streams.append(stream_id)
        
        self.last_health_check = current_time
        
        health_results = {
            "timestamp": current_time,
            "total_streams": len(self.active_streams),
            "healthy_streams": healthy_count,
            "unhealthy_streams": unhealthy_count,
            "health_percentage": (healthy_count / len(self.active_streams) * 100) if self.active_streams else 100,
            "unhealthy_stream_ids": self.unhealthy_streams.copy()
        }
        
        if unhealthy_count > 0:
            self.logger.warning("⚠️ Health check found %d unhealthy streams out of %d total", 
                              unhealthy_count, len(self.active_streams))
        else:
            self.logger.debug("✅ All %d streams are healthy", len(self.active_streams))
        
        return health_results
    
    async def _check_stream_health(self, stream_info: StreamInfo) -> bool:
        """
        Check the health of an individual stream
        
        Args:
            stream_info: Information about the stream to check
            
        Returns:
            True if stream is healthy, False otherwise
        """
        try:
            # Basic checks
            if stream_info.send_stream is None or stream_info.receive_stream is None:
                return False
            
            # Check if streams are closed
            # Note: AnyIO streams don't have a direct "is_closed" property,
            # so we rely on the lifecycle tracking
            
            # Additional health checks could include:
            # - Buffer utilization monitoring
            # - Message flow rate analysis
            # - Memory usage tracking
            
            return True
            
        except Exception:
            return False
    
    def record_message_sent(self, stream_id: str, message_size: int = 0):
        """Record a message being sent through a stream"""
        if stream_id in self.active_streams:
            self.statistics.total_messages_sent += 1
            self.statistics.total_bytes_transferred += message_size
    
    def record_message_received(self, stream_id: str, message_size: int = 0):
        """Record a message being received from a stream"""
        if stream_id in self.active_streams:
            self.statistics.total_messages_received += 1
            self.statistics.total_bytes_transferred += message_size
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        current_time = time.time()
        stats = self.get_stream_statistics()
        
        # Calculate rates
        message_rate = 0
        byte_rate = 0
        if self.statistics.stream_creation_times:
            earliest_creation = min(stream_info.created_at for stream_info in self.active_streams.values()) if self.active_streams else current_time
            duration = current_time - earliest_creation
            if duration > 0:
                message_rate = (self.statistics.total_messages_sent + self.statistics.total_messages_received) / duration
                byte_rate = self.statistics.total_bytes_transferred / duration
        
        return {
            "timestamp": current_time,
            "statistics": stats,
            "performance": {
                "message_rate_per_second": message_rate,
                "byte_rate_per_second": byte_rate,
                "stream_creation_rate": len(self.statistics.stream_creation_times) / max(1, len(self.statistics.stream_creation_times)),
                "resource_efficiency": {
                    "streams_per_component": stats["active_count"] / max(1, len(set(
                        [info.source_component for info in self.active_streams.values() if info.source_component] +
                        [info.target_component for info in self.active_streams.values() if info.target_component]
                    ))),
                    "average_buffer_utilization": stats["average_buffer_utilization"]
                }
            },
            "health": {
                "healthy_stream_percentage": 100 - (len(self.unhealthy_streams) / max(1, stats["active_count"]) * 100),
                "last_health_check": self.last_health_check
            }
        }
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'active_streams') and self.active_streams:
            self.logger.warning("⚠️ StreamManager destroyed with %d active streams", len(self.active_streams))


# Export main classes
__all__ = [
    'StreamManager',
    'StreamInfo',
    'StreamStatistics', 
    'StreamManagerError',
    'StreamCreationError',
    'StreamNotFoundError',
    'StreamHealthError'
]