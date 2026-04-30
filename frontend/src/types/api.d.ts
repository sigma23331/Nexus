// src/types/api.d.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 新增登录响应类型
export interface LoginResponse {
  token: string
  userInfo: {
    uid: string
    nickname: string
    avatar: string
  }
}
