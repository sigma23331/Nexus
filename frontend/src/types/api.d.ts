// src/types/api.d.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 登录/注册响应数据类型
export interface LoginResponse {
  token: string
  userInfo: {
    uid: string
    nickname: string
    avatar: string
    birthday?: string | null
    gender?: 'male' | 'female' | 'secret' | null
  }
  isNewUser: boolean
}
