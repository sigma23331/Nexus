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
        <p><strong>更新时间：2026年5月24日</strong></p>
        <p><strong>生效时间：2026年5月24日</strong></p>

        <h4 class="font-semibold text-slate-800">欢迎您使用心运岛！</h4>
        <p>
          Nexus（以下简称“我们”）非常重视您的隐私和个人信息保护。本隐私政策适用于您通过任何方式对我们提供的<strong>心运岛服务</strong>的访问和使用。
        </p>
        <p>
          您可以通过心运岛（包括但不限于网站、WebApp、移动端小程序、PWA应用）获取心运岛产品和服务（以下统称“心运岛产品或服务”）。我们仅会处理（如收集、存储等）您使用产品或服务所需的必要个人信息。
        </p>
        <p>
          <strong
            >请您在使用心运岛产品或服务前仔细阅读并理解本隐私政策，尤其是字体加粗的内容，以便做出适当的选择。</strong
          >
        </p>

        <h4 class="font-semibold text-slate-800">1. 我们收集的信息及相应的使用目的</h4>
        <p>我们将遵循合法、正当、必要的原则，收集和使用您的个人信息。</p>

        <h5 class="font-semibold text-slate-700 mt-2">1.1 注册、登录账号</h5>
        <p>
          为使用心运岛的核心功能（如发布评论、收藏内容、生成运势卡片等），您需要通过手机号码注册或登录。当您注册或登录时，您需向我们提供您中华人民共和国境内的<strong>手机号码</strong>。您可以选择设置昵称、头像、生日、性别等信息。
        </p>
        <p>如果您仅浏览运势看板、使用答案之书等基础功能，您无需注册登录。</p>

        <h5 class="font-semibold text-slate-700 mt-2">1.2 心运岛产品功能</h5>
        <p>为提供服务，我们可能会收集以下信息：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>
            <strong>您主动提供或生成的内容</strong
            >：包括情绪日记、答案之书的提问、运势评论、收藏内容、分享记录等。
          </li>
          <li>
            <strong>设备信息</strong
            >：包括设备型号、操作系统版本、设备配置、IP地址、设备标识符等，用于保障服务安全和改善体验。
          </li>
          <li>
            <strong>日志信息</strong>：包括访问时间、使用时长、错误日志等，用于问题诊断和性能优化。
          </li>
          <li>
            <strong>地理位置</strong
            >：当您使用基于天气或地理位置的彩蛋机制时，我们需要获取您的<strong>地理位置</strong>，以便为您触发特定的回复风格或视觉主题。您可以通过设备设置关闭此权限。
          </li>
          <li>
            <strong>相册访问权限</strong
            >：当您上传头像、保存运势卡片或分享图片时，我们需要访问您的<strong>相册</strong>以读取或保存图片。您可以通过设备设置关闭此权限。
          </li>
        </ul>

        <h5 class="font-semibold text-slate-700 mt-2">1.3 情绪日记的特殊保护</h5>
        <p>
          <strong>情绪日记</strong
          >可能包含您的心情记录等较为敏感的信息。我们会对情绪日记内容进行加密存储，仅用于为您生成个人运势图谱和情绪复盘，不会用于任何其他目的。您可随时在“我的-情绪日记本”中查看、编辑或删除您的日记记录。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.4 答案之书与彩蛋机制</h5>
        <p>
          当您使用答案之书功能时，您输入的提问内容可能被用于优化AI模型，但我们会进行去标识化处理，确保无法追溯到您的个人身份。
        </p>
        <p>
          彩蛋机制（例如在雨天、深夜或特定节气触发特殊回复）需要收集您的<strong>设备时间</strong>和<strong>地理位置</strong>（您可拒绝提供位置，仅影响天气相关彩蛋）。这些信息仅用于判断彩蛋触发条件，不会保存或用于其他用途。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.5 树洞模块</h5>
        <p>
          <strong>树洞</strong
          >是心运岛内的一个轻量情绪宣泄入口。您在树洞中输入的内容<strong>不会被保存</strong>，我们不会存储、记录或分析您的任何输入；树洞的回答为预设的静态治愈短句，不调用任何API，也不会与您的账号关联。您可放心使用。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.6 分享广场内容审核</h5>
        <p>
          您在分享广场发布的评论、分享卡片等内容，我们会通过<strong>大模型API</strong>进行自动审核，以过滤违法违规、不良信息。审核仅针对内容本身，不会保存您的个人信息。您对自己发布的内容承担全部责任。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.7 PWA相关数据</h5>
        <p>
          当您将心运岛添加到手机主屏幕（PWA安装）后，我们可能会收集<strong>安装状态</strong>、<strong>使用频率</strong>等数据，用于改进PWA的兼容性和用户体验。这些数据不包含您的个人身份信息。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.8 保证服务安全、优化和改善服务</h5>
        <p>
          为了保障账号安全、预防欺诈行为、优化产品体验，我们会收集您的设备信息、日志信息及登录环境信息。
        </p>
        <p>
          在确保数据经过加密处理且无法追溯至具体个人身份的情况下，我们可能会将您与AI交互时输入的内容、发出的指令、AI生成的响应以及产品使用记录等数据用于模型训练和性能优化，以持续提升运势推荐和答案生成的个性化水平。<strong
            >若您不同意将您的数据用于模型训练，您可以通过本政策第8条的联系方式告知我们，我们将停止使用。</strong
          >
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.9 用户画像与个性化推荐</h5>
        <p>
          为了向您提供更符合您偏好的运势内容和答案推荐，我们可能会将您的使用行为信息（如情绪标签、答案偏好、分享行为等）进行汇聚融合，形成用户画像标签。基于这些标签，我们会为您优化运势看板、答案之书的展示内容。
        </p>
        <p>
          您有权关闭个性化推荐：您可以在“我的-设置-隐私与权限”中关闭“个性化推荐”开关。关闭后，我们将不再基于您的画像进行推荐，但您仍可正常使用产品的基础功能。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.10 消息通知</h5>
        <p>
          我们可能会通过浏览器通知向您发送每日运势提醒、活动通知或安全验证信息。您可以通过浏览器设置或“我的-设置-隐私与权限”关闭通知。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">1.11 事先征得授权同意的例外</h5>
        <p>在以下情形中，收集、使用个人信息无需事先征得您的授权同意：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>为订立、履行个人作为一方当事人的合同所必需；</li>
          <li>为履行法定职责或者法定义务所必需；</li>
          <li>为应对突发公共卫生事件，或者紧急情况下为保护自然人的生命健康和财产安全所必需；</li>
          <li>为公共利益实施新闻报道、舆论监督等行为，在合理的范围内处理个人信息；</li>
          <li>
            依照法律法规的规定在合理的范围内处理您自行公开的个人信息，或者其他已经合法公开的个人信息；
          </li>
          <li>法律、行政法规另有规定的情形。</li>
        </ul>

        <h4 class="font-semibold text-slate-800 mt-4">2. 我们如何使用 Cookie 和同类技术</h4>
        <p>
          当您使用心运岛时，我们会向您的设备发送一个或多个Cookie，用于记住您的偏好（如主题风格、语言），省去重复输入的步骤。您可根据自己的偏好管理或删除Cookie，但这可能影响您使用部分功能。
        </p>

        <h4 class="font-semibold text-slate-800 mt-4">
          3. 我们如何共享、转让、公开披露您的个人信息以及所接入的第三方SDK
        </h4>

        <h5 class="font-semibold text-slate-700 mt-2">3.1 共享</h5>
        <p>
          除非经过您本人事先单独同意或符合其他法律法规规定的情形，我们不会向第三方共享您的个人信息。
        </p>
        <p>在下列情况下，我们可能会与以下第三方共享您的个人信息：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>
            <strong>第三方SDK服务提供商</strong
            >：为了实现微信登录、分享功能，我们接入了微信开放平台SDK。具体请见本节“3.4
            我们所接入的第三方SDK”。
          </li>
          <li>
            <strong>法定情形下的共享</strong
            >：根据法律法规、诉讼、仲裁或行政、司法机关的要求，我们可能会共享您的个人信息。
          </li>
        </ul>

        <h5 class="font-semibold text-slate-700 mt-2">3.2 转让</h5>
        <p>我们不会将您的个人信息转让给任何公司、组织和个人，但以下情况除外：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>事先获得您的明确授权；</li>
          <li>满足法律法规、法律程序的要求或强制性的政府要求；</li>
          <li>
            如我们涉及合并、分立、清算、资产或业务的收购或出售等交易，您的个人信息有可能作为此类交易的一部分而被转移，我们将确保接收方继续受本隐私政策的约束。
          </li>
        </ul>

        <h5 class="font-semibold text-slate-700 mt-2">3.3 公开披露</h5>
        <p>我们仅会在以下情况下，公开披露您的个人信息：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>获得您的单独同意；</li>
          <li>基于法律法规、法律程序、诉讼或政府主管部门强制性要求下；</li>
          <li>对违规账号、违规行为进行处罚公告时，可能包含必要的账号信息（但会尽可能匿名化）。</li>
        </ul>

        <h5 class="font-semibold text-slate-700 mt-2">3.4 我们所接入的第三方SDK</h5>
        <p>
          我们仅接入了<strong>微信开放平台SDK</strong>，用于实现微信登录和分享卡片至微信。该SDK可能收集您的设备信息和微信账号信息（openid、昵称、头像），具体请参见微信的隐私政策：https://weixin.qq.com/cgi-bin/readtemplate?lang=zh_CN&t=weixin_agreement&s=privacy。
        </p>
        <p>
          <strong>我们未接入其他第三方统计、推送或内容审核SDK</strong
          >。内容审核通过大模型API完成，该API调用仅传输内容本身，不留存您的个人信息。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">3.5 共享、转让、公开披露的例外</h5>
        <p>在以下情形中，共享、转让、公开披露个人信息无需事先征得授权同意：</p>
        <ul class="list-disc pl-5 space-y-1">
          <li>为订立、履行个人作为一方当事人的合同所必需；</li>
          <li>为履行法定职责或者法定义务所必需；</li>
          <li>为应对突发公共卫生事件，或者紧急情况下为保护自然人的生命健康和财产安全所必需；</li>
          <li>为公共利益实施新闻报道、舆论监督等行为，在合理的范围内处理个人信息；</li>
          <li>
            依照法律法规的规定在合理的范围内处理您自行公开的个人信息，或者其他已经合法公开的个人信息；
          </li>
          <li>法律、行政法规另有规定的情形。</li>
        </ul>

        <h4 class="font-semibold text-slate-800 mt-4">4. 我们如何保存及保护您的个人信息</h4>

        <h5 class="font-semibold text-slate-700 mt-2">4.1 保存期限</h5>
        <p>
          我们将在提供服务所需的最短期限内保存您的个人信息。在您撤回同意、删除或注销账号期间，或者保存期限未届满时，我们会持续保留相关信息。超出保存期限后，我们将删除您的个人信息或进行匿名化处理。
        </p>
        <p>
          <strong>注销账号后的数据删除</strong
          >：当您注销心运岛账号时，您的情绪日记、收藏内容、历史运势记录等所有个人数据将被<strong>立即删除</strong>，无法恢复。法律法规另有规定的（如日志留存），我们会依法保留相应期限后删除。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">4.2 保存地域</h5>
        <p>
          我们在中华人民共和国境内收集和产生的个人信息，将存储在中华人民共和国境内。我们不会主动将您的个人信息转移至境外。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">4.3 安全措施</h5>
        <p>
          我们会采用加密技术、访问控制、安全审计等业界标准措施保护您的个人信息。我们会与员工签署保密协议，并定期进行安全培训。但请您理解，互联网环境并非绝对安全，我们无法保证信息百分之百安全。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">4.4 安全事件通知</h5>
        <p>
          一旦发生个人信息安全事件，我们将按照法律法规要求及时向您告知事件的基本情况、可能的影响以及我们已采取的处理措施，并主动上报监管部门。
        </p>

        <h4 class="font-semibold text-slate-800 mt-4">5. 您的权利</h4>
        <p>您对自己的个人信息享有以下权利：</p>

        <h5 class="font-semibold text-slate-700 mt-2">5.1 查阅权</h5>
        <p>
          您可以在“我的”页面查看您的昵称、头像、生日、性别等信息；在“我的-收藏”查看收藏的答案；在“我的-历史运势”查看历史运势记录。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">5.2 更正及补充权</h5>
        <p>您可以在“我的-修改个人信息”中自行更正或补充您的信息。</p>

        <h5 class="font-semibold text-slate-700 mt-2">5.3 删除权</h5>
        <p>
          您可以直接删除情绪日记、取消收藏等。此外，在以下情形中，您可联系我们要求删除您的个人信息：
        </p>
        <ul class="list-disc pl-5 space-y-1">
          <li>处理目的已实现、不再必要；</li>
          <li>我们已停止提供服务或保存期限已届满；</li>
          <li>您已撤回同意；</li>
          <li>我们违反法律法规或约定收集、使用您的信息。</li>
        </ul>

        <h5 class="font-semibold text-slate-700 mt-2">5.4 撤回同意权</h5>
        <p>
          您可以通过设备设置关闭地理位置、相册等权限，或在“我的-设置-隐私与权限”中关闭个性化推荐、消息通知等。您也可以通过注销账号的方式撤回全部同意。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">5.5 注销账号权</h5>
        <p>
          您可以在“我的-设置”中申请注销账号。注销是不可逆的，注销后您的所有个人数据将被立即删除。请谨慎操作。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">5.6 复制权和可携带权</h5>
        <p>
          您有权联系我们获取您的个人信息副本。在技术可行的前提下，您也可以要求我们将信息转移至您指定的其他主体。
        </p>

        <h5 class="font-semibold text-slate-700 mt-2">5.7 获得解释的权利</h5>
        <p>您有权要求我们就个人信息处理规则作出解释。您可以通过第8条的联系方式与我们沟通。</p>

        <h5 class="font-semibold text-slate-700 mt-2">5.8 响应您的请求</h5>
        <p>
          为保障安全，我们可能会要求您验证身份后再处理您的请求。我们将在15个工作日内做出答复。对于无端重复、需要过多技术手段的请求，我们可能会予以拒绝。
        </p>

        <h4 class="font-semibold text-slate-800 mt-4">6. 我们如何处理未成年人的个人信息</h4>
        <p>
          我们的产品和服务主要面向成年人。如您是未满14周岁的未成年人，在使用心运岛前，应请您的父母或其他监护人仔细阅读本隐私政策，并在征得监护人同意的前提下使用我们的服务。如果我们发现在未获监护人同意的情况下收集了未成年人的个人信息，我们将尽快删除。
        </p>

        <h4 class="font-semibold text-slate-800 mt-4">7. 本隐私政策的更新</h4>
        <p>
          我们可能适时修订本政策。对于重大变更，我们会通过产品页面公告、站内信或电子邮件等方式通知您。若您不同意变更，请立即停止使用心运岛。
        </p>
        <p>
          重大变更包括但不限于：服务模式重大变化、所有权结构变化、信息共享对象变化、您的权利行使方式变化等。
        </p>

        <h4 class="font-semibold text-slate-800 mt-4">8. 如何联系我们</h4>
        <p>
          如果您对本隐私政策有任何疑问、意见或建议，或发现您的个人信息可能被泄露，您可以通过以下方式与我们联系：
        </p>
        <ul class="list-disc pl-5 space-y-1">
          <li>发送邮件至：<strong>2370262693@qq.com</strong></li>
          <li>或通过心运岛内的“我的-设置-帮助与反馈”提交问题</li>
        </ul>
        <p>
          我们将在15个工作日内回复。如果您对我们的回复不满意，您还可以向有关政府部门投诉或向有管辖权的人民法院提起诉讼。
        </p>

        <p class="text-xs text-slate-400 mt-4">Nexus<br />更新日期：2026年5月24日</p>
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
