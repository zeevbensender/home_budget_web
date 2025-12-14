#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

# Extract database host and port from DATABASE_URL
# Format: postgresql://user:password@host:port/dbname
# Default to 'db' and '5432' for Docker Compose compatibility
DB_HOST="db"
DB_PORT="5432"

if [ -n "$DATABASE_URL" ]; then
  # Extract host and port from DATABASE_URL using parameter expansion and sed
  # Remove protocol prefix
  DB_URL_NO_PROTOCOL="${DATABASE_URL#*://}"
  # Extract the host:port part (between @ and /)
  # Format: user:password@host:port/database
  if [[ "$DB_URL_NO_PROTOCOL" == *@* ]]; then
    DB_HOST_PORT=$(echo "$DB_URL_NO_PROTOCOL" | sed 's/.*@\([^/]*\).*/\1/')
    
    if [[ "$DB_HOST_PORT" == *:* ]]; then
      DB_HOST="${DB_HOST_PORT%:*}"
      DB_PORT="${DB_HOST_PORT#*:}"
    else
      # No port specified, use host and default port
      DB_HOST="$DB_HOST_PORT"
      DB_PORT="5432"
    fi
  fi
fi

echo "Checking database connection at $DB_HOST:$DB_PORT..."

# Wait for PostgreSQL to be available
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
cd /app
alembic -c /app/alembic.ini upgrade head

echo "Starting application..."
exec "$@"
