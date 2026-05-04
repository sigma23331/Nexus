/** 按日期稳定映射到八卦索引 0–7，用于分享卡配色与卦名点缀 */
export function baguaIndexFromDate(dateStr: string): number {
  let h = 2166136261
  for (let i = 0; i < dateStr.length; i++) {
    h ^= dateStr.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h) % 8
}

export const BAGUA_KEYS = ['qian', 'dui', 'li', 'zhen', 'xun', 'kan', 'gen', 'kun'] as const

export const BAGUA_LABELS: Record<(typeof BAGUA_KEYS)[number], string> = {
  qian: '乾 · 天',
  dui: '兑 · 泽',
  li: '离 · 火',
  zhen: '震 · 雷',
  xun: '巽 · 风',
  kan: '坎 · 水',
  gen: '艮 · 山',
  kun: '坤 · 地',
}

export function baguaKeyFromDate(dateStr: string): (typeof BAGUA_KEYS)[number] {
  return BAGUA_KEYS[baguaIndexFromDate(dateStr)]!
}
