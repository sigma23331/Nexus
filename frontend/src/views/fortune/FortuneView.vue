<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 加载状态（仅首次加载显示，避免闪烁） -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-purple-600">加载中...</div>
    </div>

    <template v-else>
      <header class="flex items-center gap-2 px-6 pt-6 pb-2">
        <span class="text-2xl">✨</span>
        <h1 class="text-2xl font-bold">运势看板</h1>
      </header>

      <!-- 轻提示：数据加载失败时显示，但不影响布局 -->
      <div
        v-if="loadError"
        class="mx-6 mb-2 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700"
      >
        📡 数据加载失败，请稍后重试
      </div>

      <main class="px-6 py-4 space-y-8">
        <!-- 今日运势卡片 -->
        <section
          class="relative overflow-hidden rounded-3xl border border-amber-200 bg-white p-5 shadow-sm"
        >
          <div class="absolute -top-10 -right-10 h-24 w-24 rounded-full bg-amber-100"></div>
          <div class="absolute -bottom-10 -left-10 h-24 w-24 rounded-full bg-rose-100"></div>
          <div class="relative space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold tracking-wide text-amber-700">今日签文</span>
              <span class="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
                {{ fortuneData.title }}
              </span>
            </div>
            <TodayFortuneContent
              :content-main="fortuneData.content_main"
              :content-sub="fortuneData.content_sub"
            />

            <div class="space-y-3">
              <h2 class="text-sm font-semibold text-slate-700">今日概览</h2>
              <ul class="grid grid-cols-2 gap-3 text-sm">
                <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                  <span class="text-slate-500">爱情</span>
                  <span class="ml-2 font-semibold text-pink-500">{{ fortuneData.love }}</span>
                </li>
                <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                  <span class="text-slate-500">事业</span>
                  <span class="ml-2 font-semibold text-blue-500">{{ fortuneData.career }}</span>
                </li>
                <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                  <span class="text-slate-500">健康</span>
                  <span class="ml-2 font-semibold text-green-600">{{ fortuneData.health }}</span>
                </li>
                <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                  <span class="text-slate-500">财富</span>
                  <span class="ml-2 font-semibold text-yellow-600">{{ fortuneData.wealth }}</span>
                </li>
              </ul>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-3">
                <p class="text-xs font-semibold text-emerald-700">宜</p>
                <ul class="mt-2 text-sm text-emerald-700 space-y-1">
                  <li v-for="item in fortuneData.yi" :key="item">• {{ item }}</li>
                </ul>
              </div>
              <div class="rounded-2xl border border-rose-200 bg-rose-50 p-3">
                <p class="text-xs font-semibold text-rose-700">忌</p>
                <ul class="mt-2 text-sm text-rose-700 space-y-1">
                  <li v-for="item in fortuneData.ji" :key="item">• {{ item }}</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <!-- 运势轨迹 + ECharts -->
        <section>
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-lg font-semibold">运势轨迹</h2>
            <span
              class="rounded-full border px-3 py-1 text-xs font-semibold"
              :class="trendBadgeClass"
            >
              {{ trendText }}
            </span>
          </div>
          <div
            class="relative overflow-hidden rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 via-white to-rose-50 p-4 shadow-[0_10px_30px_rgba(180,83,9,0.16)]"
          >
            <div
              class="pointer-events-none absolute -left-16 top-6 h-36 w-36 rounded-full bg-amber-200/35 blur-3xl"
            ></div>
            <div
              class="pointer-events-none absolute -right-12 bottom-8 h-32 w-32 rounded-full bg-rose-200/40 blur-3xl"
            ></div>
            <div class="mb-4 grid grid-cols-3 gap-2 text-center">
              <div class="rounded-xl border border-amber-200 bg-white/80 px-2 py-2">
                <p class="text-[11px] text-amber-700">今日签象</p>
                <p class="mt-1 text-base font-semibold text-slate-900">{{ fortuneData.title }}</p>
              </div>
              <div class="rounded-xl border border-amber-200 bg-white/80 px-2 py-2">
                <p class="text-[11px] text-amber-700">卦意</p>
                <div class="mt-1 min-h-10 text-base font-semibold text-slate-900 leading-5">
                  <p>{{ guaMeaningLines[0] }}</p>
                  <p>{{ guaMeaningLines[1] }}</p>
                </div>
              </div>
              <div class="rounded-xl border border-amber-200 bg-white/80 px-2 py-2">
                <p class="text-[11px] text-amber-700">开运时辰</p>
                <p class="mt-1 text-base font-semibold text-slate-900 leading-5">
                  {{ luckyHourName }}<br />
                  {{ luckyHourRange }}
                </p>
              </div>
            </div>
            <div ref="chartRef" class="relative h-60 w-full"></div>
            <p class="mt-3 text-center text-xs text-amber-700/90">太极流转，顺势而为</p>
          </div>
        </section>

        <!-- 运势卡片生成 -->
        <section>
          <h2 class="text-lg font-semibold mb-3">运势卡片</h2>
          <FortuneCardPreview
            :title="fortuneData.title"
            :score="fortuneData.score"
            :content-main="fortuneData.content_main"
            :content-sub="fortuneData.content_sub"
            :yi="fortuneData.yi"
            :ji="fortuneData.ji"
          />
          <div class="flex gap-3 mt-4">
            <button
              class="flex-1 bg-purple-600 hover:bg-purple-700 rounded-xl py-2 text-sm font-medium text-white"
            >
              生成卡片
            </button>
            <button
              type="button"
              class="flex-1 bg-white border border-slate-200 text-slate-700 rounded-xl py-2 text-sm font-medium"
              @click="sharePreviewOpen = true"
            >
              分享
            </button>
          </div>
        </section>
      </main>
    </template>

    <Teleport to="body">
      <Transition name="fortune-share">
        <div
          v-if="sharePreviewOpen && fortuneSharePayload"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
          @click.self="sharePreviewOpen = false"
        >
          <div
            class="fortune-share-panel max-h-[90vh] w-full max-w-sm overflow-y-auto rounded-2xl bg-white p-5 shadow-xl"
          >
            <div class="mb-4 flex items-center justify-between">
              <h3 class="text-sm font-semibold text-slate-900">分享运势</h3>
              <button
                type="button"
                class="rounded-full px-2 py-1 text-xs text-slate-500 hover:bg-slate-100"
                @click="sharePreviewOpen = false"
              >
                关闭
              </button>
            </div>
            <FortuneShareReveal :fortune="fortuneSharePayload" />
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import FortuneCardPreview from './components/FortuneCardPreview.vue'
import FortuneShareReveal from './components/FortuneShareReveal.vue'
import TodayFortuneContent from './components/TodayFortuneContent.vue'
import { getFortuneToday, getFortuneTrend, type FortuneToday, type TrendPoint } from '@/api/fortune'

