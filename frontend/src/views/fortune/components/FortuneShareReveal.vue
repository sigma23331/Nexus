<template>
  <div class="reveal">
    <div class="reveal__stage">
      <!-- 与看板「运势卡片」区块一致的预览卡 -->
      <div class="reveal__card" :class="{ 'reveal__card--visible': phase === 'card' }">
        <FortuneCardPreview
          :title="fortune.title"
          :score="fortune.score"
          :content-main="fortune.content_main"
          :content-sub="fortune.content_sub"
          :yi="fortune.yi"
          :ji="fortune.ji"
        />
      </div>

      <!-- 摇出的上上签：仅在 stick 阶段显示，随后消失 -->
      <div
        class="reveal__stick"
        :data-phase="phase"
        :aria-hidden="phase === 'bucket' || phase === 'hiding' || phase === 'card'"
      >
        <div class="reveal__stick-inner">
          <p class="reveal__stick-title">上上签</p>
        </div>
      </div>

      <!-- 竹签筒：摇动阶段 -->
      <div class="reveal__bucket-wrap" :class="{ 'reveal__bucket-wrap--hide': phase !== 'bucket' }">
        <div class="reveal__bucket" :class="{ 'reveal__bucket--shake': phase === 'bucket' }">
          <svg
            class="reveal__tube-svg"
            viewBox="0 0 120 168"
            width="120"
            height="168"
            aria-hidden="true"
          >
            <defs>
              <linearGradient id="tube-bamboo" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#5c432f" />
                <stop offset="22%" stop-color="#c9a66c" />
                <stop offset="50%" stop-color="#deb887" />
                <stop offset="78%" stop-color="#b8925a" />
                <stop offset="100%" stop-color="#4a3528" />
              </linearGradient>
              <pattern id="tube-ribs" width="10" height="168" patternUnits="userSpaceOnUse">
                <rect width="10" height="168" fill="url(#tube-bamboo)" />
                <line
                  x1="9"
                  y1="0"
                  x2="9"
                  y2="168"
                  stroke="#3d291c"
                  stroke-opacity="0.35"
                  stroke-width="0.8"
                />
              </pattern>
              <linearGradient id="tube-rim" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#8b6914" />
                <stop offset="100%" stop-color="#5c4033" />
              </linearGradient>
            </defs>
            <!-- 筒底 -->
            <ellipse cx="60" cy="158" rx="44" ry="10" fill="#3d291c" />
            <!-- 筒身 -->
            <path
              fill="url(#tube-ribs)"
              d="M18 52 Q18 48 22 46 L98 46 Q102 48 102 52 L102 148 Q102 156 94 158 L26 158 Q18 156 18 148 Z"
            />
            <!-- 筒口外沿 -->
            <ellipse cx="60" cy="48" rx="48" ry="14" fill="url(#tube-rim)" />
            <!-- 筒口内阴影 -->
            <ellipse cx="60" cy="50" rx="36" ry="9" fill="#1a0f0a" />
            <!-- 露出的签头 -->
            <g class="reveal__tube-sticks">
              <rect
                x="44"
                y="18"
                width="4.5"
                height="38"
                rx="1"
                fill="#f7ecd8"
                stroke="#c4a574"
                stroke-width="0.4"
              />
              <rect
                x="51"
                y="14"
                width="4"
                height="42"
                rx="1"
                fill="#faf4e6"
                stroke="#c4a574"
                stroke-width="0.4"
              />
              <rect
                x="57"
                y="16"
                width="4.5"
                height="40"
                rx="1"
                fill="#f2e6cc"
                stroke="#c4a574"
                stroke-width="0.4"
              />
              <rect
                x="64"
                y="12"
                width="4"
                height="44"
                rx="1"
                fill="#fff9ed"
                stroke="#c4a574"
                stroke-width="0.4"
              />
              <rect
                x="71"
                y="17"
                width="4"
                height="39"
                rx="1"
                fill="#f5ebd8"
                stroke="#c4a574"
                stroke-width="0.4"
              />
            </g>
            <!-- 口沿高光 -->
            <ellipse
              cx="60"
              cy="44"
              rx="40"
              ry="10"
              fill="none"
              stroke="#ffffff"
              stroke-opacity="0.15"
              stroke-width="1"
            />
          </svg>
        </div>
        <p class="reveal__hint">轻晃签筒，求一支吉签</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import FortuneCardPreview from './FortuneCardPreview.vue'

