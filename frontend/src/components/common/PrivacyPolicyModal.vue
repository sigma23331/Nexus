<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
    @click.self="close"
  >
    <div
      class="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl flex flex-col max-h-[80vh]"
    >
      <!-- 头部 -->
      <div class="relative px-6 py-4 border-b border-slate-100">
        <h3 class="text-lg font-bold text-slate-800 text-center">隐私政策</h3>
        <button
          @click="close"
          class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-2xl leading-none"
          aria-label="关闭"
        >
          &times;
        </button>
      </div>

      <!-- 内容区域（滚动） -->
      <div class="px-6 py-4 overflow-y-auto text-sm text-slate-700 space-y-4">
        <div>更新日期：<strong>2026/4/26</strong></div>
        <div>生效日期：<strong>2026/4/26</strong></div>

        <h4 class="font-semibold text-slate-800">导言</h4>
        <p>
          <i>心运岛</i> 是一款由 <i>Nexus</i> （以下简称“我们”）提供的产品。
          您在使用我们的服务时，我们可能会收集和使用您的相关信息。我们希望通过本《隐私政策》向您说明，在使用我们的服务时，我们如何收集、使用、储存和分享这些信息，以及我们为您提供的访问、更新、控制和保护这些信息的方式。
        </p>
        <p>
          <strong
            >您使用或继续使用我们的服务，即意味着同意我们按照本《隐私政策》收集、使用、储存和分享您的相关信息。</strong
          >
        </p>
        <p>
          如对本《隐私政策》或相关事宜有任何问题，请通过
          <strong>2370262693@qq.com</strong> 与我们联系。
        </p>

        <h4 class="font-semibold text-slate-800">1. 我们收集的信息</h4>
        <p>我们或我们的第三方合作伙伴提供服务时，可能会收集、储存和使用下列与您有关的信息：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li><strong>个人信息</strong>：电话号码、电子邮件等。</li>
          <li><strong>日志信息</strong>：设备信息、浏览信息、点击信息等。</li>
        </ul>
        <p>我们接入的第三方SDK：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>微信开放平台 SDK：用于微信登录，收集微信 openid、昵称、头像。</li>
          <li>阿里云短信服务 SDK：用于发送短信验证码，收集手机号码。</li>
        </ul>

        <h4 class="font-semibold text-slate-800">2. 信息的存储</h4>
        <p>
          我们会通过安全的方式存储您的信息，境内收集的信息存储于中国境内。服务停止运营时，我们会及时删除您的个人信息。
        </p>

        <h4 class="font-semibold text-slate-800">3. 信息安全</h4>
        <p>我们使用加密技术保护您的个人信息，但请您理解，任何安全措施都无法做到100%安全。</p>

        <h4 class="font-semibold text-slate-800">4. 我们如何使用信息</h4>
        <p>用于提供服务、身份验证、安全防范、改善产品、个性化推荐等。</p>

        <h4 class="font-semibold text-slate-800">5. 信息共享</h4>
        <p>我们不会主动共享您的个人信息给第三方，除非获得您的明确同意或法律法规要求。</p>

        <h4 class="font-semibold text-slate-800">6. 您的权利</h4>
        <p>您有权查询、更正、删除您的个人信息，也可以注销账户。</p>

        <h4 class="font-semibold text-slate-800">7. 变更</h4>
        <p>本政策可能适时修订，若您继续使用服务即视为同意更新后的政策。</p>

        <h4 class="font-semibold text-slate-800">8. 未成年人保护</h4>
        <p>未满18岁的未成年人需在监护人指导下使用服务。</p>

        <p class="text-xs text-slate-400">更新日期：2026年4月26日</p>
      </div>

      <!-- 底部按钮 -->
      <div class="px-6 py-4 border-t border-slate-100">
        <button
          @click="close"
          class="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2.5 rounded-xl transition"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)

const open = () => {
  visible.value = true
}

const close = () => {
  visible.value = false
}

defineExpose({ open, close })
</script>
