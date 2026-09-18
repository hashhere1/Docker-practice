#!/bin/sh
set -e

if [ "$#" -gt 0 ]; then
    echo "Executing custom command: $@"
    exec "$@"
fi

echo "Running alembic migration..."
alembic upgrade head

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload