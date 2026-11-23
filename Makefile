-include .env
export

MANAGE := uv run python sites_cms/manage.py
LOCAL_DB := postgresql://sites_cms:sites_cms@localhost:5434/sites_cms

.DEFAULT_GOAL := help
.PHONY: help setup db run seed test lint format check-migrations \
	check-deploy lock

help: ## Show the commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "} {printf "  %-18s %s\n", $$1, $$2}'

setup: ## First-time setup: dependencies, database, admin user, seed data
	uv sync
	$(MAKE) db
	$(MANAGE) migrate
	$(MANAGE) create_local_admin
	$(MANAGE) seed

db: ## Start the database and wait until it is ready
	@docker compose up -d --wait db

run: db ## Start the dev server on http://localhost:8000/admin/
	$(MANAGE) runserver 8000

seed: ## Load sample content
	$(MANAGE) seed

test: db ## Run the tests (reuses the test database between runs)
	uv run pytest -q --tb=short -x --reuse-db

lint: ## Check code style
	uv run ruff check .
	uv run ruff format --check .

format: ## Fix code style
	uv run ruff check --fix .
	uv run ruff format .

check-migrations: db ## Fail if a model change has no migration
	$(MANAGE) makemigrations --check --dry-run

check-deploy: db ## Run Django's deployment checks on production settings
	DJANGO_SETTINGS_MODULE=sites_cms.settings.production \
	DJANGO_SECRET_KEY=check-only-not-a-real-key-0123456789-abcdefghijklmnop \
	DJANGO_ALLOWED_HOSTS=cms.example.com \
	DJANGO_BASE_URL=https://cms.example.com \
	POSTGRESQL_DB_CONNECT_STRING=$(or $(DATABASE_URL),$(LOCAL_DB)) \
	$(MANAGE) check --deploy --fail-level WARNING

lock: ## Regenerate uv.lock and requirements.txt
	uv lock
	uv export --no-dev --no-emit-project --format requirements-txt \
		-o requirements.txt
