.PHONY: install backend frontend dev test-backend test-integration test-frontend help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && uv sync
	cd frontend && npm install

backend: ## Start backend dev server on :8000
	cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend dev server
	cd frontend && npm run dev

dev: ## Start frontend and backend together (Ctrl-C stops both)
	@trap 'kill 0' EXIT; \
	  (cd backend && uv run uvicorn app.main:app --reload --port 8000) & \
	  (cd frontend && npm run dev) & \
	  wait

test-backend: ## Run backend unit tests
	cd backend && uv run pytest tests/ -v

test-integration: ## Run backend integration tests against a temporary SQLite database
	cd backend && uv run pytest tests_integration/ -v

test-frontend: ## Run frontend tests
	cd frontend && npm test
