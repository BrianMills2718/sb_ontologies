#!/usr/bin/env python3
"""
Full Harness Integration Test - Week 1 Complete System Test
=========================================================

Comprehensive integration test of the complete SystemExecutionHarness
architecture including all Day 1-3 components working together in a
realistic system scenario.

Test Scenarios:
1. Multi-component data processing pipeline
2. Complex stream communication patterns  
3. Error recovery and component failure scenarios
4. Performance benchmarking under load
5. Health monitoring and system diagnostics
6. Graceful shutdown and resource cleanup
"""

import asyncio
import anyio
import time
import logging
import random
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from evidence.phase2_component_library.day1_core_component_classes.enhanced_base import ComponentConfiguration
from evidence.phase6_harness.day1_harness_component.harness_component import HarnessComponent
from evidence.phase6_harness.day1_harness_component.component_status import ComponentState
from evidence.phase6_harness.day2_execution_harness.system_execution_harness import (
    SystemExecutionHarness, HarnessConfiguration, HarnessState
)
from evidence.phase6_harness.day3_stream_communication.message_protocol import MessageType
from evidence.phase6_harness.day3_stream_communication.stream_framework import StreamFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationTestResults:
    """Results from integration testing"""
    test_name: str
    start_time: float
    end_time: float
    success: bool
    components_tested: int
    messages_processed: int
    errors_encountered: int
    performance_metrics: Dict[str, Any]
    health_checks_passed: int
    details: List[str]
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def throughput(self) -> float:
        return self.messages_processed / self.duration if self.duration > 0 else 0


class DataIngestionComponent(HarnessComponent):
    """Simulates data ingestion from external sources"""
    
    def __init__(self, name: str, data_rate: float = 2.0):
        config = ComponentConfiguration(
            name=name,
            component_type="data_ingestion",
            service_type="data_source",
            base_type="source"
        )
        super().__init__(config)
        self.data_rate = data_rate  # messages per second
        self.message_count = 0
        self.last_send_time = 0
        self.total_messages_to_send = 50
        self.data_sources = ["sensor_1", "sensor_2", "api_feed", "database"]
    
    async def process(self):
        """Generate realistic data ingestion messages"""
        current_time = time.time()
        
        if (current_time - self.last_send_time >= (1.0 / self.data_rate) and 
            self.message_count < self.total_messages_to_send):
            
            # Generate realistic data
            data_source = random.choice(self.data_sources)
            message = {
                "id": f"data_{self.message_count:04d}",
                "source": data_source,
                "timestamp": current_time,
                "data": {
                    "temperature": random.uniform(20.0, 35.0),
                    "humidity": random.uniform(30.0, 80.0),
                    "pressure": random.uniform(1000.0, 1020.0),
                    "status": random.choice(["OK", "WARNING", "ERROR"])
                },
                "metadata": {
                    "ingestion_node": self.name,
                    "batch_id": f"batch_{self.message_count // 10}",
                    "priority": random.choice([1, 2, 3])
                }
            }
            
            # Send to all output streams
            for stream_name in self.send_streams.keys():
                await self.send_message(stream_name, message)
            
            self.message_count += 1
            self.last_send_time = current_time
        
        await asyncio.sleep(0.01)


