import { ref } from 'vue'

export type ToastType = 'info' | 'success' | 'error' | 'warning'

export interface ToastItem {
  id: number
  message: string
  type: ToastType
}

const toasts = ref<ToastItem[]>([])
const MAX_VISIBLE = 3
let seed = 0

function push(message: string, type: ToastType, duration: number): number {
  const id = ++seed
  toasts.value.push({ id, message, type })
  // 超出最大可见数量时移除最早的一条，避免堆叠过多
  if (toasts.value.length > MAX_VISIBLE) {
    toasts.value.shift()
  }
  if (duration > 0) {
    setTimeout(() => dismiss(id), duration)
  }
  return id
}

function dismiss(id: number): void {
  const index = toasts.value.findIndex((item) => item.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

/**
 * 全局轻提示。模块级单例，任意组件/工具内调用 useToast() 共享同一队列。
 * 容器由 main.ts 独立挂载，无需在业务页面中放置组件。
 */
export function useToast() {
  return {
    toasts,
    show: (message: string, duration = 2500) => push(message, 'info', duration),
    info: (message: string, duration = 2500) => push(message, 'info', duration),
    success: (message: string, duration = 2500) => push(message, 'success', duration),
    error: (message: string, duration = 3000) => push(message, 'error', duration),
    warning: (message: string, duration = 3000) => push(message, 'warning', duration),
    dismiss,
  }
}
