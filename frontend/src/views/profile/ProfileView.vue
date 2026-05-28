<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <div class="relative bg-gradient-to-r from-purple-50 to-indigo-50 pt-8 pb-6 px-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div
            class="w-16 h-16 rounded-full bg-purple-200 flex items-center justify-center overflow-hidden"
          >
            <img :src="displayAvatar" class="w-full h-full object-cover" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-slate-800">
              {{ userStore.userInfo?.nickname || '未登录' }}
            </h2>
            <div class="flex justify-between items-center mt-1 gap-4">
              <span class="text-xs text-slate-500"> 🎂 {{ formattedBirthday }} </span>
              <span class="text-xs text-slate-500 flex items-center gap-1">
                {{ genderIcon }} {{ genderText }}
              </span>
            </div>
            <p class="mt-1 text-[11px] text-slate-400">位置：{{ locationDisplayText }}</p>
          </div>
        </div>
      </div>
    </div>

    <main class="px-6 py-4 space-y-8">
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
          <li
            class="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 bg-white p-3"
            @click="router.push('/profile/settings')"
          >
            <div class="flex items-center gap-2">
              <IconSettings />
              <span>设置</span>
            </div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 text-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 18l6-6-6-6" />
            </svg>
          </li>
        </ul>
      </section>

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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUserProfile } from '@/api/user'
import { getHistoryFortune } from '@/api/fortune'
import { getFavoriteAnswers } from '@/api/answer'
import MonthlyMoodOverview from '@/components/business/MonthlyMoodOverview.vue'
import MoodDiaryModal from '@/components/business/MoodDiaryModal.vue'
import { saveDiaryOfflineFirst } from '@/utils/diaryService'
import type { MoodTag } from '@/utils/storage'
import IconSettings from '@/components/icons/IconSettings.vue'
import { getValidAvatar } from '@/utils/avatar'

interface DiaryData {
  date: string
  moodTag: MoodTag
  content: string
}

const router = useRouter()
const userStore = useUserStore()
const favoriteCount = ref(0)
const historyCount = ref(0)

const moodModalRef = ref<InstanceType<typeof MoodDiaryModal> | null>(null)
const monthlyOverviewRef = ref<InstanceType<typeof MonthlyMoodOverview> | null>(null)

const displayAvatar = computed(() => getValidAvatar(userStore.userInfo?.avatar))

const genderIcon = computed(() => {
  const gender = userStore.userInfo?.gender
  switch (gender) {
    case 'male':
      return '♂'
    case 'female':
      return '♀'
    default:
      return '🔒'
  }
})

const genderText = computed(() => {
  const gender = userStore.userInfo?.gender
  switch (gender) {
    case 'male':
      return '男'
    case 'female':
      return '女'
    default:
      return '保密'
  }
})

const formattedBirthday = computed(() => {
  const birthday = userStore.userInfo?.birthday
  if (!birthday) return '未填写'
  const [year, month, day] = birthday.split('-')
  return `${year}年${month}月${day}日`
})

const locationDisplayText = computed(() => {
  const latitude = userStore.userInfo?.latitude
  const longitude = userStore.userInfo?.longitude
  const updatedAt = userStore.userInfo?.locationUpdatedAt

  if (typeof latitude !== 'number' || typeof longitude !== 'number') {
    return '未保存'
  }

  const coordinateText = `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`
  if (!updatedAt) return coordinateText

  const timeText = updatedAt.replace('T', ' ').slice(0, 19)
  return `${coordinateText}（${timeText}）`
})

const openMoodModal = () => moodModalRef.value?.open()

const onDiarySubmitted = async (data: DiaryData) => {
  await saveDiaryOfflineFirst({
    date: data.date,
    moodTag: data.moodTag,
    content: data.content,
  })
  monthlyOverviewRef.value?.refresh()
}

const fetchFavoriteCount = async () => {
  try {
    const res = await getFavoriteAnswers(1, 1)
    favoriteCount.value = res.total
  } catch (err) {
    console.error('获取收藏数量失败', err)
  }
}

const fetchHistoryCount = async () => {
  try {
    const res = await getHistoryFortune(1, 1)
    historyCount.value = res.total
  } catch (err) {
    console.error('获取历史运势总数失败', err)
  }
}

const refreshCounts = async () => {
  await Promise.all([fetchFavoriteCount(), fetchHistoryCount()])
}

const handleAnswersUpdated = () => {
  fetchFavoriteCount()
}

onMounted(async () => {
  if (localStorage.getItem('token') && !userStore.userInfo) {
    try {
      const profile = await getUserProfile()
      userStore.setUserInfo(profile.userInfo)
    } catch {
      // 静默失败
    }
  }
  await refreshCounts()
  window.addEventListener('answers-updated', handleAnswersUpdated)
})

onActivated(() => {
  refreshCounts()
})

onUnmounted(() => {
  window.removeEventListener('answers-updated', handleAnswersUpdated)
})
</script>
