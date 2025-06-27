#!/usr/bin/env python3
"""
Base HarnessComponent class for all Autocoder 4.3 components
"""
from typing import Dict, Any
from ..orchestration.component import Component


class HarnessComponent(Component):
    """
    System-first compatible base class for all generated components.
    Uses anyio streams exclusively - NO QUEUES.
    """
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.component_type = config.get('type', 'Unknown') if config else 'Unknown'
        
        # Component-specific setup hooks (optional overrides)
    async def _start_component(self):
        """Component-specific startup logic"""
        pass
    
    async def _stop_component(self):
        """Component-specific shutdown logic"""
        pass
    
    def _cleanup_component(self):
        """Component-specific cleanup logic"""
        pass