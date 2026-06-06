<template>
  <div class="flex gap-2">
    <div
      class="w-8 h-8 shrink-0 rounded-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center overflow-hidden text-sm"
    >
      <img
        :src="getValidAvatar(comment.owner.avatar)"
        class="w-full h-full object-cover"
        alt=""
        @error="handleAvatarError"
      />
    </div>
    <div class="min-w-0 flex-1">
      <div class="flex items-baseline gap-1 flex-wrap">
        <span class="text-xs font-semibold text-slate-700">{{ comment.owner.nickname }}</span>
        <!-- 已佩戴徽章展示区域（小尺寸） -->
        <div class="flex items-center gap-0.5">
          <div v-for="badge in displayBadges" :key="badge.code" class="group relative">
            <img
              :src="getBadgeIconUrl(badge.code, false)"
              :alt="badge.name"
              class="h-4 w-4 rounded-full object-contain transition-transform hover:scale-110"
              @error="handleBadgeImageError"
            />
            <div
              class="absolute bottom-full left-1/2 mb-1 hidden -translate-x-1/2 whitespace-nowrap rounded bg-slate-800 px-1.5 py-0.5 text-[9px] text-white group-hover:block z-10"
            >
              {{ badge.name }} Lv.{{ badge.level }}
            </div>
          </div>
        </div>
        <span v-if="isReply && comment.replyToUser" class="text-[10px] text-slate-400">
          回复 @{{ comment.replyToUser.nickname }}
        </span>
        <span class="text-[10px] text-slate-400">{{ formatTime(comment.createdAt) }}</span>
      </div>
      <p class="mt-0.5 text-sm text-slate-700 break-words whitespace-pre-wrap">
        {{ comment.content }}
      </p>
      <div class="mt-1 flex gap-3 text-[10px]">
        <button
          v-if="!isReply"
          type="button"
          class="text-slate-500 hover:text-purple-600"
          @click="emit('reply', comment)"
        >
          回复
        </button>
        <button
          v-if="comment.canDelete"
          type="button"
          class="text-slate-500 hover:text-rose-600"
          @click="emit('delete', comment)"
        >
          删除
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getValidAvatar } from '@/utils/avatar'
import { getBadgeIconUrl, BADGE_SORT_MAP } from '@/utils/badgeUtils'
import type { PlazaComment } from '@/types/models'
import type { EquippedBadge } from '@/api/badge'

// 扩展 PlazaComment 的 owner 类型以包含 badges
interface ExtendedPlazaComment extends PlazaComment {
  owner: PlazaComment['owner'] & {
    badges?: EquippedBadge[]
  }
}

const props = defineProps<{
  comment: ExtendedPlazaComment
  isReply?: boolean
}>()

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

// 展示徽章
const displayBadges = computed(() => {
  const badges = props.comment.owner.badges || []
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

const emit = defineEmits<{
  (e: 'reply', comment: ExtendedPlazaComment): void
  (e: 'delete', comment: ExtendedPlazaComment): void
}>()

const formatTime = (iso: string) => {
  const d = new Date(iso)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60_000) return '刚刚'
  if (diff < 3600_000) return `${Math.floor(diff / 60_000)} 分钟前`
  if (diff < 86400_000) return `${Math.floor(diff / 3600_000)} 小时前`
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${m}/${day} ${h}:${min}`
}
</script>
