#!/usr/bin/env python3
"""
FastAPI Backend Application Entry Point

This module runs the FastAPI application on port 5000.
"""

import os
import sys

# Add the parent directory to the path so we can import from main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

if __name__ == "__main__":
    import uvicorn
    
    # Run on port 5000 as requested
    port = 5000
    print(f"Starting FastAPI application on port {port}")
    print("Health endpoint available at: http://localhost:5000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
