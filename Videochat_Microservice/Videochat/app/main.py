from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.manager import ConnectionManager
from app.services.wait_for_mongo import wait_for_mongo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for MongoDB to be ready before starting the app
wait_for_mongo()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()

@app.websocket("/ws/{room_id}/{user_id}")
async def signaling_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """
    WebSocket endpoint to handle real-time communication for a specific room and user.
    
    This endpoint establishes a WebSocket connection, listens for messages, and broadcasts
    them to all other connected users in the same room.

    Args:
        websocket (WebSocket): The WebSocket connection object used to communicate with the client.
        room_id (str): The ID of the room the user is connecting to.
        user_id (str): The unique ID of the user connecting to the room.
    """
    logger.info(f"New WebSocket connection - Room: {room_id}, User: {user_id}")
    await manager.connect(room_id, user_id, websocket)

    try:
        while True:
            # Receive messages from the WebSocket and broadcast them
            data = await websocket.receive_text()
            await manager.broadcast(room_id, user_id, data)
    except WebSocketDisconnect:
        # Handle disconnection of the user
        logger.info(f"User {user_id} disconnected from Room {room_id}")
        await manager.disconnect(room_id, user_id, websocket)
    except Exception as e:
        # Catch unexpected exceptions and log the error
        logger.error(f"An error occurred while handling WebSocket communication: {e}")
        await websocket.close()
