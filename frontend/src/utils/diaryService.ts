// src/utils/diaryService.ts
import { createDiaryEntry, getDiaryTimeline } from '@/api/diary'
import type { MoodTag } from './storage'

export interface LocalDiary {
  id: string // 本地唯一ID（格式 local_时间戳_随机数）
  date: string // YYYY-MM-DD
  moodTag: MoodTag
  content: string
  synced: boolean // 是否已同步到服务器
  serverId?: string // 服务端返回的ID
  createdAt: string // ISO 字符串
}

const STORAGE_KEY = 'xyd_diaries'

// 读取所有本地日记
function getLocalDiaries(): LocalDiary[] {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw)
  } catch {
    return []
  }
}

// 保存本地日记（全量覆盖）
function saveLocalDiaries(diaries: LocalDiary[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(diaries))
}

// 添加或更新本地日记（合并）
export function upsertLocalDiary(diary: LocalDiary) {
  const diaries = getLocalDiaries()
  const index = diaries.findIndex((d) => d.id === diary.id)
  if (index >= 0) {
    diaries[index] = diary
  } else {
    diaries.push(diary)
  }
  saveLocalDiaries(diaries)
}

// 获取某个月份的所有本地日记
export function getLocalDiariesByMonth(year: number, month: number): LocalDiary[] {
  const prefix = `${year}-${String(month).padStart(2, '0')}-`
  return getLocalDiaries().filter((d) => d.date.startsWith(prefix))
}

// 标记本地日记为已同步
export function markSynced(localId: string, serverId: string) {
  const diaries = getLocalDiaries()
  const diary = diaries.find((d) => d.id === localId)
  if (diary && !diary.synced) {
    diary.synced = true
    diary.serverId = serverId
    saveLocalDiaries(diaries)
  }
}

// 获取所有未同步的日记
export function getUnsyncedDiaries(): LocalDiary[] {
  return getLocalDiaries().filter((d) => !d.synced)
}

// 删除本地日记
export function deleteLocalDiary(id: string) {
  const diaries = getLocalDiaries().filter((d) => d.id !== id)
  saveLocalDiaries(diaries)
}

// 保存日记（离线优先）
export async function saveDiaryOfflineFirst(entry: {
  date: string
  moodTag: MoodTag
  content: string
}): Promise<{ localId: string; synced: boolean }> {
  const localId = `local_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`
  const localEntry: LocalDiary = {
    id: localId,
    date: entry.date,
    moodTag: entry.moodTag,
    content: entry.content,
    synced: false,
    createdAt: new Date().toISOString(),
  }
  // 1. 先存本地
  upsertLocalDiary(localEntry)
  // 2. 尝试同步到服务器（非阻塞）
  if (navigator.onLine) {
    try {
      const res = await createDiaryEntry({
        moodTag: entry.moodTag,
        content: entry.content,
        isPublic: false,
      })
      markSynced(localId, res.id)
      return { localId, synced: true }
    } catch (err) {
      console.warn('同步日记到服务器失败，已保存到本地', err)
      return { localId, synced: false }
    }
  } else {
    return { localId, synced: false }
  }
}

// 加载某月日记（先返回本地数据，再异步拉取远程并合并）
export async function loadMonthDiaries(year: number, month: number): Promise<LocalDiary[]> {
  // 1. 立即返回本地数据
  const localEntries = getLocalDiariesByMonth(year, month)
  // 2. 异步拉取远程数据并合并（不阻塞UI）
  setTimeout(async () => {
    try {
      const yearMonth = `${year}-${String(month).padStart(2, '0')}`
      const res = await getDiaryTimeline({ yearMonth, limit: 31 })
      const remoteList = res.list || []
      // 将远程数据同步到本地（如果本地没有则添加）
      for (const remote of remoteList) {
        const existingLocal = localEntries.find((l) => l.date === remote.date)
        if (!existingLocal) {
          // 远程有而本地没有，创建本地记录（标记为已同步）
          const newLocal: LocalDiary = {
            id: `remote_${remote.id}`,
            date: remote.date,
            moodTag: remote.moodTag as MoodTag,
            content: remote.snippet, // 摘要作为内容占位，完整内容需点击详情时再获取
            synced: true,
            serverId: remote.id,
            createdAt: new Date(remote.date).toISOString(),
          }
          upsertLocalDiary(newLocal)
        } else if (existingLocal.synced === false) {
          // 本地有未同步的日记，且远程已有同一天数据（冲突），保留本地未同步的，不覆盖
          // 这里不做处理，保留本地记录
        } else if (existingLocal.synced === true && existingLocal.serverId !== remote.id) {
          // 远程ID与本地不同，以后端为准更新本地内容
          existingLocal.content = remote.snippet
          existingLocal.moodTag = remote.moodTag as MoodTag
          existingLocal.serverId = remote.id
          upsertLocalDiary(existingLocal)
        }
      }
      // 通知视图更新（通过事件或刷新组件，这里简单触发一个自定义事件）
      window.dispatchEvent(new CustomEvent('diaries-updated', { detail: { year, month } }))
    } catch (err) {
      console.error('拉取远程日记失败', err)
    }
  }, 0)
  return localEntries
}
