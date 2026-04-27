<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <header class="flex items-center gap-2 px-6 pt-6 pb-2">
      <span class="text-2xl">👤</span>
      <h1 class="text-2xl font-bold">我的</h1>
    </header>

    <main class="px-6 py-4 space-y-8">
      <!-- 快捷入口 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">快捷入口</h2>
        <ul class="space-y-2">
          <li
            class="p-3 bg-white border border-slate-200 rounded-xl flex justify-between items-center cursor-pointer"
          >
            <span>⭐ 收藏的答案</span>
            <span class="text-sm text-slate-500">{{ favoriteCount }}</span>
          </li>
          <li
            class="p-3 bg-white border border-slate-200 rounded-xl flex justify-between items-center cursor-pointer"
          >
            <span>📅 历史运势记录</span>
            <span class="text-sm text-slate-500">{{ historyCount }}</span>
          </li>
        </ul>
      </section>

      <!-- 情绪日记本：月度概览 + 今日心情按钮 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">情绪日记本</h2>
        <MonthlyMoodOverview ref="monthlyOverviewRef" />
        <div class="mt-4">
          <button
            @click="openMoodModal"
            class="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2.5 rounded-xl transition"
          >
            📝 今日心情
          </button>
        </div>
      </section>

      <!-- 个人运势图谱（占位） -->
      <section>
        <h2 class="text-lg font-semibold mb-3">个人运势图谱</h2>
        <div
          class="bg-white border border-slate-200 rounded-xl p-6 text-center text-slate-400 shadow-sm"
        >
          📊 图表占位（后续接入 ECharts）
        </div>
      </section>
    </main>

    <!-- 模态框 -->
    <MoodDiaryModal ref="moodModalRef" @submitted="onDiarySubmitted" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MonthlyMoodOverview from '@/components/business/MonthlyMoodOverview.vue'
import MoodDiaryModal from '@/components/business/MoodDiaryModal.vue'
import { saveDiary } from '@/utils/storage'

import type { MoodTag } from '@/utils/storage'

interface DiaryData {
  date: string
  moodTag: MoodTag
  content: string
}
const favoriteCount = ref(15)
const historyCount = ref(28)

const moodModalRef = ref<InstanceType<typeof MoodDiaryModal> | null>(null)
const monthlyOverviewRef = ref<InstanceType<typeof MonthlyMoodOverview> | null>(null)

const openMoodModal = () => {
  moodModalRef.value?.open()
}

// 提交日记后的回调：保存到本地存储并刷新日历
const onDiarySubmitted = (data: DiaryData) => {
  saveDiary({
    date: data.date,
    moodTag: data.moodTag,
    content: data.content,
  })
  monthlyOverviewRef.value?.refresh()
}

// ==================== Pinia 接入示例（注释） ====================
/*
import { useUserStore } from '@/stores/user'
import { useAnswerStore } from '@/stores/answer'
import { useDiaryStore } from '@/stores/diary'
import { useFortuneStore } from '@/stores/fortune'
import { computed, onMounted } from 'vue'
import { getUserProfile, getFavoriteAnswers, getFortuneHistory } from '@/api/user'

const userStore = useUserStore()
const answerStore = useAnswerStore()
const diaryStore = useDiaryStore()
const fortuneStore = useFortuneStore()

const favoriteCount = computed(() => answerStore.favoriteTotal)
const historyCount = computed(() => fortuneStore.historyTotal)

const onDiarySubmitted = async (data) => {
  await diaryStore.saveEntry({
    moodTag: data.moodTag,
    content: data.content,
    isPublic: false,
  })
  // 刷新月度概览（重新获取当月数据）
  await monthlyOverviewRef.value?.refresh()
}

onMounted(async () => {
  if (!userStore.userInfo) {
    const profile = await getUserProfile()
    userStore.setUserInfo(profile.userInfo)
  }
  if (answerStore.favoriteList.length === 0) {
    const favRes = await getFavoriteAnswers()
    answerStore.setFavoriteList(favRes.list, favRes.total)
  }
  if (fortuneStore.historyTotal === 0) {
    const historyRes = await getFortuneHistory()
    // set history...
  }
  if (diaryStore.timelineList.length === 0) {
    await diaryStore.fetchTimeline()
  }
})
*/
</script>
