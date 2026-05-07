<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 顶部导航栏 -->
    <div class="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b border-slate-200">
      <div class="flex items-center px-4 py-3">
        <button @click="router.back()" class="p-2 -ml-2 rounded-full hover:bg-slate-100">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
        <h1 class="flex-1 text-center text-lg font-semibold">历史运势记录</h1>
        <div class="w-8"></div>
      </div>
    </div>

    <!-- 月份筛选栏 -->
    <div
      class="sticky top-[57px] z-10 bg-white/90 backdrop-blur-sm px-4 py-3 border-b border-slate-100"
    >
      <div class="flex items-center gap-2 flex-wrap">
        <button
          @click="selectedMonth = ''"
          :class="[
            'rounded-full px-4 py-1.5 text-xs font-medium transition',
            selectedMonth === ''
              ? 'bg-purple-600 text-white'
              : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50',
          ]"
        >
          全部
        </button>
        <div class="relative" ref="monthSelectorRef">
          <button
            @click="toggleMonthSelector"
            :class="[
              'rounded-full px-4 py-1.5 text-xs font-medium transition flex items-center gap-1',
              selectedMonth !== ''
                ? 'bg-purple-600 text-white'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50',
            ]"
          >
            {{ selectedMonthDisplay || '选择月份' }}
            <span class="text-xs">▼</span>
          </button>
          <div
            v-if="showMonthSelector"
            class="absolute left-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto w-32"
          >
            <div
              v-for="opt in availableMonths"
              :key="opt.value"
              @click="selectMonth(opt.value)"
              class="px-3 py-2 text-xs hover:bg-slate-100 cursor-pointer text-slate-700"
              :class="{ 'bg-purple-50 text-purple-600': opt.value === selectedMonth }"
            >
              {{ opt.label }}
            </div>
          </div>
        </div>
        <span class="text-xs text-slate-500 ml-auto">共 {{ filteredTotal }} 条</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && list.length === 0" class="flex justify-center items-center h-64">
      <div class="text-purple-600">加载中...</div>
    </div>

    <!-- 数据列表（采用潮流卡片样式） -->
    <div v-else-if="filteredList.length > 0" class="space-y-3 p-4">
      <article
        v-for="item in filteredList"
        :key="item.date"
        class="cursor-pointer rounded-2xl border border-amber-100 bg-gradient-to-r from-amber-50/60 to-white p-4 shadow-sm transition hover:shadow-md"
        @click="openDetail(item)"
      >
        <div class="mb-3 flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-slate-900">
              {{ formatDate(item.date) }} · {{ item.title }}
            </p>
            <p class="text-xs text-slate-500">{{ summaryText(item) }}</p>
          </div>
          <span
            class="rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="scoreLevelClass(item.score)"
          >
            {{ item.score }} 分
          </span>
        </div>
        <div class="flex gap-2 text-xs">
          <span
            class="inline-flex items-center rounded-full bg-emerald-50 px-2 py-1 text-emerald-700"
          >
            宜：{{ item.yi?.[0] || '--' }}
          </span>
          <span class="inline-flex items-center rounded-full bg-rose-50 px-2 py-1 text-rose-700">
            忌：{{ item.ji?.[0] || '--' }}
          </span>
        </div>
        <div class="mt-2 flex items-center justify-between text-right text-[11px] text-slate-400">
          <span class="text-amber-600">点击查看详情</span>
          <span>{{ getRelativeTime(item.date) }}</span>
        </div>
      </article>

      <!-- 分页加载更多 -->
      <div class="py-4 text-center">
        <button
          v-if="hasMore && selectedMonth === ''"
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-2 text-sm text-purple-600 bg-purple-50 rounded-full hover:bg-purple-100 transition disabled:opacity-50"
        >
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
        <!-- 非筛选模式且无更多数据时显示“已经到底了” -->
        <p v-else-if="!selectedMonth && !hasMore" class="text-xs text-slate-400">
          —— 已经到底了 ——
        </p>
        <!-- 筛选模式下直接显示“已经到底了”（因为数据已全部展示） -->
        <p v-else-if="selectedMonth" class="text-xs text-slate-400">—— 已经到底了 ——</p>
      </div>
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="!loading && filteredList.length === 0"
      class="flex flex-col items-center justify-center h-64 text-slate-400"
    >
      <span class="text-4xl mb-2">📭</span>
      <p>{{ selectedMonth ? '该月份没有运势记录' : '暂无历史运势记录' }}</p>
    </div>

    <!-- 回到顶部按钮 -->
    <transition name="fade-scale">
      <button
        v-show="showBackToTop"
        @click="scrollToTop"
        class="fixed bottom-20 right-5 z-30 flex h-10 w-10 items-center justify-center rounded-full bg-purple-600 text-white shadow-lg hover:bg-purple-700 transition-all duration-200 focus:outline-none"
        aria-label="回到顶部"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </button>
    </transition>

    <!-- 详情弹窗 -->
    <Teleport to="body">
      <Transition name="fortune-share">
        <div
          v-if="detailOpen && selectedItem"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/55 p-4 backdrop-blur-sm"
          @click.self="detailOpen = false"
        >
          <div
            class="w-full max-w-sm max-h-[85vh] overflow-y-auto rounded-2xl bg-white p-5 shadow-xl"
          >
            <div class="mb-3 flex items-center justify-between">
              <h3 class="text-base font-semibold text-slate-900">历史运势详情</h3>
              <button
                type="button"
                class="rounded-full px-2 py-1 text-xs text-slate-500 hover:bg-slate-100"
                @click="detailOpen = false"
              >
                关闭
              </button>
            </div>
            <div class="space-y-3 text-sm">
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs text-slate-500">{{ formatDate(selectedItem.date) }}</p>
                <p class="mt-1 text-base font-semibold text-slate-900">{{ selectedItem.title }}</p>
                <p class="mt-1 text-slate-700">{{ selectedItem.content_main || '—' }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ selectedItem.content_sub || '' }}</p>
              </div>
              <div
                class="flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-3 py-2"
              >
                <span class="text-slate-600">综合评分</span>
                <span class="font-semibold text-amber-700">{{ selectedItem.score }} 分</span>
              </div>
              <div class="grid grid-cols-2 gap-3 text-xs">
                <div
                  class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-emerald-700"
                >
                  <p class="font-semibold">宜</p>
                  <p class="mt-1">{{ (selectedItem.yi || []).join('、') || '--' }}</p>
                </div>
                <div class="rounded-xl border border-rose-200 bg-rose-50 p-3 text-rose-700">
                  <p class="font-semibold">忌</p>
                  <p class="mt-1">{{ (selectedItem.ji || []).join('、') || '--' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryFortune } from '@/api/fortune'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

// 扩展后端返回的类型
export interface ExtendedHistoryFortuneItem {
  date: string
  score: number
  title: string
  content_main?: string
  content_sub?: string
  yi?: string[]
  ji?: string[]
}

const router = useRouter()

// 数据状态
const list = ref<ExtendedHistoryFortuneItem[]>([])
const total = ref(0)
const page = ref(1)
const limit = 12
const loading = ref(false)
const loadingMore = ref(false)
const hasMore = ref(true)

// 筛选相关
const selectedMonth = ref('')
const showMonthSelector = ref(false)
const monthSelectorRef = ref<HTMLElement | null>(null)

// 回到顶部
const showBackToTop = ref(false)

// 详情弹窗
const detailOpen = ref(false)
const selectedItem = ref<ExtendedHistoryFortuneItem | null>(null)

// 计算可选的月份列表（基于当前已加载的全部数据）
const availableMonths = computed(() => {
  const monthsSet = new Set<string>()
  list.value.forEach((item) => {
    const month = item.date.slice(0, 7) // YYYY-MM
    monthsSet.add(month)
  })
  return Array.from(monthsSet)
    .sort((a, b) => b.localeCompare(a))
    .map((value) => ({ value, label: value.replace('-', '年') + '月' }))
})

const selectedMonthDisplay = computed(() => {
  if (!selectedMonth.value) return ''
  return selectedMonth.value.replace('-', '年') + '月'
})

const filteredList = computed(() => {
  if (!selectedMonth.value) return list.value
  return list.value.filter((item) => item.date.startsWith(selectedMonth.value))
})

const filteredTotal = computed(() => filteredList.value.length)

const formatDate = (isoDate: string) => {
  if (!isoDate) return '--'
  const parts = isoDate.split('-')
  if (parts.length === 3) return `${parts[1]}-${parts[2]}`
  return isoDate
}

const getRelativeTime = (isoDate: string) => {
  return dayjs(isoDate).fromNow()
}

const scoreLevelClass = (score: number) => {
  if (score >= 85) return 'bg-emerald-50 text-emerald-700'
  if (score >= 75) return 'bg-blue-50 text-blue-700'
  if (score >= 65) return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-700'
}

const summaryText = (item: ExtendedHistoryFortuneItem) => {
  if (item.score >= 85) return '状态很顺，适合推进关键事项'
  if (item.score >= 75) return '整体向好，保持当前节奏'
  if (item.score >= 65) return '平稳过渡，先稳再进'
  return '波动偏大，建议降低预期'
}

const loadHistory = async (reset = true) => {
  if (reset) {
    page.value = 1
    list.value = []
    hasMore.value = true
    loading.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const res = await getHistoryFortune(page.value, limit)
    total.value = res.total
    const newList = res.list as ExtendedHistoryFortuneItem[]
    if (reset) {
      list.value = newList
    } else {
      list.value.push(...newList)
    }
    hasMore.value = list.value.length < total.value
  } catch (error) {
    console.error('加载历史运势失败', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  if (loadingMore.value || !hasMore.value || selectedMonth.value) return
  page.value++
  loadHistory(false)
}

const refresh = () => {
  loadHistory(true)
}

const openDetail = (item: ExtendedHistoryFortuneItem) => {
  selectedItem.value = item
  detailOpen.value = true
}

// 月份选择器逻辑
const toggleMonthSelector = () => {
  showMonthSelector.value = !showMonthSelector.value
}
const selectMonth = (value: string) => {
  selectedMonth.value = value
  showMonthSelector.value = false
}
const handleClickOutside = (event: MouseEvent) => {
  if (monthSelectorRef.value && !monthSelectorRef.value.contains(event.target as Node)) {
    showMonthSelector.value = false
  }
}

// 滚动监听
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 300
}
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  refresh()
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll)
})

onActivated(() => {
  refresh()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.2s ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

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
