import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist'
  },
  server: {
    proxy: {
      '/token': 'http://localhost:5000',
      '/api': 'http://localhost:5000'
    }
  }
})
