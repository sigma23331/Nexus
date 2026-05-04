import request from '@/utils/request'
import type { DiaryEntryDetail, DiaryTimelinePage } from '@/types/models'

export interface DiaryTimelineParams {
  page?: number
  limit?: number
  /** 可选，YYYY-MM */
  yearMonth?: string | null
}

export const getDiaryTimeline = (params: DiaryTimelineParams = {}): Promise<DiaryTimelinePage> => {
  const { page = 1, limit = 20, yearMonth } = params
  return request.get('/v1/diary/timeline', {
    params: {
      page,
      limit,
      ...(yearMonth ? { yearMonth } : {}),
    },
  })
}

export const getDiaryEntry = (id: string): Promise<DiaryEntryDetail> => {
  return request.get(`/v1/diary/entry/${encodeURIComponent(id)}`)
}
