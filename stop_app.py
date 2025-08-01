#!/usr/bin/env python3
"""
Script to stop the Network Automation Application using Docker Compose
"""

import subprocess
import sys

def check_docker_compose_installed():
    """Check if Docker Compose is installed"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"Docker Compose version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try docker compose (newer version)
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, check=True)
            print(f"Docker Compose version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Docker Compose is not installed or not in PATH")
            return False

def stop_services():
    """Stop all services using Docker Compose"""
    print("Stopping services...")
    try:
        # Check if we're using docker-compose or docker compose
        compose_cmd = ['docker-compose']
        try:
            subprocess.run(['docker-compose', '--version'], 
                          capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            compose_cmd = ['docker', 'compose']
        
        # Stop services
        subprocess.run(compose_cmd + ['down'], check=True)
        print("Services stopped successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error stopping services: {e}")
        return False

def main():
    """Main function to stop the application"""
    print("Network Automation Application - Stop Script")
    print("="*50)
    
    # Check if Docker Compose is installed
    if not check_docker_compose_installed():
        print("\nPlease install Docker Compose before running this script.")
        print("Visit: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    # Stop services
    if not stop_services():
        print("\nFailed to stop services. Please check the error messages above.")
        sys.exit(1)
    
    print("\nApplication stopped successfully!")

if __name__ == "__main__":
    main()