<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 头部（不变） -->
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">✨</span>
      <h1 class="text-2xl font-bold">运势看板</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
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
          class="rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 via-white to-rose-50 p-4"
        >
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
          <div ref="chartRef" class="h-56 w-full"></div>
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
            class="flex-1 bg-purple-600 hover:bg-purple-700 rounded-xl py-2 text-sm font-medium"
          >
            生成卡片
          </button>
          <button
            class="flex-1 bg-white border border-slate-200 text-slate-700 rounded-xl py-2 text-sm font-medium"
          >
            分享
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import FortuneCardPreview from './components/FortuneCardPreview.vue'
import TodayFortuneContent from './components/TodayFortuneContent.vue'
// import { useFortuneStore } from '@/stores/fortune'

// 静态数据（临时，后续替换为 store）
const fortuneData = ref({
  id: 'demo_1',
  date: '2026-04-26',
  score: 88,
  title: '上上签',
  content_main: '风起云开，顺遂自来',
  content_sub: '今日宜稳中求进，心静则通达',
  love: '中上',
  career: '平稳',
  health: '注意作息',
  wealth: '谨慎消费',
  yi: ['喝奶茶', '摸鱼五分钟'],
  ji: ['熬夜', '已读不回'],
})

const trendScores = ref([63, 68, 65, 74, 71, 79, fortuneData.value.score])
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const currentScore = computed(() => trendScores.value[trendScores.value.length - 1])
const previousScore = computed(
  () => trendScores.value[trendScores.value.length - 2] ?? currentScore.value,
)
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
  if (currentScore.value >= 80) return '巳时'
  if (currentScore.value >= 70) return '午时'
  return '酉时'
})
const luckyHourRange = computed(() => {
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

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)

  chartInstance.setOption({
    backgroundColor: 'transparent',
    grid: { left: 10, right: 10, top: 16, bottom: 16, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17,24,39,0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
      formatter: (params: echarts.CallbackDataParams | echarts.CallbackDataParams[]) => {
        const point = Array.isArray(params) ? params[0] : params
        return `第${point.axisValue}日 · ${scoreToSign(point.value)}`
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['一', '二', '三', '四', '五', '六', '七'],
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
        smooth: true,
        data: trendScores.value,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#b45309' },
        itemStyle: { color: '#f59e0b', borderColor: '#fffbeb', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245,158,11,0.35)' },
            { offset: 1, color: 'rgba(245,158,11,0.05)' },
          ]),
        },
      },
    ],
  })
}

const handleResize = () => chartInstance?.resize()

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

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
