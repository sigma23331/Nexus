import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AnswerFavoriteItem, AnswerHistoryItem, AnswerResponse } from '@/types/models'

export const useAnswerStore = defineStore('answer', () => {
  const currentAnswer = ref<AnswerResponse | null>(null)
  const historyList = ref<AnswerHistoryItem[]>([])
  const historyTotal = ref(0)
  const favoriteList = ref<AnswerFavoriteItem[]>([])
  const favoriteTotal = ref(0)

  function setCurrentAnswer(answer: AnswerResponse) {
    currentAnswer.value = answer
  }

  function setHistoryList(list: AnswerHistoryItem[], total: number) {
    historyList.value = list
    historyTotal.value = total
  }

  function appendHistoryItem(item: AnswerHistoryItem) {
    historyList.value.unshift(item)
    historyTotal.value += 1
  }

  /** 分页追加（历史列表页「加载更多」） */
  function appendHistoryItems(items: AnswerHistoryItem[]) {
    historyList.value = [...historyList.value, ...items]
  }

  function setFavoriteList(list: AnswerFavoriteItem[], total: number) {
    favoriteList.value = list
    favoriteTotal.value = total
  }

  function toggleFavorite(answerId: string, isFavorited: boolean) {
    if (currentAnswer.value && currentAnswer.value.id === answerId) {
      currentAnswer.value.isFavorited = isFavorited
    }
  }

  function clearAnswers() {
    currentAnswer.value = null
    historyList.value = []
    historyTotal.value = 0
    favoriteList.value = []
    favoriteTotal.value = 0
  }

  return {
    currentAnswer,
    historyList,
    historyTotal,
    favoriteList,
    favoriteTotal,
    setCurrentAnswer,
    setHistoryList,
    appendHistoryItem,
    appendHistoryItems,
    setFavoriteList,
    toggleFavorite,
    clearAnswers,
  }
})
