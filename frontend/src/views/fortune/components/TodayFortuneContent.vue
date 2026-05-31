<template>
  <div class="space-y-0">
    <!-- 运势标题（居中，右下角带分数） -->
    <div class="flex justify-center">
      <div class="relative inline-block">
        <span
          class="rounded-full px-4 py-1.5 text-[32px] font-semibold font-lxgw text-[#B45309] bg-amber-50"
        >
          {{ title }}
        </span>
        <span class="absolute -bottom-0 -right-6 text-xs text-slate-600 bg-white/80 px-1 rounded">
          {{ score }} 分
        </span>
      </div>
    </div>
    <!-- 签文内容卡片 -->
    <div class="rounded-2xl border border-amber-100 bg-amber-50/60 px-4 py-5 text-center">
      <p class="text-lg font-semibold text-slate-900">{{ contentMain }}</p>
      <p class="mt-2 text-xs text-amber-700">{{ contentSub }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  score: number
  contentMain: string
  contentSub: string
}>()
</script>

<style scoped>
.font-lxgw {
  font-family: 'LXGW WenKai', '霞鹜文楷', 'KaiTi', '楷体', cursive;
}
</style>
