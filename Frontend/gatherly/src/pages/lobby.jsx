import React, { useState } from 'react';
import '../../src/App.css';

const VideoCallHome = () => {
    const [roomName, setRoomName] = useState('');

    const joinRoom = (event) => {
        event.preventDefault();
        const trimmedRoomName = roomName.trim();
        if (trimmedRoomName) {
            window.location.href = `/room/${trimmedRoomName}`;
        } else {
            alert('Please enter a valid room name.');
        }
    };

    //TODO: Verify the room name with DB
    

    return (
        <div className="container">
            <h1 className="title">Welcome to the Video Call App</h1>
            <form className="form" onSubmit={joinRoom}>
                <label htmlFor="room" className="label">Enter Room Name:</label>
                <input
                    type="text"
                    id="room"
                    name="room_name"
                    value={roomName}
                    onChange={(e) => setRoomName(e.target.value)}
                    required
                    className="input"
                />
                <button type="submit" className="button">Join Room</button>
            </form>
        </div>
    );
};

export default VideoCallHome;
