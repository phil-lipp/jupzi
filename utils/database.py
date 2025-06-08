import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_database_url() -> str:
    """
    Construct the database URL based on environment variables.
    When TESTING_ENVIRONMENT is True, appends '_test' to the database name.
    """
    base_url = os.getenv('DATABASE_URL', '')
    if os.getenv('TESTING_ENVIRONMENT', '').lower() == 'true':
        # Replace the database name with its test version
        base_url = base_url.replace(
            f"/{os.getenv('POSTGRES_DB')}",
            f"/{os.getenv('POSTGRES_DB')}_test"
        )
    return base_url

def get_engine():
    """Create and return a SQLAlchemy engine."""
    return create_engine(get_database_url())

def get_session() -> Session:
    """Create and return a SQLAlchemy session."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_db():
    """Initialize the database by creating all tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI or other frameworks to get a database session."""
    db = get_session()
    try:
        yield db
    finally:
        db.close() 