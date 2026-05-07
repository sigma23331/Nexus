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

      <!-- 密码登录（带自定义显示/隐藏图标） -->
      <div v-if="loginMode === 'password'">
        <label class="block text-sm font-medium text-slate-700 mb-1">密码</label>
        <div class="relative login-password-input">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400 pr-10"
            :class="{ 'border-red-500': passwordError }"
            autocomplete="off"
            autocapitalize="none"
            spellcheck="false"
          />
          <button
            type="button"
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-purple-600 transition"
          >
            <svg
              v-if="showPassword"
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
import { getUserProfile } from '@/api/user'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 登录模式
const loginMode = ref<'sms' | 'password'>('sms')
const phone = ref('')
const smsCode = ref('')
const password = ref('')
const loginLoading = ref(false)
const showPassword = ref(false) // 控制密码显示/隐藏

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
    let response
    if (loginMode.value === 'sms') {
      response = await loginBySms(phone.value, smsCode.value)
    } else {
      response = await loginByPassword(phone.value, password.value)
    }
    const loginData = 'data' in response ? response.data : response
    userStore.setToken(loginData.token)
    const profile = await getUserProfile()
    userStore.setUserInfo(profile.userInfo)
    const redirectPath = (route.query.redirect as string) || '/'
    router.replace(redirectPath)
  } catch (err) {
    const message = err instanceof Error ? err.message : '登录失败'
    alert(message)
  } finally {
    loginLoading.value = false
  }
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
/* 隐藏浏览器原生密码显示/隐藏按钮（仅作用于本页面的密码输入框） */
.login-password-input input[type='password']::-ms-reveal,
.login-password-input input[type='password']::-ms-clear {
  display: none;
}
.login-password-input input[type='password']::-webkit-credentials-auto-fill-button,
.login-password-input input[type='password']::-webkit-textfield-decoration-container,
.login-password-input input[type='password']::-webkit-inner-spin-button,
.login-password-input input[type='password']::-webkit-outer-spin-button,
.login-password-input input[type='password']::-webkit-search-cancel-button,
.login-password-input input[type='password']::-webkit-search-decoration {
  display: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
}
.login-password-input input[type='password'] {
  -webkit-appearance: textfield;
  appearance: textfield;
}
</style>
