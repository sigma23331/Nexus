// src/api/user.ts
import request from '@/utils/request'
import type { UserInfo } from '@/types/models'

// ========== 类型定义 ==========
export interface UserProfileResponse {
  userInfo: UserInfo
  stats?: {
    diaryCount: number
    answerCollected: number
    plazaPostCount: number
  }
}

export interface UpdateAvatarResponse {
  avatar: string
}

export interface UpdateNicknameResponse {
  nickname: string
}

export interface UpdatePasswordResponse {
  success: boolean
}

export interface UpdateLocationPayload {
  latitude: number
  longitude: number
  locationAccuracy?: number
}

// ========== API 函数 ==========

/**
 * 获取个人中心概览
 * GET /v1/user/profile
 */
export const getUserProfile = (): Promise<UserProfileResponse> => {
  return request.get('/v1/user/profile')
}

/**
 * 通用更新用户资料（头像/昵称等）
 * PUT /v1/user/profile
 * @param data 可包含 nickname, avatar
 */
export const updateUserProfile = (data: Partial<UserInfo>): Promise<void> => {
  return request.put('/v1/user/profile', data)
}

/**
 * 更新用户地理位置
 * PUT /v1/user/profile
 */
export const updateUserLocation = (data: UpdateLocationPayload): Promise<void> => {
  return request.put('/v1/user/profile', data)
}

/**
 * 修改头像
 * PUT /v1/user/profile/avatar
 * @param avatar 头像 URL 或 base64 字符串
 */
export const updateAvatar = (avatar: string): Promise<UpdateAvatarResponse> => {
  return request.put('/v1/user/profile/avatar', { avatar })
}

/**
 * 修改昵称
 * PUT /v1/user/profile/nickname
 * @param nickname 新昵称（1-20字符）
 */
export const updateNickname = (nickname: string): Promise<UpdateNicknameResponse> => {
  return request.put('/v1/user/profile/nickname', { nickname })
}

/**
 * 修改密码（无需旧密码，直接设置新密码）
 * PUT /v1/user/profile/password
 * @param newPassword 新密码（6-20位）
 */
export const updatePassword = (newPassword: string): Promise<UpdatePasswordResponse> => {
  return request.put('/v1/user/profile/password', { new_password: newPassword })
}
