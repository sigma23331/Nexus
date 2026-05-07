<template>
  <div class="min-h-screen bg-white text-slate-900 px-6 pt-6 pb-20">
    <div class="flex justify-center mb-4">
      <img src="/images/login_top2.png" alt="心运岛" class="w-1024 h-auto" />
    </div>
    <header class="flex flex-col items-center gap-2 pb-6">
      <h1 class="text-2xl font-bold">注册账号</h1>
      <p class="text-sm text-slate-500">加入心运岛，发现更多可能</p>
    </header>

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

      <!-- 验证码 -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">验证码</label>
        <div class="flex gap-3">
          <input
            v-model="code"
            type="text"
            maxlength="6"
            placeholder="请输入6位验证码"
            class="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
            :class="{ 'border-red-500': codeError }"
          />
          <button
            @click="handleSendCode"
            :disabled="countdown > 0 || !isPhoneValid"
            class="px-4 py-3 rounded-xl bg-purple-600 text-white text-sm font-medium whitespace-nowrap transition disabled:opacity-50"
          >
            {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
          </button>
        </div>
        <p v-if="codeError" class="text-xs text-red-500 mt-1">{{ codeError }}</p>
      </div>

      <!-- 设置密码（带自定义显示/隐藏图标） -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">设置密码</label>
        <div class="relative">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="6-20位字符"
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

      <!-- 协议勾选 -->
      <div class="flex items-start gap-2">
        <input
          v-model="agreeProtocol"
          type="checkbox"
          id="protocol"
          class="mt-1 w-4 h-4 text-purple-600 rounded"
        />
        <label for="protocol" class="text-sm text-slate-600 leading-tight">
          我已阅读并同意
          <a href="#" class="text-purple-600 hover:underline" @click.prevent="openUserAgreement"
            >《用户协议》</a
          >
          及
          <a href="#" class="text-purple-600 hover:underline" @click.prevent="openPrivacyPolicy"
            >《隐私政策》</a
          >
        </label>
      </div>
      <p v-if="protocolError" class="text-xs text-red-500 -mt-2">{{ protocolError }}</p>

      <!-- 注册按钮 -->
      <button
        @click="handleRegister"
        :disabled="!isFormValid || registerLoading"
        class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-medium py-3 rounded-xl transition disabled:opacity-50 shadow-sm"
      >
        {{ registerLoading ? '注册中...' : '注册' }}
      </button>

      <!-- 跳转登录 -->
      <div class="text-center text-sm">
        <span class="text-slate-500">已有账号？</span>
        <router-link to="/login" class="text-purple-600 font-medium ml-1">立即登录</router-link>
      </div>
    </div>

    <!-- 协议弹窗 -->
    <UserAgreementModal ref="userAgreementModalRef" />
    <PrivacyPolicyModal ref="privacyPolicyModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { sendSmsCode, register } from '@/api/auth'
import UserAgreementModal from '@/components/common/UserAgreementModal.vue'
import PrivacyPolicyModal from '@/components/common/PrivacyPolicyModal.vue'

const router = useRouter()

const userAgreementModalRef = ref<InstanceType<typeof UserAgreementModal> | null>(null)
const privacyPolicyModalRef = ref<InstanceType<typeof PrivacyPolicyModal> | null>(null)

const openUserAgreement = () => userAgreementModalRef.value?.open()
const openPrivacyPolicy = () => privacyPolicyModalRef.value?.open()

// 表单数据
const phone = ref('')
const code = ref('')
const password = ref('')
const agreeProtocol = ref(false)
const registerLoading = ref(false)
const showPassword = ref(false) // 控制密码显示/隐藏

// 倒计时
const countdown = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

// 校验
const isPhoneValid = computed(() => /^1[3-9]\d{9}$/.test(phone.value))
const phoneError = computed(() => {
  if (!phone.value) return ''
  if (!isPhoneValid.value) return '请输入正确的11位手机号'
  return ''
})
const codeError = computed(() => {
  if (!code.value) return ''
  if (!/^\d{6}$/.test(code.value)) return '验证码应为6位数字'
  return ''
})
const passwordError = computed(() => {
  if (!password.value) return ''
  if (password.value.length < 6 || password.value.length > 20) return '密码长度6-20位'
  return ''
})
const protocolError = computed(() => {
  if (!agreeProtocol.value) return '请阅读并同意协议'
  return ''
})
const isFormValid = computed(() => {
  return (
    isPhoneValid.value &&
    /^\d{6}$/.test(code.value) &&
    password.value.length >= 6 &&
    agreeProtocol.value
  )
})

// 发送验证码
const handleSendCode = async () => {
  if (!isPhoneValid.value) return
  if (countdown.value > 0) return
  try {
    await sendSmsCode(phone.value)
    countdown.value = 60
    if (timer) clearInterval(timer)
    timer = setInterval(() => {
      if (countdown.value > 0) countdown.value--
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

// 注册
const handleRegister = async () => {
  if (!isFormValid.value) return
  registerLoading.value = true
  try {
    await register(phone.value, code.value, password.value)
    alert('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    const message = err instanceof Error ? err.message : '注册失败，请重试'
    alert(message)
  } finally {
    registerLoading.value = false
  }
}

// 清理定时器
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
/* 隐藏浏览器原生密码显示/隐藏按钮（仅作用于本页面的密码输入框） */
.register-password-input input[type='password']::-ms-reveal,
.register-password-input input[type='password']::-ms-clear {
  display: none;
}
.register-password-input input[type='password']::-webkit-credentials-auto-fill-button,
.register-password-input input[type='password']::-webkit-textfield-decoration-container,
.register-password-input input[type='password']::-webkit-inner-spin-button,
.register-password-input input[type='password']::-webkit-outer-spin-button,
.register-password-input input[type='password']::-webkit-search-cancel-button,
.register-password-input input[type='password']::-webkit-search-decoration {
  display: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
}
.register-password-input input[type='password'] {
  -webkit-appearance: textfield;
  appearance: textfield;
}
</style>
