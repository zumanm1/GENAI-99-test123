#!/bin/bash

# DEVELOPMENT NOTE: 
# During development, DO NOT use Docker or Docker Compose!
# This setup script prepares the Python environment and database.
# Docker will be used only after successful development completion.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Clear Network Ports ---
echo "Clearing network ports 8001 and 8002..."
lsof -ti:8001 | xargs kill -9 || true
lsof -ti:8002 | xargs kill -9 || true
echo "Ports cleared."


# --- Create Virtual Environment ---
echo "Checking for virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# --- Activate Virtual Environment and Install Dependencies ---
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-core.txt
pip install -r requirements-ai.txt

# --- Initialize Database ---
echo "Initializing the database..."
python init_db.py

echo "
Setup complete! The virtual environment is ready and the database is initialized."
echo "To activate the virtual environment, run: source venv/bin/activate"
