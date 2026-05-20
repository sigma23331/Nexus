<template>
  <!-- 自动安装模式（支持 beforeinstallprompt），已安装后不再显示 -->
  <div v-if="!isInstalled && autoSupported && autoVisible" class="install-banner auto">
    <div class="install-banner-content">
      <span class="icon">📱</span>
      <div class="text">
        <strong>安装心运岛到桌面</strong>
        <span>一触即达，更快捷体验</span>
      </div>
      <div class="actions">
        <button @click="installApp" class="install-btn">立即安装</button>
        <button @click="dismissAuto" class="dismiss-btn">以后再说</button>
      </div>
    </div>
  </div>

  <!-- 手动引导模式（iOS 等不支持 beforeinstallprompt 的环境），已安装后不再显示 -->
  <div v-if="!isInstalled && !autoSupported && manualVisible" class="install-banner manual">
    <div class="manual-content">
      <div class="manual-header">
        <span class="icon">📲</span>
        <span>添加到主屏幕</span>
        <button @click="dismissManual" class="close-btn">✕</button>
      </div>
      <div class="manual-steps">
        <div class="step">
          <span class="step-icon">1️⃣</span>
          <span>点击底部<span class="em">分享</span>按钮</span>
        </div>
        <div class="step">
          <span class="step-icon">2️⃣</span>
          <span>滑动找到<span class="em">添加到主屏幕</span></span>
        </div>
        <div class="step-img">
          <img src="/images/guide.png" alt="添加到主屏幕步骤" class="guide-img" />
        </div>
      </div>
      <p class="manual-note">将心运岛添加到主屏幕，使用更便捷~</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide } from 'vue'

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

// 是否已经安装过 PWA（永久标记）
const isInstalled = ref(localStorage.getItem('pwa_installed') === 'true')

const autoSupported = ref(false)
const autoVisible = ref(false)
let deferredPrompt: BeforeInstallPromptEvent | null = null
let timer: ReturnType<typeof setInterval> | null = null
let elapsedSeconds = 0
let isPageVisible = true

const manualVisible = ref(false)

// 以下函数必须在顶层定义，以便模板可以访问
const isAutoDismissedRecently = () => {
  const dismissedTime = localStorage.getItem('pwa_auto_dismissed')
  if (!dismissedTime) return false
  const now = Date.now()
  const sevenDays = 7 * 24 * 60 * 60 * 1000
  return now - parseInt(dismissedTime) < sevenDays
}

const stopTimer = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const dismissAuto = () => {
  localStorage.setItem('pwa_auto_dismissed', Date.now().toString())
  autoVisible.value = false
  stopTimer()
}

const showAutoBanner = () => {
  if (!deferredPrompt) return
  if (isAutoDismissedRecently()) return
  autoVisible.value = true
  stopTimer()
}

const installApp = async () => {
  if (!deferredPrompt) return
  deferredPrompt.prompt()
  const { outcome } = await deferredPrompt.userChoice
  if (outcome === 'accepted') {
    localStorage.setItem('pwa_installed', 'true')
    isInstalled.value = true
    autoVisible.value = false
    localStorage.removeItem('pwa_auto_dismissed')
  }
  deferredPrompt = null
  stopTimer()
}

const startTimer = () => {
  if (timer) clearInterval(timer)
  elapsedSeconds = 0
  timer = setInterval(() => {
    if (isPageVisible && !autoVisible.value && deferredPrompt) {
      elapsedSeconds++
      if (elapsedSeconds >= 30) {
        showAutoBanner()
      }
    }
  }, 1000)
}

const handleVisibilityChange = () => {
  isPageVisible = !document.hidden
}

const isManualDismissedRecently = () => {
  const dismissed = localStorage.getItem('pwa_manual_dismissed')
  if (!dismissed) return false
  const now = Date.now()
  const oneDay = 24 * 60 * 60 * 1000
  return now - parseInt(dismissed) < oneDay
}

const dismissManual = () => {
  localStorage.setItem('pwa_manual_dismissed', Date.now().toString())
  manualVisible.value = false
}

const showManualGuide = () => {
  if (isManualDismissedRecently()) return
  manualVisible.value = true
}

const manualInstall = () => {
  if (autoSupported.value && deferredPrompt) {
    installApp()
  } else if (!autoSupported.value) {
    showManualGuide()
  } else {
    alert('当前环境暂不支持自动安装，请使用浏览器菜单手动添加')
  }
}

const checkAutoSupport = () => {
  let timeoutId: ReturnType<typeof setTimeout>
  const onBeforeInstall = (e: Event) => {
    clearTimeout(timeoutId)
    autoSupported.value = true
    deferredPrompt = e as BeforeInstallPromptEvent
    e.preventDefault()
    if (!isAutoDismissedRecently() && !autoVisible.value) {
      startTimer()
    }
    window.removeEventListener('beforeinstallprompt', onBeforeInstall)
  }
  window.addEventListener('beforeinstallprompt', onBeforeInstall)
  timeoutId = setTimeout(() => {
    autoSupported.value = false
    window.removeEventListener('beforeinstallprompt', onBeforeInstall)
    showManualGuide()
  }, 5000)
}

provide('triggerManualInstall', manualInstall)

onMounted(() => {
  // ========== 调试代码（需要时取消注释即可强制显示自动横幅） ==========
  // autoSupported.value = true
  // autoVisible.value = true
  // ========== 调试代码结束 ==========

  // 如果已经安装，则不再执行任何安装检测逻辑
  if (isInstalled.value) return

  checkAutoSupport()
  window.addEventListener('appinstalled', () => {
    localStorage.setItem('pwa_installed', 'true')
    isInstalled.value = true
    autoVisible.value = false
    deferredPrompt = null
    stopTimer()
  })
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  stopTimer()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.install-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}
.auto {
  background: white;
  border-top: 1px solid #e2e8f0;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
  padding: 12px 16px;
}
.install-banner-content {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}
.icon {
  font-size: 32px;
}
.text {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-size: 13px;
  color: #1e293b;
}
.text strong {
  font-size: 14px;
  margin-bottom: 2px;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: nowrap;
}
.install-btn,
.dismiss-btn {
  flex: 1;
  white-space: nowrap;
  text-align: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
  border: none;
}
.install-btn {
  background: #7c3aed;
  color: white;
}
.install-btn:hover {
  background: #6d28d9;
}
.dismiss-btn {
  background: #f1f5f9;
  color: #475569;
}
.dismiss-btn:hover {
  background: #e2e8f0;
}
.close-btn {
  background: none;
  border: none;
  color: #64748b;
  font-size: 18px;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.manual {
  bottom: 20px;
  left: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 16px;
  color: white;
}
.manual-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.manual-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: bold;
  font-size: 16px;
}
.manual-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.step-icon {
  font-size: 18px;
}
.em {
  font-weight: bold;
  margin: 0 4px;
}
.step-img {
  text-align: center;
  margin: 8px 0;
  width: 100%;
}
.guide-img {
  max-width: 100%;
  width: auto;
  height: auto;
  border-radius: 8px;
  display: block;
  margin: 0 auto;
}
.manual-note {
  font-size: 12px;
  text-align: center;
  opacity: 0.8;
  margin-top: 8px;
}
</style>
