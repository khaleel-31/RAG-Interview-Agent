.PHONY: test lint typecheck

test:
	pytest -q

lint:
	ruff check .

typecheck:
	mypy .
