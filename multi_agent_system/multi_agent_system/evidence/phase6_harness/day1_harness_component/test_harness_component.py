#!/usr/bin/env python3
"""
Comprehensive Tests for HarnessComponent Base Class
=================================================

Tests all aspects of the HarnessComponent functionality including:
- Lifecycle state transitions
- Stream connection management
- Error handling and recovery
- Concurrent component execution
- Performance metrics and monitoring
"""

import asyncio
import anyio
import pytest
import time
import logging
from typing import Dict, Any, Optional
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
from evidence.phase6_harness.day1_harness_component.harness_component import (
    HarnessComponent, HarnessContext, StreamOperationError
)
from evidence.phase6_harness.day1_harness_component.component_status import (
    ComponentStatus, ComponentState, InvalidStateTransitionError
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestHarnessComponent(HarnessComponent):
    """Test implementation of HarnessComponent"""
    
    def __init__(self, name: str, service_type: str = "test_service"):
        config = ComponentConfiguration(
            name=name,
            component_type="test_component",
            service_type=service_type,
            base_type="transformer"
        )
        super().__init__(config)
        self.processed_messages = []
        self.sent_messages = []
        self.process_delay = 0.01  # Small delay to simulate processing
        self.should_error = False
        self.error_count = 0
    
    async def process(self):
        """Test processing implementation"""
        if self.should_error:
            self.error_count += 1
            raise ValueError(f"Test error #{self.error_count}")
        
        # Check for incoming messages on all receive streams
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    self.processed_messages.append({
                        "stream": stream_name,
                        "message": message,
                        "timestamp": time.time()
                    })
                    
                    # Echo message to first send stream if available
                    if self.send_streams:
                        first_send_stream = list(self.send_streams.keys())[0]
                        processed_msg = {"original": message, "processed_by": self.name}
                        await self.send_message(first_send_stream, processed_msg)
                        self.sent_messages.append(processed_msg)
            except Exception:
                # Ignore timeout errors in test
                pass
        
        # Add processing delay
        await asyncio.sleep(self.process_delay)


class TestDataSource(HarnessComponent):
    """Test data source component"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="data_source",
            service_type="data_source",
            base_type="source"
        )
        super().__init__(config)
        self.messages_to_send = []
        self.current_message_index = 0
    
    def add_test_messages(self, messages):
        """Add messages to send during processing"""
        self.messages_to_send.extend(messages)
    
    async def process(self):
        """Send test messages"""
        if (self.current_message_index < len(self.messages_to_send) and 
            self.send_streams):
            
            message = self.messages_to_send[self.current_message_index]
            first_send_stream = list(self.send_streams.keys())[0]
            
            await self.send_message(first_send_stream, message)
            self.current_message_index += 1
        
        await asyncio.sleep(0.01)


class TestDataSink(HarnessComponent):
    """Test data sink component"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="data_sink", 
            service_type="data_sink",
            base_type="sink"
        )
        super().__init__(config)
        self.received_messages = []
    
    async def process(self):
        """Receive and store messages"""
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    self.received_messages.append({
                        "stream": stream_name,
                        "message": message,
                        "timestamp": time.time()
                    })
            except Exception:
                # Ignore timeout errors in test
                pass
        
        await asyncio.sleep(0.01)


