import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.core.config import Config

# Create declarative base
Base = declarative_base()

class Database:
    """Database connection and session management."""
    
    def __init__(self, config: Config):
        """
        Initialize database connection.
        
        Args:
            config: Application configuration
        """
        self.engine = create_engine(
            config.database_url,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session.
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_db(self) -> Session:
        """
        Get a database session.
        
        Returns:
            Database session
        """
        return self.SessionLocal()

# Global database instance
_db: Optional[Database] = None

def init_db(config: Config) -> Database:
    """
    Initialize the global database instance.
    
    Args:
        config: Application configuration
        
    Returns:
        Database instance
    """
    global _db
    if _db is None:
        _db = Database(config)
        _db.create_tables()
    return _db

def get_db() -> Database:
    """
    Get the global database instance.
    
    Returns:
        Database instance
        
    Raises:
        RuntimeError: If database is not initialized
    """
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db

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