<template>
  <div class="space-y-4">
    <!-- 月份选择器 -->
    <div class="flex items-center justify-between">
      <button
        @click="prevMonth"
        class="p-2 rounded-full hover:bg-slate-100 transition"
        title="上个月"
      >
        ◀
      </button>
      <div class="relative" ref="monthSelectorRef">
        <button
          @click="toggleMonthSelector"
          class="font-semibold text-slate-800 px-4 py-2 rounded-lg hover:bg-slate-100 transition flex items-center gap-1"
        >
          {{ currentYearMonth }}
          <span class="text-sm">▼</span>
        </button>
        <div
          v-if="showMonthSelector"
          class="absolute left-0 right-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto"
        >
          <div
            v-for="opt in availableMonths"
            :key="opt.value"
            @click="selectMonth(opt.value)"
            class="px-4 py-2 text-sm hover:bg-slate-100 cursor-pointer text-slate-700"
            :class="{ 'bg-purple-50 text-purple-600': opt.value === selectedYearMonth }"
          >
            {{ opt.label }}
          </div>
        </div>
      </div>
      <button
        @click="nextMonth"
        :disabled="isNextMonthDisabled"
        class="p-2 rounded-full hover:bg-slate-100 transition disabled:opacity-30"
        title="下个月"
      >
        ▶
      </button>
    </div>

    <!-- 星期标题 -->
    <div class="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500">
      <div v-for="weekday in weekdays" :key="weekday">{{ weekday }}</div>
    </div>

    <!-- 日历网格 -->
    <div class="grid grid-cols-7 gap-1">
      <div
        v-for="(day, index) in calendarDays"
        :key="index"
        class="aspect-square flex flex-col items-center justify-center rounded-lg transition"
        :class="{
          'opacity-40': !day.isCurrentMonth || day.isFuture,
          'bg-purple-50 ring-1 ring-purple-200': day.isToday,
          'cursor-pointer hover:bg-slate-50': day.isCurrentMonth && !day.isFuture,
          'cursor-default': !day.isCurrentMonth || day.isFuture,
        }"
        @click="day.isCurrentMonth && !day.isFuture && showDayDetail(day)"
      >
        <span
          class="text-sm font-medium"
          :class="day.isToday ? 'text-purple-600' : 'text-slate-700'"
        >
          {{ day.dayNumber }}
        </span>
        <span class="text-lg mt-0.5">{{ getMoodEmoji(day.moodTag) }}</span>
      </div>
    </div>

    <!-- 图例 -->
    <div class="flex flex-wrap gap-3 justify-center text-xs text-slate-500 pt-2">
      <span v-for="item in moodLegend" :key="item.value" class="flex items-center gap-1">
        <span class="text-base">{{ item.emoji }}</span>
        <span>{{ item.label }}</span>
      </span>
      <span class="flex items-center gap-1">
        <span class="text-base">⚪️</span>
        <span>未记录</span>
      </span>
    </div>

    <!-- 弹窗 -->
    <DiaryDetailModal ref="diaryModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import DiaryDetailModal from './DiaryDetailModal.vue'
import { loadMonthDiaries, type LocalDiary } from '@/utils/diaryService'
import { getDiaryEntry } from '@/api/diary'

// 心情映射
const moodEmoji: Record<string, string> = {
  happy: '😄',
  calm: '😌',
  tired: '😴',
  anxious: '😟',
  angry: '😡',
  sad: '😢',
  null: '⚪️',
}
const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const moodLegend = [
  { emoji: '😄', value: 'happy', label: '开心' },
  { emoji: '😌', value: 'calm', label: '平静' },
  { emoji: '😴', value: 'tired', label: '困倦' },
  { emoji: '😟', value: 'anxious', label: '焦虑' },
  { emoji: '😡', value: 'angry', label: '生气' },
  { emoji: '😢', value: 'sad', label: '难过' },
]

// 当前真实时间限制（服务器时间此处用本地时间模拟）
const today = new Date()
const maxYear = today.getFullYear()
const maxMonth = today.getMonth()
// 今天的日期字符串 YYYY-MM-DD
const todayStr = today.toISOString().slice(0, 10)

const currentYear = ref(today.getFullYear())
const currentMonth = ref(today.getMonth())
const isNextMonthDisabled = computed(
  () => currentYear.value === maxYear && currentMonth.value === maxMonth,
)

// 日记数据
const diaryEntries = ref<LocalDiary[]>([])

// 日历数据类型
interface CalendarDay {
  date: string
  dayNumber: number
  isCurrentMonth: boolean
  isToday: boolean
  isFuture: boolean // 是否未来日期
  moodTag: string | null
  content: string
}

// 加载日记（本地优先，后台同步）
async function loadDiaries() {
  const year = currentYear.value
  const month = currentMonth.value + 1
  const entries = await loadMonthDiaries(year, month)
  diaryEntries.value = entries
}

// 监听年月变化
watch([currentYear, currentMonth], () => {
  loadDiaries()
})

// 监听全局更新事件（当远程数据合并完成后触发）
const handleDiariesUpdated = (event: Event) => {
  const customEvent = event as CustomEvent<{ year: number; month: number }>
  const { year, month } = customEvent.detail
  if (year === currentYear.value && month === currentMonth.value + 1) {
    loadDiaries()
  }
}

onMounted(() => {
  loadDiaries()
  window.addEventListener('diaries-updated', handleDiariesUpdated)
  if (
    currentYear.value > maxYear ||
    (currentYear.value === maxYear && currentMonth.value > maxMonth)
  ) {
    currentYear.value = maxYear
    currentMonth.value = maxMonth
    selectedYearMonth.value = `${maxYear}-${String(maxMonth + 1).padStart(2, '0')}`
  }
})

