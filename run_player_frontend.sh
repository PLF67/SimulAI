#!/bin/bash
# Start the Player frontend

echo "Starting SimulAI Player Frontend..."
streamlit run frontend/player/app.py --server.port 8501
