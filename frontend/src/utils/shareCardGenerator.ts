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
  fortunebgImage: '/images/fortune_card_bg.png',
  answerBg: ['#E8F0FE', '#D9E6FF'],
  answerbgImage: '/images/answer_card_bg.png',
  titleColor: '#B45309',
  answerColor: '#6D28D9',
  textPrimary: '#1F2937',
  textSecondary: '#6B7280',
  yiColor: '#047857',
  jiColor: '#B91C1C',
  fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
  // 放大字体
  titleSize: 108,
  scoreSize: 32,
  mainSize: 32,
  subSize: 28,
  answerSize: 44,
  questionSize: 32,
  yiJiSize: 32,
  // 加大内边距
  padding: 70,
  lineHeight: 1.6,
  // 二维码配置
  qrSize: 140,
  qrMargin: 40,
  qrImagePath: '/images/qrcode.png',
  qrText: '扫码体验更多运势答案',
  qrTextSize: 20,
}

// ==================== 字体配置（治愈国风） ====================
const FONTS = {
  // 上吉/中吉/大吉等标题字体（霞鹜文楷）
  title: `bold ${STYLE.titleSize}px 'LXGW WenKai', '霞鹜文楷', 'KaiTi', '楷体', cursive`,
  // 分数专用字体（DIN）
  score: `${STYLE.scoreSize}px 'DIN', 'Arial', sans-serif`,
  // 主签文字体（Noto Serif SC）
  main: `${STYLE.mainSize}px 'Noto Serif SC', 'Times New Roman', serif`,
  // 副签文字体（Noto Serif SC）
  sub: `${STYLE.subSize}px 'Noto Serif SC', 'Times New Roman', serif`,
  // 宜/忌等辅助文本（HarmonyOS Sans）
  auxiliary: `${STYLE.yiJiSize}px 'KaiTi', '楷体', 'STKaiti', '华文楷书', 'Noto Serif SC', 'Times New Roman', serif`,
  // 底部标语字体（HarmonyOS Sans）
  footer: `24px 'HarmonyOS Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif`,
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
  const x = width - size - margin - 40
  const y = height - size - margin - 30

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

  let bgImageLoaded = false
  try {
    const bgImg = await loadImage(STYLE.fortunebgImage)
    ctx.drawImage(bgImg, 0, 0, CARD_WIDTH, CARD_HEIGHT)
    bgImageLoaded = true
  } catch (err) {
    console.warn('背景图片加载失败，使用渐变背景', err)
  }

  if (!bgImageLoaded) {
    // 降级：渐变背景
    const grad = ctx.createLinearGradient(0, 0, 0, CARD_HEIGHT)
    grad.addColorStop(0, STYLE.fortuneBg[0])
    grad.addColorStop(1, STYLE.fortuneBg[1])
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT)
  }

  ctx.textAlign = 'center'

  // 签文标题（上上签等）—— 使用 title 字体
  ctx.font = FONTS.title
  ctx.fillStyle = STYLE.titleColor
  const titleX = 640
  const titleY = 280
  ctx.fillText(data.title, titleX, titleY)

  // 分数 —— 使用 score 字体
  ctx.font = FONTS.score
  ctx.fillStyle = STYLE.textSecondary
  ctx.fillText(`运势得分 ${data.score}分`, titleX, 360)

  // 主签文 —— 使用 main 字体
  ctx.font = FONTS.main
  ctx.fillStyle = STYLE.textPrimary
  let y = 585
  y = wrapText(
    ctx,
    data.content_main,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    STYLE.mainSize * STYLE.lineHeight,
    2,
  )

  // 副签文 —— 使用 sub 字体
  ctx.font = FONTS.sub
  ctx.fillStyle = STYLE.textSecondary
  y += 15
  y = wrapText(
    ctx,
    data.content_sub,
    CARD_WIDTH / 2,
    y,
    CARD_WIDTH - 2 * STYLE.padding,
    STYLE.subSize * STYLE.lineHeight,
    1,
  )

  ctx.textAlign = 'left'
  const leftX = 260
  let currentY = 743
  // 宜 / 忌 —— 使用 auxiliary 字体
  ctx.font = FONTS.auxiliary
  ctx.fillStyle = STYLE.yiColor
  const yiFullText = `${data.yi.join('、') || '无'}`
  ctx.fillText(yiFullText, leftX, currentY)

  // 绘制忌（另起一行）
  currentY += STYLE.yiJiSize * STYLE.lineHeight + 60
  ctx.fillStyle = STYLE.jiColor
  const jiFullText = `${data.ji.join('、') || '无'}`
  ctx.fillText(jiFullText, leftX, currentY)

  // 避免 ESLint 未使用变量警告
  void y

  // 绘制二维码
  await drawQRCode(ctx, CARD_WIDTH, CARD_HEIGHT)
}

