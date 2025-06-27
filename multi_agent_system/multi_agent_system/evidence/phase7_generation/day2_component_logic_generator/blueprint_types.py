#!/usr/bin/env python3
"""
Blueprint Types for Phase 7 Generation Pipeline
===============================================

Simplified blueprint types for component generation without heavy dependencies.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ComponentLogic:
    """Component logic representation for generation"""
    business_methods: List[Dict[str, Any]] = field(default_factory=list)
    processing_logic: Dict[str, Any] = field(default_factory=dict)
    stream_handlers: Dict[str, Any] = field(default_factory=dict)
    initialization_code: Optional[str] = None
    cleanup_code: Optional[str] = None


# Export main classes
__all__ = ['ComponentLogic']