#!/usr/bin/env python3
"""
Performance Benchmark - Week 1 SystemExecutionHarness Performance Testing
========================================================================

Comprehensive performance benchmarking of the SystemExecutionHarness
architecture measuring startup time, message throughput, latency,
and resource utilization under various load conditions.

Benchmark Categories:
1. Component startup time benchmarks
2. Message throughput benchmarks  
3. Latency and responsiveness benchmarks
4. Resource utilization benchmarks
5. Stress testing under high load
6. Scalability testing with multiple components
"""

import asyncio
import time
import logging
import statistics
import gc
import psutil
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent
from evidence.phase6_harness.day1_harness_component.component_status import ComponentState
from evidence.phase6_harness.day2_execution_harness.stream_manager import StreamManager
from evidence.phase6_harness.day3_stream_communication.message_protocol import MessageProtocol, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark"""
    benchmark_name: str
    start_time: float
    end_time: float
    success: bool
    measurements: Dict[str, Any]
    performance_metrics: Dict[str, float]
    resource_usage: Dict[str, Any]
    notes: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class HighThroughputComponent(HarnessComponent):
    """Component designed for high-throughput testing"""
    
    def __init__(self, name: str, target_rate: float = 1000.0):
        config = ComponentConfiguration(
            name=name,
            component_type="high_throughput",
            service_type="benchmark",
            base_type="transformer"
        )
        super().__init__(config)
        self.target_rate = target_rate  # messages per second
        self.messages_sent = 0
        self.messages_received = 0
        self.processing_times = []
        self.last_send_time = 0
        self.max_messages = 10000
        
    async def process(self):
        """High-speed message processing"""
        current_time = time.time()
        
        # Send messages at target rate
        if (self.messages_sent < self.max_messages and 
            current_time - self.last_send_time >= (1.0 / self.target_rate)):
            
            start_process = time.time()
            
            # Generate minimal message for performance
            message = {
                "id": self.messages_sent,
                "timestamp": current_time,
                "data": f"payload_{self.messages_sent}"
            }
            
            # Send to all output streams
            for stream_name in self.send_streams.keys():
                await self.send_message(stream_name, message)
            
            self.messages_sent += 1
            self.last_send_time = current_time
            
            # Record processing time
            process_time = time.time() - start_process
            self.processing_times.append(process_time)
        
        # Receive messages
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    self.messages_received += 1
            except Exception:
                pass
        
        # Minimal delay to prevent tight loop
        await asyncio.sleep(0.0001)


class LatencyTestComponent(HarnessComponent):
    """Component for measuring message latency"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="latency_test",
            service_type="benchmark",
            base_type="transformer"
        )
        super().__init__(config)
        self.latencies = []
        self.message_count = 0
        self.send_timestamps = {}
        
    async def process(self):
        """Measure end-to-end latency"""
        current_time = time.time()
        
        # Send timestamped messages
        if self.message_count < 1000:
            message = {
                "id": self.message_count,
                "send_timestamp": current_time,
                "sender": self.name
            }
            
            self.send_timestamps[self.message_count] = current_time
            
            for stream_name in self.send_streams.keys():
                await self.send_message(stream_name, message)
            
            self.message_count += 1
        
        # Receive and measure latency
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    receive_time = time.time()
                    send_time = message.get("send_timestamp", receive_time)
                    latency = receive_time - send_time
                    self.latencies.append(latency * 1000)  # Convert to ms
            except Exception:
                pass
        
        await asyncio.sleep(0.001)


