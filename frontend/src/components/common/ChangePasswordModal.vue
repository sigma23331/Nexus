<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="close"
  >
    <div class="bg-white rounded-2xl w-full max-w-sm mx-4 p-6 shadow-xl">
      <h3 class="text-lg font-bold text-slate-800 mb-2">修改密码</h3>
      <p class="text-sm text-slate-500 mb-4">请设置新密码（6-20位）</p>

      <!-- 新密码输入框 -->
      <div class="mb-4">
        <label class="block text-xs font-medium text-slate-600 mb-1">新密码</label>
        <div class="relative">
          <input
            ref="newPasswordInput"
            v-model="newPassword"
            :type="showNewPassword ? 'text' : 'password'"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400 pr-10"
            placeholder="请输入新密码"
            @keyup.enter="confirm"
          />
          <button
            type="button"
            @click="showNewPassword = !showNewPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-600 transition"
          >
            {{ showNewPassword ? '🙈' : '👁️' }}
          </button>
        </div>
      </div>

      <!-- 确认密码输入框 -->
      <div class="mb-6">
        <label class="block text-xs font-medium text-slate-600 mb-1">确认密码</label>
        <div class="relative">
          <input
            v-model="confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400 pr-10"
            placeholder="请再次输入新密码"
            @keyup.enter="confirm"
          />
          <button
            type="button"
            @click="showConfirmPassword = !showConfirmPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-600 transition"
          >
            {{ showConfirmPassword ? '🙈' : '👁️' }}
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <p v-if="errorMsg" class="text-xs text-rose-600 mb-4">{{ errorMsg }}</p>

      <div class="flex gap-3">
        <button
          @click="close"
          class="flex-1 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition"
        >
          取消
        </button>
        <button
          @click="confirm"
          :disabled="loading"
          class="flex-1 py-2 rounded-xl bg-purple-600 text-white hover:bg-purple-700 transition disabled:opacity-50"
        >
          {{ loading ? '修改中...' : '确定' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { updatePassword } from '@/api/user'

const visible = ref(false)
const newPassword = ref('')
const confirmPassword = ref('')
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const errorMsg = ref('')
const loading = ref(false)

let resolvePromise: ((success: boolean) => void) | null = null
let newPasswordInput = ref<HTMLInputElement | null>(null)

const open = (): Promise<boolean> => {
  visible.value = true
  newPassword.value = ''
  confirmPassword.value = ''
  errorMsg.value = ''
  loading.value = false
  // 自动聚焦新密码输入框
  nextTick(() => newPasswordInput.value?.focus())
  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

const close = () => {
  visible.value = false
  if (resolvePromise) resolvePromise(false)
  resolvePromise = null
}

const confirm = async () => {
  errorMsg.value = ''

  // 校验
  if (!newPassword.value) {
    errorMsg.value = '请输入新密码'
    return
  }
  if (newPassword.value.length < 6 || newPassword.value.length > 20) {
    errorMsg.value = '密码长度需为6-20位'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  try {
    await updatePassword(newPassword.value)
    // 成功后关闭弹窗并返回 true
    visible.value = false
    if (resolvePromise) resolvePromise(true)
    resolvePromise = null
    alert('密码修改成功，下次登录请使用新密码')
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '密码修改失败，请重试'
    errorMsg.value = message
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>
