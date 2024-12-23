from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
import json
from datetime import datetime

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}  # room -> {user_id -> websocket}
        self.room_messages: Dict[str, List[Dict]] = {}    # room -> list of messages

    async def connect(self, room: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room] = {}
        if room not in self.room_messages:
            self.room_messages[room] = []
        self.rooms[room][user_id] = websocket

        if self.room_messages[room]:
            history_message = json.dumps({
                "type": "chat-history",
                "messages": self.room_messages[room]
            })
            await websocket.send_text(history_message)

    def disconnect(self, room: str, user_id: str):
        if room in self.rooms and user_id in self.rooms[room]:
            del self.rooms[room][user_id]
            if not self.rooms[room]:
                if room in self.room_messages:
                    del self.room_messages[room]
                del self.rooms[room]

    def store_message(self, room: str, message_data: Dict):
        if room not in self.room_messages:
            self.room_messages[room] = []
        
        # Add timestamp to message
        message_data["timestamp"] = datetime.now().strftime("%H:%M:%S")
        self.room_messages[room].append(message_data)

    async def send_message_to_room(self, room: str, message: str, exclude_user: str = None):
        if room in self.rooms:
            message_data = json.loads(message)
            
            # Store chat messages (not signaling messages)
            if message_data.get("type") == "chat-message":
                self.store_message(room, message_data)
            
            for user_id, connection in self.rooms[room].items():
                if exclude_user is None or user_id != exclude_user:
                    await connection.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/room/{room_name}", response_class=HTMLResponse)
async def join_room(request: Request, room_name: str):
    return templates.TemplateResponse("room.html", {"request": request, "room_name": room_name})


@app.websocket("/ws/{room_name}/{user_id}")
async def signaling_endpoint(websocket: WebSocket, room_name: str, user_id: str):
    await manager.connect(room_name, user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message_to_room(room_name, data)
    except WebSocketDisconnect:
        manager.disconnect(room_name, user_id)
        disconnect_message = json.dumps({
            "type": "user-disconnected",
            "from": user_id
        })
        await manager.send_message_to_room(room_name, disconnect_message, exclude_user=user_id)