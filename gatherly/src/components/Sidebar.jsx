import React, { useState } from "react";
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import HomeIcon from "@mui/icons-material/Home";
import ChatIcon from "@mui/icons-material/Chat";
import VideoCallIcon from "@mui/icons-material/VideoCall";
import NotificationsIcon from "@mui/icons-material/Notifications";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <IconButton onClick={toggleDrawer} sx={{ position: "absolute", top: 10, left: 10, zIndex: 1300 }}>
        <MenuIcon />
      </IconButton>
      <Drawer
        anchor="left"
        open={isOpen}
        onClose={toggleDrawer}
        sx={{ "& .MuiDrawer-paper": { width: 240, backgroundColor: "#f5f5f5" } }}
      >
        <List>
          <ListItem button>
            <ListItemIcon>
              <HomeIcon sx={{ color: "#4caf50" }} />
            </ListItemIcon>
            <ListItemText primary="Home" />
          </ListItem>
          <ListItem button>
            <ListItemIcon>
              <ChatIcon sx={{ color: "#4caf50" }} />
            </ListItemIcon>
            <ListItemText primary="Chat Rooms" />
          </ListItem>
          <ListItem button>
            <ListItemIcon>
              <VideoCallIcon sx={{ color: "#4caf50" }} />
            </ListItemIcon>
            <ListItemText primary="Video Calls" />
          </ListItem>
          <ListItem button>
            <ListItemIcon>
              <NotificationsIcon sx={{ color: "#4caf50" }} />
            </ListItemIcon>
            <ListItemText primary="Notifications" />
          </ListItem>
        </List>
      </Drawer>
    </>
  );
};

export default Sidebar;
