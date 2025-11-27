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
# 🔥 Run smoke tests (DB integration)
# ------------------------------
smoke-test:
	poetry run pytest tests/test_smoke_db.py -v

# ------------------------------
# 🗄️  Run Alembic migrations
# ------------------------------
migrate:
	poetry run alembic upgrade head

# ------------------------------
# 🌱 Seed the database
# ------------------------------
seed:
	poetry run python scripts/seed_db.py