<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl relative">
      <!-- 头部 -->
      <div class="relative px-6 py-4 border-b border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 text-center">
          {{ isFortune ? '分享运势到广场' : '分享答案到广场' }}
        </h3>
        <button
          @click="close"
          class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-2xl leading-none"
        >
          &times;
        </button>
      </div>

      <!-- 内容区域 -->
      <div class="px-6 py-4 space-y-5 max-h-[70vh] overflow-y-auto">
        <!-- 分享文案（可编辑） -->
        <div>
          <div class="text-xs text-slate-500 mb-1">分享文案（可选）</div>
          <textarea
            v-model="extraContent"
            rows="3"
            class="w-full border border-slate-200 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder="写下你想说的话，与大家分享...（最多100字）"
            maxlength="100"
          ></textarea>
          <div class="text-right text-xs text-slate-400 mt-1">{{ extraContent.length }}/100</div>
        </div>

        <!-- 原始内容预览（不可编辑）- 改用卡片样式 -->
        <div>
          <div class="text-xs text-slate-500 mb-1">预览效果</div>
          <!-- 运势卡片预览 -->
          <div
            v-if="isFortune"
            class="fortune-card rounded-xl border border-amber-200 bg-gradient-to-br from-amber-50 to-rose-50 p-4"
          >
            <div class="text-center">
              <p class="text-sm font-semibold text-amber-700">心运岛 · 今日签文</p>
            </div>
            <!-- 运势标题 + 分数（参考 TodayFortuneContent） -->
            <div class="flex justify-center mt-2">
              <div class="relative inline-block">
                <span
                  class="rounded-full px-4 py-1.5 text-[28px] font-semibold font-lxgw text-[#B45309] bg-amber-50"
                >
                  {{ fortunePreview.title }}
                </span>
                <span class="absolute -bottom-0 -right-6 text-xs text-slate-600 px-1 rounded">
                  {{ fortunePreview.score }} 分
                </span>
              </div>
            </div>

            <!-- 主签文 -->
            <div class="mt-4 text-center">
              <p class="text-lg font-bold text-slate-900">{{ fortunePreview.mainContent }}</p>
            </div>

            <!-- 副签文 -->
            <div class="mt-2 text-center text-xs text-slate-500">
              {{ fortunePreview.subContent }}
            </div>

            <!-- 爱情、事业、健康、财富四项 -->
            <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div
                class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
              >
                <span class="text-slate-500 w-7 flex-shrink-0">爱情</span>
                <span class="font-semibold text-pink-500 flex-1 break-words">{{
                  fortunePreview.love
                }}</span>
              </div>
              <div
                class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
              >
                <span class="text-slate-500 w-7 flex-shrink-0">事业</span>
                <span class="font-semibold text-blue-500 flex-1 break-words">{{
                  fortunePreview.career
                }}</span>
              </div>
              <div
                class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
              >
                <span class="text-slate-500 w-7 flex-shrink-0">健康</span>
                <span class="font-semibold text-green-600 flex-1 break-words">{{
                  fortunePreview.health
                }}</span>
              </div>
              <div
                class="rounded-xl border border-orange-200 bg-amber-50 px-3 py-2 flex justify-between items-start gap-2"
              >
                <span class="text-slate-500 w-7 flex-shrink-0">财富</span>
                <span class="font-semibold text-yellow-600 flex-1 break-words">{{
                  fortunePreview.wealth
                }}</span>
              </div>
            </div>

            <!-- 宜忌：左右两列，每个子项独立框，宽度自适应，左对齐 -->
            <div class="mt-4 grid grid-cols-2 gap-3">
              <!-- 左列：宜 -->
              <div class="flex flex-col items-start gap-1.5">
                <div
                  v-for="(item, idx) in fortunePreview.yiList"
                  :key="idx"
                  class="rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-700 w-fit"
                >
                  宜：{{ item }}
                </div>
                <div
                  v-if="!fortunePreview.yiList.length"
                  class="rounded-full bg-emerald-50 px-3 py-1 text-xs text-emerald-700 w-fit"
                >
                  宜：--
                </div>
              </div>
              <!-- 右列：忌 -->
              <div class="flex flex-col items-start gap-1.5">
                <div
                  v-for="(item, idx) in fortunePreview.jiList"
                  :key="idx"
                  class="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700 w-fit"
                >
                  忌：{{ item }}
                </div>
                <div
                  v-if="!fortunePreview.jiList.length"
                  class="rounded-full bg-rose-100 px-3 py-1 text-xs text-rose-700 w-fit"
                >
                  忌：--
                </div>
              </div>
            </div>

            <div class="mt-2 text-right text-[12px] text-amber-600/80">{{ previewDateText }}</div>
          </div>

          <!-- 答案卡片预览 -->
          <div
            v-else
            class="answer-card rounded-xl border border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 p-4"
          >
            <div class="text-center mb-3">
              <span class="text-2xl">✨</span>
              <p class="text-xs text-purple-700/80">心运岛 · 答案之书</p>
            </div>
            <div class="whitespace-pre-wrap text-sm text-slate-700">{{ answerPreviewContent }}</div>
            <div
              class="text-right text-[12px] text-purple-600/80 border-t border-purple-200/60 pt-2 mt-2"
            >
              {{ previewDateText }}
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="px-6 py-4 border-t border-slate-100 flex justify-end gap-3">
        <button
          @click="close"
          class="px-4 py-2 text-sm text-slate-600 border-2 border-slate-200 hover:bg-slate-300 rounded-lg transition"
        >
          取消
        </button>
        <button
          @click="confirmShare"
          :disabled="sharing"
          class="px-4 py-2 text-sm bg-indigo-400 text-white rounded-lg hover:bg-indigo-500 transition disabled:opacity-50"
        >
          {{ sharing ? '分享中...' : '分享' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Toast 提示 -->
  <div
    v-if="toastMessage"
    class="fixed bottom-20 left-4 right-4 bg-black/70 text-white text-sm text-center py-2 rounded-lg z-50"
  >
    {{ toastMessage }}
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { createPlazaCard } from '@/api/plaza'
import dayjs from 'dayjs'

const visible = ref(false)
const cardType = ref<'fortune' | 'answer'>('answer')
const sourceId = ref('')
const originalContent = ref('')
const extraContent = ref('')
const sharing = ref(false)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const isFortune = computed(() => cardType.value === 'fortune')
const previewDateText = computed(() => dayjs().format('YYYY-MM-DD'))

// 最终内容：用户文案 + 原始内容
const finalContent = computed(() => {
  if (extraContent.value.trim()) {
    return `✨ ${extraContent.value.trim()}\n\n${originalContent.value}`
  }
  return originalContent.value
})

// 解析运势预览数据（复用 PlazaCard 中的解析逻辑）
const getCleanedContent = (content: string) => {
  let start = 0
  // 如果内容以 ✨ 开头且有换行，则跳过第一行（分享文案）
  const match = content.match(/^✨\s*(.+?)(?=\n\n|$)/s)
  if (match && match[1]) {
    const idx = content.indexOf('\n\n')
    if (idx !== -1) start = idx + 2
  }
  return content.slice(start).trim()
}

const extractField = (content: string, fieldName: string): string => {
  const lines = content.split('\n')
  for (const line of lines) {
    if (line.startsWith(fieldName + '：') || line.startsWith(fieldName + ':')) {
      return line.replace(/^(爱情|事业|健康|财富)[：:]/, '').trim()
    }
  }
  return '--'
}

const splitYiJi = (str: string): string[] => {
  if (!str || str === '--') return []
  return str.split(/[、，, ]+/).filter((s) => s.trim().length > 0)
}

const fortunePreview = computed(() => {
  const cleaned = getCleanedContent(originalContent.value)
  const lines = cleaned.split('\n')
  const titleLine = lines[0] || ''
  const titleMatch = titleLine.match(/^(.+?)（(\d+)分）/)
  const title = titleMatch ? titleMatch[1] : titleLine.replace(/✨/, '').trim()
  const score = titleMatch ? titleMatch[2] : '0'
  const mainContent = lines[1] || ''
  const subContent = lines[2] || ''
  const yiLine = lines.find((l) => l.startsWith('宜：')) || ''
  const jiLine = lines.find((l) => l.startsWith('忌：')) || ''
  const yiText = yiLine.replace('宜：', '')
  const jiText = jiLine.replace('忌：', '')

  return {
    title,
    score,
    mainContent,
    subContent,
    love: extractField(cleaned, '爱情'),
    career: extractField(cleaned, '事业'),
    health: extractField(cleaned, '健康'),
    wealth: extractField(cleaned, '财富'),
    yiList: splitYiJi(yiText),
    jiList: splitYiJi(jiText),
  }
})

const answerPreviewContent = computed(() => {
  // 答案卡片：移除开头的分享文案（如果有）后显示
  let content = originalContent.value
  const match = content.match(/^✨\s*.+?\n\n/s)
  if (match) {
    content = content.slice(match[0].length)
  }
  return content.trim() || '✨ 暂无内容'
})

const showToast = (msg: string) => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = msg
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
    toastTimer = null
  }, 2000)
}

