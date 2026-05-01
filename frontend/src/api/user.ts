import request from '@/utils/request'
import type { UserInfo } from '@/types/models'

export interface UserProfileResponse {
  userInfo: UserInfo
  stats?: {
    diaryCount: number
    answerCollected: number
    plazaPostCount: number
  }
}

export const getUserProfile = (): Promise<UserProfileResponse> => {
  return request.get('/user/profile')
}

export const updateUserProfile = (data: Partial<UserInfo>): Promise<void> => {
  return request.put('/user/profile', data)
}
