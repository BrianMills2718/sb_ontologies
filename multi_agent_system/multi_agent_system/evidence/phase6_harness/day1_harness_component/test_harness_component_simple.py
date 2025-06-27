#!/usr/bin/env python3
"""
Simplified Tests for HarnessComponent and ComponentStatus

Focused on critical functionality without hanging async operations.
"""

import time
import logging
from typing import Any, Dict

from harness_component import HarnessComponent
from component_status import ComponentStatus, InvalidStateTransition, ComponentState


class SimpleTestableComponent(HarnessComponent):
    """Simple testable implementation of HarnessComponent"""
    
    async def process(self):
        """Simple process implementation for testing"""
        # Transition to running state
        self._harness_status.transition_to("running")
        
        # Do minimal work
        self._message_count = 10
        await self._wait_for_shutdown()
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown signal"""
        import anyio
        for _ in range(10):  # Max iterations to prevent hanging
            if self.should_shutdown():
                break
            await anyio.sleep(0.01)


def test_component_status():
    """Test ComponentStatus functionality"""
    print("Testing ComponentStatus...")
    
    # Test initial state
    status = ComponentStatus()
    assert status.state == "created"
    assert status.is_healthy()
    assert not status.is_running()
    print("✓ Initial state correct")
    
    # Test valid transitions
    status.transition_to("ready")
    assert status.state == "ready"
    assert status.can_start()
    
    status.transition_to("running")
    assert status.state == "running"
    assert status.is_running()
    
    status.transition_to("stopping")
    assert status.state == "stopping"
    
    status.transition_to("stopped")
    assert status.state == "stopped"
    assert status.is_stopped()
    print("✓ Valid transitions work")
    
    # Test invalid transitions
    status = ComponentStatus()
    try:
        status.transition_to("running")  # Invalid: created -> running
        assert False, "Should have raised InvalidStateTransition"
    except InvalidStateTransition:
        pass
    print("✓ Invalid transitions properly rejected")
    
    # Test error handling
    status = ComponentStatus()
    status.transition_to("ready")
    
    status.record_error("Test error")
    assert status.error_count == 1
    assert status.last_error == "Test error"
    assert status.is_healthy()  # Still healthy with few errors
    
    # Record many errors
    for i in range(15):
        status.record_error(f"Error {i}")
    
    assert status.state == "error"
    assert not status.is_healthy()
    print("✓ Error handling works correctly")
    
    # Test transition history
    status = ComponentStatus()
    status.transition_to("ready", "Setup complete")
    status.transition_to("running", "Starting process")
    
    history = status.get_transition_history()
    assert len(history) >= 3  # Including initial state
    assert history[1].reason == "Setup complete"
    print("✓ Transition history tracked")
    
    print("ComponentStatus tests: ALL PASSED")
    return True


def test_harness_component_basic():
    """Test basic HarnessComponent functionality"""
    print("\nTesting HarnessComponent...")
    
    # Test component creation
    component = SimpleTestableComponent("test_component", {"test": True})
    assert component.name == "test_component"
    assert component.config["test"] is True
    assert component.get_harness_status().state == "created"
    print("✓ Component creation works")
    
    # Test performance metrics
    component._message_count = 100
    component._error_count = 5
    component._start_time = time.time() - 10  # 10 seconds ago
    
    metrics = component.get_performance_metrics()
    assert metrics["message_count"] == 100
    assert metrics["error_count"] == 5
    assert metrics["uptime_seconds"] > 0
    assert metrics["error_rate"] == 0.05
    print("✓ Performance metrics work")
    
    # Test stream connections
    import anyio
    send_stream, receive_stream = anyio.create_memory_object_stream()
    
    component.connect_output_stream("output", send_stream)
    component.connect_input_stream("input", receive_stream)
    
    assert "output" in component.send_streams
    assert "input" in component.receive_streams
    print("✓ Stream connections work")
    
    # Test duplicate connection error
    try:
        component.connect_output_stream("output", send_stream)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("✓ Duplicate connection detection works")
    
    print("HarnessComponent basic tests: ALL PASSED")
    return True


async def test_harness_component_async():
    """Test async HarnessComponent functionality"""
    print("\nTesting HarnessComponent async functionality...")
    
    component = SimpleTestableComponent("test_component", {"test": True})
    
    # Test setup
    await component.setup()
    assert component.get_harness_status().state == "ready"
    assert component._start_time is not None
    print("✓ Component setup works")
    
    # Test health check
    is_healthy = await component.health_check()
    assert is_healthy
    print("✓ Health check works")
    
    # Test cleanup
    await component.cleanup()
    assert component.get_harness_status().state == "stopped"
    assert component._cleanup_complete
    print("✓ Component cleanup works")
    
    print("HarnessComponent async tests: ALL PASSED")
    return True


async def test_simple_pipeline():
    """Test a simple component pipeline"""
    print("\nTesting simple component pipeline...")
    
    import anyio
    from harness_component import DataGeneratorComponent, DataSinkComponent
    
    # Create components with small counts to avoid hanging
    generator = DataGeneratorComponent("gen", {"count": 3, "interval": 0.01})
    sink = DataSinkComponent("sink", {})
    
    # Connect them
    send_stream, receive_stream = anyio.create_memory_object_stream()
    generator.connect_output_stream("output", send_stream)
    sink.connect_input_stream("input", receive_stream)
    
    # Setup
    await generator.setup()
    await sink.setup()
    
    # Run briefly
    async with anyio.create_task_group() as tg:
        tg.start_soon(generator.run_process_with_lifecycle)
        tg.start_soon(sink.run_process_with_lifecycle)
    
    # Cleanup
    await generator.cleanup()
    await sink.cleanup()
    
    # Check results
    assert len(sink.received_items) == 3
    print(f"✓ Pipeline processed {len(sink.received_items)} items")
    
    print("Simple pipeline test: PASSED")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("HARNESS COMPONENT TESTS - EXECUTION LOG")
    print("=" * 60)
    print(f"Test execution started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configure logging to reduce noise
    logging.basicConfig(level=logging.WARNING)
    
    test_results = []
    
    try:
        # Test ComponentStatus
        result = test_component_status()
        test_results.append(("ComponentStatus", "PASS" if result else "FAIL"))
    except Exception as e:
        print(f"✗ ComponentStatus tests failed: {e}")
        test_results.append(("ComponentStatus", "FAIL"))
    
    try:
        # Test HarnessComponent basic
        result = test_harness_component_basic()
        test_results.append(("HarnessComponent.basic", "PASS" if result else "FAIL"))
    except Exception as e:
        print(f"✗ HarnessComponent basic tests failed: {e}")
        test_results.append(("HarnessComponent.basic", "FAIL"))
        import traceback
        traceback.print_exc()
    
    # Async tests
    import anyio
    
    try:
        result = anyio.run(test_harness_component_async)
        test_results.append(("HarnessComponent.async", "PASS" if result else "FAIL"))
    except Exception as e:
        print(f"✗ HarnessComponent async tests failed: {e}")
        test_results.append(("HarnessComponent.async", "FAIL"))
        import traceback
        traceback.print_exc()
    
    try:
        result = anyio.run(test_simple_pipeline)
        test_results.append(("Pipeline.simple", "PASS" if result else "FAIL"))
    except Exception as e:
        print(f"✗ Simple pipeline test failed: {e}")
        test_results.append(("Pipeline.simple", "FAIL"))
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results if r[1] == "PASS"])
    failed_tests = total_tests - passed_tests
    
    for test_name, result in test_results:
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    print()
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! HarnessComponent implementation is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.")
    
    print(f"\nTest execution completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return test_results


if __name__ == "__main__":
    import anyio
    main()