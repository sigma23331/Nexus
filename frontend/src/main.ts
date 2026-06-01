import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@/pwa/register'
import { startNetworkSync } from './utils/networkSync'
import App from './App.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
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

startNetworkSync()
