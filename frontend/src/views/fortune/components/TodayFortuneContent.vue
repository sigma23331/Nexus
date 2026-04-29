<template>
  <div class="rounded-2xl border border-amber-100 bg-amber-50/60 px-4 py-5 text-center">
    <p class="text-[11px] font-semibold tracking-wide text-amber-700">今日运势内容</p>
    <p class="mt-2 text-lg font-semibold text-slate-900">{{ contentMain }}</p>
    <p class="mt-2 text-xs text-amber-700">{{ contentSub }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  contentMain: string
  contentSub: string
}>()
</script>
