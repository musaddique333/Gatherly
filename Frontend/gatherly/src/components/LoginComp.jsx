import { useContext, useState } from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

import constant from '../constant';
import { authAxiosInstance } from '../axiosInstance';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
  const [userEmail, setUserEmail] = useState('');
  const [userPassword, setUserPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validateEmail(userEmail)) {
      setEmailError('Invalid email address');
    } else {
      const loginData = {
        email: userEmail,
        password: userPassword,
      };

      authAxiosInstance.post('/auth/login', loginData)
        .then(response => {
          const token = response.data.access_token;
          const userId = userEmail;
          login(token, userId);
          if (response.status === 200) {
            Swal.fire({
              icon: 'success',
              title: 'Login Successful',
              text: 'Welcome to Gatherly!',
            })
            navigate('/');
          }
        })
        .catch(error => {
          if (error.response) {
            if (error.response.status === 401) {
              Swal.fire({
                icon: 'error',
                title: 'Login Failed',
                text: 'Incorrect email or password',
              })
            } else if (error.response.status === 403) {
              Swal.fire({
                icon: 'error',
                title: 'Login Failed',
                text: 'User account is inactive. Please contact support.',
              })
            } else if (error.response.status === 404) {
              Swal.fire({
                icon: 'error',
                title: 'Login Failed',
                text: 'User not found',
              })
            }
          }
        });
    }
  };

  const validateEmail = (userEmail) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(userEmail);
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <Typography variant="h4" className="mb-3 font-bold">{constant.loginConsts.login}</Typography>

      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <TextField
          label="Email"
          type="email"
          value={userEmail}
          onChange={(e) => setUserEmail(e.target.value)}
          fullWidth
          margin="normal"
          className="mb-3"
          error={emailError !== ''}
          helperText={emailError}
          required
          variant='filled'
          sx={{
            backgroundColor: 'white',
          }}
        />

        <TextField
          label="Password"
          type="password"
          value={userPassword}
          onChange={(e) => setUserPassword(e.target.value)}
          fullWidth
          margin="normal"
          required
          variant='filled'
          sx={{
            backgroundColor: 'white',
          }}
        />

        <button 
          type="submit" 
          className="bg-blue-500 hover:bg-green-500 text-white font-bold py-2 px-4 rounded mt-4 w-full transition duration-300 ease-in-out"
        >
          { constant.loginConsts.login_btn }
        </button>    
      </form>
    </div>
  );
};

export default Login;
