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
          <button class="flex-1 bg-purple-600 rounded-xl py-2 text-white">生成运势卡片</button>
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
          <button class="w-full bg-purple-600 rounded-xl py-2 text-white">分享到微信</button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">分享广场</h2>
        <ul class="space-y-4">
          <li
            v-for="card in cards"
            :key="card.id"
            class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="h-10 w-10 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center text-sm"
                >
                  {{ card.avatar }}
                </div>
                <div>
                  <p class="text-sm font-semibold text-slate-900">{{ card.nickname }}</p>
                  <p class="text-xs text-slate-400">{{ card.time }}</p>
                </div>
              </div>
              <button class="text-xs text-slate-400">···</button>
            </div>
            <p class="mt-3 text-sm text-slate-700">{{ card.content }}</p>
            <div class="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-center">
              <p class="text-xs text-slate-400">{{ card.cardType }}预览</p>
              <p class="mt-1 text-sm font-semibold text-slate-700">{{ card.cardTitle }}</p>
            </div>
            <div class="mt-3 flex items-center justify-between text-xs text-slate-500">
              <div class="flex items-center gap-4">
                <button class="flex items-center gap-1" @click="toggleLike(card.id)">
                  {{ card.liked ? '❤️' : '🤍' }} {{ card.likes }}
                </button>
                <button class="flex items-center gap-1">💬 {{ card.comments }}</button>
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
          <button class="w-full bg-purple-600 rounded-xl py-2 text-white">发起 PK</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// ==================== 静态数据（暂未连接 Pinia） ====================
const cards = ref([
  {
    id: 1,
    avatar: '🐱',
    nickname: '路过的猫',
    time: '今天 09:12',
    content: '签文说今日宜请假，老板不信，我信了。',
    cardType: '📌 运势卡片',
    cardTitle: '上上签 · 风起云开',
    likes: 128,
    liked: false,
    comments: 36,
  },
  {
    id: 2,
    avatar: '🐰',
    nickname: '周二困难户',
    time: '今天 10:45',
    content: '答案让我别内耗——然后我内耗了半小时要不要信它。',
    cardType: '📌 答案卡片',
    cardTitle: '宇宙说：放下执着',
    likes: 76,
    liked: false,
    comments: 14,
  },
])

function toggleLike(id: number) {
  const card = cards.value.find((c) => c.id === id)
  if (card) {
    card.liked = !card.liked
    card.likes += card.liked ? 1 : -1
  }
}

// ==================== Pinia 接入示例（注释） ====================
/*
import { usePlazaStore } from '@/stores/plaza'
import { computed } from 'vue'

const plazaStore = usePlazaStore()

// 从 store 读取卡片列表
const cards = computed(() => plazaStore.cards)

// 点赞操作
const toggleLike = (cardId: string) => {
  const card = cards.value.find(c => c.cardId === cardId)
  if (card) {
    const action = card.stats.isLiked ? 'unlike' : 'like'
    plazaStore.likeCard(cardId, !card.stats.isLiked, card.stats.likes + (action === 'like' ? 1 : -1))
    // 调用 API：postPlazaLike(cardId, action)
  }
}

// 加载更多
const loadMore = async () => {
  if (plazaStore.hasMore) {
    const res = await getPlazaCards(plazaStore.currentTab, plazaStore.nextCursor)
    plazaStore.setCards(res.list, res.nextCursor, res.hasMore)
  }
}
*/
</script>
