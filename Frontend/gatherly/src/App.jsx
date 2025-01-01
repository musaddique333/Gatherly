import React from 'react'
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
  return(
  <AuthProvider>
          <Router>
            <Navbar/>
            <div>
              <MainContent/>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<BetterLogin />} />
                {/*<Route path="/video" element={<VideoCallHome />} />*/} {/* needs to be protected*/}
                {/*<Route path="/room/:roomName" element={<Room />} />*/} {/* needs to be protected*/}
                {/*<Route path="/user/create-event" element={<EventForm/>} />*/} {/* needs to be protected*/} 
                <Route path='/video' element={<ProtectedRoute element={<VideoCallHome />} />} />
                <Route path='/room/:roomName' element={<ProtectedRoute element={<Room />} />} />
                <Route path='/create-event' element={<ProtectedRoute element={<EventForm />} />} />
              </Routes>
            </div>
          </Router>
   </AuthProvider>
   ); 
}

export default App
