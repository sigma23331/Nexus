<template>
  <div
    v-if="visible"
    class="change-password-modal fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
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
            autocomplete="off"
            autocapitalize="none"
            spellcheck="false"
            @keyup.enter="confirm"
          />
          <button
            type="button"
            @click="showNewPassword = !showNewPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-600 transition"
          >
            <svg
              v-if="showNewPassword"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-5 h-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-5 h-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.864-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65"
              />
              <circle cx="12" cy="12" r="3" />
            </svg>
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
            autocomplete="off"
            autocapitalize="none"
            spellcheck="false"
            @keyup.enter="confirm"
          />
          <button
            type="button"
            @click="showConfirmPassword = !showConfirmPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-600 transition"
          >
            <svg
              v-if="showConfirmPassword"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-5 h-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-5 h-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.864-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65"
              />
              <circle cx="12" cy="12" r="3" />
            </svg>
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
const newPasswordInput = ref<HTMLInputElement | null>(null)

const open = (): Promise<boolean> => {
  visible.value = true
  newPassword.value = ''
  confirmPassword.value = ''
  errorMsg.value = ''
  loading.value = false
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

<style scoped>
/* 隐藏浏览器原生的密码显示/隐藏按钮 */
.change-password-modal input[type='password']::-ms-reveal,
.change-password-modal input[type='password']::-ms-clear {
  display: none;
}

.change-password-modal input[type='password']::-webkit-credentials-auto-fill-button,
.change-password-modal input[type='password']::-webkit-textfield-decoration-container,
.change-password-modal input[type='password']::-webkit-inner-spin-button,
.change-password-modal input[type='password']::-webkit-outer-spin-button,
.change-password-modal input[type='password']::-webkit-search-cancel-button,
.change-password-modal input[type='password']::-webkit-search-decoration {
  display: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
}

.change-password-modal input[type='password'] {
  -webkit-appearance: textfield;
  appearance: textfield;
}

.change-password-modal input[type='password']::-ms-clear,
.change-password-modal input[type='password']::-ms-reveal {
  display: none;
}

.change-password-modal input[type='password']::-webkit-credentials-auto-fill-button {
  opacity: 0;
  pointer-events: none;
}
</style>
