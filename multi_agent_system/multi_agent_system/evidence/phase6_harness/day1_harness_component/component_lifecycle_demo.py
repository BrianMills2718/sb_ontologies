#!/usr/bin/env python3
"""
Component Lifecycle Demo - Day 1 HarnessComponent Demonstration
==============================================================

Demonstrates the complete HarnessComponent lifecycle with three different
component implementations showing stream connections, processing, and 
graceful shutdown.

Components Demonstrated:
1. DataGenerator - Generates test data (Source component)
2. DataProcessor - Processes incoming data (Transformer component)  
3. DataCollector - Collects processed data (Sink component)
"""

import asyncio
import anyio
import time
import logging
from typing import List, Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent, HarnessContext
from evidence.phase6_harness.day1_harness_component.component_status import ComponentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataGeneratorComponent(HarnessComponent):
    """Source component that generates test data"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="data_generator",
            service_type="data_source",
            base_type="source"
        )
        super().__init__(config)
        
        # Generator state
        self.message_count = 0
        self.max_messages = 10
        self.generation_interval = 0.5  # Generate message every 500ms
        self.last_generation = 0
    
    async def _initialize_component_resources(self):
        """Initialize generator-specific resources"""
        logger.info(f"🔧 Initializing DataGenerator '{self.name}' - will generate {self.max_messages} messages")
        self.last_generation = time.time()
    
    async def process(self):
        """Generate test data messages"""
        current_time = time.time()
        
        # Check if it's time to generate a new message
        if (current_time - self.last_generation >= self.generation_interval and 
            self.message_count < self.max_messages):
            
            # Generate test message
            message = {
                "id": f"msg_{self.message_count:03d}",
                "data": f"test_data_{self.message_count}",
                "timestamp": current_time,
                "generator": self.name,
                "sequence": self.message_count
            }
            
            # Send to all output streams
            for stream_name in self.send_streams.keys():
                success = await self.send_message(stream_name, message)
                if success:
                    logger.info(f"📤 {self.name} generated message {self.message_count}: {message['id']}")
            
            self.message_count += 1
            self.last_generation = current_time
        
        # Small delay to prevent tight loop
        await asyncio.sleep(0.01)
    
    async def _cleanup_component_resources(self):
        """Clean up generator resources"""
        logger.info(f"🧹 DataGenerator '{self.name}' cleanup - generated {self.message_count} total messages")


class DataProcessorComponent(HarnessComponent):
    """Transformer component that processes incoming data"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="data_processor",
            service_type="data_processor",
            base_type="transformer"
        )
        super().__init__(config)
        
        # Processing state
        self.processed_count = 0
        self.processing_time_total = 0.0
    
    async def _initialize_component_resources(self):
        """Initialize processor-specific resources"""
        logger.info(f"🔧 Initializing DataProcessor '{self.name}' - ready to process messages")
    
    async def process(self):
        """Process incoming messages from all input streams"""
        # Check all receive streams for messages
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    # Process the message
                    processing_start = time.time()
                    
                    processed_message = {
                        "original_id": message.get("id", "unknown"),
                        "original_data": message.get("data", ""),
                        "processed_data": f"PROCESSED_{message.get('data', '')}",
                        "processed_by": self.name,
                        "processed_at": processing_start,
                        "processing_sequence": self.processed_count,
                        "original_generator": message.get("generator", "unknown")
                    }
                    
                    # Simulate processing delay
                    await asyncio.sleep(0.1)
                    
                    processing_time = time.time() - processing_start
                    self.processing_time_total += processing_time
                    
                    # Send processed message to output streams
                    for output_stream in self.send_streams.keys():
                        success = await self.send_message(output_stream, processed_message)
                        if success:
                            logger.info(f"⚙️ {self.name} processed {message['id']} → {processed_message['original_id']} in {processing_time:.3f}s")
                    
                    self.processed_count += 1
                    
            except Exception as e:
                # Handle processing errors gracefully
                logger.warning(f"⚠️ Processing error in {self.name}: {e}")
        
        # Small delay to prevent tight loop
        await asyncio.sleep(0.01)
    
    async def _cleanup_component_resources(self):
        """Clean up processor resources"""
        avg_processing_time = self.processing_time_total / max(1, self.processed_count)
        logger.info(f"🧹 DataProcessor '{self.name}' cleanup - processed {self.processed_count} messages, avg time: {avg_processing_time:.3f}s")


