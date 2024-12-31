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
import UserDashboard from './pages/UserDash';

import { AuthProvider, AuthContext } from './context/AuthContext';


function App() {
  return (
      <Router>
        <Navbar/>
        <div>
          <MainContent/>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<BetterLogin />} />
            <Route path="/video" element={<VideoCallHome />} /> {/* needs to be protected*/}
            <Route path="/room/:roomName" element={<Room />} /> {/* needs to be protected*/}
            <Route path="/user/create-event" element={<EventForm/>} /> {/* needs to be protected*/}
            <Route path="/user" element={<UserDashboard />} /> {/* needs to be protected*/}
            
          </Routes>
        </div>
      </Router>
  )
}

export default App
