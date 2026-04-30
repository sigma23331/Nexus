<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-sm mx-4 p-6 shadow-xl">
      <h3 class="text-lg font-bold text-slate-800 mb-2">{{ title }}</h3>
      <p class="text-sm text-slate-500 mb-4">{{ message }}</p>
      <input
        ref="inputRef"
        v-model="inputValue"
        type="text"
        class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400"
        :placeholder="placeholder"
        @keyup.enter="confirm"
      />
      <div class="flex gap-3 mt-6">
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
import { ref, nextTick } from 'vue'

const visible = ref(false)
const title = ref('')
const message = ref('')
const placeholder = ref('')
let resolvePromise: ((value: string | null) => void) | null = null
const inputValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

const open = (opts: {
  title: string
  message?: string
  placeholder?: string
  defaultValue?: string
}) => {
  title.value = opts.title
  message.value = opts.message || ''
  placeholder.value = opts.placeholder || ''
  inputValue.value = opts.defaultValue || ''
  visible.value = true
  return new Promise<string | null>((resolve) => {
    resolvePromise = resolve
    nextTick(() => inputRef.value?.focus())
  })
}

const close = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(null)
  resolvePromise = null
}

const confirm = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(inputValue.value)
  resolvePromise = null
}

defineExpose({ open, close })
</script>
