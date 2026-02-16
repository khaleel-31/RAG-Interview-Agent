Phase 2 Design — Modular Python Patch Plan (high level)

- Goals
  - Solidify a modular, Pythonic architecture with clear domain boundaries and DI-friendly components.
  - Separate core business logic from IO/UI and external services.

- Proposed package layout (inspired by src layout)
  - src/rag_interviewer/
    - __init__.py
    - core/
      - __init__.py
      - route_logic.py (existing core logic)
      - models.py (domain data classes, if needed)
    - adapters/
      - __init__.py
      - embeddings.py (adapter for embeddings)
      - llm.py (adapter for LLM calls)
      - chroma.py (adapter for vector store)
    - config/
      - __init__.py
      - config.py (central config and defaults)
    - ui/
      - __init__.py
      - streamlit_adapter.py (UI glue to core)
    - data/
      - __init__.py
      - repositories/
    - main.py (or bootstrap for CLI/UI)
  - tests/
    - core/
      - test_route_logic.py (example)

- Phase 2 patch plan in multiple steps
  1) Introduce a centralized config and logging (already started in patch series) and create a consistent DI surface for embeddings/LLMs.
  2) Extract core business logic (route_logic) to be completely independent from IO and services.
  3) Implement adapters for external services behind interfaces; ensure unit tests can mock these adapters.
  4) Create a UI adapter that wraps Streamlit calls and exposes a stable API for tests.
  5) Add unit tests (pytest) for core logic and adapters; ensure type hints and docstrings across public APIs.

- Patch sequencing
  - Patch A: Create the recommended src layout scaffolding (dirs and __init__ files).
  - Patch B: Move or aliases for core modules to new layout (non-destructive if possible, using imports that resolve to new paths).
  - Patch C: Implement adapters and config consolidation (completed in Phase 2 patch plan steps above).
  - Patch D: Add UI adapter module and tests for core logic.
  - Patch E: Add CI/test script and typing checks (mypy/ruff) as dev tooling.

- Acceptance criteria
  - All core logic unit-testable without requiring Streamlit or external services.
  - DI surface present for embeddings/LLMs.
  - Clear separation between engine, adapters, and UI glue.
  - Phase-2 documentation and plan completed.
