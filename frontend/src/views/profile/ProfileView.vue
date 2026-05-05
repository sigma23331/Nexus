<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <!-- 用户信息头部 -->
    <div class="relative bg-gradient-to-r from-purple-50 to-indigo-50 pt-8 pb-6 px-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div
            class="w-16 h-16 rounded-full bg-purple-200 flex items-center justify-center overflow-hidden"
          >
            <img
              v-if="userStore.userInfo?.avatar"
              :src="userStore.userInfo.avatar"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-3xl">👤</span>
          </div>
          <div>
            <h2 class="text-xl font-bold text-slate-800">
              {{ userStore.userInfo?.nickname || '未登录' }}
            </h2>
            <p class="text-xs text-slate-500 mt-1">UID: {{ userStore.userInfo?.uid || '--' }}</p>
          </div>
        </div>
        <button
          @click="openSettings"
          class="p-2 rounded-full hover:bg-slate-100 text-2xl text-slate-600"
        >
          ⚙️
        </button>
      </div>
    </div>

    <main class="px-6 py-4 space-y-8">
      <!-- 快捷入口 -->
      <section>
        <ul class="space-y-2">
          <li
            class="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 bg-white p-3"
          >
            <span>⭐ 收藏的答案</span>
            <span class="text-sm text-slate-500">{{ favoriteCount }}</span>
          </li>
          <li
            class="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 bg-white p-3"
          >
            <span>📅 历史运势记录</span>
            <span class="text-sm text-slate-500">{{ historyCount }}</span>
          </li>
        </ul>
      </section>

      <!-- 情绪日记本 -->
      <section>
        <h2 class="text-lg font-semibold mb-3">情绪日记本</h2>
        <router-link
          to="/profile/mood-timeline"
          class="mb-3 flex items-center justify-between rounded-xl border border-violet-200 bg-violet-50/80 px-4 py-3 text-sm font-medium text-violet-900 shadow-sm transition hover:bg-violet-100"
        >
          <span>📿 心情时间轴</span>
          <span class="text-xs text-violet-600">按日查看</span>
        </router-link>
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

      <!-- 个人运势图谱 -->
      <!-- <section>
        <h2 class="text-lg font-semibold mb-3">个人运势图谱</h2>
        <div
          class="bg-white border border-slate-200 rounded-xl p-6 text-center text-slate-400 shadow-sm"
        >
          📊 图表占位（后续接入 ECharts）
        </div>
      </section> -->
    </main>

    <MoodDiaryModal ref="moodModalRef" @submitted="onDiarySubmitted" />
    <SettingModal ref="settingModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getUserProfile } from '@/api/user'
import MonthlyMoodOverview from '@/components/business/MonthlyMoodOverview.vue'
import MoodDiaryModal from '@/components/business/MoodDiaryModal.vue'
import SettingModal from '@/components/common/SettingModal.vue'
import { saveDiaryOfflineFirst } from '@/utils/diaryService'
import type { MoodTag } from '@/utils/storage'

interface DiaryData {
  date: string
  moodTag: MoodTag
  content: string
}

const userStore = useUserStore()
const favoriteCount = ref(15)
const historyCount = ref(28)

const moodModalRef = ref<InstanceType<typeof MoodDiaryModal> | null>(null)
const monthlyOverviewRef = ref<InstanceType<typeof MonthlyMoodOverview> | null>(null)
const settingModalRef = ref<InstanceType<typeof SettingModal> | null>(null)

const openMoodModal = () => moodModalRef.value?.open()
const openSettings = () => settingModalRef.value?.open()

const onDiarySubmitted = async (data: DiaryData) => {
  await saveDiaryOfflineFirst({
    date: data.date,
    moodTag: data.moodTag,
    content: data.content,
  })
  // 刷新月度概览
  monthlyOverviewRef.value?.refresh()
}

onMounted(async () => {
  if (localStorage.getItem('token') && !userStore.userInfo) {
    try {
      const profile = await getUserProfile()
      userStore.setUserInfo(profile.userInfo)
      if (profile.stats) {
        favoriteCount.value = profile.stats.answerCollected || 15
        historyCount.value = profile.stats.diaryCount || 28
      }
    } catch {
      // 静默失败
    }
  }
})
</script>
