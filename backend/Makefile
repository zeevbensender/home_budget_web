# =========================================
# Home Budget Web — Backend Makefile
# Milestone 1: FastAPI + PostgreSQL backend
# =========================================

# Variables
COMPOSE = docker compose
SERVICE = backend
DATABASE_URL ?= postgresql://budget:budget@localhost:5432/budget_db

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
# 🗄️ Run database migrations
# ------------------------------
migrate:
	DATABASE_URL=$(DATABASE_URL) python -m alembic upgrade head

# ------------------------------
# 🌱 Seed the database with fixture data
# ------------------------------
seed:
	DATABASE_URL=$(DATABASE_URL) python -m scripts.seed

# ------------------------------
# 🚀 Full database setup (migrate + seed)
# ------------------------------
db-setup: migrate seed