// ========== 答案卡片（精确垂直居中版） ==========
// ========== 答案卡片（精确垂直居中版） ==========
export async function drawAnswerShareCard(
  canvas: HTMLCanvasElement,
  data: AnswerShareData,
): Promise<void> {
  canvas.width = CARD_WIDTH
  canvas.height = CARD_HEIGHT
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 1. 绘制背景
  let bgImageLoaded = false
  try {
    const bgImg = await loadImage(STYLE.answerbgImage)
    ctx.drawImage(bgImg, 0, 0, CARD_WIDTH, CARD_HEIGHT)
    bgImageLoaded = true
  } catch (err) {
    console.warn('答案卡片背景图片加载失败，使用渐变背景', err)
  }
  if (!bgImageLoaded) {
    const grad = ctx.createLinearGradient(0, 0, 0, CARD_HEIGHT)
    grad.addColorStop(0, STYLE.answerBg[0])
    grad.addColorStop(1, STYLE.answerBg[1])
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT)
  }

  // 2. 精确测量函数（完全模拟 wrapText 行数）
  function measureTextHeight(
    ctx: CanvasRenderingContext2D,
    text: string,
    maxWidth: number,
    lineHeight: number,
    maxLines?: number,
  ): number {
    if (!text) return 0
    const chars = [...text]
    let line = ''
    let lines = 0
    for (let i = 0; i < chars.length; i++) {
      const testLine = line + chars[i]
      const metrics = ctx.measureText(testLine)
      if (metrics.width > maxWidth && line.length > 0) {
        // 换行
        line = chars[i]
        lines++
        if (maxLines !== undefined && lines >= maxLines) {
          // 达到最大行数，截断行占一行
          //lines++
          break
        }
      } else {
        line = testLine
      }
    }
    // 循环结束后，如果还有剩余内容且未达到最大行数，则最后一行
    if (line && (maxLines === undefined || lines < maxLines)) {
      //lines++
    }
    return lines * lineHeight
  }

  ctx.textAlign = 'center'

  // 矩形边界（可自由调整）
  const questionRect = { top: 346, bottom: 624 }
  const answerRect = { top: 745, bottom: 998 }

  // ========== 问题区域 ==========
  const questionFont = `${STYLE.questionSize}px 'KaiTi', '楷体', 'STKaiti', '华文楷书', 'Noto Serif SC', 'Times New Roman', serif`
  const questionMaxWidth = CARD_WIDTH - 2 * 110
  const questionLineHeight = (STYLE.questionSize + 6) * STYLE.lineHeight
  const questionMaxLines = 4

  ctx.font = questionFont
  const questionHeight = measureTextHeight(
    ctx,
    data.question,
    questionMaxWidth,
    questionLineHeight,
    questionMaxLines,
  )
  const questionAvailable = questionRect.bottom - questionRect.top
  let questionY = questionRect.top + (questionAvailable - questionHeight) / 2
  questionY = Math.max(questionRect.top, Math.min(questionY, questionRect.bottom - questionHeight))

  ctx.font = questionFont
  ctx.fillStyle = STYLE.textPrimary
  let y = questionY
  y = wrapText(
    ctx,
    data.question,
    CARD_WIDTH / 2,
    y,
    questionMaxWidth,
    questionLineHeight,
    questionMaxLines,
  )

  // ========== 回答区域 ==========
  const answerFont = `bold ${STYLE.answerSize}px 'KaiTi', '楷体', 'STKaiti', '华文楷书', 'Noto Serif SC', 'Times New Roman', serif`
  const answerMaxWidth = CARD_WIDTH - 2 * 110
  const answerLineHeight = (STYLE.answerSize + 6) * STYLE.lineHeight
  const answerMaxLines = 5
  const answerText = `「${data.answerText}」`

  ctx.font = answerFont
  const answerHeight = measureTextHeight(
    ctx,
    answerText,
    answerMaxWidth,
    answerLineHeight,
    answerMaxLines,
  )
  const answerAvailable = answerRect.bottom - answerRect.top
  let answerY = answerRect.top + (answerAvailable - answerHeight) / 2
  answerY = Math.max(answerRect.top, Math.min(answerY, answerRect.bottom - answerHeight))

  ctx.font = answerFont
  ctx.fillStyle = STYLE.answerColor
  y = answerY
  y = wrapText(ctx, answerText, CARD_WIDTH / 2, y, answerMaxWidth, answerLineHeight, answerMaxLines)

  // 调试红线（开发环境）
  // if (import.meta.env.DEV) {
  //   ctx.save()
  //   ctx.strokeStyle = 'red'
  //   ctx.lineWidth = 2
  //   ctx.strokeRect(0, questionRect.top, CARD_WIDTH, questionRect.bottom - questionRect.top)
  //   ctx.strokeRect(0, answerRect.top, CARD_WIDTH, answerRect.bottom - answerRect.top)
  //   ctx.restore()
  // }

  void y
  await drawQRCode(ctx, CARD_WIDTH, CARD_HEIGHT)
}

