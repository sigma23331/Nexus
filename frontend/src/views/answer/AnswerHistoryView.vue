<template>
  <div class="min-h-screen text-slate-900 pb-8">
    <header
      class="sticky top-0 z-20 flex items-center gap-3 border-b border-purple-200 bg-white/90 px-4 py-3 backdrop-blur"
    >
      <button
        type="button"
        class="rounded-full p-2 text-slate-600"
        aria-label="返回"
        @click="goBack"
      >
        <span class="text-lg">←</span>
      </button>
      <div class="min-w-0 flex-1">
        <h1 class="text-lg font-bold text-slate-900">过往答案</h1>
      </div>
    </header>

    <main class="px-4 pt-4">
      <!-- 月份筛选栏 -->
      <div class="mb-4 flex items-center gap-2 flex-wrap">
        <button
          @click="selectedMonth = ''"
          :class="[
            'rounded-full px-4 py-1.5 text-xs font-medium transition',
            selectedMonth === ''
              ? 'bg-indigo-400 text-white'
              : 'bg-white border border-purple-300 text-slate-700 hover:bg-purple-100',
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
                ? 'bg-indigo-400 text-white'
                : 'bg-white border border-purple-300 text-slate-700 hover:bg-purple-100',
            ]"
          >
            {{ selectedMonthDisplay || '选择月份' }}
            <span class="text-xs">▼</span>
          </button>
          <div
            v-if="showMonthSelector"
            class="absolute left-0 top-full mt-1 bg-white border border-purple-300 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto w-32"
          >
            <div
              v-for="opt in availableMonths"
              :key="opt.value"
              @click="selectMonth(opt.value)"
              class="px-3 py-2 text-xs hover:bg-purple-100 cursor-pointer text-slate-700"
              :class="{ 'bg-purple-100 text-purple-700': opt.value === selectedMonth }"
            >
              {{ opt.label }}
            </div>
          </div>
        </div>
        <span class="text-xs text-slate-500 ml-auto">共 {{ filteredTotal }} 条</span>
      </div>

      <!-- 加载错误状态 -->
      <div
        v-if="loadError"
        class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-3 text-xs text-rose-700"
      >
        <p>{{ loadError }}</p>
        <p class="mt-2 text-[11px] text-rose-600/90">
          这是接口未成功返回时的提示，与「真的没有记录」不同。常见原因：本地后端未启动、路由未实现、数据库异常等。
        </p>
        <button
          type="button"
          class="mt-3 w-full rounded-lg bg-rose-600 py-2 text-xs font-semibold text-white hover:bg-rose-700"
          :disabled="loading"
          @click="retryFirstPage"
        >
          {{ loading ? '加载中…' : '重试' }}
        </button>
      </div>

      <template v-else>
        <!-- 加载占位 -->
        <div v-if="loading && !filteredList.length" class="space-y-3">
          <div v-for="n in 4" :key="n" class="h-20 animate-pulse rounded-xl bg-purple-200/70" />
        </div>

        <!-- 空状态 -->
        <div
          v-else-if="!filteredList.length"
          class="rounded-2xl border border-dashed border-purple-300 bg-white py-12 text-center text-sm text-slate-500"
        >
          {{ selectedMonth ? '该月份没有答案记录' : '暂无历史记录，去提问吧' }}
        </div>

        <!-- 列表 -->
        <ul v-else class="space-y-3">
          <li
            v-for="item in filteredList"
            :key="item.id"
            class="rounded-2xl bg-gradient-to-br from-indigo-100/80 via-white to-purple-100/80 p-4 shadow-sm cursor-pointer transition hover:shadow-md hover:from-indigo-200/80 hover:to-purple-200/80 border border-purple-200"
            @click="openDetail(item)"
          >
            <div class="flex items-start justify-between gap-2">
              <p class="text-sm font-medium text-slate-800 line-clamp-2">问：{{ item.question }}</p>
              <!-- 星标收藏按钮 -->
              <button
                @click.stop="toggleFavorite(item)"
                class="shrink-0 p-1 transition hover:scale-110"
                :class="item.isFavorited ? 'text-amber-500' : 'text-slate-400'"
                aria-label="收藏"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-5 h-5"
                  :fill="item.isFavorited ? 'currentColor' : 'none'"
                  :stroke="item.isFavorited ? 'none' : 'currentColor'"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polygon
                    points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                  />
                </svg>
              </button>
            </div>
            <p class="mt-1 text-[11px] text-slate-600 line-clamp-2">「{{ item.answerText }}」</p>
            <p class="mt-2 text-[10px] text-slate-500">{{ formatTime(item.createdAt) }}</p>
          </li>
        </ul>
        <div v-if="!selectedMonth && filteredList.length > 0" class="py-4 text-center">
          <button
            v-if="hasMore"
            type="button"
            class="rounded-full bg-purple-50 px-6 py-2 text-sm font-semibold text-purple-600 transition hover:bg-purple-100 disabled:opacity-50"
            :disabled="loadingMore"
            @click="loadMore"
          >
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </button>
          <p v-else class="text-xs text-slate-400">—— 已经到底了 ——</p>
        </div>
      </template>
    </main>

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
    <AnswerDetailModal ref="answerDetailModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import {
  fetchAndSyncHistory,
  getLocalAnswerList,
  updateLocalFavoriteStatus,
} from '@/utils/answerService'
import { favoriteAnswer, type AnswerHistoryItem } from '@/api/answer'
import AnswerDetailModal from './components/AnswerDetailModal.vue'

