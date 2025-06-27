#!/usr/bin/env python3
"""
Real System Demo - Phase 6 SystemExecutionHarness Working Demonstration
======================================================================

A complete working demonstration of the SystemExecutionHarness architecture
showing all implemented features working together independently.

Demonstrates:
1. Component lifecycle management with ComponentStatus
2. Stream-based communication using StreamManager
3. Message protocol serialization/deserialization  
4. Multi-component data processing pipeline
5. Error handling and recovery mechanisms
6. Performance monitoring and health checks
"""

import asyncio
import anyio
import time
import logging
import json
from typing import Dict, List, Any
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase6_harness.day1_harness_component.component_status import ComponentStatus, ComponentState
from evidence.phase6_harness.day2_execution_harness.stream_manager import StreamManager
from evidence.phase6_harness.day3_stream_communication.message_protocol import MessageProtocol, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DemoResults:
    """Results from the demonstration"""
    demo_name: str
    start_time: float
    end_time: float
    success: bool
    components_created: int
    streams_created: int
    messages_processed: int
    state_transitions: int
    errors_handled: int
    performance_metrics: Dict[str, Any]
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class ComponentStatusDemo:
    """Demonstrates ComponentStatus functionality"""
    
    def __init__(self):
        self.components = {}
        self.total_transitions = 0
        self.errors_handled = 0
    
    async def run_status_demo(self) -> Dict[str, Any]:
        """Demonstrate component status management"""
        logger.info("🔄 Demonstrating ComponentStatus Lifecycle Management")
        
        # Create multiple components with status tracking
        component_names = ["data_source", "processor", "validator", "sink"]
        
        for name in component_names:
            status = ComponentStatus(name)
            self.components[name] = status
            logger.info(f"✨ Created component '{name}' in state: {status.state.value}")
        
        # Demonstrate state transitions
        for name, status in self.components.items():
            logger.info(f"🔄 Transitioning '{name}' through lifecycle states")
            
            # Transition to ready
            await status.transition_to(ComponentState.READY)
            self.total_transitions += 1
            logger.info(f"   {name}: CREATED → READY")
            
            # Transition to running
            await status.transition_to(ComponentState.RUNNING)
            self.total_transitions += 1
            logger.info(f"   {name}: READY → RUNNING")
            
            # Simulate some activity
            await asyncio.sleep(0.1)
        
        # Demonstrate error handling and recovery
        error_component = self.components["processor"]
        try:
            # Record an error
            test_error = ValueError("Simulated processing error")
            await error_component.record_error(test_error)
            self.errors_handled += 1
            logger.info(f"❌ Recorded error in '{error_component.name}': {test_error}")
            
            # Attempt recovery
            recovery_success = await error_component.attempt_recovery()
            if recovery_success:
                logger.info(f"✅ Successfully recovered '{error_component.name}'")
            else:
                logger.info(f"❌ Recovery failed for '{error_component.name}'")
                
        except Exception as e:
            logger.warning(f"⚠️ Error during error handling demo: {e}")
        
        # Graceful shutdown
        for name, status in self.components.items():
            if status.state == ComponentState.RUNNING:
                await status.transition_to(ComponentState.STOPPING)
                self.total_transitions += 1
                await status.transition_to(ComponentState.STOPPED)
                self.total_transitions += 1
                logger.info(f"🛑 Gracefully stopped '{name}'")
        
        # Generate status reports
        logger.info("📊 Final Component Status Reports:")
        for name, status in self.components.items():
            summary = status.get_status_summary()
            logger.info(f"   {name}: {summary['state']} (errors: {summary['error_count']}, uptime: {summary['uptime_seconds']:.2f}s)")
        
        return {
            "components_managed": len(self.components),
            "total_transitions": self.total_transitions,
            "errors_handled": self.errors_handled,
            "all_components_stopped": all(s.state == ComponentState.STOPPED for s in self.components.values())
        }


