import { ref } from 'vue'
import { createFortunePK, getFortunePK } from '@/api/fortune'

export function useFortunePK() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 创建挑战
  const createChallenge = async () => {
    loading.value = true
    error.value = null
    try {
      const res = await createFortunePK()
      return res
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : '创建挑战失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取或参与挑战
  const fetchOrJoinPK = async (token: string) => {
    loading.value = true
    error.value = null
    try {
      const pkRecord = await getFortunePK(token)
      return pkRecord
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : '获取挑战信息失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 生成分享链接
  const getShareLink = (token: string) => {
    let baseUrl = import.meta.env.VITE_BASE_URL || window.location.origin

    // 强制使用 https（除了 localhost 开发环境）
    if (
      baseUrl.startsWith('http://') &&
      !baseUrl.includes('localhost') &&
      !baseUrl.includes('127.0.0.1')
    ) {
      baseUrl = baseUrl.replace('http://', 'https://')
    }

    const cleanBase = baseUrl.replace(/\/$/, '')
    return `${cleanBase}/fortune/pk/${token}`
  }

  // 分享挑战（使用 Web Share API 或复制链接）
  const shareChallenge = async (token: string, challengerName: string) => {
    const link = getShareLink(token)
    const shareData = {
      title: '心运岛 · 运势挑战',
      text: `${challengerName} 向你发起运势挑战！点击链接一较高下～`,
      url: link,
    }

    // 优先使用原生分享
    if (navigator.share) {
      try {
        await navigator.share(shareData)
        return true
      } catch {
        // 用户取消分享或失败，不做额外提示
        return false
      }
    }

    // 降级：尝试复制链接
    try {
      // 现代 clipboard API
      await navigator.clipboard.writeText(link)
      alert('挑战链接已复制，快去分享给好友吧！')
      return true
    } catch {
      // 传统降级方案（兼容旧浏览器）
      try {
        const textarea = document.createElement('textarea')
        textarea.value = link
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        textarea.style.left = '-9999px'
        document.body.appendChild(textarea)
        textarea.select()
        const success = document.execCommand('copy')
        document.body.removeChild(textarea)
        if (success) {
          alert('挑战链接已复制，快去分享给好友吧！')
          return true
        } else {
          alert('复制失败，请手动复制链接：' + link)
          return false
        }
      } catch {
        alert('复制失败，请手动复制链接：' + link)
        return false
      }
    }
  }

  return {
    loading,
    error,
    createChallenge,
    fetchOrJoinPK,
    getShareLink,
    shareChallenge,
  }
}
