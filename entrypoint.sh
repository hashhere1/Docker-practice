#!/bin/sh
set -e

echo "Running alembic migration"
alembic upgrade head

if [ "$#" -gt 0 ]; then
    echo "Executing custom command: $@"
    exec "$@"
else
    echo "Starting Fastapi server"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi