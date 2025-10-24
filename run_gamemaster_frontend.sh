#!/bin/bash
# Start the Game Master frontend

echo "Starting SimulAI Game Master Frontend..."
streamlit run frontend/gamemaster/app.py --server.port 8502
