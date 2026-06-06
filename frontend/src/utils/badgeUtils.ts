// src/utils/badgeUtils.ts
// 根据 BADGE_CATALOG 提取 code -> sort_order 映射（与后端保持一致）
export const BADGE_SORT_MAP: Record<string, number> = {
  first_fortune: 1,
  diary_writer: 2,
  answer_traveler: 3,
  lucky_streak: 4,
  login_streak: 5,
  share_station: 6,
  favorite_collector: 7,
  social_master: 8,
  fortune_companion: 9,
}

/**
 * 获取正确的徽章图标 URL
 * @param badgeCode 徽章 code，如 'first_fortune'
 * @param isGray 是否为灰色（未解锁）版本
 * @returns 正确的图片路径
 */
export function getBadgeIconUrl(badgeCode: string, isGray = false): string {
  const sortOrder = BADGE_SORT_MAP[badgeCode]
  if (!sortOrder) {
    // fallback: 使用原始路径（基本不会发生）
    return isGray ? `/images/badges/${badgeCode}_gray.png` : `/images/badges/${badgeCode}.png`
  }
  const padded = sortOrder.toString().padStart(2, '0')
  const suffix = isGray ? '_gray.png' : '.png'
  return `/images/badges/badges_${padded}${suffix}`
}
