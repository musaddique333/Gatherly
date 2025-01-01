import axios from 'axios';

const authAxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/',
  headers: {
    'Accept': '*/*',
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  }
});

const eventAxiosInstance = axios.create({
    baseURL: 'http://localhost:8001/',
    headers: {
      'Accept': '*/*',
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    }
  });

  const videoAxiosInstance = axios.create({
    baseURL: 'http://localhost:8002/',
    headers: {
      'Accept': '*/*',
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    }
  });

export{authAxiosInstance, eventAxiosInstance, videoAxiosInstance};
