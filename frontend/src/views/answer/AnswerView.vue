<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <img src="/images/answericon.png" alt="答案之书图标" class="w-8 h-8 object-contain" />
      <h1 class="text-2xl font-bold">答案之书</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section>
        <textarea
          v-model="question"
          rows="3"
          class="w-full bg-white border rounded-2xl p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-purple-500 transition-all"
          :class="{
            'border-red-500 animate-shake': inputError,
            'border-slate-200': !inputError,
          }"
          placeholder="午饭吃啥？要不要回那条消息？..."
        ></textarea>
        <div class="mt-3 flex items-center justify-between gap-3">
          <p class="text-xs text-slate-500">输入问题后，轻触书籍抽取答案。</p>
          <button
            class="rounded-full px-4 py-1.5 text-xs font-semibold transition"
            :class="
              canSubmit
                ? 'bg-indigo-400 text-white'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            "
            :disabled="!canSubmit"
            @click="drawAnswer"
          >
            {{ isDrawing ? '抽取中...' : '提交问题' }}
          </button>
        </div>
      </section>

      <section class="text-center">
        <div
          class="book-wrap mx-auto"
          :class="{
            shaking: isShaking,
            'book-wrap--egg': !!activeEasterEgg,
            [`book-wrap--egg-${activeEasterEgg?.animation}`]: !!activeEasterEgg,
          }"
          @click="drawAnswer"
        >
          <div class="book-3d">
            <div class="book-front">
              <p class="text-xs tracking-[0.2em] text-indigo-100">BOOK OF ANSWERS</p>
              <p class="mt-3 text-xl font-bold text-white">答案之书</p>
              <p class="mt-2 text-[11px] text-indigo-100/90">轻触书籍，抽一句指引</p>
            </div>
            <div class="book-spine"></div>
            <div class="book-glow"></div>
          </div>
        </div>
      </section>

      <section>
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold">回溯复盘</h2>
          <span class="text-xs text-slate-400">最近 {{ recentAnswerPreviewLimit }} 条</span>
        </div>
        <div class="space-y-3">
          <div
            v-for="item in recentAnswers"
            :key="item.id"
            class="rounded-2xl bg-gradient-to-br from-indigo-100/80 via-white to-purple-100/80 p-3 shadow-sm cursor-pointer transition hover:shadow-md hover:from-indigo-200/80 hover:to-purple-200/80 border border-purple-200"
            @click="openDetail(item)"
          >
            <!-- 顶部：日期（左） + 星标（右） -->
            <div class="flex justify-between items-start mb-1">
              <span class="text-[11px] text-slate-500">{{ formatDateTime(item.createdAt) }}</span>
              <button
                @click.stop="toggleItemFavorite(item)"
                class="shrink-0 p-1 transition hover:scale-110"
                :class="item.isFavorited ? 'text-amber-500' : 'text-slate-400'"
                aria-label="收藏"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-5 h-5"
                  :fill="item.isFavorited ? 'currentColor' : 'none'"
                  :stroke="item.isFavorited ? 'none' : 'currentColor'"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polygon
                    points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                  />
                </svg>
              </button>
            </div>
            <!-- 问题 -->
            <p class="text-sm font-medium text-slate-800 line-clamp-2">问：{{ item.question }}</p>
            <!-- 点击查看回答（右下角） -->
            <p class="mt-2 text-xs text-slate-500 text-right">点击查看回答</p>
          </div>
          <div
            v-if="recentAnswers.length === 0 && !loadingHistory"
            class="text-center text-xs text-slate-400 py-4"
          >
            暂无历史记录，去提问吧
          </div>
          <div v-if="loadingHistory" class="text-center text-xs text-slate-400 py-2">加载中...</div>
          <router-link
            v-if="recentAnswers.length > 0"
            :to="{ name: 'answer-history' }"
            class="block w-full rounded-xl border border-purple-100 bg-purple-50 py-2 text-center text-xs font-semibold text-purple-600 hover:bg-purple-100"
          >
            加载更多
          </router-link>
        </div>
      </section>
    </main>

    <!-- 答案弹窗（居中样式） -->
    <Transition name="answer-modal">
      <div
        v-if="modalVisible"
        class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-6"
        @click.self="hideAnswer"
      >
        <div
          class="answer-modal-panel relative overflow-hidden border rounded-3xl w-full max-w-sm p-8 text-center"
          :class="
            activeEasterEgg
              ? `answer-modal-panel--egg answer-modal-panel--egg-${activeEasterEgg.animation}`
              : 'bg-white border-slate-200'
          "
        >
          <AnswerEasterEggEffects v-if="activeEasterEgg" :animation="activeEasterEgg.animation" />
          <div class="relative z-10">
            <span v-if="activeEasterEgg" class="egg-badge">{{ activeEasterEgg.badge }}彩蛋</span>
            <span v-else class="text-4xl">✨</span>
            <p class="mt-3 text-xs text-slate-500">你问：{{ currentQuestion }}</p>
            <p class="my-6 text-xl font-bold leading-relaxed text-slate-900">
              {{ currentAnswer }}
            </p>
          </div>
          <button
            @click="hideAnswer"
            class="relative z-10 w-full rounded-2xl py-4 font-bold text-white"
            :class="
              activeEasterEgg
                ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600'
                : 'bg-gradient-to-r from-purple-600 to-pink-600'
            "
          >
            我明白了
          </button>
          <div class="relative z-10 mt-6 flex justify-center gap-4">
            <button type="button" class="flex items-center gap-1 text-xs text-slate-500">
              📤 分享卡片
            </button>
            <button
              type="button"
              class="flex items-center gap-1 text-xs text-slate-500"
              @click="toggleFavorite(currentAnswerId)"
            >
              🔖 {{ currentIsFavorited ? '取消收藏' : '存入收藏' }}
            </button>
            <!-- 调试预览按钮（仅开发环境） -->
            <!-- <button
              v-if="isDev"
              type="button"
              class="flex items-center gap-1 text-xs text-slate-500"
              @click="debugPreviewAnswerCard"
            >
              🖼️ 调试预览
            </button> -->
          </div>
        </div>
      </div>
    </Transition>

    <!-- 答案详情弹窗 -->
    <AnswerDetailModal ref="answerDetailModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { askQuestion, favoriteAnswer, type AnswerHistoryItem } from '@/api/answer'
