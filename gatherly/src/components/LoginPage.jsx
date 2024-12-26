import React, { useState } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";
import { authAPI } from "../services/api"; // Correct import

const LoginPage = () => {
  const [credentials, setCredentials] = useState({ username: "", password: "" });

  const handleLogin = async () => {
    try {
      const response = await authAPI.post("/auth/login", credentials); // Use authAPI
      localStorage.setItem("token", response.data.access_token);
      alert("Login successful!");
    } catch (error) {
      console.error(error); // Log the error for debugging
      alert("Login failed. Please try again.");
    }
  };

  return (
    <Box sx={{ maxWidth: 400, margin: "100px auto", textAlign: "center" }}>
      <Typography variant="h4" gutterBottom>
        Login to Gatherly
      </Typography>
      <TextField
        label="Username"
        fullWidth
        margin="normal"
        onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
      />
      <TextField
        label="Password"
        type="password"
        fullWidth
        margin="normal"
        onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
      />
      <Button variant="contained" color="primary" fullWidth onClick={handleLogin}>
        Login
      </Button>
    </Box>
  );
};

export default LoginPage;
