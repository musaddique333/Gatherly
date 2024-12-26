import React from "react";
import { Card, CardContent, Typography, IconButton, Box } from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import VideoCallIcon from "@mui/icons-material/VideoCall";
import "../styles/app.css";

const events = [
  { id: 1, name: "Speed Friending" },
  { id: 2, name: "Weekly Coffee" },
];

const EventsPage = () => (
  <Box sx={{ padding: 2 }}>
    <Typography variant="h4" gutterBottom>Your Events</Typography>
    {events.map((event) => (
      <Card key={event.id} sx={{ marginBottom: 2 }}>
        <CardContent>
          <Typography variant="h5">{event.name}</Typography>
          <Typography variant="body2" color="textSecondary">
            {event.description}
          </Typography>
          <Box sx={{ marginTop: 2 }}>
            <IconButton color="primary">
              <ChatIcon />
            </IconButton>
            <IconButton color="secondary">
              <VideoCallIcon />
            </IconButton>
          </Box>
        </CardContent>
      </Card>
    ))}
  </Box>
);

export default EventsPage;

