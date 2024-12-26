import React from "react";
import { Grid, Box, Typography, Button } from "@mui/material";

const MainLayout = () => (
  <Grid container>
    <Grid item xs={8} sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        Chat Room
      </Typography>
      <Box
        sx={{
          height: 300,
          border: "1px solid #ddd",
          borderRadius: 1,
          padding: 2,
          backgroundColor: "#f9f9f9",
        }}
      >
        <Typography variant="body1">Chat messages will appear here.</Typography>
      </Box>
      <Box sx={{ marginTop: 2 }}>
        <Button variant="contained" color="primary">
          Send Message
        </Button>
      </Box>
    </Grid>
    <Grid item xs={4} sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        Live Videos
      </Typography>
      <Box
        sx={{
          height: 300,
          border: "1px solid #ddd",
          borderRadius: 1,
          padding: 2,
          backgroundColor: "#f9f9f9",
        }}
      >
        <Typography variant="body1">Video content will appear here.</Typography>
      </Box>
    </Grid>
  </Grid>
);

export default MainLayout;
