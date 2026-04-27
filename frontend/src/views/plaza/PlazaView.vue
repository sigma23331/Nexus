<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 头部 -->
    <!-- <header class="flex items-center justify-between px-6 pt-6 pb-2">
      <div class="flex items-center gap-2">
        <span class="text-2xl">💬</span>
        <h1 class="text-2xl font-bold">分享社交</h1>
      </div>
    </header> -->

    <main class="px-6 py-4 space-y-8">
      <!-- 运势 PK / 好友对比 -->
      <!-- <section>
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
      </section> -->

      <!-- 分享广场（带分类筛选） -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold">分享广场</h2>
          <!-- 分类筛选按钮组 -->
          <div class="flex gap-2">
            <button
              @click="filterType = 'all'"
              :class="[
                'px-3 py-1 text-sm rounded-full transition-colors',
                filterType === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              全部
            </button>
            <button
              @click="filterType = 'fortune'"
              :class="[
                'px-3 py-1 text-sm rounded-full transition-colors',
                filterType === 'fortune'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              运势卡片
            </button>
            <button
              @click="filterType = 'answer'"
              :class="[
                'px-3 py-1 text-sm rounded-full transition-colors',
                filterType === 'answer'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              答案卡片
            </button>
          </div>
        </div>
        <div class="space-y-4">
          <PlazaCard
            v-for="card in filteredCards"
            :key="card.cardId"
            :card="card"
            @like="handleLike"
          />
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PlazaCard from './components/PlazaCard.vue'
import type { PlazaCardData } from './components/PlazaCard.vue'

// 原始静态数据（保持原有结构）
const rawCards = ref([
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
  {
    id: 3,
    avatar: '🦊',
    nickname: '林深时见鹿',
    time: '昨天 18:30',
    content: '抽到了「勇往直前」，明天有个重要会议，心里有底了！',
    cardType: '📌 运势卡片',
    cardTitle: '中吉 · 勇往直前',
    likes: 245,
    liked: true,
    comments: 28,
  },
  {
    id: 4,
    avatar: '🐶',
    nickname: '沐沐酱',
    time: '昨天 14:15',
    content: '答案说“不要害怕改变”，我决定提交转岗申请了。',
    cardType: '📌 答案卡片',
    cardTitle: '宇宙说：拥抱变化',
    likes: 312,
    liked: false,
    comments: 47,
  },
  {
    id: 5,
    avatar: '🐼',
    nickname: '风间清',
    time: '4月25日',
    content: '今日宜深度睡眠，现在就去补觉！',
    cardType: '📌 运势卡片',
    cardTitle: '小吉 · 宜休养',
    likes: 89,
    liked: false,
    comments: 12,
  },
  {
    id: 6,
    avatar: '🐨',
    nickname: '小月',
    time: '4月24日',
    content: '放下执着，接受不完美。这句话真的治愈了我。',
    cardType: '📌 答案卡片',
    cardTitle: '宇宙说：放下执着',
    likes: 156,
    liked: true,
    comments: 21,
  },
  {
    id: 7,
    avatar: '🦁',
    nickname: '阿哲',
    time: '4月23日',
    content: '连续三天大吉，是不是该去买张彩票？',
    cardType: '📌 运势卡片',
    cardTitle: '大吉 · 诸事顺遂',
    likes: 520,
    liked: false,
    comments: 68,
  },
  {
    id: 8,
    avatar: '🐸',
    nickname: '蛙仔',
    time: '4月22日',
    content: '答案告诉我“答案就在你最初的想法里”，原来我早就知道该怎么做了。',
    cardType: '📌 答案卡片',
    cardTitle: '宇宙说：相信直觉',
    likes: 97,
    liked: false,
    comments: 8,
  },
])

// 辅助函数：根据原始数据生成符合 PlazaCardData 格式的对象
function convertToPlazaCard(raw: (typeof rawCards.value)[0]): PlazaCardData {
  // 生成一个合理的 createdAt 时间（基于 id 偏移，使相对时间显示自然）
  const now = new Date()
  const hoursOffset = raw.id * 2 // 每个卡片间隔 2 小时
  const createdAt = new Date(now.getTime() - hoursOffset * 60 * 60 * 1000).toISOString()

  // 判断卡片类型
  const type = raw.cardType.includes('运势') ? 'fortune' : 'answer'

  // 生成占位图片 URL（实际项目应使用真实 snapshotUrl）
  const snapshotUrl = `https://picsum.photos/seed/${raw.id}/400/200?random=${raw.id}`

  return {
    cardId: String(raw.id),
    type,
    owner: {
      uid: String(raw.id),
      nickname: raw.nickname,
      avatar: raw.avatar,
    },
    snapshotUrl,
    content: raw.content,
    stats: {
      likes: raw.likes,
      isLiked: raw.liked,
    },
    commentCount: raw.comments,
    createdAt,
  }
}

// 计算属性：原始数据 -> PlazaCard 所需数据
const convertedCards = computed(() => rawCards.value.map(convertToPlazaCard))

// 筛选类型：'all' | 'fortune' | 'answer'
const filterType = ref<'all' | 'fortune' | 'answer'>('all')

// 根据筛选类型过滤展示的卡片
const filteredCards = computed(() => {
  if (filterType.value === 'all') {
    return convertedCards.value
  }
  return convertedCards.value.filter((card) => card.type === filterType.value)
})

// 处理点赞事件
function handleLike(cardId: string, isLiked: boolean) {
  const rawCard = rawCards.value.find((c) => String(c.id) === cardId)
  if (rawCard) {
    rawCard.liked = isLiked
    rawCard.likes += isLiked ? 1 : -1
  }
}
</script>
