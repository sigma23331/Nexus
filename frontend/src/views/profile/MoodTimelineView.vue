<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 pb-10">
    <header
      class="sticky top-0 z-20 flex items-center gap-3 border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur"
    >
      <button
        type="button"
        class="rounded-full p-2 text-slate-600 hover:bg-slate-100"
        aria-label="返回"
        @click="goBack"
      >
        <span class="text-lg">←</span>
      </button>
      <div class="min-w-0 flex-1">
        <h1 class="text-base font-bold text-slate-900">心情时间轴</h1>
        <p class="truncate text-xs text-slate-500">按时间回看情绪日记</p>
      </div>
    </header>

    <main class="px-4 pt-4">
      <div class="mb-4 flex flex-wrap items-end gap-3">
        <label class="flex flex-col gap-1 text-xs text-slate-600">
          <span>筛选月份</span>
          <input
            v-model="yearMonth"
            type="month"
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-200"
            @change="onMonthChange"
          />
        </label>
        <button
          type="button"
          class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50"
          @click="clearMonth"
        >
          全部
        </button>
      </div>

      <div
        v-if="loadError"
        class="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-3 text-xs text-rose-700"
      >
        <p>{{ loadError }}</p>
        <div class="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            class="rounded-lg bg-rose-600 px-3 py-2 font-semibold text-white hover:bg-rose-700"
            :disabled="loading"
            @click="reload"
          >
            {{ loading ? '加载中…' : '重试' }}
          </button>
          <button
            v-if="localFallbackItems.length"
            type="button"
            class="rounded-lg border border-rose-300 bg-white px-3 py-2 font-semibold text-rose-800 hover:bg-rose-50"
            @click="useLocalOnly"
          >
            仅看本机 {{ localFallbackItems.length }} 条
          </button>
        </div>
      </div>

      <div
        v-if="usingLocalOnly && localFallbackItems.length"
        class="mb-3 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900"
      >
        当前展示本机暂存的日记（未同步到服务器或接口不可用）。
        <button type="button" class="ml-1 font-semibold underline" @click="reload">
          重新加载线上
        </button>
      </div>

      <div v-if="loading && !items.length" class="space-y-3">
        <div v-for="n in 5" :key="n" class="h-24 animate-pulse rounded-2xl bg-slate-200/80" />
      </div>

      <template v-else-if="!items.length">
        <div
          class="rounded-2xl border border-slate-200 bg-white px-4 py-10 text-center text-sm text-slate-500"
        >
          <p>暂无日记记录</p>
          <p class="mt-2 text-xs text-slate-400">
            在「我的」里写「今日心情」，或连接后端保存后会显示在这里。
          </p>
          <button
            v-if="localFallbackItems.length"
            type="button"
            class="mt-4 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
            @click="useLocalOnly"
          >
            查看本机已写的 {{ localFallbackItems.length }} 条
          </button>
        </div>
      </template>

      <div v-else class="relative pl-2">
        <div
          class="pointer-events-none absolute left-[19px] top-3 bottom-3 w-px bg-gradient-to-b from-violet-200 via-violet-300 to-slate-200"
          aria-hidden="true"
        />
        <ul class="space-y-0">
          <li
            v-for="(row, idx) in items"
            :key="row.id + idx"
            class="relative flex gap-3 pb-6 last:pb-2"
          >
            <div
              class="relative z-10 mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 border-white bg-white text-xl shadow-md ring-2 ring-violet-100"
            >
              {{ moodEmoji(row.moodTag) }}
            </div>
            <button
              type="button"
              class="min-w-0 flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left shadow-sm transition hover:border-violet-200 hover:shadow-md"
              @click="openDetail(row)"
            >
              <div class="flex flex-wrap items-baseline justify-between gap-2">
                <span class="text-sm font-semibold text-slate-900">{{ row.date }}</span>
                <span class="text-xs text-slate-500">{{ weekdayCn(row.weekday, row.date) }}</span>
              </div>
              <p class="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-600">
                {{ row.snippet || '（无摘要）' }}
              </p>
              <span
                v-if="row.localOnly"
                class="mt-2 inline-block rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-800"
              >
                本机
              </span>
            </button>
          </li>
        </ul>

        <div v-if="hasMore && !usingLocalOnly" class="mt-4 pb-4 text-center">
          <button
            type="button"
            class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            :disabled="loadingMore"
            @click="loadMore"
          >
            {{ loadingMore ? '加载中…' : '加载更多' }}
          </button>
        </div>
      </div>
    </main>

    <DiaryDetailModal ref="detailRef" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getDiaryEntry, getDiaryTimeline } from '@/api/diary'
