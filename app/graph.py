"""Compatibility wrapper for legacy imports.

This module re-exports from src/rag_interviewer to maintain backward compatibility
with code that imports from app.graph during the migration phase.
"""
import sys
from pathlib import Path

# Add src to path if not already present
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Re-export from new location
from rag_interviewer.graph import app, workflow, route_logic, memory

__all__ = ["app", "workflow", "route_logic", "memory"]
