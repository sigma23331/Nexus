<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <main class="px-6 py-4 space-y-8">
      <!--
      测试卡片生成区域（临时注释）
      <section class="bg-slate-50 rounded-xl p-4 border border-slate-200">
        <h3 class="text-md font-semibold mb-3">🎴 测试生成卡片（点击下载）</h3>
        <div class="flex gap-3">
          <button
            @click="testFortuneCard"
            :disabled="isLoading"
            class="px-4 py-2 bg-purple-600 rounded-lg text-white text-sm"
          >
            {{ isLoading ? '生成中...' : '生成运势卡片' }}
          </button>
          <button
            @click="testAnswerCard"
            :disabled="isLoading"
            class="px-4 py-2 bg-indigo-600 rounded-lg text-white text-sm"
          >
            {{ isLoading ? '生成中...' : '生成答案卡片' }}
          </button>
        </div>
        <p class="text-xs text-slate-500 mt-2">图片将自动下载，可查看效果。</p>
        <canvas ref="cardCanvas" style="display: none"></canvas>
      </section>
      -->

      <!-- ========== 今日树洞入口（新增） ========== -->
      <section>
        <div
          @click="openTreeholeModal"
          class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-50 to-purple-50 p-5 shadow-sm cursor-pointer transition hover:shadow-md active:scale-[0.98]"
        >
          <div class="flex items-center gap-4">
            <div class="text-4xl">🌳</div>
            <div class="flex-1">
              <h3 class="text-base font-bold text-slate-800">今日树洞</h3>
              <p class="text-xs text-slate-500 mt-0.5">把你的烦恼丢进来，它会消失不见～</p>
            </div>
            <div class="text-purple-400 text-xl">→</div>
          </div>
          <!-- 装饰小圆点 -->
          <div
            class="absolute -right-4 -top-4 h-16 w-16 rounded-full bg-purple-200/30 blur-xl"
          ></div>
        </div>
      </section>

      <!-- 分享广场（带分类筛选） -->
      <section>
        <!-- 第一行：分类 + 只看我的 -->
        <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div class="flex gap-2">
            <button
              @click="filterType = 'all'"
              :class="[
                'px-3 py-1 text-sm rounded-full transition-colors',
                filterType === 'all'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              全部
            </button>
            <button
              @click="filterType = 'fortune'"
              :class="[
                'px-3 py-1 text-sm rounded-full transition-colors',
                filterType === 'fortune'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              运势卡片
            </button>
            <button
              @click="filterType = 'answer'"
              :class="[
                'px-3 py-1 text-sm rounded-full transition-colors',
                filterType === 'answer'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              答案卡片
            </button>
          </div>
          <button
            @click="showOnlyMine = !showOnlyMine"
            :class="[
              'px-3 py-1 text-sm rounded-full transition-colors',
              showOnlyMine
                ? 'bg-purple-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
            ]"
          >
            {{ showOnlyMine ? '我的卡片' : '只看我的' }}
          </button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="text-center py-8 text-slate-400">加载中...</div>
        <div v-else-if="error" class="text-center py-8 text-slate-400">服务器出错，请稍后重试</div>
        <div v-else-if="filteredCards.length === 0" class="text-center py-8 text-slate-400">
          暂无数据，去发布第一条吧～
        </div>
        <div v-else class="space-y-4">
          <PlazaCard
            v-for="card in filteredCards"
            :key="card.cardId"
            :card="card"
            :is-owner="card.owner.uid === currentUserId"
            @like="handleLike"
            @delete="handleDeleteCard"
          />
        </div>

        <!-- 加载更多按钮 -->
        <div
          v-if="!error && hasMore && !loading && filteredCards.length > 0"
          class="text-center mt-4"
        >
          <button @click="loadMore" class="text-sm text-purple-600">加载更多</button>
        </div>
      </section>
    </main>

    <!-- 今日树洞输入弹窗 -->
    <TreeholeModal ref="treeholeModalRef" @submit="handleTreeholeSubmit" />

    <!-- 今日树洞结果弹窗（类似答案之书） -->
    <TreeholeResultModal ref="treeholeResultRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import PlazaCard from './components/PlazaCard.vue'
