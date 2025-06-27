#!/usr/bin/env python3
"""
Tests for SystemExecutionHarness - Day 2 Integration Tests
========================================================

Comprehensive tests for the SystemExecutionHarness functionality including:
- Component registration and connection management
- Concurrent execution of multiple components
- Graceful shutdown and resource cleanup
- Error recovery and component failure handling
- Stream management and health monitoring
"""

import asyncio
import anyio
import pytest
import time
import logging
from typing import Dict, Any, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent
from evidence.phase6_harness.day1_harness_component.component_status import ComponentState
from evidence.phase6_harness.day2_execution_harness.system_execution_harness import (
    SystemExecutionHarness, HarnessConfiguration, HarnessState,
    ComponentAlreadyRegisteredError, ComponentNotFoundError, 
    HarnessAlreadyRunningError, ComponentStartupError
)
from evidence.phase6_harness.day2_execution_harness.stream_manager import StreamManager

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSourceComponent(HarnessComponent):
    """Test source component that generates messages"""
    
    def __init__(self, name: str, message_count: int = 5):
        config = ComponentConfiguration(
            name=name,
            component_type="test_source",
            service_type="data_source",
            base_type="source"
        )
        super().__init__(config)
        self.message_count = message_count
        self.current_message = 0
        self.generation_interval = 0.1
        self.last_generation = 0
    
    async def process(self):
        """Generate test messages"""
        current_time = time.time()
        
        if (current_time - self.last_generation >= self.generation_interval and 
            self.current_message < self.message_count):
            
            message = {
                "id": f"{self.name}_msg_{self.current_message}",
                "data": f"test_data_{self.current_message}",
                "timestamp": current_time,
                "source": self.name
            }
            
            # Send to all output streams
            for stream_name in self.send_streams.keys():
                await self.send_message(stream_name, message)
            
            self.current_message += 1
            self.last_generation = current_time
        
        await asyncio.sleep(0.01)


class TestProcessorComponent(HarnessComponent):
    """Test processor component that transforms messages"""
    
    def __init__(self, name: str, processing_delay: float = 0.05):
        config = ComponentConfiguration(
            name=name,
            component_type="test_processor",
            service_type="data_processor",
            base_type="transformer"
        )
        super().__init__(config)
        self.processing_delay = processing_delay
        self.processed_messages = []
    
    async def process(self):
        """Process incoming messages"""
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    # Process the message
                    await asyncio.sleep(self.processing_delay)
                    
                    processed_message = {
                        "original_id": message.get("id"),
                        "processed_data": f"PROCESSED_{message.get('data', '')}",
                        "processed_by": self.name,
                        "processed_at": time.time()
                    }
                    
                    self.processed_messages.append(processed_message)
                    
                    # Forward to output streams
                    for output_stream in self.send_streams.keys():
                        await self.send_message(output_stream, processed_message)
            except Exception:
                # Ignore timeout errors in test
                pass
        
        await asyncio.sleep(0.01)


