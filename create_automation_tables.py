#!/usr/bin/env python3
"""
Database migration script to create automation-related tables.
Run this script to ensure the automation_tasks table is created.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from backend.database.models import Base, AutomationTask
from backend.database.connection import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_automation_tables():
    """Create automation-related tables in the database"""
    try:
        # Get database URL
        logger.info(f"Connecting to database: {DATABASE_URL}")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create all tables (this will only create missing tables)
        logger.info("Creating automation tables...")
        Base.metadata.create_all(engine, checkfirst=True)
        
        # Verify table creation (SQLite compatible)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='automation_tasks'
            """))
            if result.fetchone():
                logger.info("✅ automation_tasks table created successfully")
            else:
                logger.error("❌ Failed to create automation_tasks table")
                
        logger.info("Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise

if __name__ == "__main__":
    create_automation_tables()
