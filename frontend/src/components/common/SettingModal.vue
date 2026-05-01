<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex justify-end" @click.self="close">
    <!-- 遮罩层：半透明 + 毛玻璃 -->
    <div class="fixed inset-0 bg-black/30 backdrop-blur-sm" @click="close"></div>

    <!-- 右侧面板：柔和渐变边框 + 半透明白色背景 -->
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
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="changeAvatar"
        >
          <span class="text-slate-700 hover:text-purple-700">修改头像</span>
          <span class="text-purple-400">›</span>
        </div>
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="changeNickname"
        >
          <span class="text-slate-700 hover:text-purple-700">修改昵称</span>
          <span class="text-purple-400">›</span>
        </div>
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="handleLogout"
        >
          <span class="text-slate-700 hover:text-purple-700">退出登录</span>
          <span class="text-purple-400">›</span>
        </div>
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-purple-50/80 transition duration-150"
          @click="handleSwitchAccount"
        >
          <span class="text-slate-700 hover:text-purple-700">切换账号</span>
          <span class="text-purple-400">›</span>
        </div>
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

    <!-- 隐藏文件上传 -->
    <input
      type="file"
      ref="fileInput"
      accept="image/*"
      style="display: none"
      @change="onFileChange"
    />

    <!-- 弹窗组件 -->
    <UserAgreementModal ref="userAgreementModalRef" />
    <PrivacyPolicyModal ref="privacyPolicyModalRef" />
    <PromptModal ref="promptModalRef" />
    <ConfirmModal ref="confirmModalRef" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { updateUserProfile } from '@/api/user'
import UserAgreementModal from './UserAgreementModal.vue'
import PrivacyPolicyModal from './PrivacyPolicyModal.vue'
import PromptModal from './PromptModal.vue'
import ConfirmModal from './ConfirmModal.vue'

const router = useRouter()
const userStore = useUserStore()
const visible = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const userAgreementModalRef = ref<InstanceType<typeof UserAgreementModal> | null>(null)
const privacyPolicyModalRef = ref<InstanceType<typeof PrivacyPolicyModal> | null>(null)
const promptModalRef = ref<InstanceType<typeof PromptModal> | null>(null)
const confirmModalRef = ref<InstanceType<typeof ConfirmModal> | null>(null)

const open = () => {
  visible.value = true
}
const close = () => {
  visible.value = false
}

// 修改头像
const changeAvatar = () => fileInput.value?.click()
const onFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  const reader = new FileReader()
  reader.onload = async (e) => {
    const avatarBase64 = e.target?.result as string
    try {
      await updateUserProfile({ avatar: avatarBase64 })
      const current = userStore.userInfo
      if (current) {
        userStore.setUserInfo({ ...current, avatar: avatarBase64 })
      }
      close()
    } catch {
      alert('头像更新失败，请重试')
    }
  }
  reader.readAsDataURL(file)
}

// 修改昵称（使用自定义输入弹窗）
const changeNickname = async () => {
  const newNick = await promptModalRef.value?.open({
    title: '修改昵称',
    message: '请输入新的昵称',
    placeholder: '昵称',
    defaultValue: userStore.userInfo?.nickname || '',
  })
  if (newNick && newNick.trim()) {
    try {
      await updateUserProfile({ nickname: newNick.trim() })
      const current = userStore.userInfo
      if (current) {
        userStore.setUserInfo({ ...current, nickname: newNick.trim() })
      }
      close()
    } catch {
      alert('昵称更新失败，请重试')
    }
  }
}

// 退出登录（使用自定义确认弹窗）
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

// 切换账号
const handleSwitchAccount = async () => {
  const confirmed = await confirmModalRef.value?.open({
    title: '切换账号',
    message: '切换账号将退出当前登录，确定吗？',
  })
  if (confirmed) {
    userStore.logout()
    router.replace('/login')
    close()
  }
}

// 注销账号（危险操作）
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
