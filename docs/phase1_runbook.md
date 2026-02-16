# Phase 1 Runbook (local reproducibility)

Prerequisites
- Python 3.9+ (target baseline as discussed); virtual environment recommended.
- Access to repo with the existing codebase; dependencies may be installed as needed.

Steps to reproduce the Phase 1 audit locally
- Inspect project layout
  - Windows: dir /S
  - macOS/Linux: ls -R
- Check for packaging artifacts
  - Look for pyproject.toml, setup.py, requirements.txt
- Quick static checks (no edits in Phase 1)
  - rg -n "def|class|import" app | head -n 50
- Run tests (if any exist that don’t require Streamlit or UI)
- Validate that no code edits were performed during Phase 1
- If you want to start Phase 2, prepare a patch plan and run a dry-run of the migration plan

Notes
- Phase 1 is intentionally read-only to ensure a clean baseline.
- The runbook can be extended with environment-specific steps (CI vs local dev).
