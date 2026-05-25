const TURNSTILE_SCRIPT_ID = 'cloudflare-turnstile-script'
const TURNSTILE_SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'

type TurnstileWidgetId = string

type TurnstileRenderOptions = {
  sitekey: string
  execution?: 'render' | 'execute'
  appearance?: 'always' | 'execute' | 'interaction-only'
  theme?: 'auto' | 'light' | 'dark'
  size?: 'normal' | 'flexible' | 'compact'
  callback: (token: string) => void
  'error-callback'?: (errorCode?: string) => void
  'expired-callback'?: () => void
  'timeout-callback'?: () => void
  'response-field'?: boolean
}

type TurnstileApi = {
  render: (container: HTMLElement | string, options: TurnstileRenderOptions) => TurnstileWidgetId
  execute: (widgetId: TurnstileWidgetId | HTMLElement | string) => void
  reset: (widgetId: TurnstileWidgetId) => void
  remove: (widgetId: TurnstileWidgetId) => void
}

declare global {
  interface Window {
    turnstile?: TurnstileApi
  }
}

let turnstileScriptPromise: Promise<void> | null = null

const loadTurnstileScript = () => {
  if (window.turnstile) return Promise.resolve()
  if (turnstileScriptPromise) return turnstileScriptPromise

  turnstileScriptPromise = new Promise<void>((resolve, reject) => {
    const existingScript = document.getElementById(TURNSTILE_SCRIPT_ID) as HTMLScriptElement | null
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener('error', () => reject(new Error('人机验证脚本加载失败')), {
        once: true,
      })
      return
    }

    const script = document.createElement('script')
    script.id = TURNSTILE_SCRIPT_ID
    script.src = TURNSTILE_SCRIPT_SRC
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('人机验证脚本加载失败'))
    document.head.appendChild(script)
  })

  return turnstileScriptPromise
}

const createTurnstileError = (errorCode?: string) => {
  if (!errorCode) return new Error('人机验证失败，请重试')
  return new Error(`人机验证失败，请重试（错误码：${errorCode}）`)
}

export const executeTurnstile = async (siteKey: string, container: HTMLElement | null) => {
  if (!siteKey) throw new Error('人机验证配置缺失，请联系管理员')
  if (!container) throw new Error('人机验证容器未初始化，请刷新后重试')

  await loadTurnstileScript()

  if (!window.turnstile) {
    throw new Error('人机验证脚本不可用，请稍后重试')
  }

  return new Promise<string>((resolve, reject) => {
    let widgetId: TurnstileWidgetId | null = null
    let settled = false

    const cleanup = () => {
      if (widgetId) {
        window.turnstile?.remove(widgetId)
      }
      container.innerHTML = ''
    }

    const finish = (callback: () => void) => {
      if (settled) return
      settled = true
      cleanup()
      callback()
    }

    try {
      widgetId = window.turnstile.render(container, {
        sitekey: siteKey,
        execution: 'execute',
        appearance: 'interaction-only',
        'response-field': false,
        callback: (token) => {
          finish(() => resolve(token))
        },
        'error-callback': (errorCode) => {
          console.warn('Turnstile error', errorCode)
          finish(() => reject(createTurnstileError(errorCode)))
        },
        'expired-callback': () => {
          finish(() => reject(new Error('人机验证已过期，请重试')))
        },
        'timeout-callback': () => {
          finish(() => reject(new Error('人机验证超时，请重试')))
        },
      })
      window.turnstile.execute(widgetId)
    } catch (error) {
      finish(() => reject(error instanceof Error ? error : new Error('人机验证失败，请重试')))
    }
  })
}

type VisibleTurnstileCallbacks = {
  onVerified: (token: string) => void
  onError?: (errorCode?: string) => void
  onExpired?: () => void
  onTimeout?: () => void
}

export type VisibleTurnstileWidget = {
  reset: () => void
  remove: () => void
}

export const renderVisibleTurnstile = async (
  siteKey: string,
  container: HTMLElement | null,
  callbacks: VisibleTurnstileCallbacks,
): Promise<VisibleTurnstileWidget> => {
  if (!siteKey) throw new Error('人机验证配置缺失，请联系管理员')
  if (!container) throw new Error('人机验证容器未初始化，请刷新后重试')

  await loadTurnstileScript()

  if (!window.turnstile) {
    throw new Error('人机验证脚本不可用，请稍后重试')
  }

  container.innerHTML = ''
  const widgetId = window.turnstile.render(container, {
    sitekey: siteKey,
    appearance: 'always',
    theme: 'auto',
    size: 'normal',
    'response-field': false,
    callback: callbacks.onVerified,
    'error-callback': callbacks.onError,
    'expired-callback': callbacks.onExpired,
    'timeout-callback': callbacks.onTimeout,
  })

  return {
    reset: () => window.turnstile?.reset(widgetId),
    remove: () => {
      window.turnstile?.remove(widgetId)
      container.innerHTML = ''
    },
  }
}