export type FortuneShareFortune = {
  title: string
  score: number
  content_main: string
  content_sub: string
  yi: string[]
  ji: string[]
}

defineProps<{
  fortune: FortuneShareFortune
}>()

const phase = ref<'bucket' | 'stick' | 'hiding' | 'card'>('bucket')

let timers: ReturnType<typeof setTimeout>[] = []

onMounted(() => {
  timers.push(
    setTimeout(() => {
      phase.value = 'stick'
    }, 1900),
  )
  timers.push(
    setTimeout(() => {
      phase.value = 'hiding'
    }, 4200),
  )
  timers.push(
    setTimeout(() => {
      phase.value = 'card'
    }, 5000),
  )
})

onBeforeUnmount(() => {
  timers.forEach(clearTimeout)
  timers = []
})
</script>

<style scoped>
.reveal {
  min-height: 380px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 0 12px;
}

.reveal__stage {
  position: relative;
  width: 100%;
  max-width: 360px;
  min-height: 360px;
  margin: 0 auto;
}

/* ----- 看板同款运势卡 ----- */
.reveal__card {
  position: relative;
  width: 100%;
  opacity: 0;
  transform: translateY(10px) scale(0.98);
  transition:
    opacity 0.55s ease,
    transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
  z-index: 1;
}

.reveal__card--visible {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* ----- 上上签 ----- */
.reveal__stick {
  position: absolute;
  left: 50%;
  top: 42%;
  z-index: 4;
  transition:
    opacity 0.45s ease,
    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.reveal__stick[data-phase='bucket'] {
  opacity: 0;
  transform: translate(-50%, 72px) scale(0.92);
  pointer-events: none;
}

.reveal__stick[data-phase='stick'] {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
  pointer-events: none;
}

.reveal__stick[data-phase='hiding'],
.reveal__stick[data-phase='card'] {
  opacity: 0;
  transform: translate(-50%, -118%) scale(0.88);
  pointer-events: none;
}

.reveal__stick-inner {
  width: 52px;
  min-height: 188px;
  padding: 28px 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #fdf6e8 0%, #ecdcc4 48%, #e0d0b8 100%);
  border-radius: 5px;
  border: 1px solid rgba(100, 50, 30, 0.4);
  box-shadow:
    0 14px 32px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.reveal__stick-title {
  margin: 0;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 0.42em;
  font-size: 20px;
  font-weight: 800;
  color: #7f1d1d;
  font-family: 'Songti SC', 'Noto Serif SC', 'Microsoft YaHei', serif;
  line-height: 1.2;
}

/* ----- 签筒 ----- */
.reveal__bucket-wrap {
  position: absolute;
  left: 50%;
  top: 44%;
  transform: translate(-50%, -50%);
  z-index: 6;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  opacity: 1;
  transition:
    opacity 0.5s ease,
    transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.reveal__bucket-wrap--hide {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.92);
  pointer-events: none;
}

.reveal__hint {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: #64748b;
}

.reveal__bucket {
  transform-origin: 50% 92%;
}

.reveal__bucket--shake {
  animation: bucket-rock 0.16s ease-in-out infinite alternate;
}

@keyframes bucket-rock {
  from {
    transform: rotate(-10deg);
  }
  to {
    transform: rotate(10deg);
  }
}

.reveal__tube-svg {
  display: block;
  filter: drop-shadow(0 10px 18px rgba(0, 0, 0, 0.22));
}
</style>
