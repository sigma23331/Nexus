// src/composables/useShareCard.ts
import { ref } from 'vue'
import {
  drawFortuneShareCard,
  drawAnswerShareCard,
  downloadCanvasAsImage,
  type FortuneShareData,
  type AnswerShareData,
} from '@/utils/shareCardGenerator'

export function useShareCard() {
  const isGenerating = ref(false)

  const generateFortuneCard = async (data: FortuneShareData, filename?: string) => {
    if (isGenerating.value) return
    isGenerating.value = true
    try {
      const canvas = document.createElement('canvas')
      await drawFortuneShareCard(canvas, data)
      downloadCanvasAsImage(canvas, filename || `fortune_${Date.now()}.png`)
    } catch (err) {
      console.error('生成运势卡片失败', err)
      alert('生成失败，请重试')
    } finally {
      isGenerating.value = false
    }
  }

  const generateAnswerCard = async (data: AnswerShareData, filename?: string) => {
    if (isGenerating.value) return
    isGenerating.value = true
    try {
      const canvas = document.createElement('canvas')
      await drawAnswerShareCard(canvas, data)
      downloadCanvasAsImage(canvas, filename || `answer_${Date.now()}.png`)
    } catch (err) {
      console.error('生成答案卡片失败', err)
      alert('生成失败，请重试')
    } finally {
      isGenerating.value = false
    }
  }

  return {
    isGenerating,
    generateFortuneCard,
    generateAnswerCard,
  }
}
