"""
Multi-Agent Development System

A proven methodology for implementing development phases with 100/100 quality standards.
Uses isolated implementation agents, objective external evaluation, and automatic remediation.
"""

from .auto_phase_manager import AutoPhaseManager
from .multi_agent_toolkit import MultiAgentToolkit, quick_phase

__version__ = "1.0.0"
__all__ = ["AutoPhaseManager", "MultiAgentToolkit", "quick_phase"]