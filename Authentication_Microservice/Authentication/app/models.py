from sqlalchemy import Column, Integer, String, Boolean
from app.core.db import Base
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Individual user model for sign up
class IndividualSignUp(BaseModel):
    username: Optional[str]
    email: EmailStr
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')  # Basic E.164 format for phone numbers
    password: str = Field(..., min_length=8, max_length=32)

class UserLogin(BaseModel):
    email: str
    password: str

class IndividualUser(Base):
    __tablename__ = "individual_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
