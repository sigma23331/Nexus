import request from '@/utils/request'
import type { LoginResponse } from '@/types/api'

export interface SliderCaptchaChallenge {
  challengeToken: string
  targetX: number
  sliderWidth: number
  handleSize: number
  expiresIn: number
}

export interface SliderCaptchaVerifyResult {
  captchaToken: string
  expiresIn: number
}

export interface SliderCaptchaTrackPoint {
  x: number
  y: number
  t: number
}

export const createSliderCaptchaChallenge = (phone: string): Promise<SliderCaptchaChallenge> => {
  return request.post('/v1/auth/captcha/slider/challenge', { phone })
}

export const verifySliderCaptcha = (
  phone: string,
  challengeToken: string,
  offsetX: number,
  durationMs: number,
  track: SliderCaptchaTrackPoint[],
): Promise<SliderCaptchaVerifyResult> => {
  return request.post('/v1/auth/captcha/slider/verify', {
    phone,
    challengeToken,
    offsetX,
    durationMs,
    track,
  })
}

// 发送验证码（携带滑块验证 token）
export const sendSmsCode = (phone: string, captchaToken: string): Promise<void> => {
  return request.post('/v1/auth/sms/send', { phone, captchaToken })
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
