from fastapi import WebSocket
import logging
import json
import asyncio

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

    async def connect(self, room_id: str, user_id: str, websocket: WebSocket):
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


    async def disconnect(self, room_id: str, user_id: str, websocket: WebSocket):
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
        await self.broadcast_disconnect_message(room_id, user_id)

    # async def broadcast(self, room_id: str, user_id: str, message: str, websocket: WebSocket):
    #     """
    #     Broadcasts a message to all users in a room.

    #     Args:
    #         room_id (str): The ID of the room.
    #         user_id (str): The ID of the user sending the message.
    #         message (str): The message to broadcast in JSON format.

    #     This method saves the message to the database and sends it to all connected 
    #     users in the room. If there is an error, it handles disconnecting users properly.
    #     """
    #     try:
    #         # Add this message to MongoDB with room_id and user_id
    #         message_data = json.loads(message)

    #         logger.info(f"Broadcasting message: {message_data}")
    #         # Save the message to MongoDB

    #         if message_data["message"] == "user connected":
    #             # Send all previous messages to the new user when they join the room
    #             await self.send_previous_messages(room_id, websocket)
    #         else:
    #             print(message_data)
    #             await insert_message(room_id, user_id, message_data["message"])

    #         logger.info("Inserted message to MongoDB")
    #         # Broadcast this message to all connected users
    #         if room_id in self.rooms:
    #             logger.info(f"Broadcasting message to room {room_id}")
    #             for user_id, connections in list(self.rooms[room_id].items()):
    #                 logger.info(f"Broadcasting message to user {user_id}")
    #                 for connection in connections:
    #                     logger.info(f"Sending message to user {user_id} in for connection {connection}")
    #                     try:

    #                         rtc_data = json.loads(message_data["message"])

    #                         if rtc_data.get("type") in ["offer", "answer", "ice-candidate"]:
    #                             broadcast_message = message_data
    #                         else:
    #                         # Build the full message structure before sending
    #                             broadcast_message = {
    #                                 "user_id": user_id,
    #                                 "message": message_data["message"],
    #                                 "timestamp": datetime.now(timezone.utc).isoformat()
    #                             }
                            
    #                         # Send the complete message as JSON to the WebSocket
    #                         await connection.send_text(json.dumps(broadcast_message))

    #                         logger.info(f"Sent message to user {user_id}: {broadcast_message}")
    #                     except Exception as e:
    #                         logger.error(f"Error sending message to user {user_id}: {e}")
    #                         self.disconnect(room_id, user_id, connection)
    #     except Exception as e:
    #         logger.error(f"Error in broadcast: {e}")


    async def broadcast(self, room_id: str, user_id: str, message: str, websocket: WebSocket):
        try:
            message_data = json.loads(message)
            logger.info(f"Broadcasting message: {message_data}")

            # Handle different message types
            if message_data.get("type") == "new-user":
                logger.info(f"New user message received: {message_data}")
                await self.send_previous_messages(room_id, websocket)

                new_user_message = {
                    "type": "new-user",
                    "user_id": user_id,
                    "message": message_data["message"]
                }

                if room_id in self.rooms:
                    for other_user_id, connections in list(self.rooms[room_id].items()):
                        for connection in connections:
                            try:
                                await connection.send_text(json.dumps(new_user_message))
                                logger.info(f"Sent new-user notification to {other_user_id}")
                            except Exception as e:
                                logger.error(f"Error sending new-user message to {other_user_id}: {e}")
                                await self.disconnect(room_id, other_user_id, connection)

            elif message_data.get("type") == "offer":
                logger.info(f"Offer message received from {user_id}: {message_data}")
                target_user_id = message_data.get("to")
                if target_user_id and room_id in self.rooms:
                    if target_user_id in self.rooms[room_id]:
                        for connection in self.rooms[room_id][target_user_id]:
                            try:
                                offer_message = {
                                    "type": "offer",
                                    "user_id": user_id,
                                    "offer": message_data["offer"]
                                }
                                await connection.send_text(json.dumps(offer_message))
                                logger.info(f"Sent offer to user {target_user_id}")
                            except Exception as e:
                                logger.error(f"Error sending offer to user {target_user_id}: {e}")
                                await self.disconnect(room_id, target_user_id, connection)
                    else:
                        logger.warning(f"Target user {target_user_id} not in room {room_id}")
                else:
                    logger.warning(f"Invalid target user or room for offer: {message_data}")

            elif message_data.get("type") == "answer":
                logger.info(f"Answer message received from {user_id}: {message_data}")
                target_user_id = message_data.get("to")
                if target_user_id and room_id in self.rooms:
                    if target_user_id in self.rooms[room_id]:
                        for connection in self.rooms[room_id][target_user_id]:
                            try:
                                answer_message = {
                                    "type": "answer",
                                    "user_id": user_id,
                                    "answer": message_data["answer"]
                                }
                                await connection.send_text(json.dumps(answer_message))
                                logger.info(f"Sent answer to user {target_user_id}")
                            except Exception as e:
                                logger.error(f"Error sending answer to user {target_user_id}: {e}")
                                await self.disconnect(room_id, target_user_id, connection)
                    else:
                        logger.warning(f"Target user {target_user_id} not in room {room_id}")
                else:
                    logger.warning(f"Invalid target user or room for answer: {message_data}")

            else:
                # Handle regular messages
                await insert_message(room_id, user_id, message_data["message"])
                logger.info("Inserted message to MongoDB")

                if room_id in self.rooms:
                    logger.info(f"Broadcasting message to room {room_id}")
                    for room_user_id, connections in list(self.rooms[room_id].items()):
                        for connection in connections:
                            try:
                                broadcast_message = {
                                    "user_id": room_user_id,
                                    "message": message_data["message"],
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                                await connection.send_text(json.dumps(broadcast_message))
                                logger.info(f"Sent message to user {room_user_id}: {broadcast_message}")
                            except Exception as e:
                                logger.error(f"Error sending message to user {room_user_id}: {e}")
                                await self.disconnect(room_id, room_user_id, connection)

        except Exception as e:
            logger.error(f"Error in broadcast: {e}")


    async def send_previous_messages(self, room_id: str, websocket: WebSocket):
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
                    "type": "chat-history",
                    "user_id": msg.user_id,
                    "message": msg.message,
                    "timestamp": msg.timestamp.isoformat()
                }

                logger.info(f"Sending message: {message}")
                await websocket.send_text(json.dumps(message))  # Send the message as JSON

    async def broadcast_disconnect_message(self, room_id: str, user_id: str):
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
