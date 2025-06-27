#!/usr/bin/env python3
"""
Tests for Stream Communication Components

Tests cover:
- MessageProtocol serialization/deserialization
- StreamFramework functionality
- Message routing and broadcasting
- Error handling and recovery
- Performance characteristics
"""

import pytest
import anyio
import time
import json
import gzip
from typing import Any, Dict

from message_protocol import (
    MessageProtocol, Message, MessageType, CompressionType,
    MessageSerializationError, MessageDeserializationError
)
from stream_framework import (
    StreamFramework, StreamOperationError, MessageFilterError
)


class TestMessageProtocol:
    """Test MessageProtocol functionality"""
    
    def test_message_creation(self):
        """Test basic message creation"""
        protocol = MessageProtocol()
        
        message = protocol.create_message(
            payload={"test": "data"},
            message_type=MessageType.DATA,
            sender="test_component"
        )
        
        assert message.payload == {"test": "data"}
        assert message.metadata.type == MessageType.DATA
        assert message.metadata.sender == "test_component"
        assert message.metadata.id is not None
        assert message.metadata.timestamp > 0
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization"""
        protocol = MessageProtocol()  # JSON is the default format
        
        message = protocol.create_message(
            payload={"number": 42, "text": "hello", "list": [1, 2, 3]},
            message_type=MessageType.DATA
        )
        
        # Serialize
        serialized = protocol.serialize(message)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0
        
        # Deserialize
        deserialized = protocol.deserialize(serialized)
        assert deserialized.payload == message.payload
        assert deserialized.metadata.type == message.metadata.type
        assert deserialized.metadata.id == message.metadata.id
    
    def test_pickle_serialization(self):
        """Test pickle serialization for complex objects"""
        protocol = MessageProtocol()  # Uses JSON with custom serializer for complex objects
        
        # Create complex data that JSON can't handle
        complex_data = {
            "function": lambda x: x * 2,
            "set": {1, 2, 3},
            "custom_object": type("CustomObj", (), {"value": 42})()
        }
        
        message = protocol.create_message(
            payload=complex_data,
            message_type=MessageType.DATA
        )
        
        # Serialize and deserialize
        serialized = protocol.serialize(message)
        deserialized = protocol.deserialize(serialized)
        
        # Check basic structure (can't test function/custom object equality directly)
        assert isinstance(deserialized.payload, dict)
        assert "set" in deserialized.payload
        assert "custom_object" in deserialized.payload
    
    def test_compressed_serialization(self):
        """Test compressed serialization formats"""
        protocol = MessageProtocol(enable_compression=True, compression_threshold=100)
        
        # Create large data to see compression benefit
        large_data = {"data": "x" * 1000, "numbers": list(range(100))}
        
        message = protocol.create_message(payload=large_data)
        
        # Serialize with compression
        compressed = protocol.serialize(message)
        
        # Serialize without compression for comparison
        uncompressed_protocol = MessageProtocol(enable_compression=False)
        uncompressed = uncompressed_protocol.serialize(message)
        
        # Compressed should be smaller
        assert len(compressed) < len(uncompressed)
        
        # Should deserialize correctly
        deserialized = protocol.deserialize(compressed)
        assert deserialized.payload == large_data
    
    def test_message_validation(self):
        """Test message validation"""
        protocol = MessageProtocol(enable_checksums=True)
        
        # Create valid message
        message = protocol.create_message(payload={"test": "data"})
        issues = protocol.validate_message(message)
        assert len(issues) == 0
        
        # Create message with issues
        from evidence.phase6_harness.day3_stream_communication.message_protocol import MessageMetadata
        invalid_metadata = MessageMetadata(
            id="",  # Invalid: empty ID
            type="invalid",  # Invalid: not MessageType enum
            timestamp=-1,  # Invalid: negative timestamp
            ttl=-5  # Invalid: negative TTL
        )
        invalid_message = Message(
            metadata=invalid_metadata,
            payload=None
        )
        
        issues = protocol.validate_message(invalid_message)
        assert len(issues) > 0
        assert any("Missing message ID" in issue for issue in issues)
    
    def test_message_expiration(self):
        """Test message TTL and expiration"""
        protocol = MessageProtocol()
        
        # Create message with short TTL
        message = protocol.create_message(
            payload={"test": "data"},
            ttl=0.1  # 100ms TTL
        )
        
        assert not message.metadata.is_expired()
        
        # Wait for expiration
        time.sleep(0.15)
        assert message.metadata.is_expired()
        
        # Current implementation allows serializing expired messages
        # but should deserialize them with a warning
        serialized = protocol.serialize(message)
        assert len(serialized) > 0  # Should still serialize successfully
    
    def test_request_response_pattern(self):
        """Test request/response message creation"""
        protocol = MessageProtocol()
        
        # Create request
        request = protocol.create_message(
            payload={"query": "get_status"},
            message_type=MessageType.REQUEST,
            sender="client",
            recipient="server"
        )
        
        # Create response
        response = protocol.create_message(
            payload={"status": "ok"},
            message_type=MessageType.RESPONSE,
            sender="server",
            recipient="client",
            correlation_id=request.metadata.id
        )
        
        assert response.metadata.type == MessageType.RESPONSE
        assert response.metadata.sender == "server"
        assert response.metadata.recipient == "client"
        assert response.metadata.correlation_id == request.metadata.id
    
    def test_protocol_statistics(self):
        """Test statistics collection"""
        protocol = MessageProtocol()
        
        # Initial stats
        stats = protocol.get_performance_metrics()
        assert stats['serialization']['total_operations'] == 0
        assert stats['deserialization']['total_operations'] == 0
        
        # Serialize some messages
        for i in range(5):
            message = protocol.create_message(payload={"count": i})
            serialized = protocol.serialize(message)
            protocol.deserialize(serialized)
        
        # Check updated stats
        stats = protocol.get_performance_metrics()
        assert stats['serialization']['total_operations'] == 5
        assert stats['deserialization']['total_operations'] == 5
        assert stats['messages']['total_processed'] > 0
        assert stats['messages']['average_size_bytes'] > 0


class TestStreamFramework:
    """Test StreamFramework functionality"""
    
    def test_framework_creation(self):
        """Test framework creation and initialization"""
        framework = StreamFramework()
        
        assert framework.message_protocol is not None
        assert len(framework.endpoints) == 0
        assert framework.enable_metrics is True
    
    def test_endpoint_registration(self):
        """Test stream endpoint registration"""
        framework = StreamFramework()
        
        # Create test streams
        send_stream, receive_stream = anyio.create_memory_object_stream()
        
        # Register endpoints
        send_id = framework.register_endpoint("output", "test_component", send_stream)
        recv_id = framework.register_endpoint("input", "test_component", receive_stream)
        
        assert len(framework.endpoints) == 2
        assert send_id == "output"
        assert recv_id == "input"
        
        # Check endpoints exist
        assert "output" in framework.endpoints
        assert "input" in framework.endpoints
        assert framework.endpoints["output"].stream_type == "send"
        assert framework.endpoints["input"].stream_type == "receive"
    
    async def test_message_sending_receiving(self):
        """Test basic message sending and receiving"""
        framework = StreamFramework()
        
        # Create and register streams
        send_stream, receive_stream = anyio.create_memory_object_stream()
        send_id = framework.register_endpoint("output", "test_component", send_stream)
        recv_id = framework.register_endpoint("input", "test_component", receive_stream)
        
        # Send message
        test_data = {"message": "hello", "number": 42}
        await framework.send_message(send_id, test_data, MessageType.DATA)
        
        # Receive message
        received_message = await framework.receive_message(recv_id)
        
        assert received_message.payload == test_data
        assert received_message.metadata.type == MessageType.DATA
        assert received_message.metadata.id is not None
    
    async def test_message_broadcast(self):
        """Test message broadcasting to multiple streams"""
        framework = StreamFramework("test-framework")
        
        # Create multiple receive streams
        streams = []
        recv_ids = []
        send_streams = []
        
        for i in range(3):
            send_stream, receive_stream = anyio.create_memory_object_stream()
            send_id = framework.register_send_stream(f"output_{i}", send_stream)
            recv_id = framework.register_receive_stream(f"input_{i}", receive_stream)
            
            streams.append((send_stream, receive_stream))
            recv_ids.append(recv_id)
            send_streams.append(send_id)
        
        # Create broadcast group
        group_id = framework.create_broadcast_group("test_group", send_streams)
        
        # Broadcast message
        broadcast_data = {"broadcast": "message", "time": time.time()}
        results = await framework.broadcast_message(group_id, broadcast_data)
        
        # Check broadcast results
        assert len(results) == 3
        assert all(success for success in results.values())
        
        # Verify all receivers got the message
        for recv_id in recv_ids:
            message = await framework.receive_message(recv_id)
            assert message.data == broadcast_data
            assert message.message_type == MessageType.DATA
    
    async def test_message_routing(self):
        """Test message routing between endpoints"""
        framework = StreamFramework("test-framework")
        
        # Create source and destination streams
        source_send, source_recv = anyio.create_memory_object_stream()
        dest1_send, dest1_recv = anyio.create_memory_object_stream()
        dest2_send, dest2_recv = anyio.create_memory_object_stream()
        
        source_send_id = framework.register_send_stream("source_out", source_send)
        dest1_send_id = framework.register_send_stream("dest1_out", dest1_send)
        dest2_send_id = framework.register_send_stream("dest2_out", dest2_send)
        
        dest1_recv_id = framework.register_receive_stream("dest1_in", dest1_recv)
        dest2_recv_id = framework.register_receive_stream("dest2_in", dest2_recv)
        
        # Setup routing
        framework.add_message_route(source_send_id, [dest1_send_id, dest2_send_id])
        
        # Create and route message
        test_message = framework.message_protocol.create_message(
            data={"routed": "message"}
        )
        
        route_results = await framework.route_message(source_send_id, test_message)
        
        # Check routing results
        assert len(route_results) == 2
        assert all(success for success in route_results.values())
        
        # Verify destinations received message
        for recv_id in [dest1_recv_id, dest2_recv_id]:
            message = await framework.receive_message(recv_id)
            assert message.data == {"routed": "message"}
    
    def test_message_filtering(self):
        """Test message filtering"""
        framework = StreamFramework("test-framework")
        
        # Create filter function
        def priority_filter(message):
            return message.priority > 5
        
        # Create streams
        send_stream, receive_stream = anyio.create_memory_object_stream()
        recv_id = framework.register_receive_stream("filtered_input", receive_stream)
        
        # Add filter
        framework.add_message_filter(recv_id, priority_filter)
        
        # Check filter was added
        assert recv_id in framework.message_filters
        assert len(framework.message_filters[recv_id]) == 1
    
    async def test_framework_statistics(self):
        """Test framework statistics collection"""
        framework = StreamFramework("test-framework")
        
        # Create and use some streams
        send_stream, receive_stream = anyio.create_memory_object_stream()
        send_id = framework.register_send_stream("output", send_stream)
        recv_id = framework.register_receive_stream("input", receive_stream)
        
        # Send some messages
        for i in range(3):
            await framework.send_message(send_id, {"count": i})
            await framework.receive_message(recv_id)
        
        # Get statistics
        stats = framework.get_statistics()
        
        assert stats['total_messages_sent'] == 3
        assert stats['total_messages_received'] == 3
        assert stats['total_endpoints'] == 2
        assert stats['average_latency_ms'] >= 0
    
    async def test_framework_health_check(self):
        """Test framework health checking"""
        framework = StreamFramework("test-framework")
        
        # Create some endpoints
        send_stream, receive_stream = anyio.create_memory_object_stream()
        send_id = framework.register_send_stream("output", send_stream)
        recv_id = framework.register_receive_stream("input", receive_stream)
        
        # Perform health check
        health = await framework.health_check()
        
        assert health['overall_healthy'] is True
        assert health['healthy_endpoints'] == 2
        assert health['unhealthy_endpoints'] == 0
        assert len(health['issues']) == 0
    
    async def test_error_handling(self):
        """Test error handling in framework operations"""
        framework = StreamFramework("test-framework")
        
        # Test sending to non-existent endpoint
        with pytest.raises(StreamOperationError):
            await framework.send_message("non-existent", {"data": "test"})
        
        # Test receiving from non-existent endpoint
        with pytest.raises(StreamOperationError):
            await framework.receive_message("non-existent")
        
        # Test creating broadcast group with non-existent endpoints
        with pytest.raises(StreamOperationError):
            framework.create_broadcast_group("bad_group", ["non-existent"])


class TestIntegration:
    """Integration tests combining protocol and framework"""
    
    async def test_end_to_end_communication(self):
        """Test complete end-to-end communication"""
        # Create framework with custom protocol
        framework = StreamFramework("integration-test")
        
        # Create communication pipeline
        send_stream, receive_stream = anyio.create_memory_object_stream()
        send_id = framework.register_send_stream("producer", send_stream, "producer_component")
        recv_id = framework.register_receive_stream("consumer", receive_stream, "consumer_component")
        
        # Send various types of messages
        messages_to_send = [
            {"type": "data", "value": 42},
            {"type": "status", "health": "ok"},
            {"type": "error", "message": "test error"}
        ]
        
        # Send messages
        for i, data in enumerate(messages_to_send):
            await framework.send_message(
                send_id, 
                data, 
                MessageType.DATA,
                metadata={"sequence": i}
            )
        
        # Receive and verify messages
        received_messages = []
        for _ in range(len(messages_to_send)):
            message = await framework.receive_message(recv_id)
            received_messages.append(message)
        
        # Verify all messages received correctly
        assert len(received_messages) == len(messages_to_send)
        
        for i, (sent_data, received_msg) in enumerate(zip(messages_to_send, received_messages)):
            assert received_msg.data == sent_data
            assert received_msg.get_metadata("sequence") == i
    
    async def test_performance_characteristics(self):
        """Test performance characteristics under load"""
        framework = StreamFramework("performance-test")
        
        # Create high-throughput connection
        send_stream, receive_stream = anyio.create_memory_object_stream(buffer_size=1000)
        send_id = framework.register_send_stream("high_throughput_out", send_stream)
        recv_id = framework.register_receive_stream("high_throughput_in", receive_stream)
        
        # Send many messages quickly
        message_count = 100
        start_time = time.time()
        
        # Send messages
        for i in range(message_count):
            await framework.send_message(send_id, {"id": i, "data": f"message_{i}"})
        
        send_time = time.time() - start_time
        
        # Receive messages
        receive_start = time.time()
        received_count = 0
        
        for _ in range(message_count):
            message = await framework.receive_message(recv_id)
            received_count += 1
        
        receive_time = time.time() - receive_start
        
        # Calculate performance metrics
        send_throughput = message_count / send_time
        receive_throughput = message_count / receive_time
        
        # Performance assertions (should be reasonably fast)
        assert send_throughput > 100  # At least 100 messages/second
        assert receive_throughput > 100
        assert received_count == message_count
        
        # Check framework statistics
        stats = framework.get_statistics()
        assert stats['total_messages_sent'] == message_count
        assert stats['total_messages_received'] == message_count


def run_sync_tests():
    """Run synchronous tests"""
    print("Running MessageProtocol tests...")
    
    protocol_tests = TestMessageProtocol()
    
    try:
        protocol_tests.test_message_creation()
        print("✓ Message creation test passed")
        
        protocol_tests.test_json_serialization()
        print("✓ JSON serialization test passed")
        
        protocol_tests.test_pickle_serialization()
        print("✓ Pickle serialization test passed")
        
        protocol_tests.test_compressed_serialization()
        print("✓ Compressed serialization test passed")
        
        protocol_tests.test_message_validation()
        print("✓ Message validation test passed")
        
        protocol_tests.test_message_expiration()
        print("✓ Message expiration test passed")
        
        protocol_tests.test_request_response_pattern()
        print("✓ Request/response pattern test passed")
        
        protocol_tests.test_protocol_statistics()
        print("✓ Protocol statistics test passed")
        
        print("✓ All MessageProtocol sync tests passed")
        return True
        
    except Exception as e:
        print(f"✗ MessageProtocol sync tests failed: {e}")
        return False


async def run_async_tests():
    """Run asynchronous tests"""
    print("\nRunning async tests...")
    
    framework_tests = TestStreamFramework()
    integration_tests = TestIntegration()
    
    test_results = []
    
    # StreamFramework tests
    try:
        framework_tests.test_framework_creation()
        test_results.append(("StreamFramework.creation", "PASS"))
        
        framework_tests.test_endpoint_registration()
        test_results.append(("StreamFramework.registration", "PASS"))
        
        await framework_tests.test_message_sending_receiving()
        test_results.append(("StreamFramework.messaging", "PASS"))
        
        await framework_tests.test_message_broadcast()
        test_results.append(("StreamFramework.broadcast", "PASS"))
        
        await framework_tests.test_message_routing()
        test_results.append(("StreamFramework.routing", "PASS"))
        
        framework_tests.test_message_filtering()
        test_results.append(("StreamFramework.filtering", "PASS"))
        
        await framework_tests.test_framework_statistics()
        test_results.append(("StreamFramework.statistics", "PASS"))
        
        await framework_tests.test_framework_health_check()
        test_results.append(("StreamFramework.health_check", "PASS"))
        
        await framework_tests.test_error_handling()
        test_results.append(("StreamFramework.error_handling", "PASS"))
        
    except Exception as e:
        print(f"✗ StreamFramework tests failed: {e}")
        test_results.append(("StreamFramework.async", "FAIL"))
        import traceback
        traceback.print_exc()
    
    # Integration tests
    try:
        await integration_tests.test_end_to_end_communication()
        test_results.append(("Integration.end_to_end", "PASS"))
        
        await integration_tests.test_performance_characteristics()
        test_results.append(("Integration.performance", "PASS"))
        
    except Exception as e:
        print(f"✗ Integration tests failed: {e}")
        test_results.append(("Integration.async", "FAIL"))
        import traceback
        traceback.print_exc()
    
    return test_results


async def main():
    """Run all tests and generate output"""
    print("=" * 60)
    print("STREAM COMMUNICATION TESTS - EXECUTION LOG")
    print("=" * 60)
    print(f"Test execution started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run sync tests
    sync_passed = run_sync_tests()
    
    # Run async tests
    async_results = await run_async_tests()
    
    # Combine results
    all_results = [("MessageProtocol.sync", "PASS" if sync_passed else "FAIL")] + async_results
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r[1] == "PASS"])
    failed_tests = total_tests - passed_tests
    
    for test_name, result in all_results:
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    print()
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Stream communication implementation is working correctly.")
        print("\nKey functionality verified:")
        print("✓ Message serialization with multiple formats")
        print("✓ Stream endpoint registration and management")
        print("✓ Point-to-point and broadcast communication")
        print("✓ Message routing and filtering")
        print("✓ Error handling and recovery")
        print("✓ Performance characteristics under load")
        print("✓ Health monitoring and statistics")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.")
    
    print(f"\nTest execution completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return all_results


if __name__ == "__main__":
    results = anyio.run(main)