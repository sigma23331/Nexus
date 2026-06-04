<template>
  <Transition name="answer-modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      @click.self="close"
    >
      <div
        class="w-full max-w-md overflow-hidden shadow-xl rounded-2xl bg-gradient-to-br from-purple-100 via-white to-indigo-100 border border-purple-200"
      >
        <!-- 头部 -->
        <div class="relative px-5 py-4 border-b border-purple-200">
          <h3 class="text-lg font-semibold text-slate-800 text-center">答案详情</h3>
          <button
            @click="close"
            class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition"
            aria-label="关闭"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- 内容区域 -->
        <div class="px-5 py-4 space-y-4">
          <!-- 你的问题 -->
          <div class="rounded-xl bg-slate-50/80 p-4 border border-slate-300">
            <div class="text-sm text-slate-700 mb-1 flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              你的问题
            </div>
            <p class="text-base font-medium text-slate-800 leading-relaxed font-lxgw">
              {{ detailData.question }}
            </p>
          </div>

          <!-- 宇宙的回答 -->
          <div class="rounded-xl bg-purple-100/50 p-4 border border-purple-200">
            <div class="text-sm text-purple-700 mb-1 flex items-center gap-1.5">
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                stroke-width="1.5"
              >
                <path
                  d="M12 2v3m0 14v3M2 12h3m14 0h3M5.5 5.5l2 2m9 9l2 2M5.5 18.5l2-2m9-9l2-2"
                  stroke-linecap="round"
                />
                <circle cx="12" cy="12" r="2" fill="currentColor" stroke="none" />
              </svg>
              宇宙的回答
            </div>
            <p class="text-lg font-bold text-purple-800 leading-relaxed font-lxgw">
              {{ detailData.answerText }}
            </p>
          </div>

          <div class="flex justify-end">
            <span class="text-[11px] text-slate-400">{{ formatDate(detailData.createdAt) }}</span>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="px-5 py-4 border-t border-purple-200 flex justify-center gap-3">
          <!-- 收藏按钮（五角星） -->
          <button
            @click="toggleFavorite"
            :disabled="favoriteLoading"
            class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white/60 py-2 text-sm text-slate-700 transition hover:bg-white disabled:opacity-50"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5"
              :class="detailData.isFavorited ? 'text-amber-500' : 'text-slate-400'"
              :fill="detailData.isFavorited ? 'currentColor' : 'none'"
              :stroke="detailData.isFavorited ? 'none' : 'currentColor'"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polygon
                points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
              />
            </svg>
            <span>{{ detailData.isFavorited ? '已收藏' : '收藏' }}</span>
          </button>

          <!-- 分享按钮 -->
          <button
            @click="openShareModal"
            class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white/60 py-2 text-sm text-slate-700 transition hover:bg-white"
          >
            <span class="text-base">📤</span>
            <span>分享到广场</span>
          </button>

          <!-- 下载卡片按钮 -->
          <button
            @click="downloadCard"
            :disabled="cardGenerating"
            class="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white/60 py-2 text-sm text-slate-700 transition hover:bg-white disabled:opacity-50"
          >
            <span class="text-base">⬇️</span>
            <span>{{ cardGenerating ? '生成卡片中...' : '下载卡片' }}</span>
          </button>
        </div>
      </div>
    </div>
  </Transition>

  <ShareToPlazaModal ref="shareModalRef" />

  <div
    v-if="toastMessage"
    class="fixed bottom-20 left-4 right-4 bg-black/70 text-white text-sm text-center py-2 rounded-lg z-50"
  >
    {{ toastMessage }}
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import dayjs from 'dayjs'
import { favoriteAnswer, type AnswerHistoryItem } from '@/api/answer'
import { updateLocalFavoriteStatus } from '@/utils/answerService'
import ShareToPlazaModal from '@/components/common/ShareToPlazaModal.vue'
import { useShareCard } from '@/composables/useShareCard'

interface AnswerDetail extends AnswerHistoryItem {
  isFavorited: boolean
}

const visible = ref(false)
const detailData = reactive<AnswerDetail>({
  id: '',
  question: '',
  answerText: '',
  createdAt: '',
  isFavorited: false,
})

const favoriteLoading = ref(false)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const shareModalRef = ref<InstanceType<typeof ShareToPlazaModal> | null>(null)

const formatDate = (iso: string) => dayjs(iso).format('YYYY-MM-DD HH:mm')

const open = (answer: AnswerHistoryItem) => {
  detailData.id = answer.id
  detailData.question = answer.question
  detailData.answerText = answer.answerText
  detailData.createdAt = answer.createdAt
  detailData.isFavorited = answer.isFavorited || false
  visible.value = true
}

const close = () => {
  visible.value = false
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = ''
}

const showToast = (msg: string) => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = msg
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
    toastTimer = null
  }, 2000)
}

const toggleFavorite = async () => {
  if (favoriteLoading.value) return
  if (!navigator.onLine) {
    showToast('网络不可用，请稍后重试')
    return
  }
  const action = detailData.isFavorited ? 'unfavorite' : 'favorite'
  favoriteLoading.value = true
  try {
    await favoriteAnswer(detailData.id, action)
    const newStatus = !detailData.isFavorited
    updateLocalFavoriteStatus(detailData.id, newStatus)
    detailData.isFavorited = newStatus
    showToast(newStatus ? '已收藏' : '已取消收藏')
  } catch (err) {
    console.error('操作失败', err)
    showToast('操作失败，请重试')
  } finally {
    favoriteLoading.value = false
  }
}

const openShareModal = () => {
  const originalContent = `问：${detailData.question}\n答：${detailData.answerText}`
  shareModalRef.value?.open({
    type: 'answer',
    sourceId: detailData.id,
    content: originalContent,
  })
}

const { isGenerating: cardGenerating, generateAnswerCard } = useShareCard()

const downloadCard = () => {
  if (!detailData.question || !detailData.answerText) return
  generateAnswerCard({
    question: detailData.question,
    answerText: detailData.answerText,
    createdAt: detailData.createdAt,
  })
}

defineExpose({ open, close })
</script>

<style scoped>
.font-lxgw {
  font-family: 'KaiTi', '楷体', cursive;
}

.answer-modal-enter-active,
.answer-modal-leave-active {
  transition: background-color 0.22s ease;
}
.answer-modal-enter-active .answer-modal-panel,
.answer-modal-leave-active .answer-modal-panel {
  transition:
    transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1),
    opacity 0.28s ease;
}
.answer-modal-enter-from {
  background-color: rgba(0, 0, 0, 0);
}
.answer-modal-enter-from .answer-modal-panel {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}
.answer-modal-leave-to {
  background-color: rgba(0, 0, 0, 0);
}
.answer-modal-leave-to .answer-modal-panel {
  opacity: 0;
  transform: translateY(8px) scale(0.99);
}
</style>
