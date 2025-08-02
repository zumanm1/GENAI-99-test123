import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.device import Device
from app.auth import get_password_hash


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_db():
    """Create a test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create a database session for testing"""
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def client(test_db):
    """Create a test client"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    # Check if user already exists
    existing_user = db_session.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        return existing_user
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_device(db_session, test_user):
    """Create a test device"""
    device = Device(
        name="Test Router",
        ip_address="192.168.1.1",
        model="Cisco ISR 4000",
        status="online",
        owner_id=test_user.id
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for API calls"""
    response = client.post(
        "/auth/token",
        data={"username": test_user.email, "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
