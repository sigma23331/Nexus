import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/models'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

  // Actions
  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  function setUserInfo(info: UserInfo | null) {
    userInfo.value = info
  }

  // 登录成功后调用
  function loginSuccess(token: string, user: UserInfo) {
    setToken(token)
    setUserInfo(user)
  }

  // 登出
  function logout() {
    setToken(null)
    setUserInfo(null)
    // 可选：清空其他 store 的敏感数据
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    setToken,
    setUserInfo,
    loginSuccess,
    logout,
  }
})
