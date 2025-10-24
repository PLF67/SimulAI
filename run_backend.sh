#!/bin/bash
# Start the FastAPI backend server

echo "Starting SimulAI Backend API..."
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
