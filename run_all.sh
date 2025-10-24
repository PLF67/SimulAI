#!/bin/bash
# Start all components of SimulAI

echo "Starting SimulAI Business Game - All Components"
echo "================================================"

# Create data directory if it doesn't exist
mkdir -p data

# Start backend in background
echo "Starting Backend API..."
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 5

# Start Player Frontend in background
echo "Starting Player Frontend..."
streamlit run frontend/player/app.py --server.port 8501 &
PLAYER_PID=$!
echo "Player Frontend started (PID: $PLAYER_PID)"

# Start Game Master Frontend in background
echo "Starting Game Master Frontend..."
streamlit run frontend/gamemaster/app.py --server.port 8502 &
GM_PID=$!
echo "Game Master Frontend started (PID: $GM_PID)"

# Start Dashboard in background
echo "Starting Dashboard..."
streamlit run frontend/dashboard/app.py --server.port 8503 &
DASH_PID=$!
echo "Dashboard started (PID: $DASH_PID)"

echo ""
echo "================================================"
echo "SimulAI is now running!"
echo "================================================"
echo "Backend API:       http://localhost:8000"
echo "API Docs:          http://localhost:8000/docs"
echo "Player Frontend:   http://localhost:8501"
echo "Game Master:       http://localhost:8502"
echo "Dashboard:         http://localhost:8503"
echo "================================================"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo 'Stopping all services...'; kill $BACKEND_PID $PLAYER_PID $GM_PID $DASH_PID; exit" INT
wait
