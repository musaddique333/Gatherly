import React from "react";
import { Box, List, ListItem, ListItemIcon, ListItemText } from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import ChatIcon from "@mui/icons-material/Chat";
import VideoCallIcon from "@mui/icons-material/VideoCall";
import NotificationsIcon from "@mui/icons-material/Notifications";

const Sidebar = () => (
  <Box
    sx={{
      width: 240,
      height: "100vh",
      backgroundColor: "#f5f5f5",
      borderRight: "1px solid #ddd",
    }}
  >
    <List>
      <ListItem button>
        <ListItemIcon>
          <HomeIcon />
        </ListItemIcon>
        <ListItemText primary="Home" />
      </ListItem>
      <ListItem button>
        <ListItemIcon>
          <ChatIcon />
        </ListItemIcon>
        <ListItemText primary="Chat Rooms" />
      </ListItem>
      <ListItem button>
        <ListItemIcon>
          <VideoCallIcon />
        </ListItemIcon>
        <ListItemText primary="Video Calls" />
      </ListItem>
      <ListItem button>
        <ListItemIcon>
          <NotificationsIcon />
        </ListItemIcon>
        <ListItemText primary="Notifications" />
      </ListItem>
    </List>
  </Box>
);

export default Sidebar;
