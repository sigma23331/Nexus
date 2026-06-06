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
            :src="getValidAvatar(card.owner.avatar)"
            class="w-full h-full object-cover"
            alt="头像"
            @error="handleAvatarError"
          />
        </div>
        <div>
          <div class="flex items-center gap-1 flex-wrap">
            <p class="text-sm font-semibold text-slate-800">{{ card.owner.nickname }}</p>
            <!-- 已佩戴徽章展示区域 -->
            <div class="flex items-center gap-0.5">
              <div v-for="badge in displayBadges" :key="badge.code" class="group relative">
                <img
                  :src="getBadgeIconUrl(badge.code, false)"
                  :alt="badge.name"
                  class="h-5 w-5 rounded-full object-contain transition-transform hover:scale-110"
                  @error="handleBadgeImageError"
                />
                <div
                  class="absolute top-full left-1/2 mt-1 hidden -translate-x-1/2 whitespace-nowrap rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-white group-hover:block z-10"
                >
                  {{ badge.name }} Lv.{{ badge.level }}
                </div>
              </div>
            </div>
          </div>
          <p class="text-xs text-slate-400">{{ formatTime(card.createdAt) }}</p>
        </div>
      </div>
      <div class="relative" v-if="isOwner">
        <button
          @click="showMenu = !showMenu"
          class="text-slate-400 hover:text-slate-600"
          aria-label="菜单"
        >
          ···
        </button>
        <div
          v-if="showMenu"
          class="absolute right-0 mt-1 w-28 bg-white border border-slate-200 rounded-lg shadow-lg z-10"
        >
          <button
            @click="confirmDelete"
            class="block w-full text-left px-4 py-2 text-sm text-rose-600 hover:bg-slate-50"
          >
            删除卡片
          </button>
        </div>
      </div>
      <div v-else class="w-8"></div>
    </div>

    <!-- 分割线：淡淡的一条线 -->
    <div class="border-t border-slate-300 mx-4 my-2"></div>

    <!-- 分享文案（独立于卡片外部） -->
    <div v-if="shareMessage" class="px-2 pb-2">
      <div class="bg-white/80 rounded-lg p-3 text-sm text-slate-600 shadow-sm">
        {{ shareMessage }}
      </div>
    </div>

    <!-- 卡片主要内容 -->
    <div class="px-4 pb-2">
      <!-- 图片卡片 -->
      <div v-if="hasValidImage" class="mb-2">
        <img :src="card.snapshotUrl" class="w-full rounded-xl border border-slate-200" />
      </div>

      <!-- 运势卡片 -->
      <div
        v-else-if="card.type === 'fortune'"
        class="fortune-card rounded-xl border border-amber-200 bg-gradient-to-br from-amber-50 to-rose-50 p-4"
      >
        <div class="text-center">
          <p class="text-sm font-semibold text-amber-700">心运岛 · 今日签文</p>
        </div>
        <!-- 运势标题 + 分数 -->
        <div class="flex justify-center mt-2">
          <div class="relative inline-block">
            <span
              class="rounded-full px-4 py-1.5 text-[28px] font-semibold font-lxgw text-[#B45309] bg-amber-50"
            >
              {{ fortuneTitle }}
            </span>
            <span class="absolute -bottom-0 -right-6 text-xs text-slate-600 px-1 rounded">
              {{ fortuneScore }} 分
            </span>
          </div>
        </div>

        <!-- 主签文 -->
        <div class="mt-4 text-center">
          <p class="text-lg font-bold text-slate-900">{{ fortuneMainContent }}</p>
        </div>

        <!-- 副签文 -->
        <div class="mt-2 text-center text-xs text-slate-500">{{ fortuneSubContent }}</div>

        <!-- 爱情、事业、健康、财富四项 -->
        <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
          <div
            class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
          >
            <span class="text-slate-500 w-7 flex-shrink-0">爱情</span>
            <span class="font-semibold text-pink-500 flex-1 break-words">{{ fortuneLove }}</span>
          </div>
          <div
            class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
          >
            <span class="text-slate-500 w-7 flex-shrink-0">事业</span>
            <span class="font-semibold text-blue-500 flex-1 break-words">{{ fortuneCareer }}</span>
          </div>
          <div
            class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
          >
            <span class="text-slate-500 w-7 flex-shrink-0">健康</span>
            <span class="font-semibold text-green-600 flex-1 break-words">{{ fortuneHealth }}</span>
          </div>
          <div
            class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
          >
            <span class="text-slate-500 w-7 flex-shrink-0">财富</span>
            <span class="font-semibold text-yellow-600 flex-1 break-words">{{
              fortuneWealth
            }}</span>
          </div>
        </div>

        <!-- 宜忌 -->
        <div class="mt-4 grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <div
              v-for="(item, idx) in fortuneYiList"
              :key="idx"
              class="rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-700 inline-block"
            >
              宜：{{ item }}
            </div>
            <div
              v-if="!fortuneYiList.length"
              class="rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-700 inline-block"
            >
              宜：--
            </div>
          </div>
          <div class="space-y-1.5">
            <div
              v-for="(item, idx) in fortuneJiList"
              :key="idx"
              class="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700 inline-block"
            >
              忌：{{ item }}
            </div>
            <div
              v-if="!fortuneJiList.length"
              class="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700 inline-block"
            >
              忌：--
            </div>
          </div>
        </div>

        <div class="mt-2 text-right text-[12px] text-amber-600/80">{{ dateText }}</div>
      </div>

      <!-- 答案卡片 -->
      <div
        v-else
        class="answer-card rounded-xl border border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 p-4"
      >
        <div class="text-center mb-3">
          <span class="text-2xl">✨</span>
          <p class="text-xs text-purple-700/80">心运岛 · 答案之书</p>
        </div>
        <div class="whitespace-pre-wrap text-sm text-slate-700">{{ cardInnerContent }}</div>
        <div
          class="text-right text-[12px] text-purple-600/80 border-t border-purple-200/60 pt-2 mt-2"
        >
          {{ dateText }}
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div
      class="flex items-center justify-between px-4 text-xs text-slate-500 mt-1"
      :class="showComments ? 'pb-2' : 'pb-4'"
    >
      <div class="flex items-center gap-4">
        <button @click="toggleLike" class="flex items-center gap-1 transition">
          <span class="text-base">{{ card.stats.isLiked ? '❤️' : '🤍' }}</span>
          <span>{{ card.stats.likes }}</span>
        </button>
        <button
          type="button"
          class="flex items-center gap-1 transition hover:text-purple-600"
          @click="toggleComments"
        >
          <span class="text-base">💬</span>
          <span>{{ commentsCount }}</span>
        </button>
      </div>
      <span class="text-xs text-slate-500">{{
        card.type === 'fortune' ? '运势卡片' : '答案卡片'
      }}</span>
    </div>

    <PlazaCommentPanel
      v-if="showComments"
      :card-id="card.cardId"
      :comments-count="commentsCount"
      @update:comments-count="onCommentsCountUpdate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import PlazaCommentPanel from './PlazaCommentPanel.vue'