class TestSinkComponent(HarnessComponent):
    """Test sink component that collects messages"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="test_sink",
            service_type="data_sink",
            base_type="sink"
        )
        super().__init__(config)
        self.collected_messages = []
    
    async def process(self):
        """Collect incoming messages"""
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    self.collected_messages.append({
                        "message": message,
                        "collected_at": time.time(),
                        "stream": stream_name
                    })
            except Exception:
                # Ignore timeout errors in test
                pass
        
        await asyncio.sleep(0.01)


class TestErrorComponent(HarnessComponent):
    """Component that generates errors for testing error handling"""
    
    def __init__(self, name: str, error_on_setup: bool = False, error_on_process: bool = False):
        config = ComponentConfiguration(
            name=name,
            component_type="test_error",
            service_type="error_test",
            base_type="transformer"
        )
        super().__init__(config)
        self.error_on_setup = error_on_setup
        self.error_on_process = error_on_process
        self.process_count = 0
    
    async def _initialize_component_resources(self):
        if self.error_on_setup:
            raise ValueError(f"Intentional setup error in {self.name}")
    
    async def process(self):
        self.process_count += 1
        if self.error_on_process and self.process_count > 2:
            raise ValueError(f"Intentional process error in {self.name}")
        await asyncio.sleep(0.01)


class TestStreamManager:
    """Test StreamManager functionality"""
    
    async def test_stream_creation(self):
        """Test basic stream creation and management"""
        stream_manager = StreamManager(default_buffer_size=50)
        
        # Create streams
        send1, receive1 = stream_manager.create_stream(buffer_size=100, source_component="comp1", target_component="comp2")
        send2, receive2 = stream_manager.create_stream(source_component="comp2", target_component="comp3")
        
        # Verify streams were created
        assert send1 is not None
        assert receive1 is not None
        assert send2 is not None
        assert receive2 is not None
        
        # Check statistics
        stats = stream_manager.get_stream_statistics()
        assert stats["total_created"] == 2
        assert stats["active_count"] == 2
        
        # Test stream communication
        test_message = {"test": "data"}
        await send1.send(test_message)
        received = await receive1.receive()
        assert received == test_message
        
        # Cleanup
        await stream_manager.close_all_streams()
        stats_after = stream_manager.get_stream_statistics()
        assert stats_after["active_count"] == 0
        assert stats_after["total_closed"] == 2
    
    async def test_stream_health_monitoring(self):
        """Test stream health monitoring"""
        stream_manager = StreamManager()
        
        # Create some streams
        for i in range(3):
            stream_manager.create_stream(source_component=f"comp{i}", target_component=f"comp{i+1}")
        
        # Perform health check
        health_result = await stream_manager.health_check_streams()
        
        assert health_result["total_streams"] == 3
        assert health_result["healthy_streams"] >= 0
        assert "health_percentage" in health_result
        
        # Cleanup
        await stream_manager.close_all_streams()


class TestSystemExecutionHarness:
    """Test SystemExecutionHarness functionality"""
    
    async def test_harness_initialization(self):
        """Test harness initialization and configuration"""
        config = HarnessConfiguration(
            startup_timeout=10.0,
            shutdown_timeout=5.0,
            stream_buffer_size=200
        )
        
        harness = SystemExecutionHarness(config)
        
        assert harness.state == HarnessState.CREATED
        assert harness.config.startup_timeout == 10.0
        assert harness.config.stream_buffer_size == 200
        assert not harness.running
        assert len(harness.components) == 0
    
    async def test_component_registration(self):
        """Test component registration and unregistration"""
        harness = SystemExecutionHarness()
        
        # Create test components
        source = TestSourceComponent("source")
        processor = TestProcessorComponent("processor")
        sink = TestSinkComponent("sink")
        
        # Register components
        harness.register_component("source", source, start_priority=1)
        harness.register_component("processor", processor, start_priority=2, dependencies=["source"])
        harness.register_component("sink", sink, start_priority=3, dependencies=["processor"])
        
        assert len(harness.components) == 3
        assert harness.state == HarnessState.CONFIGURED
        assert "source" in harness.components
        assert "processor" in harness.components
        assert "sink" in harness.components
        
        # Test duplicate registration
        with pytest.raises(ComponentAlreadyRegisteredError):
            harness.register_component("source", source)
        
        # Test component info
        comp_info = harness.get_component_info("processor")
        assert comp_info["name"] == "processor"
        assert comp_info["registration"]["dependencies"] == ["source"]
        
        # Test unregistration
        harness.unregister_component("sink")
        assert len(harness.components) == 2
        assert "sink" not in harness.components
    
    async def test_stream_connections(self):
        """Test stream connection setup"""
        harness = SystemExecutionHarness()
        
        source = TestSourceComponent("source")
        sink = TestSinkComponent("sink")
        
        harness.register_component("source", source)
        harness.register_component("sink", sink)
        
        # Create connection
        harness.connect("source.output", "sink.input", buffer_size=150)
        
        assert len(harness.stream_connections) == 1
        
        # Verify streams were added to components
        assert len(source.send_streams) == 1
        assert len(sink.receive_streams) == 1
        assert "output" in source.send_streams
        assert "input" in sink.receive_streams
        
        # Test connection info
        connections = harness.list_connections()
        assert len(connections) == 1
        assert connections[0]["from"] == "source.output"
        assert connections[0]["to"] == "sink.input"
        assert connections[0]["buffer_size"] == 150
    
    async def test_simple_pipeline_execution(self):
        """Test execution of a simple 3-component pipeline"""
        harness = SystemExecutionHarness(
            HarnessConfiguration(
                startup_timeout=5.0,
                shutdown_timeout=2.0,
                health_check_interval=1.0
            )
        )
        
        # Create pipeline: source → processor → sink
        source = TestSourceComponent("source", message_count=3)
        processor = TestProcessorComponent("processor")
        sink = TestSinkComponent("sink")
        
        # Register components
        harness.register_component("source", source, start_priority=1)
        harness.register_component("processor", processor, start_priority=2)
        harness.register_component("sink", sink, start_priority=3)
        
        # Connect pipeline
        harness.connect("source.output", "processor.input")
        harness.connect("processor.output", "sink.input")
        
        # Run pipeline for a short time
        async def run_pipeline():
            await harness.run()
        
        # Start pipeline and let it run
        harness_task = asyncio.create_task(run_pipeline())
        
        # Wait for startup and some processing
        await asyncio.sleep(2.0)
        
        # Stop harness
        await harness.stop()
        
        # Wait for harness task to complete
        try:
            await asyncio.wait_for(harness_task, timeout=5.0)
        except asyncio.TimeoutError:
            harness_task.cancel()
        
        # Verify results
        assert harness.state == HarnessState.STOPPED
        assert len(sink.collected_messages) > 0
        
        # Verify message flow
        for collected in sink.collected_messages:
            message = collected["message"]
            assert "processed_by" in message
            assert message["processed_by"] == "processor"
    
    async def test_dependency_order_startup(self):
        """Test that components start in correct dependency order"""
        harness = SystemExecutionHarness()
        
        # Create components with dependencies
        comp_a = TestSourceComponent("comp_a")
        comp_b = TestProcessorComponent("comp_b")  # depends on comp_a
        comp_c = TestSinkComponent("comp_c")       # depends on comp_b
        
        # Register in random order to test sorting
        harness.register_component("comp_c", comp_c, dependencies=["comp_b"])
        harness.register_component("comp_a", comp_a)
        harness.register_component("comp_b", comp_b, dependencies=["comp_a"])
        
        # Calculate startup order
        startup_order = harness._calculate_startup_order()
        
        # Verify correct order
        assert startup_order.index("comp_a") < startup_order.index("comp_b")
        assert startup_order.index("comp_b") < startup_order.index("comp_c")
    
    async def test_error_handling_during_setup(self):
        """Test error handling during component setup"""
        harness = SystemExecutionHarness()
        
        # Create components, one with setup error
        good_comp = TestSourceComponent("good_comp")
        error_comp = TestErrorComponent("error_comp", error_on_setup=True)
        
        harness.register_component("good_comp", good_comp)
        harness.register_component("error_comp", error_comp)
        
        # Try to run harness - should fail due to setup error
        with pytest.raises(ComponentStartupError):
            await harness.run()
        
        # Verify error tracking
        assert len(harness.startup_errors) > 0
        assert "error_comp" in harness.failed_components
        assert harness.state == HarnessState.ERROR
    
    async def test_component_failure_isolation(self):
        """Test that component failures don't crash the entire harness"""
        harness = SystemExecutionHarness(
            HarnessConfiguration(shutdown_timeout=1.0)
        )
        
        # Create components, one that will fail during processing
        good_comp = TestSourceComponent("good_comp")
        error_comp = TestErrorComponent("error_comp", error_on_process=True)
        
        harness.register_component("good_comp", good_comp)
        harness.register_component("error_comp", error_comp)
        
        # Start harness
        async def run_harness():
            await harness.run()
        
        harness_task = asyncio.create_task(run_harness())
        
        # Let it run and encounter the error
        await asyncio.sleep(1.0)
        
        # Stop harness
        await harness.stop()
        
        try:
            await asyncio.wait_for(harness_task, timeout=3.0)
        except asyncio.TimeoutError:
            harness_task.cancel()
        
        # Verify that the error was tracked but didn't crash everything
        assert len(harness.runtime_errors) > 0 or len(harness.failed_components) > 0
    
    async def test_health_monitoring(self):
        """Test health monitoring functionality"""
        harness = SystemExecutionHarness(
            HarnessConfiguration(
                health_check_interval=0.5,
                enable_health_monitoring=True
            )
        )
        
        source = TestSourceComponent("source")
        harness.register_component("source", source)
        
        # Start harness
        async def run_harness():
            await harness.run()
        
        harness_task = asyncio.create_task(run_harness())
        
        # Let it run and perform health checks
        await asyncio.sleep(1.5)
        
        # Check that health monitoring occurred
        assert harness.last_health_check > 0
        assert "source" in harness.component_health_status
        
        # Stop harness
        await harness.stop()
        
        try:
            await asyncio.wait_for(harness_task, timeout=3.0)
        except asyncio.TimeoutError:
            harness_task.cancel()
    
    async def test_harness_status_reporting(self):
        """Test comprehensive status reporting"""
        harness = SystemExecutionHarness()
        
        source = TestSourceComponent("source")
        sink = TestSinkComponent("sink")
        
        harness.register_component("source", source)
        harness.register_component("sink", sink)
        harness.connect("source.output", "sink.input")
        
        # Get initial status
        status = harness.get_status()
        
        assert status["state"] == "configured"
        assert status["components"]["total"] == 2
        assert status["streams"]["total_connections"] == 1
        assert not status["running"]
        
        # Verify component list
        component_list = harness.list_components()
        assert "source" in component_list
        assert "sink" in component_list
        assert len(component_list) == 2
    
    async def test_concurrent_component_execution(self):
        """Test concurrent execution of multiple independent components"""
        harness = SystemExecutionHarness()
        
        # Create multiple independent sources
        sources = []
        sinks = []
        
        for i in range(3):
            source = TestSourceComponent(f"source_{i}", message_count=2)
            sink = TestSinkComponent(f"sink_{i}")
            
            harness.register_component(f"source_{i}", source)
            harness.register_component(f"sink_{i}", sink)
            harness.connect(f"source_{i}.output", f"sink_{i}.input")
            
            sources.append(source)
            sinks.append(sink)
        
        # Run harness
        async def run_harness():
            await harness.run()
        
        harness_task = asyncio.create_task(run_harness())
        
        # Let it run
        await asyncio.sleep(1.5)
        
        # Stop harness
        await harness.stop()
        
        try:
            await asyncio.wait_for(harness_task, timeout=3.0)
        except asyncio.TimeoutError:
            harness_task.cancel()
        
        # Verify all pipelines processed messages
        for i, sink in enumerate(sinks):
            assert len(sink.collected_messages) > 0, f"Sink {i} should have received messages"


