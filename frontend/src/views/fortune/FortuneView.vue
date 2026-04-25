<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 头部 -->
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">✨</span>
      <h1 class="text-2xl font-bold">运势看板</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <!-- 今日签文 -->
      <section class="relative overflow-hidden rounded-3xl border border-amber-200 bg-white p-5 shadow-sm">
        <div class="absolute -top-10 -right-10 h-24 w-24 rounded-full bg-amber-100"></div>
        <div class="absolute -bottom-10 -left-10 h-24 w-24 rounded-full bg-rose-100"></div>
        <div class="relative space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold tracking-wide text-amber-700">今日签文</span>
            <span class="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
              上上签
            </span>
          </div>
          <div class="rounded-2xl border border-amber-100 bg-amber-50/60 px-4 py-5 text-center">
            <p class="text-lg font-semibold text-slate-900">风起云开，顺遂自来</p>
            <p class="mt-2 text-xs text-amber-700">今日宜稳中求进，心静则通达</p>
          </div>

          <div class="space-y-3">
            <h2 class="text-sm font-semibold text-slate-700">今日概览</h2>
            <ul class="grid grid-cols-2 gap-3 text-sm">
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">爱情</span>
                <span class="ml-2 font-semibold text-pink-500">中上</span>
              </li>
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">事业</span>
                <span class="ml-2 font-semibold text-blue-500">平稳</span>
              </li>
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">健康</span>
                <span class="ml-2 font-semibold text-green-600">注意作息</span>
              </li>
              <li class="rounded-xl border border-slate-200 bg-white px-3 py-2">
                <span class="text-slate-500">财富</span>
                <span class="ml-2 font-semibold text-yellow-600">谨慎消费</span>
              </li>
            </ul>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-3">
              <p class="text-xs font-semibold text-emerald-700">宜</p>
              <ul class="mt-2 text-sm text-emerald-700 space-y-1">
                <li>• 喝奶茶</li>
                <li>• 摸鱼五分钟</li>
              </ul>
            </div>
            <div class="rounded-2xl border border-rose-200 bg-rose-50 p-3">
              <p class="text-xs font-semibold text-rose-700">忌</p>
              <ul class="mt-2 text-sm text-rose-700 space-y-1">
                <li>• 熬夜</li>
                <li>• 已读不回</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- 运势轨迹（占位，后续用 ECharts） -->
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
