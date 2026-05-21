<template>
  <Transition name="result-modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-6"
      @click.self="close"
    >
      <div class="result-modal-panel bg-white rounded-3xl w-full max-w-sm p-8 text-center">
        <span class="text-5xl">✨</span>
        <p class="mt-3 text-sm text-slate-500">树洞收到了你的悄悄话</p>
        <p class="my-6 text-lg font-bold leading-relaxed text-slate-900">
          {{ resultMessage }}
        </p>
        <button
          @click="close"
          class="w-full rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 py-4 font-bold text-white"
        >
          我明白了
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
// 固定文案，后续可根据后端返回动态修改
const resultMessage = ref('你的烦恼消失了，身心变得无比轻松～\n愿你今日晴朗 ☀️')

const open = (customMessage?: string) => {
  if (customMessage) resultMessage.value = customMessage
  else {
    resultMessage.value = '你的烦恼消失了，身心变得无比轻松～\n愿你今日晴朗 ☀️'
  }
  visible.value = true
}

const close = () => {
  visible.value = false
}

defineExpose({ open, close })
</script>

<style scoped>
.result-modal-enter-active,
.result-modal-leave-active {
  transition: background-color 260ms ease;
}
.result-modal-enter-active .result-modal-panel,
.result-modal-leave-active .result-modal-panel {
  transition: transform 300ms cubic-bezier(0.2, 0.8, 0.2, 1), opacity 300ms ease;
}
.result-modal-enter-from {
  background-color: rgba(0, 0, 0, 0);
}
.result-modal-enter-from .result-modal-panel {
  opacity: 0;
  transform: translateY(18px) scale(0.96);
}
.result-modal-leave-to {
  background-color: rgba(0, 0, 0, 0);
}
.result-modal-leave-to .result-modal-panel {
  opacity: 0;
  transform: translateY(14px) scale(0.98);
}
</style>