// 下载图片
export function downloadCanvasAsImage(canvas: HTMLCanvasElement, filename: string) {
  const link = document.createElement('a')
  link.download = filename
  link.href = canvas.toDataURL('image/png')
  link.click()
}

// ========== 调试预览功能（开发环境使用） ==========
/**
 * 在页面中央弹窗预览运势卡片，点击任意位置关闭
 * @param data 运势数据
 */
export async function previewFortuneCard(data: FortuneShareData) {
  const canvas = document.createElement('canvas')
  await drawFortuneShareCard(canvas, data)

  // 创建遮罩层
  const overlay = document.createElement('div')
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    z-index: 99999;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    backdrop-filter: blur(4px);
  `

  // 创建图片元素展示卡片
  const img = document.createElement('img')
  img.src = canvas.toDataURL()
  img.style.maxWidth = '90%'
  img.style.maxHeight = '90%'
  img.style.borderRadius = '16px'
  img.style.boxShadow = '0 20px 35px rgba(0,0,0,0.4)'
  img.style.border = '2px solid #fff'

  overlay.appendChild(img)
  document.body.appendChild(overlay)

  // 点击遮罩层关闭预览
  overlay.onclick = () => overlay.remove()
}

/**
 * 预览答案卡片
 */
export async function previewAnswerCard(data: AnswerShareData) {
  const canvas = document.createElement('canvas')
  await drawAnswerShareCard(canvas, data)

  const overlay = document.createElement('div')
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.85);
    z-index: 99999;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    backdrop-filter: blur(4px);
  `
  const img = document.createElement('img')
  img.src = canvas.toDataURL()
  img.style.maxWidth = '90%'
  img.style.maxHeight = '90%'
  img.style.borderRadius = '16px'
  img.style.boxShadow = '0 20px 35px rgba(0,0,0,0.4)'
  overlay.appendChild(img)
  document.body.appendChild(overlay)
  overlay.onclick = () => overlay.remove()
}