interface EChartsTooltipParam {
  axisValue: string
  value: number
  [key: string]: unknown
}

// 默认占位数据（保证页面框架始终显示）
const defaultFortuneData: FortuneToday = {
  id: '',
  date: '',
  score: 0,
  title: '--',
  content_main: '--',
  content_sub: '--',
  love: '--',
  career: '--',
  health: '--',
  wealth: '--',
  yi: [],
  ji: [],
}

// 状态
const loading = ref(true)
const loadError = ref(false)
const fortuneData = ref<FortuneToday>(defaultFortuneData)
const trendPoints = ref<TrendPoint[]>([])

const sharePreviewOpen = ref(false)

// 卡片分享数据
const fortuneSharePayload = computed(() => ({
  title: fortuneData.value.title,
  score: fortuneData.value.score,
  content_main: fortuneData.value.content_main,
  content_sub: fortuneData.value.content_sub,
  yi: fortuneData.value.yi,
  ji: fortuneData.value.ji,
}))

// 从 trendPoints 中提取分数数组
const trendScores = computed(() => trendPoints.value.map((p) => p.value))

// 用于趋势判断的分数前后差值
const currentScore = computed(() => {
  if (trendScores.value.length === 0) return 0
  return trendScores.value[trendScores.value.length - 1]
})
const previousScore = computed(() => {
  if (trendScores.value.length < 2) return currentScore.value
  return trendScores.value[trendScores.value.length - 2]
})
const delta = computed(() => currentScore.value - previousScore.value)

