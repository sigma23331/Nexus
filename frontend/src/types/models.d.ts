// 用户信息
export interface UserInfo {
  uid: string
  nickname: string
  avatar: string
  phone?: string | null
  birthday?: string | null // YYYY-MM-DD
  gender?: 'male' | 'female' | 'secret' | null
  latitude?: number | null
  longitude?: number | null
  locationAccuracy?: number | null
  locationUpdatedAt?: string | null
}

// 情绪标签（与后端 MoodType 枚举对齐）
export type MoodType = 'happy' | 'calm' | 'sad' | 'angry' | 'tired'

// 今日运势
export interface FortuneToday {
  id: string
  date: string
  score: number
  title: string
  content_main: string
  content_sub: string
  yi: string[]
  ji: string[]
  love?: string
  career?: string
  health?: string
  wealth?: string
  gua_meaning_lines?: string[]
  lucky_hour_name?: string
  lucky_hour_range?: string
}

// 运势轨迹
export interface FortuneTrend {
  trendPoints: Array<{ date: string; value: number }>
}

// 全站统计
export interface FortuneGlobalStats {
  date: string
  averageScore: number
  topTitle: string
  topTitleRatio: number
  totalParticipants?: number
}

// 答案响应
export interface AnswerResponse {
  id: string
  question: string
  answerText: string
  createdAt: string
  isFavorited?: boolean
}

// 历史记录项
export interface AnswerHistoryItem {
  id: string
  question: string
  answerText: string
  createdAt: string
  isFavorited?: boolean
}

// 收藏项
export interface AnswerFavoriteItem {
  id: string
  question: string
  answerText: string
  createdAt: string
}

// 广场卡片
export interface PlazaCard {
  cardId: string
  type: 'fortune' | 'answer'
  owner: {
    uid: string
    nickname: string
    avatar: string
  }
  snapshotUrl: string
  content?: string
  stats: {
    likes: number
    comments: number
    isLiked: boolean
  }
  createdAt: string
}

export interface PlazaCommentOwner {
  uid: string
  nickname: string
  avatar: string
}

export interface PlazaComment {
  commentId: string
  cardId: string
  owner: PlazaCommentOwner
  content: string
  parentId: string | null
  replyToUser: PlazaCommentOwner | null
  status: string
  createdAt: string
  canDelete: boolean
  replyCount: number
  replies: PlazaComment[]
}

export interface PlazaCommentsResponse {
  list: PlazaComment[]
  nextCursor: string | null
  hasMore: boolean
}

// 日记时间轴项（来自 API）
export interface DiaryTimelineItem {
  id: string
  date: string
  weekday: string
  moodTag: MoodType
  snippet: string
  localOnly?: boolean // 标记是否仅为本地数据（无服务端ID）
}

// 日记时间轴分页
export interface DiaryTimelinePage {
  totalDays: number
  page: number
  limit: number
  list: DiaryTimelineItem[]
}

// 日记详情（用于单条查看）
export interface DiaryEntryDetail {
  id: string
  moodTag: MoodType
  content: string
  createdAt: string
}
