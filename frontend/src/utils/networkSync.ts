// src/utils/networkSync.ts
import { getUnsyncedDiaries, markSynced } from './diaryService'
import { createDiaryEntry } from '@/api/diary'

let syncTimer: ReturnType<typeof setTimeout> | null = null

async function syncAllPending() {
  const unsynced = getUnsyncedDiaries()
  if (unsynced.length === 0) return
  console.log(`发现 ${unsynced.length} 条未同步日记，开始同步...`)
  for (const diary of unsynced) {
    try {
      const res = await createDiaryEntry({
        moodTag: diary.moodTag,
        content: diary.content,
        isPublic: false,
      })
      markSynced(diary.id, res.id)
      console.log(`日记 ${diary.id} 同步成功，服务器 ID: ${res.id}`)
    } catch (err) {
      console.error(`日记 ${diary.id} 同步失败:`, err)
    }
  }
}

export function startNetworkSync() {
  // 初始同步（如果在线）
  if (navigator.onLine) {
    syncAllPending()
  }
  // 监听网络恢复
  window.addEventListener('online', () => {
    console.log('网络已恢复，开始同步日记')
    syncAllPending()
  })
  // 可选：每5分钟重试一次
  if (syncTimer) clearInterval(syncTimer)
  syncTimer = setInterval(
    () => {
      if (navigator.onLine) {
        syncAllPending()
      }
    },
    5 * 60 * 1000,
  )
}

export function stopNetworkSync() {
  if (syncTimer) {
    clearInterval(syncTimer)
    syncTimer = null
  }
  window.removeEventListener('online', syncAllPending)
}
