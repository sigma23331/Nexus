<template>
  <!-- 添加 pb-safe 类（或直接内联样式） -->
  <div
    class="fixed bottom-0 left-0 right-0 z-10 bg-white border-t border-slate-200 flex justify-around items-center px-4"
    :style="{ paddingBottom: 'env(safe-area-inset-bottom)' }"
  >
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="flex flex-col items-center gap-1 text-slate-500 transition-colors duration-200 py-2"
      active-class="text-indigo-600"
    >
      <iconify-icon :icon="tab.icon" class="text-2xl"></iconify-icon>
      <span class="text-[10px]">{{ tab.name }}</span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { Icon as IconifyIcon } from '@iconify/vue'

const tabs = [
  { path: '/fortune', name: '看板', icon: 'mdi:auto-fix' },
  { path: '/answer', name: '答案', icon: 'mdi:book-open-page-variant' },
  { path: '/plaza', name: '广场', icon: 'mdi:compass-outline' },
  { path: '/profile', name: '我的', icon: 'mdi:account-circle-outline' },
]
</script>
