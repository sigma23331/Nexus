<template>
  <div class="min-h-screen bg-gradient-to-b from-amber-50 to-white pb-8">
    <!-- 头部：返回按钮 + 标题 -->
    <div class="sticky top-0 z-10 bg-white/80 backdrop-blur-sm border-b border-amber-100">
      <div class="flex items-center px-4 py-3">
        <button @click="goBack" class="p-2 -ml-2 rounded-full hover:bg-amber-50">
          <svg class="w-5 h-5 text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        <h1 class="flex-1 text-center text-lg font-bold text-slate-800">运势挑战</h1>
        <div class="w-8"></div>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-pulse text-amber-600">加载中...</div>
    </div>

    <!-- 错误提示 -->
    <div
      v-else-if="errorMsg"
      class="flex flex-col items-center justify-center py-20 px-6 text-center"
    >
      <div class="text-rose-500 mb-4 text-5xl">⚠️</div>
      <p class="text-slate-600 mb-4">{{ errorMsg }}</p>
      <button @click="retry" class="px-5 py-2 bg-amber-500 text-white rounded-full text-sm">
        重试
      </button>
    </div>

    <!-- PK内容 -->
    <div v-else-if="pkRecord" class="px-5 py-6 space-y-6">
      <!-- 对战双方卡片 -->
      <div class="grid grid-cols-2 gap-4">
        <!-- 挑战者（发起者） -->
        <div class="bg-white rounded-2xl shadow-md p-4 text-center border border-amber-200">
          <div class="flex justify-center mb-2">
            <img
              :src="getValidAvatar(pkRecord.challenger?.avatar)"
              class="w-16 h-16 rounded-full object-cover border-2 border-amber-300"
              @error="handleAvatarError"
            />
          </div>
          <div class="font-medium text-slate-800">
            {{ pkRecord.challenger?.nickname || '挑战者' }}
          </div>
          <div class="text-sm text-slate-500 mt-1">运势分数</div>
          <div class="text-2xl font-bold text-amber-600">{{ pkRecord.challengerScore }}</div>
        </div>

        <!-- 应战者（防守者） -->
        <div class="bg-white rounded-2xl shadow-md p-4 text-center border border-amber-200">
          <div class="flex justify-center mb-2">
            <img
              :src="getValidAvatar(pkRecord.defender?.avatar)"
              class="w-16 h-16 rounded-full object-cover border-2 border-amber-300"
              @error="handleAvatarError"
            />
          </div>
          <div class="font-medium text-slate-800">
            {{ pkRecord.defender?.nickname || (isDefenderWaiting ? '等待应战...' : '应战者') }}
          </div>
          <div class="text-sm text-slate-500 mt-1">运势分数</div>
          <div class="text-2xl font-bold text-amber-600">
            {{ pkRecord.defenderScore !== null ? pkRecord.defenderScore : '—' }}
          </div>
        </div>
      </div>

      <!-- 比赛结果区域 -->
      <div class="bg-white rounded-2xl shadow-md p-5 border border-amber-200 text-center space-y-3">
        <div v-if="pkRecord.status === 'pending'">
          <div v-if="isChallenger && !pkRecord.defenderId" class="py-4">
            <div class="text-amber-600 text-lg mb-2">✨ 挑战已发出 ✨</div>
            <p class="text-slate-500 text-sm">等待好友接受挑战...</p>
            <button
              @click="resendShare"
              class="mt-4 px-4 py-2 bg-amber-500 text-white rounded-full text-sm"
            >
              重新分享链接
            </button>
          </div>
          <div
            v-else-if="!isChallenger && !pkRecord.defenderId && !isCurrentUserDefender"
            class="py-4"
          >
            <div class="text-amber-600 text-lg mb-2">🤝 欢迎观战</div>
            <p class="text-slate-500 text-sm">挑战尚未被接受，你可以等待应战者加入或分享给朋友～</p>
          </div>
          <div v-else-if="isCurrentUserDefender && !pkRecord.defenderId" class="py-4">
            <!-- 当前登录用户是应战者，但PK还未完成（后端已自动完成，此情况理论上不会出现，因为调用接口时会自动完成，留作后备） -->
            <div class="animate-pulse text-amber-600">正在匹配运势...</div>
          </div>
        </div>

        <div v-else-if="pkRecord.status === 'completed'">
          <div class="text-2xl font-bold" :class="resultColor">
            {{ resultText }}
          </div>
          <div class="text-slate-500 text-sm mt-2">
            挑战时间：{{ formatDate(pkRecord.completedAt) }}
          </div>
          <div class="mt-4 text-xs text-slate-400">
            {{ pkRecord.challenger?.nickname }} VS {{ pkRecord.defender?.nickname }}
          </div>
        </div>

        <div v-else-if="pkRecord.status === 'expired'" class="py-4">
          <div class="text-rose-500 text-lg">⏰ 挑战已过期</div>
          <p class="text-slate-500 text-sm">该挑战链接只在当天有效，可发起新的挑战～</p>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex gap-3 pt-4">
        <button
          @click="goToFortune"
          class="flex-1 py-2.5 bg-white border border-amber-300 text-amber-700 rounded-full text-sm font-medium"
        >
          返回运势看板
        </button>
        <button
          v-if="pkRecord.status === 'pending' && isChallenger"
          @click="resendShare"
          class="flex-1 py-2.5 bg-amber-500 text-white rounded-full text-sm font-medium"
        >
          邀请好友
        </button>
        <button
          v-else-if="pkRecord.status === 'pending' && !isChallenger && !pkRecord.defenderId"
          @click="acceptChallenge"
          class="flex-1 py-2.5 bg-amber-500 text-white rounded-full text-sm font-medium"
        >
          我要应战
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useFortunePK } from '@/composables/useFortunePK'
import type { FortunePKRecord } from '@/types/models'
import { getValidAvatar } from '@/utils/avatar'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { fetchOrJoinPK, shareChallenge } = useFortunePK()