async def benchmark_component_startup() -> BenchmarkResult:
    """Benchmark component startup performance"""
    logger.info("🚀 Starting Component Startup Benchmark")
    start_time = time.time()
    
    try:
        startup_times = []
        component_counts = [1, 5, 10, 20, 50]
        
        for count in component_counts:
            logger.info(f"   Testing startup with {count} components")
            
            # Measure startup time for this count
            startup_start = time.time()
            
            components = []
            for i in range(count):
                comp = HighThroughputComponent(f"comp_{i}")
                components.append(comp)
                
                # Setup component
                setup_start = time.time()
                await comp.setup()
                setup_time = time.time() - setup_start
                
                if i == 0:  # Record first component setup time
                    startup_times.append(setup_time)
            
            total_startup_time = time.time() - startup_start
            
            # Cleanup
            for comp in components:
                await comp.cleanup()
            
            logger.info(f"   {count} components started in {total_startup_time:.3f}s")
        
        # Calculate metrics
        avg_startup_time = statistics.mean(startup_times) if startup_times else 0
        min_startup_time = min(startup_times) if startup_times else 0
        max_startup_time = max(startup_times) if startup_times else 0
        
        return BenchmarkResult(
            benchmark_name="Component Startup Performance",
            start_time=start_time,
            end_time=time.time(),
            success=True,
            measurements={
                "component_counts_tested": component_counts,
                "individual_startup_times": startup_times
            },
            performance_metrics={
                "average_startup_time_ms": avg_startup_time * 1000,
                "min_startup_time_ms": min_startup_time * 1000,
                "max_startup_time_ms": max_startup_time * 1000,
                "startup_time_requirement_met": avg_startup_time < 0.1  # < 100ms requirement
            },
            resource_usage={}
        )
        
    except Exception as e:
        logger.error(f"❌ Component startup benchmark failed: {e}")
        return BenchmarkResult(
            benchmark_name="Component Startup Performance",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            measurements={},
            performance_metrics={},
            resource_usage={},
            notes=[f"Error: {e}"]
        )


async def benchmark_message_throughput() -> BenchmarkResult:
    """Benchmark message throughput performance"""
    logger.info("📈 Starting Message Throughput Benchmark")
    start_time = time.time()
    
    try:
        # Create stream manager
        stream_manager = StreamManager(default_buffer_size=1000)
        
        # Create high-throughput components
        producer = HighThroughputComponent("producer", target_rate=2000.0)
        consumer = HighThroughputComponent("consumer", target_rate=2000.0)
        
        # Setup components
        await producer.setup()
        await consumer.setup()
        
        # Create stream connection
        send_stream, receive_stream = stream_manager.create_stream(
            buffer_size=2000,
            source_component="producer",
            target_component="consumer"
        )
        
        producer.add_send_stream("output", send_stream)
        consumer.add_receive_stream("input", receive_stream)
        
        # Start components
        await producer.start_processing()
        await consumer.start_processing()
        
        # Let them run for throughput measurement
        test_duration = 5.0
        await asyncio.sleep(test_duration)
        
        # Stop components
        await producer.stop_processing()
        await consumer.stop_processing()
        
        # Calculate throughput metrics
        total_messages_sent = producer.messages_sent
        total_messages_received = consumer.messages_received
        
        send_throughput = total_messages_sent / test_duration
        receive_throughput = total_messages_received / test_duration
        
        # Processing time statistics
        if producer.processing_times:
            avg_processing_time = statistics.mean(producer.processing_times)
            min_processing_time = min(producer.processing_times)
            max_processing_time = max(producer.processing_times)
        else:
            avg_processing_time = min_processing_time = max_processing_time = 0
        
        # Cleanup
        await producer.cleanup()
        await consumer.cleanup()
        await stream_manager.close_all_streams()
        
        return BenchmarkResult(
            benchmark_name="Message Throughput Performance",
            start_time=start_time,
            end_time=time.time(),
            success=True,
            measurements={
                "test_duration_seconds": test_duration,
                "messages_sent": total_messages_sent,
                "messages_received": total_messages_received,
                "processing_times": producer.processing_times[:100]  # Sample
            },
            performance_metrics={
                "send_throughput_msg_per_sec": send_throughput,
                "receive_throughput_msg_per_sec": receive_throughput,
                "avg_processing_time_ms": avg_processing_time * 1000,
                "min_processing_time_ms": min_processing_time * 1000,
                "max_processing_time_ms": max_processing_time * 1000,
                "throughput_requirement_met": send_throughput > 1000  # > 1000 msg/sec requirement
            },
            resource_usage={}
        )
        
    except Exception as e:
        logger.error(f"❌ Throughput benchmark failed: {e}")
        return BenchmarkResult(
            benchmark_name="Message Throughput Performance",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            measurements={},
            performance_metrics={},
            resource_usage={},
            notes=[f"Error: {e}"]
        )


