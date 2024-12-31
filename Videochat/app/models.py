from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Pydantic Schema for Message
class RoomMessage(BaseModel):
    user_id: str = Field(..., description="The ID of the user who sent the message.")
    message: str = Field(..., description="The content of the message.")
    timestamp: datetime = Field(..., description="The timestamp when the message was sent.")

# Pydantic Schema for Room
class RoomSchema(BaseModel):
    room_id: str = Field(..., description="Unique ID for the room.")
    messages: List[RoomMessage] = Field(..., description="List of messages in the room.")

# Response model for fetching room messages
class RoomMessagesResponse(BaseModel):
    room_id: str
    messages: List[RoomMessage]