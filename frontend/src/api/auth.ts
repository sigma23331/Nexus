import request from '@/utils/request'
import type { LoginResponse } from '@/types/api'

export const sendSmsCode = (phone: string): Promise<void> => {
  return request.post('/auth/sms/send', { phone })
}

export const loginBySms = (phone: string, code: string): Promise<LoginResponse> => {
  return request.post('/auth/sms/login', { phone, code })
}

export const loginByPassword = (username: string, password: string): Promise<LoginResponse> => {
  return request.post('/auth/password/login', { username, password })
}

export const register = (phone: string, code: string, password: string): Promise<void> => {
  return request.post('/auth/register', { phone, code, password })
}