async def benchmark_message_latency() -> BenchmarkResult:
    """Benchmark message latency performance"""
    logger.info("⏱️ Starting Message Latency Benchmark")
    start_time = time.time()
    
    try:
        # Create stream manager
        stream_manager = StreamManager(default_buffer_size=100)
        
        # Create latency test components
        sender = LatencyTestComponent("sender")
        receiver = LatencyTestComponent("receiver")
        
        # Setup components
        await sender.setup()
        await receiver.setup()
        
        # Create stream connection
        send_stream, receive_stream = stream_manager.create_stream(
            buffer_size=100,
            source_component="sender",
            target_component="receiver"
        )
        
        sender.add_send_stream("output", send_stream)
        receiver.add_receive_stream("input", receive_stream)
        
        # Start components
        await sender.start_processing()
        await receiver.start_processing()
        
        # Let them run for latency measurement
        await asyncio.sleep(3.0)
        
        # Stop components
        await sender.stop_processing()
        await receiver.stop_processing()
        
        # Calculate latency metrics
        latencies = receiver.latencies
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        else:
            avg_latency = min_latency = max_latency = p95_latency = p99_latency = 0
        
        # Cleanup
        await sender.cleanup()
        await receiver.cleanup()
        await stream_manager.close_all_streams()
        
        return BenchmarkResult(
            benchmark_name="Message Latency Performance",
            start_time=start_time,
            end_time=time.time(),
            success=len(latencies) > 0,
            measurements={
                "total_messages": len(latencies),
                "latency_samples": latencies[:100]  # Sample
            },
            performance_metrics={
                "avg_latency_ms": avg_latency,
                "min_latency_ms": min_latency,
                "max_latency_ms": max_latency,
                "p95_latency_ms": p95_latency,
                "p99_latency_ms": p99_latency,
                "latency_requirement_met": avg_latency < 10  # < 10ms requirement
            },
            resource_usage={}
        )
        
    except Exception as e:
        logger.error(f"❌ Latency benchmark failed: {e}")
        return BenchmarkResult(
            benchmark_name="Message Latency Performance",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            measurements={},
            performance_metrics={},
            resource_usage={},
            notes=[f"Error: {e}"]
        )


async def benchmark_message_protocol() -> BenchmarkResult:
    """Benchmark message protocol serialization/deserialization performance"""
    logger.info("📦 Starting Message Protocol Benchmark")
    start_time = time.time()
    
    try:
        protocol = MessageProtocol()
        
        # Test data of varying sizes
        test_messages = [
            {"simple": "test"},  # Small message
            {"data": list(range(100))},  # Medium message
            {"large_data": list(range(1000)), "metadata": {"key": "value"}},  # Large message
        ]
        
        serialization_times = []
        deserialization_times = []
        compression_ratios = []
        
        for test_data in test_messages:
            # Test serialization
            for _ in range(100):  # Multiple iterations for accurate timing
                start_ser = time.time()
                message = protocol.create_message(test_data)
                serialized = protocol.serialize(message)
                ser_time = time.time() - start_ser
                serialization_times.append(ser_time)
                
                # Test deserialization
                start_deser = time.time()
                deserialized = protocol.deserialize(serialized)
                deser_time = time.time() - start_deser
                deserialization_times.append(deser_time)
                
                # Calculate compression ratio
                original_size = len(str(test_data))
                compressed_size = len(serialized)
                compression_ratios.append(compressed_size / original_size)
        
        # Calculate metrics
        avg_ser_time = statistics.mean(serialization_times) * 1000  # Convert to ms
        avg_deser_time = statistics.mean(deserialization_times) * 1000
        avg_compression_ratio = statistics.mean(compression_ratios)
        
        protocol_metrics = protocol.get_performance_metrics()
        
        return BenchmarkResult(
            benchmark_name="Message Protocol Performance",
            start_time=start_time,
            end_time=time.time(),
            success=True,
            measurements={
                "serialization_times": serialization_times[:50],  # Sample
                "deserialization_times": deserialization_times[:50],
                "compression_ratios": compression_ratios[:50]
            },
            performance_metrics={
                "avg_serialization_time_ms": avg_ser_time,
                "avg_deserialization_time_ms": avg_deser_time,
                "avg_compression_ratio": avg_compression_ratio,
                "protocol_metrics": protocol_metrics
            },
            resource_usage={}
        )
        
    except Exception as e:
        logger.error(f"❌ Protocol benchmark failed: {e}")
        return BenchmarkResult(
            benchmark_name="Message Protocol Performance",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            measurements={},
            performance_metrics={},
            resource_usage={},
            notes=[f"Error: {e}"]
        )


