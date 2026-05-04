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
      <section>
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-800">历史列表</h2>
          <span class="text-xs text-slate-500">共 {{ answerStore.historyTotal }} 条</span>
        </div>

        <div
          v-if="loadError"
          class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-3 text-xs text-rose-700"
        >
          <p>{{ loadError }}</p>
          <p class="mt-2 text-[11px] text-rose-600/90">
            这是接口未成功返回时的提示，与「真的没有记录」不同。常见原因：本地后端未启动、路由未实现、数据库异常等（HTTP
            500 表示服务端出错）。
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
          <div v-if="loading && !answerStore.historyList.length" class="space-y-3">
            <div v-for="n in 4" :key="n" class="h-20 animate-pulse rounded-xl bg-slate-200/80" />
          </div>

          <div
            v-else-if="!answerStore.historyList.length"
            class="rounded-2xl border border-dashed border-slate-200 bg-white py-12 text-center text-sm text-slate-400"
          >
            暂无历史记录
          </div>

          <ul v-else class="space-y-3">
            <li
              v-for="item in answerStore.historyList"
              :key="item.id"
              class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <div class="flex items-start justify-between gap-2">
                <p class="text-xs font-medium text-slate-800 line-clamp-2">
                  问：{{ item.question }}
                </p>
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

        <button
          v-if="answerStore.historyList.length > 0 && hasMore"
          type="button"
          class="mt-4 w-full rounded-xl border border-slate-200 bg-white py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
          :disabled="loadingMore"
          @click="loadMore"
        >
          {{ loadingMore ? '加载中…' : '加载更多' }}
        </button>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { useAnswerStore } from '@/stores/answer'
import { getAnswerHistory } from '@/api/answer'

const router = useRouter()
const answerStore = useAnswerStore()

const loading = ref(false)
const loadingMore = ref(false)
const loadError = ref('')
const page = ref(1)
const limit = 10

const hasMore = computed(() => answerStore.historyList.length < answerStore.historyTotal)

function formatTime(iso: string) {
  return dayjs(iso).format('YYYY-MM-DD HH:mm')
}

function goBack() {
  if (window.history.length > 1) router.back()
  else router.replace({ name: 'answer' })
}

async function fetchPage(nextPage: number, append: boolean) {
  const res = await getAnswerHistory(nextPage, limit)
  if (append) {
    answerStore.appendHistoryItems(res.list)
  } else {
    answerStore.setHistoryList(res.list, res.total)
  }
  page.value = nextPage
}

onMounted(async () => {
  loading.value = true
  loadError.value = ''
  try {
    await fetchPage(1, false)
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
})

async function loadMore() {
  if (!hasMore.value || loadingMore.value) return
  loadingMore.value = true
  loadError.value = ''
  try {
    await fetchPage(page.value + 1, true)
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loadingMore.value = false
  }
}

async function retryFirstPage() {
  loading.value = true
  loadError.value = ''
  try {
    await fetchPage(1, false)
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
