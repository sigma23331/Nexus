<template>
  <div class="min-h-screen bg-slate-100 pb-8">
    <!-- 顶部导航栏 -->
    <div class="sticky top-0 z-10 bg-white border-b border-slate-200 px-4 py-3 flex items-center">
      <button
        @click="router.back()"
        class="p-1 rounded-full text-slate-600 hover:bg-slate-100 transition mr-3"
      >
        <IconChevronLeft />
      </button>
      <h1 class="text-lg font-semibold text-slate-800">帮助与反馈</h1>
    </div>

    <div class="px-4 py-6 space-y-6">
      <!-- 引导语卡片 -->
      <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-100">
        <div class="flex items-start gap-3">
          <svg
            class="h-8 w-8 text-indigo-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
          <div class="flex-1">
            <h3 class="font-semibold text-slate-800 mb-1">我们珍视您的每一条反馈</h3>
            <p class="text-sm text-slate-600 leading-relaxed">
              您在使用心运岛的过程中遇到任何问题、有任何建议或想法，都可以在这里告诉我们。
              我们会认真阅读每一条反馈，并努力优化产品体验。感谢您的支持！
            </p>
          </div>
        </div>
      </div>

      <!-- 反馈表单 -->
      <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-100">
        <h3 class="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <span class="text-lg">📝</span> 提交反馈
        </h3>

        <form @submit.prevent="submitFeedback" class="space-y-4">
          <!-- 反馈类型 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1"
              >反馈类型 <span class="text-red-400">*</span></label
            >
            <select
              v-model="form.type"
              class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
              required
            >
              <option value="bug">问题反馈（Bug）</option>
              <option value="suggestion">功能建议</option>
              <option value="other">其他</option>
            </select>
          </div>

          <!-- 问题描述 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1"
              >问题描述 <span class="text-red-400">*</span></label
            >
            <textarea
              v-model="form.content"
              rows="5"
              placeholder="请详细描述您遇到的问题或建议，例如：我在使用答案之书时，点击摇一摇没有反应……"
              class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 resize-none"
              required
            ></textarea>
            <p class="text-xs text-slate-400 mt-1">最多500字</p>
          </div>

          <!-- 联系方式（选填） -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">联系方式（选填）</label>
            <input
              v-model="form.contact"
              type="text"
              placeholder="QQ / 微信 / 邮箱，方便我们联系您"
              class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
            />
            <p class="text-xs text-slate-400 mt-1">仅用于我们跟进反馈，不会泄露给第三方</p>
          </div>

          <!-- 提交按钮 -->
          <button
            type="submit"
            :disabled="submitting"
            class="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2.5 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ submitting ? '提交中...' : '提交反馈' }}
          </button>
        </form>
      </div>

      <!-- 历史反馈入口（可选） -->
      <div class="text-center">
        <button
          @click="showHistory = !showHistory"
          class="text-sm text-purple-500 hover:text-purple-600 transition"
        >
          {{ showHistory ? '收起历史反馈' : '查看我提交过的反馈' }}
        </button>
      </div>

      <!-- 历史反馈列表 -->
      <div v-if="showHistory" class="bg-white rounded-xl p-5 shadow-sm border border-slate-100">
        <h3 class="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <span class="text-lg">📋</span> 我的反馈记录
        </h3>
        <div v-if="feedbackList.length === 0" class="text-center text-slate-400 py-6 text-sm">
          暂无反馈记录
        </div>
        <div v-else class="space-y-3 max-h-64 overflow-y-auto">
          <div
            v-for="(item, idx) in feedbackList"
            :key="idx"
            class="border-b border-slate-100 pb-3 last:border-0"
          >
            <div class="flex justify-between items-start mb-1">
              <span
                class="text-xs font-medium px-2 py-0.5 rounded-full"
                :class="typeBadgeClass(item.type)"
              >
                {{ typeLabel(item.type) }}
              </span>
              <span class="text-xs text-slate-400">{{ formatDate(item.time) }}</span>
            </div>
            <p class="text-sm text-slate-700 mt-1">{{ item.content }}</p>
            <p v-if="item.contact" class="text-xs text-slate-400 mt-1">
              联系方式：{{ item.contact }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 提交成功 Toast 提示 -->
    <div
      v-if="toastVisible"
      class="fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-slate-800 text-white px-4 py-2 rounded-full text-sm shadow-lg z-50 transition-opacity"
      :class="toastVisible ? 'opacity-100' : 'opacity-0'"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import IconChevronLeft from '@/components/icons/IconChevronLeft.vue'

interface FeedbackItem {
  id: string
  type: string
  content: string
  contact: string
  time: number
}

const router = useRouter()

// 表单数据
const form = reactive({
  type: 'bug',
  content: '',
  contact: '',
})

const submitting = ref(false)
const showHistory = ref(false)
const feedbackList = ref<FeedbackItem[]>([])

// Toast 提示
const toastVisible = ref(false)
const toastMessage = ref('')

const showToast = (msg: string) => {
  toastMessage.value = msg
  toastVisible.value = true
  setTimeout(() => {
    toastVisible.value = false
  }, 2000)
}

// 类型标签样式
const typeBadgeClass = (type: string) => {
  switch (type) {
    case 'bug':
      return 'bg-red-100 text-red-600'
    case 'suggestion':
      return 'bg-green-100 text-green-600'
    default:
      return 'bg-slate-100 text-slate-600'
  }
}

const typeLabel = (type: string) => {
  switch (type) {
    case 'bug':
      return '问题反馈'
    case 'suggestion':
      return '功能建议'
    default:
      return '其他'
  }
}

const formatDate = (timestamp: number) => {
  const date = new Date(timestamp)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 保存反馈到本地
const saveFeedbackToLocal = (feedback: FeedbackItem) => {
  const key = 'xinyundao_feedback_list'
  const existing = localStorage.getItem(key)
  let list: FeedbackItem[] = existing ? JSON.parse(existing) : []
  list.unshift(feedback) // 最新在最前
  // 只保留最近50条
  if (list.length > 50) list = list.slice(0, 50)
  localStorage.setItem(key, JSON.stringify(list))
  feedbackList.value = list
}

// 加载历史反馈
const loadFeedbackHistory = () => {
  const key = 'xinyundao_feedback_list'
  const existing = localStorage.getItem(key)
  if (existing) {
    feedbackList.value = JSON.parse(existing)
  }
}

// 提交反馈
const submitFeedback = async () => {
  if (!form.content.trim()) {
    showToast('请填写问题描述')
    return
  }
  if (form.content.length > 500) {
    showToast('问题描述不能超过500字')
    return
  }

  submitting.value = true

  // 模拟异步提交（实际可调用后端接口）
  await new Promise((resolve) => setTimeout(resolve, 500))

  const newFeedback: FeedbackItem = {
    id: Date.now().toString(),
    type: form.type,
    content: form.content.trim(),
    contact: form.contact.trim(),
    time: Date.now(),
  }

  saveFeedbackToLocal(newFeedback)

  // 清空表单
  form.content = ''
  form.contact = ''
  form.type = 'bug'

  submitting.value = false
  showToast('反馈提交成功，感谢您的支持！')

  // 如果历史记录是展开的，刷新列表
  if (showHistory.value) {
    loadFeedbackHistory()
  }
}

// 删除反馈（可选，简单实现一个长按删除？为了简洁，暂不加删除功能，可后续扩展）

onMounted(() => {
  loadFeedbackHistory()
})
</script>