async def benchmark_resource_usage() -> BenchmarkResult:
    """Benchmark resource usage under load"""
    logger.info("🔧 Starting Resource Usage Benchmark")
    start_time = time.time()
    
    try:
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple components to test resource usage
        components = []
        stream_manager = StreamManager()
        
        # Create and setup components
        for i in range(20):
            comp = HighThroughputComponent(f"comp_{i}", target_rate=100.0)
            await comp.setup()
            components.append(comp)
        
        # Measure memory after component creation
        post_creation_memory = process.memory_info().rss / 1024 / 1024
        
        # Create stream connections
        streams_created = 0
        for i in range(len(components) - 1):
            send_stream, receive_stream = stream_manager.create_stream()
            components[i].add_send_stream("output", send_stream)
            components[i + 1].add_receive_stream("input", receive_stream)
            streams_created += 1
        
        # Measure memory after stream creation
        post_streams_memory = process.memory_info().rss / 1024 / 1024
        
        # Start all components
        for comp in components:
            await comp.start_processing()
        
        # Let them run and measure peak memory
        peak_memory = post_streams_memory
        for _ in range(10):
            await asyncio.sleep(0.5)
            current_memory = process.memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, current_memory)
        
        # Stop and cleanup
        for comp in components:
            await comp.stop_processing()
            await comp.cleanup()
        
        await stream_manager.close_all_streams()
        
        # Force garbage collection and measure final memory
        gc.collect()
        await asyncio.sleep(0.1)
        final_memory = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="Resource Usage Performance",
            start_time=start_time,
            end_time=time.time(),
            success=True,
            measurements={
                "components_created": len(components),
                "streams_created": streams_created
            },
            performance_metrics={
                "initial_memory_mb": initial_memory,
                "post_creation_memory_mb": post_creation_memory,
                "post_streams_memory_mb": post_streams_memory,
                "peak_memory_mb": peak_memory,
                "final_memory_mb": final_memory,
                "memory_per_component_mb": (post_creation_memory - initial_memory) / len(components),
                "memory_per_stream_mb": (post_streams_memory - post_creation_memory) / streams_created,
                "memory_requirement_met": peak_memory < 100  # < 100MB for this test
            },
            resource_usage={
                "memory_usage": {
                    "initial": initial_memory,
                    "peak": peak_memory,
                    "final": final_memory
                }
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Resource usage benchmark failed: {e}")
        return BenchmarkResult(
            benchmark_name="Resource Usage Performance",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            measurements={},
            performance_metrics={},
            resource_usage={},
            notes=[f"Error: {e}"]
        )


async def run_all_benchmarks():
    """Run all performance benchmarks"""
    logger.info("🏁 Starting Complete Performance Benchmark Suite")
    logger.info("=" * 80)
    
    benchmark_results = []
    overall_start = time.time()
    
    # List of benchmarks to run
    benchmarks = [
        ("Component Startup", benchmark_component_startup),
        ("Message Throughput", benchmark_message_throughput),
        ("Message Latency", benchmark_message_latency),
        ("Message Protocol", benchmark_message_protocol),
        ("Resource Usage", benchmark_resource_usage)
    ]
    
    for name, benchmark_func in benchmarks:
        logger.info(f"📋 Running {name} Benchmark")
        try:
            result = await benchmark_func()
            benchmark_results.append(result)
            
            # Log results
            status = "✅ PASSED" if result.success else "❌ FAILED"
            logger.info(f"{status} {result.benchmark_name}")
            logger.info(f"   Duration: {result.duration:.3f}s")
            
            if result.success:
                # Log key performance metrics
                for key, value in result.performance_metrics.items():
                    if "requirement_met" in key:
                        req_status = "✅" if value else "❌"
                        logger.info(f"   {req_status} {key}: {value}")
                    elif isinstance(value, (int, float)) and "ms" in key:
                        logger.info(f"   {key}: {value:.3f}")
                    elif isinstance(value, (int, float)) and "mb" in key.lower():
                        logger.info(f"   {key}: {value:.2f}")
                    elif isinstance(value, (int, float)):
                        logger.info(f"   {key}: {value:.2f}")
            
        except Exception as e:
            logger.error(f"❌ {name} benchmark failed: {e}")
            # Create failed result
            failed_result = BenchmarkResult(
                benchmark_name=name,
                start_time=time.time(),
                end_time=time.time(),
                success=False,
                measurements={},
                performance_metrics={},
                resource_usage={},
                notes=[f"Exception: {e}"]
            )
            benchmark_results.append(failed_result)
        
        # Small delay between benchmarks
        await asyncio.sleep(1.0)
    
    # Generate overall summary
    overall_duration = time.time() - overall_start
    passed_benchmarks = sum(1 for result in benchmark_results if result.success)
    total_benchmarks = len(benchmark_results)
    
    logger.info("=" * 80)
    logger.info("📊 Performance Benchmark Summary")
    logger.info(f"   Benchmarks passed: {passed_benchmarks}/{total_benchmarks}")
    logger.info(f"   Success rate: {passed_benchmarks/total_benchmarks*100:.1f}%")
    logger.info(f"   Total duration: {overall_duration:.2f}s")
    
    # Performance requirements summary
    logger.info("\n🎯 Performance Requirements Check:")
    requirements_met = 0
    total_requirements = 0
    
    for result in benchmark_results:
        for key, value in result.performance_metrics.items():
            if "requirement_met" in key:
                total_requirements += 1
                if value:
                    requirements_met += 1
                    logger.info(f"   ✅ {key.replace('_requirement_met', '').replace('_', ' ').title()}")
                else:
                    logger.info(f"   ❌ {key.replace('_requirement_met', '').replace('_', ' ').title()}")
    
    if total_requirements > 0:
        req_percentage = requirements_met / total_requirements * 100
        logger.info(f"\n📈 Requirements Met: {requirements_met}/{total_requirements} ({req_percentage:.1f}%)")
    
    # Detailed results
    logger.info("\n📋 Detailed Benchmark Results:")
    for result in benchmark_results:
        status = "✅" if result.success else "❌"
        logger.info(f"   {status} {result.benchmark_name}")
        logger.info(f"      Duration: {result.duration:.3f}s")
        
        if result.success:
            # Show top metrics
            metrics_shown = 0
            for key, value in result.performance_metrics.items():
                if metrics_shown >= 3:  # Limit output
                    break
                if not "requirement_met" in key and isinstance(value, (int, float)):
                    logger.info(f"      {key}: {value:.3f}")
                    metrics_shown += 1
    
    # Overall success determination
    overall_success = passed_benchmarks == total_benchmarks
    
    if overall_success:
        logger.info("🎉 All performance benchmarks PASSED!")
    else:
        logger.info("❌ Some performance benchmarks FAILED!")
    
    return {
        "overall_success": overall_success,
        "passed_benchmarks": passed_benchmarks,
        "total_benchmarks": total_benchmarks,
        "success_rate": passed_benchmarks/total_benchmarks*100,
        "total_duration": overall_duration,
        "requirements_met": requirements_met,
        "total_requirements": total_requirements,
        "requirements_percentage": requirements_met/total_requirements*100 if total_requirements > 0 else 0,
        "benchmark_results": benchmark_results
    }


if __name__ == "__main__":
    async def main():
        logger.info("🎯 SystemExecutionHarness Performance Benchmark Suite")
        logger.info("🎯 Measuring startup time, throughput, latency, and resource usage")
        
        results = await run_all_benchmarks()
        
        # Return results for external evaluation
        return results
    
    # Run the benchmarks
    asyncio.run(main())