import TreeholeModal from '@/components/business/TreeholeModal.vue'
import TreeholeResultModal from '@/components/business/TreeholeResultModal.vue'
import { getPlazaCards, likePlazaCard, deletePlazaCard } from '@/api/plaza'
import type { PlazaCard as PlazaCardType } from '@/types/models'
import type { GetPlazaCardsParams } from '@/api/plaza'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userInfo?.uid || '')

// 数据状态
const cards = ref<PlazaCardType[]>([])
const loading = ref(false)
const error = ref(false)
const hasMore = ref(true)
const nextCursor = ref<string | null>(null)
const filterType = ref<'all' | 'fortune' | 'answer'>('all')
const currentTab = ref<'hot' | 'latest'>('latest')
const showOnlyMine = ref(false)
const treeholeModalRef = ref<InstanceType<typeof TreeholeModal> | null>(null)
const treeholeResultRef = ref<InstanceType<typeof TreeholeResultModal> | null>(null)

// 打开树洞输入弹窗
const openTreeholeModal = () => {
  treeholeModalRef.value?.open()
}

// 处理提交烦恼（关闭输入窗，打开结果窗）
const handleTreeholeSubmit = () => {
  treeholeResultRef.value?.open()
}

// 前端过滤（分类 + 只看我的）
const filteredCards = computed(() => {
  let filtered = cards.value
  if (filterType.value !== 'all') {
    filtered = filtered.filter((card) => card.type === filterType.value)
  }
  if (showOnlyMine.value && currentUserId.value) {
    filtered = filtered.filter((card) => card.owner.uid === currentUserId.value)
  }
  return filtered
})

// 获取卡片列表（支持分页）
const fetchCards = async (reset = true) => {
  if (loading.value) return
  loading.value = true
  error.value = false
  try {
    const params: GetPlazaCardsParams = {
      tab: currentTab.value,
      limit: 10,
    }
    if (!reset && nextCursor.value) {
      params.cursor = nextCursor.value
    }
    const res = await getPlazaCards(params)
    if (reset) {
      cards.value = res.list
    } else {
      cards.value.push(...res.list)
    }
    nextCursor.value = res.nextCursor
    hasMore.value = res.hasMore
  } catch (err) {
    console.error('获取广场卡片失败', err)
    error.value = true
    if (reset) cards.value = []
    hasMore.value = false
  } finally {
    loading.value = false
  }
}

// 重置并获取（切换筛选条件时调用）
const resetAndFetch = () => {
  nextCursor.value = null
  hasMore.value = true
  error.value = false
  fetchCards(true)
}

// 监听筛选变化
watch([filterType, showOnlyMine], () => {
  resetAndFetch()
})

// 加载更多
const loadMore = () => {
  if (!hasMore.value || loading.value || error.value) return
  fetchCards(false)
}

// 点赞/取消点赞
const handleLike = async (cardId: string, isLiked: boolean) => {
  const action = isLiked ? 'like' : 'unlike'
  try {
    const res = await likePlazaCard(cardId, action)
    const card = cards.value.find((c) => c.cardId === cardId)
    if (card) {
      card.stats.likes = res.likes
      card.stats.isLiked = res.isLiked
    }
  } catch (err) {
    console.error('点赞操作失败', err)
  }
}

// 删除卡片
const handleDeleteCard = async (cardId: string) => {
  try {
    await deletePlazaCard(cardId)
    // 从本地列表移除
    cards.value = cards.value.filter((c) => c.cardId !== cardId)
  } catch (err) {
    console.error('删除失败', err)
    alert('删除失败，请重试')
  }
}

onMounted(() => {
  fetchCards(true)
})
</script>
