import { useState,  useRef } from "react";
import { TextField, Button } from "@mui/material";
import Typography from "@mui/material/Typography";
import constants from "./../constant";
import { authAxiosInstance } from '../axiosInstance';
import Swal from 'sweetalert2';

const Register = () => {
  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [userPhone, setUserPhone] = useState("");
  const [userPassword, setUserPassword] = useState("");
  const [emailError, setEmailError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateEmail(userEmail)) {
      setEmailError("Invalid email address");
    } else {
      const registerData = {
        username: userName,
        email: userEmail,
        phone_number: userPhone,
        password: userPassword,
      };

      authAxiosInstance
        .post("/auth/signup", registerData)
        .then((response) => {
          Swal.fire({
            icon: "success",
            title: "Registration Successful",
            text: response.data.message,
          })
        })
        .catch((error) => {
          Swal.fire({
            icon: "error",
            title: "Registration Failed",
            text: error.response.data.message,
          })
          if (error.response && error.response.status === 409) {
            Swal.fire({
              icon: "error",
              title: "Registration Failed",
              text: "Email is already in use!",})
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
      <Typography variant="h4" className="mb-3 font-bold">
        {constants.register.title}
      </Typography>
      <Typography variant="body1" className="mb-6 text-gray-500">
        {constants.register.body}
      </Typography>

      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <div className="mb-4">
          <TextField
            label="User Name"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            fullWidth
            margin="normal"
            variant='filled'
            sx={{
              backgroundColor: 'white',
            }}
          />
        </div>

        <div className="mb-4">
          <TextField
            label="Email"
            value={userEmail}
            onChange={(e) => setUserEmail(e.target.value)}
            fullWidth
            error={emailError !== ""}
            helperText={emailError}
            required
            variant='filled'
            sx={{
              backgroundColor: 'white',
            }}
          />
        </div>

        <div className="mb-4">
          <TextField
            label="Phone number"
            value={userPhone}
            onChange={(e) => setUserPhone(e.target.value)}
            fullWidth
            margin="normal"
            required
            variant='filled'
            sx={{
              backgroundColor: 'white',
            }}
          />
        </div>

        <div className="mb-4">
          <TextField
            label="Password"
            value={userPassword}
            onChange={(e) => setUserPassword(e.target.value)}
            fullWidth
            type="password"
            required
            variant='filled'
            sx={{
              backgroundColor: 'white',
            }}
          />
        </div>

        <button
          type="submit"
          className="bg-blue-500 hover:bg-green-500 text-white font-bold py-2 px-4 rounded mt-4 w-full transition duration-300 ease-in-out"
        >
          {constants.register.btn}
        </button>
      </form>
    </div>
  );
};

export default Register;
