# Frontend

## 环境要求（需手动确认/配置）

- Node.js >= **18.18.0**

## 配置说明（无需手动确认/配置）

| 依赖             | 版本    |
| ---------------- | ------- |
| **Vue**          | 3.5.32  |
| **Vite**         | 5.4.21  |
| **TypeScript**   | 5.9.3   |
| **Tailwind CSS** | 3.4.19  |
| Vue Router       | 4.6.4   |
| Pinia            | 3.0.4   |
| Axios            | 1.15.1  |
| ECharts          | 6.0.0   |
| html2canvas      | 1.4.1   |
| dayjs            | 1.11.20 |

## 快速开始（开发）

```bash
# 1. 进入前端项目目录
cd frontend

# 2. 安装依赖
npm ci
# 安装后出现六条警告，忽略
# 同时注意：使用 npm audit fix 而不带 --force（重点！会影响到版本配置同步）
# 千万不要使用 npm install

# 3. 启动开发服务器
npm run dev
# 该命令在终端上保持运行，修改前端页面可实现热更新
# 同时注意：不要一边开着 npm run dev，一边随意点击陌生链接

# 4.退出
Ctrl + C -> Y

# 生产构建： 输出 dist 目录
npm run build
# 生产构建： 执行预览
npm run preview

# 前端代码规范
# 检查是否有错误（frontend）
npm run lint
# 格式化所有代码（frontend）
npm run format
```

## 组织架构（同步修改）

```txt
frontend/
│
├── .gitignore                      # Git 忽略文件（node_modules, dist, .env.local 等）
├── .prettierignore                 # Prettier 忽略文件
├── .prettierrc                     # Prettier 配置（代码格式化规则）
├── eslint.config.js                # ESLint 扁平配置（代码检查规则）
├── index.html                      # HTML 入口（Vite 自动注入脚本）
├── package.json                    # 项目依赖与脚本
├── package-lock.json               # 依赖锁版本（必须提交）
├── postcss.config.js               # PostCSS 配置（引入 Tailwind）
├── README.md                       # 项目说明文档
├── tailwind.config.js              # Tailwind CSS 配置（content 路径、主题扩展）
├── tsconfig.json                   # TypeScript 配置（路径别名、严格模式等）
├── tsconfig.node.json              # Node 环境 TS 配置（用于 vite.config.ts，可选）
├── vite.config.ts                  # Vite 配置（插件、代理、路径别名）
│
├── public/                         # 静态资源目录（不经过构建，直接复制到 dist）
│   ├── icons/
│   │   ├── icon-192.png            # PWA 图标 192x192
│   │   └── icon-512.png            # PWA 图标 512x512
│   ├── images/
│   │   ├── login_top.png           # 登陆文字
│   │   ├── login_top2.png          # 登陆文字
│   │   ├── card_fortune.png        # 运势卡片模板
│   │   └── card_answer.png         # 答案卡片模板
│   ├── offline.html                # 离线占位页
│   ├── manifest.json               # Web App Manifest
│   └── favicon.ico                 # 网站图标
│
└── src/
    ├── api/                        # API 请求模块（按业务划分）
    │   ├── auth.ts                 # 认证相关（登录、验证码、绑定手机号）
    │   ├── fortune.ts              # 运势模块接口
    │   ├── answer.ts               # 答案之书接口
    │   ├── plaza.ts                # 广场卡片接口
    │   ├── user.ts                 # 用户信息、日记、收藏等
    │   └── types.ts                # API 相关的 TypeScript 类型（从契约生成）
    │
    ├── assets/                     # 静态资源（图片、字体、全局样式）
    │   ├── images/                 # 图片文件
    │   └── fonts/                  # 字体文件
    │
    ├── components/                 # 公共组件（可复用 UI 单元）
    │   ├── common/                 # 通用组件（按钮、输入框、弹窗、加载动画）
    │   │   ├── UserAgreementModal.vue  # 用户协议弹窗
    │   │   ├── PrivacyPolicyModal.vue  # 隐私政策弹窗
    │   │   ├── SettingModal.vue        # 设置弹窗
    │   │   ├── PromptModal.vue         # 自定义输入弹窗（修改昵称等）
    │   │   └── ConfirmModal.vue        # 自定义确认弹窗（退出/切换/注销）
    |   |
    │   ├── layout/                 # 布局组件（TabBar、Header、安全区容器）
    │   └── business/               # 业务组件（运势卡片、答案卡片、日记条目等）
    │       ├── DiaryDetailModal.vue    # 日记详情弹窗
    │       ├── MonthlyMoodOverview.vue # 月度情绪概览（日历）
    │       ├── MoodDiaryForm.vue       # 情绪日记表单
    │       └── MoodDiaryModal.vue      # 情绪日记弹窗（含表单）
    │
    ├── composables/                # 组合式函数（封装可复用的响应式逻辑）
    │   ├── useAuth.ts              # 登录、token 管理
    │   ├── useFortune.ts           # 获取运势、轨迹等
    │   ├── useAnswer.ts            # 提问、历史、收藏
    │   ├── usePlaza.ts             # 广场卡片加载、点赞
    │   └── useCardGenerator.ts     # 卡片生成
    │
    ├── config/
    │   └── typography.ts           # 字体样式配置文件
    │
    ├── layouts/                    # 布局模板（可选，App.vue 已包含主布局）
    │   └── DefaultLayout.vue       # 含 TabBar 和路由视口的布局（若需要复杂布局）
    │
    ├── router/                     # 路由配置
    │   └── index.ts                # 创建路由实例，定义各页面路由
    │
    ├── stores/                     # Pinia 状态管理
    │   ├── user.ts                 # 用户信息、token
    │   ├── fortune.ts              # 今日运势、轨迹
    │   ├── answer.ts               # 当前答案、历史列表
    │   ├── plaza.ts                # 广场卡片列表、分页游标
    │   └── index.ts                # 统一导出（可选）
    │
    ├── types/                      # 全局 TypeScript 类型定义
    │   ├── api.d.ts                # API 响应类型（可自动生成）
    │   ├── models.d.ts             # 数据模型（User, Fortune, Answer, Diary, PlazaCard）
    │   └── global.d.ts             # 全局类型扩展（如环境变量）
    │
    ├── utils/                      # 工具函数
    │   ├── request.ts              # Axios 封装（拦截器、错误处理）
    │   ├── storage.ts              # 本地存储封装（token、用户偏好）
    │   ├── format.ts               # 日期格式化、运势分数映射等
    │   ├── validator.ts            # 表单校验（手机号、密码等）
    │   └── cardGenerator.ts        # 卡片生成核心逻辑
    │
    ├── views/                      # 页面级组件（按路由划分）
    │   ├── fortune/                # 运势看板模块
    │   │   ├── FortuneView.vue     # 主页面
    │   │   └── components/         # 该页面私有组件
    │   ├── answer/                 # 答案之书模块
    │   │   ├── AnswerView.vue
    │   │   └── components/
    │   ├── plaza/                  # 分享广场模块
    │   │   ├── PlazaView.vue
    │   │   └── components/
    │   │       └── PlazaCard.vue   # 卡片组件（支持点赞、时间格式化等）
    │   ├── profile/                # 我的页面模块
    │   │   ├── ProfileView.vue
    │   │   └── components/
    │   └── auth/                   # 认证相关页面
    │       ├── LoginView.vue       # 登录
    │       ├── RegisterView.vue    # 注册
    │       └── BindPhoneView.vue   # 绑定手机号（可选）
    │
    ├── App.vue                     # 根组件（包含路由视图和 TabBar 控制）
    ├── main.ts                     # 入口文件（挂载 Pinia、Router、全局样式）
    ├── style.css                   # 全局样式（Tailwind 指令）
    └── vite-env.d.ts               # Vite 环境类型声明（CSS 模块、图片模块等）
```

