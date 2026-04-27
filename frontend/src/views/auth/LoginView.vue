<template>
  <div class="min-h-screen bg-white text-slate-900 px-6 pt-6 pb-20">
    <div class="flex justify-center mb-4">
      <img src="/images/login_top2.png" alt="心运岛" class="w-1024 h-auto" />
    </div>
    <!-- 头部：欢迎语 + 模式切换按钮 -->
    <div class="flex justify-between items-center pb-6">
      <h1 class="text-2xl font-bold">欢迎回来</h1>
      <button
        @click="loginMode = loginMode === 'sms' ? 'password' : 'sms'"
        class="text-sm text-purple-600 font-medium"
      >
        {{ loginMode === 'sms' ? '密码登录' : '验证码登录' }}
      </button>
    </div>

    <div class="max-w-md mx-auto space-y-6">
      <!-- 手机号 -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">手机号</label>
        <input
          v-model="phone"
          type="tel"
          maxlength="11"
          placeholder="请输入11位手机号"
          class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400"
          :class="{ 'border-red-500': phoneError }"
        />
        <p v-if="phoneError" class="text-xs text-red-500 mt-1">{{ phoneError }}</p>
      </div>

      <!-- 验证码登录 -->
      <div v-if="loginMode === 'sms'">
        <label class="block text-sm font-medium text-slate-700 mb-1">验证码</label>
        <div class="flex gap-3">
          <input
            v-model="smsCode"
            type="text"
            maxlength="6"
            placeholder="请输入6位验证码"
            class="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
            :class="{ 'border-red-500': smsCodeError }"
          />
          <button
            @click="handleSendSmsCode"
            :disabled="smsCountdown > 0 || !isPhoneValid"
            class="px-4 py-3 rounded-xl bg-purple-600 text-white text-sm font-medium whitespace-nowrap transition disabled:opacity-50"
          >
            {{ smsCountdown > 0 ? `${smsCountdown}秒后重试` : '获取验证码' }}
          </button>
        </div>
        <p v-if="smsCodeError" class="text-xs text-red-500 mt-1">{{ smsCodeError }}</p>
      </div>

      <!-- 密码登录 -->
      <div v-if="loginMode === 'password'">
        <label class="block text-sm font-medium text-slate-700 mb-1">密码</label>
        <input
          v-model="password"
          type="password"
          placeholder="请输入密码"
          class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
          :class="{ 'border-red-500': passwordError }"
        />
        <p v-if="passwordError" class="text-xs text-red-500 mt-1">{{ passwordError }}</p>
      </div>

      <!-- 登录按钮 -->
      <button
        @click="handleLogin"
        :disabled="!isFormValid || loginLoading"
        class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-medium py-3 rounded-xl transition disabled:opacity-50 shadow-sm"
      >
        {{ loginLoading ? '登录中...' : '登录' }}
      </button>

      <!-- 跳转注册 -->
      <div class="text-center text-sm">
        <span class="text-slate-500">还没有账号？</span>
        <router-link to="/register" class="text-purple-600 font-medium ml-1">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { sendSmsCode, loginBySms, loginByPassword } from '@/api/auth'
import type { LoginResponse } from '@/types/api'

const router = useRouter()
const route = useRoute()

// 登录模式
const loginMode = ref<'sms' | 'password'>('sms')
const phone = ref('')
const smsCode = ref('')
const password = ref('')
const loginLoading = ref(false)

// 倒计时
const smsCountdown = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

// 校验
const isPhoneValid = computed(() => /^1[3-9]\d{9}$/.test(phone.value))
const phoneError = computed(() => {
  if (!phone.value) return ''
  if (!isPhoneValid.value) return '请输入正确的11位手机号'
  return ''
})
const smsCodeError = computed(() => {
  if (loginMode.value !== 'sms') return ''
  if (!smsCode.value) return ''
  if (!/^\d{6}$/.test(smsCode.value)) return '验证码应为6位数字'
  return ''
})
const passwordError = computed(() => {
  if (loginMode.value !== 'password') return ''
  if (!password.value) return ''
  if (password.value.length < 6) return '密码长度至少6位'
  return ''
})
const isFormValid = computed(() => {
  if (!isPhoneValid.value) return false
  if (loginMode.value === 'sms') {
    return /^\d{6}$/.test(smsCode.value)
  } else {
    return password.value.length >= 6
  }
})

// 发送验证码
const handleSendSmsCode = async () => {
  if (!isPhoneValid.value) return
  if (smsCountdown.value > 0) return
  try {
    await sendSmsCode(phone.value)
    smsCountdown.value = 60
    if (timer) clearInterval(timer)
    timer = setInterval(() => {
      if (smsCountdown.value > 0) smsCountdown.value--
      else {
        if (timer) clearInterval(timer)
        timer = null
      }
    }, 1000)
  } catch (err) {
    const message = err instanceof Error ? err.message : '验证码发送失败'
    alert(message)
  }
}

// 登录
const handleLogin = async () => {
  if (!isFormValid.value) return
  loginLoading.value = true
  try {
    let response: LoginResponse
    if (loginMode.value === 'sms') {
      response = (await loginBySms(phone.value, smsCode.value)) as unknown as LoginResponse
    } else {
      response = (await loginByPassword(phone.value, password.value)) as unknown as LoginResponse
    }
    localStorage.setItem('token', response.token)
    // 可选的 Pinia 存储
    // const userStore = useUserStore()
    // userStore.loginSuccess(response.token, response.userInfo)
    const redirectPath = (route.query.redirect as string) || '/'
    router.replace(redirectPath)
  } catch (err) {
    const message = err instanceof Error ? err.message : '登录失败，请检查手机号/验证码/密码'
    alert(message)
  } finally {
    loginLoading.value = false
  }
}

// 清理定时器
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
