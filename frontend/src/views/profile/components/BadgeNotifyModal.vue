<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
    @click.self="close"
  >
    <div
      class="w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-xl animate-in fade-in zoom-in duration-200"
    >
      <div class="mb-3 text-4xl">🎉</div>
      <h2 class="text-xl font-bold text-slate-800">新的勋章！</h2>

      <div class="my-5 max-h-80 overflow-auto">
        <div
          v-for="change in changes"
          :key="change.id"
          class="mb-4 flex items-center gap-3 rounded-xl bg-slate-50 p-3 text-left"
        >
          <img
            :src="getIconUrl(change.badgeCode)"
            class="h-12 w-12 rounded-full object-contain"
            @error="handleImageError"
          />
          <div class="flex-1">
            <div class="font-semibold text-slate-800">{{ change.badgeName }}</div>
            <div class="text-sm text-slate-500">
              <span v-if="change.changeType === 'unlock'">✨ 获得新勋章</span>
              <span v-else>⬆️ 升级至 Lv.{{ change.level }}</span>
              <span v-if="change.title"> - {{ change.title }}</span>
            </div>
          </div>
        </div>
      </div>

      <button
        @click="close"
        class="mt-2 w-full rounded-full bg-purple-500 py-2.5 font-medium text-white transition hover:bg-purple-600"
      >
        收下勋章
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { BadgeChange } from '@/api/badge'
import { getBadgeIconUrl } from '@/utils/badgeUtils'

const visible = ref(false)
const changes = ref<BadgeChange[]>([])

const open = (newChanges: BadgeChange[]) => {
  changes.value = newChanges
  visible.value = true
}

const close = () => {
  visible.value = false
  emit('closed')
}

const emit = defineEmits<{
  (e: 'closed'): void
}>()

// 根据 badgeCode 生成正确的彩色图标（通知均为解锁/升级，使用彩色）
const getIconUrl = (badgeCode: string) => {
  return getBadgeIconUrl(badgeCode, false)
}

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src =
    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2394A3B8"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/%3E%3C/svg%3E'
}

defineExpose({ open })
</script>
