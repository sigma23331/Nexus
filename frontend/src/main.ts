import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@/pwa/register'
import { startNetworkSync } from './utils/networkSync'
import { autoRequestUserLocation } from '@/utils/locationAutoUpdate'
import App from './App.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import GlobalOverlay from '@/components/common/GlobalOverlay.vue'
import { useRouteProgress } from '@/composables/useRouteProgress'
import { useToast } from '@/composables/useToast'
import { startSessionGuard } from '@/utils/sessionGuard'
import { registerLocalIcons } from '@/utils/localIcons'
import { useUserStore } from '@/stores/user'
import router from './router'
import './style.css'

// 本地注册 TabBar 图标，首屏不再等待 iconify 在线 API（且离线可用）
registerLocalIcons()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')

// 全局 Toast 容器独立挂载，与业务页面解耦：任意位置 useToast() 即可调用
const toastHost = document.createElement('div')
document.body.appendChild(toastHost)
createApp(ToastContainer).mount(toastHost)

// 全局浮层（路由进度条 + 网络状态条），同样独立挂载、与页面解耦
const overlayHost = document.createElement('div')
document.body.appendChild(overlayHost)
createApp(GlobalOverlay).mount(overlayHost)

// 路由切换驱动顶部进度条（懒加载分块时给予加载反馈）
const routeProgress = useRouteProgress()
router.beforeEach(() => {
  routeProgress.start()
})
router.afterEach(() => {
  routeProgress.done()
})
router.onError(() => {
  routeProgress.done()
})

// 会话守卫：登录满固定时长（< 后端 token 有效期）自动退出并回到登录页
startSessionGuard(() => {
  const userStore = useUserStore()
  userStore.logout()
  const current = router.currentRoute.value
  if (current.name !== 'login' && current.name !== 'register') {
    useToast().warning('登录已过期，请重新登录')
    router.replace({ name: 'login', query: { redirect: current.fullPath } })
  }
})

startNetworkSync()

// 首屏渲染完成后，空闲时静默预取其他 Tab 页的 JS chunk，使 Tab 切换瞬时完成。
// 模块标识与路由懒加载一致，Vite 会复用同一 chunk，不会重复打包。
const prefetchTabViews = () => {
  void import('@/views/answer/AnswerView.vue')
  void import('@/views/plaza/PlazaView.vue')
  void import('@/views/profile/ProfileView.vue')
}
if ('requestIdleCallback' in window) {
  requestIdleCallback(prefetchTabViews, { timeout: 5000 })
} else {
  setTimeout(prefetchTabViews, 3000)
}

autoRequestUserLocation().catch(() => {
  // 自动位置请求失败时保持静默，不影响其他功能
})
