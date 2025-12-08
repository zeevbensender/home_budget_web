#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
# Wait for PostgreSQL to be available
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
cd /app
alembic -c /app/alembic.ini upgrade head

echo "Starting application..."
exec "$@"