class TestComponentStatus:
    """Test ComponentStatus functionality"""
    
    def test_component_status_initialization(self):
        """Test ComponentStatus initialization"""
        status = ComponentStatus("test_component")
        
        assert status.name == "test_component"
        assert status.state == ComponentState.CREATED
        assert status.is_healthy == False  # CREATED is not healthy
        assert status.error_count == 0
        assert status.recovery_attempts == 0
    
    async def test_valid_state_transitions(self):
        """Test valid state transitions"""
        status = ComponentStatus("test_component")
        
        # CREATED -> READY
        result = await status.transition_to(ComponentState.READY)
        assert result == True
        assert status.state == ComponentState.READY
        assert status.is_healthy == True
        
        # READY -> RUNNING
        await status.transition_to(ComponentState.RUNNING)
        assert status.state == ComponentState.RUNNING
        assert status.is_running == True
        
        # RUNNING -> STOPPING
        await status.transition_to(ComponentState.STOPPING)
        assert status.state == ComponentState.STOPPING
        
        # STOPPING -> STOPPED
        await status.transition_to(ComponentState.STOPPED)
        assert status.state == ComponentState.STOPPED
        assert status.is_stopped == True
    
    async def test_invalid_state_transitions(self):
        """Test invalid state transitions raise errors"""
        status = ComponentStatus("test_component")
        
        # Cannot go from CREATED directly to RUNNING
        with pytest.raises(InvalidStateTransitionError):
            await status.transition_to(ComponentState.RUNNING)
        
        # Cannot go from CREATED to STOPPED
        with pytest.raises(InvalidStateTransitionError):
            await status.transition_to(ComponentState.STOPPED)
    
    async def test_error_handling(self):
        """Test error recording and recovery"""
        status = ComponentStatus("test_component")
        await status.transition_to(ComponentState.READY)
        
        # Record an error
        test_error = ValueError("Test error")
        await status.record_error(test_error)
        
        assert status.error_count == 1
        assert status.last_error == test_error
        assert status.state == ComponentState.ERROR
        
        # Test recovery
        recovery_result = await status.attempt_recovery()
        assert recovery_result == True
        assert status.state == ComponentState.READY
        assert status.recovery_attempts == 1
    
    def test_status_summary(self):
        """Test status summary generation"""
        status = ComponentStatus("test_component")
        summary = status.get_status_summary()
        
        assert summary["name"] == "test_component"
        assert summary["state"] == "created"
        assert "metrics" in summary
        assert "recent_transitions" in summary
        
        health_report = status.get_health_report()
        assert health_report["component"] == "test_component"
        assert "healthy" in health_report
        assert "performance" in health_report


class TestHarnessComponentLifecycle:
    """Test HarnessComponent lifecycle management"""
    
    async def test_component_initialization(self):
        """Test component initialization"""
        component = TestHarnessComponent("test_comp")
        
        assert component.name == "test_comp"
        assert component.service_type == "test_service"
        assert component.current_state == ComponentState.CREATED
        assert not component.is_running
        assert not component._processing_active
    
    async def test_component_setup(self):
        """Test component setup process"""
        component = TestHarnessComponent("test_comp")
        
        # Create test harness context
        context = HarnessContext(
            harness_id="test_harness",
            component_registry={"test_comp": component},
            global_config={"test": True}
        )
        
        await component.setup(context)
        
        assert component.current_state == ComponentState.READY
        assert component.harness_context == context
        assert component.is_healthy
    
    async def test_stream_management(self):
        """Test stream addition and management"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        # Create test streams
        send_stream, receive_stream = anyio.create_memory_object_stream()
        
        # Add streams to component
        component.add_send_stream("output", send_stream, "target_comp")
        component.add_receive_stream("input", receive_stream, "source_comp")
        
        assert "output" in component.send_streams
        assert "input" in component.receive_streams
        
        stream_info = component.get_stream_info()
        assert len(stream_info["send_streams"]) == 1
        assert len(stream_info["receive_streams"]) == 1
        assert stream_info["send_streams"]["output"]["connected_to"] == "target_comp"
    
    async def test_message_sending_receiving(self):
        """Test message sending and receiving"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        # Create stream pair
        send_stream, receive_stream = anyio.create_memory_object_stream()
        
        component.add_send_stream("output", send_stream)
        component.add_receive_stream("input", receive_stream)
        
        # Send message
        test_message = {"data": "test", "value": 42}
        result = await component.send_message("output", test_message)
        assert result == True
        
        # Receive message
        received = await component.receive_message("input", timeout=1.0)
        assert received == test_message
        
        # Check metrics
        assert component._status.metrics.total_messages_sent == 1
    
    async def test_processing_lifecycle(self):
        """Test component processing start/stop"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        # Start processing
        await component.start_processing()
        assert component.is_running
        assert component._processing_active
        
        # Let it process for a bit
        await asyncio.sleep(0.1)
        
        # Stop processing
        await component.stop_processing()
        assert not component._processing_active
        assert component.current_state == ComponentState.STOPPING
    
    async def test_error_handling_in_processing(self):
        """Test error handling during processing"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        # Configure component to generate errors
        component.should_error = True
        
        # Start processing
        await component.start_processing()
        
        # Let it process and generate errors
        await asyncio.sleep(0.2)
        
        # Component should still be running but with errors recorded
        assert component._status.error_count > 0
        assert component.consecutive_errors > 0
        
        # Stop processing
        await component.stop_processing()
    
    async def test_cleanup(self):
        """Test component cleanup"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        # Add streams
        send_stream, receive_stream = anyio.create_memory_object_stream()
        component.add_send_stream("output", send_stream)
        component.add_receive_stream("input", receive_stream)
        
        # Start and then cleanup
        await component.start_processing()
        await asyncio.sleep(0.05)
        await component.cleanup()
        
        assert component.current_state == ComponentState.STOPPED
        assert not component._processing_active
        assert len(component.send_streams) == 0
        assert len(component.receive_streams) == 0
    
    async def test_health_check(self):
        """Test health check functionality"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        health = await component.health_check()
        
        assert health["component"] == "test_comp"
        assert health["healthy"] == True
        assert health["state"] == "ready"
        assert "stream_connections" in health
        assert "performance" in health
    
    async def test_performance_metrics(self):
        """Test performance metrics collection"""
        component = TestHarnessComponent("test_comp")
        await component.setup()
        
        # Add streams and send messages
        send_stream, receive_stream = anyio.create_memory_object_stream()
        component.add_send_stream("output", send_stream)
        
        # Send multiple messages
        for i in range(5):
            await component.send_message("output", f"message_{i}")
        
        metrics = component.get_performance_metrics()
        
        assert metrics["component"] == "test_comp"
        assert metrics["processing_metrics"]["total_sent"] == 5
        assert "stream_metrics" in metrics
        assert "error_metrics" in metrics


