from datetime import datetime, timezone
from app.models import RoomMessage, RoomMessagesResponse
from app.core.db import collection
from app.utils import encrypt_message, decrypt_message

# Function to insert a message into a room
async def insert_message(room_id: str, user_id: str, message: str) -> dict:
    timestamp = datetime.now(timezone.utc)

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
        await collection.update_one(
            {"room_id": room_id},
            {"$push": 
                    {
                        "messages": 
                                    {
                                    "user_id": user_id, 
                                    "message": encrypted_message, 
                                    "timestamp": timestamp
                                    }
                    }
            }
        )
    else:
        await collection.insert_one(room_message)

    return {"room_id": room_id, "message": "Message added successfully."}

# Function to get all messages from a room
async def get_messages(room_id: str) -> RoomMessagesResponse:
    # Query to find the room
    room = await collection.find_one({"room_id": room_id})

    if not room:
        return RoomMessagesResponse(room_id=room_id, messages=[])  # Room doesn't exist

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
