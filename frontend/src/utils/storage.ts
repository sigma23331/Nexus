// src/utils/storage.ts

// ==================== 通用存储封装 ====================

/**
 * 存储键名枚举（集中管理，避免冲突）
 */
export enum StorageKey {
  // 用户相关
  TOKEN = 'auth_token',
  USER_INFO = 'user_info',
  // 用户偏好
  FONT_PREF = 'diary_note_font_style',
  // 日记数据
  DIARIES = 'mood_diaries',
}

/**
 * 从 localStorage 读取数据（自动 JSON 解析）
 */
export function getItem<T>(key: string): T | null {
  const raw = localStorage.getItem(key)
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

/**
 * 写入 localStorage（自动 JSON 序列化）
 */
export function setItem<T>(key: string, value: T): void {
  localStorage.setItem(key, JSON.stringify(value))
}

/**
 * 删除指定存储项
 */
export function removeItem(key: string): void {
  localStorage.removeItem(key)
}

/**
 * 清空所有本应用存储（慎用）
 */
export function clearAll(): void {
  Object.values(StorageKey).forEach((key) => {
    localStorage.removeItem(key)
  })
}

// ==================== 日记存储业务接口 ====================

export type MoodTag = 'happy' | 'calm' | 'sad' | 'angry' | 'tired' | 'anxious'

export interface DiaryEntry {
  date: string // YYYY-MM-DD
  moodTag: MoodTag
  content: string
}

/**
 * 获取所有日记
 */
export function getAllDiaries(): DiaryEntry[] {
  return getItem<DiaryEntry[]>(StorageKey.DIARIES) || []
}

/**
 * 保存日记（同一天会覆盖）
 */
export function saveDiary(entry: DiaryEntry): void {
  const diaries = getAllDiaries()
  const index = diaries.findIndex((d) => d.date === entry.date)
  if (index !== -1) {
    diaries[index] = entry
  } else {
    diaries.push(entry)
  }
  setItem(StorageKey.DIARIES, diaries)
}

/**
 * 删除指定日期的日记
 */
export function deleteDiary(date: string): void {
  const diaries = getAllDiaries()
  const filtered = diaries.filter((d) => d.date !== date)
  setItem(StorageKey.DIARIES, filtered)
}

/**
 * 获取指定年月的日记（异步兼容原接口）
 */
export async function getDiariesByMonth(year: number, month: number): Promise<DiaryEntry[]> {
  const all = getAllDiaries()
  const prefix = `${year}-${month.toString().padStart(2, '0')}-`
  return all.filter((entry) => entry.date.startsWith(prefix))
}

/**
 * 获取某一天的日记
 */
export function getDiaryByDate(date: string): DiaryEntry | undefined {
  const all = getAllDiaries()
  return all.find((entry) => entry.date === date)
}

// ==================== 用户偏好存储（示例） ====================

/**
 * 保存用户字体偏好
 */
export function saveFontPreference(fontId: string): void {
  setItem(StorageKey.FONT_PREF, fontId)
}

/**
 * 获取用户字体偏好
 */
export function getFontPreference(): string | null {
  return getItem<string>(StorageKey.FONT_PREF)
}
