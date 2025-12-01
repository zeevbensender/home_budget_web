# =========================================
# Home Budget Web — Backend Makefile
# Milestone 1: FastAPI + PostgreSQL backend
# =========================================

# Variables
COMPOSE = docker compose
SERVICE = backend

# ------------------------------
# 🧱 Build the backend container
# ------------------------------
build:
	$(COMPOSE) build

# ------------------------------
# 🚀 Start the stack (backend + db)
# ------------------------------
up:
	$(COMPOSE) up

# ------------------------------
# 🚀 Start in detached mode
# ------------------------------
up-detached:
	$(COMPOSE) up -d

# ------------------------------
# 🧩 Stop and remove containers
# ------------------------------
down:
	$(COMPOSE) down

# ------------------------------
# 🧹 Stop and remove containers + volumes
# ------------------------------
clean:
	$(COMPOSE) down -v

# ------------------------------
# 🧪 Run tests inside the backend container
# ------------------------------
test:
	$(COMPOSE) run --rm $(SERVICE) poetry run pytest -v

# ------------------------------
# 🔁 Rebuild from scratch (no cache)
# ------------------------------
rebuild:
	$(COMPOSE) build --no-cache

# ------------------------------
# 📦 Database Migrations (Alembic)
# ------------------------------

# Run migrations to latest version
migrate:
	$(COMPOSE) run --rm $(SERVICE) poetry run alembic upgrade head

# Create a new migration (auto-generate from models)
# Usage: make migration MSG="add_user_table"
migration:
	$(COMPOSE) run --rm $(SERVICE) poetry run alembic revision --autogenerate -m "$(MSG)"

# Show current migration status
migrate-status:
	$(COMPOSE) run --rm $(SERVICE) poetry run alembic current

# Show migration history
migrate-history:
	$(COMPOSE) run --rm $(SERVICE) poetry run alembic history

# Downgrade one migration
migrate-down:
	$(COMPOSE) run --rm $(SERVICE) poetry run alembic downgrade -1

# ------------------------------
# 🌱 Seed smoke test data
# ------------------------------
seed-smoke:
	$(COMPOSE) run --rm $(SERVICE) poetry run python scripts/seed_smoke.py