class TestComponentCommunication:
    """Test communication between multiple components"""
    
    async def test_two_component_communication(self):
        """Test communication between two components"""
        # Create components
        source = TestDataSource("source")
        sink = TestDataSink("sink")
        
        # Setup components
        await source.setup()
        await sink.setup()
        
        # Create communication stream
        send_stream, receive_stream = anyio.create_memory_object_stream()
        source.add_send_stream("output", send_stream, "sink")
        sink.add_receive_stream("input", receive_stream, "source")
        
        # Add test messages to source
        test_messages = ["msg1", "msg2", "msg3"]
        source.add_test_messages(test_messages)
        
        # Start both components
        await source.start_processing()
        await sink.start_processing()
        
        # Let them communicate
        await asyncio.sleep(0.2)
        
        # Stop components
        await source.stop_processing()
        await sink.stop_processing()
        
        # Verify communication
        assert len(sink.received_messages) == len(test_messages)
        received_data = [msg["message"] for msg in sink.received_messages]
        assert received_data == test_messages
        
        # Cleanup
        await source.cleanup()
        await sink.cleanup()
    
    async def test_three_component_pipeline(self):
        """Test a pipeline of three components"""
        # Create components
        source = TestDataSource("source")
        processor = TestHarnessComponent("processor", "processor")
        sink = TestDataSink("sink")
        
        # Setup components
        await source.setup()
        await processor.setup()
        await sink.setup()
        
        # Create pipeline streams
        # source -> processor
        send1, receive1 = anyio.create_memory_object_stream()
        source.add_send_stream("output", send1, "processor")
        processor.add_receive_stream("input", receive1, "source")
        
        # processor -> sink
        send2, receive2 = anyio.create_memory_object_stream()
        processor.add_send_stream("output", send2, "sink")
        sink.add_receive_stream("input", receive2, "processor")
        
        # Add test messages
        test_messages = ["pipeline_msg1", "pipeline_msg2"]
        source.add_test_messages(test_messages)
        
        # Start all components
        await source.start_processing()
        await processor.start_processing()
        await sink.start_processing()
        
        # Let pipeline process
        await asyncio.sleep(0.3)
        
        # Stop all components
        await source.stop_processing()
        await processor.stop_processing()
        await sink.stop_processing()
        
        # Verify pipeline processing
        assert len(processor.processed_messages) > 0
        assert len(processor.sent_messages) > 0
        assert len(sink.received_messages) > 0
        
        # Verify data transformation through pipeline
        for received in sink.received_messages:
            assert "original" in received["message"]
            assert received["message"]["processed_by"] == "processor"
        
        # Cleanup
        await source.cleanup()
        await processor.cleanup()
        await sink.cleanup()


