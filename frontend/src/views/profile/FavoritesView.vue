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
        <h1 class="flex-1 text-center text-lg font-semibold">收藏的答案</h1>
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
    <div v-if="loading && allFavorites.length === 0" class="flex justify-center items-center h-64">
      <div class="text-purple-600">加载中...</div>
    </div>

    <!-- 列表 -->
    <div v-else-if="filteredList.length > 0" class="divide-y divide-slate-100">
      <div
        v-for="item in filteredList"
        :key="item.id"
        class="p-4 hover:bg-slate-50 transition cursor-pointer"
        @click="openDetail(item)"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1">
            <p class="text-sm font-medium text-slate-800 line-clamp-2">问：{{ item.question }}</p>
            <p class="mt-1 text-xs text-slate-600 line-clamp-2">「{{ item.answerText }}」</p>
            <p class="mt-2 text-[10px] text-slate-400">{{ formatTime(item.createdAt) }}</p>
          </div>
          <button
            @click.stop="handleUnfavorite(item.id)"
            :disabled="unfavoritingId === item.id"
            class="shrink-0 px-2 py-1 rounded-full bg-rose-50 text-rose-600 text-xs font-medium hover:bg-rose-100 transition disabled:opacity-50"
          >
            {{ unfavoritingId === item.id ? '取消中' : '取消收藏' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="!loading && filteredList.length === 0"
      class="flex flex-col items-center justify-center h-64 text-slate-400"
    >
      <span class="text-4xl mb-2">⭐</span>
      <p>{{ selectedMonth ? '该月份没有收藏的答案' : '暂无收藏的答案' }}</p>
      <router-link to="/answer" class="mt-4 text-sm text-purple-600 hover:underline">
        去提问并收藏
      </router-link>
    </div>

    <!-- 错误提示 -->
    <div
      v-if="errorMsg"
      class="fixed bottom-4 left-4 right-4 bg-rose-600 text-white text-sm p-3 rounded-xl shadow-lg"
    >
      {{ errorMsg }}
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
    <AnswerDetailModal ref="answerDetailModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { getFavoriteAnswers, favoriteAnswer, type AnswerHistoryItem } from '@/api/answer'
import { updateLocalFavoriteStatus } from '@/utils/answerService'
import AnswerDetailModal from '@/views/answer/components/AnswerDetailModal.vue'

const router = useRouter()

// 数据状态
const allFavorites = ref<AnswerHistoryItem[]>([]) // 全部收藏（已排序）
const loading = ref(false)
const errorMsg = ref('')
const unfavoritingId = ref<string | null>(null)

// 筛选相关
const selectedMonth = ref('') // 格式 YYYY-MM
const showMonthSelector = ref(false)
const monthSelectorRef = ref<HTMLElement | null>(null)

// 回到顶部
const showBackToTop = ref(false)

// 计算可选的月份列表（基于 allFavorites 的 createdAt）
const availableMonths = computed(() => {
  const monthsSet = new Set<string>()
  allFavorites.value.forEach((item) => {
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

// 根据月份筛选后的列表
const filteredList = computed(() => {
  if (!selectedMonth.value) return allFavorites.value
  return allFavorites.value.filter((item) => item.createdAt.startsWith(selectedMonth.value))
})

const filteredTotal = computed(() => filteredList.value.length)

// 递归加载全部收藏（按时间倒序排序）
async function fetchAllFavorites(page = 1, limit = 20) {
  const res = await getFavoriteAnswers(page, limit)
  // 为每个 item 补充 isFavorited = true
  const itemsWithFlag = res.list.map((item) => ({
    ...item,
    isFavorited: true,
  }))
  if (page === 1) {
    allFavorites.value = [...itemsWithFlag]
  } else {
    allFavorites.value.push(...itemsWithFlag)
  }
  // 按 createdAt 降序排序
  allFavorites.value.sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
  )
  if (allFavorites.value.length < res.total) {
    await fetchAllFavorites(page + 1, limit)
  }
}

// 刷新全部收藏（从零开始）
async function refreshAllFavorites() {
  loading.value = true
  errorMsg.value = ''
  try {
    allFavorites.value = []
    await fetchAllFavorites(1, 20)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '加载收藏失败'
  } finally {
    loading.value = false
  }
}

// 取消收藏
const handleUnfavorite = async (answerId: string) => {
  if (unfavoritingId.value) return
  unfavoritingId.value = answerId
  errorMsg.value = ''
  try {
    await favoriteAnswer(answerId, 'unfavorite')
    // 更新本地缓存（触发全局事件）
    updateLocalFavoriteStatus(answerId, false)
    // 从本地列表中移除
    allFavorites.value = allFavorites.value.filter((item) => item.id !== answerId)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '取消收藏失败'
  } finally {
    unfavoritingId.value = null
  }
}

// 监听全局数据更新（当其他页面修改收藏状态时）
function handleAnswersUpdated() {
  // 重新加载全部收藏
  refreshAllFavorites()
}

// 月份选择器逻辑
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

// 滚动事件
function handleScroll() {
  showBackToTop.value = window.scrollY > 300
}
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function formatTime(iso: string) {
  return dayjs(iso).format('YYYY-MM-DD HH:mm')
}

// 详情弹窗
const answerDetailModalRef = ref<InstanceType<typeof AnswerDetailModal> | null>(null)
function openDetail(item: AnswerHistoryItem) {
  answerDetailModalRef.value?.open(item)
}

onMounted(() => {
  refreshAllFavorites()
  window.addEventListener('answers-updated', handleAnswersUpdated)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll)
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
