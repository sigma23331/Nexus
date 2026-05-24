<template>
  <div
    class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-50 transition"
    :class="{ 'text-rose-500': colorRed }"
    @click="$emit('click')"
  >
    <div class="flex items-center gap-3">
      <!-- 图标插槽：父组件可传入任意内容（SVG、字体图标、emoji 等） -->
      <slot name="icon">
        <!-- 默认无图标，仅显示标签 -->
      </slot>
      <span class="text-base">{{ label }}</span>
    </div>
    <!-- 右箭头（矢量 V 形） -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-4 w-4 text-slate-400"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 18l6-6-6-6" />
    </svg>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  colorRed?: boolean
}>()
defineEmits(['click'])
</script>
