import React, { useContext } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import VideoCallHome from './pages/lobby'
import Room from './pages/Room';
import Navbar from './components/Navbar';
import BetterLogin from './pages/Login';
import MainContent from './components/maincontent';
import Home from './pages/Home';

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
          </Routes>
        </div>
      </Router>
  )
}

export default App