import {
  getLocalAnswerList,
  addLocalAnswer,
  fetchAndSyncHistory,
  updateLocalFavoriteStatus,
} from '@/utils/answerService'
import AnswerDetailModal from './components/AnswerDetailModal.vue'
import AnswerEasterEggEffects from './components/AnswerEasterEggEffects.vue'
import {
  detectAnswerEasterEgg,
  recordEasterEggTrigger,
  type AnswerEasterEgg,
} from '@/composables/useAnswerEasterEgg'

// ---------- 数据 ----------
const question = ref('')
const modalVisible = ref(false)
const currentAnswer = ref('')
const currentQuestion = ref('')
const currentAnswerId = ref('')
const currentIsFavorited = ref(false)
const isShaking = ref(false)
const isDrawing = ref(false)
const recentAnswers = ref<AnswerHistoryItem[]>([])
const loadingHistory = ref(false)
const answerDetailModalRef = ref<InstanceType<typeof AnswerDetailModal> | null>(null)
const activeEasterEgg = ref<AnswerEasterEgg | null>(null)
const recentAnswerPreviewLimit = 3

// 输入框错误状态（用于抖动和红框）
const inputError = ref(false)
let errorTimer: ReturnType<typeof setTimeout> | null = null

// 是否可提交
const canSubmit = computed(() => question.value.trim().length > 0 && !isDrawing.value)

// 触发输入框错误效果
function triggerInputError() {
  if (errorTimer) clearTimeout(errorTimer)
  inputError.value = true
  errorTimer = setTimeout(() => {
    inputError.value = false
    errorTimer = null
  }, 400) // 与动画时长一致
}

// 格式化日期（仅日期）
// function formatDate(iso: string) {
//   return dayjs(iso).format('MM月DD日')
// }

// 格式化日期时间（带时分秒）
function formatDateTime(iso: string) {
  return dayjs(iso).format('MM月DD日 HH:mm:ss')
}

// 首页只预览少量记录，其余进入完整历史页继续加载
async function loadRecentHistory() {
  loadingHistory.value = true
  try {
    const local = getLocalAnswerList()
    recentAnswers.value = local.slice(0, recentAnswerPreviewLimit)
    await fetchAndSyncHistory(1, recentAnswerPreviewLimit)
    const updated = getLocalAnswerList()
    recentAnswers.value = updated.slice(0, recentAnswerPreviewLimit)
  } catch (err) {
    console.error('加载历史记录失败', err)
  } finally {
    loadingHistory.value = false
  }
}

