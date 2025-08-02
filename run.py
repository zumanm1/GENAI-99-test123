#!/usr/bin/env python3
"""
Run script for the Network Automation Application

DEVELOPMENT NOTE: 
During development, DO NOT use Docker or Docker Compose!
This script runs services directly using Python.
Docker will be used only after successful development completion.
"""

import os
import sys
import subprocess
import signal
import time

def run_database_init():
    """
    Initialize the database
    """
    print("Initializing database...")
    try:
        result = subprocess.run([sys.executable, "init_db.py"], check=True)
        print("Database initialized successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing database: {e}")
        return False

def start_application():
    """
    Start the FastAPI application
    """
    print("Starting the application...")
    try:
        # Change to the backend directory
        os.chdir("backend/api")
        
        # Start the FastAPI application
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    finally:
        # Change back to the original directory
        os.chdir("../..")

def main():
    """
    Main function to run the application
    """
    print("Network Automation Application")
    print("=" * 30)
    
    # Initialize database
    if not run_database_init():
        print("Failed to initialize database. Exiting...")
        sys.exit(1)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()