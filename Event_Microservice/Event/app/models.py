from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from uuid import UUID as N_UUID
from uuid import uuid4
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from app.core.db import Base

# ---------------------------
# Database Models
# ---------------------------

class Event(Base):
    """
    Represents an event entity in the database.

    Attributes:
        id (UUID): Primary key of the event, auto-generated in UUID format.
        title (str): Title of the event.
        date (datetime): Date and time of the event.
        description (str, optional): Description of the event.
        location (str, optional): Physical or virtual location of the event.
        tags (List[str], optional): List of tags associated with the event.
        is_online (bool): Indicates if the event is online.
        organizer_email (str): Email of the event organizer.
    """
    __tablename__ = "events"

    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    title = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    is_online = Column(Boolean, default=True)
    organizer_email = Column(String, index=True, nullable=False)

    # Relationships
    reminders = relationship("Reminder", back_populates="event")
    members = relationship("EventMember", back_populates="event")


class EventMember(Base):
    """
    Represents a member of an event.

    Attributes:
        id (int): Primary key of the event member.
        event_id (int): Foreign key to the Event table.
        user_email (str): Email of the member participating in the event.
    """
    __tablename__ = "event_members"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False, index=True)
    user_email = Column(String, nullable=False, index=True)

    # Relationships
    event = relationship("Event", back_populates="members")

    # Constraints
    __table_args__ = (UniqueConstraint('event_id', 'user_email', name='unique_event_member'),)


class Reminder(Base):
    """
    Represents a reminder for an event.

    Attributes:
        id (int): Primary key of the reminder.
        event_id (int): Foreign key to the Event table.
        user_email (str): Email of the user to receive the reminder.
        reminder_time (datetime): Time of the reminder.
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False, index=True)
    user_email = Column(String, nullable=False)
    reminder_time = Column(DateTime, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="reminders")

# ---------------------------
# Pydantic Schemas
# ---------------------------

class EventBase(BaseModel):
    """
    Base schema for event operations.

    Attributes:
        title (str): Title of the event.
        date (datetime): Date and time of the event.
        description (Optional[str]): Description of the event.
        location (Optional[str]): Physical or virtual location of the event.
        tags (Optional[List[str]]): List of tags for the event.
        is_online (bool): Indicates if the event is online.
    """
    title: str
    date: datetime
    description: Optional[str]
    location: Optional[str]
    tags: Optional[List[str]] = []
    is_online: bool


class EventCreate(EventBase):
    """
    Schema for creating an event.

    Attributes:
        organizer_email (str): Email of the event organizer.
    """
    organizer_email: str


class EventUpdate(EventBase):
    """Schema for updating an event."""
    pass


class EventOut(EventBase):
    """
    Schema for retrieving event details.

    Attributes:
        id (UUID): Unique identifier of the event.
    """
    id: N_UUID

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class EventMemberBase(BaseModel):
    """
    Base schema for event member operations.

    Attributes:
        event_id (UUID): ID of the event.
        user_email (EmailStr): Email of the member.
    """
    event_id: N_UUID
    user_email: EmailStr


class EventMemberCreate(EventMemberBase):
    """Schema for creating an event member."""
    pass


class EventMemberOut(EventMemberBase):
    """
    Schema for retrieving event member details.

    Attributes:
        id (int): Unique identifier of the event member.
    """
    id: int

    class Config:
        from_attributes = True


class ReminderCreate(BaseModel):
    """
    Schema for creating a reminder.

    Attributes:
        event_id (UUID): ID of the associated event.
        user_email (str): Email of the user to receive the reminder.
        reminder_time (datetime): Time of the reminder.
    """
    event_id: N_UUID
    user_email: str
    reminder_time: datetime


class ReminderOut(ReminderCreate):
    """
    Schema for retrieving reminder details.

    Attributes:
        id (int): Unique identifier of the reminder.
    """
    id: int

    class Config:
        from_attributes = True
