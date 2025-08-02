#!/usr/bin/env python3
"""
Database initialization script
This script creates all tables and adds initial data to the database
"""

import os
import sys
from sqlalchemy.orm import Session
from backend.database.connection import init_db, engine, SessionLocal
from backend.database.models import Base, User, NetworkDevice, LLMSetting

def create_tables():
    """
    Create all tables in the database
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def create_initial_user(db: Session):
    """
    Create an initial admin user
    """
    print("Creating initial admin user...")
    
    # Check if admin user already exists
    existing_user = db.query(User).filter(User.email == "admin@example.com").first()
    if existing_user:
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin_user = User(
        email="admin@example.com",
        display_name="Admin User",
        role="admin"
    )
    admin_user.set_password("admin123")
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print("Admin user created successfully!")
    print("Email: admin@example.com")
    print("Password: admin123")

def create_sample_devices(db: Session):
    """
    Create sample devices for testing
    """
    print("Creating sample devices...")
    
    # Check if sample devices already exist
    existing_device = db.query(NetworkDevice).filter(NetworkDevice.name == "Router R15").first()
    if existing_device:
        print("Sample devices already exist!")
        return
    
    # Create sample devices
    sample_devices = [
        NetworkDevice(
            name="Router R15",
            ip_address="192.168.1.15",
            model="Cisco ISR 4331",
            status="online"
        ),
        NetworkDevice(
            name="Router R16",
            ip_address="192.168.1.16",
            model="Cisco ASR 1001-X",
            status="online"
        ),
        NetworkDevice(
            name="Router R17",
            ip_address="192.168.1.17",
            model="Cisco ISR 4321",
            status="offline"
        ),
        NetworkDevice(
            name="Switch SW01",
            ip_address="192.168.1.101",
            model="Cisco Catalyst 9300",
            status="online"
        ),
        NetworkDevice(
            name="Firewall FW01",
            ip_address="192.168.1.254",
            model="Cisco ASA 5516-X",
            status="warning"
        )
    ]
    
    for device in sample_devices:
        db.add(device)
    
    db.commit()
    print("Sample devices created successfully!")

def create_default_llm_settings(db: Session):
    """
    Create default LLM settings
    """
    print("Creating default LLM settings...")
    
    # Check if LLM settings already exist
    existing_setting = db.query(LLMSetting).first()
    if existing_setting:
        print("LLM settings already exist!")
        return
    
    # Create default LLM setting
    default_setting = LLMSetting(
        provider="openai",
        api_key="",  # Empty by default, to be filled by user
        model="gpt-3.5-turbo",
        temperature=70,
        max_tokens=2000,
        is_active=True
    )
    
    db.add(default_setting)
    db.commit()
    db.refresh(default_setting)
    
    print("Default LLM settings created successfully!")

def main():
    """
    Main function to initialize the database
    """
    print("Initializing database...")
    
    # Create tables explicitly
    create_tables()
    
    # Initialize the database (create tables)
    init_db()
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create initial data
        create_initial_user(db)
        create_sample_devices(db)
        create_default_llm_settings(db)
        
        print("\nDatabase initialization completed successfully!")
        print("\nYou can now run the application with:")
        print("python -m backend.api.main")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()