<!-- src/views/profile/components/BadgeDetailModal.vue -->
<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
    @click.self="close"
  >
    <div class="max-h-[80vh] w-full max-w-sm overflow-auto rounded-2xl bg-white p-5 shadow-xl">
      <div class="flex justify-end">
        <button @click="close" class="text-slate-400 hover:text-slate-600">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <div v-if="badge" class="text-center">
        <img
          :src="badgeIconUrl"
          :alt="badge.name"
          class="mx-auto h-24 w-24 object-contain"
          @error="handleImageError"
        />

        <h2 class="mt-3 text-xl font-bold text-slate-800">{{ badge.name }}</h2>

        <div class="mt-1 text-sm text-slate-500">
          <span v-if="badge.unlocked">
            {{ badge.title || '已获得' }}
            <span v-if="badge.maxLevel > 1">（Lv.{{ badge.level }}/{{ badge.maxLevel }}）</span>
          </span>
          <span v-else>未解锁</span>
        </div>

        <p class="mt-4 text-sm text-slate-600">{{ badge.description }}</p>

        <!-- 佩戴/摘下按钮 - 仅已解锁徽章显示 -->
        <div v-if="badge.unlocked" class="mt-5">
          <button
            v-if="isEquipped"
            @click="handleUnequip"
            :disabled="updating"
            class="w-full rounded-full border border-slate-300 bg-white py-2.5 font-medium text-slate-600 transition hover:bg-slate-50 disabled:opacity-50"
          >
            <span v-if="updating">处理中...</span>
            <span v-else>摘下徽章</span>
          </button>
          <button
            v-else
            @click="handleEquip"
            :disabled="updating || isMaxReached"
            class="w-full rounded-full bg-purple-500 py-2.5 font-medium text-white transition hover:bg-purple-600 disabled:opacity-50"
          >
            <span v-if="updating">处理中...</span>
            <span v-else-if="isMaxReached">已达佩戴上限（{{ maxEquipped }}个）</span>
            <span v-else>佩戴徽章</span>
          </button>
        </div>

        <!-- 未解锁提示 -->
        <div v-else class="mt-5">
          <div class="rounded-lg bg-slate-100 px-4 py-3 text-sm text-slate-500">
            🔒 完成对应条件即可解锁此徽章
          </div>
        </div>

        <!-- 进度条（多等级且非满级） -->
        <div v-if="badge.maxLevel > 1 && !isMaxLevel" class="mt-5">
          <div class="mb-2 flex justify-between text-sm">
            <span class="text-slate-600">下一等级进度</span>
            <span class="font-medium text-purple-600"
              >{{ badge.progress }} / {{ badge.target }}</span
            >
          </div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              class="h-full rounded-full bg-purple-500 transition-all"
              :style="{ width: `${progressPercent}%` }"
            ></div>
          </div>
          <p class="mt-2 text-xs text-slate-400">下一级称号：{{ badge.nextTitle || '最高级' }}</p>
        </div>

        <!-- 等级详情 -->
        <div class="mt-6 border-t border-slate-100 pt-4">
          <h3 class="mb-3 text-sm font-semibold text-slate-700">等级详情</h3>
          <div class="space-y-2">
            <div
              v-for="level in badge.levels"
              :key="level.level"
              class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
              :class="{ 'bg-purple-50': badge.unlocked && badge.level >= level.level }"
            >
              <div class="flex items-center gap-2">
                <span class="font-medium text-slate-700">Lv.{{ level.level }}</span>
                <span class="text-slate-600">{{ level.title }}</span>
              </div>
              <div class="text-xs text-slate-500">{{ level.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { UserBadge } from '@/api/badge'
import { getBadgeIconUrl } from '@/utils/badgeUtils'

const props = defineProps<{
  badge: UserBadge | null
  equippedBadgeCodes: Set<string>
  maxEquipped: number
}>()

const emit = defineEmits<{
  (e: 'update-equipped', badgeCodes: string[]): Promise<void>
}>()

const visible = ref(false)
const updating = ref(false)

const isEquipped = computed(() => {
  if (!props.badge) return false
  return props.equippedBadgeCodes.has(props.badge.code)
})

const isMaxReached = computed(() => {
  return props.equippedBadgeCodes.size >= props.maxEquipped
})

const isMaxLevel = computed(() => {
  return props.badge ? props.badge.level >= props.badge.maxLevel : false
})

const progressPercent = computed(() => {
  if (!props.badge || props.badge.target <= 0) return 0
  const percent = (props.badge.progress / props.badge.target) * 100
  return Math.min(percent, 100)
})

const badgeIconUrl = computed(() => {
  if (!props.badge) return ''
  const isGray = !props.badge.unlocked
  return getBadgeIconUrl(props.badge.code, isGray)
})

// 佩戴徽章
const handleEquip = async () => {
  if (!props.badge) return
  if (isMaxReached.value) {
    // 提示已达上限
    return
  }

  updating.value = true
  try {
    const newCodes = [...props.equippedBadgeCodes, props.badge.code]
    await emit('update-equipped', newCodes)
  } catch (err: unknown) {
    if (err instanceof Error) {
      console.error(err.message)
    } else {
      console.error(String(err))
    }
  } finally {
    updating.value = false
  }
}

// 摘下徽章
const handleUnequip = async () => {
  if (!props.badge) return

  updating.value = true
  try {
    const newCodes = [...props.equippedBadgeCodes].filter((code) => code !== props.badge?.code)
    await emit('update-equipped', newCodes)
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error)
    alert(message)
  } finally {
    updating.value = false
  }
}

const open = () => {
  visible.value = true
}

const close = () => {
  visible.value = false
}

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src =
    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2394A3B8"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/%3E%3C/svg%3E'
}

defineExpose({ open })
</script>
