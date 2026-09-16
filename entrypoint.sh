#!/bin/sh
set -e

echo "Running alembic migration"
alembic upgrade head

echo "Starting Fastapi server"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload