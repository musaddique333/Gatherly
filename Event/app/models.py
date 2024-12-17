from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.core.db import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    num_members = Column(Integer, default=0)
    tags = Column(ARRAY(String), nullable=True)  # List of tags
    is_online = Column(Boolean, default=False)
    organizer_id = Column(Integer, nullable=False)  # Foreign key to the User table in Authentication service

class EventBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str]
    location: Optional[str]
    num_members: Optional[int] = 0
    tags: Optional[List[str]] = []
    is_online: bool

class EventCreate(EventBase):
    organizer_id: int  # ID of the user organizing the event

class EventUpdate(EventBase):
    pass

class EventOut(EventBase):
    id: int

    class Config:
        orm_mode = True
