<template>
  <!-- 顶部路由切换进度条 -->
  <div
    v-show="visible"
    class="fixed left-0 top-0 z-[2000] h-0.5 bg-purple-500 transition-[width] duration-200 ease-out"
    :style="{ width: progress + '%' }"
    role="progressbar"
    aria-hidden="true"
  />

  <!-- 网络状态条：离线常驻提示，恢复后短暂提示后自动消失 -->
  <Transition name="netbar">
    <div
      v-if="banner.show"
      class="fixed inset-x-0 z-[1500] flex justify-center px-3"
      :style="{ top: 'env(safe-area-inset-top)' }"
      role="status"
    >
      <div
        class="mt-2 rounded-full px-4 py-1.5 text-xs font-medium text-white shadow-md"
        :class="online ? 'bg-green-600/90' : 'bg-slate-700/90'"
      >
        {{ banner.text }}
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouteProgress } from '@/composables/useRouteProgress'

const { visible, progress } = useRouteProgress()

const online = ref(navigator.onLine)
const banner = reactive({ show: false, text: '' })
let recoverTimer: ReturnType<typeof setTimeout> | null = null

function handleOffline() {
  online.value = false
  if (recoverTimer) clearTimeout(recoverTimer)
  banner.text = '网络已断开，部分内容将使用离线缓存'
  banner.show = true
}

function handleOnline() {
  online.value = true
  banner.text = '网络已恢复'
  banner.show = true
  if (recoverTimer) clearTimeout(recoverTimer)
  recoverTimer = setTimeout(() => {
    banner.show = false
  }, 2200)
}

onMounted(() => {
  window.addEventListener('offline', handleOffline)
  window.addEventListener('online', handleOnline)
  // 首屏即处于离线状态时直接提示
  if (!navigator.onLine) handleOffline()
})

onUnmounted(() => {
  window.removeEventListener('offline', handleOffline)
  window.removeEventListener('online', handleOnline)
  if (recoverTimer) clearTimeout(recoverTimer)
})
</script>

<style scoped>
.netbar-enter-active,
.netbar-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.netbar-enter-from,
.netbar-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
