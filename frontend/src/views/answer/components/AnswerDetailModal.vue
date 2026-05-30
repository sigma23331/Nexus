<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl relative">
      <!-- 头部 -->
      <div class="relative px-6 py-4 border-b border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 text-center">答案详情</h3>
        <button
          @click="close"
          class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-2xl leading-none"
          aria-label="关闭"
        >
          &times;
        </button>
      </div>

      <!-- 内容区域 -->
      <div class="px-6 py-4 space-y-5">
        <div>
          <div class="text-xs text-slate-500 mb-1">你的问题</div>
          <p class="text-base font-medium text-slate-800 leading-relaxed">
            {{ detailData.question }}
          </p>
        </div>
        <div>
          <div class="text-xs text-slate-500 mb-1">✨ 宇宙的回答</div>
          <p class="text-lg font-bold text-purple-700 leading-relaxed">
            {{ detailData.answerText }}
          </p>
        </div>
        <div class="flex justify-end">
          <span class="text-[11px] text-slate-400">{{ formatDate(detailData.createdAt) }}</span>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="px-6 py-4 border-t border-slate-100 flex justify-center gap-6">
        <button
          @click="toggleFavorite"
          :disabled="favoriteLoading"
          class="flex items-center gap-2 text-sm text-slate-600 hover:text-purple-600 transition disabled:opacity-50"
        >
          <span class="text-xl">{{ detailData.isFavorited ? '❤️' : '🤍' }}</span>
          <span>{{ detailData.isFavorited ? '已收藏' : '收藏' }}</span>
        </button>
        <button
          @click="openShareModal"
          class="flex items-center gap-2 text-sm text-slate-600 hover:text-purple-600 transition"
        >
          <span class="text-xl">📤</span>
          <span>分享到广场</span>
        </button>
        <button
          @click="downloadCard"
          :disabled="cardGenerating"
          class="flex items-center gap-2 text-sm text-slate-600 hover:text-purple-600 transition disabled:opacity-50"
        >
          <span class="text-xl">⬇️</span>
          <span>{{ cardGenerating ? '生成卡片中...' : '下载答案卡片' }}</span>
        </button>
        <!-- 调试预览按钮（仅开发环境） -->
        <!-- <button
          v-if="isDev"
          @click="debugPreviewCard"
          class="flex items-center gap-2 text-sm text-slate-600 hover:text-purple-600 transition"
        >
          <span class="text-xl">🖼️</span>
          <span>调试预览</span>
        </button> -->
      </div>
    </div>
  </div>

  <!-- 通用分享弹窗 -->
  <ShareToPlazaModal ref="shareModalRef" />

  <!-- Toast 提示 -->
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

// 打开分享编辑弹窗
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
// import { previewAnswerCard } from '@/utils/shareCardGenerator'
// const isDev = import.meta.env.DEV

// const debugPreviewCard = async () => {
//   await previewAnswerCard({
//     question: detailData.question,
//     answerText: detailData.answerText,
//     createdAt: detailData.createdAt,
//   })
// }
</script>
