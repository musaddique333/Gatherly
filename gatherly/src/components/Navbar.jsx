import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Button,
  TextField,
  Box,
  Dialog,
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";

const Navbar = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [openLogin, setOpenLogin] = useState(false);
  const notifications = ["New message from John", "Weekly Review starts soon"];

  const handleBellClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLoginOpen = () => {
    setOpenLogin(true);
  };

  const handleLoginClose = () => {
    setOpenLogin(false);
  };

  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Gatherly
        </Typography>
        <IconButton color="inherit" onClick={handleBellClick}>
          <Badge badgeContent={notifications.length} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleClose}
          MenuListProps={{
            "aria-labelledby": "basic-button",
          }}
        >
          {notifications.map((notification, index) => (
            <MenuItem key={index} onClick={handleClose}>
              {notification}
            </MenuItem>
          ))}
        </Menu>
        <IconButton color="inherit" onClick={handleLoginOpen}>
          <AccountCircleIcon />
        </IconButton>
        <Dialog open={openLogin} onClose={handleLoginClose}>
          <Box sx={{ padding: 2 }}>
            <Typography variant="h6" gutterBottom>
              Login
            </Typography>
            <TextField
              label="Username"
              fullWidth
              margin="normal"
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              margin="normal"
            />
            <Button
              variant="contained"
              color="primary"
              fullWidth
              sx={{ marginTop: 2 }}
              onClick={handleLoginClose}
            >
              Login
            </Button>
          </Box>
        </Dialog>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
