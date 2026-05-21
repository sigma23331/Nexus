import { ref } from 'vue'
import { registerSW } from 'virtual:pwa-register'

/** 有新版本可用，等待用户确认刷新 */
export const pwaNeedRefresh = ref(false)
/** 静态资源已缓存，可离线打开壳页面 */
export const pwaOfflineReady = ref(false)

export const updateServiceWorker = registerSW({
  immediate: true,
  onOfflineReady() {
    pwaOfflineReady.value = true
    console.log('[PWA] 应用已可离线使用')
  },
  onNeedRefresh() {
    pwaNeedRefresh.value = true
    console.log('[PWA] 发现新版本')
  },
  onRegisteredSW(_swUrl, registration) {
    if (registration) {
      setInterval(() => registration.update(), 60 * 60 * 1000)
    }
  },
  onRegisterError(error) {
    console.error('[PWA] Service Worker 注册失败:', error)
  },
})

export function applyPwaUpdate() {
  updateServiceWorker(true)
}
