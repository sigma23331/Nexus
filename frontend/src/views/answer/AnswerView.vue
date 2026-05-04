<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">📖</span>
      <h1 class="text-2xl font-bold">答案之书</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <p class="text-slate-400 text-sm text-center">闭上眼，在心里默念你的问题</p>

      <div class="flex gap-2 justify-center">
        <button
          class="px-4 py-1 bg-blue-50 border border-blue-200 rounded-full text-xs text-blue-700"
        >
          焦虑
        </button>
        <button
          class="px-4 py-1 bg-purple-50 border border-purple-200 rounded-full text-xs text-purple-700"
        >
          迷茫
        </button>
        <button
          class="px-4 py-1 bg-pink-50 border border-pink-200 rounded-full text-xs text-pink-700"
        >
          期待
        </button>
      </div>

      <section>
        <h2 class="text-lg font-semibold mb-3">你的问题</h2>
        <textarea
          v-model="question"
          rows="3"
          class="w-full bg-white border border-slate-200 rounded-2xl p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-purple-500"
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
              <p class="mt-2 text-[11px] text-indigo-100/90">轻触抽一条宇宙提示</p>
            </div>
            <div class="book-spine"></div>
            <div class="book-glow"></div>
          </div>
        </div>
        <p class="text-xs text-slate-500 mt-3">轻触书籍，抽一句指引</p>
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
            v-for="item in history"
            :key="item.id"
            class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3"
          >
            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-pink-500/20"
            >
              {{ item.icon }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-xs font-medium">问：{{ item.question }}</p>
              <p class="line-clamp-1 text-[10px] text-slate-500">「{{ item.answer }}」</p>
            </div>
            <span class="shrink-0 text-[10px] text-slate-500">{{ item.date }}</span>
          </div>
        </div>
      </section>
    </main>

    <!-- 答案弹窗 -->
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
          <p class="my-6 text-xl font-bold leading-relaxed text-slate-900">{{ currentAnswer }}</p>
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
            <button type="button" class="flex items-center gap-1 text-xs text-slate-500">
              🔖 存入收藏
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const question = ref('')
const modalVisible = ref(false)
const currentAnswer = ref('')
const currentQuestion = ref('')
const isShaking = ref(false)
const isDrawing = ref(false)

const answerPool = [
  '答案就在你最初的想法里。',
  '现在不是犹豫的时候，全速前进。',
  '你需要寻求他人的建议再做决定。',
  '放下执着，你会看到更好的选择。',
  '答案比你想象的要简单得多。',
  '有些事情值得你再等一等。',
  '当你开始爱自己，答案就会浮现。',
]

const history = ref([
  { id: 1, icon: '✓', question: '要不要去旅行？', answer: '最好的风景就在脚下', date: '4月10日' },
  {
    id: 2,
    icon: '⏳',
    question: '这次面试能过吗？',
    answer: '耐心等待，时机未到',
    date: '4月08日',
  },
])

const canSubmit = computed(() => question.value.trim().length > 0 && !isDrawing.value)

function drawAnswer() {
  if (!canSubmit.value) return
  isDrawing.value = true
  isShaking.value = true

  window.setTimeout(() => {
    const random = answerPool[Math.floor(Math.random() * answerPool.length)]
    const q = question.value.trim()
    currentQuestion.value = q
    currentAnswer.value = `宇宙说：${random}`
    modalVisible.value = true

    history.value.unshift({
      id: Date.now(),
      icon: '✨',
      question: q,
      answer: random,
      date: new Date().toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' }),
    })
    question.value = ''
    isShaking.value = false
    isDrawing.value = false
  }, 900)
}

function hideAnswer() {
  modalVisible.value = false
}
</script>

<style scoped>
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

.book-front::after {
  content: '';
  position: absolute;
  right: -9px;
  top: 10px;
  width: 12px;
  height: calc(100% - 20px);
  border-radius: 8px;
  background: linear-gradient(180deg, #eef2ff 0%, #dbeafe 40%, #c7d2fe 100%);
  opacity: 0.92;
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