class TestConcurrentExecution:
    """Test concurrent execution of multiple components"""
    
    async def test_concurrent_component_execution(self):
        """Test multiple components running concurrently"""
        # Create multiple components
        components = []
        for i in range(3):
            comp = TestHarnessComponent(f"comp_{i}")
            await comp.setup()
            components.append(comp)
        
        # Start all components concurrently
        start_tasks = []
        for comp in components:
            start_tasks.append(asyncio.create_task(comp.start_processing()))
        
        await asyncio.gather(*start_tasks)
        
        # Verify all are running
        for comp in components:
            assert comp.is_running
            assert comp._processing_active
        
        # Let them run concurrently
        await asyncio.sleep(0.1)
        
        # Stop all components
        stop_tasks = []
        for comp in components:
            stop_tasks.append(asyncio.create_task(comp.stop_processing()))
        
        await asyncio.gather(*stop_tasks)
        
        # Cleanup
        cleanup_tasks = []
        for comp in components:
            cleanup_tasks.append(asyncio.create_task(comp.cleanup()))
        
        await asyncio.gather(*cleanup_tasks)
        
        # Verify all stopped
        for comp in components:
            assert comp.current_state == ComponentState.STOPPED
    
    async def test_component_failure_isolation(self):
        """Test that component failures don't affect others"""
        # Create components
        good_comp = TestHarnessComponent("good_comp")
        bad_comp = TestHarnessComponent("bad_comp")
        
        await good_comp.setup()
        await bad_comp.setup()
        
        # Configure bad component to error
        bad_comp.should_error = True
        
        # Start both
        await good_comp.start_processing()
        await bad_comp.start_processing()
        
        # Let them run
        await asyncio.sleep(0.2)
        
        # Good component should still be healthy
        assert good_comp.is_healthy
        assert good_comp.is_running
        assert good_comp._status.error_count == 0
        
        # Bad component should have errors but still be managed
        assert bad_comp._status.error_count > 0
        assert bad_comp.consecutive_errors > 0
        
        # Stop both
        await good_comp.stop_processing()
        await bad_comp.stop_processing()
        
        # Cleanup
        await good_comp.cleanup()
        await bad_comp.cleanup()


# Test runner function
async def run_all_tests():
    """Run all tests and collect results"""
    test_results = {
        "passed": 0,
        "failed": 0,
        "errors": [],
        "details": []
    }
    
    # Test classes and their methods
    test_classes = [
        (TestComponentStatus, [
            "test_component_status_initialization",
            "test_valid_state_transitions", 
            "test_invalid_state_transitions",
            "test_error_handling",
            "test_status_summary"
        ]),
        (TestHarnessComponentLifecycle, [
            "test_component_initialization",
            "test_component_setup",
            "test_stream_management",
            "test_message_sending_receiving",
            "test_processing_lifecycle",
            "test_error_handling_in_processing",
            "test_cleanup",
            "test_health_check",
            "test_performance_metrics"
        ]),
        (TestComponentCommunication, [
            "test_two_component_communication",
            "test_three_component_pipeline"
        ]),
        (TestConcurrentExecution, [
            "test_concurrent_component_execution",
            "test_component_failure_isolation"
        ])
    ]
    
    for test_class, test_methods in test_classes:
        test_instance = test_class()
        
        for method_name in test_methods:
            try:
                logger.info(f"🧪 Running {test_class.__name__}.{method_name}")
                
                test_method = getattr(test_instance, method_name)
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()
                
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
        logger.info("🚀 Starting HarnessComponent comprehensive tests")
        
        results = await run_all_tests()
        
        logger.info("📊 Test Results Summary:")
        logger.info(f"   ✅ Passed: {results['passed']}")
        logger.info(f"   ❌ Failed: {results['failed']}")
        logger.info(f"   📈 Success Rate: {results['passed'] / (results['passed'] + results['failed']) * 100:.1f}%")
        
        if results["errors"]:
            logger.info("🚨 Failures:")
            for error in results["errors"]:
                logger.info(f"   {error}")
        
        return results
    
    # Run tests
    asyncio.run(main())