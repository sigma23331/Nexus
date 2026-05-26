<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    @click.self="handleMaskClick"
  >
    <div class="bg-white rounded-2xl w-full max-w-md max-h-[90vh] overflow-y-auto shadow-xl">
      <div
        class="sticky top-0 bg-white border-b border-slate-100 px-5 py-4 flex justify-between items-center"
      >
        <h3 class="text-lg font-bold text-slate-800">完善资料</h3>
        <button @click="close(true)" class="text-slate-400 hover:text-slate-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <div class="p-5 space-y-5">
        <!-- 头像上传（仅文件选择，移除 URL 输入） -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">头像</label>
          <div class="flex items-center gap-4">
            <div class="relative">
              <img
                :src="avatarPreview || defaultAvatar"
                class="w-20 h-20 rounded-full object-cover border-2 border-slate-200"
              />
              <button
                type="button"
                @click="triggerFileInput"
                class="absolute bottom-0 right-0 bg-purple-600 rounded-full p-1 shadow-md hover:bg-purple-700"
              >
                <svg
                  class="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </button>
            </div>
            <div class="flex-1 text-xs text-slate-500">支持 JPG/PNG，建议正方形图片</div>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png"
            class="hidden"
            @change="handleFileSelect"
          />
        </div>

        <!-- 昵称（必填） -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">
            昵称 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="nickname"
            type="text"
            maxlength="20"
            placeholder="请填写昵称"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
            :class="{ 'border-red-500': nicknameError }"
          />
          <p v-if="nicknameError" class="text-xs text-red-500 mt-1">{{ nicknameError }}</p>
        </div>

        <!-- 生日 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">生日（选填）</label>
          <BirthdayPicker v-model="birthday" />
        </div>

        <!-- 性别 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">性别（选填）</label>
          <div class="flex gap-6">
            <label class="flex items-center gap-2">
              <input type="radio" value="male" v-model="gender" class="text-purple-600" />
              <span class="text-sm">男</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="radio" value="female" v-model="gender" class="text-purple-600" />
              <span class="text-sm">女</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="radio" value="secret" v-model="gender" class="text-purple-600" />
              <span class="text-sm">保密</span>
            </label>
          </div>
        </div>

        <p v-if="errorMsg" class="text-sm text-red-500 text-center">{{ errorMsg }}</p>
      </div>

      <div class="p-5 border-t border-slate-100 flex gap-3">
        <button
          @click="close(true)"
          class="flex-1 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition"
        >
          暂不完善
        </button>
        <button
          @click="submit"
          :disabled="submitting || !nickname.trim()"
          class="flex-1 py-2 rounded-xl bg-purple-600 text-white hover:bg-purple-700 transition disabled:opacity-50"
        >
          {{ submitting ? '保存中...' : '保存并继续' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { updateUserProfile } from '@/api/user'
import { useUserStore } from '@/stores/user'
import BirthdayPicker from '@/components/common/BirthdayPicker.vue'

interface ProfilePayload {
  nickname: string
  avatar?: string
  birthday?: string
  gender?: 'male' | 'female' | 'secret'
}

const emit = defineEmits<{
  (e: 'completed'): void
  (e: 'skipped'): void
}>()

const userStore = useUserStore()
const visible = ref(false)
const submitting = ref(false)
const errorMsg = ref('')

// 表单数据
const nickname = ref('')
const avatarPreview = ref('') // 仅用于预览，提交时直接从 file 转 base64
const birthday = ref('')
const gender = ref<'male' | 'female' | 'secret' | ''>('')
let selectedFileBase64: string | null = null // 存储待提交的 base64

const fileInput = ref<HTMLInputElement | null>(null)
const defaultAvatar = '/images/avatar.png'

// 昵称校验
const nicknameError = computed(() => {
  if (!nickname.value.trim()) return '昵称不能为空'
  if (nickname.value.trim().length > 20) return '昵称不能超过20个字符'
  return ''
})

// 将图片文件转为 base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const handleFileSelect = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    errorMsg.value = '请选择图片文件'
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    errorMsg.value = '图片大小不能超过 2MB'
    return
  }
  try {
    const base64 = await fileToBase64(file)
    selectedFileBase64 = base64
    avatarPreview.value = base64
    errorMsg.value = ''
  } catch {
    errorMsg.value = '图片读取失败'
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const open = () => {
  // 重置表单（不预填头像，因为头像需要用户主动选择）
  nickname.value = userStore.userInfo?.nickname || ''
  avatarPreview.value = ''
  selectedFileBase64 = null
  birthday.value = userStore.userInfo?.birthday?.split('T')[0] || ''
  gender.value = userStore.userInfo?.gender ?? ''
  errorMsg.value = ''
  visible.value = true
}

const close = (skip = true) => {
  visible.value = false
  if (skip) {
    emit('skipped')
  } else {
    emit('completed')
  }
}

const submit = async () => {
  if (nicknameError.value) {
    errorMsg.value = nicknameError.value
    return
  }
  submitting.value = true
  errorMsg.value = ''

  const payload: ProfilePayload = {
    nickname: nickname.value.trim(),
  }
  // 如果用户选择了新头像，则提交 base64
  if (selectedFileBase64) {
    payload.avatar = selectedFileBase64
  }
  if (birthday.value) payload.birthday = birthday.value
  if (gender.value) payload.gender = gender.value

  try {
    await updateUserProfile(payload)
    // 刷新 store 中的用户信息
    await userStore.fetchUserInfo()
    close(false)
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '保存失败，请重试'
    errorMsg.value = message
  } finally {
    submitting.value = false
  }
}

const handleMaskClick = () => {
  // 点击遮罩层不做任何操作，防止误关闭
}

defineExpose({ open })
</script>
