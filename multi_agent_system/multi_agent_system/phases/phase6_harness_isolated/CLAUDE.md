# Phase 6: SystemExecutionHarness Architecture Implementation

**IMPLEMENTATION AGENT INSTRUCTIONS - ISOLATED CONTEXT**

## Objective

Implement the core SystemExecutionHarness architecture for V5.0, including HarnessComponent base class, SystemExecutionHarness orchestrator, and stream-based communication framework.

## Success Criteria

Create a complete, working SystemExecutionHarness that can orchestrate multiple components communicating via AnyIO MemoryObjectStreams with proper lifecycle management.

## Required Evidence Structure

```
evidence/phase6_harness/
├── day1_harness_component/
│   ├── harness_component.py              # Complete HarnessComponent base class
│   ├── component_status.py               # ComponentStatus state management
│   ├── test_harness_component.py         # Comprehensive unit tests
│   ├── test_execution_log.txt            # Raw test output showing PASS/FAIL
│   └── component_lifecycle_demo.py       # Working demo with output logs
├── day2_execution_harness/
│   ├── system_execution_harness.py       # Complete SystemExecutionHarness
│   ├── stream_manager.py                 # AnyIO stream management
│   ├── test_execution_harness.py         # Integration tests
│   ├── harness_test_output.txt           # Raw test execution logs
│   └── harness_demo_system.py            # End-to-end demo with logs
├── day3_stream_communication/
│   ├── stream_framework.py               # Stream abstraction layer
│   ├── message_protocol.py               # Serialization/deserialization
│   ├── test_stream_communication.py      # Stream communication tests
│   ├── stream_test_logs.txt              # Raw execution output
│   └── multi_component_demo.py           # 3+ components communicating
└── week1_integration/
    ├── full_harness_integration_test.py  # Complete system test
    ├── integration_test_output.txt       # Raw execution logs
    ├── performance_benchmark.py          # Performance measurement
    ├── benchmark_results.txt             # Raw performance data
    └── real_system_demo.py               # Working system demonstrating all features
```

## Day 1: HarnessComponent Base Class

### Target Implementation

Create the foundational HarnessComponent class that all V5.0 components inherit from:

```python
class HarnessComponent(Component):
    """Base class for all harness-compatible components"""
    
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.receive_streams: Dict[str, anyio.MemoryObjectReceiveStream] = {}
        self.send_streams: Dict[str, anyio.MemoryObjectSendStream] = {}
        self._status = ComponentStatus()
        
    async def setup(self, harness_context: Optional[Dict[str, Any]] = None):
        """Initialize component resources (database connections, etc.)"""
        await super().setup(harness_context)
        self._status.transition_to("ready")
        
    async def process(self):
        """Core logic loop - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process()")
        
    async def cleanup(self):
        """Clean up resources"""
        self._status.transition_to("stopping")
        # Close all streams
        for stream in self.send_streams.values():
            await stream.aclose()
        self._status.transition_to("stopped")
```

### ComponentStatus Implementation

```python
class ComponentStatus:
    """Manages component lifecycle state"""
    
    def __init__(self):
        self.state = "created"
        self.last_transition = time.time()
        self.error_count = 0
        
    def transition_to(self, new_state: str):
        """Transition to new state with validation"""
        valid_transitions = {
            "created": ["ready", "error"],
            "ready": ["running", "stopping", "error"],
            "running": ["stopping", "error"],
            "stopping": ["stopped", "error"],
            "stopped": ["ready"],  # Allow restart
            "error": ["ready", "stopped"]
        }
        
        if new_state not in valid_transitions.get(self.state, []):
            raise InvalidStateTransition(f"Cannot transition from {self.state} to {new_state}")
            
        self.state = new_state
        self.last_transition = time.time()
        
    @property
    def is_running(self) -> bool:
        return self.state == "running"
```

### Implementation Requirements

1. **HarnessComponent Base Class** (`harness_component.py`):
   - Inherit from existing Component class
   - Add stream connection management (receive_streams, send_streams)
   - Implement lifecycle methods (setup, process, cleanup)
   - Add ComponentStatus integration
   - Include error handling and graceful shutdown

2. **ComponentStatus** (`component_status.py`):
   - State machine for component lifecycle
   - Valid state transitions with validation
   - Error tracking and recovery mechanisms
   - Thread-safe state management

3. **Comprehensive Tests** (`test_harness_component.py`):
   - Test all lifecycle transitions
   - Test stream connection setup
   - Test error handling and recovery
   - Test concurrent component execution
   - Generate raw test output to `test_execution_log.txt`

