import request from '@/utils/request'
import type { AnswerHistoryItem } from '@/types/models'

/** 与 API.md 传统分页结构一致 */
export interface AnswerHistoryPage {
  total: number
  page: number
  limit: number
  list: AnswerHistoryItem[]
}

export const getAnswerHistory = (page = 1, limit = 10): Promise<AnswerHistoryPage> => {
  return request.get('/v1/answer/history', { params: { page, limit } })
}
