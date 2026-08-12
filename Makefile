.DEFAULT_GOAL := help
.PHONY: help install dev dev-backend dev-frontend build test lint format check docker-build docker-run deploy clean

NPM := npm --prefix frontend

help:  ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install:  ## Install backend and frontend dependencies
	uv sync
	$(NPM) ci

dev:  ## Run backend and frontend dev servers together
	@trap 'kill 0' EXIT; $(MAKE) dev-backend & $(MAKE) dev-frontend & wait

dev-backend:  ## Run the API on :8000 with reload
	ENVIRONMENT=development uv run uvicorn wmf_scraper.main:app --reload --port 8000

dev-frontend:  ## Run the Vite dev server on :3000, proxying /api to :8000
	$(NPM) run dev

build:  ## Build the production frontend into frontend/dist
	$(NPM) run build

test:  ## Run the backend test suite with coverage
	uv run pytest --cov --cov-report=term-missing

lint:  ## Lint and type-check both sides
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
	$(NPM) run typecheck

format:  ## Auto-format the Python code
	uv run ruff check --fix .
	uv run ruff format .

check: lint test  ## Everything CI runs

docker-build:  ## Build the production image
	docker build -t wmf-scraper:local .

docker-run: docker-build  ## Run the production image on :8000 against a local volume
	docker run --rm -p 8000:8000 \
		-v $(PWD)/data:/data \
		-e SESSION_SECRET=local-development-secret \
		-e SUPERADMIN_USERNAME=admin -e SUPERADMIN_PASSWORD=admin \
		wmf-scraper:local

deploy:  ## Deploy to the wmf-scraper Fly app
	fly deploy

clean:  ## Remove build artefacts and caches
	rm -rf frontend/dist .pytest_cache .ruff_cache .mypy_cache .coverage
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
