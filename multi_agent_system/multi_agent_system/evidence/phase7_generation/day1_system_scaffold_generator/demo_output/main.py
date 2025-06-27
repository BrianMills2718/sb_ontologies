#!/usr/bin/env python3
"""
Generated SystemExecutionHarness-based system
Generated from: Natural Language via V5.0 Two-Phase Generation Pipeline
Generated on: 2025-06-23T11:00:02.443790
"""

import asyncio
import logging
from pathlib import Path
import sys
import os

# Add component paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'components'))

# Import SystemExecutionHarness
from evidence.phase6_harness.day2_execution_harness.system_execution_harness import (
    SystemExecutionHarness, HarnessConfiguration
)

# Import generated components
from components.api_gateway import APIGateway
from components.task_controller import TaskController
from components.task_store import TaskStore
from components.data_processor import DataProcessor

# Import configuration
from config.system_config import get_config, get_component_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main harness orchestration function"""
    logger.info("🚀 Starting SystemExecutionHarness-based system...")
    
    try:
        # Load system configuration
        system_config = get_config()
        harness_config = HarnessConfiguration(**system_config.get('harness', {}))
        
        # Initialize harness
        harness = SystemExecutionHarness(harness_config)
        logger.info("✨ SystemExecutionHarness initialized")
        
        # Component registration

        # Register api_gateway component
        api_gateway_config = {
    "port": 8080,
    "host": "0.0.0.0",
    "cors_enabled": true,
    "rate_limit": 1000
}
        api_gateway_component = APIGateway(api_gateway_config)
        harness.register_component('api_gateway', api_gateway_component)

        # Register task_controller component
        task_controller_config = {
    "max_concurrent_tasks": 100,
    "processing_timeout": 30,
    "retry_attempts": 3
}
        task_controller_component = TaskController(task_controller_config)
        harness.register_component('task_controller', task_controller_component)

        # Register task_store component
        task_store_config = {
    "storage_type": "redis",
    "connection_pool_size": 10,
    "key_prefix": "tasks:",
    "ttl_seconds": 3600
}
        task_store_component = TaskStore(task_store_config)
        harness.register_component('task_store', task_store_component)

        # Register data_processor component
        data_processor_config = {
    "processing_mode": "async",
    "batch_size": 10,
    "processing_interval": 1.0
}
        data_processor_component = DataProcessor(data_processor_config)
        harness.register_component('data_processor', data_processor_component)
        
        logger.info("📝 All components registered")
        
        # Stream connections
        # Stream connections
        harness.connect('api_gateway.requests', 'task_controller.input')
        harness.connect('task_controller.store_commands', 'task_store.input')
        harness.connect('task_controller.process_requests', 'data_processor.input')
        harness.connect('task_store.responses', 'task_controller.store_data')
        harness.connect('data_processor.processed_data', 'task_controller.processed_results')
        
        logger.info("🔗 All stream connections established")
        
        # Start system
        logger.info("▶️ Starting harness system...")
        await harness.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ System startup failed: {e}")
        raise
    finally:
        logger.info("🏁 System shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System interrupted by user")
    except Exception as e:
        print(f"❌ System failed: {e}")
        sys.exit(1)
