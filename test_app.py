#!/usr/bin/env python3
"""
Test script to verify that the application is working correctly
"""

import requests
import time
import sys
import pytest

def test_api_endpoints():
    """
    Test API endpoints
    """
    base_url = "http://localhost:5000"
    
    print("Testing API endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Root endpoint is working")
        else:
            print(f"✗ Root endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test health check endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health check endpoint is working")
        else:
            print(f"✗ Health check endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Health check endpoint failed: {e}")
    
    # Test API status endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/status")
        if response.status_code == 200:
            print("✓ API status endpoint is working")
        else:
            print(f"✗ API status endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ API status endpoint failed: {e}")
    
    # Test devices endpoint (should return empty list or sample devices)
    try:
        response = requests.get(f"{base_url}/api/v1/devices/")
        if response.status_code == 200:
            print("✓ Devices endpoint is working")
        else:
            print(f"✗ Devices endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Devices endpoint failed: {e}")
    
    # Test dashboard overview endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard/overview")
        if response.status_code == 200:
            print("✓ Dashboard overview endpoint is working")
        else:
            print(f"✗ Dashboard overview endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Dashboard overview endpoint failed: {e}")

def test_auth_endpoints():
    """
    Test authentication endpoints
    """
    base_url = "http://localhost:5000"
    
    print("\nTesting authentication endpoints...")
    
    # Test login endpoint
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            print("✓ Login endpoint is working")
            return response.json().get("access_token")
        else:
            print(f"✗ Login endpoint failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Login endpoint failed: {e}")
        return None

@pytest.fixture
def token():
    base_url = "http://localhost:5000"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        pytest.skip("Skipping because token could not be retrieved")


def test_protected_endpoints(token):
    """
    Test protected endpoints with authentication token
    """
    base_url = "http://localhost:5000"
    headers = {"Authorization": f"Bearer {token}"}

    print("\nTesting protected endpoints...")

    # Test dashboard metrics endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard/metrics", headers=headers)
        if response.status_code == 200:
            print("✓ Dashboard metrics endpoint is working")
        else:
            print(f"✗ Dashboard metrics endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Dashboard metrics endpoint failed: {e}")

def main():
    """
    Main function to run all tests
    """
    print("Starting application tests...\n")
    
    # Wait a moment for the application to start
    print("Waiting for application to start...")
    time.sleep(5)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test authentication endpoints
    token = test_auth_endpoints()
    
    # Test protected endpoints
    test_protected_endpoints(token)
    
    print("\nApplication tests completed!")

if __name__ == "__main__":
    main()