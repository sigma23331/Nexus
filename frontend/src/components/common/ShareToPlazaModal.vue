<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl relative">
      <!-- 头部 -->
      <div class="relative px-6 py-4 border-b border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 text-center">
          {{ isFortune ? '分享运势到广场' : '分享答案到广场' }}
        </h3>
        <button
          @click="close"
          class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-2xl leading-none"
        >
          &times;
        </button>
      </div>

      <!-- 内容区域：调整顺序，分享文案在上，原始内容在下 -->
      <div class="px-6 py-4 space-y-5 max-h-[70vh] overflow-y-auto">
        <!-- 分享文案（可编辑，放在最上面） -->
        <div>
          <div class="text-xs text-slate-500 mb-1">分享文案（可选）</div>
          <textarea
            v-model="extraContent"
            rows="3"
            class="w-full border border-slate-200 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder="写下你想说的话，与大家分享...（最多100字）"
            maxlength="100"
          ></textarea>
          <div class="text-right text-xs text-slate-400 mt-1">{{ extraContent.length }}/100</div>
        </div>

        <!-- 原始内容预览（不可编辑） -->
        <div>
          <div class="text-xs text-slate-500 mb-1">
            {{ isFortune ? '运势内容' : '你的提问与回答' }}
          </div>
          <div class="bg-slate-50 p-3 rounded-lg whitespace-pre-wrap text-sm text-slate-700">
            {{ originalContent }}
          </div>
        </div>

        <!-- 预览卡片样式（最终效果） -->
        <div class="bg-amber-50 rounded-xl p-3 border border-amber-200">
          <p class="text-xs text-amber-700 mb-2">📖 预览效果</p>
          <div class="whitespace-pre-wrap text-sm text-slate-700">
            {{ finalContent }}
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
        <button
          @click="close"
          class="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition"
        >
          取消
        </button>
        <button
          @click="confirmShare"
          :disabled="sharing"
          class="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
        >
          {{ sharing ? '分享中...' : '确认分享' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Toast 提示 -->
  <div
    v-if="toastMessage"
    class="fixed bottom-20 left-4 right-4 bg-black/70 text-white text-sm text-center py-2 rounded-lg z-50"
  >
    {{ toastMessage }}
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { createPlazaCard } from '@/api/plaza'

const visible = ref(false)
const cardType = ref<'fortune' | 'answer'>('answer')
const sourceId = ref('')
const originalContent = ref('')
const extraContent = ref('')
const sharing = ref(false)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const isFortune = computed(() => cardType.value === 'fortune')

// 最终内容：分享文案（如果有）放在最上面，然后是原始内容
const finalContent = computed(() => {
  if (extraContent.value.trim()) {
    return `✨ ${extraContent.value.trim()}\n\n${originalContent.value}`
  }
  return originalContent.value
})

const showToast = (msg: string) => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = msg
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
    toastTimer = null
  }, 2000)
}

const open = (params: { type: 'fortune' | 'answer'; sourceId: string; content: string }) => {
  cardType.value = params.type
  sourceId.value = params.sourceId
  originalContent.value = params.content
  extraContent.value = ''
  visible.value = true
}

const close = () => {
  visible.value = false
  extraContent.value = ''
}

const confirmShare = async () => {
  if (sharing.value) return
  if (!navigator.onLine) {
    showToast('网络不可用，请稍后重试')
    return
  }

  sharing.value = true
  try {
    const placeholderUrl = 'https://placehold.co/400x400/FEF7E0/8B5CF6?text=心运岛&font=montserrat'
    await createPlazaCard({
      type: cardType.value,
      sourceId: sourceId.value,
      snapshotUrl: placeholderUrl,
      content: finalContent.value,
      tags: [],
    })
    showToast('✨ 已分享到广场！')
    setTimeout(() => {
      close()
    }, 1500)
  } catch (err) {
    console.error('分享失败', err)
    showToast('分享失败，请重试')
  } finally {
    sharing.value = false
  }
}

defineExpose({ open })
</script>
