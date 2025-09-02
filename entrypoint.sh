#!/bin/bash

export PYTHONPATH=/app/apps/api_fastapi

flask --app apps/ui_flask/app run --host=0.0.0.0 --port=3000 &

uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir /app/apps/api_fastapi &

wait