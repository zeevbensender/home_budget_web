# Grafana Cloud + Prometheus Metrics Integration

This document describes how to export application metrics from the Home Budget Web backend and visualize them in Grafana Cloud.

## Overview

The integration enables:
- **Prometheus metrics export** from the FastAPI/Uvicorn backend
- **Grafana Cloud dashboards** for monitoring request rates, error rates, and database latency
- **Alerting capabilities** based on metric thresholds

## Prerequisites

- Grafana Cloud account (free tier available at https://grafana.com/products/cloud/)
- Access to the Home Budget Web backend deployment
- Python 3.11+ with Poetry

## Setting Up Prometheus Metrics Export

### Step 1: Install Dependencies

Add the Prometheus client library to your backend dependencies:

```bash
cd backend
poetry add prometheus-client
```

Or add to `pyproject.toml`:

```toml
[tool.poetry.dependencies]
prometheus-client = "^0.21"
```

### Step 2: Add Metrics Middleware

Create a new file `backend/app/core/metrics.py`:

```python
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Database metrics
DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

DB_ERROR_COUNT = Counter(
    "db_errors_total",
    "Total database errors",
    ["operation", "error_type"]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    async def dispatch(self, request: Request, call_next):
        method = request.method
        # Normalize endpoint to avoid high cardinality
        endpoint = self._normalize_endpoint(request.url.path)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        status_code = str(response.status_code)

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response

    def _normalize_endpoint(self, path: str) -> str:
        """Normalize path to reduce cardinality.
        
        Replaces numeric IDs with placeholders.
        """
        parts = path.split("/")
        normalized = []
        for part in parts:
            if part.isdigit():
                normalized.append("{id}")
            else:
                normalized.append(part)
        return "/".join(normalized)


def metrics_endpoint():
    """Endpoint handler for /metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### Step 3: Register Middleware and Endpoint

Update `backend/app/main.py` to include the metrics middleware and endpoint:

```python
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import expense_router, income_router, health_router, config_router
from app.core.metrics import PrometheusMiddleware, metrics_endpoint

app = FastAPI(title="Home Budget Web Backend")

# Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# CORS for frontend (React from any host during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # restrict later for Prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router.router, prefix="/api/v1")
app.include_router(expense_router.router, prefix="/api/v1")
app.include_router(income_router.router, prefix="/api/v1")
app.include_router(config_router.router, prefix="/api/v1")

# Metrics endpoint
app.add_route("/metrics", metrics_endpoint)

@app.get("/")
def root():
    return {"message": "Home Budget Web Backend running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

### Step 4: Instrument Database Operations

To track database latency, use the `DB_QUERY_LATENCY` histogram in your repository/service layer:

```python
import time
from app.core.metrics import DB_QUERY_LATENCY, DB_ERROR_COUNT

def execute_query(operation: str, query_func):
    """Wrapper to instrument database queries."""
    start_time = time.time()
    try:
        result = query_func()
        return result
    except Exception as e:
        DB_ERROR_COUNT.labels(
            operation=operation,
            error_type=type(e).__name__
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        DB_QUERY_LATENCY.labels(operation=operation).observe(duration)
```

## Connecting to Grafana Cloud

### Step 1: Create a Grafana Cloud Account

1. Sign up at https://grafana.com/products/cloud/
2. Create a new stack (or use existing)
3. Note your Grafana Cloud URL (e.g., `https://your-stack.grafana.net`)

### Step 2: Configure Prometheus Remote Write

Grafana Cloud provides a Prometheus-compatible remote write endpoint. You can either:

**Option A: Use Grafana Agent** (Recommended for production)

1. Install Grafana Agent on your server
2. Configure it to scrape your `/metrics` endpoint and remote write to Grafana Cloud:

```yaml
# grafana-agent.yaml
metrics:
  configs:
    - name: home_budget
      scrape_configs:
        - job_name: 'home-budget-backend'
          scrape_interval: 15s
          static_configs:
            - targets: ['localhost:8000']
      remote_write:
        - url: https://prometheus-prod-XX-prod-XX.grafana.net/api/prom/push
          basic_auth:
            username: YOUR_GRAFANA_CLOUD_USER_ID
            password: YOUR_GRAFANA_CLOUD_API_KEY
```

**Option B: Use a Prometheus Server**

Configure your existing Prometheus server to scrape the backend and remote write to Grafana Cloud.

### Step 3: Verify Connection

1. Log into your Grafana Cloud instance
2. Navigate to **Explore**
3. Select your Prometheus data source
4. Query for `http_requests_total` to verify metrics are being received

## Example Grafana Dashboard

Import the example dashboard JSON located at `docs/grafana-dashboards/home-budget-overview.json`.

### Dashboard Panels

The example dashboard includes:

1. **Request Rate** - Requests per second by endpoint
2. **Error Rate** - HTTP 4xx/5xx errors per second
3. **Request Latency (p50, p95, p99)** - Response time percentiles
4. **Database Query Latency** - Database operation timing
5. **Active Endpoints** - Most frequently accessed endpoints

### Importing the Dashboard

1. In Grafana Cloud, go to **Dashboards** → **Import**
2. Upload the JSON file or paste its contents
3. Select your Prometheus data source
4. Click **Import**

## Alerting

### Recommended Alerts

1. **High Error Rate**
   - Condition: `rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1`
   - Severity: Critical

2. **High Latency**
   - Condition: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2`
   - Severity: Warning

3. **Database Errors**
   - Condition: `increase(db_errors_total[5m]) > 0`
   - Severity: Warning

## Dashboard Links

After setting up your dashboards, update your project documentation and PR templates with the actual dashboard URLs:

| Dashboard | URL |
|-----------|-----|
| Overview | `<YOUR_GRAFANA_CLOUD_URL>/d/home-budget-overview` |
| API Performance | `<YOUR_GRAFANA_CLOUD_URL>/d/home-budget-api` |
| Database Metrics | `<YOUR_GRAFANA_CLOUD_URL>/d/home-budget-db` |

## Troubleshooting

### No metrics appearing

1. Verify the `/metrics` endpoint returns data:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Check Grafana Agent logs for scrape errors

3. Verify network connectivity to Grafana Cloud

### High cardinality warnings

If you see cardinality warnings, ensure endpoint paths are being normalized correctly in the middleware. Avoid including dynamic values (IDs, timestamps) in metric labels.

### Missing database metrics

Ensure your repository/service layer is using the instrumented query wrapper functions.

## References

- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Grafana Cloud Documentation](https://grafana.com/docs/grafana-cloud/)
- [Grafana Agent Configuration](https://grafana.com/docs/agent/latest/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
