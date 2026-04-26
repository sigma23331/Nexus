<template>
  <div class="min-h-screen bg-white text-slate-900 px-6 pt-6 pb-20">
    <header class="flex items-center gap-2 pb-6">
      <span class="text-2xl">🔐</span>
      <h1 class="text-2xl font-bold">登录</h1>
    </header>

    <div class="max-w-md mx-auto space-y-6">
      <!-- 手机号输入 -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">手机号</label>
        <input
          v-model="phone"
          type="tel"
          maxlength="11"
          placeholder="请输入11位手机号"
          class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400"
          :class="{ 'border-red-500 focus:ring-red-500/60': phoneError }"
        />
        <p v-if="phoneError" class="text-xs text-red-500 mt-1">{{ phoneError }}</p>
      </div>

      <!-- 验证码 + 获取按钮 -->
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">验证码</label>
        <div class="flex gap-3">
          <input
            v-model="code"
            type="text"
            maxlength="6"
            placeholder="请输入6位验证码"
            class="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60 focus:border-purple-400"
            :class="{ 'border-red-500 focus:ring-red-500/60': codeError }"
          />
          <button
            @click="sendCode"
            :disabled="countdown > 0 || !isPhoneValid"
            class="px-4 py-3 rounded-xl bg-purple-600 text-white text-sm font-medium whitespace-nowrap transition disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-700"
          >
            {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
          </button>
        </div>
        <p v-if="codeError" class="text-xs text-red-500 mt-1">{{ codeError }}</p>
      </div>

      <!-- 协议勾选 -->
      <div class="flex items-start gap-2">
        <input
          v-model="agreeProtocol"
          type="checkbox"
          id="protocol"
          class="mt-1 w-4 h-4 text-purple-600 border-slate-300 rounded focus:ring-purple-500"
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

      <!-- 登录按钮 -->
      <button
        @click="handleLogin"
        :disabled="!isFormValid || loginLoading"
        class="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-medium py-3 rounded-xl transition disabled:opacity-50 shadow-sm"
      >
        {{ loginLoading ? '登录中...' : '登录' }}
      </button>

      <!-- 开发提示（后续可移除） -->
      <div class="text-center text-xs text-slate-400 pt-4">
        测试手机号：13800138000<br />
        验证码：任意6位数字
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
import UserAgreementModal from '@/components/common/UserAgreementModal.vue'
import PrivacyPolicyModal from '@/components/common/PrivacyPolicyModal.vue'

const router = useRouter()

// 弹窗引用
const userAgreementModalRef = ref<InstanceType<typeof UserAgreementModal> | null>(null)
const privacyPolicyModalRef = ref<InstanceType<typeof PrivacyPolicyModal> | null>(null)

// 打开协议弹窗
const openUserAgreement = () => {
  userAgreementModalRef.value?.open()
}
const openPrivacyPolicy = () => {
  privacyPolicyModalRef.value?.open()
}

// 表单数据
const phone = ref('')
const code = ref('')
const agreeProtocol = ref(false)
const loginLoading = ref(false)

// 倒计时
const countdown = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

// 校验相关
const phoneError = computed(() => {
  if (!phone.value) return ''
  if (!/^1[3-9]\d{9}$/.test(phone.value)) return '请输入正确的11位手机号'
  return ''
})
const isPhoneValid = computed(() => /^1[3-9]\d{9}$/.test(phone.value))

const codeError = computed(() => {
  if (!code.value) return ''
  if (!/^\d{6}$/.test(code.value)) return '验证码应为6位数字'
  return ''
})

const protocolError = computed(() => {
  if (!agreeProtocol.value) return '请阅读并同意协议'
  return ''
})

const isFormValid = computed(() => {
  return isPhoneValid.value && /^\d{6}$/.test(code.value) && agreeProtocol.value
})

// 发送验证码（模拟）
const sendCode = () => {
  if (!isPhoneValid.value) return
  if (countdown.value > 0) return

  // 模拟发送请求
  console.log(`发送验证码到 ${phone.value}`)

  // 开始倒计时
  countdown.value = 60
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      if (timer) clearInterval(timer)
      timer = null
    }
  }, 1000)
}

// 登录处理
const handleLogin = async () => {
  if (!isFormValid.value) return

  loginLoading.value = true
  try {
    // TODO: 调用真实登录 API
    await new Promise((resolve) => setTimeout(resolve, 1000))

    if (!code.value) {
      alert('验证码不能为空')
      return
    }

    // 模拟登录成功，存储 token
    localStorage.setItem('token', 'mock-token')

    // 获取登录前想要访问的页面（如果有），否则跳转到首页
    const redirectPath = (router.currentRoute.value.query.redirect as string) || '/'
    router.replace(redirectPath)
  } catch (error) {
    console.error(error)
    alert('登录失败，请重试')
  } finally {
    loginLoading.value = false
  }
}

// 清理定时器
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>
