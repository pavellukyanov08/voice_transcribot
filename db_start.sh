#!/bin/sh
set -e

echo "1. Waiting for the database to be ready..."

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

echo "2. Running database migrations..."

alembic upgrade head

echo "3. Starting the application..."
exec "$@"
