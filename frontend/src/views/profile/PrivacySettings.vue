<template>
  <div class="min-h-screen bg-slate-100 pb-20">
    <!-- 顶部导航栏 -->
    <div class="sticky top-0 z-10 bg-white border-b border-slate-200 px-4 py-3 flex items-center">
      <button
        @click="router.back()"
        class="p-1 rounded-full text-slate-600 hover:bg-slate-100 transition mr-3"
      >
        <IconChevronLeft />
      </button>
      <h1 class="text-lg font-semibold text-slate-800">隐私与权限</h1>
    </div>

    <div class="mt-3 space-y-3">
      <!-- 个性化推荐 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingToggle
          label="个性化推荐"
          icon="🎯"
          :value="recommendationEnabled"
          @toggle="toggleRecommendation"
        >
          <template #description>
            <span class="text-xs text-slate-500">根据您的使用习惯推荐更契合的运势和答案</span>
          </template>
        </SettingToggle>
      </div>

      <!-- 通知权限 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingToggle
          label="通知权限"
          icon="🔔"
          :value="notificationEnabled"
          @toggle="toggleNotification"
        >
          <template #description>
            <span class="text-xs text-slate-500">接收每日运势提醒和活动通知</span>
          </template>
        </SettingToggle>
      </div>

      <!-- 位置权限 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingToggle label="位置权限" icon="📍" :value="locationEnabled" @toggle="toggleLocation">
          <template #description>
            <span class="text-xs text-slate-500">用于天气彩蛋等个性化体验</span>
          </template>
        </SettingToggle>
      </div>

      <!-- 相册权限 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingToggle label="相册权限" icon="🖼️" :value="albumEnabled" @toggle="toggleAlbum">
          <template #description>
            <span class="text-xs text-slate-500">用于上传头像和保存运势卡片</span>
          </template>
        </SettingToggle>
      </div>

      <!-- 数据管理 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="清除缓存" @click="clearCache">
          <template #icon><IconTrash class="text-slate-500" /></template>
        </SettingItem>
        <Divider />
        <SettingItem label="管理授权" @click="manageAuthApps">
          <template #icon><IconApps /></template>
        </SettingItem>
      </div>

      <!-- 说明文字 -->
      <div class="text-center text-xs text-slate-400 px-6 py-4">
        我们尊重您的隐私，您可随时管理这些权限。<br />
        部分权限关闭后可能影响相关功能的正常使用。
      </div>
    </div>

    <!-- Toast 提示 -->
    <div
      v-if="toastMessage"
      class="fixed bottom-20 left-4 right-4 bg-black/70 text-white text-sm text-center py-2 rounded-lg z-50"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import IconChevronLeft from '@/components/icons/IconChevronLeft.vue'
import SettingItem from '@/views/profile/components/SettingItem.vue'
import SettingToggle from '@/views/profile/components/SettingToggle.vue'
import Divider from '@/views/profile/components/Divider.vue'
import IconTrash from '@/components/icons/IconTrash.vue'
import IconApps from '@/components/icons/IconApps.vue'

const router = useRouter()

// 开关状态（存储到 localStorage）
const recommendationEnabled = ref(true)
const notificationEnabled = ref(false)
const locationEnabled = ref(false)
const albumEnabled = ref(false)

const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(msg: string) {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = msg
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 2000)
}

// 加载保存的设置
function loadSettings() {
  recommendationEnabled.value = localStorage.getItem('privacy_recommendation') !== 'false'
  notificationEnabled.value = localStorage.getItem('privacy_notification') === 'true'
  locationEnabled.value = localStorage.getItem('privacy_location') === 'true'
  albumEnabled.value = localStorage.getItem('privacy_album') === 'true'
}

// 保存设置
function saveSetting(key: string, value: boolean) {
  localStorage.setItem(key, value ? 'true' : 'false')
}

// 个性化推荐
function toggleRecommendation() {
  const newVal = !recommendationEnabled.value
  recommendationEnabled.value = newVal
  saveSetting('privacy_recommendation', newVal)
  showToast(newVal ? '已开启个性化推荐' : '已关闭个性化推荐')
  // 这里可以触发全局事件，通知其他组件停止/开始收集画像数据
  window.dispatchEvent(new CustomEvent('recommendation-changed', { detail: { enabled: newVal } }))
}

// 通知权限
async function toggleNotification() {
  const newVal = !notificationEnabled.value
  if (newVal && Notification.permission === 'default') {
    const permission = await Notification.requestPermission()
    if (permission === 'granted') {
      notificationEnabled.value = true
      saveSetting('privacy_notification', true)
      showToast('已开启通知权限')
    } else {
      notificationEnabled.value = false
      saveSetting('privacy_notification', false)
      showToast('通知权限被拒绝，请在浏览器设置中开启')
    }
    return
  }
  if (newVal && Notification.permission === 'denied') {
    notificationEnabled.value = false
    saveSetting('privacy_notification', false)
    showToast('通知权限已被拒绝，请在浏览器设置中手动开启')
    return
  }
  notificationEnabled.value = newVal
  saveSetting('privacy_notification', newVal)
  showToast(newVal ? '已开启通知' : '已关闭通知')
}

// 位置权限
function toggleLocation() {
  const newVal = !locationEnabled.value
  if (newVal) {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        () => {
          locationEnabled.value = true
          saveSetting('privacy_location', true)
          showToast('已获取位置权限')
        },
        (err) => {
          locationEnabled.value = false
          saveSetting('privacy_location', false)
          showToast('位置权限被拒绝，请在浏览器设置中开启')
          console.warn(err)
        },
      )
    } else {
      locationEnabled.value = false
      saveSetting('privacy_location', false)
      showToast('当前浏览器不支持地理位置')
    }
  } else {
    locationEnabled.value = false
    saveSetting('privacy_location', false)
    showToast('已关闭位置权限')
  }
}

// 相册权限（其实浏览器相册权限通过 input 文件选择触发，这里只是模拟开关存储）
function toggleAlbum() {
  const newVal = !albumEnabled.value
  albumEnabled.value = newVal
  saveSetting('privacy_album', newVal)
  showToast(newVal ? '已开启相册权限' : '已关闭相册权限（上传图片时会请求）')
}

// 清除缓存
function clearCache() {
  if (confirm('清除缓存将删除本地存储的日记、历史答案等数据，但不会删除账号信息。确定继续吗？')) {
    // 清除除用户认证和设置外的数据
    const keysToKeep = [
      'token',
      'userInfo',
      'privacy_recommendation',
      'privacy_notification',
      'privacy_location',
      'privacy_album',
    ]
    const allKeys = Object.keys(localStorage)
    allKeys.forEach((key) => {
      if (!keysToKeep.includes(key) && !key.startsWith('privacy_')) {
        localStorage.removeItem(key)
      }
    })
    showToast('缓存已清除')
    // 重新加载页面以重置状态
    setTimeout(() => window.location.reload(), 1500)
  }
}

// 管理授权应用（暂未实现）
function manageAuthApps() {
  alert('此功能暂未开放，敬请期待')
}

onMounted(() => {
  loadSettings()
})
</script>