// 提交问题并获取答案
async function drawAnswer() {
  if (!canSubmit.value) {
    triggerInputError()
    return
  }
  if (!navigator.onLine) {
    alert('当前网络不可用，请检查网络后重试')
    return
  }
  isDrawing.value = true
  isShaking.value = true
  activeEasterEgg.value = null

  try {
    const [egg, res] = await Promise.all([
      detectAnswerEasterEgg(),
      askQuestion(question.value.trim()),
    ])
    currentQuestion.value = res.question
    currentAnswerId.value = res.id
    currentIsFavorited.value = false

    if (egg) {
      activeEasterEgg.value = egg
      currentAnswer.value = `${egg.prefix}${egg.answerText}`
      recordEasterEggTrigger(egg.id)
    } else {
      currentAnswer.value = `宇宙说：${res.answerText}`
    }

    modalVisible.value = true

    const newItem: AnswerHistoryItem = {
      id: res.id,
      question: res.question,
      answerText: res.answerText,
      createdAt: res.createdAt,
      isFavorited: false,
    }
    addLocalAnswer(newItem)
    recentAnswers.value = [newItem, ...recentAnswers.value.slice(0, recentAnswerPreviewLimit - 1)]
    question.value = ''
  } catch (err) {
    console.error('提问失败', err)
    alert('提问失败，请重试')
  } finally {
    isShaking.value = false
    isDrawing.value = false
  }
}

// 收藏/取消收藏（用于当前答案弹窗）
async function toggleFavorite(answerId: string) {
  if (!navigator.onLine) {
    alert('网络不可用')
    return
  }
  const action = currentIsFavorited.value ? 'unfavorite' : 'favorite'
  try {
    await favoriteAnswer(answerId, action)
    const newStatus = !currentIsFavorited.value
    currentIsFavorited.value = newStatus
    updateLocalFavoriteStatus(answerId, newStatus)
    const recentItem = recentAnswers.value.find((a) => a.id === answerId)
    if (recentItem) recentItem.isFavorited = newStatus
  } catch (err) {
    console.error('操作失败', err)
    alert('操作失败')
  }
}

// 列表项收藏/取消收藏
const toggleItemFavorite = async (item: AnswerHistoryItem) => {
  if (!navigator.onLine) {
    alert('网络不可用')
    return
  }
  const action = item.isFavorited ? 'unfavorite' : 'favorite'
  try {
    await favoriteAnswer(item.id, action)
    const newStatus = !item.isFavorited
    updateLocalFavoriteStatus(item.id, newStatus)
    const target = recentAnswers.value.find((a) => a.id === item.id)
    if (target) target.isFavorited = newStatus
  } catch (err) {
    console.error('操作失败', err)
    alert('操作失败')
  }
}

function hideAnswer() {
  modalVisible.value = false
  activeEasterEgg.value = null
}

// 打开详情弹窗
function openDetail(item: AnswerHistoryItem) {
  answerDetailModalRef.value?.open(item)
}

// 分享功能（弹窗中的分享卡片按钮调用）
// function openShareModal() {
//   // 暂时仅输出，后续可接入分享弹窗
//   console.log('分享卡片', currentQuestion.value, currentAnswer.value)
// }

onMounted(() => {
  loadRecentHistory()
})

// import { previewAnswerCard } from '@/utils/shareCardGenerator'
// const isDev = import.meta.env.DEV

// // 调试预览当前答案卡片
// const debugPreviewAnswerCard = async () => {
//   await previewAnswerCard({
//     question: currentQuestion.value,
//     answerText: currentAnswer.value.replace('宇宙说：', ''),
//     createdAt: new Date().toISOString(),
//   })
// }
</script>

<style scoped>
/* 书籍原有样式保持不变 */
.book-wrap {
  width: 192px;
  height: 256px;
  perspective: 1000px;
  cursor: pointer;
}

.book-3d {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  transform-style: preserve-3d;
  transform: rotateY(-18deg) rotateX(9deg) translateY(0);
  transition: transform 220ms ease;
  animation: floatBook 2.8s ease-in-out infinite;
}

.book-wrap:hover .book-3d {
  transform: rotateY(-23deg) rotateX(11deg) translateY(-4px);
}

.book-front {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  border: 1px solid #a5b4fc;
  background: linear-gradient(100deg, #0d5bbbc4 0%, #5a8fc7db 62%, #48aed9e1 100%);
  box-shadow: 0 18px 36px rgba(99, 102, 241, 0.34);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 18px 14px;
}

.book-front::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: repeating-linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.1) 0px,
    rgba(255, 255, 255, 0.1) 2px,
    transparent 2px,
    transparent 8px
  );
  pointer-events: none;
  border-radius: inherit;
}

.book-spine {
  position: absolute;
  left: -14px;
  top: 10px;
  width: 16px;
  height: calc(100% - 20px);
  border-radius: 0;
  background: linear-gradient(180deg, #2c5a7a 0%, #1e3f58 70%, #142e42 100%);
  transform: rotateY(90deg);
  transform-origin: left center;
}

.book-spine::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 12px;
  width: 10px;
  height: calc(100% - 24px);
  border-radius: 0;
  background: linear-gradient(180deg, rgba(100, 150, 180, 0.6), rgba(64, 113, 172, 0.15));
}

