<template>
  <div class="min-h-screen bg-[#0f0a1e] text-white pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">💬</span>
      <h1 class="text-2xl font-bold">分享社交</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section>
        <h2 class="text-lg font-semibold mb-3">生成与分享</h2>
        <div class="flex gap-3">
          <button class="flex-1 bg-purple-600 rounded-xl py-2">生成运势卡片</button>
          <button class="flex-1 bg-white/10 border border-white/20 rounded-xl py-2">
            生成答案卡片
          </button>
        </div>
        <div class="mt-4 bg-white/5 rounded-xl p-6 text-center text-slate-400">🖼️ 卡片预览占位</div>
        <div class="mt-4">
          <button class="w-full bg-purple-600 rounded-xl py-2">分享到微信</button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">分享广场</h2>
        <ul class="space-y-3">
          <li class="p-3 bg-white/5 rounded-xl flex justify-between items-center">
            <span>@路过的猫：签文说今日宜请假，老板不信，我信了。</span>
            <button class="text-xs text-purple-400">评论</button>
          </li>
          <li class="p-3 bg-white/5 rounded-xl flex justify-between items-center">
            <span>@周二困难户：答案让我别内耗——然后我内耗了半小时要不要信它。</span>
            <button class="text-xs text-purple-400">评论</button>
          </li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">运势 PK / 好友对比</h2>
        <table class="w-full text-sm border border-white/10 rounded-xl overflow-hidden">
          <thead class="bg-white/5">
            <tr>
              <th class="p-2 text-left">项目</th>
              <th>我</th>
              <th>对方</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="p-2">今日综合</td>
              <td class="text-center">—</td>
              <td class="text-center">—</td>
            </tr>
            <tr>
              <td class="p-2">爱情</td>
              <td class="text-center">—</td>
              <td class="text-center">—</td>
            </tr>
          </tbody>
        </table>
        <div class="mt-4">
          <button class="w-full bg-purple-600 rounded-xl py-2">发起 PK</button>
        </div>
      </section>
    </main>
  </div>
</template>
