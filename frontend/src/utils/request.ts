// src/utils/request.ts
import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types/api'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 默认使用代理 /api
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器：处理标准响应格式
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { code, message, data } = response.data

    // 成功
    if (code === 200) {
      return data
    }

    // token 失效或未登录
    if (code === 401) {
      // 清除本地 token
      localStorage.removeItem('token')
      // 如果不在登录页，跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(new Error(message || '请重新登录'))
    }

    // 其他业务错误
    return Promise.reject(new Error(message || '请求失败'))
  },
  (error) => {
    // 网络错误或超时
    let errorMsg = '网络错误，请稍后重试'
    if (error.code === 'ECONNABORTED') {
      errorMsg = '请求超时，请稍后重试'
    } else if (error.response) {
      // 服务器返回了错误状态码（如 500、404 等）
      errorMsg = error.response.data?.message || `请求失败: ${error.response.status}`
    }
    return Promise.reject(new Error(errorMsg))
  },
)

export default request
