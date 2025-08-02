#!/bin/bash

# NETWORK PORTS
BACKEND_PORT=5000
FRONTEND_PORT=8001

# FUNCTION TO CLEAN PORTS AND PROCESSES
clean_services() {
    echo "Stopping services and clearing ports..."
    
    # Kill processes using specific ports
    lsof -ti:${BACKEND_PORT} | xargs kill -9 || true
    lsof -ti:${FRONTEND_PORT} | xargs kill -9 || true
    
    # Kill specific Python processes
    pkill -f "python backend/app.py" || true
    pkill -f "python frontend/server.py" || true
    
    echo "Services stopped and ports cleared."
}

# MAIN FUNCTION
main() {
    echo "Stopping Network Automation Application services..."
    clean_services
    echo "All services stopped successfully!"
}

main
