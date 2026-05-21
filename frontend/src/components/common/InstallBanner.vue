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

  <!-- 手动引导模式（适用于无法自动安装的环境） -->
  <div v-if="!isInstalled && manualVisible" class="install-banner manual">
    <div class="manual-content">
      <div class="manual-header">
        <span class="icon">📲</span>
        <span>添加到主屏幕</span>
        <button @click="dismissManual" class="close-btn">✕</button>
      </div>
      <div class="manual-steps">
        <!-- iOS 引导 -->
        <template v-if="platform === 'ios'">
          <div class="step">
            <span class="step-icon">1️⃣</span>
            <span>点击底部<span class="em">分享</span>按钮</span>
          </div>
          <div class="step">
            <span class="step-icon">2️⃣</span>
            <span>滑动找到<span class="em">添加到主屏幕</span></span>
          </div>
        </template>

        <!-- 支持PWA的浏览器（Chrome、Edge等）引导 -->
        <template v-else-if="platform === 'pwa'">
          <div class="step">
            <span class="step-icon">1️⃣</span>
            <span>点击右上角<span class="em">菜单</span>按钮（⋮）</span>
          </div>
          <div class="step">
            <span class="step-icon">2️⃣</span>
            <span>选择<span class="em">添加到主屏幕</span>或<span class="em">安装应用</span></span>
          </div>
        </template>

        <!-- 其他浏览器（QQ、Vivo、UC等）引导 - 4步书签法 -->
        <template v-else>
          <div class="step">
            <span class="step-icon">1️⃣</span>
            <span>点击浏览器右上角<span class="em">菜单</span>按钮</span>
          </div>
          <div class="step">
            <span class="step-icon">2️⃣</span>
            <span>选择<span class="em">添加到书签</span>（或收藏）</span>
          </div>
          <div class="step">
            <span class="step-icon">3️⃣</span>
            <span>编辑书签名（如“心运岛”），点击<span class="em">保存/完成</span></span>
          </div>
          <div class="step">
            <span class="step-icon">4️⃣</span>
            <span>再次打开菜单，选择<span class="em">添加到桌面</span>即可</span>
          </div>
        </template>

        <div class="step-img">
          <img :src="guideImage" alt="添加到主屏幕步骤" class="guide-img" />
        </div>
      </div>
      <p class="manual-note">将心运岛添加到主屏幕，使用更便捷~</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, provide, computed } from 'vue'

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const isInstalled = ref(localStorage.getItem('pwa_installed') === 'true')

const autoSupported = ref(false)
const autoVisible = ref(false)
let deferredPrompt: BeforeInstallPromptEvent | null = null
let timer: ReturnType<typeof setInterval> | null = null
let elapsedSeconds = 0
let isPageVisible = true

const manualVisible = ref(false)

// ========== 平台检测（增强版） ==========
// platform 类型：'ios' | 'pwa' | 'other'
const platform = ref<'ios' | 'pwa' | 'other'>('other')

const detectPlatform = () => {
  const ua = navigator.userAgent.toLowerCase()
  // 1. 检测 iOS / iPadOS
  const isIOS = /iphone|ipad|ipod/.test(ua)
  const isIPad = /macintosh/.test(ua) && navigator.maxTouchPoints && navigator.maxTouchPoints > 2
  if (isIOS || isIPad) {
    platform.value = 'ios'
    return
  }

  // 2. 检测是否支持 PWA 安装的现代浏览器（Chrome、Edge、Samsung Internet、Opera等）
  // 通过 UA 匹配常见内核，且排除国内定制浏览器（QQ、UC等）
  const isChrome = /chrome/.test(ua) && !/edg|qq|ucbrowser|vivaldi/.test(ua)
  const isEdge = /edg/.test(ua)
  const isSamsung = /samsungbrowser/.test(ua)
  const isOpera = /opr|opera/.test(ua)
  // 也支持 Firefox（但 Firefox 对 PWA 支持有限，仍可归为 pwa 类）
  const isFirefox = /firefox/.test(ua) && !/focus/.test(ua)

  if (isChrome || isEdge || isSamsung || isOpera || isFirefox) {
    platform.value = 'pwa'
  } else {
    // 其他浏览器（QQ、Vivo、UC、360、百度、夸克等）
    platform.value = 'other'
  }
}

// 根据平台动态选择引导图片
const guideImage = computed(() => {
  if (platform.value === 'ios') return '/images/guide.png'
  if (platform.value === 'pwa') return '/images/guide1.png'
  return '/images/guide2.png'
})

// ========== 自动安装相关（不变） ==========
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
  if (deferredPrompt) {
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
  } else {
    showManualGuideForce()
  }
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

// ========== 手动引导相关（不变） ==========
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

const showManualGuideForce = () => {
  manualVisible.value = true
}

const manualInstall = () => {
  if (deferredPrompt) {
    installApp()
  } else {
    showManualGuideForce()
  }
}

// ========== 检测自动安装支持（不变） ==========
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

const handleManualInstallEvent = () => {
  manualInstall()
}

onMounted(() => {
  // 调试代码（取消注释可强制显示自动横幅）
  // autoSupported.value = true
  // autoVisible.value = true

  // 检测平台类型（增强版）
  detectPlatform()

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
  window.addEventListener('manual-install-trigger', handleManualInstallEvent)
})

onUnmounted(() => {
  stopTimer()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  window.removeEventListener('manual-install-trigger', handleManualInstallEvent)
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

/* ========== 手动引导卡片样式优化 ========== */
.manual {
  bottom: env(safe-area-inset-bottom, 20px);
  left: 16px;
  right: 16px;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 16px;
  color: white;
  max-width: calc(100% - 32px);
  margin: 0 auto;
  box-sizing: border-box;
}
.manual-content {
  max-height: 60vh;
  overflow-y: auto;
}
.manual-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 30px;
  position: relative;
  font-weight: bold;
  font-size: 16px;
}
.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.manual-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
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

/* 针对 PWA 独立窗口微调 */
@media all and (display-mode: standalone) {
  .manual {
    bottom: 20px;
    left: 20px;
    right: 20px;
  }
  .manual-content {
    max-height: 90vh;
  }
}
</style>
