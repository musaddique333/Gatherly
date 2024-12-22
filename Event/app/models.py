from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
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
    is_online = Column(Boolean, default=True)
    organizer_email = Column(String, index=True, nullable=False)  # Foreign key to the User table in Authentication service

class EventBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str]
    location: Optional[str]
    num_members: Optional[int] = 0
    tags: Optional[List[str]] = []
    is_online: bool

class EventCreate(EventBase):
    organizer_email: str  # email ID of the user organizing the event

class EventUpdate(EventBase):
    pass

class EventOut(EventBase):
    id: int

    class Config:
        orm_mode = True

class EventMember(Base):
    __tablename__ = "event_members"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    user_email = Column(String, nullable=False, index=True)

    event = relationship("Event", back_populates="members")  # Relationship back to Event

    __table_args__ = (UniqueConstraint("event_id", "user_email", name="unique_event_user"),)

class EventMemberBase(BaseModel):
    event_id: int
    user_email: EmailStr

class EventMemberCreate(EventMemberBase):
    pass

class EventMemberOut(EventMemberBase):
    id: int

    class Config:
        orm_mode = True