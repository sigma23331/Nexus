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
            @click="router.push('/profile/favorites')"
          >
            <span>⭐ 收藏的答案</span>
            <span class="text-sm text-slate-500">{{ favoriteCount }}</span>
          </li>
          <li
            class="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 bg-white p-3"
            @click="router.push('/profile/history-fortune')"
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
    </main>

    <MoodDiaryModal ref="moodModalRef" @submitted="onDiarySubmitted" />
    <SettingModal ref="settingModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUserProfile } from '@/api/user'
import { getHistoryFortune } from '@/api/fortune'
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

const router = useRouter()
const userStore = useUserStore()
const favoriteCount = ref(15)
const historyCount = ref(0) // 初始为0，后续从API获取

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
  // 获取用户信息（如果已登录但store中没有）
  if (localStorage.getItem('token') && !userStore.userInfo) {
    try {
      const profile = await getUserProfile()
      userStore.setUserInfo(profile.userInfo)
      if (profile.stats) {
        favoriteCount.value = profile.stats.answerCollected || 15
        // 注意：profile.stats.diaryCount 是日记数，不是运势记录数，所以不在这里设置 historyCount
      }
    } catch {
      // 静默失败
    }
  }

  // 单独获取历史运势总数
  try {
    const res = await getHistoryFortune(1, 1) // 只请求第一页，limit=1，仅获取total
    historyCount.value = res.total
  } catch (error) {
    console.error('获取历史运势总数失败', error)
    historyCount.value = 0
  }
})
</script>
