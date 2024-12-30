from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import json
from datetime import datetime
import redis
import os
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
    retry_on_timeout=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

class ConnectionManager:
    def __init__(self):
        #Uncomment this line and comment the next one 
        # self.rooms: Dict[str, Dict[str, WebSocket]] = {}
        self.rooms: Dict[str, Dict[str, List[WebSocket]]] = {}

                
    def get_redis_key(self, room: str) -> str:
        return f"chat_messages:{room}"

    async def connect(self, room: str, user_id: str, websocket: WebSocket):
        logger.info(f"New connection request - Room: {room}, User: {user_id}")
        await websocket.accept()
        
        if room not in self.rooms:
            self.rooms[room] = {}
        if user_id not in self.rooms[room]:
            self.rooms[room][user_id] = []
        self.rooms[room][user_id].append(websocket)

        try:
            history = self.get_message_history(room)
            logger.info(f"Retrieved {len(history)} messages for room {room}")
            
            if history:
                history_message = json.dumps({
                    "type": "chat-history",
                    "messages": history
                })
                await websocket.send_text(history_message)
                logger.info(f"Sent message history to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending message history: {e}")

    def disconnect(self, room: str, user_id: str, websocket: WebSocket):
        logger.info(f"Disconnecting user {user_id} from room {room}")
        if room in self.rooms and user_id in self.rooms[room]:
            if websocket in self.rooms[room][user_id]:
                self.rooms[room][user_id].remove(websocket)
            if not self.rooms[room][user_id]:
                del self.rooms[room][user_id]
            if not self.rooms[room]:
                del self.rooms[room]

    def store_message(self, room: str, message_data: Dict):
        try:
            if message_data.get("type") == "chat-message":
                redis_key = self.get_redis_key(room)

                if "timestamp" not in message_data:
                    message_data["timestamp"] = datetime.now().strftime("%H:%M:%S")
                
                message_json = json.dumps(message_data)
                logger.info(f"Storing message in Redis - Room: {room}, Message: {message_json}")

                redis_client.rpush(redis_key, message_json)
                redis_client.expire(redis_key, 24 * 60 * 60)

                stored_messages = redis_client.lrange(redis_key, -1, -1)
                logger.info(f"Verification - Last stored message: {stored_messages[0] if stored_messages else 'None'}")
        except Exception as e:
            logger.error(f"Error storing message: {e}")
    
    def get_message_history(self, room: str) -> List[Dict]:
        try:
            redis_key = self.get_redis_key(room)
            messages = redis_client.lrange(redis_key, 0, -1)
            logger.info(f"Retrieved raw messages from Redis for room {room}: {messages}")
            
            history = []
            for msg_json in messages:
                try:
                    msg = json.loads(msg_json)
                    if msg.get("type") == "chat-message":
                        history.append(msg)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding message: {e}")
                    continue
            
            logger.info(f"Processed message history for room {room}: {history}")
            return history
            
        except Exception as e:
            logger.error(f"Error getting message history: {e}")
            return []

    async def send_message_to_room(self, room: str, message: str, exclude_user: str = None):
        try:
            message_data = json.loads(message)
            # logger.info(f"Sending message to room {room}: {message}")

            self.store_message(room, message_data)
            history = self.get_message_history(room)
            if history:
                history_message = json.dumps({
                    "type": "chat-history",
                    "messages": history
                })

            if room in self.rooms:
                for user_id, connections in list(self.rooms[room].items()):
                    if exclude_user is None or user_id != exclude_user:
                        for connection in connections:
                            try:
                                await connection.send_text(history_message)
                            except Exception as e:
                                logger.error(f"Error sending message to user {user_id}: {e}")
                                self.disconnect(room, user_id, connection)
        except Exception as e:
            logger.error(f"Error in send_message_to_room: {e}")


    
    #Uncomment the code below to see actual backend
        
    # async def connect(self, room: str, user_id: str, websocket: WebSocket):
    #     logger.info(f"New connection request - Room: {room}, User: {user_id}")
    #     await websocket.accept()
        
    #     if room not in self.rooms:
    #         self.rooms[room] = {}
    #     self.rooms[room][user_id] = websocket
        
    #     try:
    #         history = self.get_message_history(room)
    #         logger.info(f"Retrieved {len(history)} messages for room {room}")
            
    #         if history:
    #             history_message = json.dumps({
    #                 "type": "chat-history",
    #                 "messages": history
    #             })
    #             await websocket.send_text(history_message)
    #             logger.info(f"Sent message history to user {user_id}")
    #     except Exception as e:
    #         logger.error(f"Error sending message history: {e}")
    
    # def disconnect(self, room: str, user_id: str):
    #     logger.info(f"Disconnecting user {user_id} from room {room}")
    #     if room in self.rooms and user_id in self.rooms[room]:
    #         del self.rooms[room][user_id]
    #         if not self.rooms[room]:
    #             del self.rooms[room]
    
    # def store_message(self, room: str, message_data: Dict):
    #     try:
    #         if message_data.get("type") == "chat-message":
    #             redis_key = self.get_redis_key(room)
                
    #             if "timestamp" not in message_data:
    #                 message_data["timestamp"] = datetime.now().strftime("%H:%M:%S")
                
    #             message_json = json.dumps(message_data)
    #             logger.info(f"Storing message in Redis - Room: {room}, Message: {message_json}")

    #             redis_client.rpush(redis_key, message_json)
    #             redis_client.expire(redis_key, 24 * 60 * 60)  # 24 hours expiry

    #             stored_messages = redis_client.lrange(redis_key, -1, -1)
    #             logger.info(f"Verification - Last stored message: {stored_messages[0] if stored_messages else 'None'}")
    #     except Exception as e:
    #         logger.error(f"Error storing message: {e}")
    
    # def get_message_history(self, room: str) -> List[Dict]:
    #     try:
    #         redis_key = self.get_redis_key(room)
    #         messages = redis_client.lrange(redis_key, 0, -1)
    #         logger.info(f"Retrieved raw messages from Redis for room {room}: {messages}")
            
    #         history = []
    #         for msg_json in messages:
    #             try:
    #                 msg = json.loads(msg_json)
    #                 if msg.get("type") == "chat-message":
    #                     history.append(msg)
    #             except json.JSONDecodeError as e:
    #                 logger.error(f"Error decoding message: {e}")
    #                 continue
            
    #         logger.info(f"Processed message history for room {room}: {history}")
    #         return history
            
    #     except Exception as e:
    #         logger.error(f"Error getting message history: {e}")
    #         return []
    
    # async def send_message_to_room(self, room: str, message: str, exclude_user: str = None):
    #     try:
    #         message_data = json.loads(message)
    #         logger.info(f"Sending message to room {room}: {message}")

    #         self.store_message(room, message_data)

    #         if room in self.rooms:
    #             for user_id, connection in list(self.rooms[room].items()):
    #                 if exclude_user is None or user_id != exclude_user:
    #                     try:
    #                         await connection.send_text(message)
    #                     except Exception as e:
    #                         logger.error(f"Error sending message to user {user_id}: {e}")
    #                         self.disconnect(room, user_id)
    #     except Exception as e:
    #         logger.error(f"Error in send_message_to_room: {e}")