.book-glow {
  position: absolute;
  left: 50%;
  bottom: -20px;
  width: 70%;
  height: 18px;
  background: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.36), transparent 70%);
  transform: translateX(-50%);
  filter: blur(4px);
}

.shaking .book-3d {
  animation: shakeBook 0.9s ease;
}

@keyframes floatBook {
  0%,
  100% {
    transform: rotateY(-18deg) rotateX(9deg) translateY(0);
  }
  50% {
    transform: rotateY(-18deg) rotateX(9deg) translateY(-8px);
  }
}

@keyframes shakeBook {
  0% {
    transform: rotateY(-18deg) rotateX(9deg) rotateZ(0deg) scale(1);
  }
  20% {
    transform: rotateY(-18deg) rotateX(9deg) rotateZ(-2deg) scale(1.02);
  }
  40% {
    transform: rotateY(-18deg) rotateX(9deg) rotateZ(2deg) scale(1.03);
  }
  60% {
    transform: rotateY(-18deg) rotateX(9deg) rotateZ(-2deg) scale(1.02);
  }
  80% {
    transform: rotateY(-18deg) rotateX(9deg) rotateZ(1deg) scale(1.01);
  }
  100% {
    transform: rotateY(-18deg) rotateX(9deg) rotateZ(0deg) scale(1);
  }
}

/* 输入框抖动动画 */
@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  10%,
  30%,
  50%,
  70%,
  90% {
    transform: translateX(-4px);
  }
  20%,
  40%,
  60%,
  80% {
    transform: translateX(4px);
  }
}
.animate-shake {
  animation: shake 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

/* 答案弹窗过渡动画 */
.answer-modal-enter-active,
.answer-modal-leave-active {
  transition: background-color 260ms ease;
}
.answer-modal-enter-active .answer-modal-panel,
.answer-modal-leave-active .answer-modal-panel {
  transition:
    transform 300ms cubic-bezier(0.2, 0.8, 0.2, 1),
    opacity 300ms ease;
}
.answer-modal-enter-from {
  background-color: rgba(0, 0, 0, 0);
}
.answer-modal-enter-from .answer-modal-panel {
  opacity: 0;
  transform: translateY(18px) scale(0.96);
}
.answer-modal-leave-to {
  background-color: rgba(0, 0, 0, 0);
}
.answer-modal-leave-to .answer-modal-panel {
  opacity: 0;
  transform: translateY(14px) scale(0.98);
}

.egg-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #6d28d9;
  background: rgba(237, 233, 254, 0.95);
  border: 1px solid rgba(167, 139, 250, 0.45);
}

.answer-modal-panel--egg {
  border-color: rgba(167, 139, 250, 0.45);
  background: linear-gradient(180deg, #faf5ff 0%, #ffffff 58%, #fff7ed 100%);
  box-shadow: 0 18px 40px rgba(109, 40, 217, 0.18);
}

.answer-modal-panel--egg-midnight {
  background: linear-gradient(180deg, #1e1b4b 0%, #312e81 42%, #ffffff 100%);
}
.answer-modal-panel--egg-midnight .egg-badge,
.answer-modal-panel--egg-midnight p {
  color: #e0e7ff;
}
.answer-modal-panel--egg-midnight .text-slate-500 {
  color: #c7d2fe;
}
.answer-modal-panel--egg-midnight .text-slate-900 {
  color: #f8fafc;
}

.answer-modal-panel--egg-rain {
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
}

.answer-modal-panel--egg-snow {
  background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%);
}

.answer-modal-panel--egg-dawn {
  background: linear-gradient(180deg, #fff7ed 0%, #ffffff 100%);
}

.answer-modal-panel--egg-solar,
.answer-modal-panel--egg-festival {
  background: linear-gradient(180deg, #fffbeb 0%, #ffffff 100%);
}

.book-wrap--egg .book-glow {
  width: 90%;
  height: 24px;
  filter: blur(6px);
  animation: egg-glow-pulse 1.2s ease-in-out infinite;
}

.book-wrap--egg-rain .book-glow {
  background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.45), transparent 70%);
}

.book-wrap--egg-midnight .book-glow {
  background: radial-gradient(ellipse at center, rgba(129, 140, 248, 0.55), transparent 70%);
}

.book-wrap--egg-dawn .book-glow,
.book-wrap--egg-solar .book-glow,
.book-wrap--egg-festival .book-glow {
  background: radial-gradient(ellipse at center, rgba(251, 191, 36, 0.5), transparent 70%);
}

.book-wrap--egg-snow .book-glow {
  background: radial-gradient(ellipse at center, rgba(186, 230, 253, 0.55), transparent 70%);
}

@keyframes egg-glow-pulse {
  0%,
  100% {
    opacity: 0.65;
    transform: translateX(-50%) scale(0.95);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.05);
  }
}
</style>
