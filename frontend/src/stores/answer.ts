import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { AnswerResponse, AnswerHistoryItem, AnswerFavoriteItem } from '@/types/models'

export const useAnswerStore = defineStore('answer', () => {
  // State
  const currentAnswer = ref<AnswerResponse | null>(null)
  const historyList = ref<AnswerHistoryItem[]>([])
  const historyTotal = ref(0)
  const favoriteList = ref<AnswerFavoriteItem[]>([])
  const favoriteTotal = ref(0)

  // Actions
  function setCurrentAnswer(answer: AnswerResponse) {
    currentAnswer.value = answer
  }

  function setHistoryList(list: AnswerHistoryItem[], total: number) {
    historyList.value = list
    historyTotal.value = total
  }

  function appendHistoryItem(item: AnswerHistoryItem) {
    historyList.value.unshift(item)
    historyTotal.value++
  }

  function setFavoriteList(list: AnswerFavoriteItem[], total: number) {
    favoriteList.value = list
    favoriteTotal.value = total
  }

  function toggleFavorite(answerId: string, isFavorited: boolean) {
    // 更新当前答案的收藏状态
    if (currentAnswer.value && currentAnswer.value.id === answerId) {
      currentAnswer.value.isFavorited = isFavorited
    }
    // 可选：同步更新历史列表和收藏列表中的状态
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
    setFavoriteList,
    toggleFavorite,
    clearAnswers,
  }
})
