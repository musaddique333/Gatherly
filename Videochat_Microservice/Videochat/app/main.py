from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from app.core.manager import ConnectionManager
from app.services.wait_for_mongo import wait_for_mongo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wait for MongoDB to be ready before starting the app
wait_for_mongo()

app = FastAPI()

manager = ConnectionManager()

@app.get("/")
async def get_home():
    """
    Home page route that provides a welcome message and instructions to connect via React.
    
    Returns:
        dict: A message welcoming users to the WebSocket Room API.
    """
    return {"message": "Welcome to the WebSocket Room API! Connect via React."}

@app.get("/room/")
async def join_room(request: Request):
    """
    API route to join a room by providing the room_id and user_id as query parameters.
    
    Args:
        request (Request): The incoming request object that holds the query parameters.
        
    Returns:
        dict: Room ID and User ID if provided, or an error message if either is missing.
    """
    room_id = request.query_params.get("room_id")
    user_id = request.query_params.get("user_id")

    if not room_id or not user_id:
        return {"error": "Room ID and User ID are required."}, 400

    return {"room_id": room_id, "user_id": user_id}

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