const trendText = computed(() => {
  if (delta.value >= 3) return '气运上扬'
  if (delta.value <= -3) return '气运回落'
  return '气运平稳'
})

const guaMeaningLines = computed(() => {
  if (delta.value >= 3) return ['火土相生', '宜主动求进']
  if (delta.value <= -3) return ['水势偏重', '宜静守内观']
  return ['阴阳守中', '宜稳步前行']
})

const luckyHourName = computed(() => {
  const score = currentScore.value
  if (score >= 80) return '巳时'
  if (score >= 70) return '午时'
  return '酉时'
})

const luckyHourRange = computed(() => {
  const score = currentScore.value
  if (score >= 80) return '09:00-11:00'
  if (score >= 70) return '11:00-13:00'
  return '17:00-19:00'
})

const trendBadgeClass = computed(() => {
  if (delta.value >= 3) return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (delta.value <= -3) return 'border-rose-200 bg-rose-50 text-rose-700'
  return 'border-amber-200 bg-amber-50 text-amber-700'
})

const scoreToSign = (score: number) => {
  if (score >= 85) return '上上签'
  if (score >= 75) return '上吉'
  if (score >= 65) return '中平'
  if (score >= 55) return '小谨'
  return '守静'
}

// ECharts 部分
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value || trendScores.value.length === 0) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)

  const xAxisData = trendPoints.value.map((p) => p.date)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    grid: { left: 10, right: 10, top: 16, bottom: 16, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17,24,39,0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
      formatter: (params: EChartsTooltipParam | EChartsTooltipParam[]) => {
        const point = Array.isArray(params) ? params[0] : params
        return `${point.axisValue} · ${scoreToSign(point.value)}`
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData,
      axisLine: { lineStyle: { color: '#f59e0b' } },
      axisLabel: { color: '#92400e' },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 40,
      max: 100,
      splitNumber: 4,
      axisLabel: {
        color: '#a16207',
        formatter: (value: number) => scoreToSign(value),
      },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(180,83,9,0.15)' } },
    },
    series: [
      {
        type: 'line',
        smooth: 0.55,
        data: trendScores.value,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 4,
          color: '#b45309',
          shadowColor: 'rgba(180,83,9,0.35)',
          shadowBlur: 12,
          shadowOffsetY: 4,
        },
        itemStyle: { color: '#f59e0b', borderColor: '#fffbeb', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245,158,11,0.42)' },
            { offset: 0.55, color: 'rgba(251,191,36,0.20)' },
            { offset: 1, color: 'rgba(245,158,11,0.05)' },
          ]),
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            shadowColor: 'rgba(245,158,11,0.45)',
            shadowBlur: 18,
          },
        },
      },
    ],
  })
}

const handleResize = () => chartInstance?.resize()

// 加载数据（若失败则保持默认占位数据）
const loadData = async () => {
  loading.value = true
  loadError.value = false
  try {
    const [today, trendRes] = await Promise.all([getFortuneToday(), getFortuneTrend()])
    fortuneData.value = today
    trendPoints.value = trendRes.trendPoints
  } catch (error) {
    console.error('加载运势数据失败，使用默认占位符:', error)
    loadError.value = true
    // 保持 fortuneData 为默认占位符（已在 ref 中初始化），不需要额外处理
    trendPoints.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadData()
  // 如果趋势数据为空，则图表不初始化（避免报错）
  if (chartRef.value && trendScores.value.length > 0) {
    initChart()
    window.addEventListener('resize', handleResize)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<style scoped>
.fortune-share-enter-active,
.fortune-share-leave-active {
  transition: background-color 0.22s ease;
}
.fortune-share-enter-active .fortune-share-panel,
.fortune-share-leave-active .fortune-share-panel {
  transition:
    transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1),
    opacity 0.28s ease;
}
.fortune-share-enter-from {
  background-color: rgba(0, 0, 0, 0);
}
.fortune-share-enter-from .fortune-share-panel {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}
.fortune-share-leave-to {
  background-color: rgba(0, 0, 0, 0);
}
.fortune-share-leave-to .fortune-share-panel {
  opacity: 0;
  transform: translateY(8px) scale(0.99);
}
</style>
