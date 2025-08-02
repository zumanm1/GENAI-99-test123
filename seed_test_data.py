#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    # Check if test user already exists
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        print("Test user already exists")
        return
    
    # Create test user
    test_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"Created test user: {test_user.email}")
    db.close()

if __name__ == "__main__":
    create_test_user()
