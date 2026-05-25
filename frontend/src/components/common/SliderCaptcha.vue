<template>
  <div class="rounded-2xl border border-purple-100 bg-purple-50/60 p-4">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-slate-700">拖动滑块完成验证</p>
        <p class="mt-1 text-xs text-slate-500">验证通过后将自动发送短信验证码</p>
      </div>
      <button
        type="button"
        class="text-xs text-purple-600 disabled:opacity-50"
        :disabled="loading || verifying"
        @click="refreshChallenge"
      >
        换一个
      </button>
    </div>

    <div class="flex justify-center">
      <div
        class="relative h-11 select-none overflow-hidden rounded-full border border-slate-200 bg-white shadow-inner"
        :style="{ width: `${sliderWidth}px` }"
      >
        <div
          class="absolute inset-y-0 left-0 bg-purple-200/70 transition-[width]"
          :style="progressStyle"
        ></div>
        <div
          class="absolute top-1/2 h-7 -translate-y-1/2 rounded-full border border-dashed border-purple-300 bg-purple-100/80"
          :style="targetStyle"
        ></div>
        <span
          class="pointer-events-none absolute inset-0 flex items-center justify-center text-xs text-slate-400"
        >
          {{ verified ? '验证通过' : loading ? '加载中...' : '按住滑块拖到高亮区域' }}
        </span>
        <button
          type="button"
          class="absolute left-0 top-0 z-10 flex h-11 items-center justify-center rounded-full bg-purple-600 text-white shadow-md transition-transform disabled:opacity-60"
          :class="{ 'bg-emerald-500': verified }"
          :style="handleStyle"
          :disabled="loading || verifying || verified"
          @pointerdown.prevent="onPointerDown"
        >
          {{ verified ? '✓' : '›' }}
        </button>
      </div>
    </div>

    <p v-if="errorMessage" class="mt-2 text-center text-xs text-red-500">{{ errorMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  createSliderCaptchaChallenge,
  verifySliderCaptcha,
  type SliderCaptchaTrackPoint,
} from '@/api/auth'

const props = defineProps<{
  phone: string
}>()

const emit = defineEmits<{
  verified: [token: string]
}>()

const loading = ref(false)
const verifying = ref(false)
const verified = ref(false)
const errorMessage = ref('')
const challengeToken = ref('')
const targetX = ref(0)
const sliderWidth = ref(280)
const handleSize = ref(44)
const handleX = ref(0)

const dragging = ref(false)
let startClientX = 0
let startHandleX = 0
let startedAt = 0
let track: SliderCaptchaTrackPoint[] = []

const maxOffset = computed(() => Math.max(sliderWidth.value - handleSize.value, 0))
const handleStyle = computed(() => ({
  width: `${handleSize.value}px`,
  transform: `translateX(${handleX.value}px)`,
}))
const targetStyle = computed(() => ({
  left: `${targetX.value}px`,
  width: `${handleSize.value}px`,
}))
const progressStyle = computed(() => ({
  width: `${Math.min(handleX.value + handleSize.value / 2, sliderWidth.value)}px`,
}))

function clampOffset(value: number) {
  return Math.min(Math.max(value, 0), maxOffset.value)
}

function addTrackPoint(event: PointerEvent) {
  track.push({
    x: Math.round(handleX.value),
    y: Math.round(event.clientY),
    t: Date.now() - startedAt,
  })
}

function resetInteraction() {
  verified.value = false
  handleX.value = 0
  errorMessage.value = ''
  track = []
}

async function refreshChallenge() {
  if (!props.phone) return

  loading.value = true
  resetInteraction()
  try {
    const challenge = await createSliderCaptchaChallenge(props.phone)
    challengeToken.value = challenge.challengeToken
    targetX.value = challenge.targetX
    sliderWidth.value = challenge.sliderWidth
    handleSize.value = challenge.handleSize
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : '滑块加载失败，请重试'
  } finally {
    loading.value = false
  }
}

function onPointerDown(event: PointerEvent) {
  if (loading.value || verifying.value || verified.value || !challengeToken.value) return

  dragging.value = true
  startClientX = event.clientX
  startHandleX = handleX.value
  startedAt = Date.now()
  track = []
  addTrackPoint(event)
  window.addEventListener('pointermove', onPointerMove)
  window.addEventListener('pointerup', onPointerUp)
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) return

  handleX.value = clampOffset(startHandleX + event.clientX - startClientX)
  addTrackPoint(event)
}

async function onPointerUp(event: PointerEvent) {
  if (!dragging.value) return

  dragging.value = false
  addTrackPoint(event)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup', onPointerUp)
  await submitVerification()
}

async function submitVerification() {
  verifying.value = true
  errorMessage.value = ''
  try {
    const result = await verifySliderCaptcha(
      props.phone,
      challengeToken.value,
      handleX.value,
      Date.now() - startedAt,
      track,
    )
    verified.value = true
    emit('verified', result.captchaToken)
  } catch (err) {
    const message = err instanceof Error ? err.message : '滑块验证失败，请重试'
    await refreshChallenge()
    errorMessage.value = message
  } finally {
    verifying.value = false
  }
}

watch(
  () => props.phone,
  () => {
    refreshChallenge()
  },
)

onMounted(() => {
  refreshChallenge()
})

onUnmounted(() => {
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup', onPointerUp)
})
</script>
