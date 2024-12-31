import React, { useState } from "react";

const ChatBox = ({ chatMessages, chatInput, setChatInput, handleChatSubmit }) => {
  return (
    <div className="h-96 w-full border border-gray-300 rounded-md bg-white flex flex-col">
      <div className="flex items-center justify-between p-2 border-b border-gray-300 bg-gray-100">
        <h2 className="text-lg font-semibold">Live Chat</h2>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {chatMessages.map((msg, index) => (
          <p key={index} className="text-left text-sm">
            <span className="font-bold">[{msg.timestamp}] {msg.from}:</span> {msg.message}
          </p>
        ))}
      </div>
      <div className="p-2 border-t border-gray-300 bg-gray-100">
        <input
          type="text"
          placeholder="Type a message and press Enter"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyDown={handleChatSubmit}
          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
};

export default ChatBox;