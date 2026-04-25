<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">👤</span>
      <h1 class="text-2xl font-bold">我的</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section>
        <h2 class="text-lg font-semibold mb-3">快捷入口</h2>
        <ul class="space-y-2">
          <li class="p-3 bg-white border border-slate-200 rounded-xl">⭐ 收藏的答案</li>
          <li class="p-3 bg-white border border-slate-200 rounded-xl">📅 历史运势记录</li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">情绪日记本</h2>
        <div class="space-y-4">
          <label class="block text-sm"
            >日期
            <input
              type="date"
              value="2026-04-19"
              class="w-full mt-1 bg-white border border-slate-200 rounded-lg p-2 text-slate-800"
            />
          </label>
          <label class="block text-sm"
            >心情
            <div class="mt-2 grid grid-cols-6 gap-2">
              <button
                type="button"
                class="h-12 rounded-lg border border-slate-200 bg-white text-lg"
                aria-label="开心"
                title="开心"
              >
                😄
              </button>
              <button
                type="button"
                class="h-12 rounded-lg border border-slate-200 bg-white text-lg"
                aria-label="平静"
                title="平静"
              >
                😌
              </button>
              <button
                type="button"
                class="h-12 rounded-lg border border-slate-200 bg-white text-lg"
                aria-label="困倦"
                title="困倦"
              >
                😴
              </button>
              <button
                type="button"
                class="h-12 rounded-lg border border-slate-200 bg-white text-lg"
                aria-label="焦虑"
                title="焦虑"
              >
                😟
              </button>
              <button
                type="button"
                class="h-12 rounded-lg border border-slate-200 bg-white text-lg"
                aria-label="生气"
                title="生气"
              >
                😡
              </button>
              <button
                type="button"
                class="h-12 rounded-lg border border-slate-200 bg-white text-lg"
                aria-label="难过"
                title="难过"
              >
                😢
              </button>
            </div>
          </label>
          <label class="block text-sm"
            >备注
            <textarea
              rows="2"
              class="w-full mt-1 bg-white border border-slate-200 rounded-lg p-2 text-slate-800 placeholder:text-slate-400"
            ></textarea>
          </label>
          <button class="w-full bg-purple-600 rounded-xl py-2">保存日记</button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">个人运势图谱</h2>
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center text-slate-400">
          📊 图表占位
        </div>
      </section>
    </main>
  </div>
</template>
