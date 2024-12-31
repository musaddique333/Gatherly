from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from app.core.manager import ConnectionManager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

manager = ConnectionManager()

# Home page - to input room_id and user_id
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Join Room</title>
    </head>
    <body>
        <h2>Join Room</h2>
        <form action="/room/" method="get">
            <label for="room_id">Room ID:</label>
            <input type="text" id="room_id" name="room_id" required><br><br>
            <label for="user_id">User ID:</label>
            <input type="text" id="user_id" name="user_id" required><br><br>
            <button type="submit">Join Room</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Room page - to send messages and view conversation
@app.get("/room/", response_class=HTMLResponse)
async def join_room(request: Request):
    room_id = request.query_params.get("room_id")
    user_id = request.query_params.get("user_id")

    if not room_id or not user_id:
        return HTMLResponse(content="Room ID and User ID are required", status_code=400)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Room {room_id}</title>
        <style>
            #messages {{
                border: 1px solid #ccc;
                padding: 10px;
                height: 300px;
                overflow-y: scroll;
                margin-bottom: 10px;
            }}
            #message_input {{
                width: 80%;
                padding: 10px;
            }}
            #send_button {{
                padding: 10px;
            }}
        </style>
    </head>
    <body>
        <h2>Room {room_id}</h2>
        <div id="messages"></div>
        <input type="text" id="message_input" placeholder="Type a message..." />
        <button id="send_button">Send</button>

        <script>
            const roomId = "{room_id}";
            const userId = "{user_id}";

            const ws = new WebSocket(`ws://localhost:8002/ws/${{roomId}}/${{userId}}`);

            ws.onopen = () => {{
                console.log("Connected to the WebSocket");
            }};

            ws.onmessage = (event) => {{
                const message = JSON.parse(event.data);

                // Parse the timestamp from the message and create a Date object
                const timestamp = new Date(message.timestamp);

                // Extract the date and time components
                const year = timestamp.getFullYear();
                const month = String(timestamp.getMonth() + 1).padStart(2, '0'); // Months are zero-indexed
                const day = String(timestamp.getDate()).padStart(2, '0');
                const hours = timestamp.getHours();
                const minutes = String(timestamp.getMinutes()).padStart(2, '0');
                const seconds = String(timestamp.getSeconds()).padStart(2, '0');

                // Determine AM/PM
                const ampm = hours >= 12 ? 'PM' : 'AM';
                const formattedHours = hours % 12 || 12; // Converts 0 to 12 (for 12 AM)

                // Format the timestamp as "YYYY/MM/DD HH:MM:SS AM/PM"
                const formattedTimestamp = `${{year}}/${{month}}/${{day}} ${{formattedHours}}:${{minutes}}:${{seconds}} ${{ampm}}`;

                // Create a message div to display
                const messageDiv = document.createElement("div");
                messageDiv.textContent = `${{formattedTimestamp}} - ${{message.user_id}}: ${{message.message}}`;

                // Append the message to the chat
                document.getElementById("messages").appendChild(messageDiv);
                document.getElementById("messages").scrollTop = document.getElementById("messages").scrollHeight;
            }};

            document.getElementById("send_button").onclick = () => {{
                const messageInput = document.getElementById("message_input");
                const message = messageInput.value;
                if (message.trim() !== "") {{
                    ws.send(JSON.stringify({{ "message": message }}));
                    messageInput.value = "";
                }}
            }};
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{room_id}/{user_id}")
async def signaling_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    logger.info(f"New WebSocket connection - Room: {room_id}, User: {user_id}")
    await manager.connect(room_id, user_id, websocket)

    try:
        while True:
            # Receive messages from the WebSocket
            data = await websocket.receive_text()
            await manager.broadcast(room_id, user_id, data)
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from Room {room_id}")
        await manager.disconnect(room_id, user_id, websocket)
