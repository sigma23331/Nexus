// src/api/answer.ts
import request from '@/utils/request'

// ========== 类型定义 ==========
export interface AnswerHistoryItem {
  id: string
  question: string
  answerText: string
  createdAt: string
  isFavorited?: boolean
}

/** 传统分页响应结构 */
export interface AnswerHistoryPage {
  total: number
  page: number
  limit: number
  list: AnswerHistoryItem[]
}

/** 提交提问响应 */
export interface AskResponse {
  id: string
  question: string
  answerText: string
  createdAt: string
}

/** 收藏/取消收藏响应 */
export interface FavoriteResponse {
  answerId: string
  isFavorited: boolean
}

// ========== API 函数 ==========

/**
 * 提交提问并抽取答案
 * POST /v1/answer/ask
 * @param question 问题内容（1-200字符）
 */
export const askQuestion = (question: string): Promise<AskResponse> => {
  return request.post('/v1/answer/ask', { question })
}

/**
 * 获取历史提问记录（分页）
 * GET /v1/answer/history
 * @param page 页码，默认 1
 * @param limit 每页数量，默认 10，最大 50
 */
export const getAnswerHistory = (page = 1, limit = 10): Promise<AnswerHistoryPage> => {
  return request.get('/v1/answer/history', { params: { page, limit } })
}

/**
 * 收藏或取消收藏答案
 * POST /v1/answer/favorite
 * @param answerId 答案记录ID
 * @param action favorite | unfavorite
 */
export const favoriteAnswer = (
  answerId: string,
  action: 'favorite' | 'unfavorite',
): Promise<FavoriteResponse> => {
  return request.post('/v1/answer/favorite', { answerId, action })
}

/**
 * 获取收藏的答案列表
 * GET /v1/user/history/favorites （属于用户模块，但为了统一放在 answer.ts 或 user.ts 均可）
 * @param page 页码，默认 1
 * @param limit 每页数量，默认 10
 */
export const getFavoriteAnswers = (page = 1, limit = 10): Promise<AnswerHistoryPage> => {
  return request.get('/v1/user/history/favorites', { params: { page, limit } })
}
