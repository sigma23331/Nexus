import { onMounted, onUnmounted, ref, unref, type Ref } from 'vue'

export interface PullToRefreshOptions {
  /** 触发刷新所需的下拉距离（px） */
  threshold?: number
  /** 最大可视下拉距离（px） */
  max?: number
  /** 阻尼系数，越小越「重」 */
  damping?: number
}

type ElementSource = Ref<HTMLElement | null | undefined> | HTMLElement | null | undefined

/**
 * 移动端下拉刷新（解耦构件，不绑定任何具体页面）。
 *
 * 用法（在列表页 setup 中）：
 *   const scroller = ref<HTMLElement | null>(null)
 *   const { distance, refreshing } = usePullToRefresh(scroller, async () => {
 *     await reloadList()
 *   })
 * 然后用 distance / refreshing 渲染顶部下拉指示条即可。
 * 不传 target 时默认监听整页滚动（document）。
 */
export function usePullToRefresh(
  target: ElementSource,
  onRefresh: () => Promise<void> | void,
  options: PullToRefreshOptions = {},
) {
  const threshold = options.threshold ?? 70
  const max = options.max ?? 110
  const damping = options.damping ?? 0.5

  const distance = ref(0)
  const refreshing = ref(false)
  const pulling = ref(false)

  let startY = 0
  let active = false

  const resolveEl = (): HTMLElement | Document => unref(target) ?? document

  const scrollTopOf = (): number => {
    const el = unref(target)
    if (el) return el.scrollTop
    return document.scrollingElement?.scrollTop ?? document.documentElement.scrollTop ?? 0
  }

  const onTouchStart = (e: TouchEvent) => {
    if (refreshing.value || scrollTopOf() > 0) {
      active = false
      return
    }
    startY = e.touches[0].clientY
    active = true
  }

  const onTouchMove = (e: TouchEvent) => {
    if (!active || refreshing.value) return
    const dy = e.touches[0].clientY - startY
    if (dy <= 0) {
      distance.value = 0
      pulling.value = false
      return
    }
    distance.value = Math.min(max, dy * damping)
    pulling.value = true
    if (e.cancelable) e.preventDefault()
  }

  const onTouchEnd = async () => {
    if (!active) return
    active = false
    if (refreshing.value) return
    if (distance.value >= threshold) {
      refreshing.value = true
      distance.value = threshold
      try {
        await onRefresh()
      } finally {
        refreshing.value = false
        distance.value = 0
        pulling.value = false
      }
    } else {
      distance.value = 0
      pulling.value = false
    }
  }

  const bind = (el: HTMLElement | Document) => {
    el.addEventListener('touchstart', onTouchStart as EventListener, { passive: true })
    el.addEventListener('touchmove', onTouchMove as EventListener, { passive: false })
    el.addEventListener('touchend', onTouchEnd as EventListener)
    el.addEventListener('touchcancel', onTouchEnd as EventListener)
  }

  const unbind = (el: HTMLElement | Document) => {
    el.removeEventListener('touchstart', onTouchStart as EventListener)
    el.removeEventListener('touchmove', onTouchMove as EventListener)
    el.removeEventListener('touchend', onTouchEnd as EventListener)
    el.removeEventListener('touchcancel', onTouchEnd as EventListener)
  }

  onMounted(() => bind(resolveEl()))
  onUnmounted(() => unbind(resolveEl()))

  return { distance, refreshing, pulling }
}
