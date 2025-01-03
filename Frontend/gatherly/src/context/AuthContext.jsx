import React, { createContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Swal from 'sweetalert2';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('userId');
    if (storedToken && storedUserId) {
      setToken(storedToken);
      setUserId(storedUserId);
      setIsAuthenticated(true);
    }
    else
    {
      setIsAuthenticated(false);
    }
  }, []);

  const login = (token, userId) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userId', userId);
    localStorage.setItem('isAuthenticated', isAuthenticated);
    setToken(token);
    setUserId(userId);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('isAuthenticated');
    setToken(null);
    setUserId(null);
    setIsAuthenticated(false);
    Swal.fire({
      icon: 'success',
      title: 'Logout Successful',
    })
    
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, token, userId}}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthProvider, AuthContext };

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
