import sys
from pathlib import Path


def fix_main_import(repo_root: Path):
    main_py = repo_root / "main.py"
    if not main_py.exists():
        print(f"main.py not found at {main_py}")
        return 1

    text = main_py.read_text()
    old = "from rag_interviewer.graph import app  # Ensure your LangGraph is exported as 'app'"
    if old not in text:
        # If the exact line isn't present, try a relaxed approach by patching the first import occurrence
        pass
    new_block = (
        "try:\n"
        "    from rag_interviewer.graph import app  # Ensure your LangGraph is exported as 'app'\n"
        "except Exception:\n"
        "    # Fallback for environments where the new src layout isn't importable yet\n"
        "    from app.graph import app  # type: ignore\n"
    )
    text = text.replace(old, new_block)
    main_py.write_text(text)
    print("main.py import block updated with fallback.")
    return 0


def main():
    repo_root = Path(__file__).resolve().parents[1]
    sys.exit(fix_main_import(repo_root))


if __name__ == "__main__":
    main()
