import React, { useState } from "react";
import { Box, TextField, Button, List, ListItem } from "@mui/material";

const ChatSection = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (input) {
      setMessages([...messages, input]);
      setInput("");
    }
  };

  return (
    <Box>
      <List>
        {messages.map((msg, idx) => (
          <ListItem key={idx}>{msg}</ListItem>
        ))}
      </List>
      <TextField
        placeholder="Type a message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        fullWidth
      />
      <Button onClick={sendMessage}>Send</Button>
    </Box>
  );
};

export default ChatSection;
