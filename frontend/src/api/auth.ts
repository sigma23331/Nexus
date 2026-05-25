import request from '@/utils/request'
import type { LoginResponse } from '@/types/api'

// 发送验证码（携带 Cloudflare Turnstile token）
export const sendSmsCode = (phone: string, turnstileToken: string): Promise<void> => {
  return request.post('/v1/auth/sms/send', { phone, turnstileToken })
}

export const loginBySms = (phone: string, code: string): Promise<LoginResponse> => {
  return request.post('/v1/auth/sms/login', { phone, code })
}

export const loginByPassword = (phone: string, password: string): Promise<LoginResponse> => {
  return request.post('/v1/auth/password/login', { phone, password })
}

export const register = (phone: string, code: string, password: string): Promise<LoginResponse> => {
  return request.post('/v1/auth/register', { phone, code, password })
}
