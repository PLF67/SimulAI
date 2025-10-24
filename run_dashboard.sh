#!/bin/bash
# Start the Dashboard

echo "Starting SimulAI Dashboard..."
streamlit run frontend/dashboard/app.py --server.port 8503
