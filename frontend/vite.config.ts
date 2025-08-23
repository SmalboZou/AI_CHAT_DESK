import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0', // 允许从所有网络接口访问
    port: 5173,
    strictPort: false, // 如果端口被占用，自动尝试下一个端口
    open: false, // 不自动打开浏览器，因为使用Electron
    cors: true, // 允许跨域请求
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
    },
  },
  base: './', // 为Electron设置相对路径
})