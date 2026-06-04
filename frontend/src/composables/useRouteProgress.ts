import { ref } from 'vue'

/**
 * 顶部路由进度条状态（模块级单例）。
 * 由 main.ts 注册的路由钩子驱动，GlobalOverlay 负责渲染，与业务页面解耦。
 */
const visible = ref(false)
const progress = ref(0)
let timer: ReturnType<typeof setInterval> | null = null
let hideTimer: ReturnType<typeof setTimeout> | null = null

function start(): void {
  if (timer) clearInterval(timer)
  if (hideTimer) clearTimeout(hideTimer)
  visible.value = true
  progress.value = 8
  // 缓慢趋近 90%，等待真正加载完成后由 done() 收尾到 100%
  timer = setInterval(() => {
    const remaining = 90 - progress.value
    if (remaining <= 0.5) {
      progress.value = 90
      if (timer) {
        clearInterval(timer)
        timer = null
      }
      return
    }
    progress.value += Math.max(0.6, remaining * 0.08)
  }, 200)
}

function done(): void {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  progress.value = 100
  hideTimer = setTimeout(() => {
    visible.value = false
    progress.value = 0
    hideTimer = null
  }, 280)
}

export function useRouteProgress() {
  return { visible, progress, start, done }
}
