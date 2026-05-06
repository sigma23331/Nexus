<!-- MoodDiaryForm.vue -->
<template>
  <div class="space-y-6">
    <!-- 日期选择区块 -->
    <div class="space-y-1">
      <label class="block text-sm font-medium text-slate-700">日期</label>
      <input
        type="date"
        v-model="form.date"
        :max="maxDate"
        class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400"
      />
    </div>

    <!-- 心情选择区块 -->
    <div class="space-y-2">
      <span class="block text-sm font-medium text-slate-700">今天的心情</span>
      <div class="grid grid-cols-3 sm:grid-cols-6 gap-2">
        <button
          v-for="item in MOOD_OPTIONS"
          :key="item.value"
          type="button"
          @click="setMood(item.value)"
          :class="[
            'h-14 rounded-xl text-2xl transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-purple-400',
            form.moodTag === item.value
              ? 'bg-purple-100 border-2 border-purple-500 shadow-sm ring-2 ring-purple-200'
              : 'bg-slate-50 border border-slate-200 hover:bg-slate-100 hover:scale-105',
          ]"
          :title="item.label"
          :aria-label="`选择心情：${item.label}`"
        >
          {{ item.emoji }}
        </button>
      </div>
      <p class="text-xs text-slate-500 mt-1">
        当前：{{ MOOD_OPTIONS.find((m) => m.value === form.moodTag)?.label || '未选择' }}
      </p>
    </div>

    <!-- 备注输入区块 -->
    <div class="space-y-1">
      <label class="block text-sm font-medium text-slate-700">备注</label>
      <textarea
        v-model="form.content"
        rows="4"
        class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400 resize-none"
        placeholder="记录今天的心情…（最多500字）"
        maxlength="500"
      ></textarea>
      <div class="flex justify-between text-xs text-slate-400">
        <span>支持500字</span>
        <span>{{ form.content.length }}/500</span>
      </div>
    </div>

    <!-- 提交按钮 -->
    <button
      @click="handleSubmit"
      :disabled="submitting"
      class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-medium py-2.5 rounded-xl transition disabled:opacity-50 shadow-sm"
    >
      {{ submitting ? '保存中…' : '保存日记' }}
    </button>

    <!-- 提示消息 -->
    <p
      v-if="message.text"
      class="text-center text-sm py-2 rounded-lg"
      :class="message.type === 'success' ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'"
    >
      {{ message.text }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

type MoodTag = 'happy' | 'calm' | 'sad' | 'angry' | 'tired' | 'anxious'

interface MoodOption {
  emoji: string
  value: MoodTag
  label: string
}

const MOOD_OPTIONS: readonly MoodOption[] = [
  { emoji: '😄', value: 'happy', label: '开心' },
  { emoji: '😌', value: 'calm', label: '平静' },
  { emoji: '😴', value: 'tired', label: '困倦' },
  { emoji: '😟', value: 'anxious', label: '焦虑' },
  { emoji: '😡', value: 'angry', label: '生气' },
  { emoji: '😢', value: 'sad', label: '难过' },
]

// 最大可选日期为今天
const maxDate = new Date().toISOString().slice(0, 10)

// 表单逻辑
const useMoodForm = () => {
  const form = reactive({
    date: new Date().toISOString().slice(0, 10),
    moodTag: 'happy' as MoodTag,
    content: '',
  })
  const setMood = (mood: MoodTag) => {
    form.moodTag = mood
  }
  const resetContent = () => {
    form.content = ''
  }
  const getSubmitData = () => ({ date: form.date, moodTag: form.moodTag, content: form.content })
  return { form, setMood, resetContent, getSubmitData }
}

// 提示消息
const useToastMessage = () => {
  const message = reactive({ text: '', type: 'success' as 'success' | 'error' })
  const show = (text: string, type: 'success' | 'error' = 'success') => {
    message.text = text
    message.type = type
    setTimeout(() => {
      message.text = ''
    }, 2000)
  }
  return { message, show }
}

const { form, setMood, resetContent, getSubmitData } = useMoodForm()
const { message, show: showToast } = useToastMessage()
const submitting = ref(false)

const emit = defineEmits<{
  (e: 'submit', data: { date: string; moodTag: MoodTag; content: string }): void
  (e: 'success'): void
}>()

const handleSubmit = async () => {
  // 二次校验：日期不能大于今天
  const selectedDate = form.date
  if (selectedDate > maxDate) {
    showToast('不能记录未来日期的日记', 'error')
    return
  }
  if (!form.content.trim()) {
    showToast('请填写备注内容', 'error')
    return
  }
  submitting.value = true
  try {
    emit('submit', getSubmitData())
    resetContent()
    showToast('保存成功！', 'success')
    setTimeout(() => {
      emit('success')
    }, 800)
  } catch {
    showToast('保存失败，请重试', 'error')
  } finally {
    submitting.value = false
  }
}
</script>
