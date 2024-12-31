import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import dns from 'dns';

dns.setDefaultResultOrder('verbatim');

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/registration': {
        target: 'http://registration-microservice:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/registration/, ''),
        secure: false,
      },
      '/api/event': {
        target: 'http://event-microservice:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/registration\/node/, ''),
        secure: false,
      },
    },
  },
});