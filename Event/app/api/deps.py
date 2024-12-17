from sqlalchemy.orm import Session
from app.core.db import SessionLocal

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