class DataValidationComponent(HarnessComponent):
    """Validates and filters incoming data"""
    
    def __init__(self, name: str, error_rate: float = 0.1):
        config = ComponentConfiguration(
            name=name,
            component_type="data_validation",
            service_type="data_processor",
            base_type="transformer"
        )
        super().__init__(config)
        self.error_rate = error_rate
        self.validated_messages = []
        self.rejected_messages = []
        self.validation_errors = 0
    
    async def process(self):
        """Validate incoming data messages"""
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    # Simulate validation process
                    await asyncio.sleep(0.02)  # Processing delay
                    
                    is_valid = await self._validate_message(message)
                    
                    if is_valid:
                        validated_message = {
                            "original_id": message.get("id"),
                            "validated_at": time.time(),
                            "validator": self.name,
                            "validation_result": "VALID",
                            "data": message.get("data"),
                            "metadata": message.get("metadata", {})
                        }
                        validated_message["metadata"]["validated_by"] = self.name
                        
                        self.validated_messages.append(validated_message)
                        
                        # Forward to output streams
                        for output_stream in self.send_streams.keys():
                            await self.send_message(output_stream, validated_message)
                    else:
                        self.rejected_messages.append(message)
                        
            except Exception as e:
                self.validation_errors += 1
                logger.warning(f"⚠️ Validation error in {self.name}: {e}")
        
        await asyncio.sleep(0.01)
    
    async def _validate_message(self, message: Any) -> bool:
        """Validate message content"""
        try:
            # Basic structure validation
            if not isinstance(message, dict):
                return False
            
            if "data" not in message:
                return False
            
            data = message["data"]
            
            # Validate data ranges
            if "temperature" in data:
                if not (10.0 <= data["temperature"] <= 50.0):
                    return False
            
            if "humidity" in data:
                if not (0.0 <= data["humidity"] <= 100.0):
                    return False
            
            # Simulate random validation failures
            if random.random() < self.error_rate:
                return False
            
            return True
            
        except Exception:
            return False


