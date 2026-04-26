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
        <h3 class="text-lg font-bold text-slate-800 text-center">用户协议</h3>
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
        <p><strong>欢迎使用心运岛！</strong></p>
        <p>
          <i>Nexus</i
          >（以下简称“我们”）依据本协议为用户（以下简称“你”）提供<i>心运岛</i>服务。本协议对你和我们均具有法律约束力。
        </p>

        <h4 class="font-semibold text-slate-800">一、本服务的功能</h4>
        <p>
          你可以使用本服务每日/每周运势看板（覆盖爱情、事业等维度，支持多流派切换与AI个性化文案）、智能答案之书（摇机或点击获取哲思回复，并融入彩蛋与情绪感知）、情绪日记与个人中心（记录心情、生成运势图谱实现自我复盘），以及低压力社交分享（生成精美卡片、设置分享广场与全站情绪可视化）。
        </p>

        <h4 class="font-semibold text-slate-800">二、账号注册</h4>
        <p>
          1.
          您应当具备中华人民共和国法律规定的与您行为相适应的民事行为能力，确保您能够独立承担法律责任。
        </p>
        <p>2. 您应提供真实、准确、完整的注册信息，不得冒用他人身份或使用虚假信息。</p>

        <h4 class="font-semibold text-slate-800">三、用户行为规范</h4>
        <p>1. 您在使用心运岛服务时，应遵守国家法律法规，不得利用本服务从事违法违规行为。</p>
        <p>2. 您不得发布、传播任何含有色情、暴力、恐怖、赌博、诈骗等违法信息的内容。</p>
        <p>3. 您应对通过心运岛发布的内容承担全部责任，我们有权对违规内容进行删除。</p>

        <h4 class="font-semibold text-slate-800">四、责任范围及限制</h4>
        <p>
          你使用本服务得到的结果仅供参考，实际情况以官方为准。我们不对因不可抗力、技术故障、第三方原因导致的服务中断或数据丢失承担责任。
        </p>

        <h4 class="font-semibold text-slate-800">五、服务变更与终止</h4>
        <p>1. 我们有权根据实际情况调整、暂停或终止部分或全部服务，并会提前通知您。</p>
        <p>2. 如您违反本协议，我们有权立即终止您的账号使用权限。</p>

        <h4 class="font-semibold text-slate-800">六、隐私保护</h4>
        <p>
          我们重视对你隐私的保护，你的个人隐私信息将根据《隐私政策》受到保护与规范，详情请参阅《隐私政策》。
        </p>

        <h4 class="font-semibold text-slate-800">七、其他条款</h4>
        <p>
          7.1 本协议所有条款的标题仅为阅读方便，本身并无实际涵义，不能作为本协议涵义解释的依据。
        </p>
        <p>7.2 本协议条款无论因何种原因部分无效或不可执行，其余条款仍有效，对双方具有约束力。</p>
        <p>7.3 本协议的任何条款无论因何种原因无效，其余条款仍应有效且具有约束力。</p>
        <p>7.4 本协议的最终解释权归心运岛所有。</p>

        <p class="text-xs text-slate-400 mt-2">更新日期：2026年4月26日</p>
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
