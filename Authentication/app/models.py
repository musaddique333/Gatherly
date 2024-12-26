from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.core.db import Base


# ---------------------------
# Database Models
# ---------------------------
class IndividualUser(Base):
    """
    SQLAlchemy model for the 'individual_users' table.

    Attributes:
    - id (int): Unique identifier for the user (Primary Key).
    - username (str): The username of the user (optional).
    - email (str): The email address of the user (unique and indexed).
    - phone_number (str): The phone number of the user (unique).
    - hashed_password (str): The hashed password of the user.
    - is_email_verified (bool): Indicates whether the user's email is verified (default is False).
    - is_phone_verified (bool): Indicates whether the user's phone number is verified (default is False).
    """
    __tablename__ = "individual_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)

# ---------------------------
# Pydantic Schemas
# ---------------------------
class IndividualSignUp(BaseModel):
    """
    Pydantic model to validate the data for individual user sign-up.

    Attributes:
    - username (Optional[str]): The username for the user (optional).
    - email (EmailStr): The email address of the user.
    - phone_number (str): The user's phone number, must be in E.164 format.
    - password (str): The user's password, must be between 8 and 32 characters long.
    """
    username: Optional[str]
    email: EmailStr
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=8, max_length=32)

class UserLogin(BaseModel):
    """
    Pydantic model for user login.

    Attributes:
    - email (str): The email address of the user.
    - password (str): The password of the user.
    """
    email: str
    password: str