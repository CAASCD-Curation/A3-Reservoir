import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
export default defineConfig({ plugins:[vue()], base:'./', build:{rollupOptions:{output:{manualChunks:{vue:['vue'],three:['three']}}}} })
