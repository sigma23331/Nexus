<template>
  <div class="flex items-center justify-between px-4 py-3">
    <div class="flex-1">
      <div class="flex items-center gap-3">
        <span class="text-xl">{{ icon }}</span>
        <div>
          <p class="text-base text-slate-800">{{ label }}</p>
          <slot name="description"></slot>
        </div>
      </div>
    </div>
    <button
      @click="$emit('toggle')"
      class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
      :class="value ? 'bg-purple-600' : 'bg-slate-300'"
    >
      <span
        class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform"
        :class="value ? 'translate-x-5' : 'translate-x-0.5'"
      />
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  icon: string
  value: boolean
}>()
defineEmits<{ (e: 'toggle'): void }>()
</script>
