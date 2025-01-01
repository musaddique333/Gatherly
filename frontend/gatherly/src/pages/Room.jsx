import React, { useState, useEffect, useRef, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";

import ChatBox from "../components/chats";
import { AuthContext } from "../context/AuthContext";

const Room = () => {
  const {roomName} = useParams();
// const {userId} = useContext(AuthContext); //DO NOT REMOVE THIS LINE
  const userId = useRef(Math.random().toString(36).substring(2, 8)); //TODO: repalce userId.current with userId
  const [peerConnections, setPeerConnections] = useState({});
  const [localStream, setLocalStream] = useState(null);
  const [audioMuted, setAudioMuted] = useState(false);
  const [videoMuted, setVideoMuted] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  
  const wsRef = useRef(null);
  const existingUsers = useRef(new Set());
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const configuration = {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
  };

  useEffect(() => {
    connectWebSocket();
    return () => cleanup();
  }, []);

  const connectWebSocket = () => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const signalingServer = `${wsProtocol}//${window.location.host}/ws/${roomName}/${userId}`;
    
    wsRef.current = new WebSocket(signalingServer);

    wsRef.current.onopen = () => {
      console.log("Connected to signaling server");
      reconnectAttemptsRef.current = 0;
      startCall();
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket connection closed.");
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
        console.log(`Attempting to reconnect in ${delay/1000} seconds...`);
        setTimeout(connectWebSocket, delay);
        reconnectAttemptsRef.current++;
      } else {
        console.log("Maximum reconnection attempts reached.");
        alert("Connection lost. Please refresh the page to try again.");
      }
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  };

  const cleanup = () => {
    Object.values(peerConnections).forEach(pc => pc.close());
    if (wsRef.current) wsRef.current.close();
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
    }
  };

  const createPeerConnection = async (remoteUserId) => {
    const pc = new RTCPeerConnection(configuration);

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        wsRef.current?.send(JSON.stringify({
          type: "ice-candidate",
          from: userId,
          to: remoteUserId,
          candidate: event.candidate
        }));
      }
    };

    pc.ontrack = (event) => {
      if (!existingUsers.current.has(remoteUserId)) {
        addVideoStream(event.streams[0], `remote-${remoteUserId}`);
        existingUsers.current.add(remoteUserId);
      }
    };

    if (localStream) {
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
    }

    setPeerConnections(prev => ({ ...prev, [remoteUserId]: pc }));
    return pc;
  };

  const startCall = async () => {
    try {
      if (!localStream) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
        setLocalStream(stream);
        const localVideo = document.getElementById("localVideo");
        if (localVideo) localVideo.srcObject = stream;
      }

      wsRef.current.onmessage = async (message) => {
        const data = JSON.parse(message.data);
        const { type, from, offer, answer, candidate, message: chatMessage, messages, timestamp } = data;

        if (from === userId) return;

        switch (type) {
          case "offer":
            if (!peerConnections[from]) {
              const pc = await createPeerConnection(from);
              await pc.setRemoteDescription(new RTCSessionDescription(offer));
              const answer = await pc.createAnswer();
              await pc.setLocalDescription(answer);
              wsRef.current?.send(JSON.stringify({ type: "answer", from: userId, to: from, answer }));
            }
            break;

          case "answer":
            if (peerConnections[from]) {
              await peerConnections[from].setRemoteDescription(new RTCSessionDescription(answer));
            }
            break;

          case "ice-candidate":
            if (peerConnections[from]) {
              await peerConnections[from].addIceCandidate(new RTCIceCandidate(candidate));
            }
            break;

          case "chat-message":
            setChatMessages(prev => [...prev, { from, message: chatMessage, timestamp }]);
            break;

          case "chat-history":
            setChatMessages(messages);
            break;

          case "new-user":
            if (!peerConnections[from]) {
              const pc = await createPeerConnection(from);
              const offer = await pc.createOffer();
              await pc.setLocalDescription(offer);
              wsRef.current?.send(JSON.stringify({ type: "offer", from: userId, to: from, offer }));
            }
            break;

          case "user-disconnected":
            removeVideo(`remote-${from}`);
            if (peerConnections[from]) {
              peerConnections[from].close();
              setPeerConnections(prev => {
                const newConnections = { ...prev };
                delete newConnections[from];
                return newConnections;
              });
            }
            existingUsers.current.delete(from);
            break;
        }
      };

      wsRef.current?.send(JSON.stringify({ type: "new-user", from: userId }));
    } catch (error) {
      console.error("Error in startCall:", error);
    }
  };

  const toggleAudio = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = audioMuted;
      });
      setAudioMuted(!audioMuted);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach(track => {
        track.enabled = videoMuted;
      });
      setVideoMuted(!videoMuted);
    }
  };

  const startScreenSharing = async () => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      const screenTrack = screenStream.getVideoTracks()[0];
      
      Object.values(peerConnections).forEach(pc => {
        const sender = pc.getSenders().find(s => s.track?.kind === "video");
        if (sender) {
          sender.replaceTrack(screenTrack);
        }
      });

      const localVideo = document.getElementById("localVideo");
      if (localVideo) localVideo.srcObject = screenStream;
      
      screenTrack.onended = stopScreenSharing;
      setIsScreenSharing(true);
    } catch (error) {
      console.error("Error sharing screen:", error);
    }
  };

  const stopScreenSharing = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0];
      Object.values(peerConnections).forEach(pc => {
        const sender = pc.getSenders().find(s => s.track?.kind === "video");
        if (sender) {
          sender.replaceTrack(videoTrack);
        }
      });

      const localVideo = document.getElementById("localVideo");
      if (localVideo) localVideo.srcObject = localStream;
      setIsScreenSharing(false);
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (chatInput.trim()) {
      const messageData = {
        type: "chat-message",
        from: userId,
        message: chatInput,
        timestamp: new Date().toLocaleTimeString()
      };
      wsRef.current?.send(JSON.stringify(messageData));
      setChatMessages(prev => [...prev, messageData]);
      setChatInput('');
    }
  };

  const endCall = () => {
    wsRef.current?.send(JSON.stringify({ type: "user-disconnected", from: userId }));
    cleanup();
    window.location.replace("/");
  };

  const addVideoStream = (stream, id) => {
    removeVideo(id);
    const videoElement = document.createElement("video");
    videoElement.id = id;
    videoElement.autoplay = true;
    videoElement.playsInline = true;
    videoElement.srcObject = stream;
    document.getElementById("videos")?.appendChild(videoElement);
  };

  const removeVideo = (id) => {
    const videoElement = document.getElementById(id);
    if (videoElement) {
      videoElement.srcObject = null;
      videoElement.remove();
    }
  };

  return (
    <div className="max-w-3xl mx-auto text-center">
      <h1 className="text-2xl font-bold mb-4">Room: {roomName}</h1>

      <div id="videos" className="flex flex-wrap gap-4 justify-center mb-4">
        <video
          id="localVideo"
          autoPlay
          playsInline
          muted
          className="w-72 h-auto border-2 border-black rounded-md"
        ></video>
      </div>
      
    <ChatBox
      chatMessages={chatMessages}
      chatInput={chatInput}
      setChatInput={setChatInput}
      handleChatSubmit={handleChatSubmit}
    />

      <div className="controls mt-4 flex flex-wrap justify-center gap-2">
        <button
          onClick={toggleAudio}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-700"
        >
          {audioMuted ? "Unmute" : "Mute"}
        </button>
        <button
          onClick={toggleVideo}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-700"
        >
          {videoMuted ? "Turn on" : "Turn off"}
        </button>
        <button
          onClick={isScreenSharing ? stopScreenSharing : startScreenSharing}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-700"
        >
          {isScreenSharing ? "Stop Sharing" : "Share Screen"}
        </button>
        <button
          onClick={endCall}
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-700"
        >
          Leave Room
        </button>
      </div>
    </div>
  );
};

export default Room;
