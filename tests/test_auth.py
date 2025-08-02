import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_token_correct_credentials(client, test_user):
    response = client.post("/auth/token", data={"username": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_get_token_wrong_credentials(client):
    response = client.post("/auth/token", data={"username": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "access_token" not in response.json()
