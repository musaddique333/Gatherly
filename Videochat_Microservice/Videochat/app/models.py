from pydantic import BaseModel, Field
from datetime import datetime

# Pydantic Schema for Message
class RoomMessage(BaseModel):
    """
    Represents a message in a room.

    Attributes:
        user_id (str): The ID of the user who sent the message.
        message (str): The content of the message.
        timestamp (datetime): The timestamp when the message was sent.
    """
    user_id: str = Field(..., description="The ID of the user who sent the message.")
    message: str = Field(..., description="The content of the message.")
    timestamp: datetime = Field(..., description="The timestamp when the message was sent.")


# Pydantic Schema for Room
class RoomSchema(BaseModel):
    """
    Represents a room containing messages.

    Attributes:
        room_id (str): Unique ID for the room.
        messages (List[RoomMessage]): List of messages in the room.
    """
    room_id: str = Field(..., description="Unique ID for the room.")
    messages: list[RoomMessage] = Field(..., description="List of messages in the room.")



# Response model for fetching room messages
class RoomMessagesResponse(BaseModel):
    """
    Response model for fetching messages from a specific room.

    Attributes:
        room_id (str): The unique ID of the room.
        messages (List[RoomMessage]): The list of messages in the room.
    """
    room_id: str
    messages: list[RoomMessage]