const router = useRouter()

// 数据状态
const allAnswers = ref<AnswerHistoryItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 5
const loading = ref(false)
const loadingMore = ref(false)
const loadError = ref('')
const hasMore = ref(true)

// 筛选相关
const selectedMonth = ref('')
const showMonthSelector = ref(false)
const monthSelectorRef = ref<HTMLElement | null>(null)

// 回到顶部
const showBackToTop = ref(false)

// 计算可选的月份列表
const availableMonths = computed(() => {
  const monthsSet = new Set<string>()
  allAnswers.value.forEach((item) => {
    const month = item.createdAt.slice(0, 7)
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
  if (!selectedMonth.value) return allAnswers.value
  return allAnswers.value.filter((item) => item.createdAt.startsWith(selectedMonth.value))
})

const filteredTotal = computed(() => filteredList.value.length)

function mergeLoadedAnswers(items: AnswerHistoryItem[]) {
  const merged = new Map<string, AnswerHistoryItem>()
  allAnswers.value.forEach((item) => merged.set(item.id, item))
  items.forEach((item) => merged.set(item.id, item))
  allAnswers.value = Array.from(merged.values()).sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
  )
}

// 首屏只加载 5 条，剩余记录通过“加载更多”分页追加
async function loadAnswerPage(reset = true) {
  if (reset) {
    page.value = 1
    allAnswers.value = []
    hasMore.value = true
    loading.value = true
  } else {
    loadingMore.value = true
  }
  loadError.value = ''
  try {
    const res = await fetchAndSyncHistory(page.value, pageSize)
    total.value = res.total
    if (reset) {
      allAnswers.value = res.list
    } else {
      mergeLoadedAnswers(res.list)
    }
    hasMore.value = allAnswers.value.length < total.value
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : '加载失败，请稍后重试'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  if (loadingMore.value || loading.value || !hasMore.value || selectedMonth.value) return
  page.value += 1
  loadAnswerPage(false)
}

// 监听全局数据更新
function handleAnswersUpdated() {
  allAnswers.value = getLocalAnswerList().slice(0, page.value * pageSize)
  hasMore.value = allAnswers.value.length < total.value
}

// 月份选择器
function toggleMonthSelector() {
  showMonthSelector.value = !showMonthSelector.value
}
function selectMonth(value: string) {
  selectedMonth.value = value
  showMonthSelector.value = false
}
function handleClickOutside(event: MouseEvent) {
  if (monthSelectorRef.value && !monthSelectorRef.value.contains(event.target as Node)) {
    showMonthSelector.value = false
  }
}

// 滚动
function handleScroll() {
  showBackToTop.value = window.scrollY > 300
}
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function formatTime(iso: string) {
  return dayjs(iso).format('YYYY-MM-DD HH:mm')
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.replace({ name: 'answer' })
}

const answerDetailModalRef = ref<InstanceType<typeof AnswerDetailModal> | null>(null)
function openDetail(item: AnswerHistoryItem) {
  answerDetailModalRef.value?.open(item)
}

function retryFirstPage() {
  loadAnswerPage()
}

// 切换收藏状态
const toggleFavorite = async (item: AnswerHistoryItem) => {
  if (!navigator.onLine) {
    alert('网络不可用')
    return
  }
  const action = item.isFavorited ? 'unfavorite' : 'favorite'
  try {
    await favoriteAnswer(item.id, action)
    const newStatus = !item.isFavorited
    updateLocalFavoriteStatus(item.id, newStatus)
    // 更新当前列表中的状态
    const target = allAnswers.value.find((a) => a.id === item.id)
    if (target) target.isFavorited = newStatus
  } catch (err) {
    console.error('收藏操作失败', err)
    alert('操作失败，请重试')
  }
}

onMounted(() => {
  loadAnswerPage()
  window.addEventListener('answers-updated', handleAnswersUpdated)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll)
})

onActivated(() => {
  allAnswers.value = getLocalAnswerList().slice(0, page.value * pageSize)
  loadAnswerPage().catch(console.warn)
})

onUnmounted(() => {
  window.removeEventListener('answers-updated', handleAnswersUpdated)
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
</style>
