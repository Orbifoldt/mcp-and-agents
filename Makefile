SHELL := /bin/sh

UV ?= uv

.PHONY: help app mcp phoenix-up phoenix-down phoenix-logs lint format-check type-check test check all

help:
	@echo "Available targets:"
	@echo "  make app          Run the FastAPI application with reload enabled"
	@echo "  make mcp          Run the MCP server over HTTP on port 8001"
	@echo "  make phoenix-up   Start Phoenix with Docker Compose"
	@echo "  make phoenix-down Stop Phoenix"
	@echo "  make phoenix-logs Follow Phoenix logs"
	@echo "  make lint         Run Ruff linting"
	@echo "  make format-check Check formatting with Ruff"
	@echo "  make type-check   Run Pyrefly type checking"
	@echo "  make test         Run tests when tests/ exists"
	@echo "  make check        Run all linting, formatting, type checking, and tests"

app:
	$(UV) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

mcp:
	$(UV) run python -m mcp_server.main

phoenix-up:
	docker compose up -d phoenix

phoenix-down:
	docker compose down

phoenix-logs:
	docker compose logs -f phoenix

lint:
	$(UV) run ruff check .

format-check:
	$(UV) run ruff format --check .

format:
	$(UV) run ruff format .

type-check:
	$(UV) run pyrefly check .

test:
	@if [ -d tests ]; then \
		$(UV) run pytest; \
	else \
		echo "No tests/ directory yet; skipping tests."; \
	fi

check: lint format type-check test

all: check