import { getValidAvatar } from '@/utils/avatar'
import { getBadgeIconUrl, BADGE_SORT_MAP } from '@/utils/badgeUtils'
import type { EquippedBadge } from '@/api/badge'

export interface PlazaCardData {
  cardId: string
  type: 'fortune' | 'answer'
  owner: {
    uid: string
    nickname: string
    avatar: string
    badges?: EquippedBadge[]
  }
  snapshotUrl: string
  content?: string
  stats: {
    likes: number
    comments: number
    isLiked: boolean
  }
  createdAt: string
}

const props = defineProps<{
  card: PlazaCardData
  isOwner: boolean
}>()

const emit = defineEmits<{
  (e: 'like', cardId: string, isLiked: boolean): void
  (e: 'delete', cardId: string): void
  (e: 'update-comments', cardId: string, count: number): void
}>()

const showMenu = ref(false)
const showComments = ref(false)
const commentsCount = ref(props.card.stats.comments ?? 0)

// 展示徽章
const displayBadges = computed(() => {
  const badges = props.card.owner.badges || []
  return [...badges].sort((a, b) => {
    // 等级降序
    if (a.level !== b.level) {
      return b.level - a.level
    }
    // 等级相同：按徽章序号升序
    const sortA = BADGE_SORT_MAP[a.code] ?? 999
    const sortB = BADGE_SORT_MAP[b.code] ?? 999
    return sortA - sortB
  })
})

