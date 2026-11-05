# Use the local venv's tools when it exists, otherwise whatever is on PATH (e.g. in CI).
BIN := $(if $(wildcard .venv/bin/ruff),.venv/bin/,)
LINT_PATHS := src tests

.PHONY: help install lint lint-fix test check

help:
	@echo "make install   Install dev deps and the git pre-commit hook"
	@echo "make lint      Check lint and formatting (no changes)"
	@echo "make lint-fix  Auto-fix lint issues and reformat"
	@echo "make test      Run pytest"
	@echo "make check     lint + test"

install:
	$(BIN)pip install -r requirements-dev.txt
	$(BIN)pre-commit install

lint:
	$(BIN)ruff check $(LINT_PATHS)
	$(BIN)ruff format --check $(LINT_PATHS)

lint-fix:
	$(BIN)ruff check --fix $(LINT_PATHS)
	$(BIN)ruff format $(LINT_PATHS)

test:
	$(BIN)pytest -q

check: lint test
