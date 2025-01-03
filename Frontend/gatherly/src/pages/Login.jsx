import React, { useContext, useState } from 'react';
import { Switch } from '@mui/material';
import { Box, color } from "@mui/system";
import { styled } from "@mui/system";

import Login from '../components/LoginComp';
import Register from '../components/Registration';

const BetterLogin = () => {
  const [isSignUpMode, setIsSignUpMode] = useState(false);

  const handleToggle = () => {
    setIsSignUpMode(!isSignUpMode);
  };


  const BoxBox = styled(Box)({
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#000000",
    color: "#fff",
    borderRadius: "2vh",
    padding: "2rem",
    position: "fixed",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    zIndex: 10,
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
    opacity: 0.85,
    marginTop: "2.5rem",
    width: "40vw",
    height: "auto",
    maxWidth: "90vw",
    maxHeight: "90vh",
    overflowY: "auto",
    '@media (max-width: 768px)': {
      width: "80vw",
    }
  });

  return (
    <div style={{ position: 'fixed', width: '100%', height: '100vh', overflow: 'hidden' }}>
      <BoxBox>
        <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
          <div className="flex flex-col mt-1">
            <span>{isSignUpMode ? 'Already have an account?' : "Don't have an account?"}</span>
            <div className="ml-1">
              Click Here → <Switch checked={isSignUpMode} onChange={handleToggle} color="primary" />
            </div>
          </div>
        </div>
        {isSignUpMode ? <Register /> : <Login />}
      </BoxBox>
    </div>
  );
};

export default BetterLogin;
