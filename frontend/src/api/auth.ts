import request from '@/utils/request'
import type { LoginResponse } from '@/types/api'

export const sendSmsCode = (phone: string): Promise<void> => {
  return request.post('/v1/auth/sms/send', { phone })
}

export const loginBySms = (phone: string, code: string): Promise<LoginResponse> => {
  return request.post('/v1/auth/sms/login', { phone, code })
}

export const loginByPassword = (phone: string, password: string): Promise<LoginResponse> => {
  return request.post('/v1/auth/password/login', { phone, password })
}

// 修正：register 接口实际返回与 login 相同的结构（包含 token, userInfo, isNewUser）
export const register = (phone: string, code: string, password: string): Promise<LoginResponse> => {
  return request.post('/v1/auth/register', { phone, code, password })
}
