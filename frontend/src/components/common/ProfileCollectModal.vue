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
        <!-- 头像上传（自动裁剪压缩） -->
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
                :disabled="isProcessing"
                class="absolute bottom-0 right-0 bg-purple-600 rounded-full p-1 shadow-md hover:bg-purple-700 disabled:bg-gray-400"
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
            <div class="flex-1 text-xs text-slate-500">
              支持 JPG/PNG，自动裁剪为正方形并压缩至合适大小
            </div>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png"
            class="hidden"
            @change="handleFileSelect"
          />
          <div v-if="isProcessing" class="text-xs text-purple-600 mt-2 text-center">
            处理图片中，请稍候...
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">
            昵称 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="nickname"
            type="text"
            maxlength="15"
            placeholder="请填写昵称"
            class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400/60"
            :class="{ 'border-red-500': nicknameError }"
          />
          <p v-if="nicknameError" class="text-xs text-red-500 mt-1">{{ nicknameError }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">生日（选填）</label>
          <BirthdayPicker v-model="birthday" />
        </div>

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
          :disabled="submitting || !nickname.trim() || isProcessing"
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
const isProcessing = ref(false)

const nickname = ref('')
const avatarPreview = ref('')
const birthday = ref('')
const gender = ref<'male' | 'female' | 'secret' | ''>('')
let compressedBase64: string | null = null

const fileInput = ref<HTMLInputElement | null>(null)
const defaultAvatar = '/images/avatar.png'

const nicknameError = computed(() => {
  if (!nickname.value.trim()) return '昵称不能为空'
  if (nickname.value.trim().length > 15) return '昵称不能超过15个字符'
  return ''
})

/**
 * 将图片文件压缩为 80-150KB 的正方形 JPEG Base64
 * @param file 原始图片文件
 * @returns Promise<string> Base64 字符串
 */
const compressAndCropToSquare = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const size = Math.min(img.width, img.height)
        const sx = (img.width - size) / 2
        const sy = (img.height - size) / 2

        const targetSize = 512
        const canvas = document.createElement('canvas')
        canvas.width = targetSize
        canvas.height = targetSize
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('无法创建 canvas 上下文'))
          return
        }
        ctx.drawImage(img, sx, sy, size, size, 0, 0, targetSize, targetSize)

        let quality = 0.9
        let resultBase64 = ''
        const minSizeKB = 80
        const maxSizeKB = 150
        for (let attempt = 0; attempt < 6; attempt++) {
          resultBase64 = canvas.toDataURL('image/jpeg', quality)
          const fileSizeKB = Math.round((resultBase64.length * 0.75) / 1024)
          if (fileSizeKB >= minSizeKB && fileSizeKB <= maxSizeKB) {
            break
          }
          if (fileSizeKB > maxSizeKB) {
            quality -= 0.15
          } else {
            quality += 0.1
          }
          quality = Math.min(0.95, Math.max(0.3, quality))
        }
        resolve(resultBase64)
      }
      img.onerror = () => reject(new Error('图片加载失败'))
      img.src = e.target?.result as string
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
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

  const MAX_RAW_SIZE = 4 * 1024 * 1024
  if (file.size > MAX_RAW_SIZE) {
    errorMsg.value = '图片不能超过 4MB，请选择较小的图片'
    return
  }

  isProcessing.value = true
  errorMsg.value = ''
  try {
    const base64 = await compressAndCropToSquare(file)
    compressedBase64 = base64
    avatarPreview.value = base64
    const compressedKB = Math.round((base64.length * 0.75) / 1024)
    console.log(`图片已压缩为 ${compressedKB} KB`)
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : '图片处理失败'
    errorMsg.value = message
    compressedBase64 = null
    avatarPreview.value = ''
  } finally {
    isProcessing.value = false
    if (input) input.value = ''
  }
}

const triggerFileInput = () => {
  if (isProcessing.value) return
  fileInput.value?.click()
}

const open = () => {
  nickname.value = userStore.userInfo?.nickname || ''
  avatarPreview.value = ''
  compressedBase64 = null
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
  if (compressedBase64) {
    payload.avatar = compressedBase64
  }
  if (birthday.value) payload.birthday = birthday.value
  if (gender.value) payload.gender = gender.value

  try {
    await updateUserProfile(payload)
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
