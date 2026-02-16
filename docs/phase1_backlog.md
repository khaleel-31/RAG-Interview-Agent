# Phase 1 Backlog (prioritized)

- High Impact / Quick Wins
- B1 Logging Layer
- B2 Central Config
- B3 External Adapters (IO isolation)
- B4 UI-Core separation (engine/core layer)
- B5 Unit tests for core logic (route_logic, evaluator path) with mocks
- B6 Typing/docstrings on public APIs across graph/state/nodes
- B7 Packaging scaffolding (pyproject.toml) and a minimal Makefile
- B8 Move DI-friendly pattern towards, replacing global singletons gradually
- B9 Phase 2 design doc outlining directory structure and migration plan

- Medium Impact
- B10 Expand tests to cover edge cases in scoring and level-up logic
- B11 Introduce a Config class with environment-variable fallbacks and defaults
- B12 Create a lightweight UI adapter layer to separate Streamlit from core
- B13 Add a small logger configuration module and a single entry point to initialize logging
- B14 Define common interfaces for adapters (Chroma, Embeddings, Groq)
- B15 Add dedicated docs for Phase 2 migration plan

- Low Impact / Longer-term
- B16 Establish a formal packaging layout (src/ layout) and CI hints
- B17 Add typing stubs for external libraries where necessary
- B18 Create a sample venv and a local test script for contributors

- Notes
- Priorities assume Phase 1 findings confirm the described opportunities. The plan is to implement changes in Phase 2 via incremental PRs to minimize risk.
