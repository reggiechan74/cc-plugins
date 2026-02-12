import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'framer-motion': ['framer-motion'],
          'radix': ['radix-ui'],
          'markdown': ['react-markdown', 'remark-gfm'],
        },
      },
    },
  },
  // For GitHub Pages: set base to '/<REPO_NAME>/'
  // For custom domain or local: set base to '/'
  base: '/',
})
