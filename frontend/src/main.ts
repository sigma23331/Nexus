import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { startNetworkSync } from './utils/networkSync'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
startNetworkSync()
