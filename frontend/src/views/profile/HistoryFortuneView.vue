<template>
  <div class="min-h-screen bg-white text-slate-900">
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

    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="text-purple-600">加载中...</div>
    </div>

    <!-- 数据列表 -->
    <div v-else-if="list.length > 0" class="space-y-3 p-4">
      <article
        v-for="item in list"
        :key="item.date"
        class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
      >
        <div class="mb-2 flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-slate-900">{{ formatDate(item.date) }}</p>
            <p class="text-xs text-slate-500">{{ item.title }}</p>
          </div>
          <span
            class="rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="scoreLevelClass(item.score)"
          >
            {{ item.score }} 分
          </span>
        </div>
        <p class="text-sm text-slate-700">{{ item.title }}</p>
      </article>

      <!-- 分页加载更多 -->
      <div class="py-4 text-center">
        <button
          v-if="hasMore"
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-2 text-sm text-purple-600 bg-purple-50 rounded-full hover:bg-purple-100 transition disabled:opacity-50"
        >
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
        <p v-else class="text-xs text-slate-400">—— 已经到底了 ——</p>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex flex-col items-center justify-center h-64 text-slate-400">
      <span class="text-4xl mb-2">📭</span>
      <p>暂无历史运势记录</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { getHistoryFortune, type HistoryFortuneItem } from '@/api/fortune'

const router = useRouter()
const loading = ref(true)
const loadingMore = ref(false)
const list = ref<HistoryFortuneItem[]>([])
const page = ref(1)
const limit = 10
const total = ref(0)
const hasMore = ref(true)

const formatDate = (isoDate: string) => {
  const parts = isoDate.split('-')
  if (parts.length === 3) return `${parts[1]}-${parts[2]}`
  return isoDate
}

const scoreLevelClass = (score: number) => {
  if (score >= 85) return 'bg-emerald-50 text-emerald-700'
  if (score >= 75) return 'bg-blue-50 text-blue-700'
  if (score >= 65) return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-700'
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
    const newList = res.list
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
  if (loadingMore.value || !hasMore.value) return
  page.value++
  loadHistory(false)
}

// 刷新列表（重置到第一页）
const refresh = () => {
  loadHistory(true)
}

onMounted(() => {
  refresh()
})

// 从缓存激活时重新加载数据
onActivated(() => {
  refresh()
})
</script>
