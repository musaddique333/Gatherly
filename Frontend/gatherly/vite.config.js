import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import dns from 'dns';

dns.setDefaultResultOrder('verbatim');

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Ensure Vite listens on all network interfaces
    port: 8003, // Define the port explicitlye
    strictPort: true,
    watch: {
      usePolling: true,
    }
  },
});