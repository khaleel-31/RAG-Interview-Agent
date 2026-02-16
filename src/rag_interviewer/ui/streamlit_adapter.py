"""UI adapter for Streamlit-based front-end.

This module provides a minimal, test-friendly interface to render the UI
and capture user input. The goal is to decouple UI concerns from the engine
and pave the way for alternative front-ends in Phase-5.
"""

def render_ui(state=None):
    """Render the UI using Streamlit if available.

    For now, this is a light-weight adapter that the real UI glue can call
    to gather input in a test-friendly way. If Streamlit is not installed or
    not enabled, this function will simply return a sentinel value.
    """
    try:
        import streamlit as st  # type: ignore
        # Basic scaffold: in future we can wire actual UI elements here
        if state is None:
            state = {}
        # Expose a predictable interface for the engine to consume
        return {"ui_ready": True, "state": state}
    except Exception:
        # Non-UI environments (tests) gracefully degrade
        return {"ui_ready": False, "state": state or {}}

def prepare_ui_state(state=None):
    """Phase-B bridge hook: seed or enrich UI-driven state if possible.

    Currently a safe pass-through that can be extended as UI glue evolves.
    Returns a dict of state that can be consumed by the engine.
    """
    if state is None:
        state = {}
    try:
        # Future: pull from UI widgets or environment. For now, echo the input.
        return state
    except Exception:
        return {}
