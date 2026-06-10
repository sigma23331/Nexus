// 会话守卫：登录满固定时长后自动退出登录，避免 token 在使用中悄然过期。
// 时长须小于后端 JWT 有效期（backend/config.py JWT_ACCESS_TOKEN_EXPIRES = 7 天）。

const ISSUED_AT_KEY = 'token_issued_at'

/** 会话最长保留时间：6 天（< 后端 7 天），到期强制重新登录 */
export const SESSION_MAX_AGE_MS = 6 * 24 * 60 * 60 * 1000

/** 周期检查间隔 */
const CHECK_INTERVAL_MS = 60 * 1000

/** 登录成功时调用：记录会话起始时间 */
export function markSessionStart(): void {
  localStorage.setItem(ISSUED_AT_KEY, String(Date.now()))
}

/** 登出时调用：清除会话起始时间 */
export function clearSessionStart(): void {
  localStorage.removeItem(ISSUED_AT_KEY)
}

function isSessionExpired(): boolean {
  if (!localStorage.getItem('token')) return false
  const issuedAt = Number(localStorage.getItem(ISSUED_AT_KEY))
  if (!issuedAt) {
    // 本次改动上线前已登录的旧会话没有时间戳：从现在开始计时，避免立即误登出
    markSessionStart()
    return false
  }
  return Date.now() - issuedAt > SESSION_MAX_AGE_MS
}

let timer: ReturnType<typeof setInterval> | null = null
let visibilityHandler: (() => void) | null = null

/**
 * 启动会话守卫（在 main.ts 调用一次）。
 * 立即检查一次，之后每分钟检查；PWA/页面从后台切回前台时也立即检查，
 * 保证长时间挂后台后一回到应用就能跳转登录页，而不是等到下一次定时器。
 */
export function startSessionGuard(onExpire: () => void): void {
  const check = () => {
    if (isSessionExpired()) onExpire()
  }

  check()

  if (timer) clearInterval(timer)
  timer = setInterval(check, CHECK_INTERVAL_MS)

  visibilityHandler = () => {
    if (!document.hidden) check()
  }
  document.addEventListener('visibilitychange', visibilityHandler)
}

export function stopSessionGuard(): void {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  if (visibilityHandler) {
    document.removeEventListener('visibilitychange', visibilityHandler)
    visibilityHandler = null
  }
}
