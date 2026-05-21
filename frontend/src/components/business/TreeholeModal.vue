<template>
  <Transition name="treehole-modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-6"
      @click.self="close"
    >
      <div class="treehole-modal-panel bg-white rounded-3xl w-full max-w-sm p-8 text-center">
        <span class="text-5xl">🌳</span>
        <h3 class="mt-2 text-xl font-bold text-slate-800">今日树洞</h3>
        <p class="mt-1 text-xs text-slate-500">把烦恼说出来，它会消失不见</p>

        <div class="mt-6 text-left">
          <textarea
            v-model="content"
            rows="4"
            maxlength="200"
            class="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            placeholder="写下你的烦恼…（最多200字）"
          ></textarea>
          <div class="flex justify-end mt-1">
            <span class="text-xs text-slate-400">{{ content.length }}/200</span>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button
            @click="close"
            class="flex-1 py-3 rounded-xl border border-slate-200 text-slate-600 text-sm font-medium hover:bg-slate-50 transition"
          >
            取消
          </button>
          <button
            @click="submit"
            :disabled="!content.trim() || isSubmitting"
            class="flex-1 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-bold disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {{ isSubmitting ? '投入中...' : '投入树洞' }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const content = ref('')
const isSubmitting = ref(false)

const emit = defineEmits<{
  (e: 'submit', text: string): void
}>()

const open = () => {
  content.value = ''
  visible.value = true
  isSubmitting.value = false
}

const close = () => {
  visible.value = false
  content.value = ''
  isSubmitting.value = false
}

const submit = async () => {
  const text = content.value.trim()
  if (!text) return

  isSubmitting.value = true
  // 模拟提交延迟（后续可替换为真实 API）
  await new Promise((resolve) => setTimeout(resolve, 300))
  // 此处可调用后端接口（预留）
  // await submitWorry({ content: text })
  isSubmitting.value = false
  close()
  emit('submit', text)
}

defineExpose({ open, close })
</script>

<style scoped>
.treehole-modal-enter-active,
.treehole-modal-leave-active {
  transition: background-color 260ms ease;
}
.treehole-modal-enter-active .treehole-modal-panel,
.treehole-modal-leave-active .treehole-modal-panel {
  transition:
    transform 300ms cubic-bezier(0.2, 0.8, 0.2, 1),
    opacity 300ms ease;
}
.treehole-modal-enter-from {
  background-color: rgba(0, 0, 0, 0);
}
.treehole-modal-enter-from .treehole-modal-panel {
  opacity: 0;
  transform: translateY(18px) scale(0.96);
}
.treehole-modal-leave-to {
  background-color: rgba(0, 0, 0, 0);
}
.treehole-modal-leave-to .treehole-modal-panel {
  opacity: 0;
  transform: translateY(14px) scale(0.98);
}
</style>
