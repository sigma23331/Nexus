<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 头部（不变） -->
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">✨</span>
      <h1 class="text-2xl font-bold">运势看板</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section
        v-if="loading"
        class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600"
      >
        正在加载运势数据...
      </section>
      <section
        v-else-if="errorMessage"
        class="flex items-center justify-between rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700"
      >
        <span>📡 {{ errorMessage }}</span>
        <button
          type="button"
          class="rounded-lg border border-rose-300 px-3 py-1 text-xs hover:bg-rose-100"
          @click="loadFortuneBoard"
        >
          重试
        </button>
      </section>

      <section
        class="relative overflow-hidden rounded-3xl border border-amber-200 bg-white p-5 shadow-sm"
      >
        <div class="absolute -top-10 -right-10 h-24 w-24 rounded-full bg-amber-100"></div>
        <div class="absolute -bottom-10 -left-10 h-24 w-24 rounded-full bg-rose-100"></div>
        <div class="relative space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold tracking-wide text-amber-700">今日签文</span>
            <!-- 运势分展示（本示例忽略，全站统计需要） -->
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
                <li v-if="!fortuneData.yi.length">• --</li>
              </ul>
            </div>
            <div class="rounded-2xl border border-rose-200 bg-rose-50 p-3">
              <p class="text-xs font-semibold text-rose-700">忌</p>
              <ul class="mt-2 text-sm text-rose-700 space-y-1">
                <li v-for="item in fortuneData.ji" :key="item">• {{ item }}</li>
                <li v-if="!fortuneData.ji.length">• --</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

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

      <section>
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold">历史运势记录</h2>
          <span class="text-xs text-slate-500">最近 7 天</span>
        </div>
        <div class="space-y-3">
          <article
            v-for="record in historyFortunes"
            :key="record.id"
            class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div class="mb-2 flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ record.date }}</p>
                <p class="text-xs text-slate-500">{{ record.title }}</p>
              </div>
              <span
                class="rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="scoreLevelClass(record.score)"
              >
                {{ record.score }} 分
              </span>
            </div>
            <p class="text-sm text-slate-700">{{ record.contentMain }}</p>
            <div class="mt-3 flex gap-2 text-xs">
              <span
                class="inline-flex max-w-[48%] items-center rounded-full bg-emerald-50 px-2 py-1 text-emerald-700"
              >
                宜：{{ record.yi[0] }}
              </span>
              <span
                class="inline-flex max-w-[48%] items-center rounded-full bg-rose-50 px-2 py-1 text-rose-700"
              >
                忌：{{ record.ji[0] }}
              </span>
            </div>
          </article>
          <article
            v-if="!historyFortunes.length"
            class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500"
          >
            暂无历史运势记录
          </article>
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
            class="flex-1 bg-purple-600 hover:bg-purple-700 rounded-xl py-2 text-sm font-medium"
            @click="loadFortuneBoard"
          >
            刷新卡片
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

    <Teleport to="body">
      <Transition name="fortune-share">
        <div
          v-if="sharePreviewOpen"
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { getFortuneToday, getFortuneTrend, getHistoryFortune } from '@/api/fortune'
import FortuneCardPreview from './components/FortuneCardPreview.vue'
import FortuneShareReveal from './components/FortuneShareReveal.vue'
import TodayFortuneContent from './components/TodayFortuneContent.vue'
// import { useFortuneStore } from '@/stores/fortune'

type FortuneViewData = {
  id: string
  date: string
  score: number
  title: string
  content_main: string
  content_sub: string
  yi: string[]
  ji: string[]
  love: string
  career: string
  health: string
  wealth: string
  gua_meaning_lines: string[]
  lucky_hour_name: string
  lucky_hour_range: string
}

const fortuneData = ref({
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
  gua_meaning_lines: [] as string[],
  lucky_hour_name: '',
  lucky_hour_range: '',
  yi: [] as string[],
  ji: [] as string[],
} satisfies FortuneViewData)

const loading = ref(true)
const errorMessage = ref('')

const sharePreviewOpen = ref(false)

const fortuneSharePayload = computed(() => ({
  title: fortuneData.value.title,
  score: fortuneData.value.score,
  content_main: fortuneData.value.content_main,
  content_sub: fortuneData.value.content_sub,
  yi: fortuneData.value.yi,
  ji: fortuneData.value.ji,
}))

const trendScores = ref<number[]>([])
const filledTrendDays = ref(0)
const historyFortunes = ref<
  Array<{
    id: string
    date: string
    score: number
    title: string
    contentMain: string
    yi: string[]
    ji: string[]
  }>
>([])
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const chartScores = computed<(number | null)[]>(() => {
  const filled = Math.min(Math.max(filledTrendDays.value, 0), 7)
  if (filled === 0) return [fortuneData.value.score, null, null, null, null, null, null]

  // 历史不足7天：第1天从第1格开始依次填充；满7天后切换为最近7天滚动
  if (filled < 7) {
    const validScores = trendScores.value.slice(-filled)
    return [...validScores, ...Array.from({ length: 7 - filled }, () => null)]
  }

  return trendScores.value.slice(-7)
})

