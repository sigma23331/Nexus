<template>
  <div class="min-h-screen bg-slate-100 pb-20">
    <!-- 顶部导航栏（不变） -->
    <div
      class="sticky top-0 z-10 bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-center"
    >
      <button
        @click="router.back()"
        class="absolute left-4 p-1 rounded-full text-slate-600 hover:bg-slate-100 transition"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 18l-6-6 6-6" />
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-slate-800">设置</h1>
    </div>

    <div class="mt-3 space-y-3">
      <!-- 账号与安全板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="个人资料" @click="openProfileEdit">
          <template #icon><IconUser /></template>
        </SettingItem>
        <Divider />
        <!-- 修改密码 -->
        <SettingItem label="修改密码" @click="changePassword">
          <template #icon><IconKey /></template>
        </SettingItem>
      </div>

      <!-- 通用板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="添加到主屏幕" @click="handleInstallToDesktop">
          <template #icon><IconDeviceMobile /></template>
        </SettingItem>
      </div>

      <!-- 隐私与权限板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="隐私与权限" @click="goToPrivacySettings">
          <template #icon><IconLock /></template>
        </SettingItem>
        <Divider />
        <SettingItem label="获取并保存当前位置" @click="captureAndSaveLocation">
          <template #icon><IconDeviceMobile /></template>
        </SettingItem>
      </div>

      <!-- 其他板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="用户协议" @click="openAgreement">
          <template #icon><IconDocument /></template>
        </SettingItem>
        <Divider />
        <!-- 隐私政策：保持盾牌 -->
        <SettingItem label="隐私政策" @click="openPrivacy">
          <template #icon><IconShield /></template>
        </SettingItem>
      </div>

      <!-- 帮助与反馈板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="帮助与反馈" @click="goToHelp">
          <template #icon><IconHelp /></template>
        </SettingItem>
      </div>

      <!-- 账号操作板块（红色文字） -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="退出登录" @click="handleLogout" color-red>
          <template #icon><IconLogout class="text-rose-500" /></template>
        </SettingItem>
        <Divider />
        <SettingItem label="注销账号" @click="handleDeleteAccount" color-red>
          <template #icon><IconTrash class="text-rose-500" /></template>
        </SettingItem>
      </div>
    </div>

    <!-- 弹窗组件（不变） -->
    <UserAgreementModal ref="userAgreementModalRef" />
    <PrivacyPolicyModal ref="privacyPolicyModalRef" />
    <ConfirmModal ref="confirmModalRef" />
    <ChangePasswordModal ref="changePasswordModalRef" />
    <ProfileEditModal ref="profileEditModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { updateUserLocation } from '@/api/user'
import UserAgreementModal from '@/components/common/UserAgreementModal.vue'
import PrivacyPolicyModal from '@/components/common/PrivacyPolicyModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ChangePasswordModal from '@/components/common/ChangePasswordModal.vue'
import ProfileEditModal from '@/components/common/ProfileEditModal.vue'
import SettingItem from '@/views/profile/components/SettingItem.vue'
import Divider from '@/views/profile/components/Divider.vue'
// 导入图标组件
import IconUser from '@/components/icons/IconUser.vue'
import IconLock from '@/components/icons/IconLock.vue'
import IconDeviceMobile from '@/components/icons/IconDeviceMobile.vue'
import IconDocument from '@/components/icons/IconDocument.vue'
import IconShield from '@/components/icons/IconShield.vue'
import IconLogout from '@/components/icons/IconLogout.vue'
import IconTrash from '@/components/icons/IconTrash.vue'
import IconKey from '@/components/icons/IconKey.vue'
import IconHelp from '@/components/icons/IconHelp.vue'

const router = useRouter()
const userStore = useUserStore()

const userAgreementModalRef = ref<InstanceType<typeof UserAgreementModal> | null>(null)
const privacyPolicyModalRef = ref<InstanceType<typeof PrivacyPolicyModal> | null>(null)
const confirmModalRef = ref<InstanceType<typeof ConfirmModal> | null>(null)
const changePasswordModalRef = ref<InstanceType<typeof ChangePasswordModal> | null>(null)
const profileEditModalRef = ref<InstanceType<typeof ProfileEditModal> | null>(null)

const openProfileEdit = () => profileEditModalRef.value?.open()
const changePassword = async () => await changePasswordModalRef.value?.open()
const handleInstallToDesktop = () => window.dispatchEvent(new CustomEvent('manual-install-trigger'))

// 临时弹窗提示（未实现页面）
const goToPrivacySettings = () => {
  alert('隐私与权限设置正在开发中，敬请期待～')
}

const captureAndSaveLocation = async () => {
  if (!window.isSecureContext && location.hostname !== 'localhost') {
    alert('定位功能仅支持 HTTPS 或 localhost 环境')
    return
  }
  if (!('geolocation' in navigator)) {
    alert('当前浏览器不支持定位功能')
    return
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        await updateUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          locationAccuracy: position.coords.accuracy,
        })
        await userStore.fetchUserInfo()
        alert('位置已保存')
      } catch (err: unknown) {
        alert(err instanceof Error ? err.message : '位置保存失败，请稍后重试')
      }
    },
    (error) => {
      const messageMap: Record<number, string> = {
        1: '未授予定位权限，请在浏览器设置中允许定位',
        2: '无法获取位置信息，请检查 GPS 或网络',
        3: '定位超时，请重试',
      }
      alert(messageMap[error.code] || '定位失败，请稍后重试')
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    },
  )
}
const goToHelp = () => {
  router.push('/profile/settings/help')
}

const handleLogout = async () => {
  const confirmed = await confirmModalRef.value?.open({
    title: '退出登录',
    message: '确定要退出登录吗？',
  })
  if (confirmed) {
    userStore.logout()
    router.replace('/login')
  }
}

const handleDeleteAccount = async () => {
  const confirmed = await confirmModalRef.value?.open({
    title: '注销账号',
    message: '⚠️ 注销账号将永久删除所有数据，不可恢复。确定要继续吗？',
  })
  if (confirmed) {
    userStore.logout()
    localStorage.clear()
    router.replace('/login')
  }
}

const openAgreement = () => userAgreementModalRef.value?.open()
const openPrivacy = () => privacyPolicyModalRef.value?.open()
</script>
