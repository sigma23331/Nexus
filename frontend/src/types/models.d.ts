// 用户信息
export interface UserInfo {
  uid: string
  nickname: string
  avatar: string
  phone?: string | null
}

// 今日运势
export interface FortuneToday {
  id: string
  date: string
  // 今日签文
  score: number // 用于全站数据统计
  title: string // “上上签”
  content_main: string // "风起云开，顺遂自来"
  content_sub: string // "今日宜稳中求进，心静则通达"
  // 今日概览
  yi: string[]
  ji: string[]
  love?: string
  career?: string
  health?: string
  wealth?: string
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
    isLiked: boolean
  }
  tags?: string[]
  createdAt: string
}

/** GET /v1/diary/timeline 单条摘要 */
export interface DiaryTimelineItem {
  id: string
  date: string
  weekday: string
  moodTag: string
  snippet: string
  /** 来自本机 localStorage，无服务端 id 时详情走本地缓存 */
  localOnly?: boolean
}

/** GET /v1/diary/timeline 分页 */
export interface DiaryTimelinePage {
  totalDays: number
  page: number
  limit: number
  list: DiaryTimelineItem[]
}

/** GET /v1/diary/entry/:id */
export interface DiaryEntryDetail {
  id: string
  moodTag: string
  content: string
  createdAt: string | null
}
