import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FortuneToday, FortuneTrend, FortuneGlobalStats } from '@/types/models'

export const useFortuneStore = defineStore('fortune', () => {
  // State
  const todayFortune = ref<FortuneToday | null>(null)
  const trendPoints = ref<FortuneTrend['trendPoints']>([])
  const globalStats = ref<FortuneGlobalStats | null>(null)

  // Actions
  function setTodayFortune(data: FortuneToday) {
    todayFortune.value = data
  }

  function setTrendPoints(points: FortuneTrend['trendPoints']) {
    trendPoints.value = points
  }

  function setGlobalStats(stats: FortuneGlobalStats) {
    globalStats.value = stats
  }

  // 清空所有运势数据（登出时可选）
  function clearFortune() {
    todayFortune.value = null
    trendPoints.value = []
    globalStats.value = null
  }

  return {
    todayFortune,
    trendPoints,
    globalStats,
    setTodayFortune,
    setTrendPoints,
    setGlobalStats,
    clearFortune,
  }
})
