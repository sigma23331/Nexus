<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 头部（不变） -->
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">✨</span>
      <h1 class="text-2xl font-bold">运势看板</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section
        class="relative overflow-hidden rounded-3xl border border-amber-200 bg-white p-5 shadow-sm"
      >
        <div class="absolute -top-10 -right-10 h-24 w-24 rounded-full bg-amber-100"></div>
        <div class="absolute -bottom-10 -left-10 h-24 w-24 rounded-full bg-rose-100"></div>
        <div class="relative space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold tracking-wide text-amber-700">今日签文</span>
            <!-- 运势分展示（本示例忽略，全站统计需要） -->
            <span class="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
              {{ fortuneData.title }}
            </span>
          </div>
          <div class="rounded-2xl border border-amber-100 bg-amber-50/60 px-4 py-5 text-center">
            <p class="text-lg font-semibold text-slate-900">{{ fortuneData.content_main }}</p>
            <p class="mt-2 text-xs text-amber-700">{{ fortuneData.content_sub }}</p>
          </div>

          <div class="space-y-3">
            <h2 class="text-sm font-semibold text-slate-700">今日概览</h2>
            <ul class="grid grid-cols-2 gap-3 text-sm">
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">爱情</span>
                <span class="ml-2 font-semibold text-pink-500">{{ fortuneData.love }}</span>
              </li>
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">事业</span>
                <span class="ml-2 font-semibold text-blue-500">{{ fortuneData.career }}</span>
              </li>
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">健康</span>
                <span class="ml-2 font-semibold text-green-600">{{ fortuneData.health }}</span>
              </li>
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">财富</span>
                <span class="ml-2 font-semibold text-yellow-600">{{ fortuneData.wealth }}</span>
              </li>
            </ul>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-3">
              <p class="text-xs font-semibold text-emerald-700">宜</p>
              <ul class="mt-2 text-sm text-emerald-700 space-y-1">
                <li v-for="item in fortuneData.yi" :key="item">• {{ item }}</li>
              </ul>
            </div>
            <div class="rounded-2xl border border-rose-200 bg-rose-50 p-3">
              <p class="text-xs font-semibold text-rose-700">忌</p>
              <ul class="mt-2 text-sm text-rose-700 space-y-1">
                <li v-for="item in fortuneData.ji" :key="item">• {{ item }}</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- 运势轨迹占位 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">运势轨迹</h2>
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center text-slate-400">
          📈 图表占位
        </div>
      </section>

      <!-- 运势卡片生成 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">运势卡片</h2>
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center text-slate-400">
          🖼️ 卡片预览占位
        </div>
        <div class="flex gap-3 mt-4">
          <button
            class="flex-1 bg-purple-600 hover:bg-purple-700 rounded-xl py-2 text-sm font-medium"
          >
            生成卡片
          </button>
          <button
            class="flex-1 bg-white border border-slate-200 text-slate-700 rounded-xl py-2 text-sm font-medium"
          >
            分享
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// import { useFortuneStore } from '@/stores/fortune'

// 静态数据（临时，后续替换为 store）
const fortuneData = ref({
  id: 'demo_1',
  date: '2026-04-26',
  score: 88,
  title: '上上签',
  content_main: '风起云开，顺遂自来',
  content_sub: '今日宜稳中求进，心静则通达',
  love: '中上',
  career: '平稳',
  health: '注意作息',
  wealth: '谨慎消费',
  yi: ['喝奶茶', '摸鱼五分钟'],
  ji: ['熬夜', '已读不回'],
})

// ===== Pinia 接入示例（注释保留） =====
// 1. 引入 store
// const fortuneStore = useFortuneStore()
//
// 2. 从 store 读取数据（假设已经通过 API 设置过）
// const fortuneData = computed(() => {
//   if (fortuneStore.todayFortune) {
//     return fortuneStore.todayFortune
//   } else {
//     // 降级：使用静态数据或展示占位
//     return fallbackFortune
//   }
// })
//
// 3. 在 mounted 中请求数据并存入 store
// onMounted(async () => {
//   if (!fortuneStore.todayFortune) {
//     const data = await getFortuneToday()  // 调用 API
//     fortuneStore.setTodayFortune(data)
//   }
// })
//
// 4. 注意：getFortuneToday 需要定义在 src/api/fortune.ts 中

// 为了不破坏当前显示，暂时不调用真实 API，保留静态数据
</script>
