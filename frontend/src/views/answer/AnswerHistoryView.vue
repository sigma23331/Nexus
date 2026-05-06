<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 pb-8">
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
        <h1 class="text-base font-bold text-slate-900">过往答案</h1>
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
          <div v-for="n in 4" :key="n" class="h-20 animate-pulse rounded-xl bg-slate-200/80" />
        </div>

        <!-- 空状态 -->
        <div
          v-else-if="!filteredList.length"
          class="rounded-2xl border border-dashed border-slate-200 bg-white py-12 text-center text-sm text-slate-400"
        >
          {{ selectedMonth ? '该月份没有答案记录' : '暂无历史记录，去提问吧' }}
        </div>

        <!-- 列表 -->
        <ul v-else class="space-y-3">
          <li
            v-for="item in filteredList"
            :key="item.id"
            class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm cursor-pointer hover:bg-slate-50 transition"
            @click="openDetail(item)"
          >
            <div class="flex items-start justify-between gap-2">
              <p class="text-xs font-medium text-slate-800 line-clamp-2">问：{{ item.question }}</p>
              <span
                v-if="item.isFavorited"
                class="shrink-0 rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700"
              >
                已收藏
              </span>
            </div>
            <p class="mt-2 text-[11px] text-slate-500 line-clamp-2">「{{ item.answerText }}」</p>
            <p class="mt-2 text-[10px] text-slate-400">{{ formatTime(item.createdAt) }}</p>
          </li>
        </ul>
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
import { fetchAndSyncHistory, getLocalAnswerList } from '@/utils/answerService'
import type { AnswerHistoryItem } from '@/api/answer'
import AnswerDetailModal from './components/AnswerDetailModal.vue'

const router = useRouter()

// 数据状态
const allAnswers = ref<AnswerHistoryItem[]>([])
const loading = ref(false)
const loadError = ref('')

// 筛选相关
const selectedMonth = ref('') // 格式 YYYY-MM
const showMonthSelector = ref(false)
const monthSelectorRef = ref<HTMLElement | null>(null)

// 回到顶部
const showBackToTop = ref(false)

// 计算可选的月份列表
const availableMonths = computed(() => {
  const monthsSet = new Set<string>()
  allAnswers.value.forEach((item) => {
    const month = item.createdAt.slice(0, 7) // YYYY-MM
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

// 加载所有数据
async function loadAllAnswers() {
  loading.value = true
  loadError.value = ''
  try {
    await fetchAllRemoteAndSync()
    allAnswers.value = getLocalAnswerList()
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 递归拉取所有分页
async function fetchAllRemoteAndSync(page = 1, limit = 20) {
  const res = await fetchAndSyncHistory(page, limit)
  if (res.list.length === limit && res.list.length < res.total) {
    await fetchAllRemoteAndSync(page + 1, limit)
  }
}

// 监听全局数据更新
function handleAnswersUpdated() {
  allAnswers.value = getLocalAnswerList()
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

// 监听滚动，控制回到顶部按钮显示
function handleScroll() {
  // 滚动超过 300px 时显示按钮
  showBackToTop.value = window.scrollY > 300
}

// 回到顶部
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  })
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
  loadAllAnswers()
}

onMounted(() => {
  loadAllAnswers()
  window.addEventListener('answers-updated', handleAnswersUpdated)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll)
})

onActivated(() => {
  allAnswers.value = getLocalAnswerList()
  fetchAllRemoteAndSync().catch(console.warn)
})

onUnmounted(() => {
  window.removeEventListener('answers-updated', handleAnswersUpdated)
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 淡入淡出 + 缩放动画 */
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
