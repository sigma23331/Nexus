// src/api/fortune.ts
import request from '@/utils/request'

// 今日运势响应类型
export interface FortuneToday {
  id: string
  date: string // YYYY-MM-DD
  score: number
  title: string
  content_main: string
  content_sub: string
  yi: string[]
  ji: string[]
  love: string
  career: string
  health: string
  wealth: string
}

// 运势轨迹点
export interface TrendPoint {
  date: string // MM-dd 格式
  value: number
}

// 历史运势记录项（来自 /user/history/fortune）
export interface HistoryFortuneItem {
  date: string // YYYY-MM-DD
  score: number
  title: string
}

// 今日运势
export const getFortuneToday = (): Promise<FortuneToday> => {
  return request.get('/v1/fortune/today')
}

// 运势轨迹（最近7天）
export const getFortuneTrend = (): Promise<{ trendPoints: TrendPoint[] }> => {
  return request.get('/v1/fortune/trend')
}

// 历史运势记录（分页，默认 limit=7 取最近7天）
export const getHistoryFortune = (
  page = 1,
  limit = 7,
): Promise<{
  total: number
  page: number
  limit: number
  list: HistoryFortuneItem[]
}> => {
  return request.get('/v1/user/history/fortune', { params: { page, limit } })
}
