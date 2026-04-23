<template>
  <div class="min-h-screen bg-[#0f0a1e] text-white pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">📖</span>
      <h1 class="text-2xl font-bold">答案之书</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <p class="text-slate-400 text-sm text-center">闭上眼，在心里默念你的问题</p>

      <div class="flex gap-2 justify-center">
        <button
          class="px-4 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full text-xs text-blue-300"
        >
          焦虑
        </button>
        <button
          class="px-4 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full text-xs text-purple-300"
        >
          迷茫
        </button>
        <button
          class="px-4 py-1 bg-pink-500/20 border border-pink-500/30 rounded-full text-xs text-pink-300"
        >
          期待
        </button>
      </div>

      <section>
        <h2 class="text-lg font-semibold mb-3">你的问题</h2>
        <textarea
          v-model="question"
          rows="3"
          class="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:border-purple-500"
          placeholder="午饭吃啥？要不要回那条消息？..."
        ></textarea>
        <div class="flex gap-3 mt-4">
          <button @click="showAnswer" class="flex-1 bg-purple-600 rounded-xl py-2">开启答案</button>
          <button
            @click="showAnswer"
            class="flex-1 bg-white/10 border border-white/20 rounded-xl py-2"
          >
            模拟摇晃
          </button>
        </div>
      </section>

      <section class="text-center">
        <div
          @click="showAnswer"
          class="inline-flex items-center justify-center w-48 h-64 rounded-2xl bg-gradient-to-br from-indigo-900 via-purple-900 to-indigo-950 border-l-8 border-indigo-400 shadow-2xl cursor-pointer active:scale-95 transition"
        >
          <span class="text-6xl">📖</span>
        </div>
        <p class="text-xs text-slate-500 mt-3">轻触书籍，抽一句指引</p>
      </section>

      <section>
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold">回溯复盘</h2>
          <button class="text-xs text-purple-400">查看更多</button>
        </div>
        <div class="space-y-3">
          <div
            v-for="item in history"
            :key="item.id"
            class="flex gap-3 items-center p-3 bg-white/5 rounded-xl"
          >
            <div class="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
              {{ item.icon }}
            </div>
            <div class="flex-1">
              <p class="text-xs font-medium truncate">问：{{ item.question }}</p>
              <p class="text-[10px] text-slate-500">「{{ item.answer }}」</p>
            </div>
            <span class="text-[10px] text-slate-500">{{ item.date }}</span>
          </div>
        </div>
      </section>
    </main>

    <!-- 答案弹窗 -->
    <div
      v-if="modalVisible"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-6"
      @click.self="hideAnswer"
    >
      <div class="bg-[#1e1932] border border-white/20 rounded-3xl w-full max-w-sm p-8 text-center">
        <span class="text-4xl">✨</span>
        <p class="text-xl font-bold leading-relaxed my-6">{{ currentAnswer }}</p>
        <button
          @click="hideAnswer"
          class="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl font-bold"
        >
          我明白了
        </button>
        <div class="flex justify-center gap-4 mt-6">
          <button class="text-xs text-slate-400 flex items-center gap-1">📤 分享卡片</button>
          <button class="text-xs text-slate-400 flex items-center gap-1">🔖 存入收藏</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const question = ref('')
const modalVisible = ref(false)
const currentAnswer = ref('')

const answerPool = [
  '答案就在你最初的想法里。',
  '现在不是犹豫的时候，全速前进。',
  '你需要寻求他人的建议再做决定。',
  '放下执着，你会看到更好的选择。',
  '答案比你想象的要简单得多。',
  '有些事情值得你再等一等。',
  '当你开始爱自己，答案就会浮现。',
]

const showAnswer = () => {
  const random = answerPool[Math.floor(Math.random() * answerPool.length)]
  currentAnswer.value = `宇宙说：${random}`
  modalVisible.value = true
}

const hideAnswer = () => {
  modalVisible.value = false
}

// 模拟历史数据
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
</script>
