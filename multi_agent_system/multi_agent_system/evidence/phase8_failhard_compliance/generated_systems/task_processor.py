#!/usr/bin/env python3
"""
Generated Transformer Component: task_processor
Processes task operations with business logic validation

This component follows the V5.1 harness-compatible Transformer pattern.
"""
import anyio
import logging
from typing import Dict, Any
from datetime import datetime
import uuid

from autocoder.components import Transformer


class GeneratedTransformer_task_processor(Transformer):
    """
    Processes task operations with business logic validation
    
    V5.1 harness-compatible Transformer that processes data from anyio input streams 
    and sends results to anyio output streams.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        
        # Configuration for task processing business logic
        self.max_tasks_per_user = config.get('max_tasks_per_user', 100) if config else 100
        self.auto_assign_enabled = config.get('auto_assign_enabled', True) if config else True
        self.priority_levels = config.get('priority_levels', ["low", "medium", "high", "urgent"]) if config else ["low", "medium", "high", "urgent"]
        self.processed_count = 0
        
    async def _transform_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task operations with business logic validation.
        
        Handles task creation, updates, assignments, and priority management
        according to business rules and user context.
        """
        self.processed_count += 1
        
        # Extract task operation and user context from inputs
        task_operation = inputs.get('task_operations', {})
        user_context = inputs.get('user_context', {})
        
        # Validate required inputs
        if not task_operation:
            return {"error": "No task operation provided", "processed_by": self.name}
        
        operation_type = task_operation.get('type', 'unknown')
        task_data = task_operation.get('data', {})
        user_id = user_context.get('user_id')
        
        try:
            if operation_type == 'create_task':
                return await self._process_task_creation(task_data, user_context)
            elif operation_type == 'update_task':
                return await self._process_task_update(task_data, user_context)
            elif operation_type == 'assign_task':
                return await self._process_task_assignment(task_data, user_context)
            elif operation_type == 'complete_task':
                return await self._process_task_completion(task_data, user_context)
            else:
                return {
                    "error": f"Unknown operation type: {operation_type}",
                    "processed_by": self.name,
                    "operation_count": self.processed_count
                }
        except Exception as e:
            return {
                "error": f"Task processing failed: {str(e)}",
                "processed_by": self.name,
                "operation_count": self.processed_count
            }
    
    async def _process_task_creation(self, task_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process task creation with business logic validation"""
        
        # Validate task data
        if not task_data.get('title'):
            return {"error": "Task title is required", "processed_by": self.name}
        
        # Apply business rules
        user_id = user_context.get('user_id')
        if not user_id:
            return {"error": "User context required for task creation", "processed_by": self.name}
        
        # Set priority with validation
        priority = task_data.get('priority', 'medium')
        if priority not in self.priority_levels:
            priority = 'medium'  # Default to medium if invalid
        
        # Generate processed task data
        processed_task = {
            "id": str(uuid.uuid4()),
            "title": task_data['title'],
            "description": task_data.get('description', ''),
            "priority": priority,
            "status": "pending",
            "assigned_to": user_id if self.auto_assign_enabled else None,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Generate notification
        notification = {
            "type": "task_created",
            "message": f"Task '{processed_task['title']}' created successfully",
            "task_id": processed_task['id'],
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "processed_tasks": processed_task,
            "task_notifications": notification,
            "processed_by": self.name,
            "operation_count": self.processed_count
        }
    
    async def _process_task_update(self, task_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process task updates with validation"""
        
        task_id = task_data.get('id')
        if not task_id:
            return {"error": "Task ID required for updates", "processed_by": self.name}
        
        user_id = user_context.get('user_id')
        
        # Apply business rules for updates
        updated_fields = {}
        if 'title' in task_data:
            updated_fields['title'] = task_data['title']
        if 'description' in task_data:
            updated_fields['description'] = task_data['description']
        if 'priority' in task_data and task_data['priority'] in self.priority_levels:
            updated_fields['priority'] = task_data['priority']
        if 'status' in task_data:
            updated_fields['status'] = task_data['status']
        
        updated_fields['updated_at'] = datetime.utcnow().isoformat()
        updated_fields['updated_by'] = user_id
        
        # Generate notification
        notification = {
            "type": "task_updated",
            "message": f"Task {task_id} updated successfully",
            "task_id": task_id,
            "user_id": user_id,
            "changes": list(updated_fields.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "processed_tasks": {"id": task_id, **updated_fields},
            "task_notifications": notification,
            "processed_by": self.name,
            "operation_count": self.processed_count
        }
    
    async def _process_task_assignment(self, task_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process task assignment with validation"""
        
        task_id = task_data.get('task_id')
        assignee_id = task_data.get('assignee_id')
        
        if not task_id or not assignee_id:
            return {"error": "Task ID and assignee ID required", "processed_by": self.name}
        
        user_id = user_context.get('user_id')
        
        # Process assignment
        updated_task = {
            "id": task_id,
            "assigned_to": assignee_id,
            "status": "assigned",
            "updated_at": datetime.utcnow().isoformat(),
            "assigned_by": user_id
        }
        
        notification = {
            "type": "task_assigned",
            "message": f"Task {task_id} assigned to user {assignee_id}",
            "task_id": task_id,
            "assignee_id": assignee_id,
            "assigned_by": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "processed_tasks": updated_task,
            "task_notifications": notification,
            "processed_by": self.name,
            "operation_count": self.processed_count
        }
    
    async def _process_task_completion(self, task_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process task completion with validation"""
        
        task_id = task_data.get('task_id')
        if not task_id:
            return {"error": "Task ID required for completion", "processed_by": self.name}
        
        user_id = user_context.get('user_id')
        
        # Process completion
        completed_task = {
            "id": task_id,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "completed_by": user_id,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        notification = {
            "type": "task_completed",
            "message": f"Task {task_id} marked as completed",
            "task_id": task_id,
            "completed_by": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "processed_tasks": completed_task,
            "task_notifications": notification,
            "processed_by": self.name,
            "operation_count": self.processed_count
        }
