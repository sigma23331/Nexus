/**
 * 答案之书彩蛋：根据时间 / 天气 / 节气触发特殊回复与视觉主题。
 * 触发条件仅在本地判断，不上传服务端。
 */

export type AnswerEasterEggType = 'time' | 'weather' | 'solar_term'
export type AnswerEasterEggAnimation = 'midnight' | 'dawn' | 'rain' | 'snow' | 'solar' | 'festival'

export interface AnswerEasterEgg {
  id: string
  type: AnswerEasterEggType
  label: string
  answerText: string
  prefix: string
  animation: AnswerEasterEggAnimation
  badge: string
}

const WEATHER_CACHE_KEY = 'answer-easter-egg-weather-v1'
const WEATHER_CACHE_TTL_MS = 30 * 60 * 1000
const EGG_STATS_KEY = 'answer-easter-egg-stats-v1'

/** 节气 / 节日窗口（阳历近似，可逐年扩展） */
const SOLAR_WINDOWS: Array<{
  id: string
  label: string
  start: string
  end: string
  answerText: string
  prefix: string
  animation: AnswerEasterEggAnimation
  badge: string
}> = [
  {
    id: 'spring-equinox',
    label: '春分',
    start: '03-19',
    end: '03-21',
    prefix: '🌱 春分秘语：',
    answerText: '昼夜等长时，心也会慢慢找到平衡。',
    animation: 'solar',
    badge: '春分',
  },
  {
    id: 'summer-solstice',
    label: '夏至',
    start: '06-20',
    end: '06-22',
    prefix: '☀️ 夏至回响：',
    answerText: '阳气最盛，行动比犹豫更有力量。',
    animation: 'solar',
    badge: '夏至',
  },
  {
    id: 'duanwu',
    label: '端午',
    start: '06-16',
    end: '06-22',
    prefix: '🎋 端午彩蛋：',
    answerText: '粽叶飘香时，先稳住节奏，再出发。',
    animation: 'festival',
    badge: '端午',
  },
  {
    id: 'winter-solstice',
    label: '冬至',
    start: '12-20',
    end: '12-22',
    prefix: '❄️ 冬至低语：',
    answerText: '最长夜里，答案往往藏在耐心之后。',
    animation: 'solar',
    badge: '冬至',
  },
]

const TIME_EGGS: Array<{
  id: string
  label: string
  match: (hour: number) => boolean
  answerText: string
  prefix: string
  animation: AnswerEasterEggAnimation
  badge: string
}> = [
  {
    id: 'midnight',
    label: '子夜',
    match: (h) => h >= 0 && h < 1,
    prefix: '🌙 子夜秘语：',
    answerText: '夜深了，先睡一觉，明早答案会更清楚。',
    animation: 'midnight',
    badge: '子夜',
  },
  {
    id: 'late-night',
    label: '深夜',
    match: (h) => h >= 23 || h < 5,
    prefix: '🌌 深夜回响：',
    answerText: '别急着定论，先把心放轻一点。',
    animation: 'midnight',
    badge: '深夜',
  },
  {
    id: 'dawn',
    label: '清晨',
    match: (h) => h >= 5 && h < 7,
    prefix: '🌅 晨光彩蛋：',
    answerText: '新的一天刚开始，犹豫往往已经有了出口。',
    animation: 'dawn',
    badge: '清晨',
  },
]

function isLocationEnabled(): boolean {
  return localStorage.getItem('privacy_location') === 'true'
}