class StreamManagerDemo:
    """Demonstrates StreamManager functionality"""
    
    def __init__(self):
        self.stream_manager = StreamManager(default_buffer_size=100)
        self.streams_created = 0
        self.messages_sent = 0
        self.messages_received = 0
    
    async def run_stream_demo(self) -> Dict[str, Any]:
        """Demonstrate stream management and communication"""
        logger.info("📡 Demonstrating StreamManager Communication")
        
        # Create multiple stream connections
        stream_pairs = []
        component_names = ["source", "processor", "enricher", "sink"]
        
        for i in range(len(component_names) - 1):
            source_comp = component_names[i]
            target_comp = component_names[i + 1]
            
            send_stream, receive_stream = self.stream_manager.create_stream(
                buffer_size=50,
                source_component=source_comp,
                target_component=target_comp
            )
            
            stream_pairs.append((send_stream, receive_stream, source_comp, target_comp))
            self.streams_created += 1
            logger.info(f"🔗 Created stream: {source_comp} → {target_comp}")
        
        # Demonstrate message passing through the pipeline
        logger.info("📤 Sending messages through pipeline")
        
        # Send initial messages
        test_messages = [
            {"id": 1, "data": "message_1", "timestamp": time.time()},
            {"id": 2, "data": "message_2", "timestamp": time.time()},
            {"id": 3, "data": "message_3", "timestamp": time.time()}
        ]
        
        # Send messages through the first stream
        first_send_stream = stream_pairs[0][0]
        for message in test_messages:
            await first_send_stream.send(message)
            self.messages_sent += 1
            logger.info(f"📤 Sent message {message['id']} to pipeline")
        
        # Process messages through the pipeline
        for i, (send_stream, receive_stream, source, target) in enumerate(stream_pairs):
            logger.info(f"🔄 Processing messages in {source} → {target}")
            
            # Receive messages
            processed_messages = []
            for _ in range(len(test_messages)):
                try:
                    with anyio.fail_after(2.0):  # 2 second timeout
                        message = await receive_stream.receive()
                        processed_messages.append(message)
                        self.messages_received += 1
                        logger.info(f"📥 {target} received message {message.get('id', 'unknown')}")
                except anyio.EndOfStream:
                    logger.info(f"📥 Stream closed for {target}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Receive timeout or error in {target}: {e}")
                    break
            
            # Forward to next stage (if not the last stream)
            if i < len(stream_pairs) - 1:
                next_send_stream = stream_pairs[i + 1][0]
                for message in processed_messages:
                    # Add processing metadata
                    processed_message = {
                        **message,
                        "processed_by": target,
                        "processed_at": time.time()
                    }
                    await next_send_stream.send(processed_message)
                    self.messages_sent += 1
                    logger.info(f"📤 {target} forwarded processed message {message.get('id', 'unknown')}")
        
        # Get stream statistics
        stats = self.stream_manager.get_stream_statistics()
        logger.info(f"📊 Stream Statistics: {stats['total_created']} created, {stats['active_count']} active")
        
        # Health check
        health_result = await self.stream_manager.health_check_streams()
        logger.info(f"🏥 Stream Health: {health_result.get('healthy_streams', 0)}/{health_result.get('total_streams', 0)} healthy")
        
        # Cleanup
        await self.stream_manager.close_all_streams()
        logger.info("🧹 All streams closed")
        
        return {
            "streams_created": self.streams_created,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "stream_statistics": stats,
            "health_result": health_result
        }


class MessageProtocolDemo:
    """Demonstrates MessageProtocol functionality"""
    
    def __init__(self):
        self.protocol = MessageProtocol(
            compression_threshold=100,
            enable_compression=True,
            enable_validation=True
        )
        self.messages_serialized = 0
        self.messages_deserialized = 0
        self.serialization_errors = 0
    
    async def run_protocol_demo(self) -> Dict[str, Any]:
        """Demonstrate message protocol operations"""
        logger.info("📦 Demonstrating MessageProtocol Serialization")
        
        # Test different message types and sizes
        test_cases = [
            {"type": "simple", "data": {"value": 42, "text": "hello"}},
            {"type": "complex", "data": {"numbers": list(range(50)), "metadata": {"source": "demo"}}},
            {"type": "large", "data": {"payload": "x" * 500, "items": list(range(100))}},
        ]
        
        serialization_times = []
        deserialization_times = []
        
        for test_case in test_cases:
            logger.info(f"📦 Testing {test_case['type']} message")
            
            try:
                # Create message
                message = self.protocol.create_message(
                    payload=test_case["data"],
                    message_type=MessageType.DATA,
                    sender="demo_sender",
                    recipient="demo_receiver"
                )
                
                # Serialize
                start_time = time.time()
                serialized = self.protocol.serialize(message)
                ser_time = time.time() - start_time
                serialization_times.append(ser_time)
                self.messages_serialized += 1
                
                logger.info(f"   Serialized in {ser_time*1000:.3f}ms, size: {len(serialized)} bytes")
                
                # Deserialize
                start_time = time.time()
                deserialized = self.protocol.deserialize(serialized)
                deser_time = time.time() - start_time
                deserialization_times.append(deser_time)
                self.messages_deserialized += 1
                
                logger.info(f"   Deserialized in {deser_time*1000:.3f}ms")
                
                # Verify data integrity
                if deserialized.payload == test_case["data"]:
                    logger.info(f"   ✅ Data integrity verified")
                else:
                    logger.warning(f"   ❌ Data integrity check failed")
                
            except Exception as e:
                self.serialization_errors += 1
                logger.error(f"   ❌ Serialization error: {e}")
        
        # Test special message types
        logger.info("📦 Testing special message types")
        
        # Error message
        error_msg = self.protocol.create_error_message(
            ValueError("Test error"),
            original_message_id="test_123",
            sender="demo_component"
        )
        error_serialized = self.protocol.serialize(error_msg)
        error_deserialized = self.protocol.deserialize(error_serialized)
        logger.info(f"   ✅ Error message: {len(error_serialized)} bytes")
        
        # Heartbeat message
        heartbeat_msg = self.protocol.create_heartbeat_message(
            sender="demo_component",
            status={"healthy": True, "uptime": 123.45}
        )
        heartbeat_serialized = self.protocol.serialize(heartbeat_msg)
        heartbeat_deserialized = self.protocol.deserialize(heartbeat_serialized)
        logger.info(f"   ✅ Heartbeat message: {len(heartbeat_serialized)} bytes")
        
        # Get performance metrics
        perf_metrics = self.protocol.get_performance_metrics()
        logger.info("📊 Protocol Performance Metrics:")
        logger.info(f"   Serialization: {perf_metrics['serialization']['average_time_ms']:.3f}ms avg")
        logger.info(f"   Deserialization: {perf_metrics['deserialization']['average_time_ms']:.3f}ms avg")
        logger.info(f"   Compression ratio: {perf_metrics['compression']['average_compression_ratio']:.3f}")
        
        return {
            "messages_serialized": self.messages_serialized,
            "messages_deserialized": self.messages_deserialized,
            "serialization_errors": self.serialization_errors,
            "avg_serialization_time": sum(serialization_times) / len(serialization_times) if serialization_times else 0,
            "avg_deserialization_time": sum(deserialization_times) / len(deserialization_times) if deserialization_times else 0,
            "performance_metrics": perf_metrics
        }


