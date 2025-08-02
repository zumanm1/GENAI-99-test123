from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
# Use DB_URL for SQLite or DATABASE_URL for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL", "sqlite:///data/app.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    Dependency to get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables
    """
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)