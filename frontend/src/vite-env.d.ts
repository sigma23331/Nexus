/// <reference types="vite/client" />

declare module '*.css' {
  const content: string
  export default content
}

// 如果还有其他静态资源（图片等），也可以添加
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, any>
  export default component
}
