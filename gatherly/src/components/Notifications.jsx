import React, { useState } from "react";
import { IconButton, Menu, MenuItem, Badge } from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";

const Notifications = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const notifications = ["Event reminder", "New message"];

  const openMenu = (e) => setAnchorEl(e.currentTarget);
  const closeMenu = () => setAnchorEl(null);

  return (
    <>
      <IconButton onClick={openMenu}>
        <Badge badgeContent={notifications.length} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={closeMenu}>
        {notifications.map((note, idx) => (
          <MenuItem key={idx}>{note}</MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default Notifications;
