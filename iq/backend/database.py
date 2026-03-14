"""
Database Configuration - SQLAlchemy setup for IQ Analyzer
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./iq_analyzer.db")

# Create database directory if it doesn't exist
db_dir = Path(DATABASE_URL.replace("sqlite:///", "").replace("/", "\\")).parent
db_dir.mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 20
    },
    echo=False  # Set to True for SQL logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    from backend.models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """
    Drop all tables (for testing)
    """
    from backend.models import Base
    Base.metadata.drop_all(bind=engine)
