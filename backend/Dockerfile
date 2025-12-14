FROM python:3.11-slim

WORKDIR /app

# Install netcat for database readiness check
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/alembic.ini .
COPY backend/entrypoint.sh .

RUN chmod +x entrypoint.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
# (render.yaml or other) is responsible for mapping external ports.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
