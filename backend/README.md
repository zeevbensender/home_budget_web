# 🏡 Home Budget Web — Backend

Backend service for **Home Budget Web**, a cloud-native personal finance manager.  
Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, designed for **Render** deployment and easy migration to **AWS**, **GCP**, or other platforms.

---

## 🚀 Overview

This service provides RESTful APIs to manage:
- Expenses and incomes  
- Categories, businesses, and accounts  
- Data export (CSV/Excel)  

The backend is part of a full-stack project including a React-based frontend (added in later milestones).

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| Framework | FastAPI |
| ORM & Migrations | SQLAlchemy + Alembic |
| Database | PostgreSQL |
| Configuration | Poetry + `.env` |
| Containerization | Docker |
| Deployment | Render |
| CI/CD | GitHub Actions |

---

## 🧱 Project Structure

```
backend/
│
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── core/                  # Config & database
│   │   ├── config.py
│   │   └── db.py
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic models
│   ├── routers/               # API endpoints
│   ├── services/              # Business logic
│   ├── utils/                 # Export helpers
│   └── __init__.py
│
├── alembic/                   # Database migrations
├── pyproject.toml             # Poetry dependencies
├── poetry.lock
├── requirements.txt           # Auto-exported for Render/CI
├── Dockerfile
├── .env.example
└── README.md
```

---

## ⚙️ Local Development

### 1. Prerequisites
- **Python 3.11+**
- **Poetry** installed (`pip install poetry`)
- **Docker** (optional but recommended)

### 2. Clone the repository
```bash
git clone https://github.com/zeevbensender/home_budget_web.git
cd home_budget_web/backend
```

### 3. Create `.env`
```bash
DATABASE_URL=postgresql://budget:budget@localhost:5432/budget_db
ENV=dev
```

### 4. Install dependencies
```bash
poetry install
```

---

### 🧩 Exporting Dependencies

Render and CI/CD use a `requirements.txt` file, which you can generate from your Poetry setup.

#### Option 1 — Recommended (Poetry Export Plugin)
If you have Poetry ≥1.2, install the export plugin once:

```bash
poetry self add poetry-plugin-export
```

Then export your dependencies:

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

✅ This creates a clean, locked `requirements.txt` file used by Docker, Render, and GitHub Actions.

You can verify the plugin is active with:
```bash
poetry self show plugins
```

Expected to include:
```
poetry-plugin-export
```

#### Option 2 — Alternative (Using pip freeze)
If you prefer not to install the plugin:
```bash
poetry run pip freeze > requirements.txt
```

This works for quick exports, though it may include additional transient dependencies.

---

### 5. Run locally
```bash
uvicorn app.main:app --reload
```
Then open [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🐳 Docker (Local Setup)

```bash
docker compose up
```

This will start:
- PostgreSQL (port 5432)
- FastAPI backend (port 8000)

---

## 🚀 Deployment (Render)

1. Connect your GitHub repo to [Render](https://render.com).  
2. Create a **Web Service** using `backend/Dockerfile`.  
3. Add environment variable:
   ```
   DATABASE_URL = <your Render PostgreSQL connection string>
   ```
4. Deploy automatically from the `main` branch.  

Render will detect `requirements.txt` and start the app.

---

## 🧪 Testing

Run tests using Poetry:
```bash
poetry run pytest -v
```

---

## 🧭 Roadmap (Backend)

| Milestone | Feature | Status |
|------------|----------|--------|
| **1.0** | Expenses & Incomes CRUD, CSV Export | 🚧 In progress |
| **1.1** | Authentication, categories linking | ⏳ Planned |
| **2.0** | AI receipt parsing, smart budget insights | 🔮 Future |

---

## 💡 Design Principles
- **Cloud-agnostic:** Deployable on Render, AWS, or GCP.  
- **Separation of concerns:** Models, routers, and services are modular.  
- **Stateless:** Easy to scale horizontally.  
- **Readable & testable:** For long-term maintainability.  

---

## 📜 License
Released under the [MIT License](../LICENSE).

---

## ✨ Author
**Zeev Ben Sender**  
📂 [GitHub Portfolio](https://github.com/zeevbensender)  
📧 <bensender@gmail.com>

---

> _“Start small, build clean, scale with purpose.”_
