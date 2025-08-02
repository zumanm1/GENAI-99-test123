#!/usr/bin/env python3
"""
Script to start the Network Automation Application

DEVELOPMENT NOTE: 
During development, DO NOT use Docker or Docker Compose!
This script now uses Python/bash to start services directly.
Docker will be used only after successful development completion.
"""

import subprocess
import sys
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUDO_PASSWORD = os.getenv("SUDO_PASSWORD")

def run_sudo_command(command, check=True):
    """Run a command with sudo, providing the password via stdin"""
    if not SUDO_PASSWORD:
        # Fallback to regular command if no password is set
        return subprocess.run(command, capture_output=True, text=True, check=check)

    sudo_command = ['sudo', '-S'] + command
    try:
        result = subprocess.run(
            sudo_command,
            input=SUDO_PASSWORD + '\n',
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        # Print stderr for better debugging if the command fails
        print(f"Error running command: {' '.join(command)}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        raise e

def check_docker_installed():
    """Check if Docker is installed"""
    try:
        result = run_sudo_command(['docker', '--version'])
        print(f"Docker version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docker is not installed or not in PATH")
        return False

def check_docker_compose_installed():
    """Check if Docker Compose is installed"""
    try:
        # This check is problematic with sudo -S as it might not be installed
        # We will rely on the docker compose check below
        return True
        print(f"Docker Compose version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try docker compose (newer version)
            result = run_sudo_command(['docker', 'compose', 'version'])
            print(f"Docker Compose version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Docker Compose is not installed or not in PATH")
            return False

def build_and_start_services():
    """Build and start all services using Python"""
    print("Building and starting services...")
    try:
        # Start services using python
        print("Starting services...")
        run_sudo_command(['python', 'main.py'])
        print("Services started successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting services: {e}")
        return False

def check_services_status():
    """Check the status of running services"""
    print("\nChecking service status...")
    try:
        # Check service status using python
        print("Checking service status...")
        result = run_sudo_command(['python', 'main.py', 'status'])
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking service status: {e}")
        return False

def show_access_info():
    """Show information on how to access the application"""
    print("\n" + "="*50)
    print("APPLICATION ACCESS INFORMATION")
    print("="*50)
    print("Frontend (Dashboard): http://localhost:5888")
    print("API Documentation: http://localhost:8000/docs")
    print("API ReDoc: http://localhost:8000/redoc")
    print("\nDefault Login Credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\nTo stop the application, run: pkill -f main.py")
    print("="*50)

def main():
    """Main function to start the application"""
    print("Network Automation Application - Startup Script")
    print("="*50)
    
    # No need to check for Docker or Docker Compose
    
    # Build and start services
    if not build_and_start_services():
        print("\nFailed to start services. Please check the error messages above.")
        sys.exit(1)
    
    # Wait a moment for services to start
    print("\nWaiting for services to start...")
    time.sleep(10)
    
    # Check service status
    check_services_status()
    
    # Show access information
    show_access_info()
    
    print("\nApplication startup completed!")

if __name__ == "__main__":
    main()
