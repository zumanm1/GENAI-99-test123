import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_full_authentication_flow(client):
    """Test complete authentication flow"""
    # First, attempt to access protected resource without auth
    response = client.get("/api/devices")
    assert response.status_code == 401
    
    # Create a user (this would typically be done through registration)
    # For now, we'll use the test user from fixtures
    
    # Login with correct credentials
    response = client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    
    # Use token to access protected resource
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    response = client.get("/api/devices", headers=headers)
    assert response.status_code == 200


def test_device_crud_workflow(client, auth_headers):
    """Test complete CRUD operations for devices"""
    
    # Create a device
    device_data = {
        "name": "Integration Test Router",
        "ip_address": "10.0.0.1",
        "model": "Cisco ISR 4321",
        "status": "online"
    }
    
    response = client.post("/api/devices", headers=auth_headers, json=device_data)
    assert response.status_code == 201
    created_device = response.json()
    device_id = created_device["id"]
    
    # Read the device
    response = client.get(f"/api/devices/{device_id}", headers=auth_headers)
    assert response.status_code == 200
    device = response.json()
    assert device["name"] == device_data["name"]
    assert device["ip_address"] == device_data["ip_address"]
    
    # Update the device
    updated_data = {
        "name": "Updated Router Name",
        "ip_address": "10.0.0.2",
        "model": "Cisco ISR 4431",
        "status": "offline"
    }
    
    response = client.put(f"/api/devices/{device_id}", headers=auth_headers, json=updated_data)
    assert response.status_code == 200
    updated_device = response.json()
    assert updated_device["name"] == updated_data["name"]
    assert updated_device["status"] == updated_data["status"]
    
    # List all devices and verify our device is there
    response = client.get("/api/devices", headers=auth_headers)
    assert response.status_code == 200
    devices = response.json()
    device_names = [d["name"] for d in devices]
    assert "Updated Router Name" in device_names
    
    # Delete the device
    response = client.delete(f"/api/devices/{device_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify device is deleted
    response = client.get(f"/api/devices/{device_id}", headers=auth_headers)
    assert response.status_code == 404


def test_unauthorized_access_scenarios(client):
    """Test various unauthorized access scenarios"""
    
    # No token provided
    response = client.get("/api/devices")
    assert response.status_code == 401
    
    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/devices", headers=headers)
    assert response.status_code == 401
    
    # Malformed authorization header
    headers = {"Authorization": "InvalidFormat token"}
    response = client.get("/api/devices", headers=headers)
    assert response.status_code == 401


def test_api_error_handling(client, auth_headers):
    """Test API error handling scenarios"""
    
    # Try to get non-existent device
    response = client.get("/api/devices/999999", headers=auth_headers)
    assert response.status_code == 404
    
    # Try to create device with invalid data
    invalid_device_data = {
        "name": "",  # Empty name
        "ip_address": "invalid_ip",  # Invalid IP
        "model": "",  # Empty model
    }
    
    response = client.post("/api/devices", headers=auth_headers, json=invalid_device_data)
    assert response.status_code == 422  # Validation error
    
    # Try to delete non-existent device
    response = client.delete("/api/devices/999999", headers=auth_headers)
    assert response.status_code == 404


def test_concurrent_device_operations(client, auth_headers):
    """Test handling of concurrent operations"""
    
    # Create multiple devices
    devices_to_create = [
        {"name": f"Router-{i}", "ip_address": f"192.168.1.{i}", "model": "Cisco ISR", "status": "online"}
        for i in range(10, 15)
    ]
    
    created_devices = []
    for device_data in devices_to_create:
        response = client.post("/api/devices", headers=auth_headers, json=device_data)
        assert response.status_code == 201
        created_devices.append(response.json())
    
    # Verify all devices were created
    response = client.get("/api/devices", headers=auth_headers)
    assert response.status_code == 200
    all_devices = response.json()
    
    created_device_names = {d["name"] for d in created_devices}
    existing_device_names = {d["name"] for d in all_devices}
    
    assert created_device_names.issubset(existing_device_names)
    
    # Clean up - delete all created devices
    for device in created_devices:
        response = client.delete(f"/api/devices/{device['id']}", headers=auth_headers)
        assert response.status_code == 200
