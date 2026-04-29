<template>
  <div
    class="overflow-hidden rounded-2xl border border-violet-200 bg-gradient-to-br from-violet-50 via-white to-amber-50"
  >
    <div class="border-b border-violet-100 px-4 py-3">
      <p class="text-xs font-semibold tracking-wide text-violet-700">心运岛 · 今日运势卡</p>
    </div>

    <div class="space-y-3 px-4 py-4">
      <div class="flex items-center justify-between">
        <p class="text-base font-semibold text-slate-900">{{ title }}</p>
        <span class="rounded-full bg-violet-100 px-2.5 py-1 text-xs font-semibold text-violet-700">
          {{ score }} 分
        </span>
      </div>

      <p class="text-sm font-medium text-slate-800">{{ contentMain }}</p>
      <p class="text-xs text-slate-500">{{ contentSub }}</p>

      <div class="grid grid-cols-2 gap-3 text-xs">
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2">
          <p class="font-semibold text-emerald-700">宜</p>
          <p class="mt-1 text-emerald-700">{{ yiPreview }}</p>
        </div>
        <div class="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2">
          <p class="font-semibold text-rose-700">忌</p>
          <p class="mt-1 text-rose-700">{{ jiPreview }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  score: number
  contentMain: string
  contentSub: string
  yi: string[]
  ji: string[]
}>()

const yiPreview = computed(() => props.yi.slice(0, 2).join('、') || '顺势而为')
const jiPreview = computed(() => props.ji.slice(0, 2).join('、') || '急躁冒进')
</script>
