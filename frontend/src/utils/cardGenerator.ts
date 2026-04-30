// src/utils/cardGenerator.ts

export interface FortuneCardData {
  text: string // 主文案
  sub: string // 副文案
  stats: string[] // 四个自定义字符串，例如 ["中上", "平稳", "注意作息", "谨慎消费"]
}

export interface AnswerCardData {
  answer: string // 答案文本
}

// 加载图片
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

// 文本自动换行
function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number,
) {
  const chars = text.split('')
  let line = ''
  let currentY = y
  for (let n = 0; n < chars.length; n++) {
    const testLine = line + chars[n]
    const metrics = ctx.measureText(testLine)
    const testWidth = metrics.width
    if (testWidth > maxWidth && n > 0) {
      ctx.fillText(line, x, currentY)
      line = chars[n]
      currentY += lineHeight
    } else {
      line = testLine
    }
  }
  ctx.fillText(line, x, currentY)
  return currentY + lineHeight
}

// 绘制运势卡片（基于模板 /images/card_fortune.png）
export async function drawFortuneCard(
  canvas: HTMLCanvasElement,
  data: FortuneCardData,
): Promise<void> {
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const templateImg = await loadImage('/images/card_fortune.png')
  canvas.width = templateImg.width
  canvas.height = templateImg.height
  ctx.drawImage(templateImg, 0, 0, canvas.width, canvas.height)

  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  // 1. 主文案（text）
  ctx.fillStyle = '#333333'
  ctx.font = `bold ${canvas.width * 0.08}px "Georgia", serif`
  wrapText(
    ctx,
    data.text,
    canvas.width / 2,
    canvas.height * 0.52,
    canvas.width * 0.68,
    canvas.height * 0.047,
  )

  // 2. 副文案（sub）
  ctx.fillStyle = '#888888'
  ctx.font = `${canvas.width * 0.027}px sans-serif`
  ctx.fillText(data.sub, canvas.width / 2, canvas.height * 0.6)

  // 3. 四个百分比数值
  const statsCenterX = [0.205, 0.395, 0.595, 0.795] // 从左到右，四个数字的 X 中心比例
  const statsY = canvas.height * 0.79 // 标签 y 坐标（与模板中文字垂直对齐）
  data.stats.forEach((text, i) => {
    const x = canvas.width * statsCenterX[i]
    ctx.fillStyle = '#6b5cff'
    ctx.font = `bold ${canvas.width * 0.035}px sans-serif`
    ctx.fillText(text, x, statsY + canvas.height * 0.05)
    // ctx.fillStyle = 'red'
    // ctx.beginPath()
    // ctx.arc(x, statsY + canvas.height * 0.05, 5, 0, 2 * Math.PI)
    // ctx.fill()
  })
}

// 绘制答案卡片（基于模板 /images/card_answer.png）
export async function drawAnswerCard(
  canvas: HTMLCanvasElement,
  data: AnswerCardData,
): Promise<void> {
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const templateImg = await loadImage('/images/card_answer.png')
  canvas.width = templateImg.width
  canvas.height = templateImg.height
  ctx.drawImage(templateImg, 0, 0, canvas.width, canvas.height)

  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  // 答案文本
  ctx.fillStyle = '#222222'
  ctx.font = `bold ${canvas.width * 0.048}px "Georgia", serif`
  wrapText(
    ctx,
    data.answer,
    canvas.width / 2,
    canvas.height * 0.5,
    canvas.width * 0.61,
    canvas.height * 0.058,
  )
}

// 导出图片并下载
export function downloadCard(canvas: HTMLCanvasElement, filename = 'card.png') {
  const link = document.createElement('a')
  link.download = filename
  link.href = canvas.toDataURL('image/png')
  link.click()
}
