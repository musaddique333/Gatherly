import React from "react";
import { Box, Typography } from "@mui/material";

const HomePage = () => (
  <Box sx={{ padding: 2 }}>
    <Typography variant="h4" gutterBottom>Welcome to Gatherly!</Typography>
    <Typography variant="body1">
      Plan and collaborate effortlessly with events, notifications, and chat features.
    </Typography>
  </Box>
);

export default HomePage;
