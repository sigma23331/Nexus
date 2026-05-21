import { ref, computed, onMounted, onUnmounted } from 'vue'

function isIosDevice() {
  return /iphone|ipad|ipod/i.test(navigator.userAgent)
}

function isStandaloneMode() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  )
}

export function usePwaInstall() {
  const canInstall = ref(false)
  const isInstalled = ref(isStandaloneMode())
  const isIos = ref(isIosDevice())
  let deferredPrompt: BeforeInstallPromptEvent | null = null

  const showInstallEntry = computed(() => !isInstalled.value && (canInstall.value || isIos.value))

  const iosInstallHint = computed(
    () =>
      isIos.value &&
      !isInstalled.value &&
      '点击 Safari 底部分享按钮，选择「添加到主屏幕」即可安装。',
  )

  function onBeforeInstallPrompt(e: BeforeInstallPromptEvent) {
    e.preventDefault()
    deferredPrompt = e
    canInstall.value = true
  }

  function onAppInstalled() {
    deferredPrompt = null
    canInstall.value = false
    isInstalled.value = true
  }

  onMounted(() => {
    isInstalled.value = isStandaloneMode()
    window.addEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.addEventListener('appinstalled', onAppInstalled)
  })

  onUnmounted(() => {
    window.removeEventListener('beforeinstallprompt', onBeforeInstallPrompt)
    window.removeEventListener('appinstalled', onAppInstalled)
    deferredPrompt = null
  })

  async function promptInstall(): Promise<boolean> {
    if (!deferredPrompt) return false
    await deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    deferredPrompt = null
    canInstall.value = false
    if (outcome === 'accepted') {
      isInstalled.value = true
    }
    return outcome === 'accepted'
  }

  return {
    canInstall,
    isInstalled,
    isIos,
    showInstallEntry,
    iosInstallHint,
    promptInstall,
  }
}
