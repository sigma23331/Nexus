<template>
  <div
    v-for="i in count"
    :key="i"
    class="skeleton"
    :class="[circle ? 'rounded-full' : '', i < count ? 'mb-2' : '']"
    :style="style"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 宽度，数字按 px，字符串原样（如 '60%'） */
    width?: number | string
    /** 高度，数字按 px */
    height?: number | string
    /** 圆角（px），circle 为 true 时忽略 */
    radius?: number
    /** 圆形（头像占位） */
    circle?: boolean
    /** 重复行数（文本占位） */
    count?: number
  }>(),
  {
    width: '100%',
    height: 16,
    radius: 8,
    circle: false,
    count: 1,
  },
)

const toUnit = (v: number | string) => (typeof v === 'number' ? `${v}px` : v)

const style = computed(() => ({
  width: toUnit(props.width),
  height: toUnit(props.height),
  borderRadius: props.circle ? '9999px' : `${props.radius}px`,
}))
</script>

<style scoped>
.skeleton {
  position: relative;
  overflow: hidden;
  background-color: #e9edf3;
}
.skeleton::after {
  content: '';
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  animation: skeleton-shimmer 1.3s infinite;
}
@keyframes skeleton-shimmer {
  100% {
    transform: translateX(100%);
  }
}
@media (prefers-reduced-motion: reduce) {
  .skeleton::after {
    animation: none;
  }
}
</style>