class DataCollectorComponent(HarnessComponent):
    """Sink component that collects processed data"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="data_collector",
            service_type="data_sink", 
            base_type="sink"
        )
        super().__init__(config)
        
        # Collection state
        self.collected_messages: List[Dict[str, Any]] = []
        self.collection_stats = {
            "total_collected": 0,
            "first_message_time": None,
            "last_message_time": None
        }
    
    async def _initialize_component_resources(self):
        """Initialize collector-specific resources"""
        logger.info(f"🔧 Initializing DataCollector '{self.name}' - ready to collect data")
    
    async def process(self):
        """Collect messages from all input streams"""
        # Check all receive streams for messages
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    # Store the collected message
                    collection_entry = {
                        "collected_at": time.time(),
                        "collected_from_stream": stream_name,
                        "message": message,
                        "collection_sequence": len(self.collected_messages)
                    }
                    
                    self.collected_messages.append(collection_entry)
                    
                    # Update stats
                    self.collection_stats["total_collected"] += 1
                    current_time = time.time()
                    
                    if self.collection_stats["first_message_time"] is None:
                        self.collection_stats["first_message_time"] = current_time
                    
                    self.collection_stats["last_message_time"] = current_time
                    
                    logger.info(f"📥 {self.name} collected message from {message.get('original_generator', 'unknown')}: {message.get('original_id', 'unknown')}")
                    
            except Exception as e:
                # Handle collection errors gracefully
                logger.warning(f"⚠️ Collection error in {self.name}: {e}")
        
        # Small delay to prevent tight loop
        await asyncio.sleep(0.01)
    
    async def _cleanup_component_resources(self):
        """Clean up collector resources and report statistics"""
        total_time = 0
        if (self.collection_stats["first_message_time"] and 
            self.collection_stats["last_message_time"]):
            total_time = self.collection_stats["last_message_time"] - self.collection_stats["first_message_time"]
        
        logger.info(f"🧹 DataCollector '{self.name}' cleanup - collected {len(self.collected_messages)} messages over {total_time:.2f}s")
        
        # Log summary of collected data
        if self.collected_messages:
            logger.info(f"📊 Collection Summary:")
            logger.info(f"   First message: {self.collected_messages[0]['message'].get('original_id', 'unknown')}")
            logger.info(f"   Last message: {self.collected_messages[-1]['message'].get('original_id', 'unknown')}")
            logger.info(f"   Processing chain: {self.collected_messages[0]['message'].get('original_generator', 'unknown')} → processor → {self.name}")


async def demonstrate_component_lifecycle():
    """Demonstrate complete component lifecycle with three components"""
    logger.info("🚀 Starting Component Lifecycle Demonstration")
    logger.info("=" * 60)
    
    # Phase 1: Component Creation
    logger.info("📋 Phase 1: Creating Components")
    
    generator = DataGeneratorComponent("data_generator")
    processor = DataProcessorComponent("data_processor") 
    collector = DataCollectorComponent("data_collector")
    
    components = [generator, processor, collector]
    logger.info(f"✅ Created {len(components)} components")
    
    # Phase 2: Component Setup
    logger.info("📋 Phase 2: Setting Up Components")
    
    # Create harness context
    context = HarnessContext(
        harness_id="lifecycle_demo_harness",
        component_registry={comp.name: comp for comp in components},
        global_config={
            "demo_mode": True,
            "max_runtime": 30,
            "log_level": "INFO"
        }
    )
    
    # Setup all components
    for component in components:
        await component.setup(context)
        logger.info(f"✅ {component.name} setup complete - state: {component.current_state.value}")
    
    # Phase 3: Stream Connection Setup
    logger.info("📋 Phase 3: Establishing Stream Connections")
    
    # Create stream: generator → processor
    generator_to_processor_send, generator_to_processor_receive = anyio.create_memory_object_stream(buffer_size=50)
    generator.add_send_stream("output", generator_to_processor_send, "data_processor")
    processor.add_receive_stream("input", generator_to_processor_receive, "data_generator")
    
    # Create stream: processor → collector
    processor_to_collector_send, processor_to_collector_receive = anyio.create_memory_object_stream(buffer_size=50)
    processor.add_send_stream("output", processor_to_collector_send, "data_collector")
    collector.add_receive_stream("input", processor_to_collector_receive, "data_processor")
    
    logger.info("✅ Stream connections established:")
    logger.info("   data_generator → data_processor → data_collector")
    
    # Phase 4: Component Processing
    logger.info("📋 Phase 4: Starting Component Processing")
    
    # Start all components
    start_time = time.time()
    for component in components:
        await component.start_processing()
        logger.info(f"✅ {component.name} processing started - state: {component.current_state.value}")
    
    # Let the pipeline process for a while
    processing_duration = 8.0
    logger.info(f"🔄 Allowing pipeline to process for {processing_duration}s...")
    
    # Monitor progress
    await asyncio.sleep(processing_duration / 2)
    logger.info("📊 Mid-processing status:")
    for component in components:
        health = await component.health_check()
        logger.info(f"   {component.name}: healthy={health['healthy']}, state={health['state']}")
    
    await asyncio.sleep(processing_duration / 2)
    
    # Phase 5: Performance and Health Check
    logger.info("📋 Phase 5: Performance and Health Assessment")
    
    total_processing_time = time.time() - start_time
    logger.info(f"⏱️ Total processing time: {total_processing_time:.2f}s")
    
    for component in components:
        metrics = component.get_performance_metrics()
        logger.info(f"📊 {component.name} metrics:")
        logger.info(f"   Messages processed: {metrics['processing_metrics']['total_processed']}")
        logger.info(f"   Messages sent: {metrics['processing_metrics']['total_sent']}")
        logger.info(f"   Error count: {metrics['error_metrics']['error_count']}")
        logger.info(f"   Uptime: {metrics['uptime_seconds']:.2f}s")
    
    # Phase 6: Graceful Shutdown
    logger.info("📋 Phase 6: Graceful Component Shutdown")
    
    # Stop processing
    for component in components:
        await component.stop_processing()
        logger.info(f"🛑 {component.name} processing stopped - state: {component.current_state.value}")
    
    # Cleanup resources
    for component in components:
        await component.cleanup()
        logger.info(f"🧹 {component.name} cleanup complete - state: {component.current_state.value}")
    
    # Phase 7: Final Results Summary
    logger.info("📋 Phase 7: Final Results Summary")
    logger.info("=" * 60)
    
    # Component status summary
    logger.info("🏁 Final Component Status:")
    for component in components:
        status_summary = component.status.get_status_summary()
        logger.info(f"   {component.name}:")
        logger.info(f"     State: {status_summary['state']}")
        logger.info(f"     Healthy: {status_summary['is_healthy']}")
        logger.info(f"     Uptime: {status_summary['uptime_seconds']:.2f}s")
        logger.info(f"     Messages processed: {status_summary['metrics']['total_messages_processed']}")
        logger.info(f"     Error count: {status_summary['error_count']}")
    
    # Pipeline effectiveness
    generated_count = generator.message_count
    processed_count = processor.processed_count  
    collected_count = len(collector.collected_messages)
    
    logger.info("📈 Pipeline Effectiveness:")
    logger.info(f"   Messages generated: {generated_count}")
    logger.info(f"   Messages processed: {processed_count}")
    logger.info(f"   Messages collected: {collected_count}")
    
    if generated_count > 0:
        processing_efficiency = (processed_count / generated_count) * 100
        collection_efficiency = (collected_count / generated_count) * 100
        logger.info(f"   Processing efficiency: {processing_efficiency:.1f}%")
        logger.info(f"   Collection efficiency: {collection_efficiency:.1f}%")
    
    # Stream information
    logger.info("🔗 Stream Connection Summary:")
    for component in components:
        stream_info = component.get_stream_info()
        if stream_info["send_streams"] or stream_info["receive_streams"]:
            logger.info(f"   {component.name}:")
            for name, info in stream_info["send_streams"].items():
                logger.info(f"     Send '{name}' → {info['connected_to']}: {info['message_count']} messages")
            for name, info in stream_info["receive_streams"].items():
                logger.info(f"     Receive '{name}' ← {info['connected_from']}: {info['message_count']} messages")
    
    logger.info("✅ Component Lifecycle Demonstration Complete!")
    logger.info("=" * 60)


async def demonstrate_error_handling():
    """Demonstrate error handling and recovery mechanisms"""
    logger.info("🚀 Starting Error Handling Demonstration")
    logger.info("=" * 50)
    
    # Create a component that will encounter errors
    class ErrorProneComponent(HarnessComponent):
        def __init__(self):
            config = ComponentConfiguration(
                name="error_prone",
                component_type="error_test",
                service_type="test",
                base_type="transformer"
            )
            super().__init__(config)
            self.process_count = 0
            self.should_error_on = [3, 7]  # Error on these process calls
        
        async def process(self):
            self.process_count += 1
            if self.process_count in self.should_error_on:
                raise ValueError(f"Intentional error on process #{self.process_count}")
            await asyncio.sleep(0.1)
    
    error_component = ErrorProneComponent()
    await error_component.setup()
    
    logger.info("🧪 Starting component that will generate intentional errors...")
    await error_component.start_processing()
    
    # Let it run and encounter errors
    await asyncio.sleep(2.0)
    
    # Check error status
    health = await error_component.health_check()
    logger.info(f"🏥 Health after errors: {health}")
    
    # Attempt recovery
    logger.info("🔄 Attempting error recovery...")
    recovery_result = await error_component.status.attempt_recovery()
    logger.info(f"Recovery result: {recovery_result}")
    
    # Stop and cleanup
    await error_component.stop_processing()
    await error_component.cleanup()
    
    logger.info("✅ Error Handling Demonstration Complete!")


if __name__ == "__main__":
    async def main():
        logger.info("🎯 HarnessComponent Day 1 Lifecycle Demonstration")
        logger.info("🎯 Showing complete component lifecycle with stream communication")
        print()
        
        # Run main lifecycle demonstration
        await demonstrate_component_lifecycle()
        
        print()
        logger.info("-" * 60)
        print()
        
        # Run error handling demonstration
        await demonstrate_error_handling()
        
        logger.info("🎯 All demonstrations completed successfully!")
    
    # Run the demonstration
    asyncio.run(main())