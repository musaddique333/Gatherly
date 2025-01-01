from datetime import datetime, timezone
from uuid import UUID

from app.models import RoomMessage, RoomMessagesResponse
from app.core.db import collection
from app.utils import encrypt_message, decrypt_message
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Function to insert a message into a room
async def insert_message(room_id: UUID, user_id: str, message: str) -> dict:
    """
    Insert a message into a specific room. If the room doesn't exist, it will be created.

    Args:
        room_id (str): The ID of the room to insert the message into.
        user_id (str): The ID of the user sending the message.
        message (str): The message to be sent.

    Returns:
        dict: A response containing the room ID and a success message.

    Raises:
        Exception: If any error occurs during the database operation.
    """
    try:
        timestamp = datetime.now(timezone.utc)

        # Encrypt the message before storing
        encrypted_message = encrypt_message(message)

        room_message = {
            "room_id": room_id,
            "messages": [
                {"user_id": user_id, 
                 "message": encrypted_message, 
                 "timestamp": timestamp
                }
            ]
        }
        
        # Check if room exists, otherwise create it
        existing_room = await collection.find_one({"room_id": room_id})
        if existing_room:
            # If the room exists, push the new message
            await collection.update_one(
                {"room_id": room_id},
                {"$push": {
                        "messages": {
                            "user_id": user_id, 
                            "message": encrypted_message, 
                            "timestamp": timestamp
                        }
                    }
                }
            )
        else:
            # If the room doesn't exist, create a new room and insert the message
            await collection.insert_one(room_message)

        return {"room_id": room_id, "message": "Message added successfully."}
    
    except Exception as e:
        logger.error(f"Error inserting message into room {room_id}: {e}")
        raise Exception(f"Error inserting message into room {room_id}: {e}")

# Function to get all messages from a room
async def get_messages(room_id: UUID) -> RoomMessagesResponse:
    """
    Retrieve all messages from a specific room, sorted by timestamp, and decrypt the messages.

    Args:
        room_id (str): The ID of the room to retrieve messages from.

    Returns:
        RoomMessagesResponse: A Pydantic model containing the room ID and a list of messages.

    Raises:
        Exception: If any error occurs during the database operation.
    """
    try:
        # Query to find the room
        room = await collection.find_one({"room_id": room_id})

        if not room:
            # If the room doesn't exist, return an empty message list
            return RoomMessagesResponse(room_id=room_id, messages=[])

        # Retrieve and sort messages in ascending order by timestamp
        messages = room.get("messages", [])
        sorted_messages = sorted(messages, key=lambda msg: msg["timestamp"])  # Sort by timestamp in ascending order

        # Decrypt messages and convert to Pydantic models
        filtered_messages = [
            RoomMessage(
                **{
                    "user_id": msg["user_id"],
                    "message": decrypt_message(msg["message"]),
                    "timestamp": msg["timestamp"]
                }
            )
            for msg in sorted_messages
        ]
        
        return RoomMessagesResponse(room_id=room_id, messages=filtered_messages)
    
    except Exception as e:
        logger.error(f"Error retrieving messages from room {room_id}: {e}")
        raise Exception(f"Error retrieving messages from room {room_id}: {e}")
