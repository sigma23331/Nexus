<template>
  <div class="app-container relative min-h-screen bg-[#0f0a1e]">
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
</script>