# Home Budget Web

A budget-tracking web application with a FastAPI backend and React frontend.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start (Full Stack)](#quick-start-full-stack)
3. [Running PostgreSQL Locally](#running-postgresql-locally)
4. [Running Backend (Development)](#running-backend-development)
5. [Running Frontend (Development)](#running-frontend-development)
6. [Running Tests](#running-tests)
7. [Migrations](#migrations)
8. [Seeding Data](#seeding-data)
9. [Project Structure](#project-structure)

---

## Prerequisites

- **Docker** and **Docker Compose** (for running PostgreSQL and the full stack)
- **Python 3.11+** (for backend development)
- **Poetry** (Python dependency manager)
- **Node.js 18+** (for frontend development)
- **npm** (comes with Node.js)

---

## Quick Start (Full Stack)

Run the entire application (backend + frontend + PostgreSQL) using Docker Compose:

```bash
# Start the full stack
docker compose up

# Or run in detached mode
docker compose up -d
```

Services:
- **Frontend**: http://localhost:5080
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432 (user: `budget`, password: `budget`, database: `budget_db`)

To stop and clean up:

```bash
# Stop all services
docker compose down

# Stop and remove volumes (resets database)
docker compose down -v
```

---

## Running PostgreSQL Locally

To run only PostgreSQL (for local backend development):

```bash
# Start PostgreSQL container
docker compose -f docker-compose-postgres.yaml up -d

# Verify it's running
docker ps | grep home_budget_db
```

Connection details:
- **Host**: localhost
- **Port**: 5432
- **User**: budget
- **Password**: budget
- **Database**: budget_db

Connection string:
```
postgresql://budget:budget@localhost:5432/budget_db
```

To stop PostgreSQL:

```bash
docker compose -f docker-compose-postgres.yaml down

# To also remove data volume
docker compose -f docker-compose-postgres.yaml down -v
```

---

## Running Backend (Development)

1. **Start PostgreSQL** (see [Running PostgreSQL Locally](#running-postgresql-locally))

2. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   The default settings connect to the local PostgreSQL container.

4. **Install dependencies**:
   ```bash
   poetry install
   ```

5. **Run migrations** (see [Migrations](#migrations))

6. **Start the development server**:
   ```bash
   poetry run uvicorn app.main:app --reload --port 8000
   ```
   
   Or using the convenience script:
   ```bash
   ./run_local.sh
   ```

The backend API will be available at http://localhost:8000

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Running Frontend (Development)

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5173

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest -v

# Run with PYTHONPATH set (if needed)
PYTHONPATH=$PYTHONPATH:$(pwd) poetry run pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with watch mode
npm test -- --watch
```

### E2E Smoke Tests

To run smoke tests that require the backend:

1. Start PostgreSQL and the backend (see sections above)
2. Run frontend tests with backend URL:
   ```bash
   cd frontend
   BACKEND_URL=http://localhost:8000 npm test
   ```

---

## Migrations

The project uses Alembic for database migrations. Migration files are located in `backend/migrations/`.

> **Note**: The migration system is being set up. Currently the application runs in JSON storage mode (see `backend/README.md` for details).

### Running Migrations (Future)

Once migrations are available:

```bash
cd backend

# Run all pending migrations
poetry run alembic upgrade head

# Create a new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Downgrade one migration
poetry run alembic downgrade -1
```

---

## Seeding Data

> **Note**: The seed script is being developed. Once available, you can seed the database with sample data for development and testing.

### Seeding (Future)

```bash
cd backend

# Run seed script to populate sample data
poetry run python -m scripts.seed
```

---

## Project Structure

```
home_budget_web/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Core settings and utilities
│   │   ├── data/           # JSON storage (temporary)
│   │   ├── routers/        # API route handlers
│   │   └── main.py         # Application entry point
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # Backend tests
│   ├── .env.example        # Environment template
│   ├── pyproject.toml      # Python dependencies
│   └── README.md           # Backend-specific docs
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── tests/          # Frontend tests
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node dependencies
│   └── README.md           # Frontend-specific docs
├── docs/                   # Project documentation
│   └── milestones/         # Milestone status reports
├── docker-compose.yaml     # Full stack (backend + frontend + db)
├── docker-compose-postgres.yaml  # PostgreSQL only
└── README.md               # This file
```

---

## Development Workflow

### New Developer Onboarding

1. Clone the repository
2. Start PostgreSQL:
   ```bash
   docker compose -f docker-compose-postgres.yaml up -d
   ```
3. Set up backend:
   ```bash
   cd backend
   cp .env.example .env
   poetry install
   poetry run pytest -v  # Verify tests pass
   ```
4. Set up frontend:
   ```bash
   cd frontend
   npm install
   npm test  # Verify tests pass
   ```
5. Start development servers (in separate terminals):
   ```bash
   # Terminal 1: Backend
   cd backend && poetry run uvicorn app.main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

### Running Smoke Tests

To verify your setup is working correctly:

```bash
# 1. Start PostgreSQL
docker compose -f docker-compose-postgres.yaml up -d

# 2. Run backend tests
cd backend
poetry run pytest -v

# 3. Run frontend tests
cd frontend
npm test
```

All tests should pass if your environment is set up correctly.

---

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (dev/staging/prod) | dev |
| `DATABASE_URL` | PostgreSQL connection string | postgresql://budget:budget@localhost:5432/budget_db |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

See `backend/.env.example` for the full template.

---

## Additional Resources

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Milestone Status](docs/milestones/)
- [Migration PR Template](backend/migrations/migration_pr_template.md)
