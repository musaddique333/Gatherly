import React from "react";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "./theme";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import MainLayout from "./components/MainLayout";

const App = () => (
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <Navbar />
    <div style={{ display: "flex" }}>
      <Sidebar />
      <MainLayout />
    </div>
  </ThemeProvider>
);

export default App;
