// PWA 资源生成脚本
// 生成：maskable 图标 / 快捷方式图标 / iOS 启动图（apple-touch-startup-image）
// 用法：在 frontend 目录下安装 sharp 后运行
//   npm i -D sharp && node scripts/gen-pwa-assets.mjs
// 生成的是静态 PNG，运行时不依赖 sharp。
import sharp from 'sharp'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, '..')
const SRC_ICON = path.join(root, 'public/icons/icon-512.png')
const ICONS_DIR = path.join(root, 'public/icons')
const SPLASH_DIR = path.join(root, 'public/splash')

// 与 manifest.background_color / 启动色保持一致
const BG = { r: 255, g: 255, b: 255, alpha: 1 }

async function makeMaskable(size) {
  // maskable 安全区为中心 80% 圆形，logo 缩放至 ~78% 居中，四周填白，避免被裁切
  const inner = Math.round(size * 0.78)
  const logo = await sharp(SRC_ICON)
    .resize(inner, inner, { fit: 'contain', background: BG })
    .toBuffer()
  await sharp({
    create: { width: size, height: size, channels: 4, background: BG },
  })
    .composite([{ input: logo, gravity: 'center' }])
    .png()
    .toFile(path.join(ICONS_DIR, `icon-${size}-maskable.png`))
  console.log(`maskable icon-${size}-maskable.png`)
}

async function makeShortcutIcon(size) {
  await sharp(SRC_ICON)
    .resize(size, size, { fit: 'contain', background: BG })
    .png()
    .toFile(path.join(ICONS_DIR, `icon-${size}.png`))
  console.log(`shortcut icon-${size}.png`)
}

// iOS 启动图（竖屏）。media 必须精确匹配设备，否则 iOS 忽略。
// [文件名, 像素宽, 像素高, css设备宽, css设备高, dpr]
const SPLASH = [
  ['iphone-se', 750, 1334, 375, 667, 2],
  ['iphone-8plus', 1242, 2208, 414, 736, 3],
  ['iphone-x', 1125, 2436, 375, 812, 3],
  ['iphone-xr', 828, 1792, 414, 896, 2],
  ['iphone-xsmax', 1242, 2688, 414, 896, 3],
  ['iphone-12', 1170, 2532, 390, 844, 3],
  ['iphone-12promax', 1284, 2778, 428, 926, 3],
  ['iphone-14pro', 1179, 2556, 393, 852, 3],
  ['iphone-14promax', 1290, 2796, 430, 932, 3],
  ['ipad', 1536, 2048, 768, 1024, 2],
  ['ipad-pro11', 1668, 2388, 834, 1194, 2],
  ['ipad-pro129', 2048, 2732, 1024, 1366, 2],
]

async function makeSplash([name, w, h]) {
  const logoSize = Math.round(Math.min(w, h) * 0.42)
  const logo = await sharp(SRC_ICON)
    .resize(logoSize, logoSize, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .toBuffer()
  await sharp({ create: { width: w, height: h, channels: 4, background: BG } })
    .composite([{ input: logo, gravity: 'center' }])
    .png()
    .toFile(path.join(SPLASH_DIR, `${name}.png`))
  console.log(`splash ${name}.png (${w}x${h})`)
}

function printLinks() {
  console.log('\n=== 把以下 <link> 复制进 index.html <head> ===\n')
  for (const [name, w, h, dw, dh, dpr] of SPLASH) {
    const media = `screen and (device-width: ${dw}px) and (device-height: ${dh}px) and (-webkit-device-pixel-ratio: ${dpr}) and (orientation: portrait)`
    console.log(
      `    <link rel="apple-touch-startup-image" media="${media}" href="/splash/${name}.png" />`,
    )
  }
}

async function main() {
  await mkdir(ICONS_DIR, { recursive: true })
  await mkdir(SPLASH_DIR, { recursive: true })
  await makeMaskable(192)
  await makeMaskable(512)
  await makeShortcutIcon(96)
  for (const s of SPLASH) await makeSplash(s)
  printLinks()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
