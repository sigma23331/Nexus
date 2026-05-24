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
        <SettingItem label="修改个人信息" @click="openProfileEdit">
          <template #icon><IconUser /></template>
        </SettingItem>
        <Divider />
        <SettingItem label="修改密码" @click="changePassword">
          <template #icon><IconLock /></template>
        </SettingItem>
      </div>

      <!-- 通用板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="添加到主屏幕" @click="handleInstallToDesktop">
          <template #icon><IconDeviceMobile /></template>
        </SettingItem>
      </div>

      <!-- 其他板块 -->
      <div class="bg-white rounded-lg mx-3 overflow-hidden">
        <SettingItem label="用户协议" @click="openAgreement">
          <template #icon><IconDocument /></template>
        </SettingItem>
        <Divider />
        <SettingItem label="隐私政策" @click="openPrivacy">
          <template #icon><IconShield /></template>
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
import UserAgreementModal from '@/components/common/UserAgreementModal.vue'
import PrivacyPolicyModal from '@/components/common/PrivacyPolicyModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ChangePasswordModal from '@/components/common/ChangePasswordModal.vue'
import ProfileEditModal from '@/components/common/ProfileEditModal.vue'
import SettingItem from '@/components/common/SettingItem.vue'
import Divider from '@/components/common/Divider.vue'
// 导入图标组件
import IconUser from '@/components/icons/IconUser.vue'
import IconLock from '@/components/icons/IconLock.vue'
import IconDeviceMobile from '@/components/icons/IconDeviceMobile.vue'
import IconDocument from '@/components/icons/IconDocument.vue'
import IconShield from '@/components/icons/IconShield.vue'
import IconLogout from '@/components/icons/IconLogout.vue'
import IconTrash from '@/components/icons/IconTrash.vue'

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
