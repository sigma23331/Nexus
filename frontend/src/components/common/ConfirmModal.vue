<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-sm mx-4 p-6 shadow-xl">
      <h3 class="text-lg font-bold text-slate-800 mb-2">{{ title }}</h3>
      <p class="text-sm text-slate-500 mb-6">{{ message }}</p>
      <div class="flex gap-3">
        <button
          @click="close"
          class="flex-1 py-2 rounded-xl border border-slate-200 text-slate-600"
        >
          取消
        </button>
        <button @click="confirm" class="flex-1 py-2 rounded-xl bg-purple-600 text-white">
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
let resolvePromise: ((value: boolean) => void) | null = null
let title = ref('')
let message = ref('')

const open = (opts: { title: string; message: string }) => {
  title.value = opts.title
  message.value = opts.message
  visible.value = true
  return new Promise<boolean>((resolve) => {
    resolvePromise = resolve
  })
}

const close = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(false)
  resolvePromise = null
}

const confirm = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(true)
  resolvePromise = null
}

defineExpose({ open, close })
</script>