4. **Working Demo** (`component_lifecycle_demo.py`):
   - Create 3 different HarnessComponent implementations
   - Demonstrate full lifecycle (setup → running → cleanup)
   - Show stream connections between components
   - Log all output to demonstrate working functionality

## Day 2: SystemExecutionHarness Orchestrator

### Target Implementation

```python
class SystemExecutionHarness:
    """Universal orchestrator for component-based systems"""
    
    def __init__(self):
        self.components: Dict[str, HarnessComponent] = {}
        self.streams: Dict[str, Tuple[anyio.MemoryObjectSendStream, anyio.MemoryObjectReceiveStream]] = {}
        self.task_group: Optional[anyio.TaskGroup] = None
        self.running = False
        
    def register_component(self, name: str, component: HarnessComponent):
        """Register a component with the harness"""
        if name in self.components:
            raise ComponentAlreadyRegistered(f"Component {name} already registered")
        self.components[name] = component
        
    def connect(self, from_output: str, to_input: str):
        """Create stream-based connection between components"""
        # Parse "component.port" format
        from_component, from_port = from_output.split(".")
        to_component, to_port = to_input.split(".")
        
        # Create stream
        send_stream, receive_stream = anyio.create_memory_object_stream()
        
        # Connect to components
        self.components[from_component].send_streams[from_port] = send_stream
        self.components[to_component].receive_streams[to_port] = receive_stream
        
    async def run(self):
        """Start all components concurrently"""
        if self.running:
            raise HarnessAlreadyRunning("Harness is already running")
            
        self.running = True
        
        async with anyio.create_task_group() as tg:
            self.task_group = tg
            
            # Setup all components
            for component in self.components.values():
                await component.setup()
                
            # Start all components
            for name, component in self.components.items():
                tg.start_soon(self._run_component, name, component)
                
    async def stop(self):
        """Graceful shutdown with resource cleanup"""
        self.running = False
        
        # Cleanup all components
        for component in self.components.values():
            await component.cleanup()
```

### StreamManager Implementation

```python
class StreamManager:
    """Manages AnyIO stream lifecycle and health"""
    
    def __init__(self):
        self.active_streams: Dict[str, StreamInfo] = {}
        
    def create_stream(self, buffer_size: int = 100) -> Tuple[anyio.MemoryObjectSendStream, anyio.MemoryObjectReceiveStream]:
        """Create new memory object stream with tracking"""
        send_stream, receive_stream = anyio.create_memory_object_stream(buffer_size)
        
        stream_id = str(uuid.uuid4())
        self.active_streams[stream_id] = StreamInfo(
            id=stream_id,
            send_stream=send_stream,
            receive_stream=receive_stream,
            created_at=time.time()
        )
        
        return send_stream, receive_stream
        
    async def close_all_streams(self):
        """Close all managed streams"""
        for stream_info in self.active_streams.values():
            await stream_info.send_stream.aclose()
            
    def get_stream_stats(self) -> Dict[str, Any]:
        """Get statistics about active streams"""
        return {
            "active_count": len(self.active_streams),
            "total_created": len(self.active_streams)  # Simplified for demo
        }
```

### Implementation Requirements

1. **SystemExecutionHarness** (`system_execution_harness.py`):
   - Component registration and lifecycle management
   - Stream connection setup and management
   - Concurrent execution using anyio.TaskGroup
   - Graceful shutdown with proper resource cleanup
   - Error handling and component failure recovery

2. **StreamManager** (`stream_manager.py`):
   - AnyIO MemoryObjectStream creation and management
   - Stream health monitoring and statistics
   - Buffer size configuration and optimization
   - Stream cleanup and resource management

3. **Integration Tests** (`test_execution_harness.py`):
   - Test component registration and connection
   - Test concurrent execution of multiple components
   - Test graceful shutdown and resource cleanup
   - Test error recovery and component failure handling
   - Generate raw test output to `harness_test_output.txt`

4. **End-to-End Demo** (`harness_demo_system.py`):
   - Create a complete system with 3+ components
   - Demonstrate data flowing through stream connections
   - Show graceful startup and shutdown
   - Log all execution output to demonstrate functionality

## Day 3: Stream-Based Communication

### Target Implementation

