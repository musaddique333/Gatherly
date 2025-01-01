from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.core.config import settings

# Database connection URL from settings
SQLALCHEMY_DATABASE_URL = settings.SUPABASE_DATABASE_URL

# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal factory to create a new session instance
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Dependency to retrieve the DB session for each request.
    
    This function will yield a database session that can be used in the route handlers.
    After the request completes, the session is closed.
    """
    db = SessionLocal()
    try:
        yield db  # Provides the database session to the caller
    except Exception as e:
        # Handle exception (if needed)
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
    finally:
        db.close()
