import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../shared')
    },
    dedupe: ['react', 'react-dom', 'react-router-dom'],
    modules: [path.resolve(__dirname, 'node_modules'), 'node_modules']
  },
  optimizeDeps: {
    include: ['react-icons/fa', 'react-icons/md', 'react-icons/bi', 'react-icons/fi']
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