const pkRecord = ref<FortunePKRecord | null>(null)
const loading = ref(true)
const errorMsg = ref('')

// 从路由获取 token
const token = computed(() => route.params.token as string)

// 判断当前用户角色
const isChallenger = computed(() => {
  if (!pkRecord.value || !userStore.userInfo) return false
  return pkRecord.value.challengerId === userStore.userInfo.uid
})
const isCurrentUserDefender = computed(() => {
  if (!pkRecord.value || !userStore.userInfo) return false
  return pkRecord.value.defenderId === userStore.userInfo.uid
})
const isDefenderWaiting = computed(() => {
  return pkRecord.value?.status === 'pending' && !pkRecord.value.defenderId
})

// 结果颜色和文字
const resultColor = computed(() => {
  if (!pkRecord.value?.result) return 'text-slate-600'
  if (pkRecord.value.result === 'challenger_win') return 'text-emerald-600'
  if (pkRecord.value.result === 'defender_win') return 'text-blue-600'
  return 'text-amber-600'
})

const resultText = computed(() => {
  if (!pkRecord.value?.result) return '未知'
  if (pkRecord.value.result === 'challenger_win')
    return `${pkRecord.value.challenger?.nickname} 获胜！`
  if (pkRecord.value.result === 'defender_win') return `${pkRecord.value.defender?.nickname} 获胜！`
  return '平局！'
})

// 加载数据
const loadPK = async () => {
  if (!token.value) {
    errorMsg.value = '无效的挑战链接'
    loading.value = false
    return
  }
  loading.value = true
  errorMsg.value = ''
  try {
    const record = await fetchOrJoinPK(token.value)
    pkRecord.value = record
    // 如果用户是应战者且PK刚刚完成（后端自动完成），刷新后展示结果
    if (record.status === 'completed' && isCurrentUserDefender.value) {
      // 可选：显示成功提示
    }
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : '加载挑战失败，请检查链接是否有效'
  } finally {
    loading.value = false
  }
}

// 重试
const retry = () => {
  loadPK()
}

// 应战：实际上用户访问链接时后端已经自动完成了（如果他是defender），这里刷新即可
const acceptChallenge = async () => {
  await loadPK()
  if (pkRecord.value?.status === 'completed') {
    // 挑战完成，刷新展示结果
  } else if (pkRecord.value?.status === 'pending') {
    alert('你还不是应战者，请使用正确的挑战链接或等待发起者邀请～')
  }
}

// 重新分享链接
const resendShare = async () => {
  if (!pkRecord.value) return
  await shareChallenge(pkRecord.value.token, pkRecord.value.challenger?.nickname || '我')
}

// 返回运势看板
const goToFortune = () => {
  router.push({ name: 'fortune' })
}

// 返回上一页（如果历史记录存在且不是当前页）
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goToFortune()
  }
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

// 本地兜底头像，避免依赖境外 placehold.co（慢且可能不通）
const fallbackAvatar = '/images/avatar.png'

const handleAvatarError = (e: Event) => {
  const img = e.target as HTMLImageElement
  // 如果当前 src 已经是 fallback 则不再循环
  if (img.src !== fallbackAvatar) {
    img.src = fallbackAvatar
  }
}

onMounted(() => {
  loadPK()
})
</script>
