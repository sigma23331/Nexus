// src/api/plaza.ts
import request from '@/utils/request'
import type { PlazaCard, PlazaComment, PlazaCommentsResponse } from '@/types/models'

export interface PlazaCardsResponse {
  list: PlazaCard[]
  nextCursor: string | null
  hasMore: boolean
}

export interface GetPlazaCardsParams {
  tab?: 'hot' | 'latest'
  cursor?: string | null
  limit?: number
}

export interface CreatePlazaCardParams {
  type: 'fortune' | 'answer'
  sourceId: string // 运势日期(yyyy-mm-dd) 或 答案ID
  snapshotUrl: string // 卡片图片URL（可为空字符串，前端降级显示文本卡片）
  content?: string // 可选，1-100字符
  tags?: string[] // 可选，最多3个，每个1-10字符
}

export const getPlazaCards = (params: GetPlazaCardsParams = {}): Promise<PlazaCardsResponse> => {
  const { tab = 'latest', cursor = null, limit = 10 } = params
  return request.get('/v1/plaza/cards', {
    params: {
      tab,
      ...(cursor && { cursor }),
      limit,
    },
  })
}

export const likePlazaCard = (
  cardId: string,
  action: 'like' | 'unlike',
): Promise<{ cardId: string; likes: number; isLiked: boolean }> => {
  return request.post('/v1/plaza/like', { cardId, action })
}

export const createPlazaCard = (params: CreatePlazaCardParams): Promise<PlazaCard> => {
  return request.post('/v1/plaza/card', params)
}

export const deletePlazaCard = (cardId: string): Promise<{ success: boolean }> => {
  return request.delete(`/v1/plaza/card/${encodeURIComponent(cardId)}`)
}

export interface GetPlazaCommentsParams {
  cursor?: string | null
  limit?: number
}

export const getPlazaComments = (
  cardId: string,
  params: GetPlazaCommentsParams = {},
): Promise<PlazaCommentsResponse> => {
  const { cursor = null, limit = 20 } = params
  return request.get(`/v1/plaza/cards/${encodeURIComponent(cardId)}/comments`, {
    params: {
      limit,
      ...(cursor && { cursor }),
    },
  })
}

export const createPlazaComment = (
  cardId: string,
  payload: { content: string; parentId?: string },
): Promise<PlazaComment> => {
  return request.post(`/v1/plaza/cards/${encodeURIComponent(cardId)}/comments`, payload)
}

export const deletePlazaComment = (commentId: string): Promise<{ success: boolean }> => {
  return request.delete(`/v1/plaza/comments/${encodeURIComponent(commentId)}`)
}

export const getPlazaCommentReplies = (
  commentId: string,
  params: GetPlazaCommentsParams = {},
): Promise<PlazaCommentsResponse> => {
  const { cursor = null, limit = 20 } = params
  return request.get(`/v1/plaza/comments/${encodeURIComponent(commentId)}/replies`, {
    params: {
      limit,
      ...(cursor && { cursor }),
    },
  })
}