watch(
  () => props.card.stats.comments,
  (value) => {
    commentsCount.value = value ?? 0
  },
)

const toggleComments = () => {
  showComments.value = !showComments.value
}

const onCommentsCountUpdate = (count: number) => {
  commentsCount.value = count
  emit('update-comments', props.card.cardId, count)
}

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

const confirmDelete = () => {
  if (confirm('确定要删除这张卡片吗？删除后不可恢复。')) {
    emit('delete', props.card.cardId)
    showMenu.value = false
  }
}

const fallbackAvatar = 'https://placehold.co/100x100/FDE68A/8B5CF6?text=U'
const handleAvatarError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== fallbackAvatar) {
    img.src = fallbackAvatar
  }
}

const handleBadgeImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src =
    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2394A3B8"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/%3E%3C/svg%3E'
}

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

const fullContent = computed(() => props.card.content || '')
const getCleanedContent = () => {
  let start = 0
  if (shareMessage.value) {
    const idx = fullContent.value.indexOf('\n\n')
    if (idx !== -1) start = idx + 2
  }
  return fullContent.value.slice(start).trim()
}

const fortuneTitle = computed(() => {
  const rest = getCleanedContent()
  const firstLine = rest.split('\n')[0] || ''
  const cleaned = firstLine
    .replace(/✨/, '')
    .replace(/[（(][^）)]*[）)]/g, '')
    .trim()
  return cleaned
})

const fortuneScore = computed(() => {
  const rest = getCleanedContent()
  const match = rest.match(/(\d+)\s*分/)
  return match ? match[1] : '0'
})

const fortuneMainContent = computed(() => {
  const rest = getCleanedContent()
  const linesArr = rest.split('\n')
  return linesArr[1] || ''
})

const fortuneSubContent = computed(() => {
  const rest = getCleanedContent()
  const linesArr = rest.split('\n')
  return linesArr[2] || ''
})

const extractField = (fieldName: string): string => {
  const rest = getCleanedContent()
  const lines = rest.split('\n')
  for (const line of lines) {
    if (line.startsWith(fieldName + '：') || line.startsWith(fieldName + ':')) {
      return line.replace(/^(爱情|事业|健康|财富)[：:]/, '').trim()
    }
  }
  return '--'
}

const fortuneLove = computed(() => extractField('爱情'))
const fortuneCareer = computed(() => extractField('事业'))
const fortuneHealth = computed(() => extractField('健康'))
const fortuneWealth = computed(() => extractField('财富'))

const fortuneYi = computed(() => {
  const rest = getCleanedContent()
  const yiLine = rest.split('\n').find((l) => l.startsWith('宜：')) || ''
  return yiLine.replace('宜：', '')
})

const fortuneJi = computed(() => {
  const rest = getCleanedContent()
  const jiLine = rest.split('\n').find((l) => l.startsWith('忌：')) || ''
  return jiLine.replace('忌：', '')
})

const splitYiJi = (str: string): string[] => {
  if (!str || str === '--') return []
  return str.split(/[、，, ]+/).filter((s) => s.trim().length > 0)
}

const fortuneYiList = computed(() => splitYiJi(fortuneYi.value))
const fortuneJiList = computed(() => splitYiJi(fortuneJi.value))
</script>

<style scoped>
.font-lxgw {
  font-family: 'KaiTi', '楷体', cursive;
}

.fortune-card,
.answer-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>
