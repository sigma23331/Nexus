<template>
  <div class="egg-fx pointer-events-none absolute inset-0 overflow-hidden rounded-3xl" :data-anim="animation">
    <template v-if="animation === 'rain'">
      <span v-for="i in 18" :key="`rain-${i}`" class="egg-fx__rain" :style="rainStyle(i)" />
    </template>
    <template v-else-if="animation === 'snow'">
      <span v-for="i in 16" :key="`snow-${i}`" class="egg-fx__snow" :style="snowStyle(i)" />
    </template>
    <template v-else-if="animation === 'midnight'">
      <span v-for="i in 12" :key="`star-${i}`" class="egg-fx__star" :style="starStyle(i)" />
    </template>
    <template v-else-if="animation === 'dawn'">
      <div class="egg-fx__dawn" />
    </template>
    <template v-else-if="animation === 'solar'">
      <div class="egg-fx__solar-ring" />
    </template>
    <template v-else-if="animation === 'festival'">
      <span v-for="i in 8" :key="`leaf-${i}`" class="egg-fx__leaf" :style="leafStyle(i)" />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { AnswerEasterEggAnimation } from '@/composables/useAnswerEasterEgg'

defineProps<{
  animation: AnswerEasterEggAnimation
}>()

const rainStyle = (i: number) => ({
  left: `${(i * 17) % 100}%`,
  animationDelay: `${(i % 7) * 0.12}s`,
  animationDuration: `${0.8 + (i % 5) * 0.1}s`,
})

const snowStyle = (i: number) => ({
  left: `${(i * 13) % 100}%`,
  animationDelay: `${(i % 6) * 0.18}s`,
  animationDuration: `${1.6 + (i % 4) * 0.2}s`,
})

const starStyle = (i: number) => ({
  left: `${(i * 19) % 92 + 4}%`,
  top: `${(i * 23) % 70 + 8}%`,
  animationDelay: `${(i % 5) * 0.25}s`,
})

const leafStyle = (i: number) => ({
  left: `${(i * 21) % 90 + 5}%`,
  animationDelay: `${(i % 4) * 0.3}s`,
})
</script>

<style scoped>
.egg-fx__rain {
  position: absolute;
  top: -12px;
  width: 2px;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(147, 197, 253, 0.9), rgba(59, 130, 246, 0.2));
  animation: egg-rain-fall linear infinite;
}

.egg-fx__snow {
  position: absolute;
  top: -8px;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.8);
  animation: egg-snow-fall linear infinite;
}

.egg-fx__star {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: #fde68a;
  box-shadow: 0 0 8px rgba(253, 224, 71, 0.9);
  animation: egg-star-twinkle 1.8s ease-in-out infinite;
}

.egg-fx__dawn {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 110%, rgba(251, 191, 36, 0.35), transparent 55%);
  animation: egg-dawn-pulse 2.4s ease-in-out infinite;
}

.egg-fx__solar-ring {
  position: absolute;
  inset: -20%;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.22), transparent 62%);
  animation: egg-solar-spin 6s linear infinite;
}

.egg-fx__leaf {
  position: absolute;
  top: -16px;
  font-size: 14px;
  animation: egg-leaf-fall 2.8s ease-in infinite;
}

.egg-fx__leaf::before {
  content: '🍃';
}

@keyframes egg-rain-fall {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  to {
    transform: translateY(320px);
    opacity: 0;
  }
}

@keyframes egg-snow-fall {
  from {
    transform: translateY(-8px) translateX(0);
    opacity: 0;
  }
  15% {
    opacity: 1;
  }
  to {
    transform: translateY(320px) translateX(12px);
    opacity: 0;
  }
}

@keyframes egg-star-twinkle {
  0%,
  100% {
    opacity: 0.35;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes egg-dawn-pulse {
  0%,
  100% {
    opacity: 0.55;
  }
  50% {
    opacity: 0.95;
  }
}

@keyframes egg-solar-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes egg-leaf-fall {
  from {
    transform: translateY(-12px) rotate(0deg);
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  to {
    transform: translateY(300px) rotate(180deg);
    opacity: 0;
  }
}
</style>
