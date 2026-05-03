<template>
  <div
    :class="[
      'app-container relative min-h-screen text-slate-900 w-full mx-auto',
      isWideLayout ? 'max-w-none shadow-none' : 'max-w-md bg-white shadow-sm',
    ]"
  >
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
    <TabBar v-if="showTabBar" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from '@/components/layout/TabBar.vue'

const route = useRoute()
const showTabBar = computed(() => route.meta.tabBar === true)
const isWideLayout = computed(() => route.meta.fullWidth === true)
</script>

<style>
/* 确保页面内容不被顶部安全区遮挡，但又不产生额外滚动 */
body {
  padding-top: 0;
  padding-bottom: 0;
  margin: 0;
}
/* 可选：为固定定位的 TabBar 预留底部空间已在组件中处理，无需额外调整 */
</style>