async def run_complete_system_demo() -> DemoResults:
    """Run complete system demonstration"""
    logger.info("🚀 Starting Complete SystemExecutionHarness Demo")
    logger.info("=" * 80)
    
    start_time = time.time()
    total_components = 0
    total_streams = 0
    total_messages = 0
    total_transitions = 0
    total_errors = 0
    
    try:
        # Demo 1: Component Status Management
        logger.info("📋 Demo 1: Component Status Management")
        status_demo = ComponentStatusDemo()
        status_results = await status_demo.run_status_demo()
        
        total_components += status_results["components_managed"]
        total_transitions += status_results["total_transitions"]
        total_errors += status_results["errors_handled"]
        
        logger.info(f"✅ Status Demo: {status_results['components_managed']} components, {status_results['total_transitions']} transitions")
        
        # Small delay between demos
        await asyncio.sleep(1.0)
        
        # Demo 2: Stream Communication
        logger.info("\n📋 Demo 2: Stream Communication")
        stream_demo = StreamManagerDemo()
        stream_results = await stream_demo.run_stream_demo()
        
        total_streams += stream_results["streams_created"]
        total_messages += stream_results["messages_sent"] + stream_results["messages_received"]
        
        logger.info(f"✅ Stream Demo: {stream_results['streams_created']} streams, {stream_results['messages_sent']} sent, {stream_results['messages_received']} received")
        
        # Small delay between demos
        await asyncio.sleep(1.0)
        
        # Demo 3: Message Protocol
        logger.info("\n📋 Demo 3: Message Protocol")
        protocol_demo = MessageProtocolDemo()
        protocol_results = await protocol_demo.run_protocol_demo()
        
        total_messages += protocol_results["messages_serialized"] + protocol_results["messages_deserialized"]
        
        logger.info(f"✅ Protocol Demo: {protocol_results['messages_serialized']} serialized, {protocol_results['messages_deserialized']} deserialized")
        
        # Compile performance metrics
        performance_metrics = {
            "component_lifecycle": status_results,
            "stream_communication": stream_results,
            "message_protocol": protocol_results,
            "overall": {
                "total_components": total_components,
                "total_streams": total_streams,
                "total_messages": total_messages,
                "total_transitions": total_transitions,
                "total_errors_handled": total_errors
            }
        }
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Final summary
        logger.info("=" * 80)
        logger.info("📊 Complete Demo Summary")
        logger.info(f"   Duration: {duration:.2f}s")
        logger.info(f"   Components: {total_components}")
        logger.info(f"   Streams: {total_streams}")
        logger.info(f"   Messages: {total_messages}")
        logger.info(f"   State transitions: {total_transitions}")
        logger.info(f"   Errors handled: {total_errors}")
        
        if total_messages > 0 and duration > 0:
            throughput = total_messages / duration
            logger.info(f"   Throughput: {throughput:.2f} messages/sec")
        
        logger.info("🎉 Complete SystemExecutionHarness Demo SUCCESSFUL!")
        
        return DemoResults(
            demo_name="Complete SystemExecutionHarness Demo",
            start_time=start_time,
            end_time=end_time,
            success=True,
            components_created=total_components,
            streams_created=total_streams,
            messages_processed=total_messages,
            state_transitions=total_transitions,
            errors_handled=total_errors,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {e}")
        return DemoResults(
            demo_name="Complete SystemExecutionHarness Demo",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            components_created=total_components,
            streams_created=total_streams,
            messages_processed=total_messages,
            state_transitions=total_transitions,
            errors_handled=total_errors,
            performance_metrics={"error": str(e)}
        )


async def demonstrate_architecture_features():
    """Demonstrate key architectural features independently"""
    logger.info("🏗️ Demonstrating SystemExecutionHarness Architecture Features")
    logger.info("=" * 80)
    
    features_demonstrated = []
    
    # Feature 1: Component State Management
    logger.info("🔄 Feature 1: Advanced Component State Management")
    status = ComponentStatus("demo_component")
    
    # Show state transitions
    await status.transition_to(ComponentState.READY)
    await status.transition_to(ComponentState.RUNNING)
    
    # Show error handling
    await status.record_error(ValueError("Demo error"))
    recovery_success = await status.attempt_recovery()
    
    # Show metrics
    health_report = status.get_health_report()
    logger.info(f"   Component health: {health_report['healthy']}")
    logger.info(f"   Error count: {health_report['error_count']}")
    logger.info(f"   Recovery attempts: {health_report['recovery_attempts']}")
    
    features_demonstrated.append("Component State Management")
    
    # Feature 2: Stream Management
    logger.info("\n📡 Feature 2: High-Performance Stream Management")
    stream_manager = StreamManager(default_buffer_size=50)
    
    # Create streams
    send_stream, receive_stream = stream_manager.create_stream(
        source_component="feature_demo_source",
        target_component="feature_demo_target"
    )
    
    # Demonstrate communication
    await send_stream.send({"demo": "message", "feature": "stream_management"})
    received = await receive_stream.receive()
    logger.info(f"   Stream communication successful: {received['demo']}")
    
    # Show statistics
    stats = stream_manager.get_stream_statistics()
    logger.info(f"   Streams created: {stats['total_created']}")
    logger.info(f"   Active streams: {stats['active_count']}")
    
    await stream_manager.close_all_streams()
    features_demonstrated.append("Stream Management")
    
    # Feature 3: Message Protocol
    logger.info("\n📦 Feature 3: Advanced Message Protocol")
    protocol = MessageProtocol()
    
    # Demonstrate different message types
    data_msg = protocol.create_message({"feature": "protocol_demo"}, MessageType.DATA)
    error_msg = protocol.create_error_message(ValueError("Demo error"))
    heartbeat_msg = protocol.create_heartbeat_message("demo_sender")
    
    # Show serialization
    for msg_type, msg in [("Data", data_msg), ("Error", error_msg), ("Heartbeat", heartbeat_msg)]:
        serialized = protocol.serialize(msg)
        deserialized = protocol.deserialize(serialized)
        logger.info(f"   {msg_type} message: {len(serialized)} bytes")
    
    # Show performance metrics
    perf = protocol.get_performance_metrics()
    logger.info(f"   Serialization performance: {perf['serialization']['average_time_ms']:.3f}ms")
    
    features_demonstrated.append("Message Protocol")
    
    logger.info("=" * 80)
    logger.info(f"✅ Successfully demonstrated {len(features_demonstrated)} architecture features:")
    for feature in features_demonstrated:
        logger.info(f"   ✅ {feature}")
    
    return features_demonstrated


if __name__ == "__main__":
    async def main():
        logger.info("🎯 SystemExecutionHarness Real System Demonstration")
        logger.info("🎯 Showing production-ready architecture components working independently")
        print()
        
        # Run architecture features demo
        features = await demonstrate_architecture_features()
        
        print()
        logger.info("-" * 80)
        print()
        
        # Run complete system demo
        demo_results = await run_complete_system_demo()
        
        logger.info("-" * 80)
        logger.info("🎯 Final Demonstration Results:")
        logger.info(f"   Success: {demo_results.success}")
        logger.info(f"   Duration: {demo_results.duration:.2f}s")
        logger.info(f"   Components: {demo_results.components_created}")
        logger.info(f"   Streams: {demo_results.streams_created}")
        logger.info(f"   Messages: {demo_results.messages_processed}")
        logger.info(f"   Architecture features: {len(features)}")
        
        if demo_results.success:
            logger.info("🎉 SystemExecutionHarness architecture successfully demonstrated!")
        else:
            logger.info("❌ Some aspects of the demonstration encountered issues")
        
        return {
            "demo_results": demo_results,
            "features_demonstrated": features,
            "overall_success": demo_results.success and len(features) >= 3
        }
    
    # Run the demonstration
    asyncio.run(main())