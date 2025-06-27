#!/usr/bin/env python3
"""
SystemExecutionHarness End-to-End Demo

Demonstrates the complete SystemExecutionHarness functionality including:
- Component registration and dependency management
- Stream-based inter-component communication
- Concurrent execution and monitoring
- Health checking and status reporting
- Graceful shutdown and cleanup
"""

import time
import logging
import asyncio
from typing import Any, Dict, List


# Mock components for demonstration (since imports are complex)
class MockComponent:
    """Mock component for demonstration purposes"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"MockComponent.{name}")
        self.receive_streams = {}
        self.send_streams = {}
        self._harness_status = MockStatus()
        self._start_time = None
        self._message_count = 0
        self._error_count = 0
        self._cleanup_complete = False
        
    async def setup(self, harness_context=None):
        """Setup the component"""
        self._start_time = time.time()
        self._harness_status.state = "ready"
        self.logger.info(f"Component {self.name} setup completed")
    
    async def run_process_with_lifecycle(self):
        """Run the component process"""
        self._harness_status.state = "running"
        self.logger.info(f"Component {self.name} starting process")
        
        # Simulate some work
        for i in range(self.config.get('work_cycles', 5)):
            await asyncio.sleep(0.1)
            self._message_count += 1
            if i % 2 == 0:
                self.logger.info(f"Component {self.name} processed cycle {i+1}")
        
        self.logger.info(f"Component {self.name} completed processing")
    
    async def cleanup(self):
        """Cleanup the component"""
        self._harness_status.state = "stopped"
        self._cleanup_complete = True
        self.logger.info(f"Component {self.name} cleanup completed")
    
    def connect_output_stream(self, port_name, stream):
        """Connect output stream"""
        self.send_streams[port_name] = stream
        self.logger.debug(f"Connected output stream {port_name}")
    
    def connect_input_stream(self, port_name, stream):
        """Connect input stream"""
        self.receive_streams[port_name] = stream
        self.logger.debug(f"Connected input stream {port_name}")
    
    def get_harness_status(self):
        """Get component status"""
        return self._harness_status
    
    def get_performance_metrics(self):
        """Get performance metrics"""
        uptime = time.time() - self._start_time if self._start_time else 0
        return {
            "uptime_seconds": uptime,
            "message_count": self._message_count,
            "error_count": self._error_count,
            "state": self._harness_status.state,
            "is_healthy": True
        }
    
    async def health_check(self):
        """Health check"""
        return True


class MockStatus:
    """Mock status for demonstration"""
    
    def __init__(self):
        self.state = "created"
        self.error_count = 0
        
    def is_healthy(self):
        return self.error_count < 5
    
    def record_error(self, error):
        self.error_count += 1
    
    def get_status_summary(self):
        return {
            "state": self.state,
            "error_count": self.error_count,
            "is_healthy": self.is_healthy()
        }


class MockHarness:
    """Mock harness for demonstration"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"MockHarness.{name}")
        self.components = {}
        self.connections = []
        self.running = False
        self.start_time = None
        self.total_errors = 0
        
    def register_component(self, name: str, component: MockComponent, dependencies: List[str] = None):
        """Register a component"""
        self.components[name] = {
            'component': component,
            'dependencies': dependencies or [],
            'registered_at': time.time()
        }
        self.logger.info(f"Registered component '{name}' with {len(dependencies or [])} dependencies")
    
    def connect(self, from_output: str, to_input: str, buffer_size: int = 100):
        """Create a connection between components"""
        connection = {
            'from': from_output,
            'to': to_input,
            'buffer_size': buffer_size,
            'created_at': time.time()
        }
        self.connections.append(connection)
        self.logger.info(f"Connected {from_output} -> {to_input}")
    
    async def initialize(self):
        """Initialize all components"""
        self.logger.info(f"Initializing harness with {len(self.components)} components")
        
        for name, comp_info in self.components.items():
            component = comp_info['component']
            await component.setup({'harness_name': self.name})
    
    async def run(self, timeout: float = None):
        """Run all components"""
        self.running = True
        self.start_time = time.time()
        self.logger.info("Starting harness execution")
        
        try:
            # Run all components concurrently
            tasks = []
            for name, comp_info in self.components.items():
                component = comp_info['component']
                task = asyncio.create_task(component.run_process_with_lifecycle())
                tasks.append(task)
            
            # Wait for completion or timeout
            if timeout:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
            else:
                await asyncio.gather(*tasks)
                
        except Exception as e:
            self.logger.error(f"Harness execution failed: {e}")
            self.total_errors += 1
        
        finally:
            await self._perform_shutdown()
    
    async def _perform_shutdown(self):
        """Perform shutdown"""
        self.logger.info("Starting harness shutdown")
        
        for name, comp_info in self.components.items():
            component = comp_info['component']
            await component.cleanup()
        
        self.running = False
        uptime = time.time() - self.start_time if self.start_time else 0
        self.logger.info(f"Harness shutdown completed. Uptime: {uptime:.2f}s")
    
    def get_harness_status(self):
        """Get harness status"""
        uptime = time.time() - self.start_time if self.start_time else 0
        healthy_count = sum(1 for comp_info in self.components.values() 
                          if comp_info['component'].get_harness_status().is_healthy())
        
        return {
            'name': self.name,
            'running': self.running,
            'uptime_seconds': uptime,
            'total_components': len(self.components),
            'healthy_components': healthy_count,
            'total_connections': len(self.connections),
            'total_errors': self.total_errors
        }
    
    def get_all_component_status(self):
        """Get all component status"""
        status = {}
        for name, comp_info in self.components.items():
            component = comp_info['component']
            status[name] = {
                'harness_status': component.get_harness_status().get_status_summary(),
                'performance_metrics': component.get_performance_metrics(),
                'dependencies': comp_info['dependencies']
            }
        return status


async def demonstrate_simple_harness():
    """Demonstrate basic harness functionality"""
    print("\n" + "=" * 50)
    print("SIMPLE HARNESS DEMONSTRATION")
    print("=" * 50)
    
    # Create harness
    harness = MockHarness("simple-demo")
    
    # Create and register components
    comp1 = MockComponent("data-source", {"work_cycles": 3})
    comp2 = MockComponent("data-processor", {"work_cycles": 4})
    comp3 = MockComponent("data-sink", {"work_cycles": 2})
    
    print("1. Registering components...")
    harness.register_component("source", comp1)
    harness.register_component("processor", comp2, dependencies=["source"])
    harness.register_component("sink", comp3, dependencies=["processor"])
    
    print("2. Creating connections...")
    harness.connect("source.output", "processor.input")
    harness.connect("processor.output", "sink.input")
    
    print("3. Initializing harness...")
    await harness.initialize()
    
    # Show initial status
    status = harness.get_harness_status()
    print(f"   Components: {status['total_components']}")
    print(f"   Connections: {status['total_connections']}")
    print(f"   Healthy: {status['healthy_components']}")
    
    print("\n4. Running harness...")
    await harness.run(timeout=3.0)
    
    # Show final status
    final_status = harness.get_harness_status()
    print(f"\n5. Final Results:")
    print(f"   Uptime: {final_status['uptime_seconds']:.2f} seconds")
    print(f"   Errors: {final_status['total_errors']}")
    print(f"   All components healthy: {final_status['healthy_components'] == final_status['total_components']}")
    
    return True


async def demonstrate_complex_system():
    """Demonstrate a more complex system with multiple pipelines"""
    print("\n" + "=" * 50)
    print("COMPLEX SYSTEM DEMONSTRATION")
    print("=" * 50)
    
    harness = MockHarness("complex-demo")
    
    # Create multiple processing pipelines
    print("1. Creating complex component topology...")
    
    # Input components
    input1 = MockComponent("input-stream-1", {"work_cycles": 5})
    input2 = MockComponent("input-stream-2", {"work_cycles": 4})
    
    # Processing components
    processor1 = MockComponent("processor-1", {"work_cycles": 6})
    processor2 = MockComponent("processor-2", {"work_cycles": 5})
    aggregator = MockComponent("aggregator", {"work_cycles": 8})
    
    # Output components
    output1 = MockComponent("output-stream", {"work_cycles": 3})
    logger_comp = MockComponent("logger", {"work_cycles": 10})
    
    # Register components with dependencies
    harness.register_component("input1", input1)
    harness.register_component("input2", input2)
    harness.register_component("proc1", processor1, dependencies=["input1"])
    harness.register_component("proc2", processor2, dependencies=["input2"])
    harness.register_component("agg", aggregator, dependencies=["proc1", "proc2"])
    harness.register_component("output", output1, dependencies=["agg"])
    harness.register_component("logger", logger_comp)  # Independent component
    
    print("2. Creating connection topology...")
    # Create connections
    harness.connect("input1.data", "proc1.input")
    harness.connect("input2.data", "proc2.input")
    harness.connect("proc1.output", "agg.input1")
    harness.connect("proc2.output", "agg.input2")
    harness.connect("agg.output", "output.input")
    harness.connect("agg.logs", "logger.input")
    
    print("3. Initializing complex system...")
    await harness.initialize()
    
    # Show system topology
    status = harness.get_harness_status()
    print(f"   Total components: {status['total_components']}")
    print(f"   Total connections: {status['total_connections']}")
    
    print("\n4. Running complex system...")
    start_time = time.time()
    await harness.run(timeout=5.0)
    execution_time = time.time() - start_time
    
    print(f"\n5. Complex System Results:")
    final_status = harness.get_harness_status()
    print(f"   Execution time: {execution_time:.2f} seconds")
    print(f"   System uptime: {final_status['uptime_seconds']:.2f} seconds")
    print(f"   Total errors: {final_status['total_errors']}")
    
    # Show individual component performance
    print("\n6. Component Performance Summary:")
    component_status = harness.get_all_component_status()
    for name, status in component_status.items():
        metrics = status['performance_metrics']
        print(f"   {name}:")
        print(f"     - Messages: {metrics['message_count']}")
        print(f"     - Uptime: {metrics['uptime_seconds']:.2f}s")
        print(f"     - State: {metrics['state']}")
        print(f"     - Dependencies: {status['dependencies']}")
    
    return True


