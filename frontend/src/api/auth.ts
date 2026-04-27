// src/api/auth.ts
import request from '@/utils/request'

// 发送短信验证码
export const sendSmsCode = (phone: string) => {
  return request.post('/auth/sms/send', { phone })
}

// 手机号验证码登录/注册
export const loginBySms = (phone: string, code: string) => {
  return request.post('/auth/sms/login', { phone, code })
}

// 手机号密码登录
export const loginByPassword = (username: string, password: string) => {
  return request.post('/auth/password/login', { username, password })
}

// 注册（手机号 + 验证码 + 密码）
export const register = (phone: string, code: string, password: string) => {
  return request.post('/auth/register', { phone, code, password })
}
