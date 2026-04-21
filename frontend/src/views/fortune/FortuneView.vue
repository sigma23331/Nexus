<template>
  <div class="min-h-screen bg-[#0f0a1e] text-white pb-20">
    <!-- 头部 -->
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">✨</span>
      <h1 class="text-2xl font-bold">运势看板</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <!-- 维度来源（模式选择） -->
      <section>
        <h2 class="text-lg font-semibold mb-3">维度来源</h2>
        <div class="flex gap-4">
          <label class="text-sm text-slate-300">模式
            <select class="ml-2 bg-white/10 border border-white/20 rounded-lg px-3 py-1 text-sm">
              <option>星座</option>
              <option>生肖</option>
              <option>塔罗</option>
            </select>
          </label>
        </div>
      </section>

      <!-- 今日概览 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">今日概览</h2>
        <ul class="space-y-2">
          <li class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-pink-400"></span>爱情：中上</li>
          <li class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-blue-400"></span>事业：平稳</li>
          <li class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-green-400"></span>健康：注意作息</li>
          <li class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-yellow-400"></span>财富：谨慎消费</li>
        </ul>
      </section>

      <!-- 宜/忌 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">宜 / 忌</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
            <p class="text-green-400 font-bold mb-2">宜</p>
            <ul class="text-sm space-y-1 text-slate-300">
              <li>• 喝奶茶</li>
              <li>• 摸鱼五分钟</li>
            </ul>
          </div>
          <div class="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
            <p class="text-red-400 font-bold mb-2">忌</p>
            <ul class="text-sm space-y-1 text-slate-300">
              <li>• 熬夜</li>
              <li>• 已读不回</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 运势轨迹（占位，后续用 ECharts） -->
      <section>
        <h2 class="text-lg font-semibold mb-3">运势轨迹</h2>
        <div class="bg-white/5 rounded-xl p-6 text-center text-slate-400">📈 图表占位</div>
      </section>

      <!-- 运势卡片生成 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">运势卡片</h2>
        <div class="bg-white/5 rounded-xl p-6 text-center text-slate-400">🖼️ 卡片预览占位</div>
        <div class="flex gap-3 mt-4">
          <button class="flex-1 bg-purple-600 hover:bg-purple-700 rounded-xl py-2 text-sm font-medium">生成卡片</button>
          <button class="flex-1 bg-white/10 border border-white/20 rounded-xl py-2 text-sm font-medium">分享</button>
        </div>
      </section>
    </main>
  </div>
</template>