#!/usr/bin/env python3
"""
Generated System Configuration
Generated from: Task Management System with REST API
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
        "api_gateway": {"port": 8080, "host": "0.0.0.0"},
        "task_controller": {"max_concurrent_tasks": 20},
        "task_store": {"storage_type": "memory"}
    },
    "metadata": {"version": "1.0", "test_system": True}
}

def get_config() -> Dict[str, Any]:
    """Get system configuration"""
    return SYSTEM_CONFIG.copy()

def get_component_config(component_name: str) -> Dict[str, Any]:
    """Get configuration for specific component"""
    return SYSTEM_CONFIG.get("components", {}).get(component_name, {})