manager = ConnectionManager()

@app.get("/health")
async def health_check():
    try:
        redis_client.ping()
        all_keys = redis_client.keys("chat_messages:*")
        logger.info(f"Redis health check - All chat keys: {all_keys}")
        return {
            "status": "healthy",
            "redis": "connected",
            "chat_rooms": all_keys
        }
    except redis.RedisError as e:
        logger.error(f"Redis health check failed: {e}")
        return {"status": "unhealthy", "redis": "disconnected"}

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/room/{room_name}", response_class=HTMLResponse)
async def join_room(request: Request, room_name: str):
    return templates.TemplateResponse("room.html", {"request": request, "room_name": room_name})

# @app.websocket("/ws/{room_name}/{user_id}")
# async def signaling_endpoint(websocket: WebSocket, room_name: str, user_id: str):
#     logger.info(f"New WebSocket connection - Room: {room_name}, User: {user_id}")
#     await manager.connect(room_name, user_id, websocket)
    
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_message_to_room(room_name, data)
#     except WebSocketDisconnect:
#         logger.info(f"WebSocket disconnected - Room: {room_name}, User: {user_id}")
#         manager.disconnect(room_name, user_id)
#         disconnect_message = json.dumps({
#             "type": "user-disconnected",
#             "from": user_id
#         })
#         await manager.send_message_to_room(room_name, disconnect_message, exclude_user=user_id)

#comment the code below for actual working backend
@app.websocket("/ws/{room_name}/{user_id}")
async def signaling_endpoint(websocket: WebSocket, room_name: str, user_id: str):
    logger.info(f"New WebSocket connection - Room: {room_name}, User: {user_id}")
    await manager.connect(room_name, user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message_to_room(room_name, data)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected - Room: {room_name}, User: {user_id}")
        manager.disconnect(room_name, user_id, websocket)
        
        disconnect_message = json.dumps({
            "type": "user-disconnected",
            "from": user_id
        })
        await manager.send_message_to_room(room_name, disconnect_message, exclude_user=user_id)