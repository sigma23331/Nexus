import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/models'
import { getUserProfile } from '@/api/user' // 需要引入

// 辅助函数：从 localStorage 读取用户信息
function loadUserInfo(): UserInfo | null {
  const stored = localStorage.getItem('userInfo')
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch {
      return null
    }
  }
  return null
}

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(loadUserInfo())
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
    if (info) {
      localStorage.setItem('userInfo', JSON.stringify(info))
    } else {
      localStorage.removeItem('userInfo')
    }
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
  }

  // 新增：从后端获取最新用户信息并更新 store
  async function fetchUserInfo() {
    try {
      const res = await getUserProfile()
      setUserInfo(res.userInfo)
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    setToken,
    setUserInfo,
    loginSuccess,
    logout,
    fetchUserInfo,
  }
})
