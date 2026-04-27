<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl relative">
      <!-- 头部 -->
      <div class="relative px-6 py-4 border-b border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 text-center">日记详情</h3>
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
        <!-- 日期 -->
        <div class="flex items-center gap-3 text-slate-700">
          <span class="text-2xl">📅</span>
          <span class="text-base font-medium">{{ detailData.date }}</span>
        </div>

        <!-- 心情：分两行显示，第一行大表情，第二行心情标签 -->
        <div class="flex flex-col items-center gap-2 py-2">
          <div class="text-5xl">{{ moodEmoji }}</div>
        </div>

        <!-- 备注内容：文字颜色随心情变化，背景保持浅灰 -->
        <div class="bg-slate-50 rounded-xl p-4">
          <p :class="['text-sm whitespace-pre-wrap', moodTextColor]">
            {{ detailData.content || '暂无备注' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 心情映射
const moodEmojiMap: Record<string, string> = {
  happy: '😄',
  calm: '😌',
  tired: '😴',
  anxious: '😟',
  angry: '😡',
  sad: '😢',
  null: '⚪️',
}
// const moodLabelMap: Record<string, string> = {
//   happy: '开心',
//   calm: '平静',
//   tired: '困倦',
//   anxious: '焦虑',
//   angry: '生气',
//   sad: '难过',
//   null: '未记录',
// }

// 心情文字颜色映射（用于标签和备注文字）
const moodColorMap: Record<string, string> = {
  happy: 'text-yellow-600',
  calm: 'text-green-600',
  tired: 'text-slate-500',
  anxious: 'text-orange-600',
  angry: 'text-red-600',
  sad: 'text-blue-600',
  null: 'text-slate-400',
}

interface DiaryDetail {
  date: string
  moodTag: string | null
  content: string
}

const visible = ref(false)
const detailData = ref<DiaryDetail>({
  date: '',
  moodTag: null,
  content: '',
})

const moodEmoji = computed(() => moodEmojiMap[detailData.value.moodTag ?? 'null'])
// const moodLabel = computed(() => moodLabelMap[detailData.value.moodTag ?? 'null'])
// const moodColor = computed(() => moodColorMap[detailData.value.moodTag ?? 'null'])
// 备注文字直接复用相同的颜色类
const moodTextColor = computed(() => moodColorMap[detailData.value.moodTag ?? 'null'])

const open = (data: DiaryDetail) => {
  detailData.value = data
  visible.value = true
}

const close = () => {
  visible.value = false
}

defineExpose({ open, close })
</script>
