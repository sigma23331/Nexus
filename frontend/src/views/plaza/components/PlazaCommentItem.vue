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
      <div class="flex items-baseline gap-2 flex-wrap">
        <span class="text-xs font-semibold text-slate-700">{{ comment.owner.nickname }}</span>
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
import { getValidAvatar } from '@/utils/avatar'
import type { PlazaComment } from '@/types/models'

const fallbackAvatar = 'https://placehold.co/100x100/FDE68A/8B5CF6?text=U'

const handleAvatarError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== fallbackAvatar) {
    img.src = fallbackAvatar
  }
}

defineProps<{
  comment: PlazaComment
  isReply?: boolean
}>()

const emit = defineEmits<{
  (e: 'reply', comment: PlazaComment): void
  (e: 'delete', comment: PlazaComment): void
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
