import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { 
  Mic, MicOff, Video, VideoOff, Share, Phone, 
  MessageSquare, Users 
} from "lucide-react";

import ChatBox from "../components/chats";

const Room = () => {
  const { roomName } = useParams();
  const userId = localStorage.getItem("userId");

  const [peerConnections, setPeerConnections] = useState({});
  const [localStream, setLocalStream] = useState(null);
  const [audioMuted, setAudioMuted] = useState(false);
  const [videoMuted, setVideoMuted] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [showChat, setShowChat] = useState(false);
  const [participantCount, setParticipantCount] = useState(1);

  const wsRef = useRef(null);
  const existingUsers = useRef(new Set());
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const localStreamRef = useRef(null);

  const configuration = {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
  };

  useEffect(() => {
    connectWebSocket();
    return () => cleanup();
  }, []);

  const connectWebSocket = () => {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const signalingServer = `${wsProtocol}//localhost:8002/ws/${roomName}/${userId}`;

    wsRef.current = new WebSocket(signalingServer);

    wsRef.current.onopen = () => {
      reconnectAttemptsRef.current = 0;
      startCall();
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket connection closed.");
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.min(
          1000 * Math.pow(2, reconnectAttemptsRef.current),
          30000
        );
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
    Object.values(peerConnections).forEach((pc) => pc.close());
    if (wsRef.current) wsRef.current.close();
    if (localStream) {
      localStream.getTracks().forEach((track) => track.stop());
    }
  };

  const initializeLocalStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: true,
      });
      localStreamRef.current = stream;  // Set the ref immediately
      setLocalStream(stream);  // Also update the state for reactivity
      
      const localVideo = document.getElementById("localVideo");
      if (localVideo) {
        localVideo.srcObject = stream;
      }
      return stream;
    } catch (error) {
      console.error("Error getting local stream:", error);
      return null;
    }
  };

  const startCall = async () => {
    try {
      if (!localStreamRef.current) {
        const stream = await initializeLocalStream();
        if (!stream) {
            console.error("Failed to initialize local stream.");
            return;
        }
      }

      wsRef.current.onmessage = async (message) => {
        // const data = JSON.parse(message.data);

        let data;

        try{
          data = JSON.parse(message.data);
        }
        catch{
          console.log(message.data);
          return;
        }

        // const {
        //   type,
        //   from,
        //   to,
        //   offer,
        //   answer,
        //   candidate,
        //   message: chatMessage,
        //   messages,
        //   timestamp,
        // } = data;

        switch (data.type) {
          case "offer":
            if (!peerConnections[data.user_id]) {
              const pc = await createPeerConnection(data.user_id);
              await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
              const answer = await pc.createAnswer();
              await pc.setLocalDescription(answer);
              wsRef.current?.send(
                JSON.stringify({ type: "answer", from: userId, to: data.user_id, answer })
              );
            }
            break;

            case "answer":
              if (peerConnections[data.user_id]) {
                await peerConnections[data.user_id].setRemoteDescription(
                  new RTCSessionDescription(data.answer)
                );
              }
              break;

          case "ice-candidate":
            if (peerConnections[data.user_id]) {
              await peerConnections[data.user_id].addIceCandidate(
                new RTCIceCandidate(candidate)
              );
            }
            break;

          case "chat-history":
            // Here we are handling the "chat-history" message
            const modifiedData = {
              ...data,
              from: data.user_id,
            };
          
            delete modifiedData.user_id;
          
            setChatMessages((event) => [...event, modifiedData]);
            break;

          case "new-user":
            if (!peerConnections[data.user_id]) {
              const pc = await createPeerConnection(data.user_id);
              const offer = await pc.createOffer();

              await pc.setLocalDescription(offer);
              wsRef.current?.send(
                JSON.stringify({
                  type: "offer",
                  from: userId,
                  to: data.user_id,
                  offer,
                })
              );
            }
            break;

          case "user-disconnected":
            removeVideo(`remote-${from}`);
            if (peerConnections[from]) {
              peerConnections[from].close();
              setPeerConnections((prev) => {
                const newConnections = { ...prev };
                delete newConnections[from];
                return newConnections;
              });
            }
            existingUsers.current.delete(from);
            break;
          default:
              console.log("Unhandled message type:", data.type);
        }
      };

      wsRef.current?.send(
        JSON.stringify({ type: "new-user", from: userId, message: "user connected" })
      );
    } catch (error) {
      console.error("Error in startCall:", error);
    }
  };


  const createPeerConnection = async (remoteUserId) => {
    if (!localStreamRef.current) {
      console.error("Local stream not available yet");
      return null;
    }
    const pc = new RTCPeerConnection(configuration);
    peerConnections[remoteUserId] = pc;

    pc.addTransceiver('audio', { direction: 'sendrecv' });
pc.addTransceiver('video', { direction: 'sendrecv' });

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        wsRef.current?.send(
          JSON.stringify({
            type: "ice-candidate",
            from: userId,
            to: remoteUserId,
            candidate: event.candidate,
          })
        );
      }
    };

    pc.oniceconnectionstatechange = () => {
      console.log('ICE Connection State:', pc.iceConnectionState);
  };

    pc.ontrack = (event) => {
      addVideoStream(event.streams[0], `remote-${remoteUserId}`);
      existingUsers.current.add(remoteUserId);
    };

    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) =>
        pc.addTrack(track, localStreamRef.current)
      );
    }
    setPeerConnections((prev) => ({ ...prev, [remoteUserId]: pc }));
    return pc;
  };

  const toggleAudio = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach((track) => {
        track.enabled = audioMuted;
      });
      setAudioMuted(!audioMuted);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach((track) => {
        track.enabled = videoMuted;
      });
      setVideoMuted(!videoMuted);
    }
  };

  const handleChatSubmit = (e) => {
    if (e.key === "Enter" && chatInput.trim()) {
      const messageData = {
        type: "message",
        from: userId,
        message: chatInput.trim(),
        timestamp: new Date().toLocaleTimeString(),
      };

      setChatMessages((prev) => [...prev, messageData]);

      setChatInput("");
      wsRef.current.send(JSON.stringify(messageData));
    }
  };

  const endCall = () => {
    wsRef.current?.send(
      JSON.stringify({ type: "user-disconnected", from: userId })
    );
    cleanup();
    window.location.href = "/";
  };

  // const addVideoStream = (stream, id) => {
  //   removeVideo(id);
  //   console.log("Id is /////", id);
  //   const videoElement = document.createElement("video");
  //   videoElement.id = id;
  //   videoElement.autoPlay = true;
  //   videoElement.playsInline = true;
  //   videoElement.srcObject = stream;
  //   videoElement.className = "w-full h-full object-cover";

  //   const videoContainer = document.createElement("div");
  //   videoContainer.className =
  //     "relative aspect-video bg-gray-800 rounded-lg overflow-hidden";
  //   videoContainer.appendChild(videoElement);

  //   const labelContainer = document.createElement("div");
  //   labelContainer.className =
  //     "absolute bottom-4 left-4 bg-black bg-opacity-50 px-2 py-1 rounded-md text-white";
  //   labelContainer.textContent = id === "localVideo" ? "You" : "Participant";
  //   videoContainer.appendChild(labelContainer);

  //   document.getElementById("videos")?.appendChild(videoContainer);
  //   setParticipantCount((prev) => prev + 1);
  // };

  function addVideoStream(stream, id) {
    removeVideo(id); // Remove any existing video element with the same ID
    const videoElement = document.createElement("video");
    videoElement.id = id;
    videoElement.autoplay = true;
    videoElement.playsinline = true;
    videoElement.srcObject = stream;
    document.getElementById("videos").appendChild(videoElement);
    setParticipantCount((prev) => prev + 1);
  }

  const removeVideo = (id) => {
    const videoElement = document.getElementById(id);
    if (videoElement) {
      videoElement.srcObject = null;
      videoElement.remove();
    }
  };

  return (
    <div className="h-screen bg-gray-900 text-white relative overflow-hidden">
      <div className="h-full flex">
        <div className="flex-1 p-4">
          <div
            id="videos"
            className="grid gap-4 h-full grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
          >
            <div className="relative aspect-video bg-gray-800 rounded-lg overflow-hidden">
              <video
                id="localVideo"
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 px-2 py-1 rounded-md">
                You {audioMuted && <MicOff className="inline w-4 h-4 ml-2" />}
              </div>
            </div>
          </div>
        </div>
        {showChat && (
          <div className="w-80 bg-gray-800 border-l border-gray-700">
            <div className="h-full flex flex-col">
              <div className="p-4 border-b border-gray-700">
                <h2 className="text-lg font-semibold">Chat</h2>
              </div>
              <ChatBox
                chatMessages={chatMessages}
                chatInput={chatInput}
                setChatInput={setChatInput}
                handleChatSubmit={handleChatSubmit}
              />
            </div>
          </div>
        )}
      </div>
      <div className="absolute top-4 left-4 bg-gray-800 bg-opacity-90 rounded-lg px-4 py-2">
        {userId}
      </div>
      <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 rounded-lg px-4 py-2 flex items-center gap-2">
        <Users className="w-5 h-5" />
        {participantCount}
      </div>
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 transition-opacity duration-300 opacity-100">
        <div className="bg-gray-800 rounded-full px-6 py-3 flex items-center gap-6">
          <button
            onClick={toggleAudio}
            className={`p-3 rounded-full hover:bg-gray-700 ${
              audioMuted ? "bg-red-500 hover:bg-red-600" : ""
            }`}
            title={audioMuted ? "Unmute" : "Mute"}
          >
            {audioMuted ? <MicOff /> : <Mic />}
          </button>
          <button
            onClick={toggleVideo}
            className={`p-3 rounded-full hover:bg-gray-700 ${
              videoMuted ? "bg-red-500 hover:bg-red-600" : ""
            }`}
            title={videoMuted ? "Turn on camera" : "Turn off camera"}
          >
            {videoMuted ? <VideoOff /> : <Video />}
          </button>
          {/* <button
            onClick={isScreenSharing ? stopScreenSharing : startScreenSharing}
            className={`p-3 rounded-full hover:bg-gray-700 ${
              isScreenSharing ? "bg-blue-500 hover:bg-blue-600" : ""
            }`}
            title={isScreenSharing ? "Stop sharing" : "Share screen"}
          >
            <Share />
          </button> */}
          <button
            onClick={() => setShowChat(!showChat)}
            className={`p-3 rounded-full hover:bg-gray-700 ${
              showChat ? "bg-blue-500 hover:bg-blue-600" : ""
            }`}
            title="Toggle chat"
          >
            <MessageSquare />
          </button>
          <button
            onClick={endCall}
            className="p-3 rounded-full bg-red-500 hover:bg-red-600"
            title="Leave call"
          >
            <Phone className="transform rotate-135" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Room;
