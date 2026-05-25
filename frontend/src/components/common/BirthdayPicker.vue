<!-- src/components/common/BirthdayPicker.vue -->
<template>
  <div class="flex gap-3">
    <!-- 年份 -->
    <select
      v-model="year"
      class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 appearance-none cursor-pointer"
      :class="{ 'text-slate-400': !year }"
    >
      <option value="">年</option>
      <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
    </select>

    <!-- 月份 -->
    <select
      v-model="month"
      :disabled="!year"
      class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 disabled:opacity-50 disabled:cursor-not-allowed appearance-none cursor-pointer"
      :class="{ 'text-slate-400': !month }"
    >
      <option value="">月</option>
      <option v-for="m in 12" :key="m" :value="m">{{ m }}</option>
    </select>

    <!-- 日期 -->
    <select
      v-model="day"
      :disabled="!year || !month"
      class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 disabled:opacity-50 disabled:cursor-not-allowed appearance-none cursor-pointer"
      :class="{ 'text-slate-400': !day }"
    >
      <option value="">日</option>
      <option v-for="d in dayOptions" :key="d" :value="d">{{ d }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  modelValue: string // 格式 YYYY-MM-DD 或空字符串
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// 年份范围：1900 ~ 当前年份
const currentYear = new Date().getFullYear()
const yearOptions = computed(() => {
  const years = []
  for (let y = currentYear; y >= 1900; y--) {
    years.push(y)
  }
  return years
})

// 内部绑定值（不带前导零的数字字符串）
const year = ref('')
const month = ref('')
const day = ref('')

// 根据年、月计算当月天数
const daysInMonth = computed(() => {
  if (!year.value || !month.value) return 0
  const y = parseInt(year.value)
  const m = parseInt(month.value)
  return new Date(y, m, 0).getDate()
})

// 可选的日期列表（1 ~ 当月最大天数）
const dayOptions = computed(() => {
  const max = daysInMonth.value
  if (!max) return []
  return Array.from({ length: max }, (_, i) => i + 1)
})

// 监听年/月变化，若当前选中的日期超出范围则重置
watch([year, month], () => {
  if (day.value && daysInMonth.value && parseInt(day.value) > daysInMonth.value) {
    day.value = ''
  }
})

// 三个值中任何一个变化，尝试生成最终日期并 emit
watch([year, month, day], () => {
  const y = year.value
  const m = month.value
  const d = day.value
  if (y && m && d) {
    const dateObj = new Date(parseInt(y), parseInt(m) - 1, parseInt(d))
    if (
      dateObj.getFullYear() === parseInt(y) &&
      dateObj.getMonth() + 1 === parseInt(m) &&
      dateObj.getDate() === parseInt(d)
    ) {
      const formatted = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      if (formatted !== props.modelValue) {
        emit('update:modelValue', formatted)
      }
      return
    }
  }
  // 不完整或无效日期，向外传递空字符串
  if (props.modelValue !== '') {
    emit('update:modelValue', '')
  }
})

// 监听外部传入的 modelValue，同步内部年/月/日（去掉前导零）
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal && /^\d{4}-\d{2}-\d{2}$/.test(newVal)) {
      const [y, m, d] = newVal.split('-')
      // 去掉前导零，转为数字再转字符串，确保不带前导零
      const yearStr = String(parseInt(y))
      const monthStr = String(parseInt(m))
      const dayStr = String(parseInt(d))
      if (yearStr !== year.value) year.value = yearStr
      if (monthStr !== month.value) month.value = monthStr
      if (dayStr !== day.value) day.value = dayStr
    } else {
      // 空值或无效格式，清空
      if (year.value) year.value = ''
      if (month.value) month.value = ''
      if (day.value) day.value = ''
    }
  },
  { immediate: true },
)
</script>
