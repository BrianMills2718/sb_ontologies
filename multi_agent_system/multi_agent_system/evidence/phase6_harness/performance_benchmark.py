#!/usr/bin/env python3
"""
Performance benchmark test for Phase 6 SystemExecutionHarness
"""
import sys
import os
import asyncio
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from evidence.phase6_harness.day2_execution_harness.system_execution_harness import SystemExecutionHarness
from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent

class BenchmarkSource(HarnessComponent):
    """High-performance source component for benchmarking"""
    
    def __init__(self, config):
        super().__init__(config)
        self.message_count = 0
        self.max_messages = 1000
    
    async def process(self):
        if self.message_count < self.max_messages:
            data = {"id": self.message_count, "timestamp": time.time(), "data": f"message_{self.message_count}"}
            
            if "output" in self.send_streams:
                await self.send_message("output", data)
                self.message_count += 1
        else:
            await asyncio.sleep(0.001)  # Completed, just wait

class BenchmarkProcessor(HarnessComponent):
    """High-performance processor component for benchmarking"""
    
    def __init__(self, config):
        super().__init__(config)
        self.processed_count = 0
    
    async def process(self):
        if "input" in self.receive_streams:
            data = await self.receive_message("input", timeout=0.001)
            if data:
                # Simulate processing
                processed_data = {**data, "processed": True, "processed_at": time.time()}
                
                if "output" in self.send_streams:
                    await self.send_message("output", processed_data)
                    self.processed_count += 1

class BenchmarkSink(HarnessComponent):
    """High-performance sink component for benchmarking"""
    
    def __init__(self, config):
        super().__init__(config)
        self.received_count = 0
        self.first_message_time = None
        self.last_message_time = None
    
    async def process(self):
        if "input" in self.receive_streams:
            data = await self.receive_message("input", timeout=0.001)
            if data:
                if self.first_message_time is None:
                    self.first_message_time = time.time()
                self.last_message_time = time.time()
                self.received_count += 1

async def benchmark_startup_time():
    """Test startup time - must be <100ms"""
    print("🏃 Testing startup time...")
    
    start_time = time.time()
    
    # Create harness
    harness = SystemExecutionHarness()
    
    # Create components
    source_config = ComponentConfiguration(
        name="bench_source",
        component_type="benchmark_source", 
        service_type="data_source",
        base_type="Source"
    )
    source = BenchmarkSource(source_config)
    
    # Register and start
    harness.register_component("bench_source", source)
    
    # Start the harness (this will trigger setup but we need to stop it quickly)
    run_task = asyncio.create_task(harness.run())
    await asyncio.sleep(0.01)  # Let it start up
    run_task.cancel()
    try:
        await run_task
    except asyncio.CancelledError:
        pass
    
    startup_time = (time.time() - start_time) * 1000  # Convert to ms
    
    print(f"✅ Startup time: {startup_time:.2f}ms")
    return startup_time < 100

async def benchmark_message_throughput():
    """Test message throughput - must be >1000 msg/sec"""
    print("🚀 Testing message throughput...")
    
    # Create harness
    harness = SystemExecutionHarness()
    
    # Create components
    source_config = ComponentConfiguration(
        name="source", component_type="source", service_type="data_source", base_type="Source"
    )
    processor_config = ComponentConfiguration(
        name="processor", component_type="processor", service_type="data_processor", base_type="Transformer"
    )
    sink_config = ComponentConfiguration(
        name="sink", component_type="sink", service_type="data_sink", base_type="Sink"
    )
    
    source = BenchmarkSource(source_config)
    processor = BenchmarkProcessor(processor_config)
    sink = BenchmarkSink(sink_config)
    
    # Register components
    harness.register_component("source", source)
    harness.register_component("processor", processor)
    harness.register_component("sink", sink)
    
    # Connect streams
    harness.connect("source.output", "processor.input")
    harness.connect("processor.output", "sink.input")
    
    # Start harness
    run_task = asyncio.create_task(harness.run())
    
    # Run for a few seconds
    test_duration = 3.0
    await asyncio.sleep(test_duration)
    
    # Calculate throughput
    messages_sent = source.message_count
    messages_processed = processor.processed_count
    messages_received = sink.received_count
    
    if sink.first_message_time and sink.last_message_time:
        actual_duration = sink.last_message_time - sink.first_message_time
        throughput = messages_received / actual_duration if actual_duration > 0 else 0
    else:
        throughput = 0
    
    run_task.cancel()
    try:
        await run_task
    except asyncio.CancelledError:
        pass
    
    print(f"📊 Messages: sent={messages_sent}, processed={messages_processed}, received={messages_received}")
    print(f"⚡ Throughput: {throughput:.2f} messages/second")
    
    return throughput > 1000

