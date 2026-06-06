<template>
  <div
    class="flex cursor-pointer flex-col items-center rounded-2xl bg-white p-4 text-center shadow-sm transition-all active:scale-95"
    :class="unlocked ? 'hover:shadow-md' : 'opacity-70'"
  >
    <div class="relative h-20 w-20">
      <img
        :src="currentIconUrl"
        :alt="badge.name"
        class="h-full w-full object-contain"
        @error="handleImageError"
      />
      <div
        v-if="badge.maxLevel > 1 && unlocked"
        class="absolute -bottom-1 -right-1 rounded-full bg-purple-100 px-1.5 py-0.5 text-xs font-bold text-purple-700"
      >
        Lv.{{ badge.level }}/{{ badge.maxLevel }}
      </div>
    </div>

    <h3 class="mt-3 text-sm font-semibold text-slate-800">{{ badge.name }}</h3>
    <p class="mt-1 text-xs text-slate-500">
      {{ unlocked ? badge.title || '已获得' : '未解锁' }}
    </p>

    <div v-if="badge.maxLevel > 1 && !isMaxLevel" class="mt-3 w-full">
      <div class="mb-1 flex justify-between text-xs text-slate-400">
        <span>进度</span>
        <span>{{ badge.progress }} / {{ badge.target }}</span>
      </div>
      <div class="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          class="h-full rounded-full bg-gradient-to-r from-purple-400 to-purple-600 transition-all"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
    </div>

    <div v-else-if="badge.maxLevel === 1 && !unlocked" class="mt-3 text-xs text-slate-400">
      待达成
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UserBadge } from '@/api/badge'
import { getBadgeIconUrl } from '@/utils/badgeUtils'

const props = defineProps<{
  badge: UserBadge
}>()

const unlocked = computed(() => props.badge.unlocked)
const isMaxLevel = computed(() => props.badge.level >= props.badge.maxLevel)

const progressPercent = computed(() => {
  if (props.badge.target <= 0) return 0
  const percent = (props.badge.progress / props.badge.target) * 100
  return Math.min(percent, 100)
})

// 根据解锁状态生成正确的图标 URL
const currentIconUrl = computed(() => {
  const code = props.badge.code
  return getBadgeIconUrl(code, !unlocked.value)
})

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src =
    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2394A3B8"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/%3E%3C/svg%3E'
}
</script>
