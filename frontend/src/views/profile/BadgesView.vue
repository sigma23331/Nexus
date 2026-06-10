<!-- src/views/profile/BadgesView.vue -->
<template>
  <div class="min-h-screen bg-slate-50 pb-8">
    <div class="bg-gradient-to-r from-purple-50 to-indigo-50 px-5 py-5 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="rounded-full p-2 text-slate-600 transition hover:bg-white/30"
            aria-label="返回"
            @click="goBack"
          >
            <span class="text-lg">←</span>
          </button>
          <div>
            <h1 class="text-2xl font-bold text-slate-800">我的徽章</h1>
          </div>
        </div>
        <div class="text-right">
          <div class="text-3xl font-bold text-purple-500">{{ unlockedCount }}/{{ totalCount }}</div>
          <div class="text-xs text-slate-500">已解锁</div>
        </div>
      </div>
    </div>

    <!-- 佩戴提示 -->
    <div class="mx-4 mt-3 rounded-lg bg-blue-50 px-3 py-2 text-sm text-center text-blue-600">
      最多可佩戴 {{ maxEquipped }} 个徽章，点击徽章详情可进行佩戴/摘下
    </div>

    <div class="mt-2 text-center text-xs text-slate-400 py-2">—— 记录你在心运岛的每一次成长 ——</div>

    <!-- 徽章列表 -->
    <div class="px-4 py-5">
      <div v-if="loading" class="flex justify-center py-12">
        <div
          class="h-8 w-8 animate-spin rounded-full border-4 border-purple-200 border-t-purple-600"
        ></div>
      </div>

      <div v-else-if="badges.length === 0" class="py-16 text-center text-slate-400">
        暂无徽章数据
      </div>

      <div v-else class="grid grid-cols-2 gap-4">
        <BadgeCard
          v-for="badge in badges"
          :key="badge.code"
          :badge="badge"
          @click="openDetail(badge)"
        />
      </div>
    </div>

    <!-- 徽章详情弹窗 -->
    <BadgeDetailModal
      ref="detailModalRef"
      :badge="selectedBadge"
      :equipped-badge-codes="equippedCodes"
      :max-equipped="maxEquipped"
      @update-equipped="handleUpdateEquipped"
    />

    <!-- 新徽章/升级通知弹窗 -->
    <BadgeNotifyModal ref="notifyModalRef" @closed="onNotifyClosed" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getMyBadges,
  getEquippedBadges,
  updateEquippedBadges,
  getBadgeChanges,
  markBadgeChangesRead,
  type UserBadge,
  type EquippedBadge,
} from '@/api/badge'
import BadgeCard from './components/BadgeCard.vue'
import BadgeDetailModal from './components/BadgeDetailModal.vue'
import BadgeNotifyModal from './components/BadgeNotifyModal.vue'

const router = useRouter()
const loading = ref(true)
const badges = ref<UserBadge[]>([])
const unlockedCount = ref(0)
const totalCount = ref(0)
const equippedBadges = ref<EquippedBadge[]>([])
const maxEquipped = ref(3)

const detailModalRef = ref<InstanceType<typeof BadgeDetailModal> | null>(null)
const notifyModalRef = ref<InstanceType<typeof BadgeNotifyModal> | null>(null)

const selectedBadge = ref<UserBadge | null>(null)

// 已佩戴徽章的 code 列表
const equippedCodes = ref<Set<string>>(new Set())

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'profile' })
  }
}

// 加载徽章数据
const fetchBadges = async () => {
  loading.value = true
  try {
    const res = await getMyBadges()
    badges.value = res.list
    unlockedCount.value = res.unlockedCount
    totalCount.value = res.totalCount
  } catch (error) {
    console.error('获取徽章列表失败', error)
  } finally {
    loading.value = false
  }
}

// 加载已佩戴徽章
const fetchEquipped = async () => {
  try {
    const res = await getEquippedBadges()
    equippedBadges.value = res.list
    maxEquipped.value = res.maxEquipped
    equippedCodes.value = new Set(res.list.map((item) => item.code))
  } catch (error) {
    console.error('获取已佩戴徽章失败', error)
  }
}

// 处理佩戴/摘下更新
const handleUpdateEquipped = async (newBadgeCodes: string[]) => {
  try {
    const res = await updateEquippedBadges(newBadgeCodes)
    equippedBadges.value = res.list
    maxEquipped.value = res.maxEquipped
    equippedCodes.value = new Set(res.list.map((item) => item.code))

    // 触发全局事件，通知 ProfileView 刷新
    window.dispatchEvent(new CustomEvent('badges-equipped-updated'))
  } catch (err: unknown) {
    console.error('加载徽章失败', err)
  }
}

// 检查并展示新徽章通知
const checkNewBadges = async () => {
  try {
    const changesRes = await getBadgeChanges()
    if (changesRes.total > 0 && changesRes.list.length) {
      notifyModalRef.value?.open(changesRes.list)
    }
  } catch (error) {
    console.error('获取徽章变化失败', error)
  }
}

const onNotifyClosed = async () => {
  try {
    await markBadgeChangesRead()
    await fetchBadges()
    await fetchEquipped()
  } catch (error) {
    console.error('标记已读失败', error)
  }
}

const openDetail = (badge: UserBadge) => {
  selectedBadge.value = badge
  detailModalRef.value?.open()
}

onMounted(async () => {
  await Promise.all([fetchBadges(), fetchEquipped()])
  await checkNewBadges()
})
</script>
