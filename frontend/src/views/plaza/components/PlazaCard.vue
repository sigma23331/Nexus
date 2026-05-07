<template>
  <div
    class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition hover:shadow-md"
  >
    <!-- 卡片头部 -->
    <div class="flex items-start justify-between p-4 pb-2">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center overflow-hidden"
        >
          <img
            v-if="isValidAvatarUrl"
            :src="card.owner.avatar"
            class="w-full h-full object-cover"
            alt="头像"
          />
          <span v-else class="text-lg">{{ defaultAvatar }}</span>
        </div>
        <div>
          <p class="text-sm font-semibold text-slate-800">{{ card.owner.nickname }}</p>
          <p class="text-xs text-slate-400">{{ formatTime(card.createdAt) }}</p>
        </div>
      </div>
      <button class="text-slate-400 hover:text-slate-600">···</button>
    </div>

    <!-- 分享文案（独立于卡片外部） -->
    <div v-if="shareMessage" class="px-4 pb-2">
      <div
        class="bg-white/80 rounded-lg p-3 text-sm text-purple-800 border border-purple-200 shadow-sm"
      >
        {{ shareMessage }}
      </div>
    </div>

    <!-- 卡片内容：图片或牛皮卷文本卡片 -->
    <div class="px-4 pb-2">
      <div v-if="hasValidImage" class="mb-2">
        <img :src="card.snapshotUrl" class="w-full rounded-xl border border-slate-200" />
      </div>
      <div v-else class="text-card rounded-xl border border-amber-200 bg-amber-50 p-4">
        <div class="text-center mb-3">
          <span class="text-2xl">📖</span>
          <p class="text-xs text-amber-700/80">心运岛 · 答案之书</p>
        </div>
        <div class="whitespace-pre-wrap text-sm text-slate-700">
          {{ cardInnerContent }}
        </div>
        <div
          class="text-right text-[10px] text-amber-600/60 border-t border-amber-200/60 pt-2 mt-2"
        >
          {{ dateText }}
        </div>
      </div>
    </div>

    <!-- 底部按钮：只保留点赞和卡片类型标识，移除分享按钮 -->
    <div class="flex items-center justify-between px-4 pb-4 text-xs text-slate-500">
      <div class="flex items-center gap-4">
        <button @click="toggleLike" class="flex items-center gap-1 transition">
          <span class="text-base">{{ card.stats.isLiked ? '❤️' : '🤍' }}</span>
          <span>{{ card.stats.likes }}</span>
        </button>
      </div>
      <span class="text-xs text-slate-400">{{
        card.type === 'fortune' ? '运势卡片' : '答案卡片'
      }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

const isValidAvatarUrl = computed(() => {
  const avatar = props.card.owner.avatar
  return avatar && (avatar.startsWith('http') || avatar.startsWith('data:image'))
})

const defaultAvatar = computed(() => {
  const nickname = props.card.owner.nickname
  if (nickname && nickname.length) {
    return nickname.charAt(0).toUpperCase()
  }
  return '👤'
})

const hasValidImage = computed(() => {
  const url = props.card.snapshotUrl
  if (!url || !url.startsWith('http')) return false
  if (url.includes('placehold.co') || url.includes('picsum.photos')) return false
  return true
})

const shareMessage = computed(() => {
  const content = props.card.content
  if (!content) return ''
  const match = content.match(/^✨\s*(.+?)(?=\n\n|$)/s)
  if (match && match[1]) {
    return match[1].trim()
  }
  return ''
})

const cardInnerContent = computed(() => {
  let content = props.card.content || ''
  const match = content.match(/^✨\s*.+?\n\n/s)
  if (match) {
    content = content.slice(match[0].length)
  }
  return content.trim() || '✨ 暂无内容'
})

const dateText = computed(() => {
  return formatTime(props.card.createdAt).slice(0, 10)
})
</script>

<style scoped>
.text-card {
  background: #fef7e0;
  background-image:
    radial-gradient(circle at 25% 40%, rgba(210, 180, 140, 0.08) 2%, transparent 2.5%),
    radial-gradient(circle at 70% 85%, rgba(160, 120, 80, 0.06) 1.8%, transparent 2%);
  background-size:
    40px 40px,
    35px 35px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>
