<template>
  <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
    <h1 style="color: #646cff;">🏝️ 心运岛测试版 Ver1.0</h1>
    <p>如果看到下方文字变化，说明前后端打通了：</p>
    <div style="padding: 20px; background: #f9f9f9; border-radius: 8px; display: inline-block;">
      <strong>后端消息：</strong> {{ message }}
    </div>
    <br /><br />
    <button @click="fetchData" style="padding: 10px 20px; cursor: pointer;">
      点击请求后端数据
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const message = ref('点击按钮试试...')

const fetchData = async () => {
  try {
    // 注意：这里用相对路径 /api，依赖 Vite 代理或 Nginx 转发
    const response = await fetch('/api/test')
    const data = await response.json()
    message.value = data.message
  } catch (err) {
    message.value = '请求失败，请检查 API 转发配置'
    console.error(err)
  }
}
</script>