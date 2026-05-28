// src/utils/shareCardGenerator.ts

export interface FortuneShareData {
  title: string
  score: number
  content_main: string
  content_sub: string
  yi: string[]
  ji: string[]
}

export interface AnswerShareData {
  question: string
  answerText: string
  createdAt?: string
}

// ==================== 样式配置（放大版） ====================
const CARD_WIDTH = 900
const CARD_HEIGHT = 1200

const STYLE = {
  fortuneBg: ['#FFF5E6', '#FFEAD2'],
  answerBg: ['#E8F0FE', '#D9E6FF'],
  titleColor: '#B45309',
  answerColor: '#6D28D9',
  textPrimary: '#1F2937',
  textSecondary: '#6B7280',
  yiColor: '#047857',
  jiColor: '#B91C1C',
  fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
  // 放大字体
  titleSize: 48,
  scoreSize: 32,
  mainSize: 42,
  subSize: 28,
  answerSize: 44,
  questionSize: 28,
  yiJiSize: 28,
  // 加大内边距
  padding: 48,
  lineHeight: 1.6,
  // 二维码配置
  qrSize: 140,
  qrMargin: 40,
  qrImagePath: 'public/images/qrcode.png',
  qrText: '扫码体验更多运势答案',
  qrTextSize: 20,
}

// 加载图片辅助函数
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'Anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

// 在 canvas 右下角绘制二维码（带引导文字，并增加底部间距）
async function drawQRCode(ctx: CanvasRenderingContext2D, width: number, height: number) {
  const size = STYLE.qrSize
  const margin = STYLE.qrMargin
  // 二维码左上角坐标（右下角定位，增加右侧额外偏移）
  const x = width - size - margin - 20
  const y = height - size - margin - 40

  try {
    const qrImg = await loadImage(STYLE.qrImagePath)
    ctx.drawImage(qrImg, x, y, size, size)
  } catch (err) {
    console.warn('二维码图片加载失败，使用 fallback 绘制', err)
    ctx.fillStyle = '#E5E7EB'
    roundRect(ctx, x, y, size, size, 16)
    ctx.fill()
    ctx.fillStyle = '#6B7280'
    ctx.font = `24px ${STYLE.fontFamily}`
    ctx.textAlign = 'center'
    ctx.fillText('扫码', x + size / 2, y + size / 2 + 8)
    ctx.fillText('访问', x + size / 2, y + size / 2 + 32)
  }

  // 在二维码下方添加引导文字
  ctx.fillStyle = '#9CA3AF'
  ctx.font = `${STYLE.qrTextSize}px ${STYLE.fontFamily}`
  ctx.textAlign = 'center'
  ctx.fillText(STYLE.qrText, x + size / 2, y + size + STYLE.qrTextSize + 8)
  ctx.textAlign = 'left' // 恢复
}

// 辅助函数：绘制圆角矩形
function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + w - r, y)
  ctx.quadraticCurveTo(x + w, y, x + w, y + r)
  ctx.lineTo(x + w, y + h - r)
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
  ctx.lineTo(x + r, y + h)
  ctx.quadraticCurveTo(x, y + h, x, y + h - r)
  ctx.lineTo(x, y + r)
  ctx.quadraticCurveTo(x, y, x + r, y)
  ctx.closePath()
  ctx.fill()
}

// 文本自动换行（支持居中/左/右对齐，调用前设置好 ctx.textAlign）
function wrapText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number, // 参考 X 坐标（对齐方式由 textAlign 决定）
  y: number,
  maxWidth: number,
  lineHeight: number,
  maxLines?: number,
): number {
  const chars = [...text]
  let line = ''
  let currentY = y
  let lines = 0
  for (let i = 0; i < chars.length; i++) {
    const testLine = line + chars[i]
    const metrics = ctx.measureText(testLine)
    if (metrics.width > maxWidth && line.length > 0) {
      ctx.fillText(line, x, currentY)
      line = chars[i]
      currentY += lineHeight
      lines++
      if (maxLines !== undefined && lines >= maxLines) {
        const truncated = line.slice(0, -1) + '…'
        ctx.fillText(truncated, x, currentY)
        return currentY + lineHeight
      }
    } else {
      line = testLine
    }
  }
  if (line) {
    ctx.fillText(line, x, currentY)
    currentY += lineHeight
  }
  return currentY
}

