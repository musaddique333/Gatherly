from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict, List

app = FastAPI()

# Serve templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class ConnectionManager:
    def __init__(self):
        # Each room has its own list of WebSocket connections
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        if room in self.rooms:
            self.rooms[room].remove(websocket)
            if not self.rooms[room]:  # If the room is empty, remove it
                del self.rooms[room]

    async def send_message_to_room(self, room: str, message: str):
        if room in self.rooms:
            for connection in self.rooms[room]:
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
    await manager.connect(room_name, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message_to_room(room_name, data)
    except WebSocketDisconnect:
        manager.disconnect(room_name, websocket)