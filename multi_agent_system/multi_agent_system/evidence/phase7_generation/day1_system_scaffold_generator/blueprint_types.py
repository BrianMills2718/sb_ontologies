#!/usr/bin/env python3
"""
Blueprint Types for Phase 7 Generation Pipeline
===============================================

Simplified blueprint types for scaffold generation without heavy dependencies.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SystemBlueprint:
    """Simplified system blueprint representation for generation"""
    description: str
    components: List[Dict[str, Any]]
    reasonableness_checks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentLogic:
    """Component logic representation for generation"""
    business_methods: List[Dict[str, Any]] = field(default_factory=list)
    processing_logic: Dict[str, Any] = field(default_factory=dict)
    stream_handlers: Dict[str, Any] = field(default_factory=dict)
    initialization_code: Optional[str] = None
    cleanup_code: Optional[str] = None


# Export main classes
__all__ = ['SystemBlueprint', 'ComponentLogic']