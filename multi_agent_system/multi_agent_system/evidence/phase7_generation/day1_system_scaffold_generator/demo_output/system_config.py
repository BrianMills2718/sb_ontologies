#!/usr/bin/env python3
"""
Generated System Configuration
Generated from: Task Management API with Real-time Processing
"""

import os
from typing import Dict, Any

# System configuration
SYSTEM_CONFIG = {
    "harness": {
        "startup_timeout": 30.0,
        "shutdown_timeout": 10.0,
        "health_check_interval": 5.0,
        "stream_buffer_size": 100,
        "enable_health_monitoring": True,
        "enable_performance_monitoring": True,
        "log_level": "INFO"
    },
    "components": {
    "api_gateway": {
        "port": 8080,
        "host": "0.0.0.0",
        "cors_enabled": true,
        "rate_limit": 1000
    },
    "task_controller": {
        "max_concurrent_tasks": 100,
        "processing_timeout": 30,
        "retry_attempts": 3
    },
    "task_store": {
        "storage_type": "redis",
        "connection_pool_size": 10,
        "key_prefix": "tasks:",
        "ttl_seconds": 3600
    },
    "data_processor": {
        "processing_mode": "async",
        "batch_size": 10,
        "processing_interval": 1.0
    }
},
    "metadata": {
    "version": "1.0",
    "author": "V5.0 Two-Phase Generation Pipeline",
    "created": "2024-01-01T00:00:00Z"
}
}

def get_config() -> Dict[str, Any]:
    """Get system configuration"""
    return SYSTEM_CONFIG.copy()

def get_component_config(component_name: str) -> Dict[str, Any]:
    """Get configuration for specific component"""
    return SYSTEM_CONFIG.get("components", {}).get(component_name, {})
