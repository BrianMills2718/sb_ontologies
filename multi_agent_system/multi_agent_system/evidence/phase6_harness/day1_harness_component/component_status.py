#!/usr/bin/env python3
"""
ComponentStatus: Thread-safe component lifecycle state management
================================================================

Manages component lifecycle state with validated transitions, error tracking,
and recovery mechanisms for the SystemExecutionHarness architecture.

Key Features:
- Thread-safe state management with asyncio locks
- Validated state transitions with comprehensive error handling
- Error tracking and recovery mechanisms
- Performance metrics and timing information
- Component health monitoring
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging


class ComponentState(Enum):
    """Valid component states"""
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    FAILED = "failed"


@dataclass
class StateTransition:
    """Records a state transition with timing and context"""
    from_state: ComponentState
    to_state: ComponentState
    timestamp: float
    duration: float = 0.0
    context: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None


@dataclass
class ComponentMetrics:
    """Component performance and health metrics"""
    total_messages_processed: int = 0
    total_messages_sent: int = 0
    total_errors: int = 0
    last_activity_time: float = field(default_factory=time.time)
    average_processing_time: float = 0.0
    peak_memory_usage: int = 0
    uptime_seconds: float = 0.0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_time = time.time()
    
    def record_message_processed(self, processing_time: float):
        """Record a processed message with timing"""
        self.total_messages_processed += 1
        self.average_processing_time = (
            (self.average_processing_time * (self.total_messages_processed - 1) + processing_time) /
            self.total_messages_processed
        )
        self.update_activity()
    
    def record_message_sent(self):
        """Record a sent message"""
        self.total_messages_sent += 1
        self.update_activity()
    
    def record_error(self):
        """Record an error occurrence"""
        self.total_errors += 1
        self.update_activity()


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted"""
    pass


class ComponentStatusError(Exception):
    """General component status error"""
    pass


