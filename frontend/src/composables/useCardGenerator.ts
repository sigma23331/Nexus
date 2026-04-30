// src/composables/useCardGenerator.ts
import { ref } from 'vue'
import {
  drawFortuneCard,
  drawAnswerCard,
  downloadCard,
  type FortuneCardData,
  type AnswerCardData,
} from '@/utils/cardGenerator'

export function useCardGenerator() {
  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const isLoading = ref(false)

  const initCanvas = (canvasElement: HTMLCanvasElement, width = 1024, height = 1024) => {
    canvasRef.value = canvasElement
    canvasElement.width = width
    canvasElement.height = height
  }

  const generateFortuneAndDownload = async (data: FortuneCardData, filename?: string) => {
    if (!canvasRef.value) {
      console.error('Canvas 未初始化')
      return
    }
    isLoading.value = true
    try {
      await drawFortuneCard(canvasRef.value, data)
      downloadCard(canvasRef.value, filename || `fortune_${Date.now()}.png`)
    } catch (err) {
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  const generateAnswerAndDownload = async (data: AnswerCardData, filename?: string) => {
    if (!canvasRef.value) {
      console.error('Canvas 未初始化')
      return
    }
    isLoading.value = true
    try {
      await drawAnswerCard(canvasRef.value, data)
      downloadCard(canvasRef.value, filename || `answer_${Date.now()}.png`)
    } catch (err) {
      console.error(err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    canvasRef,
    isLoading,
    initCanvas,
    generateFortuneAndDownload,
    generateAnswerAndDownload,
  }
}