// 开放方法
const open = (params: {
  type: 'fortune' | 'answer'
  sourceId: string
  content?: string
  fortuneData?: {
    title: string
    score: number
    content_main: string
    content_sub: string
    yi: string[]
    ji: string[]
    love?: string
    career?: string
    health?: string
    wealth?: string
  }
}) => {
  cardType.value = params.type
  sourceId.value = params.sourceId
  if (params.type === 'fortune' && params.fortuneData) {
    const f = params.fortuneData
    // 格式化运势原始内容，用于预览和分享内容（一行一个元素）
    originalContent.value = [
      `${f.title}（${f.score}分）`,
      f.content_main,
      f.content_sub,
      `宜：${f.yi.join('、') || '--'}`,
      `忌：${f.ji.join('、') || '--'}`,
      `爱情：${f.love || '--'}`,
      `事业：${f.career || '--'}`,
      `健康：${f.health || '--'}`,
      `财富：${f.wealth || '--'}`,
    ].join('\n')
  } else if (params.content) {
    originalContent.value = params.content
  } else {
    originalContent.value = ''
  }
  extraContent.value = ''
  visible.value = true
}

const close = () => {
  visible.value = false
  extraContent.value = ''
}

const confirmShare = async () => {
  if (sharing.value) return
  if (!navigator.onLine) {
    showToast('网络不可用，请稍后重试')
    return
  }

  sharing.value = true
  try {
    const placeholderUrl = 'https://placehold.co/400x400/FEF7E0/8B5CF6?text=心运岛&font=montserrat'
    await createPlazaCard({
      type: cardType.value,
      sourceId: sourceId.value,
      snapshotUrl: placeholderUrl,
      content: finalContent.value,
      tags: [],
    })
    showToast('✨ 已分享到广场！')
    setTimeout(() => {
      close()
    }, 1500)
  } catch (err) {
    console.error('分享失败', err)
    showToast('分享失败，请重试')
  } finally {
    sharing.value = false
  }
}

defineExpose({ open })
</script>

<style scoped>
.font-lxgw {
  font-family: 'KaiTi', '楷体', cursive;
}

.fortune-card,
.answer-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>
