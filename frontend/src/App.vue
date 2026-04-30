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
