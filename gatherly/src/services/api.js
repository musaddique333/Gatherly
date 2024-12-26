import axios from "axios";

const AUTH_API = process.env.REACT_APP_AUTH_API;

export const authAPI = axios.create({ baseURL: AUTH_API }); // Named export

authAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
