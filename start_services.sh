#!/bin/bash

# NETWORK PORTS
BACKEND_PORT=5000
FRONTEND_PORT=8001
ADDITIONAL_PORTS=(8000 8002 3000 3001)

# FUNCTION TO CLEAR PORTS AND PROCESSES
clear_ports() {
    echo "Stopping existing Python and Node processes..."
    
    # Kill existing Python processes related to the app
    pkill -f "python.*app.py" || true
    pkill -f "python.*server.py" || true
    pkill -f "python.*main.py" || true
    
    # Clear main ports
    echo "Clearing network ports $BACKEND_PORT and $FRONTEND_PORT..."
    lsof -ti:${BACKEND_PORT} | xargs kill -9 2>/dev/null || true
    lsof -ti:${FRONTEND_PORT} | xargs kill -9 2>/dev/null || true
    
    # Clear additional ports that might be in use
    for port in "${ADDITIONAL_PORTS[@]}"; do
        echo "Clearing port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    done
    
    # Wait for ports to be freed
    sleep 2
    
    echo "Ports and processes cleared."
}

# FUNCTION TO START BACKEND
start_backend() {
    echo "Starting the FastAPI backend..."
    cd /home/test/Documents/GENAI-99-test123
    source venv/bin/activate
    nohup python backend/app.py > backend.log 2>&1 &
    sleep 5
    
    # Check if backend started successfully
    if lsof -ti:${BACKEND_PORT} > /dev/null; then
        echo "Backend started successfully on port $BACKEND_PORT."
    else
        echo "Warning: Backend may not have started properly. Check backend.log for details."
    fi
}

# FUNCTION TO START FRONTEND
start_frontend() {
    echo "Starting the frontend server..."
    cd /home/test/Documents/GENAI-99-test123
    source venv/bin/activate
    nohup python frontend/server.py > frontend.log 2>&1 &
    sleep 3
    
    # Check if frontend started successfully
    if lsof -ti:${FRONTEND_PORT} > /dev/null; then
        echo "Frontend started successfully on port $FRONTEND_PORT."
    else
        echo "Warning: Frontend may not have started properly. Check frontend.log for details."
    fi
}

# MAIN FUNCTION
main() {
    echo "Initializing setup..."

    # Clear necessary ports
    clear_ports

    # Start backend service
    start_backend

    # Start frontend service
    start_frontend

    echo "Setup complete! Frontend and Backend services are up and running."
}

main

