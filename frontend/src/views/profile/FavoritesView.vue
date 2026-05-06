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

    <!-- 加载状态 -->
    <div v-if="loading && list.length === 0" class="flex justify-center items-center h-64">
      <div class="text-purple-600">加载中...</div>
    </div>

    <!-- 列表 -->
    <div v-else-if="list.length > 0" class="divide-y divide-slate-100">
      <div v-for="item in list" :key="item.id" class="p-4 hover:bg-slate-50 transition">
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1">
            <p class="text-sm font-medium text-slate-800 line-clamp-2">问：{{ item.question }}</p>
            <p class="mt-1 text-xs text-slate-600 line-clamp-2">「{{ item.answerText }}」</p>
            <p class="mt-2 text-[10px] text-slate-400">{{ formatTime(item.createdAt) }}</p>
          </div>
          <button
            @click="handleUnfavorite(item.id)"
            :disabled="unfavoritingId === item.id"
            class="shrink-0 px-2 py-1 rounded-full bg-rose-50 text-rose-600 text-xs font-medium hover:bg-rose-100 transition disabled:opacity-50"
          >
            {{ unfavoritingId === item.id ? '取消中' : '取消收藏' }}
          </button>
        </div>
      </div>

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
      <span class="text-4xl mb-2">⭐</span>
      <p>暂无收藏的答案</p>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { getFavoriteAnswers, favoriteAnswer, type AnswerHistoryItem } from '@/api/answer'

const router = useRouter()
const list = ref<AnswerHistoryItem[]>([])
const total = ref(0)
const page = ref(1)
const limit = 10
const loading = ref(false)
const loadingMore = ref(false)
const unfavoritingId = ref<string | null>(null)
const errorMsg = ref('')

const hasMore = computed(() => list.value.length < total.value)

const formatTime = (iso: string) => dayjs(iso).format('YYYY-MM-DD HH:mm')

const fetchList = async (reset = true) => {
  if (reset) {
    page.value = 1
    list.value = []
    loading.value = true
  } else {
    loadingMore.value = true
  }
  errorMsg.value = ''
  try {
    const res = await getFavoriteAnswers(page.value, limit)
    total.value = res.total
    const newItems = res.list
    if (reset) {
      list.value = newItems
    } else {
      list.value.push(...newItems)
    }
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '加载失败'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  if (loadingMore.value || !hasMore.value) return
  page.value++
  fetchList(false)
}

const handleUnfavorite = async (answerId: string) => {
  if (unfavoritingId.value) return
  unfavoritingId.value = answerId
  errorMsg.value = ''
  try {
    await favoriteAnswer(answerId, 'unfavorite')
    // 从本地列表中移除
    list.value = list.value.filter((item) => item.id !== answerId)
    total.value--
    // 可选：如果当前页空了且还有更多，自动加载下一页
    if (list.value.length === 0 && hasMore.value) {
      page.value++
      await fetchList(false)
    }
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '取消收藏失败'
  } finally {
    unfavoritingId.value = null
  }
}

onMounted(() => {
  fetchList()
})
</script>
