// 限时节日视觉主题：根据当前日期决定是否启用对应皮肤
// 当前阶段「端午」强制启用；2026/6/16-6/22 自然命中端午。
// 也支持 URL 查询参数 ?theme=duanwu / ?theme=none 进行手动覆盖。

import { computed, ref } from 'vue'

export type FestivalKey = 'duanwu' | 'none'

export interface FestivalTheme {
  key: FestivalKey
  label: string
  // 主色（朱红）
  accent: string
  // 次色（竹青）
  accentSecondary: string
}

const DUANWU_THEME: FestivalTheme = {
  key: 'duanwu',
  label: '端午',
  accent: '#b91c1c',
  accentSecondary: '#2f6f4f',
}

const NONE_THEME: FestivalTheme = {
  key: 'none',
  label: '默认',
  accent: '',
  accentSecondary: '',
}

// 阳历近似窗口：2026 端午为 6/19，给前后 3 天的窗口。
// 后续需要扩展更多年份时，可改为农历换算或维护一张映射表。
const DUANWU_WINDOWS: Array<{ start: string; end: string }> = [
  { start: '2026-06-16', end: '2026-06-22' },
]

const queryThemeOverride = (): FestivalKey | null => {
  if (typeof window === 'undefined') return null
  const params = new URLSearchParams(window.location.search)
  const value = params.get('theme')
  if (value === 'duanwu' || value === 'none') return value
  return null
}

const inDuanwuWindow = (today: Date): boolean => {
  const iso = today.toISOString().slice(0, 10)
  return DUANWU_WINDOWS.some((win) => iso >= win.start && iso <= win.end)
}

// 调试期默认强开。等节日临近后改成 false，仅靠日期+URL 控制。
const FORCE_DUANWU = true

const resolveTheme = (now: Date = new Date()): FestivalTheme => {
  const override = queryThemeOverride()
  if (override === 'duanwu') return DUANWU_THEME
  if (override === 'none') return NONE_THEME
  if (FORCE_DUANWU) return DUANWU_THEME
  if (inDuanwuWindow(now)) return DUANWU_THEME
  return NONE_THEME
}

const activeTheme = ref<FestivalTheme>(resolveTheme())

export function useFestivalTheme() {
  const theme = computed(() => activeTheme.value)
  const isDuanwu = computed(() => activeTheme.value.key === 'duanwu')

  const refresh = () => {
    activeTheme.value = resolveTheme()
  }

  return { theme, isDuanwu, refresh }
}
