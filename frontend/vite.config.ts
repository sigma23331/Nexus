import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { fileURLToPath } from 'url'
import { VitePWA } from 'vite-plugin-pwa'
// 1. 引入图片压缩插件
import ViteImagemin from 'vite-plugin-imagemin'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [
    vue(),

    // 2. 在 PWA 插件之前加入图片自动压缩配置
    ViteImagemin({
      gifsicle: { optimizationLevel: 7, interlaced: false },
      optipng: { optimizationLevel: 7 },
      pngquant: {
        quality: [0.7, 0.8], // 自动将 PNG 压缩至 70%~80% 质量，大幅减小体积
        speed: 4,
      },
      mozjpeg: { quality: 75 },
      svgo: {
        plugins: [{ name: 'removeViewBox' }, { name: 'removeEmptyAttrs', active: false }],
      },
    }),

    // 3. PWA 插件保持在你原本的配置不变
    VitePWA({
      // 使用 prompt 模式：新版本就绪后由 PwaUpdateBanner 提示用户主动刷新，
      // 避免 autoUpdate 在用户操作（登录/写日记）过程中被动刷新导致数据丢失
      registerType: 'prompt',
      includeAssets: ['favicon.ico', 'offline.html', 'icons/*.png'],
      manifest: false, // 使用 public/manifest.json
      workbox: {
        // 仅预缓存应用壳与小体积资源；图片改为运行时按需缓存，避免预缓存体积过大
        globPatterns: ['**/*.{js,css,html,ico,svg,woff2}'],
        maximumFileSizeToCacheInBytes: 3145728,
        // Vue SPA：离线时回退到已预缓存的 index.html
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api/, /^\/v1/],
        runtimeCaching: [
          {
            // 图片：CacheFirst 按需缓存，避免把大图全部塞进预缓存撑大安装体积
            urlPattern: ({ request, url }) =>
              request.destination === 'image' ||
              /\.(?:png|jpe?g|gif|webp|svg)$/i.test(url.pathname),
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: {
                maxEntries: 80,
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            // 广场 / 日记：实时性高，优先网络、弱网回退缓存，缓存时效短（30 分钟）
            urlPattern: ({ url }) => /^\/(?:api\/)?v1\/(?:plaza|diary)\//.test(url.pathname),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-realtime-cache',
              networkTimeoutSeconds: 8,
              expiration: {
                maxEntries: 60,
                maxAgeSeconds: 60 * 30,
              },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            // 运势 / 答案：每日内容，优先网络、离线可读当天结果，缓存时效长（7 天）
            urlPattern: ({ url }) => /^\/(?:api\/)?v1\/(?:fortune|answer)\//.test(url.pathname),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-daily-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 7,
              },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            // 其余 API 兜底：生产同源 /api，开发走 Vite 代理
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api') || url.pathname.startsWith('/v1'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24,
              },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
      devOptions: {
        enabled: false, // 本地调试 PWA 时可改为 true
        type: 'module',
      },
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, ''),
      },
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/v1': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/v1/, ''),
      },
    },
  },
})
