FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# (render.yaml or other) is responsible for mapping external ports.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
