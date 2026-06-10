<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <div class="relative bg-gradient-to-r from-purple-50 to-indigo-50 pt-8 pb-6 px-6">
      <div class="flex items-center justify-between">
        <!-- 左侧：头像 + 基本信息 -->
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
            <div class="mt-1">
              <!-- 生日区域 -->
              <span class="text-xs text-slate-500 flex items-center gap-1">
                <span>🎂</span>
                {{ formattedBirthday }}
              </span>
              <!-- 性别区域：仅当性别为男或女时显示，放在生日下方 -->
              <span
                v-if="
                  userStore.userInfo?.gender === 'male' || userStore.userInfo?.gender === 'female'
                "
                class="text-sm text-slate-500 flex items-center gap-1 mt-1"
              >
                <svg
                  v-if="userStore.userInfo?.gender === 'male'"
                  class="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="10" r="4" />
                  <path d="M15 13L20 18" />
                  <path d="M18 16L20 18L18 20" />
                </svg>
                <svg
                  v-else-if="userStore.userInfo?.gender === 'female'"
                  class="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="10" r="4" />
                  <path d="M12 14v6" />
                  <path d="M9 17h6" />
                </svg>
                {{ genderText }}
              </span>
            </div>
          </div>
        </div>

        <!-- 右侧：已佩戴徽章区域 -->
        <div class="flex items-center gap-1 flex-shrink-0">
          <div
            v-for="badge in displayEquippedBadges"
            :key="badge.code"
            class="group relative cursor-pointer"
            @click="goToBadges"
          >
            <img
              :src="getBadgeIconUrl(badge.code, false)"
              :alt="badge.name"
              class="h-10 w-10 rounded-full object-contain transition-transform hover:scale-110"
              @error="handleBadgeImageError"
            />
            <div
              class="absolute bottom-full left-1/2 mb-1 hidden -translate-x-1/2 whitespace-nowrap rounded bg-slate-800 px-2 py-1 text-xs text-white group-hover:block"
            >
              {{ badge.name }} Lv.{{ badge.level }}
            </div>
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
            @click="router.push('/profile/badges')"
          >
            <span>🏅 管理我的徽章</span>
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
            class="w-full bg-purple-500 hover:bg-purple-700 text-white font-medium py-2.5 rounded-xl transition"
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
import { getEquippedBadges, type EquippedBadge } from '@/api/badge'
import MonthlyMoodOverview from '@/components/business/MonthlyMoodOverview.vue'
import MoodDiaryModal from '@/components/business/MoodDiaryModal.vue'
import { saveDiaryOfflineFirst } from '@/utils/diaryService'
import type { MoodTag } from '@/utils/storage'
import IconSettings from '@/components/icons/IconSettings.vue'
import { getValidAvatar } from '@/utils/avatar'
import { getBadgeIconUrl, BADGE_SORT_MAP } from '@/utils/badgeUtils'

interface DiaryData {
  date: string
  moodTag: MoodTag
  content: string
}

const router = useRouter()
const userStore = useUserStore()
const favoriteCount = ref(0)
const historyCount = ref(0)
const equippedBadges = ref<EquippedBadge[]>([])

const moodModalRef = ref<InstanceType<typeof MoodDiaryModal> | null>(null)
const monthlyOverviewRef = ref<InstanceType<typeof MonthlyMoodOverview> | null>(null)

const displayAvatar = computed(() => getValidAvatar(userStore.userInfo?.avatar))

// 性别显示文本
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
  return `${year}/${month}/${day}`
})

// 按等级降序、sort_order升序排列显示的徽章
const displayEquippedBadges = computed(() => {
  const list = [...equippedBadges.value]
  return list.sort((a, b) => {
    if (a.level !== b.level) {
      return b.level - a.level
    }
    const sortA = BADGE_SORT_MAP[a.code] ?? 999
    const sortB = BADGE_SORT_MAP[b.code] ?? 999
    return sortA - sortB
  })
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

const fetchEquippedBadges = async () => {
  try {
    const res = await getEquippedBadges()
    equippedBadges.value = res.list
  } catch (err) {
    console.error('获取已佩戴徽章失败', err)
  }
}

const refreshCounts = async () => {
  await Promise.all([fetchFavoriteCount(), fetchHistoryCount(), fetchEquippedBadges()])
}

const handleAnswersUpdated = () => {
  fetchFavoriteCount()
}

const handleBadgesEquippedUpdated = () => {
  fetchEquippedBadges()
}

const goToBadges = () => {
  router.push('/profile/badges')
}

const handleBadgeImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.src =
    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2394A3B8"%3E%3Cpath d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/%3E%3C/svg%3E'
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
  window.addEventListener('badges-equipped-updated', handleBadgesEquippedUpdated)
})

onActivated(() => {
  refreshCounts()
})

onUnmounted(() => {
  window.removeEventListener('answers-updated', handleAnswersUpdated)
  window.removeEventListener('badges-equipped-updated', handleBadgesEquippedUpdated)
})
</script>
