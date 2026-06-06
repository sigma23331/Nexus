// src/api/badge.ts
import request from '@/utils/request'

// 徽章定义中的等级信息
export interface BadgeLevel {
  level: number
  title: string
  threshold: number
  description: string
  conditionType?: string
  metricKey?: string
}

// 徽章定义（公开）
export interface BadgeDefinition {
  code: string
  name: string
  category: string
  description: string
  iconUrl: string
  grayIconUrl: string
  sortOrder: number
  levels: BadgeLevel[]
}

// 用户徽章状态
export interface UserBadge {
  code: string
  name: string
  category: string
  level: number
  maxLevel: number
  title: string | null
  nextTitle: string | null
  progress: number
  target: number
  unlocked: boolean
  unlockedAt: string | null
  iconUrl: string
  grayIconUrl: string
  levels: BadgeLevel[]
}

// 已佩戴徽章
export interface EquippedBadge {
  code: string
  name: string
  category: string
  level: number
  maxLevel: number
  title: string | null
  iconUrl: string
  grayIconUrl: string
  slotOrder: number
}

// 用户徽章列表响应
export interface MyBadgesResponse {
  unlockedCount: number
  totalCount: number
  list: UserBadge[]
}

// 已佩戴徽章响应
export interface EquippedBadgesResponse {
  maxEquipped: number
  list: EquippedBadge[]
}

// 徽章变化通知
export interface BadgeChange {
  id: string
  badgeCode: string
  badgeName: string
  category: string | null
  level: number
  title: string | null
  changeType: 'unlock' | 'upgrade'
  iconUrl: string | null
  grayIconUrl: string | null
  createdAt: string
}

export interface BadgeChangesResponse {
  total: number
  list: BadgeChange[]
}

export const getBadgeDefinitions = () =>
  request.get<{ list: BadgeDefinition[] }>('/v1/badge/definitions')

export const getMyBadges = () => request.get<MyBadgesResponse>('/v1/badge/my')

export const getEquippedBadges = () => request.get<EquippedBadgesResponse>('/v1/badge/equipped')

export const updateEquippedBadges = (badgeCodes: string[]) =>
  request.put<EquippedBadgesResponse>('/v1/badge/equipped', { badgeCodes })

export const getBadgeChanges = () => request.get<BadgeChangesResponse>('/v1/badge/changes')

export const markBadgeChangesRead = (changeIds?: string[]) =>
  request.post<{ updated: number }>('/v1/badge/changes/read', { changeIds })
