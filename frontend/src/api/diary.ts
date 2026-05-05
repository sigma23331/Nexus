// src/api/diary.ts
import request from '@/utils/request'
import type { DiaryEntryDetail, DiaryTimelinePage } from '@/types/models'

export interface DiaryTimelineParams {
  page?: number
  limit?: number
  yearMonth?: string | null // YYYY-MM
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

export const createDiaryEntry = (data: {
  moodTag: string
  content: string
  isPublic?: boolean
}): Promise<{ id: string; createdAt: string }> => {
  return request.post('/v1/diary/entry', data)
}

export const updateDiaryEntry = (
  id: string,
  data: { moodTag?: string; content?: string; isPublic?: boolean },
): Promise<DiaryEntryDetail> => {
  return request.put(`/v1/diary/entry/${id}`, data)
}

export const deleteDiaryEntry = (id: string): Promise<{ success: boolean }> => {
  return request.delete(`/v1/diary/entry/${id}`)
}
