<template>
  <div
    class="pointer-events-none fixed inset-x-0 z-[1000] flex flex-col items-center gap-2 px-4"
    :style="{ bottom: 'calc(5rem + env(safe-area-inset-bottom))' }"
  >
    <TransitionGroup name="toast">
      <div
        v-for="item in toasts"
        :key="item.id"
        class="pointer-events-auto max-w-md w-fit rounded-lg px-4 py-2 text-center text-sm text-white shadow-lg"
        :class="toneClass(item.type)"
        role="status"
        @click="dismiss(item.id)"
      >
        {{ item.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToast, type ToastType } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

function toneClass(type: ToastType): string {
  switch (type) {
    case 'success':
      return 'bg-green-600/90'
    case 'error':
      return 'bg-red-600/90'
    case 'warning':
      return 'bg-amber-500/90'
    default:
      return 'bg-black/75'
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
.toast-move {
  transition: transform 0.25s ease;
}
</style>
