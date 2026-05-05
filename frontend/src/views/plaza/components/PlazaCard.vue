<template>
  <div
    class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition hover:shadow-md"
  >
    <!-- 卡片头部 -->
    <div class="flex items-start justify-between p-4 pb-2">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center text-lg"
        >
          {{ card.owner.avatar }}
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-800">{{ card.owner.nickname }}</p>
          <p class="text-xs text-slate-400">{{ formatTime(card.createdAt) }}</p>
        </div>
      </div>
      <button class="text-slate-400 hover:text-slate-600">···</button>
    </div>

    <!-- 卡片内容 -->
    <div class="px-4 pb-2">
      <p class="text-sm text-slate-700">{{ card.content || '暂无内容' }}</p>
    </div>

    <!-- 卡片图片区域 -->
    <div class="px-4 pb-3">
      <div class="rounded-xl border border-slate-200 bg-slate-100 p-6 text-center">
        <div class="text-3xl mb-2">📇</div>
        <p class="text-sm font-medium text-slate-600">
          {{ card.type === 'fortune' ? '运势卡片' : '答案卡片' }}
        </p>
        <p class="text-xs text-slate-400 mt-1">快照预览 · 占位图</p>
      </div>
    </div>

    <!-- 底部按钮：只保留点赞和分享，移除评论 -->
    <div class="flex items-center justify-between px-4 pb-4 text-xs text-slate-500">
      <div class="flex items-center gap-4">
        <button @click="toggleLike" class="flex items-center gap-1 transition">
          <span class="text-base">{{ card.stats.isLiked ? '❤️' : '🤍' }}</span>
          <span>{{ card.stats.likes }}</span>
        </button>
        <button class="flex items-center gap-1">
          <span class="text-base">🔗</span>
          <span>分享</span>
        </button>
      </div>
      <span class="text-xs text-slate-400">{{
        card.type === 'fortune' ? '运势卡片' : '答案卡片'
      }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface PlazaCardData {
  cardId: string
  type: 'fortune' | 'answer'
  owner: {
    uid: string
    nickname: string
    avatar: string
  }
  snapshotUrl: string
  content?: string
  stats: {
    likes: number
    isLiked: boolean
  }
  createdAt: string
}

const props = defineProps<{
  card: PlazaCardData
}>()

const emit = defineEmits<{
  (e: 'like', cardId: string, isLiked: boolean): void
}>()

const formatTime = (isoString: string) => {
  const date = new Date(isoString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}/${month}/${day} ${hours}:${minutes}`
}

const toggleLike = () => {
  emit('like', props.card.cardId, !props.card.stats.isLiked)
}
</script>
