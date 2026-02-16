Phase 1 Findings Report (read-only audit)
Scope: Analyze Pythonic modularity and project structure without editing code.

Executive snapshot
- Core shape
  - Entry: top-level Streamlit app in main.py; tests in test_app.py and app/nodes/test_agent.py.
  - Core package: app/ houses graph.py, state.py, nodes/, and utils/.
  - Packaging: no pyproject.toml or setup.py found in scanned areas; requirements.txt appears inconsistently across scans.
  - UI vs logic: UI and orchestration are intertwined in several modules (notably main.py and node modules).
- Modularity today
  - Strengths: Graph orchestration (app.graph) and node implementations (researcher, interviewer, evaluator, debug) are reasonably separated.
  - Weaknesses: Each module tends to do more than one thing (UI, orchestration, and model calls mixed); global-like patterns (singleton embeddings); IO/side effects bleed into core logic; config/logging are not centralized.
- Typing, docs, observability
  - Typing exists (TypedDict in app/state.py) but public APIs lack consistency in typing and docstrings.
  - Logging: prints are used for tracing; no centralized logging configuration.
- Config & secrets
  - dotenv and st.secrets are used; config access is scattered and not centralized.
- Testing & quality gates
  - Tests exist but appear UI-coupled; core logic lacks unit-test coverage.
- Observed patterns to address
  - Global singleton in researcher.py (_embeddings) and ad-hoc model loading.
  - IO/mixed concerns in core logic (Chroma, embeddings, Groq).
  - Move toward DI (pass dependencies via constructor/factory) instead of hard-coded globals.

Quick wins (non-destructive)
- Introduce a lightweight logging layer; replace print statements with logger calls gradually.
- Add a centralized Config module to consolidate env/config access and defaults.
- Separate UI from core engine; establish a thin UI adapter layer to keep engine testable without Streamlit.
- Improve typing and add docstrings for public APIs and data structures.
- Introduce data adapters/interfaces for external services (Chroma, embeddings, Groq) to enable DI and easier mocking.

Refactor candidates (by impact and effort)
- High impact, lower effort
- HL-01 Add logging module and replace prints in researcher.py, evaluator.py, graph.py, debug.py
- HL-02 Create a Config module exposing a single source of truth for tokens and defaults
- HL-03 Introduce simple adapters for external services; break direct imports of singletons
- HL-04 Separate UI from core: create an engine/core package for non-UI logic
- HL-05 Add unit tests for core logic (route_logic in graph.py; evaluator path with a mocked model)
- Medium effort
- HL-06 Add comprehensive type hints and docstrings to public APIs (graph.py, state.py, nodes interfaces)
- HL-07 Create packaging skeleton (pyproject.toml) and a minimal Makefile for tasks
- HL-08 Move the embedding singleton toward DI-friendly design and provide a testable factory
- Long-term scaffolding
- HL-09 Define a Phase 2 design doc with concrete directory structure and migration plan

Phase 1 runbook (reproducible locally)
- Inspect project layout and Python version
- Commands to run locally (suggested):
  - python --version
  - ls -R
  - rg -n "def|class|import" app | head
- Check packaging artifacts
  - ls -la | find . -name pyproject.toml -or -name setup.py -or -name requirements.txt
- Run tests (if any) that don’t require Streamlit UI. If tests rely on UI, skip for Phase 1.
- Verify no edits were performed in Phase 1; confirm that a Phase 2 patch can be applied cleanly.

Appendix: key files observed (high level notes)
- main.py: UI wiring; invokes graph/stream logic; initial session state and UI layout in Streamlit.
- app/graph.py: orchestration and route logic; uses MemorySaver for persistence; prints for tracing.
- app/state.py: InterviewState TypedDict; uses operator.add for some fields (may be non-obvious).
- app/nodes/researcher.py: loads embeddings (singleton pattern) and uses Chroma for RAG context; prints for traces.
- app/nodes/evaluator.py: evaluates answers; JSON extraction; prints on errors.
- app/nodes/interviewer.py: builds system prompt and calls a model; returns messages.
- app/nodes/debug.py: debugging helper; returns empty dict to avoid operator.add loop.
- app/utils/prompts.py: string templates for prompts.
- ingest.py: ingestion pipeline with cloud embeddings and Chroma.
- test_app.py: Streamlit UI startup/interaction tests.
- tests in app/nodes/test_agent.py: node-level tests (where present).
