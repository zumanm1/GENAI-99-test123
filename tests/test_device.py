import pytest


def test_fetch_device_list(client, auth_headers):
    response = client.get("/api/devices", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_device(client, auth_headers):
    response = client.post(
        "/api/devices",
        headers=auth_headers,
        json={
            "name": "New Device",
            "ip_address": "192.168.1.2",
            "model": "Cisco 2901",
            "status": "online"
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "New Device"
    assert response.json()["ip_address"] == "192.168.1.2"


def test_delete_device(client, auth_headers, test_device):
    response = client.delete(f"/api/devices/{test_device.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Device deleted successfully"
