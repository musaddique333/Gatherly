import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import PropTypes from 'prop-types';

const ProtectedRoute = ({ element }) => {
  const { isAuthenticated } = useContext(AuthContext);

  return isAuthenticated ? element : <Navigate to="/login" />;
};

export default ProtectedRoute;

ProtectedRoute.propTypes = {
  element:PropTypes.element.isRequired
};