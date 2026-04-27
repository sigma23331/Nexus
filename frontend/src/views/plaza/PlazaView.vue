<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">💬</span>
      <h1 class="text-2xl font-bold">分享社交</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section>
        <h2 class="text-lg font-semibold mb-3">生成与分享</h2>
        <div class="flex gap-3">
          <button class="flex-1 bg-purple-600 rounded-xl py-2">生成运势卡片</button>
          <button class="flex-1 bg-white border border-slate-200 text-slate-700 rounded-xl py-2">
            生成答案卡片
          </button>
        </div>
        <div
          class="mt-4 bg-slate-50 border border-slate-200 rounded-xl p-6 text-center text-slate-400"
        >
          🖼️ 卡片预览占位
        </div>
        <div class="mt-4">
          <button class="w-full bg-purple-600 rounded-xl py-2">分享到微信</button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">分享广场</h2>
        <ul class="space-y-4">
          <li class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="h-10 w-10 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center text-sm"
                >
                  🐱
                </div>
                <div>
                  <p class="text-sm font-semibold text-slate-900">路过的猫</p>
                  <p class="text-xs text-slate-400">今天 09:12</p>
                </div>
              </div>
              <button class="text-xs text-slate-400">···</button>
            </div>
            <p class="mt-3 text-sm text-slate-700">签文说今日宜请假，老板不信，我信了。</p>
            <div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
              <p class="text-xs text-slate-400">📌 运势卡片预览</p>
              <p class="mt-1 text-sm font-semibold text-slate-700">上上签 · 风起云开</p>
            </div>
            <div class="mt-3 flex items-center justify-between text-xs text-slate-500">
              <div class="flex items-center gap-4">
                <button class="flex items-center gap-1">❤️ 128</button>
                <button class="flex items-center gap-1">💬 36</button>
                <button class="flex items-center gap-1">🔗 分享</button>
              </div>
            </div>
          </li>
          <li class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="h-10 w-10 rounded-full bg-gradient-to-br from-blue-200 to-teal-200 flex items-center justify-center text-sm"
                >
                  🐰
                </div>
                <div>
                  <p class="text-sm font-semibold text-slate-900">周二困难户</p>
                  <p class="text-xs text-slate-400">今天 10:45</p>
                </div>
              </div>
              <button class="text-xs text-slate-400">···</button>
            </div>
            <p class="mt-3 text-sm text-slate-700">
              答案让我别内耗——然后我内耗了半小时要不要信它。
            </p>
            <div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
              <p class="text-xs text-slate-400">📌 答案卡片预览</p>
              <p class="mt-1 text-sm font-semibold text-slate-700">宇宙说：放下执着</p>
            </div>
            <div class="mt-3 flex items-center justify-between text-xs text-slate-500">
              <div class="flex items-center gap-4">
                <button class="flex items-center gap-1">❤️ 76</button>
                <button class="flex items-center gap-1">💬 14</button>
                <button class="flex items-center gap-1">🔗 分享</button>
              </div>
            </div>
          </li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">运势 PK / 好友对比</h2>
        <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center">
                🙂
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">我</p>
                <p class="text-xs text-slate-400">今日综合</p>
              </div>
            </div>
            <span class="text-lg font-semibold text-purple-600">—</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center">
                🧑
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">对方</p>
                <p class="text-xs text-slate-400">今日综合</p>
              </div>
            </div>
            <span class="text-lg font-semibold text-slate-400">—</span>
          </div>
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <p class="text-slate-500">爱情</p>
              <p class="mt-1 text-sm font-semibold text-pink-500">—</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <p class="text-slate-500">事业</p>
              <p class="mt-1 text-sm font-semibold text-blue-500">—</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <p class="text-slate-500">健康</p>
              <p class="mt-1 text-sm font-semibold text-green-600">—</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <p class="text-slate-500">财富</p>
              <p class="mt-1 text-sm font-semibold text-yellow-600">—</p>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <button class="w-full bg-purple-600 rounded-xl py-2">发起 PK</button>
        </div>
      </section>
    </main>
  </div>
</template>
