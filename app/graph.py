"""Compatibility wrapper for legacy imports.

This module re-exports from rag_interviewer.graph for backward compatibility.
Note: src/ path must be in sys.path before importing this module.
"""
from rag_interviewer.graph import app, workflow, route_logic, memory

__all__ = ["app", "workflow", "route_logic", "memory"]