class DataEnrichmentComponent(HarnessComponent):
    """Enriches validated data with additional information"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="data_enrichment",
            service_type="data_processor", 
            base_type="transformer"
        )
        super().__init__(config)
        self.enriched_messages = []
        self.enrichment_cache = {}
    
    async def process(self):
        """Enrich validated data messages"""
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    # Simulate enrichment process
                    await asyncio.sleep(0.03)  # Processing delay
                    
                    enriched_message = await self._enrich_message(message)
                    self.enriched_messages.append(enriched_message)
                    
                    # Forward enriched message
                    for output_stream in self.send_streams.keys():
                        await self.send_message(output_stream, enriched_message)
                        
            except Exception as e:
                logger.warning(f"⚠️ Enrichment error in {self.name}: {e}")
        
        await asyncio.sleep(0.01)
    
    async def _enrich_message(self, message: Any) -> Dict[str, Any]:
        """Enrich message with additional data"""
        enriched = {
            "original_id": message.get("original_id"),
            "enriched_at": time.time(),
            "enricher": self.name,
            "data": message.get("data", {}),
            "metadata": message.get("metadata", {}),
            "enrichment": {
                "location": await self._get_location_data(message),
                "weather_context": await self._get_weather_context(message),
                "alerts": await self._check_alerts(message),
                "processing_latency": time.time() - message.get("validated_at", time.time())
            }
        }
        
        return enriched
    
    async def _get_location_data(self, message: Any) -> Dict[str, Any]:
        """Simulate location data lookup"""
        source = message.get("source", "unknown")
        
        if source not in self.enrichment_cache:
            # Simulate external API call
            await asyncio.sleep(0.01)
            self.enrichment_cache[source] = {
                "region": random.choice(["North", "South", "East", "West"]),
                "zone": f"Zone_{random.randint(1, 10)}",
                "coordinates": {
                    "lat": round(random.uniform(40.0, 50.0), 4),
                    "lon": round(random.uniform(-120.0, -110.0), 4)
                }
            }
        
        return self.enrichment_cache[source]
    
    async def _get_weather_context(self, message: Any) -> Dict[str, Any]:
        """Simulate weather context lookup"""
        await asyncio.sleep(0.005)  # Simulate API delay
        return {
            "conditions": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
            "severity": random.choice(["low", "medium", "high"]),
            "forecast_confidence": random.uniform(0.7, 0.99)
        }
    
    async def _check_alerts(self, message: Any) -> List[str]:
        """Check for alerts based on data"""
        alerts = []
        data = message.get("data", {})
        
        if data.get("temperature", 0) > 30:
            alerts.append("HIGH_TEMPERATURE")
        
        if data.get("humidity", 0) > 70:
            alerts.append("HIGH_HUMIDITY")
        
        if data.get("status") == "ERROR":
            alerts.append("SENSOR_ERROR")
        
        return alerts


class DataAggregationComponent(HarnessComponent):
    """Aggregates enriched data for final output"""
    
    def __init__(self, name: str, batch_size: int = 5):
        config = ComponentConfiguration(
            name=name,
            component_type="data_aggregation",
            service_type="data_sink",
            base_type="sink"
        )
        super().__init__(config)
        self.batch_size = batch_size
        self.message_buffer = []
        self.aggregated_batches = []
        self.total_processed = 0
    
    async def process(self):
        """Aggregate enriched messages into batches"""
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    self.message_buffer.append(message)
                    self.total_processed += 1
                    
                    # Process batch when buffer is full
                    if len(self.message_buffer) >= self.batch_size:
                        batch = await self._create_batch()
                        self.aggregated_batches.append(batch)
                        
                        # Forward batch if there are output streams
                        for output_stream in self.send_streams.keys():
                            await self.send_message(output_stream, batch)
                        
                        # Clear buffer
                        self.message_buffer = []
                        
            except Exception as e:
                logger.warning(f"⚠️ Aggregation error in {self.name}: {e}")
        
        await asyncio.sleep(0.01)
    
    async def _create_batch(self) -> Dict[str, Any]:
        """Create aggregated batch from buffered messages"""
        if not self.message_buffer:
            return {}
        
        batch = {
            "batch_id": str(uuid.uuid4()),
            "created_at": time.time(),
            "aggregator": self.name,
            "message_count": len(self.message_buffer),
            "messages": self.message_buffer.copy(),
            "summary": {
                "temperature_avg": self._calculate_average("temperature"),
                "humidity_avg": self._calculate_average("humidity"),
                "pressure_avg": self._calculate_average("pressure"),
                "alert_count": self._count_alerts(),
                "sources": list(set(msg.get("metadata", {}).get("source", "unknown") 
                                  for msg in self.message_buffer)),
                "processing_latencies": [msg.get("enrichment", {}).get("processing_latency", 0) 
                                       for msg in self.message_buffer]
            }
        }
        
        return batch
    
    def _calculate_average(self, field: str) -> float:
        """Calculate average for a numeric field"""
        values = []
        for msg in self.message_buffer:
            data = msg.get("data", {})
            if field in data and isinstance(data[field], (int, float)):
                values.append(data[field])
        
        return sum(values) / len(values) if values else 0.0
    
    def _count_alerts(self) -> int:
        """Count total alerts in the batch"""
        total_alerts = 0
        for msg in self.message_buffer:
            enrichment = msg.get("enrichment", {})
            alerts = enrichment.get("alerts", [])
            total_alerts += len(alerts)
        
        return total_alerts


class SystemMonitoringComponent(HarnessComponent):
    """Monitors system health and performance"""
    
    def __init__(self, name: str):
        config = ComponentConfiguration(
            name=name,
            component_type="system_monitoring",
            service_type="monitoring",
            base_type="sink"
        )
        super().__init__(config)
        self.health_reports = []
        self.performance_metrics = {}
        self.last_report_time = 0
        self.report_interval = 5.0  # seconds
    
    async def process(self):
        """Monitor system health and collect metrics"""
        current_time = time.time()
        
        # Generate periodic health reports
        if current_time - self.last_report_time >= self.report_interval:
            health_report = await self._generate_health_report()
            self.health_reports.append(health_report)
            self.last_report_time = current_time
        
        # Process any incoming monitoring data
        for stream_name in self.receive_streams.keys():
            try:
                message = await self.receive_message(stream_name, timeout=0.001)
                if message is not None:
                    await self._process_monitoring_data(message)
            except Exception as e:
                logger.warning(f"⚠️ Monitoring error in {self.name}: {e}")
        
        await asyncio.sleep(0.1)
    
    async def _generate_health_report(self) -> Dict[str, Any]:
        """Generate system health report"""
        return {
            "timestamp": time.time(),
            "monitor": self.name,
            "system_status": "healthy",
            "uptime": time.time() - (self.start_time or time.time()),
            "metrics_collected": len(self.performance_metrics),
            "reports_generated": len(self.health_reports),
            "memory_usage": "normal",  # Simplified for demo
            "cpu_usage": "normal"      # Simplified for demo
        }
    
    async def _process_monitoring_data(self, message: Any):
        """Process incoming monitoring data"""
        # Store metrics for analysis
        msg_id = message.get("batch_id", str(uuid.uuid4()))
        self.performance_metrics[msg_id] = {
            "received_at": time.time(),
            "message_count": message.get("message_count", 0),
            "processing_latencies": message.get("summary", {}).get("processing_latencies", []),
            "alert_count": message.get("summary", {}).get("alert_count", 0)
        }


async def run_integration_test_scenario_1() -> IntegrationTestResults:
    """
    Integration Test Scenario 1: Basic Pipeline Functionality
    Tests basic data flow through the complete pipeline
    """
    logger.info("🧪 Starting Integration Test Scenario 1: Basic Pipeline")
    start_time = time.time()
    
    try:
        # Create harness with optimized configuration
        config = HarnessConfiguration(
            startup_timeout=10.0,
            shutdown_timeout=5.0,
            health_check_interval=2.0,
            stream_buffer_size=200,
            enable_health_monitoring=True
        )
        
        harness = SystemExecutionHarness(config)
        
        # Create components
        ingestion = DataIngestionComponent("data_ingestion", data_rate=3.0)
        validation = DataValidationComponent("data_validation", error_rate=0.05)
        enrichment = DataEnrichmentComponent("data_enrichment")
        aggregation = DataAggregationComponent("data_aggregation", batch_size=3)
        monitoring = SystemMonitoringComponent("system_monitoring")
        
        # Register components with priorities
        harness.register_component("ingestion", ingestion, start_priority=1)
        harness.register_component("validation", validation, start_priority=2, dependencies=["ingestion"])
        harness.register_component("enrichment", enrichment, start_priority=3, dependencies=["validation"])
        harness.register_component("aggregation", aggregation, start_priority=4, dependencies=["enrichment"])
        harness.register_component("monitoring", monitoring, start_priority=5)
        
        # Connect pipeline
        harness.connect("ingestion.output", "validation.input", buffer_size=100)
        harness.connect("validation.output", "enrichment.input", buffer_size=100)
        harness.connect("enrichment.output", "aggregation.input", buffer_size=100)
        harness.connect("aggregation.output", "monitoring.input", buffer_size=50)
        
        # Run the pipeline
        async def run_pipeline():
            await harness.run()
        
        pipeline_task = asyncio.create_task(run_pipeline())
        
        # Let it run for a while
        await asyncio.sleep(10.0)
        
        # Collect intermediate metrics
        status = harness.get_status()
        logger.info(f"📊 Mid-test status: {status['components']['healthy']}/{status['components']['total']} components healthy")
        
        # Continue running
        await asyncio.sleep(5.0)
        
        # Stop the harness
        await harness.stop()
        
        # Wait for pipeline to complete
        try:
            await asyncio.wait_for(pipeline_task, timeout=10.0)
        except asyncio.TimeoutError:
            pipeline_task.cancel()
        
        # Collect final results
        final_status = harness.get_status()
        
        # Verify results
        messages_ingested = ingestion.message_count
        messages_validated = len(validation.validated_messages)
        messages_enriched = len(enrichment.enriched_messages)
        batches_created = len(aggregation.aggregated_batches)
        health_reports = len(monitoring.health_reports)
        
        # Calculate performance metrics
        end_time = time.time()
        duration = end_time - start_time
        total_processed = messages_validated + messages_enriched + batches_created
        
        performance_metrics = {
            "pipeline_duration": duration,
            "messages_ingested": messages_ingested,
            "messages_validated": messages_validated,
            "messages_enriched": messages_enriched,
            "batches_created": batches_created,
            "health_reports": health_reports,
            "throughput_msg_per_sec": total_processed / duration,
            "validation_error_rate": len(validation.rejected_messages) / max(1, messages_ingested),
            "average_batch_size": aggregation.total_processed / max(1, batches_created),
            "harness_startup_time": final_status.get("performance", {}).get("total_startup_time", 0)
        }
        
        # Determine success
        success = (
            messages_validated > 0 and
            messages_enriched > 0 and
            batches_created > 0 and
            final_status["components"]["failed"] == 0 and
            validation.validation_errors < 5  # Allow some validation errors
        )
        
        details = [
            f"Messages ingested: {messages_ingested}",
            f"Messages validated: {messages_validated}",
            f"Messages enriched: {messages_enriched}",
            f"Batches created: {batches_created}",
            f"Health reports: {health_reports}",
            f"Pipeline duration: {duration:.2f}s",
            f"Throughput: {performance_metrics['throughput_msg_per_sec']:.2f} msg/s",
            f"Components healthy: {final_status['components']['healthy']}/{final_status['components']['total']}"
        ]
        
        return IntegrationTestResults(
            test_name="Basic Pipeline Functionality",
            start_time=start_time,
            end_time=end_time,
            success=success,
            components_tested=5,
            messages_processed=total_processed,
            errors_encountered=validation.validation_errors,
            performance_metrics=performance_metrics,
            health_checks_passed=health_reports,
            details=details
        )
        
    except Exception as e:
        logger.error(f"❌ Integration test scenario 1 failed: {e}")
        return IntegrationTestResults(
            test_name="Basic Pipeline Functionality",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            components_tested=5,
            messages_processed=0,
            errors_encountered=1,
            performance_metrics={},
            health_checks_passed=0,
            details=[f"Test failed with error: {e}"]
        )


async def run_integration_test_scenario_2() -> IntegrationTestResults:
    """
    Integration Test Scenario 2: Error Recovery and Resilience
    Tests system behavior under component failures and recovery
    """
    logger.info("🧪 Starting Integration Test Scenario 2: Error Recovery")
    start_time = time.time()
    
    try:
        # Create harness
        harness = SystemExecutionHarness(HarnessConfiguration(
            startup_timeout=5.0,
            shutdown_timeout=3.0,
            health_check_interval=1.0
        ))
        
        # Create components with higher error rates
        ingestion = DataIngestionComponent("ingestion", data_rate=5.0)
        validation = DataValidationComponent("validation", error_rate=0.3)  # High error rate
        monitoring = SystemMonitoringComponent("monitoring")
        
        # Register components
        harness.register_component("ingestion", ingestion)
        harness.register_component("validation", validation)
        harness.register_component("monitoring", monitoring)
        
        # Connect with smaller buffers to test backpressure
        harness.connect("ingestion.output", "validation.input", buffer_size=10)
        harness.connect("validation.output", "monitoring.input", buffer_size=10)
        
        # Run pipeline
        async def run_pipeline():
            await harness.run()
        
        pipeline_task = asyncio.create_task(run_pipeline())
        
        # Let it run and accumulate errors
        await asyncio.sleep(8.0)
        
        # Stop and analyze
        await harness.stop()
        
        try:
            await asyncio.wait_for(pipeline_task, timeout=5.0)
        except asyncio.TimeoutError:
            pipeline_task.cancel()
        
        # Collect results
        final_status = harness.get_status()
        
        messages_processed = len(validation.validated_messages) + len(validation.rejected_messages)
        errors = validation.validation_errors + len(validation.rejected_messages)
        
        performance_metrics = {
            "total_ingested": ingestion.message_count,
            "total_processed": messages_processed,
            "validation_errors": validation.validation_errors,
            "messages_rejected": len(validation.rejected_messages),
            "error_rate": errors / max(1, ingestion.message_count),
            "system_resilience": final_status["components"]["healthy"] / max(1, final_status["components"]["total"])
        }
        
        # Success if system handled errors gracefully
        success = (
            final_status["components"]["healthy"] > 0 and
            messages_processed > 0 and
            performance_metrics["error_rate"] > 0.2  # Verify we actually tested error scenarios
        )
        
        details = [
            f"Messages ingested: {ingestion.message_count}",
            f"Messages processed: {messages_processed}",
            f"Validation errors: {validation.validation_errors}",
            f"Messages rejected: {len(validation.rejected_messages)}",
            f"Error rate: {performance_metrics['error_rate']:.2%}",
            f"System resilience: {performance_metrics['system_resilience']:.2%}"
        ]
        
        return IntegrationTestResults(
            test_name="Error Recovery and Resilience",
            start_time=start_time,
            end_time=time.time(),
            success=success,
            components_tested=3,
            messages_processed=messages_processed,
            errors_encountered=errors,
            performance_metrics=performance_metrics,
            health_checks_passed=len(monitoring.health_reports),
            details=details
        )
        
    except Exception as e:
        logger.error(f"❌ Integration test scenario 2 failed: {e}")
        return IntegrationTestResults(
            test_name="Error Recovery and Resilience",
            start_time=start_time,
            end_time=time.time(),
            success=False,
            components_tested=3,
            messages_processed=0,
            errors_encountered=1,
            performance_metrics={},
            health_checks_passed=0,
            details=[f"Test failed with error: {e}"]
        )


async def run_all_integration_tests():
    """Run all integration test scenarios"""
    logger.info("🚀 Starting Full Harness Integration Tests")
    logger.info("=" * 80)
    
    test_results = []
    overall_start = time.time()
    
    # Run test scenarios
    scenarios = [
        run_integration_test_scenario_1,
        run_integration_test_scenario_2
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"📋 Running test scenario {i}/{len(scenarios)}")
        try:
            result = await scenario()
            test_results.append(result)
            
            # Log results
            status = "✅ PASSED" if result.success else "❌ FAILED"
            logger.info(f"{status} {result.test_name}")
            logger.info(f"   Duration: {result.duration:.2f}s")
            logger.info(f"   Messages: {result.messages_processed}")
            logger.info(f"   Errors: {result.errors_encountered}")
            
            if result.success:
                logger.info(f"   Throughput: {result.throughput:.2f} msg/s")
            
            for detail in result.details[:3]:  # Show first 3 details
                logger.info(f"   {detail}")
                
        except Exception as e:
            logger.error(f"❌ Test scenario {i} failed with exception: {e}")
            # Create failed result
            failed_result = IntegrationTestResults(
                test_name=f"Scenario {i}",
                start_time=time.time(),
                end_time=time.time(),
                success=False,
                components_tested=0,
                messages_processed=0,
                errors_encountered=1,
                performance_metrics={},
                health_checks_passed=0,
                details=[f"Exception: {e}"]
            )
            test_results.append(failed_result)
        
        # Small delay between tests
        await asyncio.sleep(1.0)
    
    # Generate overall summary
    overall_duration = time.time() - overall_start
    passed_tests = sum(1 for result in test_results if result.success)
    total_tests = len(test_results)
    total_messages = sum(result.messages_processed for result in test_results)
    total_errors = sum(result.errors_encountered for result in test_results)
    
    logger.info("=" * 80)
    logger.info("📊 Integration Test Summary")
    logger.info(f"   Tests passed: {passed_tests}/{total_tests}")
    logger.info(f"   Success rate: {passed_tests/total_tests*100:.1f}%")
    logger.info(f"   Total duration: {overall_duration:.2f}s")
    logger.info(f"   Total messages processed: {total_messages}")
    logger.info(f"   Total errors encountered: {total_errors}")
    
    if total_messages > 0 and overall_duration > 0:
        overall_throughput = total_messages / overall_duration
        logger.info(f"   Overall throughput: {overall_throughput:.2f} msg/s")
    
    # Detailed results
    logger.info("\n📋 Detailed Test Results:")
    for result in test_results:
        status = "✅" if result.success else "❌"
        logger.info(f"   {status} {result.test_name}")
        logger.info(f"      Duration: {result.duration:.2f}s")
        logger.info(f"      Components: {result.components_tested}")
        logger.info(f"      Messages: {result.messages_processed}")
        logger.info(f"      Errors: {result.errors_encountered}")
        if result.success and result.throughput > 0:
            logger.info(f"      Throughput: {result.throughput:.2f} msg/s")
    
    # Overall success determination
    overall_success = passed_tests == total_tests and total_messages > 0
    
    if overall_success:
        logger.info("🎉 All integration tests PASSED!")
    else:
        logger.info("❌ Some integration tests FAILED!")
    
    return {
        "overall_success": overall_success,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "success_rate": passed_tests/total_tests*100,
        "total_duration": overall_duration,
        "total_messages": total_messages,
        "total_errors": total_errors,
        "overall_throughput": total_messages / overall_duration if overall_duration > 0 else 0,
        "test_results": test_results
    }


if __name__ == "__main__":
    async def main():
        logger.info("🎯 SystemExecutionHarness Full Integration Test Suite")
        logger.info("🎯 Testing complete Phase 6 architecture with realistic workloads")
        
        results = await run_all_integration_tests()
        
        # Return results for external evaluation
        return results
    
    # Run the integration tests
    asyncio.run(main())