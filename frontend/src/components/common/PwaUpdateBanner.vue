<template>
  <Transition name="pwa-banner">
    <div
      v-if="pwaNeedRefresh"
      class="fixed left-0 right-0 z-[60] px-4"
      :class="bottomOffsetClass"
      role="status"
    >
      <div
        class="mx-auto flex max-w-md items-center justify-between gap-3 rounded-2xl bg-purple-800 px-4 py-3 text-sm text-white shadow-lg"
      >
        <span>发现新版本，刷新后即可使用</span>
        <div class="flex shrink-0 gap-2">
          <button
            type="button"
            class="rounded-full px-3 py-1 text-xs text-purple-200 hover:text-white"
            @click="dismiss"
          >
            稍后
          </button>
          <button
            type="button"
            class="rounded-full bg-white px-3 py-1 text-xs font-medium text-purple-800"
            @click="applyPwaUpdate"
          >
            刷新
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { applyPwaUpdate, pwaNeedRefresh } from '@/pwa/register'

const route = useRoute()

const bottomOffsetClass = computed(() =>
  route.meta.tabBar === true ? 'bottom-[calc(4.5rem+env(safe-area-inset-bottom))]' : 'bottom-4',
)

function dismiss() {
  pwaNeedRefresh.value = false
}
</script>

<style scoped>
.pwa-banner-enter-active,
.pwa-banner-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.pwa-banner-enter-from,
.pwa-banner-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
