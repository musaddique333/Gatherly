import React, { useState, useEffect, useRef } from "react";
import "../Room.css";
import { useParams } from "react-router-dom";

const Room = () => {
  const [localStream, setLocalStream] = useState(null);
  const [peerConnections, setPeerConnections] = useState({});
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [audioMuted, setAudioMuted] = useState(false);
  const [videoMuted, setVideoMuted] = useState(false);
  const [shareScreen, setShareScreen] = useState(false);

  const localVideoRef = useRef(null);
  const wsRef = useRef(null);
  const screenStreamRef = useRef(null);
  const {roomName} = useParams(); //TODO: Replace with eventid from DB 
  const userId = useRef(Math.random().toString(36).substring(2, 8)); //TODO: repalce with username
  const signalingServer = `ws://localhost:8000/ws/${roomName}/${userId.current}`;
  const existingUsers = useRef(new Set());

  const iceServers = {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
  };

  useEffect(() => {
    const ws = new WebSocket(signalingServer);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to signaling server");
      startCall();
    };

    ws.onmessage = handleWebSocketMessage;

    ws.onclose = () => {
      console.log("WebSocket connection closed. Attempting to reconnect...");
      setTimeout(() => connectWebSocket(), 3000);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      // Clean up resources on component unmount
      Object.values(peerConnections).forEach((pc) => pc.close());
      ws.close();
      if (localStream) {
        localStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  const startCall = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true
      });
      setLocalStream(stream);
      localVideoRef.current.srcObject = stream;
      wsRef.current.send(JSON.stringify({ type: "new-user", from: userId.current }));
    } catch (error) {
      console.error("Error in startCall:", error);
    }
  };

  const handleWebSocketMessage = async (event) => {
    const data = JSON.parse(event.data);
    const { type, from, to, offer, answer, candidate, message, timestamp, messages } = data;

    if (from === userId.current) return;

    switch (type) {
      case "offer":
        await handleOffer(from, offer);
        break;
      case "answer":
        await handleAnswer(from, answer);
        break;
      case "ice-candidate":
        await handleIceCandidate(from, candidate);
        break;
      case "chat-message":
        setChatMessages((prev) => [...prev, { from, message, timestamp }]);
        break;
      case "chat-history":
        setChatMessages(messages);
        break;
      case "user-disconnected":
        removePeerConnection(from);
        break;
      default:
        break;
    }
  };

  const handleOffer = async (from, offer) => {
    const pc = await createPeerConnection(from);
    await pc.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    wsRef.current.send(JSON.stringify({ type: "answer", from: userId.current, to: from, answer }));
  };

  const handleAnswer = async (from, answer) => {
    const pc = peerConnections[from];
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(answer));
    }
  };

  const handleIceCandidate = async (from, candidate) => {
    const pc = peerConnections[from];
    if (pc) {
      await pc.addIceCandidate(new RTCIceCandidate(candidate));
    }
  };

  const createPeerConnection = async (remoteUserId) => {
    const pc = new RTCPeerConnection(iceServers);
    setPeerConnections((prev) => ({ ...prev, [remoteUserId]: pc }));

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        wsRef.current.send(
          JSON.stringify({
            type: "ice-candidate",
            from: userId.current,
            to: remoteUserId,
            candidate: event.candidate
          })
        );
      }
    };

    pc.ontrack = (event) => {
      if (!existingUsers.current.has(remoteUserId)) {
        addRemoteVideo(event.streams[0], remoteUserId);
        existingUsers.current.add(remoteUserId);
      }
    };

    localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

    return pc;
  };

  const addRemoteVideo = (stream, id) => {
    const videoElement = document.createElement("video");
    videoElement.id = `remote-${id}`;
    videoElement.srcObject = stream;
    videoElement.autoplay = true;
    videoElement.playsInline = true;
    document.getElementById("videos").appendChild(videoElement);
  };

  const removePeerConnection = (id) => {
    if (peerConnections[id]) {
      peerConnections[id].close();
      delete peerConnections[id];
    }
    const videoElement = document.getElementById(`remote-${id}`);
    if (videoElement) videoElement.remove();
    existingUsers.current.delete(id);
  };

  const toggleAudioMute = () => {
    localStream.getAudioTracks().forEach((track) => (track.enabled = audioMuted));
    setAudioMuted((prev) => !prev);
  };

  const toggleVideoMute = () => {
    localStream.getVideoTracks().forEach((track) => (track.enabled = videoMuted));
    setVideoMuted((prev) => !prev);
  };

  const handleChatSubmit = (e) => {
    if (e.key === "Enter" && chatInput.trim()) {
      const messageData = {
        type: "chat-message",
        from: userId.current,
        message: chatInput.trim(),
        timestamp: new Date().toLocaleTimeString()
      };
      setChatMessages((prev) => [...prev, messageData]);
      wsRef.current.send(JSON.stringify(messageData));
      setChatInput("");
    }
  };

  return (
    <div className="room">
      <h1>Room: {roomName}</h1>
      <div id="videos">
        <video ref={localVideoRef} id="localVideo" autoPlay playsInline muted></video>
      </div>
      <input
        type="text"
        placeholder="Type a message and press Enter"
        value={chatInput}
        onChange={(e) => setChatInput(e.target.value)}
        onKeyDown={handleChatSubmit}
      />
      <div id="chatBox">
        {chatMessages.map((msg, index) => (
          <p key={index}>
            [{msg.timestamp}] {msg.from}: {msg.message}
          </p>
        ))}
      </div>
      <div className="controls">
        <button onClick={toggleAudioMute}>{audioMuted ? "Unmute" : "Mute"}</button>
        <button onClick={toggleVideoMute}>{videoMuted ? "Turn on" : "Turn off"}</button>
      </div>
    </div>
  );
};

export default Room;
