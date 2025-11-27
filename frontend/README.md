# Home Budget Web — Frontend

## Overview

React frontend for the Home Budget Web application, built with Vite.

---

## Prerequisites

- **Node.js 18+**
- **npm** (comes with Node.js)

---

## Setup

### 1. Install Dependencies

```bash
npm install
```

---

## Running the Frontend

### Development Server

```bash
npm run dev
```

The development server runs at http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

---

## Running Tests

The frontend uses **Vitest** for testing.

```bash
# Run tests once
npm test

# Run tests in watch mode
npm test -- --watch
```

### Test Types

- **Unit tests**  
  Pure JavaScript logic tests (no DOM), located in `src/tests/`

- **E2E smoke tests**  
  Currently **skipped by default**.  
  Enable manually by setting the backend URL:
  ```bash
  BACKEND_URL=http://localhost:8000 npm test
  ```

---

## Linting

```bash
npm run lint
```

---

## Using Docker

### Build Docker Image

From the project root:

```bash
docker build -t homebudget-frontend -f ./frontend/Dockerfile .
```

### Run with Docker Compose

```bash
docker compose up frontend
```

The frontend will be available at http://localhost:5080

---

## Project Structure

```
frontend/
├── public/             # Static assets
├── src/
│   ├── components/     # React components
│   ├── hooks/          # Custom React hooks
│   ├── tests/          # Test files
│   ├── types/          # TypeScript types
│   ├── utils/          # Utility functions
│   ├── api.js          # API client
│   ├── App.jsx         # Main application component
│   └── main.jsx        # Application entry point
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite configuration
└── eslint.config.js    # ESLint configuration
```

---

## Environment Variables

For production deployment, configure in `.env.production`:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL |

---

## Development Notes

- No component rendering tests during Variant A.
- Avoid introducing UI-level coupling in tests.
- Keep diffs minimal.

---

## Related Documentation

- [Root README](../README.md) - Full project documentation
- [Backend README](../backend/README.md) - Backend documentation
