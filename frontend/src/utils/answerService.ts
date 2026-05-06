// src/utils/answerService.ts
import { getAnswerHistory, type AnswerHistoryItem } from '@/api/answer'

export interface LocalAnswer extends AnswerHistoryItem {
  synced: boolean // 始终为 true，因为只缓存已同步的记录
}

const STORAGE_KEY = 'xyd_answers'

// 读取本地所有答案
function getLocalAnswers(): LocalAnswer[] {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw)
  } catch {
    return []
  }
}

// 保存全部答案
function saveLocalAnswers(answers: LocalAnswer[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(answers))
}

// 将远程答案转换为本地格式
function toLocalAnswer(item: AnswerHistoryItem): LocalAnswer {
  return {
    ...item,
    synced: true,
  }
}

// 合并远程答案到本地（去重，按 id）
function mergeRemoteAnswers(remoteList: AnswerHistoryItem[]) {
  const local = getLocalAnswers()
  const idSet = new Set(local.map((a) => a.id))
  const newItems = remoteList.filter((r) => !idSet.has(r.id)).map(toLocalAnswer)
  if (newItems.length === 0) return
  const merged = [...newItems, ...local]
  merged.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  saveLocalAnswers(merged)
}

// 添加单条答案到本地（用于新提问成功后）
export function addLocalAnswer(answer: AnswerHistoryItem) {
  const local = getLocalAnswers()
  const localAnswer = toLocalAnswer(answer)
  // 避免重复
  if (local.some((a) => a.id === localAnswer.id)) return
  local.unshift(localAnswer) // 最新放在前面
  saveLocalAnswers(local)
}

// 获取本地答案列表（按时间倒序）
export function getLocalAnswerList(): LocalAnswer[] {
  return getLocalAnswers()
}

// 分页从远程拉取并合并到本地，同时返回当前页的数据
export async function fetchAndSyncHistory(
  page: number,
  limit: number,
): Promise<{
  list: AnswerHistoryItem[]
  total: number
  page: number
  limit: number
}> {
  const res = await getAnswerHistory(page, limit)
  mergeRemoteAnswers(res.list)
  return res
}
