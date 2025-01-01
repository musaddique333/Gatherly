from fastapi import WebSocket
import logging
import json
from uuid import UUID

from app.crud import insert_message, get_messages
from app.models import RoomMessagesResponse
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for rooms and users.

    This class is responsible for handling new WebSocket connections, disconnects, 
    broadcasting messages, and sending previous room messages to newly connected users.
    """

    def __init__(self):
        """
        Initializes the ConnectionManager instance.

        Creates a dictionary `rooms` where keys are room IDs and values are 
        dictionaries mapping user IDs to lists of WebSocket connections.
        """
        self.rooms: dict[str, dict[str, list[WebSocket]]] = {}

    async def connect(self, room_id: UUID, user_id: str, websocket: WebSocket):
        """
        Establishes a new WebSocket connection for a user in a room.

        Args:
            room_id (str): The ID of the room.
            user_id (str): The ID of the user.
            websocket (WebSocket): The WebSocket connection.

        This method accepts the WebSocket connection, adds the user to the room, 
        and sends all previous messages in the room to the newly connected user.
        """
        logger.info(f"New connection request - Room: {room_id}, User: {user_id}")
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        if user_id not in self.rooms[room_id]:
            self.rooms[room_id][user_id] = []
        self.rooms[room_id][user_id].append(websocket)

        # Send all previous messages to the new user when they join the room
        await self.send_previous_messages(room_id, websocket)

    def disconnect(self, room_id: UUID, user_id: str, websocket: WebSocket):
        """
        Disconnects a user from a room.

        Args:
            room_id (str): The ID of the room.
            user_id (str): The ID of the user.
            websocket (WebSocket): The WebSocket connection.

        This method removes the user's WebSocket connection and sends a disconnect 
        message to all remaining users in the room.
        """
        logger.info(f"Disconnecting user {user_id} from room {room_id}")
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            if websocket in self.rooms[room_id][user_id]:
                self.rooms[room_id][user_id].remove(websocket)
            if not self.rooms[room_id][user_id]:
                del self.rooms[room_id][user_id]
            if not self.rooms[room_id]:
                del self.rooms[room_id]
        
        # Broadcast disconnect message to remaining users
        # Save this disconnect event to MongoDB as well
        self.broadcast_disconnect_message(room_id, user_id)

    async def broadcast(self, room_id: UUID, user_id: str, message: str):
        """
        Broadcasts a message to all users in a room.

        Args:
            room_id (str): The ID of the room.
            user_id (str): The ID of the user sending the message.
            message (str): The message to broadcast in JSON format.

        This method saves the message to the database and sends it to all connected 
        users in the room. If there is an error, it handles disconnecting users properly.
        """
        try:
            # Add this message to MongoDB with room_id and user_id
            message_data = json.loads(message)

            # Save the message to MongoDB
            await insert_message(room_id, user_id, message_data["message"])

            # Broadcast this message to all connected users
            if room_id in self.rooms:
                for user_id, connections in list(self.rooms[room_id].items()):
                    for connection in connections:
                        try:
                            # Build the full message structure before sending
                            broadcast_message = {
                                "user_id": user_id,
                                "message": message_data["message"],
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }

                            # Send the complete message as JSON to the WebSocket
                            await connection.send_text(json.dumps(broadcast_message))
                        except Exception as e:
                            logger.error(f"Error sending message to user {user_id}: {e}")
                            self.disconnect(room_id, user_id, connection)
        except Exception as e:
            logger.error(f"Error in broadcast: {e}")

    async def send_previous_messages(self, room_id: UUID, websocket: WebSocket):
        """
        Sends all previous messages from a room to a newly connected user.

        Args:
            room_id (str): The ID of the room.
            websocket (WebSocket): The WebSocket connection of the new user.

        This method retrieves all the messages for the room from the database 
        and sends them to the newly connected user.
        """
        # Fetch all previous messages from MongoDB for this room
        room_messages: RoomMessagesResponse = await get_messages(room_id)

        if room_messages.messages:
            # Send each message to the user
            for msg in room_messages.messages:
                message = {
                    "user_id": msg.user_id,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat()
                }
                await websocket.send_text(json.dumps(message))  # Send the message as JSON

    async def broadcast_disconnect_message(self, room_id: UUID, user_id: str):
        """
        Broadcasts a disconnect message when a user leaves the room.

        Args:
            room_id (str): The ID of the room.
            user_id (str): The ID of the user who is disconnecting.

        This method sends a message to all remaining users in the room indicating 
        that the user has disconnected and saves the disconnect message to the database.
        """
        # Save the disconnect message to MongoDB
        disconnect_message = {
            "room_id": room_id,
            "user_id": user_id,
            "message": f"User {user_id} has disconnected.",
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Save disconnect message to MongoDB
        await insert_message(room_id, user_id, disconnect_message["message"])

        # Broadcast the disconnect message to remaining users
        message = json.dumps({
            "user_id": user_id,
            "message": f"User {user_id} has disconnected.",
            "timestamp": disconnect_message["timestamp"].isoformat()
        })
        
        if room_id in self.rooms:
            for user_id, connections in list(self.rooms[room_id].items()):
                for connection in connections:
                    try:
                        await connection.send_text(message)  # Send the disconnect message
                    except Exception as e:
                        logger.error(f"Error sending disconnect message to user {user_id}: {e}")
                        self.disconnect(room_id, user_id, connection)
