#!/bin/bash
export PYTHONPATH=/opt/render/project/src/apps/api-gateway

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --host 0.0.0.0 --port $PORT