# Test runner function
async def run_all_harness_tests():
    """Run all SystemExecutionHarness tests"""
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": [],
        "details": []
    }
    
    # Test classes and methods
    test_classes = [
        (TestStreamManager, [
            "test_stream_creation",
            "test_stream_health_monitoring"
        ]),
        (TestSystemExecutionHarness, [
            "test_harness_initialization",
            "test_component_registration",
            "test_stream_connections",
            "test_simple_pipeline_execution",
            "test_dependency_order_startup",
            "test_error_handling_during_setup",
            "test_component_failure_isolation", 
            "test_health_monitoring",
            "test_harness_status_reporting",
            "test_concurrent_component_execution"
        ])
    ]
    
    for test_class, test_methods in test_classes:
        test_instance = test_class()
        
        for method_name in test_methods:
            try:
                logger.info(f"🧪 Running {test_class.__name__}.{method_name}")
                
                test_method = getattr(test_instance, method_name)
                await test_method()
                
                test_results["passed"] += 1
                test_results["details"].append(f"✅ {test_class.__name__}.{method_name}")
                logger.info(f"✅ {test_class.__name__}.{method_name} PASSED")
                
            except Exception as e:
                test_results["failed"] += 1
                error_msg = f"❌ {test_class.__name__}.{method_name} FAILED: {e}"
                test_results["errors"].append(error_msg)
                test_results["details"].append(error_msg)
                logger.error(error_msg)
    
    return test_results


if __name__ == "__main__":
    async def main():
        logger.info("🚀 Starting SystemExecutionHarness integration tests")
        
        results = await run_all_harness_tests()
        
        logger.info("📊 Test Results Summary:")
        logger.info(f"   ✅ Passed: {results['passed']}")
        logger.info(f"   ❌ Failed: {results['failed']}")
        total_tests = results['passed'] + results['failed']
        if total_tests > 0:
            logger.info(f"   📈 Success Rate: {results['passed'] / total_tests * 100:.1f}%")
        
        if results["errors"]:
            logger.info("🚨 Failures:")
            for error in results["errors"]:
                logger.info(f"   {error}")
        
        return results
    
    # Run tests
    asyncio.run(main())