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
import { useUserStore } from '@/stores/user'
import router from './router'
import './style.css'

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

autoRequestUserLocation().catch(() => {
  // 自动位置请求失败时保持静默，不影响其他功能
})