// ========== 运势卡片 ==========
export async function drawFortuneShareCard(
  canvas: HTMLCanvasElement,
  data: FortuneShareData,
): Promise<void> {
  canvas.width = CARD_WIDTH
  canvas.height = CARD_HEIGHT
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 背景渐变
  const grad = ctx.createLinearGradient(0, 0, 0, CARD_HEIGHT)
  grad.addColorStop(0, STYLE.fortuneBg[0])
  grad.addColorStop(1, STYLE.fortuneBg[1])
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT)

  // 装饰圆点
  ctx.fillStyle = '#FDE68A'
  ctx.beginPath()
  ctx.arc(CARD_WIDTH - 80, 80, 80, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#FCD34D'
  ctx.beginPath()
  ctx.arc(80, CARD_HEIGHT - 140, 70, 0, Math.PI * 2)
  ctx.fill()

  ctx.textAlign = 'center'

  // 标题
  ctx.fillStyle = STYLE.textPrimary
  ctx.font = `${STYLE.titleSize}px ${STYLE.fontFamily}`
  ctx.fillText('✨ 今日运势 ✨', CARD_WIDTH / 2, 120)

  // 签文标题 + 分数
  ctx.font = `bold ${STYLE.scoreSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.titleColor
  ctx.fillText(data.title, CARD_WIDTH / 2, 200)
  ctx.font = `${STYLE.scoreSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.textSecondary
  ctx.fillText(`${data.score}分`, CARD_WIDTH / 2, 260)

  // 主签文
  ctx.font = `${STYLE.mainSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.textPrimary
  let y = 340
  y = wrapText(
    ctx,
    data.content_main,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    STYLE.mainSize * STYLE.lineHeight,
    4,
  )

  // 副签文
  ctx.font = `${STYLE.subSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.textSecondary
  y += 30
  y = wrapText(
    ctx,
    data.content_sub,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    STYLE.subSize * STYLE.lineHeight,
    3,
  )

  // 宜 / 忌
  y += 40
  ctx.font = `${STYLE.yiJiSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.yiColor
  const yiText = `宜：${data.yi.join('、') || '无'}`
  y = wrapText(
    ctx,
    yiText,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    STYLE.yiJiSize * STYLE.lineHeight,
    2,
  )
  ctx.fillStyle = STYLE.jiColor
  const jiText = `忌：${data.ji.join('、') || '无'}`
  y = wrapText(
    ctx,
    jiText,
    CARD_WIDTH / 2,
    y + 10,
    CARD_WIDTH - 2 * STYLE.padding,
    STYLE.yiJiSize * STYLE.lineHeight,
    2,
  )

  // 底部标语
  ctx.font = `24px ${STYLE.fontFamily}`
  ctx.fillStyle = '#D97706'
  ctx.fillText('心运岛 · 每日指引', CARD_WIDTH / 2, CARD_HEIGHT - 140)

  // 避免 ESLint 未使用变量警告
  void y

  // 绘制二维码
  await drawQRCode(ctx, CARD_WIDTH, CARD_HEIGHT)
}

// ========== 答案卡片 ==========
export async function drawAnswerShareCard(
  canvas: HTMLCanvasElement,
  data: AnswerShareData,
): Promise<void> {
  canvas.width = CARD_WIDTH
  canvas.height = CARD_HEIGHT
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const grad = ctx.createLinearGradient(0, 0, 0, CARD_HEIGHT)
  grad.addColorStop(0, STYLE.answerBg[0])
  grad.addColorStop(1, STYLE.answerBg[1])
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT)

  // 装饰
  ctx.fillStyle = '#C4B5FD'
  ctx.beginPath()
  ctx.arc(CARD_WIDTH - 80, 100, 80, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#A78BFA'
  ctx.beginPath()
  ctx.arc(90, CARD_HEIGHT - 160, 90, 0, Math.PI * 2)
  ctx.fill()

  ctx.textAlign = 'center'

  // 标题
  ctx.font = `${STYLE.titleSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.textPrimary
  ctx.fillText('📖 答案之书', CARD_WIDTH / 2, 120)

  // 问题标签
  ctx.font = `${STYLE.questionSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.textSecondary
  let y = 210
  ctx.fillText('你的问题', CARD_WIDTH / 2, y)
  y += 50

  // 问题正文
  ctx.font = `${STYLE.questionSize + 6}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.textPrimary
  y = wrapText(
    ctx,
    data.question,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    (STYLE.questionSize + 6) * STYLE.lineHeight,
    4,
  )

  // 答案标签
  y += 50
  ctx.font = `${STYLE.answerSize}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.answerColor
  ctx.fillText('宇宙的回答', CARD_WIDTH / 2, y)
  y += 60

  // 答案正文
  ctx.font = `bold ${STYLE.answerSize + 6}px ${STYLE.fontFamily}`
  ctx.fillStyle = STYLE.answerColor
  y = wrapText(
    ctx,
    `「${data.answerText}」`,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    (STYLE.answerSize + 6) * STYLE.lineHeight,
    5,
  )

  // 底部标语
  ctx.font = `24px ${STYLE.fontFamily}`
  ctx.fillStyle = '#6D28D9'
  ctx.fillText('心运岛 · 答案之书', CARD_WIDTH / 2, CARD_HEIGHT - 140)

  // 避免 ESLint 未使用变量警告
  void y

  // 绘制二维码
  await drawQRCode(ctx, CARD_WIDTH, CARD_HEIGHT)
}

// 下载图片
export function downloadCanvasAsImage(canvas: HTMLCanvasElement, filename: string) {
  const link = document.createElement('a')
  link.download = filename
  link.href = canvas.toDataURL('image/png')
  link.click()
}
