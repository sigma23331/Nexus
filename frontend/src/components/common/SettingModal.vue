<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex justify-end" @click.self="close">
    <!-- 遮罩层：半透明 + 毛玻璃 -->
    <div class="fixed inset-0 bg-black/30 backdrop-blur-sm" @click="close"></div>

    <!-- 右侧面板 -->
    <div
      class="relative w-80 h-full bg-white/95 shadow-2xl shadow-purple-500/10 flex flex-col rounded-l-2xl animate-slide-in-right"
    >
      <div class="flex justify-between items-center px-5 py-4 border-b border-purple-100">
        <h3 class="text-lg font-bold text-purple-800">设置</h3>
        <button
          @click="close"
          class="text-slate-400 hover:text-purple-500 transition text-2xl leading-none"
        >
          &times;
        </button>
      </div>

      <div class="flex-1 overflow-y-auto divide-y divide-purple-100">
        <!-- 合并后的修改个人信息 -->
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="openProfileEdit"
        >
          <span class="text-slate-700 hover:text-purple-700">修改个人信息</span>
          <span class="text-purple-400">›</span>
        </div>

        <!-- 修改密码 -->
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="changePassword"
        >
          <span class="text-slate-700 hover:text-purple-700">修改密码</span>
          <span class="text-purple-400">›</span>
        </div>

        <!-- 添加到主屏幕 -->
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="handleInstallToDesktop"
        >
          <span class="text-slate-700 hover:text-purple-700">添加到主屏幕</span>
          <span class="text-purple-400">›</span>
        </div>

        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="handleLogout"
        >
          <span class="text-slate-700 hover:text-purple-700">退出登录</span>
          <span class="text-purple-400">›</span>
        </div>

        <!-- 注销账号 -->
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-rose-50/80 transition duration-150"
          @click="handleDeleteAccount"
        >
          <span class="text-rose-600">注销账号</span>
          <span class="text-rose-300">›</span>
        </div>

        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="openAgreement"
        >
          <span class="text-slate-700 hover:text-purple-700">用户协议</span>
          <span class="text-purple-400">›</span>
        </div>

        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="openPrivacy"
        >
          <span class="text-slate-700 hover:text-purple-700">隐私政策</span>
          <span class="text-purple-400">›</span>
        </div>
      </div>
    </div>

    <!-- 弹窗组件 -->
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
import UserAgreementModal from './UserAgreementModal.vue'
import PrivacyPolicyModal from './PrivacyPolicyModal.vue'
import ConfirmModal from './ConfirmModal.vue'
import ChangePasswordModal from './ChangePasswordModal.vue'
import ProfileEditModal from './ProfileEditModal.vue'

const router = useRouter()
const userStore = useUserStore()
const visible = ref(false)

const userAgreementModalRef = ref<InstanceType<typeof UserAgreementModal> | null>(null)
const privacyPolicyModalRef = ref<InstanceType<typeof PrivacyPolicyModal> | null>(null)
const confirmModalRef = ref<InstanceType<typeof ConfirmModal> | null>(null)
const changePasswordModalRef = ref<InstanceType<typeof ChangePasswordModal> | null>(null)
const profileEditModalRef = ref<InstanceType<typeof ProfileEditModal> | null>(null)

const open = () => {
  visible.value = true
}
const close = () => {
  visible.value = false
}

// 打开个人信息编辑弹窗
const openProfileEdit = () => {
  profileEditModalRef.value?.open()
  // 不关闭设置面板，让用户编辑完成后自行关闭
}

// 修改密码
const changePassword = async () => {
  const success = await changePasswordModalRef.value?.open()
  if (success) {
    // 密码修改成功，可做额外操作
  }
}

// 添加到主屏幕
const handleInstallToDesktop = () => {
  window.dispatchEvent(new CustomEvent('manual-install-trigger'))
}

// 退出登录
const handleLogout = async () => {
  const confirmed = await confirmModalRef.value?.open({
    title: '退出登录',
    message: '确定要退出登录吗？',
  })
  if (confirmed) {
    userStore.logout()
    router.replace('/login')
    close()
  }
}

// 注销账号
const handleDeleteAccount = async () => {
  const confirmed = await confirmModalRef.value?.open({
    title: '注销账号',
    message: '⚠️ 注销账号将永久删除所有数据，不可恢复。确定要继续吗？',
  })
  if (confirmed) {
    // 调用后端注销接口（需后端提供）
    // await deleteAccount()
    userStore.logout()
    localStorage.clear()
    router.replace('/login')
    close()
  }
}

const openAgreement = () => userAgreementModalRef.value?.open()
const openPrivacy = () => privacyPolicyModalRef.value?.open()

defineExpose({ open, close })
</script>

<style scoped>
.animate-slide-in-right {
  animation: slideInRight 0.3s ease-out;
}
@keyframes slideInRight {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}
</style>
