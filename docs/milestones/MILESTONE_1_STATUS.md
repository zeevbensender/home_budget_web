# Milestone 1 – Project Status Report

## Overview
This document summarizes the completed features, architecture, and fixes delivered as part of **Milestone 1** of the *Home Budget Web* project.  
It is intended to be committed to the repository and tagged together with the first milestone release.

---

## Project Scope
Milestone 1 focused on establishing a functional end‑to‑end budget‑tracking application with:
- A lightweight FastAPI backend storing data in JSON files.
- A responsive React frontend supporting both desktop and mobile flows.
- Core CRUD functionality for **expenses** and **income**.
- A stable UI/UX foundation for future milestones.

---

## Backend – Completed Features

### FastAPI Application
- App entrypoint (`app/main.py`) initialized with CORS configured for development.
- Modular router structure under `/api`.

### Routers Implemented
- **Health Router**: `/api/v1/health`, including automated test.
- **Expense Router**: CRUD operations backed by `expenses.json`.
- **Income Router**: CRUD operations backed by `incomes.json`.
- **Bulk Delete** functionality for both expenses and income.

### Storage Layer
- Temporary persistence implemented using JSON files (`app/data/expenses.json`, `app/data/incomes.json`).
- Lightweight storage wrapper for reading/writing records.

### Notes
- SQLAlchemy models exist as an empty scaffold; real DB migrations and models are deferred to Milestone 1.1.
- Authentication and user accounts intentionally postponed.

---

## Frontend – Completed Features

### Core Screens
- **Expenses view** and **Income view**, each with:
  - Tabular list of transactions.
  - Inline add-row form (desktop).
  - Editing inside the table (desktop).
  - Swipe/tap edit via modal (mobile).

### Mobile UX
- Floating “+” button opens `TransactionModal`.
- Modal supports **add** and **edit** modes.
- Toast notifications for success/error.
- Horizontal scroll handling for smaller screens.

### Desktop UX
- **Inline AddRow** component for adding new transaction rows.
- **Inline EditCell** component.
- Delete per row via a delete icon.
- Bulk delete flow:
  - “Select” mode with checkboxes.
  - “Delete Selected” and “Cancel” controls.

### Integration Logic
- All create/edit/delete operations update the local state and re-fetch fresh backend data.
- Components now follow a clean ownership model:  
  **The parent component performs API operations.**  
  (Fixed in Milestone 1 to eliminate double POST issues.)

### UI Adjustments (Milestone 1 Fixes)
- “Add Expense” and “Add Income” buttons moved **below** the tables (desktop).
- Buttons auto-hide when the add-row form is displayed.
- AddRow no longer triggers its own API call—now delegates creation upward.
- Duplicated create calls removed, resolving the 200+422 double-request bug.
- Inline form now closes reliably upon successful save.

---

## Architectural Decisions
- Maintain parity between desktop inline editing and mobile modal workflow.
- Keep state management local to components to simplify early milestones.
- Avoid introducing Redux, Zustand, or server-side state until needed.
- Postpone authentication, real DB, and Alembic migrations until Milestone 1.1.
- Follow “tiny testable steps” development protocol.

---

## Current Limitations / Deferred Items
- No PostgreSQL or SQLAlchemy models yet.
- No migrations or Alembic pipeline.
- No authentication or user settings.
- Categories, accounts, and currency lists remain free‑form text for now.
- No analytics, charts, or dashboard.

---

## Recommended Location for This File
Suggested path in the repository:

```
docs/milestones/MILESTONE_1_STATUS.md
```

Reasoning:
- Keeps milestone documentation organized.
- Avoids cluttering root or backend/frontend folders.
- Prepares a clean structure for future milestone reports.

---

## Milestone 1 Summary
This milestone established a **stable functional base**:
- Full CRUD for expenses/income.
- Clean and consistent UX across devices.
- Solid backend/ frontend integration.
- Critical bug fixes and architectural cleanup.

The project is ready to move into **Milestone 1.1**, which will introduce a real database, ORM models, migrations, and user preferences.

---
