import React, { useContext } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';
import MainContent from './components/maincontent';
import ProtectedRoute from './components/ProtectedRoute';

import Home from './pages/Home';
import VideoCallHome from './pages/lobby'
import Room from './pages/Room';
import BetterLogin from './pages/Login';
import EventForm from './pages/CreateEvent';

import { AuthProvider, AuthContext } from './context/AuthContext';


function App() {

  //TODO: Get username and room name from DB (setup context)
  //TODO: Create context for roomname
  //TODO: Create authcontext

  return (
      <Router>
        <Navbar/>
        <div>
          <MainContent/>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<BetterLogin />} />
            <Route path="/video" element={<VideoCallHome />} />
            <Route path="/room/:roomName" element={<Room />} />
            <Route path="/user/create-event" element={<EventForm/>} />
            
          </Routes>
        </div>
      </Router>
  )
}

export default App
