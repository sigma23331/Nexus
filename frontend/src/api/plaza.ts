// src/api/plaza.ts
import request from '@/utils/request'
import type { PlazaCard } from '@/types/models'

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
