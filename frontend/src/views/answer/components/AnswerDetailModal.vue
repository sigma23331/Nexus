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
        <!-- 问题 -->
        <div>
          <div class="text-xs text-slate-500 mb-1">你的问题</div>
          <p class="text-base font-medium text-slate-800 leading-relaxed">
            {{ detailData.question }}
          </p>
        </div>

        <!-- 答案 -->
        <div>
          <div class="text-xs text-slate-500 mb-1">✨ 宇宙的回答</div>
          <p class="text-lg font-bold text-purple-700 leading-relaxed">
            {{ detailData.answerText }}
          </p>
        </div>

        <!-- 时间 -->
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
          @click="shareCard"
          class="flex items-center gap-2 text-sm text-slate-600 hover:text-purple-600 transition"
        >
          <span class="text-xl">📤</span>
          <span>分享卡片</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import dayjs from 'dayjs'
import { favoriteAnswer, type AnswerHistoryItem } from '@/api/answer'
import { updateLocalFavoriteStatus } from '@/utils/answerService'

// 定义需要展示的数据（继承 AnswerHistoryItem 并确保 isFavorited 存在）
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

const formatDate = (iso: string) => dayjs(iso).format('YYYY-MM-DD HH:mm')

const open = (answer: AnswerHistoryItem) => {
  // 复制数据到弹窗内部状态
  detailData.id = answer.id
  detailData.question = answer.question
  detailData.answerText = answer.answerText
  detailData.createdAt = answer.createdAt
  detailData.isFavorited = answer.isFavorited || false
  visible.value = true
}

const close = () => {
  visible.value = false
}

// 切换收藏状态
const toggleFavorite = async () => {
  if (favoriteLoading.value) return
  if (!navigator.onLine) {
    alert('网络不可用，请稍后重试')
    return
  }
  const action = detailData.isFavorited ? 'unfavorite' : 'favorite'
  favoriteLoading.value = true
  try {
    await favoriteAnswer(detailData.id, action)
    const newStatus = !detailData.isFavorited
    // 更新本地缓存并触发全局事件
    updateLocalFavoriteStatus(detailData.id, newStatus)
    // 更新弹窗内的状态
    detailData.isFavorited = newStatus
  } catch (err) {
    console.error('操作失败', err)
    alert('操作失败，请重试')
  } finally {
    favoriteLoading.value = false
  }
}

// 分享（调用 Web Share API 或降级为复制链接）
const shareCard = async () => {
  const shareText = `问：${detailData.question}\n答：${detailData.answerText}`
  if (navigator.share) {
    try {
      await navigator.share({
        title: '答案之书',
        text: shareText,
      })
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        console.error('分享失败', err)
        fallbackCopy(shareText)
      }
    }
  } else {
    fallbackCopy(shareText)
  }
}

const fallbackCopy = (text: string) => {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      alert('已复制到剪贴板，可以分享给你的朋友')
    })
    .catch(() => {
      alert('无法复制，请手动复制')
    })
}

defineExpose({ open, close })
</script>
