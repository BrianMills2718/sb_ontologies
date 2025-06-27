#!/usr/bin/env python3
"""
Generated Source Component: task_source
Source component for task operations

This component follows the V5.1 harness-compatible pattern.
"""
import anyio
import logging
from typing import Dict, Any
from datetime import datetime
import uuid

from autocoder.components import Source


class GeneratedSource_task_source(Source):
    """
    Source component for task operations
    
    V5.1 harness-compatible Source that generates task operation data
    and sends it to anyio output streams.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.operation_count = 0
        
    async def _generate_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate task operation data for processing.
        
        OVERRIDES BASE METHOD - no default implementation used.
        """
        self.operation_count += 1
        
        # Generate realistic task operation data
        operation_types = ["create_task", "update_task", "list_tasks", "complete_task"]
        operation_type = operation_types[self.operation_count % len(operation_types)]
        
        base_data = {
            "type": operation_type,
            "timestamp": datetime.utcnow().isoformat(),
            "operation_id": str(uuid.uuid4()),
            "generated_by": self.name,
            "sequence": self.operation_count
        }
        
        if operation_type == "create_task":
            base_data["data"] = {
                "title": f"Generated Task {self.operation_count}",
                "description": f"Auto-generated task for testing - sequence {self.operation_count}",
                "priority": "medium",
                "assigned_to": None
            }
        elif operation_type == "update_task":
            base_data["data"] = {
                "task_id": f"task-{self.operation_count}",
                "updates": {
                    "status": "in_progress",
                    "priority": "high"
                }
            }
        elif operation_type == "complete_task":
            base_data["data"] = {
                "task_id": f"task-{self.operation_count}",
                "completion_notes": "Task completed successfully"
            }
        else:  # list_tasks
            base_data["data"] = {
                "filters": {
                    "status": "pending",
                    "limit": 10
                }
            }
        
        return {
            "task_operations": base_data,
            "metadata": {
                "source": self.name,
                "generated_at": datetime.utcnow().isoformat(),
                "sequence_number": self.operation_count
            }
        }