```python
class StreamFramework:
    """High-level stream abstraction for component communication"""
    
    def __init__(self):
        self.message_protocol = MessageProtocol()
        
    async def send_message(self, stream: anyio.MemoryObjectSendStream, message: Any):
        """Send serialized message through stream"""
        serialized = self.message_protocol.serialize(message)
        await stream.send(serialized)
        
    async def receive_message(self, stream: anyio.MemoryObjectReceiveStream) -> Any:
        """Receive and deserialize message from stream"""
        serialized = await stream.receive()
        return self.message_protocol.deserialize(serialized)
        
    async def broadcast_message(self, streams: List[anyio.MemoryObjectSendStream], message: Any):
        """Broadcast message to multiple streams"""
        serialized = self.message_protocol.serialize(message)
        async with anyio.create_task_group() as tg:
            for stream in streams:
                tg.start_soon(stream.send, serialized)

class MessageProtocol:
    """Message serialization/deserialization"""
    
    def serialize(self, message: Any) -> bytes:
        """Serialize message to bytes"""
        return json.dumps({
            "type": type(message).__name__,
            "data": message,
            "timestamp": time.time(),
            "id": str(uuid.uuid4())
        }).encode()
        
    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to message"""
        message_dict = json.loads(data.decode())
        return message_dict["data"]
```

### Implementation Requirements

1. **StreamFramework** (`stream_framework.py`):
   - High-level abstraction over AnyIO streams
   - Message sending/receiving with automatic serialization
   - Broadcast and multicast capabilities
   - Error handling for stream communication

2. **MessageProtocol** (`message_protocol.py`):
   - JSON-based message serialization
   - Message metadata (type, timestamp, ID)
   - Support for complex data types
   - Message validation and error handling

3. **Stream Tests** (`test_stream_communication.py`):
   - Test message serialization/deserialization
   - Test point-to-point communication
   - Test broadcast and multicast scenarios
   - Test error handling and recovery
   - Generate raw test output to `stream_test_logs.txt`

4. **Multi-Component Demo** (`multi_component_demo.py`):
   - Create 3+ components with complex communication patterns
   - Demonstrate different message types and protocols
   - Show error handling and recovery mechanisms
   - Log all communication output

## Week 1 Integration: Complete System Test

### Integration Requirements

1. **Full Integration Test** (`full_harness_integration_test.py`):
   - Test complete SystemExecutionHarness with multiple components
   - Test complex stream communication patterns
   - Test system performance under load
   - Test error recovery and component failure scenarios
   - Generate comprehensive output to `integration_test_output.txt`

2. **Performance Benchmark** (`performance_benchmark.py`):
   - Measure component startup time
   - Measure message throughput and latency
   - Measure memory usage and resource consumption
   - Compare performance against requirements
   - Output raw data to `benchmark_results.txt`

3. **Real System Demo** (`real_system_demo.py`):
   - Create a realistic system (e.g., data processing pipeline)
   - Demonstrate all harness features working together
   - Show production-ready patterns and error handling
   - Generate comprehensive execution logs

## Implementation Guidelines

### Code Quality Requirements

1. **Type Hints**: All code must use comprehensive type hints
2. **Error Handling**: Proper exception handling with custom exception types
3. **Logging**: Use structured logging for all operations
4. **Testing**: Comprehensive test coverage with raw output logs
5. **Documentation**: Clear docstrings and inline comments

### Performance Requirements

1. **Component Startup**: < 100ms per component
2. **Message Latency**: < 10ms for local communication
3. **Throughput**: > 1000 messages/second per stream
4. **Memory Usage**: < 50MB baseline for harness
5. **Shutdown Time**: < 5 seconds for graceful shutdown

### Integration Requirements

1. **Existing Component Compatibility**: Must work with existing Component base class
2. **AnyIO Integration**: Pure AnyIO patterns (no asyncio mixing)
3. **Resource Management**: Proper cleanup of all resources
4. **Error Recovery**: Graceful handling of component failures
5. **Thread Safety**: Safe for concurrent access where needed

## Evidence Requirements

### Raw Output Files Required

1. **Test Execution Logs**: Raw terminal output from all test runs
2. **Performance Data**: Actual benchmark numbers and measurements
3. **Demo Output**: Complete logs from working demonstrations
4. **Error Logs**: Examples of error handling and recovery
5. **Integration Results**: Raw output from end-to-end system tests

### Executable Requirements

- All code must be executable by external evaluator
- All tests must pass when run independently
- All demos must produce visible, verifiable results
- All benchmarks must generate measurable data
- All integration tests must demonstrate working functionality

## Success Criteria

Phase 6 is complete when:

1. **All Evidence Files Present**: Complete evidence structure as specified
2. **All Tests Pass**: Raw test output shows 100% success rate
3. **Performance Meets Requirements**: Benchmark data meets all targets
4. **Integration Works**: End-to-end demos show working system
5. **External Validation**: Independent evaluator can execute and verify all evidence

---

**CRITICAL**: This is an isolated implementation task. Do NOT reference previous conversation context. Focus solely on implementing the SystemExecutionHarness architecture as specified.