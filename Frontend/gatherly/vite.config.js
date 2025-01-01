import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import dns from 'dns';

dns.setDefaultResultOrder('verbatim');

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Ensure Vite listens on all network interfaces
    port: 5173, // Define the port explicitly
    strictPort: true, // Exit if the port is already in use
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
        rewrite: (path) => path.replace(/^\/api\/event/, ''),
        secure: false,
      },
      '/api/video': {
        target: 'http://video-microservice:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/video/, ''),
        secure: false,
      },
    },
  },
});