## 关键设计说明

1. **API 层** (`api/`)
   - 按业务模块拆分，每个文件导出对应的请求函数（如 `login(phone, code)`）。
   - 统一使用封装好的 `request` 实例，不直接在组件中调用 `axios`。

2. **状态管理** (`stores/`)
   - Pinia 存储全局数据，例如用户 token、今日运势、历史答案列表。
   - 避免在组件中重复请求同一数据，通过 store 的 `actions` 调用 API 并更新 state。

3. **组合式函数** (`composables/`)
   - 封装带有响应式状态和逻辑的复用单元，例如 `useFortune` 内部可调用 API 并返回 `ref` 数据，供多个组件共享。
   - 与 Pinia 分工：Pinia 用于跨组件共享的**全局状态**；composables 用于封装**非持久化**或特定页面的逻辑。

4. **组件划分**
   - `components/common/`：与业务无关的通用 UI（按钮、输入框、模态框）。
   - `components/business/`：跨页面使用的业务组件（如运势卡片、答案卡片）。
   - `views/*/components/`：仅属于某个页面的私有组件，避免全局污染。

5. **类型安全**
   - `types/` 下定义所有数据模型，与 `API.md` 契约保持一致。
   - API 响应类型可直接从后端契约生成（如使用 `openapi-typescript`），或手动定义。

6. **工具函数**
   - `request.ts` 包含请求/响应拦截器，自动处理 token 注入、错误码跳转等。
   - `storage.ts` 封装 `localStorage` 读写，用于存储 token 和用户偏好。

7. **路由与布局**
   - 默认使用 `App.vue` 作为根布局，内部包含 `<router-view>` 和 `<TabBar>`。
   - 若需要无 TabBar 的页面（如登录页），可通过路由 `meta` 控制 TabBar 显隐。