async def benchmark_latency():
    """Test message latency - must be <10ms"""
    print("⏱️ Testing message latency...")
    
    # Create simple source-sink pipeline
    harness = SystemExecutionHarness()
    
    source_config = ComponentConfiguration(
        name="source", component_type="source", service_type="data_source", base_type="Source"
    )
    sink_config = ComponentConfiguration(
        name="sink", component_type="sink", service_type="data_sink", base_type="Sink"
    )
    
    # Modify source to send timestamped messages
    class LatencySource(BenchmarkSource):
        def __init__(self, config):
            super().__init__(config)
            self.max_messages = 10  # Just a few messages for latency test
    
    class LatencySink(BenchmarkSink):
        def __init__(self, config):
            super().__init__(config)
            self.latencies = []
        
        async def process(self):
            if "input" in self.receive_streams:
                data = await self.receive_message("input", timeout=0.001)
                if data and "timestamp" in data:
                    receive_time = time.time()
                    latency = (receive_time - data["timestamp"]) * 1000  # Convert to ms
                    self.latencies.append(latency)
                    self.received_count += 1
    
    source = LatencySource(source_config)
    sink = LatencySink(sink_config)
    
    harness.register_component("source", source)
    harness.register_component("sink", sink)
    harness.connect("source.output", "sink.input")
    
    run_task = asyncio.create_task(harness.run())
    
    # Wait for messages to be processed
    await asyncio.sleep(1.0)
    
    run_task.cancel()
    try:
        await run_task
    except asyncio.CancelledError:
        pass
    
    if sink.latencies:
        avg_latency = sum(sink.latencies) / len(sink.latencies)
        max_latency = max(sink.latencies)
        print(f"📈 Average latency: {avg_latency:.2f}ms, Max latency: {max_latency:.2f}ms")
        return avg_latency < 10
    else:
        print("❌ No latency measurements captured")
        return False

async def main():
    """Run all performance benchmarks"""
    print("=" * 60)
    print("PHASE 6 SYSTEM EXECUTION HARNESS - PERFORMANCE BENCHMARKS")
    print("=" * 60)
    
    results = []
    
    # Test 1: Startup time (<100ms)
    try:
        startup_ok = await benchmark_startup_time()
        results.append(("Startup Time (<100ms)", startup_ok))
    except Exception as e:
        print(f"❌ Startup benchmark failed: {e}")
        results.append(("Startup Time (<100ms)", False))
    
    print()
    
    # Test 2: Throughput (>1000 msg/sec)
    try:
        throughput_ok = await benchmark_message_throughput()
        results.append(("Throughput (>1000 msg/sec)", throughput_ok))
    except Exception as e:
        print(f"❌ Throughput benchmark failed: {e}")
        results.append(("Throughput (>1000 msg/sec)", False))
    
    print()
    
    # Test 3: Latency (<10ms)
    try:
        latency_ok = await benchmark_latency()
        results.append(("Latency (<10ms)", latency_ok))
    except Exception as e:
        print(f"❌ Latency benchmark failed: {e}")
        results.append(("Latency (<10ms)", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARK RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} benchmarks passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PERFORMANCE BENCHMARKS PASSED!")
        print("SystemExecutionHarness meets all performance requirements.")
    else:
        print(f"\n⚠️ {total - passed} benchmark(s) failed - performance requirements not met")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)