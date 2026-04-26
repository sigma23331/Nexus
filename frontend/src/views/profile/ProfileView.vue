<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">👤</span>
      <h1 class="text-2xl font-bold">我的</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <section>
        <h2 class="text-lg font-semibold mb-3">快捷入口</h2>
        <ul class="space-y-2">
          <li class="p-3 bg-white border border-slate-200 rounded-xl cursor-pointer">
            ⭐ 收藏的答案（{{ favoriteCount }}）
          </li>
          <li class="p-3 bg-white border border-slate-200 rounded-xl cursor-pointer">
            📅 历史运势记录
          </li>
        </ul>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">情绪日记本</h2>
        <div class="space-y-4">
          <label class="block text-sm"
            >日期
            <input
              type="date"
              v-model="diaryDate"
              class="w-full mt-1 bg-white border border-slate-200 rounded-lg p-2 text-slate-800"
            />
          </label>
          <label class="block text-sm"
            >心情
            <div class="mt-2 grid grid-cols-6 gap-2">
              <button
                v-for="emoji in moodEmojis"
                :key="emoji.value"
                type="button"
                @click="selectedMood = emoji.value"
                :class="[
                  'h-12 rounded-lg border text-lg transition-all',
                  selectedMood === emoji.value
                    ? 'border-purple-500 bg-purple-50 ring-2 ring-purple-200'
                    : 'border-slate-200 bg-white',
                ]"
              >
                {{ emoji.emoji }}
              </button>
            </div>
          </label>
          <label class="block text-sm"
            >备注
            <textarea
              v-model="diaryNote"
              rows="2"
              class="w-full mt-1 bg-white border border-slate-200 rounded-lg p-2 text-slate-800 placeholder:text-slate-400"
              placeholder="记录今天的心情..."
            ></textarea>
          </label>
          <button @click="saveDiary" class="w-full bg-purple-600 rounded-xl py-2 text-white">
            保存日记
          </button>
        </div>
      </section>

      <section>
        <h2 class="text-lg font-semibold mb-3">个人运势图谱</h2>
        <div class="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center text-slate-400">
          📊 图表占位
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// ==================== 静态数据（暂未连接 Pinia） ====================
const favoriteCount = ref(15)
const diaryDate = ref(new Date().toISOString().slice(0, 10))
const selectedMood = ref('happy')
const diaryNote = ref('')

const moodEmojis = [
  { emoji: '😄', value: 'happy' },
  { emoji: '😌', value: 'calm' },
  { emoji: '😴', value: 'tired' },
  { emoji: '😟', value: 'anxious' },
  { emoji: '😡', value: 'angry' },
  { emoji: '😢', value: 'sad' },
]

const saveDiary = () => {
  // 模拟保存，实际应调用 API
  // console.log('保存日记', { date: diaryDate.value, mood: selectedMood.value, note: diaryNote.value })
  // alert('日记已保存（演示模式）')
  diaryNote.value = ''
}

// ==================== Pinia 接入示例（注释） ====================
/*
import { useUserStore } from '@/stores/user'
import { useAnswerStore } from '@/stores/answer'
import { useDiaryStore } from '@/stores/diary'   // 假设有日记 store
import { computed, onMounted } from 'vue'

const userStore = useUserStore()
const answerStore = useAnswerStore()
const diaryStore = useDiaryStore()

// 收藏数量从 answerStore 获取
const favoriteCount = computed(() => answerStore.favoriteTotal)

// 保存日记：调用 diaryStore 的 action
const saveDiary = async () => {
  await diaryStore.saveEntry({
    moodTag: selectedMood.value,
    content: diaryNote.value,
    isPublic: false
  })
  diaryNote.value = ''
  // 刷新日记列表
  await diaryStore.fetchTimeline()
}

// 在 onMounted 中加载用户信息、收藏列表、日记列表
onMounted(async () => {
  if (!userStore.userInfo) {
    const profile = await getUserProfile()
    userStore.setUserInfo(profile.userInfo)
  }
  if (answerStore.favoriteList.length === 0) {
    const favRes = await getFavoriteAnswers()
    answerStore.setFavoriteList(favRes.list, favRes.total)
  }
  if (diaryStore.timelineList.length === 0) {
    await diaryStore.fetchTimeline()
  }
})
*/
</script>
