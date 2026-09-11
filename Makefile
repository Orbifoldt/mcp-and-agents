SHELL := /bin/sh

UV ?= uv

.PHONY: help app mcp lint format-check test check all

help:
	@echo "Available targets:"
	@echo "  make app          Run the FastAPI application with reload enabled"
	@echo "  make mcp          Run the MCP server over HTTP on port 8001"
	@echo "  make lint         Run Ruff linting"
	@echo "  make format-check Check formatting with Ruff"
	@echo "  make test         Run tests when tests/ exists"
	@echo "  make check        Run all linting, formatting, and tests"

app:
	$(UV) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

mcp:
	$(UV) run python -m mcp_server.main

lint:
	$(UV) run ruff check .

format-check:
	$(UV) run ruff format --check .

test:
	@if [ -d tests ]; then \
		$(UV) run pytest; \
	else \
		echo "No tests/ directory yet; skipping tests."; \
	fi

check: lint format-check test

all: check
