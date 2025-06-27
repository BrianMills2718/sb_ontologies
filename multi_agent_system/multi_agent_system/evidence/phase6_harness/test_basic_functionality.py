#!/usr/bin/env python3
"""
Basic functionality test after fixing critical issues
"""
import sys
import os
import asyncio
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Test the critical fixes
def test_message_protocol():
    """Test basic MessageProtocol functionality"""
    print("🧪 Testing MessageProtocol...")
    
    from evidence.phase6_harness.day3_stream_communication.message_protocol import (
        MessageProtocol, MessageType, CompressionType
    )
    
    try:
        # Create protocol
        protocol = MessageProtocol()
        
        # Create message
        message = protocol.create_message(
            payload={"test": "data"},
            message_type=MessageType.DATA,
            sender="test_component"
        )
        
        # Check message structure
        assert message.payload == {"test": "data"}
        assert message.metadata.type == MessageType.DATA
        assert message.metadata.sender == "test_component"
        assert message.metadata.id is not None
        
        # Test serialization
        serialized = protocol.serialize(message)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0
        
        # Test deserialization
        deserialized = protocol.deserialize(serialized)
        assert deserialized.payload == message.payload
        assert deserialized.metadata.type == message.metadata.type
        
        print("✅ MessageProtocol basic functionality works!")
        return True
        
    except Exception as e:
        print(f"❌ MessageProtocol test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stream_framework():
    """Test basic StreamFramework functionality"""
    print("\n🧪 Testing StreamFramework...")
    
    try:
        from evidence.phase6_harness.day3_stream_communication.stream_framework import (
            StreamFramework, StreamOperationError
        )
        import anyio
        
        # Create framework
        framework = StreamFramework()
        
        # Check basic attributes
        assert framework.message_protocol is not None
        assert len(framework.endpoints) == 0
        assert framework.enable_metrics is True
        
        # Test endpoint registration
        send_stream, receive_stream = anyio.create_memory_object_stream(max_buffer_size=10)
        
        send_id = framework.register_endpoint("output", "test_component", send_stream)
        recv_id = framework.register_endpoint("input", "test_component", receive_stream)
        
        assert len(framework.endpoints) == 2
        assert send_id == "output"
        assert recv_id == "input"
        
        print("✅ StreamFramework basic functionality works!")
        return True
        
    except Exception as e:
        print(f"❌ StreamFramework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_message_communication():
    """Test end-to-end message communication"""
    print("\n🧪 Testing message communication...")
    
    try:
        from evidence.phase6_harness.day3_stream_communication.stream_framework import StreamFramework
        from evidence.phase6_harness.day3_stream_communication.message_protocol import MessageType
        import anyio
        
        # Create framework
        framework = StreamFramework()
        
        # Create streams with buffer (required for proper operation)
        send_stream, receive_stream = anyio.create_memory_object_stream(max_buffer_size=10)
        
        # Register endpoints
        send_id = framework.register_endpoint("sender", "sender_component", send_stream)
        recv_id = framework.register_endpoint("receiver", "receiver_component", receive_stream)
        
        # Send message
        test_data = {"test": "communication", "value": 42}
        success = await framework.send_message(send_id, test_data, MessageType.DATA)
        assert success is True
        
        # Receive message
        received = await framework.receive_message(recv_id)
        assert received.payload == test_data
        assert received.metadata.type == MessageType.DATA
        
        print("✅ End-to-end message communication works!")
        return True
        
    except Exception as e:
        print(f"❌ Message communication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_harness_component():
    """Test HarnessComponent instantiation"""
    print("\n🧪 Testing HarnessComponent...")
    
    try:
        from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
        from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent
        import asyncio
        
        # Create concrete test component
        class TestComponent(HarnessComponent):
            async def process(self):
                await asyncio.sleep(0.001)
        
        # Create configuration
        config = ComponentConfiguration(
            name="test_component",
            component_type="test",
            service_type="test_service",
            base_type="Source"
        )
        
        # Instantiate component
        component = TestComponent(config)
        
        # Test property access
        assert component.is_running == False  # Should delegate to status
        assert component._is_running == False  # Base attribute should work
        
        # Test that we can set the base attribute without conflict
        component._is_running = True
        assert component._is_running == True
        assert component.is_running == False  # Still delegates to status
        
        print("✅ HarnessComponent instantiation works!")
        return True
        
    except Exception as e:
        print(f"❌ HarnessComponent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all basic functionality tests"""
    print("=" * 60)
    print("BASIC FUNCTIONALITY TESTS AFTER CRITICAL FIXES")
    print("=" * 60)
    
    results = []
    
    # Test 1: MessageProtocol
    results.append(("MessageProtocol", test_message_protocol()))
    
    # Test 2: StreamFramework
    results.append(("StreamFramework", test_stream_framework()))
    
    # Test 3: Message Communication
    results.append(("MessageCommunication", await test_message_communication()))
    
    # Test 4: HarnessComponent
    results.append(("HarnessComponent", test_harness_component()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL BASIC FUNCTIONALITY TESTS PASSED!")
        print("The critical issues have been successfully resolved.")
        print("\nKey fixes verified:")
        print("✓ Property/attribute conflict resolved")
        print("✓ Import issues fixed")
        print("✓ Message structure updated")
        print("✓ Framework methods aligned")
    else:
        print(f"\n⚠️ {total - passed} tests still failing - may need additional fixes")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)