import DiaryDetailModal from '@/components/business/DiaryDetailModal.vue'
import type { DiaryTimelineItem } from '@/types/models'
import { getAllDiaries, getDiaryByDate } from '@/utils/storage'

const router = useRouter()

const items = ref<DiaryTimelineItem[]>([])
const total = ref(0)
const page = ref(1)
const limit = 20
const loading = ref(false)
const loadingMore = ref(false)
const loadError = ref('')
const yearMonth = ref<string>('')
const usingLocalOnly = ref(false)

const detailRef = ref<InstanceType<typeof DiaryDetailModal> | null>(null)

const EN_WEEK = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
] as const
const CN_WEEK = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const moodEmoji = (tag: string) => {
  const m: Record<string, string> = {
    happy: '😄',
    calm: '😌',
    tired: '😴',
    anxious: '😟',
    angry: '😡',
    sad: '😢',
  }
  return m[tag] ?? '📝'
}

const weekdayCn = (weekday: string, isoDate: string) => {
  const i = EN_WEEK.indexOf(weekday as (typeof EN_WEEK)[number])
  if (i >= 0) return CN_WEEK[i]
  const d = new Date(isoDate + 'T12:00:00')
  if (Number.isNaN(d.getTime())) return weekday
  return CN_WEEK[(d.getDay() + 6) % 7]
}

const localFallbackItems = computed(() => {
  const all = getAllDiaries()
  const ym = yearMonth.value
  const filtered = ym ? all.filter((e) => e.date.startsWith(`${ym}-`)) : [...all]
  return filtered
    .sort((a, b) => b.date.localeCompare(a.date))
    .map((e) => ({
      id: `local:${e.date}`,
      date: e.date,
      weekday: '',
      moodTag: e.moodTag,
      snippet: e.content.length > 40 ? `${e.content.slice(0, 40)}…` : e.content,
      localOnly: true as const,
    }))
})

/** 是否还有服务端分页（与首屏合并的本机条数无关，只看接口 totalDays） */
const hasMore = computed(() => {
  if (usingLocalOnly.value) return false
  return page.value * limit < total.value
})

/** 第一页：把本机有、但当前接口列表里没有的日期补在时间轴上 */
function mergeFirstPage(apiList: DiaryTimelineItem[]): DiaryTimelineItem[] {
  const dates = new Set(apiList.map((r) => r.date))
  const extra = localFallbackItems.value.filter((l) => !dates.has(l.date))
  return [...apiList, ...extra].sort((a, b) => b.date.localeCompare(a.date))
}

async function fetchPage(append: boolean) {
  const ym = yearMonth.value || null
  if (!append) {
    loadError.value = ''
    loading.value = true
  } else {
    loadingMore.value = true
  }
  try {
    usingLocalOnly.value = false
    const res = await getDiaryTimeline({
      page: page.value,
      limit,
      yearMonth: ym,
    })
    total.value = res.totalDays
    if (append) {
      const seen = new Set(items.value.map((x) => x.id))
      for (const row of res.list) {
        if (!seen.has(row.id)) {
          items.value.push(row)
          seen.add(row.id)
        }
      }
    } else {
      items.value = mergeFirstPage(res.list)
    }
  } catch (e) {
    if (!append) {
      loadError.value = e instanceof Error ? e.message : '加载失败'
      items.value = []
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function onMonthChange() {
  page.value = 1
  void fetchPage(false)
}

function clearMonth() {
  yearMonth.value = ''
  page.value = 1
  void fetchPage(false)
}

async function loadMore() {
  if (!hasMore.value || loadingMore.value) return
  page.value += 1
  await fetchPage(true)
}

async function reload() {
  page.value = 1
  usingLocalOnly.value = false
  await fetchPage(false)
}

function useLocalOnly() {
  usingLocalOnly.value = true
  loadError.value = ''
  items.value = localFallbackItems.value.map((x) => ({ ...x }))
  total.value = items.value.length
}

async function openDetail(row: DiaryTimelineItem) {
  if (row.localOnly) {
    const d = getDiaryByDate(row.date)
    detailRef.value?.open({
      date: row.date,
      moodTag: d?.moodTag ?? row.moodTag,
      content: d?.content ?? row.snippet,
    })
    return
  }
  try {
    const detail = await getDiaryEntry(row.id)
    const dateOnly = detail.createdAt ? detail.createdAt.slice(0, 10) : row.date
    detailRef.value?.open({
      date: dateOnly,
      moodTag: detail.moodTag,
      content: detail.content,
    })
  } catch {
    detailRef.value?.open({
      date: row.date,
      moodTag: row.moodTag,
      content: row.snippet,
    })
  }
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.push({ name: 'profile' })
}

onMounted(() => {
  void fetchPage(false)
})
</script>