class ComponentStatus:
    """Thread-safe component lifecycle state management"""
    
    # Valid state transition matrix
    VALID_TRANSITIONS = {
        ComponentState.CREATED: [ComponentState.READY, ComponentState.ERROR, ComponentState.FAILED],
        ComponentState.READY: [ComponentState.RUNNING, ComponentState.STOPPING, ComponentState.ERROR, ComponentState.FAILED],
        ComponentState.RUNNING: [ComponentState.PAUSED, ComponentState.STOPPING, ComponentState.ERROR, ComponentState.FAILED],
        ComponentState.PAUSED: [ComponentState.RUNNING, ComponentState.STOPPING, ComponentState.ERROR, ComponentState.FAILED],
        ComponentState.STOPPING: [ComponentState.STOPPED, ComponentState.ERROR, ComponentState.FAILED],
        ComponentState.STOPPED: [ComponentState.READY, ComponentState.FAILED],  # Allow restart
        ComponentState.ERROR: [ComponentState.READY, ComponentState.STOPPED, ComponentState.FAILED],  # Allow recovery
        ComponentState.FAILED: [ComponentState.READY]  # Allow recovery from failure
    }
    
    def __init__(self, name: str = "unknown"):
        self.name = name
        self.state = ComponentState.CREATED
        self.previous_state: Optional[ComponentState] = None
        self.creation_time = time.time()
        self.last_transition_time = self.creation_time
        self.error_count = 0
        self.last_error: Optional[Exception] = None
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Transition history
        self.transition_history: List[StateTransition] = []
        self.max_history_size = 100
        
        # Metrics
        self.metrics = ComponentMetrics()
        
        # Logging
        self.logger = logging.getLogger(f"ComponentStatus.{self.name}")
        
        self.logger.info(f"✨ ComponentStatus created for '{self.name}' in state {self.state.value}")
    
    async def transition_to(self, new_state: ComponentState, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transition to new state with validation and error handling
        
        Args:
            new_state: Target state to transition to
            context: Optional context information for the transition
            
        Returns:
            bool: True if transition was successful
            
        Raises:
            InvalidStateTransitionError: If transition is not allowed
        """
        async with self._lock:
            if isinstance(new_state, str):
                new_state = ComponentState(new_state)
            
            # Check if transition is valid
            if new_state not in self.VALID_TRANSITIONS.get(self.state, []):
                error_msg = f"Invalid transition from {self.state.value} to {new_state.value} for component '{self.name}'"
                self.logger.error(f"❌ {error_msg}")
                raise InvalidStateTransitionError(error_msg)
            
            # Record transition timing
            transition_start = time.time()
            
            try:
                # Update state
                self.previous_state = self.state
                self.state = new_state
                current_time = time.time()
                transition_duration = current_time - transition_start
                
                # Record transition
                transition = StateTransition(
                    from_state=self.previous_state,
                    to_state=new_state,
                    timestamp=current_time,
                    duration=transition_duration,
                    context=context
                )
                
                self._record_transition(transition)
                
                # Update timing
                self.last_transition_time = current_time
                
                # Reset error count on successful transition to healthy states
                if new_state in [ComponentState.READY, ComponentState.RUNNING]:
                    self.error_count = 0
                    self.recovery_attempts = 0
                
                # Update metrics
                self.metrics.uptime_seconds = current_time - self.creation_time
                self.metrics.update_activity()
                
                self.logger.info(f"✅ Component '{self.name}' transitioned {self.previous_state.value} → {self.state.value}")
                
                return True
                
            except Exception as e:
                # Record failed transition
                failed_transition = StateTransition(
                    from_state=self.previous_state or self.state,
                    to_state=new_state,
                    timestamp=time.time(),
                    duration=time.time() - transition_start,
                    context=context,
                    error=e
                )
                
                self._record_transition(failed_transition)
                
                self.logger.error(f"❌ Transition failed for component '{self.name}': {e}")
                raise ComponentStatusError(f"State transition failed: {e}") from e
    
    def _record_transition(self, transition: StateTransition):
        """Record transition in history with size management"""
        self.transition_history.append(transition)
        
        # Maintain history size limit
        if len(self.transition_history) > self.max_history_size:
            self.transition_history = self.transition_history[-self.max_history_size:]
    
    async def record_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Record an error and potentially transition to error state"""
        async with self._lock:
            self.error_count += 1
            self.last_error = error
            self.metrics.record_error()
            
            error_context = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "error_count": self.error_count,
                **(context or {})
            }
            
            self.logger.error(f"🚨 Error recorded for component '{self.name}': {error}")
            
            # Transition to error state if not already in terminal state
            if self.state not in [ComponentState.ERROR, ComponentState.FAILED, ComponentState.STOPPED]:
                try:
                    await self.transition_to(ComponentState.ERROR, error_context)
                except InvalidStateTransitionError:
                    # If we can't transition to ERROR, try FAILED
                    try:
                        await self.transition_to(ComponentState.FAILED, error_context)
                    except InvalidStateTransitionError:
                        self.logger.warning(f"⚠️ Could not transition to error state from {self.state.value}")
    
    async def attempt_recovery(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Attempt to recover from error state
        
        Returns:
            bool: True if recovery was successful
        """
        async with self._lock:
            if self.state not in [ComponentState.ERROR, ComponentState.FAILED]:
                self.logger.warning(f"⚠️ Recovery attempted but component '{self.name}' is not in error state")
                return False
            
            if self.recovery_attempts >= self.max_recovery_attempts:
                self.logger.error(f"❌ Max recovery attempts ({self.max_recovery_attempts}) reached for component '{self.name}'")
                return False
            
            self.recovery_attempts += 1
            recovery_context = {
                "recovery_attempt": self.recovery_attempts,
                "max_attempts": self.max_recovery_attempts,
                **(context or {})
            }
            
            try:
                await self.transition_to(ComponentState.READY, recovery_context)
                self.logger.info(f"🔄 Recovery successful for component '{self.name}' (attempt {self.recovery_attempts})")
                return True
            except Exception as e:
                self.logger.error(f"❌ Recovery failed for component '{self.name}': {e}")
                return False
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is in a healthy state"""
        return self.state in [ComponentState.READY, ComponentState.RUNNING, ComponentState.PAUSED]
    
    @property
    def is_running(self) -> bool:
        """Check if component is currently running"""
        return self.state == ComponentState.RUNNING
    
    @property
    def is_stopped(self) -> bool:
        """Check if component is stopped"""
        return self.state in [ComponentState.STOPPED, ComponentState.FAILED]
    
    @property
    def can_start(self) -> bool:
        """Check if component can be started"""
        return self.state in [ComponentState.READY, ComponentState.STOPPED]
    
    @property
    def uptime(self) -> float:
        """Get component uptime in seconds"""
        return time.time() - self.creation_time
    
    @property
    def time_since_last_transition(self) -> float:
        """Get time since last state transition"""
        return time.time() - self.last_transition_time
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        return {
            "name": self.name,
            "state": self.state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "is_healthy": self.is_healthy,
            "is_running": self.is_running,
            "is_stopped": self.is_stopped,
            "can_start": self.can_start,
            "uptime_seconds": self.uptime,
            "time_since_last_transition": self.time_since_last_transition,
            "error_count": self.error_count,
            "last_error": str(self.last_error) if self.last_error else None,
            "recovery_attempts": self.recovery_attempts,
            "max_recovery_attempts": self.max_recovery_attempts,
            "creation_time": self.creation_time,
            "last_transition_time": self.last_transition_time,
            "metrics": {
                "total_messages_processed": self.metrics.total_messages_processed,
                "total_messages_sent": self.metrics.total_messages_sent,
                "total_errors": self.metrics.total_errors,
                "last_activity_time": self.metrics.last_activity_time,
                "average_processing_time": self.metrics.average_processing_time,
                "peak_memory_usage": self.metrics.peak_memory_usage,
                "uptime_seconds": self.metrics.uptime_seconds
            },
            "recent_transitions": [
                {
                    "from": t.from_state.value,
                    "to": t.to_state.value,
                    "timestamp": t.timestamp,
                    "duration": t.duration,
                    "context": t.context,
                    "error": str(t.error) if t.error else None
                }
                for t in self.transition_history[-5:]  # Last 5 transitions
            ]
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get focused health report"""
        return {
            "component": self.name,
            "healthy": self.is_healthy,
            "state": self.state.value,
            "uptime": self.uptime,
            "error_count": self.error_count,
            "recovery_attempts": self.recovery_attempts,
            "last_activity": time.time() - self.metrics.last_activity_time,
            "performance": {
                "messages_processed": self.metrics.total_messages_processed,
                "messages_sent": self.metrics.total_messages_sent,
                "avg_processing_time": self.metrics.average_processing_time,
                "error_rate": self.metrics.total_errors / max(1, self.metrics.total_messages_processed)
            }
        }


# Export classes
__all__ = [
    'ComponentState',
    'StateTransition', 
    'ComponentMetrics',
    'ComponentStatus',
    'InvalidStateTransitionError',
    'ComponentStatusError'
]