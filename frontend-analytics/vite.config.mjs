import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const devApiTarget = process.env.VITE_DEV_API_TARGET || 'http://127.0.0.1:5060'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setupTests.js',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: devApiTarget,
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          const normalizedId = id.split('\\').join('/')
          if (!normalizedId.includes('node_modules/')) {
            return undefined
          }

          const nodeModulesPath = normalizedId.split('node_modules/')[1]
          if (!nodeModulesPath) {
            return 'vendor'
          }

          const packageName = nodeModulesPath.startsWith('@')
            ? nodeModulesPath.split('/').slice(0, 2).join('/')
            : nodeModulesPath.split('/')[0]

          if (!packageName) {
            return 'vendor'
          }

          return `pkg-${packageName.replace('@', '').replace('/', '-')}`
        },
      },
    },
  },
})