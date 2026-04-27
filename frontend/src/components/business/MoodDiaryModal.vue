<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="close"
  >
    <div
      class="bg-white rounded-2xl w-full max-w-md mx-4 p-6 shadow-xl max-h-[90vh] overflow-y-auto"
    >
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold text-slate-800">今日心情</h3>
        <button @click="close" class="text-slate-400 hover:text-slate-600 text-2xl leading-none">
          &times;
        </button>
      </div>
      <MoodDiaryForm @submit="handleSubmit" @success="handleSuccess" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MoodDiaryForm from './MoodDiaryForm.vue'
import type { MoodTag } from '@/utils/storage'

interface DiaryFormData {
  date: string
  moodTag: MoodTag
  content: string
}

const visible = ref(false)

const open = () => {
  visible.value = true
}
const close = () => {
  visible.value = false
}

const emit = defineEmits<{
  (e: 'submitted', data: DiaryFormData): void
}>()

const handleSubmit = (data: DiaryFormData) => {
  emit('submitted', data)
  close()
}

const handleSuccess = () => {
  // 可选：额外处理
}

defineExpose({ open, close })
</script>