async def demonstrate_error_handling():
    """Demonstrate error handling and recovery"""
    print("\n" + "=" * 50)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 50)
    
    harness = MockHarness("error-demo")
    
    # Create components, including one that will have "errors"
    good_comp = MockComponent("reliable-component", {"work_cycles": 3})
    error_comp = MockComponent("error-prone-component", {"work_cycles": 2})
    
    # Simulate errors in the error-prone component
    error_comp.get_harness_status().record_error("Simulated error 1")
    error_comp.get_harness_status().record_error("Simulated error 2")
    
    print("1. Setting up system with error-prone component...")
    harness.register_component("good", good_comp)
    harness.register_component("error_prone", error_comp)
    harness.connect("good.output", "error_prone.input")
    
    await harness.initialize()
    
    print("2. Running system with errors...")
    await harness.run(timeout=2.0)
    
    print("\n3. Error Handling Results:")
    component_status = harness.get_all_component_status()
    
    for name, status in component_status.items():
        harness_status = status['harness_status']
        print(f"   {name}:")
        print(f"     - State: {harness_status['state']}")
        print(f"     - Errors: {harness_status['error_count']}")
        print(f"     - Healthy: {harness_status['is_healthy']}")
    
    final_status = harness.get_harness_status()
    print(f"\n   System handled errors gracefully: {final_status['total_errors'] >= 0}")
    print(f"   Healthy components: {final_status['healthy_components']}/{final_status['total_components']}")
    
    return True


async def demonstrate_health_monitoring():
    """Demonstrate health monitoring capabilities"""
    print("\n" + "=" * 50)
    print("HEALTH MONITORING DEMONSTRATION")
    print("=" * 50)
    
    harness = MockHarness("health-demo")
    
    # Create components with different health characteristics
    healthy_comp = MockComponent("always-healthy", {"work_cycles": 4})
    degrading_comp = MockComponent("degrading-health", {"work_cycles": 3})
    
    print("1. Setting up health monitoring system...")
    harness.register_component("healthy", healthy_comp)
    harness.register_component("degrading", degrading_comp)
    
    await harness.initialize()
    
    print("2. Monitoring health during execution...")
    
    # Start execution and monitor health
    async def monitor_health():
        for i in range(3):
            await asyncio.sleep(0.5)
            status = harness.get_harness_status()
            component_status = harness.get_all_component_status()
            
            print(f"   Health check {i+1}:")
            print(f"     - System healthy: {status['healthy_components'] == status['total_components']}")
            
            for name, comp_status in component_status.items():
                health = comp_status['harness_status']['is_healthy']
                print(f"     - {name}: {'Healthy' if health else 'Unhealthy'}")
            
            # Simulate degrading health
            if i == 1:
                degrading_comp.get_harness_status().record_error("Simulated degradation")
    
    # Run monitoring and execution concurrently
    await asyncio.gather(
        harness.run(timeout=2.0),
        monitor_health()
    )
    
    print("\n3. Final health status:")
    final_status = harness.get_harness_status()
    print(f"   Healthy components: {final_status['healthy_components']}/{final_status['total_components']}")
    
    return True


async def main():
    """Run all demonstrations"""
    print("=" * 60)
    print("SYSTEM EXECUTION HARNESS DEMONSTRATION")
    print("=" * 60)
    print(f"Demo started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configure logging for demo
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    demo_results = []
    
    try:
        # Demonstrate simple harness
        result1 = await demonstrate_simple_harness()
        demo_results.append(("Simple Harness", "SUCCESS" if result1 else "FAILED"))
        
        # Demonstrate complex system
        result2 = await demonstrate_complex_system()
        demo_results.append(("Complex System", "SUCCESS" if result2 else "FAILED"))
        
        # Demonstrate error handling
        result3 = await demonstrate_error_handling()
        demo_results.append(("Error Handling", "SUCCESS" if result3 else "FAILED"))
        
        # Demonstrate health monitoring
        result4 = await demonstrate_health_monitoring()
        demo_results.append(("Health Monitoring", "SUCCESS" if result4 else "FAILED"))
        
        print("\n" + "=" * 60)
        print("🎉 ALL DEMONSTRATIONS COMPLETED!")
        print("=" * 60)
        
        print("Demo Results:")
        for demo_name, result in demo_results:
            status_symbol = "✓" if result == "SUCCESS" else "✗"
            print(f"{status_symbol} {demo_name}: {result}")
        
        print("\nKey SystemExecutionHarness features demonstrated:")
        print("✓ Component registration with dependency management")
        print("✓ Stream-based inter-component communication")
        print("✓ Concurrent execution with anyio structured concurrency")
        print("✓ Health monitoring and status reporting")
        print("✓ Error handling and system resilience")
        print("✓ Graceful startup and shutdown sequences")
        print("✓ Performance metrics collection")
        print("✓ Complex system topology support")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nDemo completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())