onUnmounted(() => {
  window.removeEventListener('diaries-updated', handleDiariesUpdated)
})

// 月份选择器逻辑
const availableMonths = computed(() => {
  const months: { value: string; label: string }[] = []
  const startYear = 2026
  const startMonth = 0
  for (let y = startYear; y <= maxYear; y++) {
    const endMonth = y === maxYear ? maxMonth : 11
    for (let m = 0; m <= endMonth; m++) {
      if (y === startYear && m < startMonth) continue
      months.push({
        value: `${y}-${String(m + 1).padStart(2, '0')}`,
        label: `${y}/${String(m + 1).padStart(2, '0')}`, // 格式改为 YYYY/MM
      })
    }
  }
  return months
})
const showMonthSelector = ref(false)
const monthSelectorRef = ref<HTMLElement | null>(null)
const selectedYearMonth = ref(
  `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}`,
)

const toggleMonthSelector = () => {
  showMonthSelector.value = !showMonthSelector.value
}
const selectMonth = (value: string) => {
  const [year, month] = value.split('-')
  currentYear.value = parseInt(year)
  currentMonth.value = parseInt(month) - 1
  selectedYearMonth.value = value
  showMonthSelector.value = false
}
const handleClickOutside = (event: MouseEvent) => {
  if (monthSelectorRef.value && !monthSelectorRef.value.contains(event.target as Node)) {
    showMonthSelector.value = false
  }
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

const prevMonth = () => {
  if (currentYear.value === 2026 && currentMonth.value === 0) return
  let newYear = currentYear.value,
    newMonth = currentMonth.value - 1
  if (newMonth < 0) {
    newMonth = 11
    newYear--
  }
  currentYear.value = newYear
  currentMonth.value = newMonth
  selectedYearMonth.value = `${newYear}-${String(newMonth + 1).padStart(2, '0')}`
}
const nextMonth = () => {
  if (isNextMonthDisabled.value) return
  let newYear = currentYear.value,
    newMonth = currentMonth.value + 1
  if (newMonth > 11) {
    newMonth = 0
    newYear++
  }
  currentYear.value = newYear
  currentMonth.value = newMonth
  selectedYearMonth.value = `${newYear}-${String(newMonth + 1).padStart(2, '0')}`
}

// 生成日历网格（使用 diaryEntries 数据）
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value

  const firstDayOfWeek = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  const prevMonthDate = new Date(year, month, 0)
  const prevYear = prevMonthDate.getFullYear()
  const prevMonth = prevMonthDate.getMonth()
  const daysInPrevMonth = new Date(prevYear, prevMonth + 1, 0).getDate()

  const diaryMap = new Map<string, LocalDiary>()
  diaryEntries.value.forEach((entry) => {
    diaryMap.set(entry.date, entry)
  })

  const fullDays: CalendarDay[] = []

  // 上月补位
  for (let i = firstDayOfWeek; i > 0; i--) {
    const dayNum = daysInPrevMonth - i + 1
    const dateStr = `${prevYear}-${String(prevMonth + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`
    fullDays.push({
      date: dateStr,
      dayNumber: dayNum,
      isCurrentMonth: false,
      isToday: false,
      isFuture: dateStr > todayStr,
      moodTag: null,
      content: '',
    })
  }

  // 当月日期
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    const diary = diaryMap.get(dateStr)
    fullDays.push({
      date: dateStr,
      dayNumber: d,
      isCurrentMonth: true,
      isToday: dateStr === todayStr,
      isFuture: dateStr > todayStr,
      moodTag: diary?.moodTag || null,
      content: diary?.content || '',
    })
  }

  // 下月补位
  let nextMonthYear = year
  let nextMonth = month + 1
  if (nextMonth > 11) {
    nextMonth = 0
    nextMonthYear++
  }
  let extra = 7 - (fullDays.length % 7)
  if (extra === 7) extra = 0
  for (let i = 1; i <= extra; i++) {
    const dateStr = `${nextMonthYear}-${String(nextMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    fullDays.push({
      date: dateStr,
      dayNumber: i,
      isCurrentMonth: false,
      isToday: false,
      isFuture: dateStr > todayStr,
      moodTag: null,
      content: '',
    })
  }

  // 去除全为下月的尾行
  const weeks: CalendarDay[][] = []
  for (let i = 0; i < fullDays.length; i += 7) {
    weeks.push(fullDays.slice(i, i + 7))
  }
  const lastWeek = weeks[weeks.length - 1]
  if (lastWeek && lastWeek.every((day) => !day.isCurrentMonth)) {
    weeks.pop()
  }
  return weeks.flat()
})

const currentYearMonth = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value + 1
  return `${year}/${String(month).padStart(2, '0')}`
})
const getMoodEmoji = (tag: string | null) => moodEmoji[tag ?? 'null']

// 弹窗相关
const diaryModalRef = ref<InstanceType<typeof DiaryDetailModal> | null>(null)

// 点击日期显示详情（未来日期不可点击，已由模板控制）
const showDayDetail = async (day: CalendarDay) => {
  if (!day.isCurrentMonth || day.isFuture) return
  let content = day.content
  const entry = diaryEntries.value.find((e) => e.date === day.date)
  // 如果本地内容为空且有服务端ID，尝试拉取完整内容
  if (entry && entry.synced && entry.serverId && (!content || content === '')) {
    try {
      const detail = await getDiaryEntry(entry.serverId)
      content = detail.content
    } catch (err) {
      console.warn('获取日记详情失败', err)
    }
  }
  diaryModalRef.value?.open({
    date: day.date,
    moodTag: day.moodTag,
    content: content,
  })
}

// 外部刷新方法
const refresh = () => {
  loadDiaries()
}
defineExpose({ refresh })
</script>
