<template>
  <div class="min-h-screen bg-white text-slate-900 pb-20">
    <main class="px-6 py-4 space-y-8">
      <!-- 测试卡片生成区域（保持不变） -->
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

      <!-- 分享广场（带分类筛选） -->
      <section>
        <div class="flex items-center justify-between mb-3">
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
        </div>
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
            @like="handleLike"
          />
        </div>
        <div
          v-if="!error && hasMore && !loading && filteredCards.length > 0"
          class="text-center mt-4"
        >
          <button @click="loadMore" class="text-sm text-purple-600">加载更多</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import PlazaCard from './components/PlazaCard.vue'
import { getPlazaCards, likePlazaCard } from '@/api/plaza'
import type { PlazaCard as PlazaCardType } from '@/types/models'
import { useCardGenerator } from '@/composables/useCardGenerator'
import type { FortuneCardData, AnswerCardData } from '@/utils/cardGenerator'
import type { GetPlazaCardsParams } from '@/api/plaza'

const cards = ref<PlazaCardType[]>([])
const loading = ref(false)
const error = ref(false)
const hasMore = ref(true)
const nextCursor = ref<string | null>(null)
const filterType = ref<'all' | 'fortune' | 'answer'>('all')
const currentTab = ref<'hot' | 'latest'>('latest')

// 前端过滤卡片
const filteredCards = computed(() => {
  if (filterType.value === 'all') return cards.value
  return cards.value.filter((card) => card.type === filterType.value)
})

// 获取卡片数据（重置或追加）
const fetchCards = async (reset = true) => {
  if (loading.value) return
  loading.value = true
  error.value = false // 重置错误
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
    if (reset) {
      cards.value = [] // 清空旧数据，避免显示错误内容
    }
    hasMore.value = false
  } finally {
    loading.value = false
  }
}

// 切换分类时重置列表
const resetAndFetch = () => {
  nextCursor.value = null
  hasMore.value = true
  error.value = false
  fetchCards(true)
}

// 监听分类变化
watch(filterType, () => {
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

// 卡片生成器（测试区域）
const { isLoading, initCanvas, generateFortuneAndDownload, generateAnswerAndDownload } =
  useCardGenerator()
const cardCanvas = ref<HTMLCanvasElement | null>(null)
const testFortuneData: FortuneCardData = {
  text: '上上签·吉行',
  sub: '宜稳中求进，静待花开',
  stats: ['中上', '平稳', '注意作息', '谨慎消费'],
}
const testAnswerData: AnswerCardData = {
  answer: '允许一切发生，专注当下就好。',
}

onMounted(() => {
  if (cardCanvas.value) {
    initCanvas(cardCanvas.value, 1024, 1024)
  }
  fetchCards(true)
})

const testFortuneCard = () => generateFortuneAndDownload(testFortuneData, 'test_fortune.png')
const testAnswerCard = () => generateAnswerAndDownload(testAnswerData, 'test_answer.png')
</script>
