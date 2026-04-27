// 字体样式选项：每个选项包含 Tailwind 类名和描述
export interface FontStyle {
  id: string
  name: string
  classes: string // 字体系列、大小、字重、行高等
  preview: string
}

// 预设字体样式列表，可供下拉选择或直接引用
export const fontStyles: FontStyle[] = [
  {
    id: 'base',
    name: '默认',
    classes: 'text-sm leading-relaxed text-slate-700',
    preview: '默认字体样式，适合日常阅读。',
  },
  {
    id: 'large-soft',
    name: '大号柔和',
    classes: 'text-base leading-loose text-slate-600 font-light',
    preview: '大号柔和字体，阅读更轻松。',
  },
  {
    id: 'compact',
    name: '紧凑',
    classes: 'text-xs leading-tight text-slate-800 font-medium',
    preview: '小号紧凑字体，节省空间。',
  },
  {
    id: 'elegant',
    name: '优雅',
    classes: 'text-base leading-relaxed text-slate-700 font-serif',
    preview: '衬线字体，更具优雅感。',
  },
  {
    id: 'bold-note',
    name: '粗体笔记',
    classes: 'text-sm font-semibold leading-normal text-slate-800',
    preview: '粗体字重，突出重点。',
  },
]

// 工具函数：根据 id 获取对应的 classes
export function getFontClasses(id: string): string {
  const style = fontStyles.find((s) => s.id === id)
  return style?.classes || fontStyles[0].classes
}
