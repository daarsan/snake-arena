.PHONY: install backend frontend dev test test-frontend help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && uv sync
	cd frontend && bun install

backend: ## Start backend dev server on :8000
	cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend dev server
	cd frontend && bun run dev

dev: ## Start frontend and backend together (Ctrl-C stops both)
	@trap 'kill 0' EXIT; \
	  (cd backend && uv run uvicorn app.main:app --reload --port 8000) & \
	  (cd frontend && bun run dev) & \
	  wait

test: ## Run backend tests
	cd backend && uv run pytest tests/ -v

test-frontend: ## Run frontend tests
	cd frontend && bun run test
