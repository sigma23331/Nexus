import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PlazaCard } from '@/types/models'

export const usePlazaStore = defineStore('plaza', () => {
  // State
  const cards = ref<PlazaCard[]>([])
  const nextCursor = ref<string | null>(null)
  const hasMore = ref(true)
  const currentTab = ref<'hot' | 'latest'>('latest')

  // Actions
  function setCards(newCards: PlazaCard[], cursor: string | null, more: boolean) {
    if (cursor === null) {
      // 首次加载或刷新，替换列表
      cards.value = newCards
    } else {
      // 追加分页
      cards.value.push(...newCards)
    }
    nextCursor.value = cursor
    hasMore.value = more
  }

  function likeCard(cardId: string, isLiked: boolean, newLikes: number) {
    const card = cards.value.find((c) => c.cardId === cardId)
    if (card) {
      card.stats.isLiked = isLiked
      card.stats.likes = newLikes
    }
  }

  function addCard(card: PlazaCard) {
    cards.value.unshift(card)
  }

  function clearCards() {
    cards.value = []
    nextCursor.value = null
    hasMore.value = true
  }

  function setCurrentTab(tab: 'hot' | 'latest') {
    currentTab.value = tab
    clearCards()
  }

  return {
    cards,
    nextCursor,
    hasMore,
    currentTab,
    setCards,
    likeCard,
    addCard,
    clearCards,
    setCurrentTab,
  }
})
