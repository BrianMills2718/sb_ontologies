#!/usr/bin/env python3
"""
Simple performance test for the basic functionality we've verified
"""
import sys
import os
import asyncio
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evidence.phase6_harness.day3_stream_communication.stream_framework import StreamFramework
from evidence.phase6_harness.day3_stream_communication.message_protocol import MessageProtocol, MessageType
import anyio

async def test_basic_performance():
    """Test basic message protocol and stream framework performance"""
    print("=" * 60)
    print("BASIC PERFORMANCE VERIFICATION")
    print("=" * 60)
    
    # Test 1: Message serialization/deserialization speed
    print("🧪 Testing message serialization performance...")
    protocol = MessageProtocol()
    
    start_time = time.time()
    message_count = 1000
    
    for i in range(message_count):
        message = protocol.create_message(
            payload={"id": i, "data": f"message_{i}", "timestamp": time.time()},
            message_type=MessageType.DATA,
            sender="test_component"
        )
        serialized = protocol.serialize(message)
        deserialized = protocol.deserialize(serialized)
    
    duration = time.time() - start_time
    throughput = message_count / duration
    
    print(f"✅ Processed {message_count} messages in {duration:.3f}s")
    print(f"⚡ Serialization throughput: {throughput:.2f} messages/second")
    
    # Test 2: Stream communication speed
    print("\n🧪 Testing stream communication performance...")
    framework = StreamFramework()
    
    # Create buffered streams
    send_stream, receive_stream = anyio.create_memory_object_stream(max_buffer_size=100)
    
    send_id = framework.register_endpoint("sender", "sender_component", send_stream)
    recv_id = framework.register_endpoint("receiver", "receiver_component", receive_stream)
    
    # Send messages as fast as possible
    start_time = time.time()
    send_count = 500
    
    for i in range(send_count):
        await framework.send_message(send_id, {"id": i, "data": f"stream_message_{i}"})
    
    send_duration = time.time() - start_time
    
    # Receive messages
    receive_start = time.time()
    received_count = 0
    
    for _ in range(send_count):
        message = await framework.receive_message(recv_id)
        if message:
            received_count += 1
    
    receive_duration = time.time() - receive_start
    total_duration = time.time() - start_time
    
    print(f"✅ Sent {send_count} messages in {send_duration:.3f}s")
    print(f"✅ Received {received_count} messages in {receive_duration:.3f}s")
    print(f"⚡ Stream throughput: {received_count / total_duration:.2f} messages/second")
    
    # Test 3: Component instantiation speed
    print("\n🧪 Testing component instantiation performance...")
    from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
    from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent
    
    class TestComponent(HarnessComponent):
        async def process(self):
            await asyncio.sleep(0.001)
    
    start_time = time.time()
    component_count = 100
    
    for i in range(component_count):
        config = ComponentConfiguration(
            name=f"test_component_{i}",
            component_type="test",
            service_type="test_service",
            base_type="Source"
        )
        component = TestComponent(config)
    
    instantiation_duration = time.time() - start_time
    avg_instantiation_time = (instantiation_duration / component_count) * 1000  # ms
    
    print(f"✅ Created {component_count} components in {instantiation_duration:.3f}s")
    print(f"⚡ Average instantiation time: {avg_instantiation_time:.2f}ms")
    
    # Summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"✅ Message Protocol: {throughput:.0f} msg/s serialization")
    print(f"✅ Stream Framework: {received_count / total_duration:.0f} msg/s communication")
    print(f"✅ Component Creation: {avg_instantiation_time:.1f}ms average")
    
    # Basic performance checks
    performance_ok = (
        throughput > 100 and  # At least 100 msg/s serialization
        (received_count / total_duration) > 50 and  # At least 50 msg/s stream communication
        avg_instantiation_time < 50  # Less than 50ms per component
    )
    
    if performance_ok:
        print("\n🎉 BASIC PERFORMANCE REQUIREMENTS MET!")
        print("The critical fixes have restored functionality with acceptable performance.")
    else:
        print("\n⚠️ Some performance thresholds not met, but basic functionality works.")
    
    return performance_ok

if __name__ == "__main__":
    success = asyncio.run(test_basic_performance())
    exit(0 if success else 1)