const currentScore = computed(() => {
  const values = chartScores.value.filter((item): item is number => typeof item === 'number')
  return values[values.length - 1] ?? fortuneData.value.score ?? 0
})
const previousScore = computed(() => {
  const values = chartScores.value.filter((item): item is number => typeof item === 'number')
  return values[values.length - 2] ?? currentScore.value
})
const delta = computed(() => currentScore.value - previousScore.value)
const trendText = computed(() => {
  if (delta.value >= 3) return '气运上扬'
  if (delta.value <= -3) return '气运回落'
  return '气运平稳'
})
const guaMeaningLines = computed(() => {
  if (fortuneData.value.gua_meaning_lines.length >= 2) {
    return fortuneData.value.gua_meaning_lines.slice(0, 2)
  }
  if (delta.value >= 3) return ['火土相生', '宜主动求进']
  if (delta.value <= -3) return ['水势偏重', '宜静守内观']
  return ['阴阳守中', '宜稳步前行']
})
const luckyHourName = computed(() => {
  if (fortuneData.value.lucky_hour_name) return fortuneData.value.lucky_hour_name
  if (currentScore.value >= 80) return '巳时'
  if (currentScore.value >= 70) return '午时'
  return '酉时'
})
const luckyHourRange = computed(() => {
  if (fortuneData.value.lucky_hour_range) return fortuneData.value.lucky_hour_range
  if (currentScore.value >= 80) return '09:00-11:00'
  if (currentScore.value >= 70) return '11:00-13:00'
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
const scoreLevelClass = (score: number) => {
  if (score >= 85) return 'bg-emerald-50 text-emerald-700'
  if (score >= 75) return 'bg-blue-50 text-blue-700'
  if (score >= 65) return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-700'
}

const normalizeFortuneToday = (
  raw: Awaited<ReturnType<typeof getFortuneToday>>,
): FortuneViewData => {
  return {
    id: raw.id ?? '',
    date: raw.date ?? '',
    score: Number(raw.score ?? 0),
    title: raw.title || '--',
    content_main: raw.content_main || '--',
    content_sub: raw.content_sub || '--',
    love: raw.love || '--',
    career: raw.career || '--',
    health: raw.health || '--',
    wealth: raw.wealth || '--',
    gua_meaning_lines: Array.isArray(raw.gua_meaning_lines) ? raw.gua_meaning_lines : [],
    lucky_hour_name: raw.lucky_hour_name || '',
    lucky_hour_range: raw.lucky_hour_range || '',
    yi: Array.isArray(raw.yi) ? raw.yi : [],
    ji: Array.isArray(raw.ji) ? raw.ji : [],
  }
}

const formatMMDD = (dateStr: string) => {
  if (!dateStr) return '--'
  return dateStr.length >= 10 ? dateStr.slice(5, 10) : dateStr
}

const loadFortuneBoard = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const [today, trend, history] = await Promise.all([
      getFortuneToday(),
      getFortuneTrend(),
      getHistoryFortune(1, 7),
    ])

    fortuneData.value = normalizeFortuneToday(today)

    const points = Array.isArray(trend.trendPoints) ? trend.trendPoints : []
    trendScores.value = points.map((item) => Number(item.value ?? 0))
    const historyList = Array.isArray(history.list) ? history.list : []
    filledTrendDays.value = Math.min(historyList.length, 7)
    if (!trendScores.value.length) {
      trendScores.value = [fortuneData.value.score]
      filledTrendDays.value = 1
    }

    historyFortunes.value = historyList.map((item, index) => ({
      id: `${item.date || 'record'}_${index}`,
      date: formatMMDD(item.date || ''),
      score: Number(item.score ?? 0),
      title: item.title || '--',
      contentMain: '详情请查看当日运势',
      yi: fortuneData.value.yi.slice(0, 1),
      ji: fortuneData.value.ji.slice(0, 1),
    }))
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '数据加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  if (!chartRef.value) return
  chartInstance?.dispose()
  chartInstance = echarts.init(chartRef.value)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    grid: { left: 10, right: 10, top: 16, bottom: 16, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17,24,39,0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
      formatter: (params: unknown) => {
        const rawPoint = Array.isArray(params) ? params[0] : params
        const point = (rawPoint || {}) as { axisValue?: string | number; value?: number }
        return `第${point.axisValue ?? '--'}日 · ${scoreToSign(Number(point.value ?? 0))}`
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['1', '2', '3', '4', '5', '6', '7'],
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
        connectNulls: false,
        smooth: 0.55,
        data: chartScores.value,
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

onMounted(() => {
  void loadFortuneBoard()
  window.addEventListener('resize', handleResize)
})

watch(
  [trendScores, filledTrendDays],
  ([scores]) => {
    if (!scores.length && !filledTrendDays.value) return
    initChart()
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})

// ===== Pinia 接入示例（注释保留） =====
// 1. 引入 store
// const fortuneStore = useFortuneStore()
//
// 2. 从 store 读取数据（假设已经通过 API 设置过）
// const fortuneData = computed(() => {
//   if (fortuneStore.todayFortune) {
//     return fortuneStore.todayFortune
//   } else {
//     // 降级：使用静态数据或展示占位
//     return fallbackFortune
//   }
// })
//
// 3. 在 mounted 中请求数据并存入 store
// onMounted(async () => {
//   if (!fortuneStore.todayFortune) {
//     const data = await getFortuneToday()  // 调用 API
//     fortuneStore.setTodayFortune(data)
//   }
// })
//
// 4. 注意：getFortuneToday 需要定义在 src/api/fortune.ts 中

// 为了不破坏当前显示，暂时不调用真实 API，保留静态数据
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
