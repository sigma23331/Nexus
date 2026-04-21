<template>
  <div class="min-h-screen bg-[#0f0a1e] text-white pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">👤</span>
      <h1 class="text-2xl font-bold">我的</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section>
        <h2 class="text-lg font-semibold mb-3">快捷入口</h2>
        <ul class="space-y-2">
          <li class="p-3 bg-white/5 rounded-xl">⭐ 收藏的答案</li>
          <li class="p-3 bg-white/5 rounded-xl">📅 历史运势记录</li>
          <li class="p-3 bg-white/5 rounded-xl">⚙️ 偏好设置</li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">偏好设置</h2>
        <div class="space-y-4">
          <label class="block text-sm">默认运势模式
            <select class="w-full mt-1 bg-white/10 border border-white/20 rounded-lg p-2">
              <option>星座</option>
              <option>生肖</option>
              <option>塔罗</option>
            </select>
          </label>
          <label class="block text-sm">心情标签
            <input type="text" placeholder="平静, 忙碌" class="w-full mt-1 bg-white/10 border border-white/20 rounded-lg p-2">
          </label>
          <button class="w-full bg-purple-600 rounded-xl py-2">保存</button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">情绪日记本</h2>
        <div class="space-y-4">
          <label class="block text-sm">日期
            <input type="date" value="2026-04-19" class="w-full mt-1 bg-white/10 border border-white/20 rounded-lg p-2">
          </label>
          <label class="block text-sm">心情
            <select class="w-full mt-1 bg-white/10 border border-white/20 rounded-lg p-2">
              <option>好</option>
              <option>一般</option>
              <option>差</option>
            </select>
          </label>
          <label class="block text-sm">备注
            <textarea rows="2" class="w-full mt-1 bg-white/10 border border-white/20 rounded-lg p-2"></textarea>
          </label>
          <button class="w-full bg-purple-600 rounded-xl py-2">保存日记</button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">个人运势图谱</h2>
        <div class="bg-white/5 rounded-xl p-6 text-center text-slate-400">📊 图表占位</div>
      </section>
    </main>
  </div>
</template>