function formatMonthDay(date: Date): string {
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${m}-${d}`
}

function detectSolarEgg(now: Date): AnswerEasterEgg | null {
  const md = formatMonthDay(now)
  const hit = SOLAR_WINDOWS.find((item) => md >= item.start && md <= item.end)
  if (!hit) return null
  return {
    id: hit.id,
    type: 'solar_term',
    label: hit.label,
    answerText: hit.answerText,
    prefix: hit.prefix,
    animation: hit.animation,
    badge: hit.badge,
  }
}

function detectTimeEgg(now: Date): AnswerEasterEgg | null {
  const hour = now.getHours()
  const hit = TIME_EGGS.find((item) => item.match(hour))
  if (!hit) return null
  return {
    id: hit.id,
    type: 'time',
    label: hit.label,
    answerText: hit.answerText,
    prefix: hit.prefix,
    animation: hit.animation,
    badge: hit.badge,
  }
}

async function getCurrentPosition(): Promise<{ latitude: number; longitude: number } | null> {
  if (!isLocationEnabled() || !('geolocation' in navigator)) return null
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude })
      },
      () => resolve(null),
      { timeout: 8000, maximumAge: 10 * 60 * 1000 },
    )
  })
}

type WeatherSnapshot = {
  weatherCode: number
  isDay: boolean
  cachedAt: number
}

async function fetchWeatherSnapshot(): Promise<WeatherSnapshot | null> {
  try {
    const raw = sessionStorage.getItem(WEATHER_CACHE_KEY)
    if (raw) {
      const cached = JSON.parse(raw) as WeatherSnapshot
      if (Date.now() - cached.cachedAt <= WEATHER_CACHE_TTL_MS) return cached
    }
  } catch {
    // ignore
  }

  const pos = await getCurrentPosition()
  if (!pos) return null

  const url = `https://api.open-meteo.com/v1/forecast?latitude=${pos.latitude}&longitude=${pos.longitude}&current=weather_code,is_day`
  const res = await fetch(url)
  if (!res.ok) return null
  const data = (await res.json()) as {
    current?: { weather_code?: number; is_day?: number }
  }
  const weatherCode = Number(data.current?.weather_code ?? -1)
  const isDay = Number(data.current?.is_day ?? 1) === 1
  if (Number.isNaN(weatherCode) || weatherCode < 0) return null

  const snapshot: WeatherSnapshot = { weatherCode, isDay, cachedAt: Date.now() }
  sessionStorage.setItem(WEATHER_CACHE_KEY, JSON.stringify(snapshot))
  return snapshot
}

function detectWeatherEgg(snapshot: WeatherSnapshot | null): AnswerEasterEgg | null {
  if (!snapshot) return null
  const { weatherCode, isDay } = snapshot

  const isRain =
    (weatherCode >= 51 && weatherCode <= 67) || (weatherCode >= 80 && weatherCode <= 82)
  const isSnow = weatherCode >= 71 && weatherCode <= 77

  if (isSnow) {
    return {
      id: 'snow',
      type: 'weather',
      label: '雪天',
      prefix: '❄️ 雪天彩蛋：',
      answerText: '慢下来，像雪一样轻，你会看见真正重要的。',
      animation: 'snow',
      badge: '雪天',
    }
  }

  if (isRain) {
    return {
      id: 'rain',
      type: 'weather',
      label: '雨天',
      prefix: '🌧️ 雨声彩蛋：',
      answerText: '雨会替你筛掉杂念，留下这一句就够了。',
      animation: 'rain',
      badge: '雨天',
    }
  }

  if (!isDay && weatherCode === 0) {
    return {
      id: 'clear-night',
      type: 'weather',
      label: '晴夜',
      prefix: '✨ 晴夜星语：',
      answerText: '星空很静，你的答案其实已经在心里。',
      animation: 'midnight',
      badge: '晴夜',
    }
  }

  return null
}

/** 优先级：节气 > 天气 > 时间 */
export async function detectAnswerEasterEgg(now = new Date()): Promise<AnswerEasterEgg | null> {
  const solar = detectSolarEgg(now)
  if (solar) return solar

  if (isLocationEnabled()) {
    try {
      const weather = await fetchWeatherSnapshot()
      const weatherEgg = detectWeatherEgg(weather)
      if (weatherEgg) return weatherEgg
    } catch {
      // 天气失败时不阻断正常流程
    }
  }

  return detectTimeEgg(now)
}

export function recordEasterEggTrigger(eggId: string) {
  try {
    const raw = localStorage.getItem(EGG_STATS_KEY)
    const stats = raw ? (JSON.parse(raw) as Record<string, number>) : {}
    stats[eggId] = (stats[eggId] || 0) + 1
    stats.total = (stats.total || 0) + 1
    localStorage.setItem(EGG_STATS_KEY, JSON.stringify(stats))
  } catch {
    // ignore
  }
}

export function getEasterEggStats(): Record<string, number> {
  try {
    const raw = localStorage.getItem(EGG_STATS_KEY)
    return raw ? (JSON.parse(raw) as Record<string, number>) : {}
  } catch {
    return {}
  }
}
