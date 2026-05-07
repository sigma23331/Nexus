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
              {{ isBoardUnlocked ? fortuneData.title : '待揭晓' }}
            </span>
          </div>
          <TodayFortuneContent
            v-if="isBoardUnlocked"
            :content-main="fortuneData.content_main"
            :content-sub="fortuneData.content_sub"
          />
          <div
            v-else
            class="rounded-2xl border border-amber-200 bg-gradient-to-br from-amber-50 to-rose-50 px-4 py-5"
          >
            <div class="board-draw">
              <div class="board-draw__stage">
                <div class="board-draw__stick" :data-phase="boardDrawPhase">
                  <div class="board-draw__stick-inner">
                    <p class="board-draw__stick-title">{{ drawStickTitle }}</p>
                  </div>
                </div>
                <div
                  class="board-draw__bucket-wrap"
                  :class="{ 'board-draw__bucket-wrap--hide': boardDrawPhase === 'stick' }"
                >
                  <div
                    class="board-draw__bucket"
                    :class="{ 'board-draw__bucket--shake': boardDrawPhase === 'shaking' }"
                  >
                    <svg
                      class="board-draw__tube-svg"
                      viewBox="0 0 120 168"
                      width="152"
                      height="212"
                      aria-hidden="true"
                    >
                      <defs>
                        <linearGradient id="board-tube-bamboo" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stop-color="#5c432f" />
                          <stop offset="22%" stop-color="#c9a66c" />
                          <stop offset="50%" stop-color="#deb887" />
                          <stop offset="78%" stop-color="#b8925a" />
                          <stop offset="100%" stop-color="#4a3528" />
                        </linearGradient>
                        <pattern
                          id="board-tube-ribs"
                          width="10"
                          height="168"
                          patternUnits="userSpaceOnUse"
                        >
                          <rect width="10" height="168" fill="url(#board-tube-bamboo)" />
                          <line
                            x1="9"
                            y1="0"
                            x2="9"
                            y2="168"
                            stroke="#3d291c"
                            stroke-opacity="0.35"
                            stroke-width="0.8"
                          />
                        </pattern>
                        <linearGradient id="board-tube-rim" x1="0%" y1="0%" x2="0%" y2="100%">
                          <stop offset="0%" stop-color="#8b6914" />
                          <stop offset="100%" stop-color="#5c4033" />
                        </linearGradient>
                      </defs>
                      <ellipse cx="60" cy="158" rx="44" ry="10" fill="#3d291c" />
                      <path
                        fill="url(#board-tube-ribs)"
                        d="M18 52 Q18 48 22 46 L98 46 Q102 48 102 52 L102 148 Q102 156 94 158 L26 158 Q18 156 18 148 Z"
                      />
                      <ellipse cx="60" cy="48" rx="48" ry="14" fill="url(#board-tube-rim)" />
                      <ellipse cx="60" cy="50" rx="36" ry="9" fill="#1a0f0a" />
                      <g>
                        <rect
                          x="44"
                          y="18"
                          width="4.5"
                          height="38"
                          rx="1"
                          fill="#f7ecd8"
                          stroke="#c4a574"
                          stroke-width="0.4"
                        />
                        <rect
                          x="51"
                          y="14"
                          width="4"
                          height="42"
                          rx="1"
                          fill="#faf4e6"
                          stroke="#c4a574"
                          stroke-width="0.4"
                        />
                        <rect
                          x="57"
                          y="16"
                          width="4.5"
                          height="40"
                          rx="1"
                          fill="#f2e6cc"
                          stroke="#c4a574"
                          stroke-width="0.4"
                        />
                        <rect
                          x="64"
                          y="12"
                          width="4"
                          height="44"
                          rx="1"
                          fill="#fff9ed"
                          stroke="#c4a574"
                          stroke-width="0.4"
                        />
                        <rect
                          x="71"
                          y="17"
                          width="4"
                          height="39"
                          rx="1"
                          fill="#f5ebd8"
                          stroke="#c4a574"
                          stroke-width="0.4"
                        />
                      </g>
                      <ellipse
                        cx="60"
                        cy="44"
                        rx="40"
                        ry="10"
                        fill="none"
                        stroke="#ffffff"
                        stroke-opacity="0.15"
                        stroke-width="1"
                      />
                    </svg>
                  </div>
                </div>
              </div>
              <p class="text-xs text-amber-700">
                {{
                  boardDrawPhase === 'shaking'
                    ? '轻晃签筒，求一支吉签'
                    : boardDrawPhase === 'stick'
                      ? '签文已显，正在解锁看板...'
                      : '今日首次进入，请先抽签'
                }}
              </p>
              <button
                v-if="boardDrawPhase === 'idle'"
                type="button"
                class="rounded-lg bg-amber-500 px-4 py-1.5 text-xs font-semibold text-white hover:bg-amber-600"
                @click="triggerBoardDraw"
              >
                开始抽签
              </button>
            </div>
          </div>

          <div v-if="isBoardUnlocked" class="space-y-3">
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

          <div v-if="isBoardUnlocked" class="grid grid-cols-2 gap-3">
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

      <section v-if="isBoardUnlocked">
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

      <section v-if="isBoardUnlocked">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-semibold">历史运势记录</h2>
          <span
            class="rounded-full border border-violet-200 bg-violet-50 px-2.5 py-1 text-xs text-violet-700"
          >
            {{ streakLabel }}
          </span>
        </div>
        <div class="space-y-3">
          <article
            v-for="record in historyFortunes"
            :key="record.id"
            class="cursor-pointer rounded-2xl border border-amber-100 bg-gradient-to-r from-amber-50/60 to-white p-4 shadow-sm transition hover:shadow-md"
            @click="openHistoryDetail(record)"
          >
            <div class="mb-3 flex items-center justify-between">
              <div>
                <p class="text-sm font-semibold text-slate-900">
                  {{ record.date }} · {{ record.title }}
                </p>
                <p class="text-xs text-slate-500">{{ record.summary }}</p>
              </div>
              <span
                class="rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="scoreLevelClass(record.score)"
              >
                {{ record.score }} 分
              </span>
            </div>
            <div class="mb-2 text-xs">
              <span class="rounded-full px-2 py-1" :class="record.linkClass">
                {{ record.linkText }}
              </span>
            </div>
            <div class="flex gap-2 text-xs">
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
            <p class="mt-2 text-right text-[11px] text-slate-400">点击查看详情</p>
          </article>
          <article
            v-if="!historyFortunes.length"
            class="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500"
          >
            暂无历史运势记录
          </article>
        </div>
      </section>

      <section v-if="isBoardUnlocked">
        <div class="flex gap-3 mt-4">
          <button
            type="button"
            class="flex-1 bg-purple-600 hover:bg-purple-700 rounded-xl py-2 text-sm font-medium text-white"
            @click="sharePreviewOpen = true"
          >
            生成运势卡片
          </button>
          <button
            type="button"
            class="flex-1 bg-white border border-slate-200 text-slate-700 rounded-xl py-2 text-sm font-medium"
            @click="openShareFortuneModal"
          >
            分享
          </button>
        </div>
      </section>
    </main>

    <Teleport to="body">
      <Transition name="fortune-share">
        <div
          v-if="historyDetailOpen && selectedHistory"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/55 p-4 backdrop-blur-sm"
          @click.self="historyDetailOpen = false"
        >
          <div class="w-full max-w-sm rounded-2xl bg-white p-5 shadow-xl">
            <div class="mb-3 flex items-center justify-between">
              <h3 class="text-base font-semibold text-slate-900">历史运势详情</h3>
              <button
                type="button"
                class="rounded-full px-2 py-1 text-xs text-slate-500 hover:bg-slate-100"
                @click="historyDetailOpen = false"
              >
                关闭
              </button>
            </div>
            <div class="space-y-3 text-sm">
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs text-slate-500">{{ selectedHistory.date }}</p>
                <p class="mt-1 text-base font-semibold text-slate-900">
                  {{ selectedHistory.title }}
                </p>
                <p class="mt-1 text-slate-700">{{ selectedHistory.summary }}</p>
                <p class="mt-2 text-xs text-violet-700">{{ selectedHistory.story }}</p>
              </div>
              <div
                class="flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-3 py-2"
              >
                <span class="text-slate-600">综合评分</span>
                <span class="font-semibold text-amber-700">{{ selectedHistory.score }} 分</span>
              </div>
              <div class="grid grid-cols-2 gap-3 text-xs">
                <div
                  class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-emerald-700"
                >
                  <p class="font-semibold">宜</p>
                  <p class="mt-1">{{ selectedHistory.yi.join('、') }}</p>
                </div>
                <div class="rounded-xl border border-rose-200 bg-rose-50 p-3 text-rose-700">
                  <p class="font-semibold">忌</p>
                  <p class="mt-1">{{ selectedHistory.ji.join('、') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <Transition name="fortune-share">
        <div
          v-if="sharePreviewOpen"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
          @click.self="sharePreviewOpen = false"
        >
          <div
            class="fortune-share-panel max-h-[90vh] w-full max-w-sm overflow-y-auto rounded-2xl bg-white p-5 shadow-xl"
          >
            <div class="mb-4 flex items-center justify-end">
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

    <!-- 通用分享弹窗 -->
    <ShareToPlazaModal ref="shareModalRef" />
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { getFortuneToday, getFortuneTrend, getHistoryFortune } from '@/api/fortune'
import FortuneShareReveal from './components/FortuneShareReveal.vue'
import TodayFortuneContent from './components/TodayFortuneContent.vue'
import ShareToPlazaModal from '@/components/common/ShareToPlazaModal.vue'

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
const isBoardUnlocked = ref(true)
const boardDrawPhase = ref<'idle' | 'shaking' | 'stick'>('idle')
let boardDrawTimers: ReturnType<typeof setTimeout>[] = []
const boardDrawStorageKey = ref('')

const sharePreviewOpen = ref(false)

const fortuneSharePayload = computed(() => ({
  title: fortuneData.value.title,
  score: fortuneData.value.score,
  content_main: fortuneData.value.content_main,
  content_sub: fortuneData.value.content_sub,
  yi: fortuneData.value.yi,
  ji: fortuneData.value.ji,
}))

const trendPoints = ref<Array<{ date: string; value: number }>>([])
const historyFortunes = ref<
  Array<{
    id: string
    date: string
    score: number
    title: string
    summary: string
    story: string
    linkText: string
    linkClass: string
    yi: string[]
    ji: string[]
  }>
>([])
const historyDetailOpen = ref(false)
const selectedHistory = ref<(typeof historyFortunes.value)[number] | null>(null)
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const normalizeMonthDay = (value: string) => {
  if (!value) return ''
  const raw = value.trim().replace(/\//g, '-')
  const match = raw.match(/^(\d{1,2})-(\d{1,2})$/)
  if (!match) return ''
  const month = match[1].padStart(2, '0')
  const day = match[2].padStart(2, '0')
  return `${month}-${day}`
}

const formatDateLabel = (dateObj: Date) => {
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${month}-${day}`
}

const chartDates = computed<string[]>(() => {
  const baseDate = new Date()
  const todayRaw = fortuneData.value.date || ''
  if (todayRaw.length >= 10) {
    const parsed = new Date(todayRaw.slice(0, 10))
    if (!Number.isNaN(parsed.getTime())) {
      baseDate.setTime(parsed.getTime())
    }
  }
  const days: string[] = []
  for (let i = 6; i >= 0; i -= 1) {
    const current = new Date(baseDate)
    current.setDate(baseDate.getDate() - i)
    days.push(formatDateLabel(current))
  }
  return days
})

const chartScores = computed<(number | null)[]>(() => {
  const scoreMap = new Map<string, number>()
  trendPoints.value.forEach((item) => {
    const key = normalizeMonthDay(item.date)
    const value = Number(item.value)
    if (!key || Number.isNaN(value)) return
    scoreMap.set(key, value)
  })

  return chartDates.value.map((date) => (scoreMap.has(date) ? scoreMap.get(date)! : null))
})

const chartAxisLabels = computed<string[]>(() => {
  return chartDates.value.map((date, index) => {
    const isLatest = index === chartDates.value.length - 1
    const hasScore = chartScores.value[index] !== null
    if (isLatest || hasScore) return date
    return ''
  })
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
const drawStickTitle = computed(() => {
  if (!isBoardUnlocked.value && boardDrawPhase.value === 'idle') return '上上签'
  return fortuneData.value.title || '上上签'
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
const scoreSummary = (score: number) => {
  if (score >= 85) return '状态很顺，适合推进关键事项'
  if (score >= 75) return '整体向好，保持当前节奏'
  if (score >= 65) return '平稳过渡，先稳再进'
  return '波动偏大，建议降低预期'
}
const relationByDelta = (deltaValue: number) => {
  if (deltaValue >= 3) {
    return {
      type: 'up',
      text: `↑ 比昨日提升 ${deltaValue} 分`,
      cls: 'bg-emerald-50 text-emerald-700',
      story: '昨日积累开始显效，今日气势顺承而上。',
    }
  }
  if (deltaValue <= -3) {
    return {
      type: 'down',
      text: `↓ 比昨日回落 ${Math.abs(deltaValue)} 分`,
      cls: 'bg-rose-50 text-rose-700',
      story: '昨日外扰余波未消，今日宜先稳住节奏。',
    }
  }
  return {
    type: 'flat',
    text: '→ 与昨日基本持平',
    cls: 'bg-amber-50 text-amber-700',
    story: '运势与昨日同频，适合延续既定安排。',
  }
}
const streakLabel = computed(() => {
  if (historyFortunes.value.length < 2) return '首日开盘'
  let streak = 1
  const first = historyFortunes.value[0].linkText
  const isUp = first.includes('提升')
  const isDown = first.includes('回落')
  for (let i = 0; i < historyFortunes.value.length; i += 1) {
    const text = historyFortunes.value[i].linkText
    if (isUp && text.includes('提升')) streak += i === 0 ? 0 : 1
    else if (isDown && text.includes('回落')) streak += i === 0 ? 0 : 1
    else if (!isUp && !isDown && text.includes('持平')) streak += i === 0 ? 0 : 1
    else if (i > 0) break
  }
  if (isUp) return `连涨 ${streak} 天`
  if (isDown) return `连跌 ${streak} 天`
  return `连稳 ${streak} 天`
})
const openHistoryDetail = (record: (typeof historyFortunes.value)[number]) => {
  selectedHistory.value = record
  historyDetailOpen.value = true
}
const initBoardDrawState = (fortuneDate: string) => {
  const dateKey = fortuneDate || new Date().toISOString().slice(0, 10)
  boardDrawStorageKey.value = `fortune-board-draw-played-${dateKey}`
  const played = localStorage.getItem(boardDrawStorageKey.value) === '1'
  isBoardUnlocked.value = played
  boardDrawPhase.value = played ? 'stick' : 'idle'
}

const triggerBoardDraw = () => {
  if (boardDrawPhase.value !== 'idle') return
  boardDrawTimers.forEach(clearTimeout)
  boardDrawTimers = []
  boardDrawPhase.value = 'shaking'

  boardDrawTimers.push(
    setTimeout(() => {
      boardDrawPhase.value = 'stick'
    }, 1900),
  )
  boardDrawTimers.push(
    setTimeout(() => {
      isBoardUnlocked.value = true
      if (boardDrawStorageKey.value) {
        localStorage.setItem(boardDrawStorageKey.value, '1')
      }
    }, 3200),
  )
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

// const fallbackCopy = (text: string) => {
//   navigator.clipboard
//     .writeText(text)
//     .then(() => {
//       alert('已复制到剪贴板，可以分享给朋友')
//     })
//     .catch(() => {
//       alert('复制失败，请手动复制')
//     })
// }

// const shareFortuneCard = async () => {
//   const shareText = [
//     `今日运势：${fortuneData.value.title}（${fortuneData.value.score}分）`,
//     `签文：${fortuneData.value.content_main}`,
//     `解读：${fortuneData.value.content_sub}`,
//     `宜：${fortuneData.value.yi.join('、') || '--'}`,
//     `忌：${fortuneData.value.ji.join('、') || '--'}`,
//   ].join('\n')

//   if (navigator.share) {
//     try {
//       await navigator.share({
//         title: '心运岛 · 今日运势卡',
//         text: shareText,
//       })
//       return
//     } catch (error) {
//       if ((error as Error).name === 'AbortError') return
//     }
//   }

//   fallbackCopy(shareText)
// }

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
    initBoardDrawState(fortuneData.value.date)

    const points = Array.isArray(trend.trendPoints) ? trend.trendPoints : []
    trendPoints.value = points.map((item) => ({
      date: String(item.date ?? ''),
      value: Number(item.value ?? 0),
    }))
    const historyList = Array.isArray(history.list) ? history.list : []
    if (!trendPoints.value.length) {
      trendPoints.value = [
        {
          date: formatMMDD(fortuneData.value.date),
          value: fortuneData.value.score,
        },
      ]
    }

    historyFortunes.value = historyList.map((item, index) => {
      const current = Number(item.score ?? 0)
      const next = Number(historyList[index + 1]?.score ?? current)
      const deltaFromPrev = current - next
      const relation = relationByDelta(deltaFromPrev)
      return {
        id: `${item.date || 'record'}_${index}`,
        date: formatMMDD(item.date || ''),
        score: current,
        title: item.title || '--',
        summary: scoreSummary(current),
        story: relation.story,
        linkText: relation.text,
        linkClass: relation.cls,
        yi: fortuneData.value.yi.slice(0, 1),
        ji: fortuneData.value.ji.slice(0, 1),
      }
    })
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
    grid: { left: 12, right: 22, top: 16, bottom: 16, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17,24,39,0.92)',
      borderWidth: 0,
      textStyle: { color: '#f8fafc' },
      formatter: (params: unknown) => {
        const rawPoint = Array.isArray(params) ? params[0] : params
        const point = (rawPoint || {}) as { axisValue?: string | number; value?: number }
        const score = Number(point.value)
        if (Number.isNaN(score)) return `${point.axisValue ?? '--'} · 暂无数据`
        return `${point.axisValue ?? '--'} · ${scoreToSign(score)}`
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartAxisLabels.value,
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
  [trendPoints, chartDates],
  () => {
    initChart()
  },
  { immediate: true },
)

watch(isBoardUnlocked, async (unlocked) => {
  // 抽签后图表节点才会渲染，需在下一次 DOM 更新后再初始化图表
  if (!unlocked) return
  await nextTick()
  initChart()
})

onBeforeUnmount(() => {
  boardDrawTimers.forEach(clearTimeout)
  boardDrawTimers = []
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})

// ===== 新增：通用分享弹窗逻辑 =====
const shareModalRef = ref<InstanceType<typeof ShareToPlazaModal> | null>(null)

// 打开分享编辑弹窗（用于运势）
const openShareFortuneModal = () => {
  shareModalRef.value?.open({
    type: 'fortune',
    sourceId: fortuneData.value.id,
    fortuneData: {
      title: fortuneData.value.title,
      score: fortuneData.value.score,
      content_main: fortuneData.value.content_main,
      content_sub: fortuneData.value.content_sub,
      yi: fortuneData.value.yi,
      ji: fortuneData.value.ji,
      love: fortuneData.value.love,
      career: fortuneData.value.career,
      health: fortuneData.value.health,
      wealth: fortuneData.value.wealth,
    },
  })
}
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

.board-draw {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
  max-width: 280px;
  margin: 0 auto;
}

.board-draw__stage {
  position: relative;
  width: 100%;
  max-width: 280px;
  min-height: 248px;
}

.board-draw__stick {
  position: absolute;
  left: 50%;
  top: 42%;
  z-index: 4;
  transition:
    opacity 0.45s ease,
    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.board-draw__stick[data-phase='idle'],
.board-draw__stick[data-phase='shaking'] {
  opacity: 0;
  transform: translate(-50%, 72px) scale(0.92);
  pointer-events: none;
}

.board-draw__stick[data-phase='stick'] {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.board-draw__stick-inner {
  width: 58px;
  min-height: 208px;
  padding: 28px 9px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #fdf6e8 0%, #ecdcc4 48%, #e0d0b8 100%);
  border-radius: 5px;
  border: 1px solid rgba(100, 50, 30, 0.4);
  box-shadow:
    0 14px 32px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.board-draw__stick-title {
  margin: 0;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 0.42em;
  font-size: 20px;
  font-weight: 800;
  color: #7f1d1d;
  font-family: 'Songti SC', 'Noto Serif SC', 'Microsoft YaHei', serif;
  line-height: 1.2;
}

.board-draw__bucket-wrap {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 6;
  opacity: 1;
  transition:
    opacity 0.5s ease,
    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.board-draw__bucket-wrap--hide {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.92);
  pointer-events: none;
}

.board-draw__bucket {
  transform-origin: 50% 92%;
}

.board-draw__bucket--shake {
  animation: boardBucketShake 0.16s ease-in-out infinite alternate;
}

.board-draw__tube-svg {
  display: block;
  filter: drop-shadow(0 10px 18px rgba(0, 0, 0, 0.22));
}

@keyframes boardBucketShake {
  from {
    transform: rotate(-10deg);
  }
  to {
    transform: rotate(10deg);
  }
}
</style>
