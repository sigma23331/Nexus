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
                ? 'bg-purple-600 text-white hover:bg-purple-700'
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
        <div class="book-wrap mx-auto" :class="{ shaking: isShaking }" @click="drawAnswer">
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
          <router-link
            :to="{ name: 'answer-history' }"
            class="text-xs font-medium text-purple-600 hover:text-purple-700"
          >
            查看更多
          </router-link>
        </div>
        <div class="space-y-3">
          <div
            v-for="item in recentAnswers"
            :key="item.id"
            class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 cursor-pointer hover:bg-slate-50 transition"
            @click="openDetail(item)"
          >
            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-pink-500/20"
            >
              ✨
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-xs font-medium">问：{{ item.question }}</p>
              <p class="line-clamp-1 text-[10px] text-slate-500">「{{ item.answerText }}」</p>
            </div>
            <span class="shrink-0 text-[10px] text-slate-500">{{
              formatDate(item.createdAt)
            }}</span>
          </div>
          <div
            v-if="recentAnswers.length === 0 && !loadingHistory"
            class="text-center text-xs text-slate-400 py-4"
          >
            暂无历史记录，去提问吧
          </div>
          <div v-if="loadingHistory" class="text-center text-xs text-slate-400 py-2">加载中...</div>
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
          class="answer-modal-panel bg-white border border-slate-200 rounded-3xl w-full max-w-sm p-8 text-center"
        >
          <span class="text-4xl">✨</span>
          <p class="mt-3 text-xs text-slate-500">你问：{{ currentQuestion }}</p>
          <p class="my-6 text-xl font-bold leading-relaxed text-slate-900">
            {{ currentAnswer }}
          </p>
          <button
            @click="hideAnswer"
            class="w-full rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 py-4 font-bold text-white"
          >
            我明白了
          </button>
          <div class="mt-6 flex justify-center gap-4">
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

function formatDate(iso: string) {
  return dayjs(iso).format('MM月DD日')
}

// 加载最近5条历史记录
async function loadRecentHistory() {
  loadingHistory.value = true
  try {
    const local = getLocalAnswerList()
    recentAnswers.value = local.slice(0, 5)
    await fetchAndSyncHistory(1, 5)
    const updated = getLocalAnswerList()
    recentAnswers.value = updated.slice(0, 5)
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

  try {
    const res = await askQuestion(question.value.trim())
    currentQuestion.value = res.question
    currentAnswer.value = `宇宙说：${res.answerText}`
    currentAnswerId.value = res.id
    currentIsFavorited.value = false
    modalVisible.value = true

    const newItem: AnswerHistoryItem = {
      id: res.id,
      question: res.question,
      answerText: res.answerText,
      createdAt: res.createdAt,
      isFavorited: false,
    }
    addLocalAnswer(newItem)
    recentAnswers.value = [newItem, ...recentAnswers.value.slice(0, 4)]
    question.value = ''
  } catch (err) {
    console.error('提问失败', err)
    alert('提问失败，请重试')
  } finally {
    isShaking.value = false
    isDrawing.value = false
  }
}

// 收藏/取消收藏
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

function hideAnswer() {
  modalVisible.value = false
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
  border-radius: 18px;
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
  border-radius: 18px;
  border: 1px solid #a5b4fc;
  background: linear-gradient(145deg, #6366f1 0%, #8b5cf6 62%, #a855f7 100%);
  box-shadow: 0 18px 36px rgba(99, 102, 241, 0.34);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 18px 14px;
}

.book-spine {
  position: absolute;
  left: -14px;
  top: 10px;
  width: 16px;
  height: calc(100% - 20px);
  border-radius: 10px;
  background: linear-gradient(180deg, #4338ca 0%, #312e81 70%, #1e1b4b 100%);
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
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(199, 210, 254, 0.7), rgba(165, 180, 252, 0.2));
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
</style>
