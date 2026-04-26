
# 心运岛 Alpha 版本 API 接口契约 (v1.0)

## 1. 通用说明

- **Base URL**: `https://api.xinyundao.com/v1` (根据实际环境替换，开发环境可替换为 Mock 地址)
- **Content-Type**: `application/json`
- **认证方式**: 请求头携带 `Authorization: Bearer {token}`（通过登录接口获得，支持手机号/账密两种方式，微信方式预留）
- **时间格式**: 所有时间字段统一使用 **ISO 8601** 格式（UTC），如 `2026-04-18T10:30:00Z`
- **分页规范**:
  - 传统分页 (`page` + `limit`) 响应格式:
    ```json
    {
      "total": 100,
      "page": 1,
      "limit": 10,
      "list": [...]
    }
    ```
  - 游标分页 (`cursor` + `limit`) 响应格式:
    ```json
    {
      "list": [...],
      "nextCursor": "base64encoded_cursor",
      "hasMore": true
    }
    ```

### 标准响应格式

```json
{
  "code": 200,        // 200:成功, 401:鉴权失败, 403:禁止访问, 400:请求参数错误, 429:限流, 500:服务器错误
  "message": "描述信息",
  "data": null        // 具体返回数据
}
```

### 错误响应示例

```json
// 400 参数错误
{
  "code": 400,
  "message": "question 字段不能为空",
  "data": null
}

// 401 未登录 / Token 失效
{
  "code": 401,
  "message": "Token 已过期，请重新登录",
  "data": null
}

// 403 无权限
{
  "code": 403,
  "message": "无权删除他人的日记",
  "data": null
}

// 404 资源不存在
{
  "code": 404,
  "message": "日记不存在",
  "data": null
}

// 429 限流
{
  "code": 429,
  "message": "请求过于频繁，请稍后再试",
  "data": null
}
```

### 枚举定义

- **MoodType**: `happy` | `calm` | `sad` | `angry` | `tired` (情绪日记标签)
- **CardType**: `fortune` | `answer` (广场卡片来源类型)
- **AnswerStyle**: `philosophical` | `humor` (答案风格偏好)
- **PreferredFeature**: `mood_diary` | `fortune` | `answer` (用户最常用功能)
- **ActiveHourBucket**: `morning` | `afternoon` | `night` (用户活跃时段)

### 限流策略（未定）

| 接口 | 限流规则 |
| ------ | ---------- |
| `/answer/ask` | 同一用户每分钟最多 5 次 |

超出限制时返回 `429`，响应头包含 `Retry-After: 60`（秒）。

---

## 2. 用户认证 (Auth)

> 主要登录/注册方式为**手机号 + 短信验证码**，账密方式作为辅助（可选），微信方式暂不实现但预留接口。  
> 所有方式成功后均返回相同的 `token` 和用户信息，后续请求携带 `Authorization: Bearer {token}`。

---

### 2.1 账密方式（辅助）

> 可作为备选登录方式，但本次开发以手机号为主，账密方式可暂缓实现。

#### 2.1.1 注册（账密）

- **接口**: `POST /auth/password/register`
- **入参**:
  ```json
  {
    "username": "user123",        // required, 4-20字符，字母数字下划线
    "password": "password123",    // required, 6-20字符
    "nickname": "苏木"            // optional, 1-20字符，默认 username
  }
  ```
- **返回 data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userInfo": {
      "uid": "10086",
      "nickname": "苏木",
      "avatar": "https://api.xinyundao.com/default_avatar.png"
    }
  }
  ```
- **错误**:
  - 400: 用户名已存在 / 参数格式错误
  - 500: 服务器错误

#### 2.1.2 登录（账密）

- **接口**: `POST /auth/password/login`
- **入参**:
  ```json
  {
    "username": "user123",   // required
    "password": "password123" // required
  }
  ```
- **返回 data**: 同 2.1.1 返回结构
- **错误**: 401 用户名或密码错误

---

### 2.2 手机号方式（主要）

> 本次开发的核心登录/注册方式，使用短信验证码，手机号未注册时自动创建账号。  
> 同时支持**已登录用户绑定手机号及换绑手机号**。

#### 2.2.1 发送短信验证码

- **接口**: `POST /auth/sms/send`
- **入参**:
  ```json
  {
    "phone": "13800138000"   // required, 中国大陆手机号
  }
  ```
- **返回 data**: `{ "success": true, "expiresIn": 300 }` (验证码有效期5分钟)
- **错误**:
  - 400: 手机号格式错误
  - 429: 发送频率过高（同一手机号每分钟1次，每天5次）

#### 2.2.2 登录 / 注册（手机号验证码）

- **接口**: `POST /auth/sms/login`
- **说明**: 手机号未注册时自动创建新用户，昵称默认为 "用户"+手机号后4位。
- **入参**:
  ```json
  {
    "phone": "13800138000",   // required
    "code": "123456"          // required, 6位数字
  }
  ```
- **返回 data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userInfo": {
      "uid": "10086",
      "nickname": "用户3800",
      "avatar": "https://api.xinyundao.com/default_avatar.png"
    },
    "isNewUser": true   // 是否新注册用户
  }
  ```
- **错误**:
  - 400: 验证码错误或过期
  - 429: 尝试次数过多

#### 2.2.3 绑定发送验证码（需登录）

- **接口**: `POST /auth/sms/bind/send`
- **说明**: 已登录用户请求绑定手机号前，先发送验证码到目标手机号。同一用户未绑定手机号时可绑定；若已绑定，则为更换手机号（需验证原手机号？本次简化为直接覆盖，但需确保新手机号未被其他用户绑定）。
- **请求头**: `Authorization: Bearer {token}`
- **入参**:
  ```json
  {
    "phone": "13900139000"   // required, 要绑定的新手机号
  }
  ```
- **返回 data**: 
  
   ```json
  {
    "success": true, 
    "expiresIn": 300          // 验证码有效期（s）
  }
  ```

- **错误**:
  - 400: 手机号格式错误 或 该手机号已被其他用户绑定
  - 401: token 无效
  - 429: 发送频率过高

#### 2.2.4 确认绑定手机号（需登录）

- **接口**: `POST /auth/sms/bind/confirm`
- **说明**: 使用验证码确认绑定，将当前登录用户的账号与手机号关联。若用户此前无手机号，则绑定；若已有手机号，则更新为新手机号（前提是新手机号未被占用）。
- **请求头**: `Authorization: Bearer {token}`
- **入参**:
  ```json
  {
    "phone": "13900139000",   // required, 与发送验证码时一致
    "code": "123456"          // required, 6位数字
  }
  ```
- **返回 data**:
  ```json
  {
    "success": true,
    "message": "手机号绑定成功"
  }
  ```
- **错误**:
  - 400: 验证码错误或过期 / 手机号已被其他用户绑定
  - 401: token 无效
  - 404: 未找到对应的验证码记录

#### 接口解读
*   **2.2.1 / 2.2.2** 是给**游客/未登录用户**用的，用于直接通过手机号进入系统。
*   **2.2.3 / 2.2.4** 是给**已经登录的用户**用的（请求头必须带 `token`）。
    *   **应用场景**：用户使用其他方式登录，要求补全手机号；或者用户想要更换目前绑定的手机号。
##### 2.2.3 绑定发送验证码 (`POST /auth/sms/bind/send`)
这个接口是预检和下发动作：
1.  **鉴权要求**：必须在 `Header` 里带上 `Authorization: Bearer {token}`。没有登录的人调不动这个接口。
2.  **唯一性校验**：后端在发短信前会先查库。如果这个手机号 `139...` 已经被**另一个 UID** 绑定了，直接报 `400` 错误（手机号已被占用），不会发短信。
3.  **防刷机制**：同样受到每天 5 次、每分钟 1 次的频率限制。
4.  **后端动作**：生成临时验证记录（如6位数字），存入缓存（如 Redis），并调用短信网关发给用户手机。此时数据库里的用户信息还没有任何变化。

##### 2.2.4 确认绑定手机号 (`POST /auth/sms/bind/confirm`)
这个接口是落库动作：
1.  **逻辑闭环**：前端提交：刚才收验证码的手机号 + 6位验证码。
2.  **后端处理**：
    *   **验证验证码**：检查验证码是否匹配且未过期。
    *   **覆盖逻辑**：
        *   如果该用户 UID 之前**没有**手机号，则直接写入。
        *   如果该用户 UID 之前**已经有**手机号，则用新号**覆盖旧号**（实现换绑）。
3.  **结果**：一旦成功，该用户的 `userInfo` 模型里，`phone` 字段就不再为 `null`。

---

*   **手机号索引**：
    *   在数据库设计时，手机号字段（`phone`）必须是 `Unique Index`（唯一索引）。

*   **业务逻辑冲突处理**：
    *   如果一个用户用 A 手机号登录了（产生 UID 1），尝试去绑定已经注册过、正在被 UID 2 使用的 B 手机号，系统必须拒绝，否则会导致两个 UID 指向同一个手机号的逻辑混乱。

---

### 2.3 微信方式（预留）

> 本次开发**暂不实现**，仅预留接口结构供后续扩展。  
> 适用于 Web App 在任意浏览器中，跳转至微信 App 授权后返回。

#### 2.3.1 获取微信授权链接（前端步骤）

- 无需后端接口，前端构造跳转链接:
  ```
  https://open.weixin.qq.com/connect/qrconnect?appid=APPID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=snsapi_login&state=STATE#wechat_redirect
  ```

#### 2.3.2 登录 / 注册（微信 code）—— 预留接口

- **接口**: `POST /auth/wechat/login`（暂不实现，返回 501）
- **入参**:
  ```json
  {
    "code": "071abc123def456..."   // required, 微信授权码
  }
  ```
- **预期返回 data**（设计参考）:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userInfo": {
      "uid": "10086",
      "nickname": "微信昵称",
      "avatar": "https://thirdwx.qlogo.cn/..."
    },
    "isNewUser": false
  }
  ```
- **当前状态**: 接口未实现，调用将返回 `501 Not Implemented`。

---

### 2.4 通用接口

#### 2.4.1 验证 token 有效性

- **接口**: `GET /auth/verify`
- **请求头**: `Authorization: Bearer {token}`
- **返回 data** (200):
  ```json
  {
    "valid": true,
    "userInfo": {
      "uid": "10086",
      "nickname": "用户3800",
      "avatar": "https://api.xinyundao.com/default_avatar.png",
      "phone": "13800138000"   // 已绑定的手机号，未绑定时为 null
    }
  }
  ```
  若 token 无效则返回 `401`。

#### 2.4.2 登出

- **接口**: `POST /auth/logout`
- **请求头**: `Authorization: Bearer {token}`
- **返回 data**:
  ```json
  {
    "id": "f_20260418_10086",    // 运势唯一ID (便于分享或追溯)
    "date": "2026-04-18",       // 运势所属日期，格式YYYY-MM-DD 
    "score": 88,                // 整数，0-100
    "title": "大吉 · 宜行",     // 1-20字符
    "content": "今日星象汇聚在你的心灵宫位，适合开启新计划。",  // 1-200字符
    "yi": ["深度睡眠", "整理书桌", "远程问候"],  // 数组，最多5个
    "ji": ["过度熬夜", "重体力劳动", "争论"],   // 数组，最多5个
    "luckyColor": null,          // 可选，幸运颜色
    "luckyDirection": null       // 可选，幸运方向
  }
  ```
  > 前端清除本地 token 即可，后端可选实现黑名单机制。

### 补充说明

- **手机号为主**: 本次开发需实现 `2.2.1`、`2.2.2` 以及绑定手机号相关接口 `2.2.3`、`2.2.4`；账密和微信可暂不实现，但保留接口定义。
- **绑定手机号逻辑**:
  - 用户必须已登录。
  - 一个手机号只能绑定一个用户。
  - 如果用户已绑定手机号，调用绑定接口将替换原手机号（需确保新手机号未被占用）。此设计简化了更换流程，后续可扩展原手机号验证。
- **密码安全**: 若实现账密登录，后端需对密码进行哈希存储（如 bcrypt）。
- **短信验证码**: 建议使用腾讯云、阿里云等短信服务，验证码有效期5分钟，同一手机号登录失败次数限制（如每小时最多5次）。
- **账号关联**: 后续可扩展“绑定微信”等功能，本次不做要求。

---

## 3. 运势模块 (Fortune)

### 3.1 获取今日运势

- **接口**: `GET /fortune/today`
- **对应任务**: 运势看板主页展示
- **返回 data**:
  ```json
  {
    "id": "f_20260418_10086",    // 运势唯一ID (便于分享或追溯)
    "date": "2026-04-18",       // 运势所属日期，格式YYYY-MM-DD 
    // summary
    "score": 88,                // 整数，0-100
    "title": "大吉 · 宜行",     // 1-20字符
    "content": "今日星象汇聚在你的心灵宫位，适合开启新计划。",  // 1-200字符
    // dailyGuide
    "yi": ["深度睡眠", "整理书桌", "远程问候"],  // 数组，最多5个
    "ji": ["过度熬夜", "重体力劳动", "争论"]    // 数组，最多5个
  }
  ```

### 3.2 获取运势轨迹 (最近7天)

- **接口**: `GET /fortune/trend`
- **对应任务**: 运势看板中的 ECharts 曲线图
- **返回 data**:
  
  ```json
  {
    "trendPoints": [
      { "date": "04-12", "value": 72 },   // date: MM-dd 格式，value: 整数0-100
      { "date": "04-13", "value": 65 },
      { "date": "04-14", "value": 80 },
      { "date": "04-15", "value": 92 },
      { "date": "04-16", "value": 75 },
      { "date": "04-17", "value": 85 },
      { "date": "04-18", "value": 88 }
    ]
  }
  ```

### 3.3 获取全站运势统计 (今日)

- **接口**: `GET /fortune/stats/global`
- **说明**: 获取今日全站所有用户的运势汇总数据。
- **返回 data**:
  
  ```json
  {
    "date": "2026-04-18",       // 运势所属日期，格式YYYY-MM-DD
    "averageScore": 76.5,         // 全站平均分
    "topTitle": "大吉 · 宜行",    // 占比最高的运势文案
    "topTitleRatio": 0.32,        // 占比比例 (0.32 代表 32%)
    "totalParticipants": 1250     // 今日已生成运势的总人数 (可选)
  }
  ```

---

## 4. 答案之书模块 (Answer)

### 4.1 提交提问并抽取答案

- **接口**: `POST /answer/ask`
- **入参**:
  ```json
  {
    "question": "这周面试能过吗？"   // required, string, 1-200字符
  }
  ```
- **返回 data**:
  ```json
  {
    "id": "ans_1002",               // 答案记录唯一ID
    "question": "这周面试能过吗？",
    "answerText": "现在不是犹豫的时候，全心投入。",  // 1-100字符
    "createdAt": "2026-04-10T00:00:00Z" 
  }
  ```

### 4.2 获取历史提问记录

- **接口**: `GET /answer/history`
- **查询参数**:
  - `page`: integer, ≥1, 默认 1
  - `limit`: integer, 1-50, 默认 10
- **返回 data** (传统分页格式):
  ```json
  {
    "total": 25,
    "page": 1,
    "limit": 10,
    "list": [
      {
        "id": "1",
        "question": "该辞职吗？",
        "answerText": "寻找新的起点。",
        "createdAt": "2026-04-10T00:00:00Z",
        "isFavorited": true
      },
      {
        "id": "2",
        "question": "要不要去旅行？",
        "answerText": "最好的风景就在脚下",
        "createdAt": "2026-04-08T12:30:00Z",
        "isFavorited": false
      }
    ]
  }
  ```

### 4.3 收藏 / 取消收藏答案

- **接口**: `POST /answer/favorite`
- **说明**: 收藏某个答案后，该记录将永久保留并在个人中心的“答案收藏库”展示。
- **入参**:
  
  ```json
  {
    "answerId": "ans_1002",           // 必填，答案记录ID
    "action": "favorite"              // 枚举值: favorite (收藏) | unfavorite (取消)
  }
  ```

- **返回 data**:
  
  ```json
  {
    "answerId": "ans_1002",
    "isFavorited": true               // 当前最新的收藏状态
  }
  ```

---

## 5. 分享广场模块 (Plaza)

### 5.1 获取广场卡片列表（瀑布流，游标分页）

- **接口**: `GET /plaza/cards`
- **查询参数**:
  - `tab`: `hot` (按点赞数降序) 或 `latest` (按创建时间降序)，默认 `latest`
  - `cursor`: 游标字符串，首次请求不传，后续传返回的 `nextCursor`
  - `limit`: integer, 1-20, 默认 10
- **返回 data** (游标分页格式):
  
  ```json
  {
    "list": [
      {
        "cardId": "uuid_789",
        "type": "answer",          // fortune 或 answer
        "owner": {
          "uid": "10086",
          "nickname": "林深时见鹿",
          "avatar": "https://img.com/u.jpg"
        },
        "snapshotUrl": "https://img.com/card_v1.png",
        "content": "有时候不回答也是一种回答。",   // 可选，1-100字符
        "stats": {
          "likes": 24,
          "isLiked": false
        },
        "createdAt": "2026-04-18T10:30:00Z"
      }
    ],
    "nextCursor": "base64encoded_cursor",
    "hasMore": true
  }
  ```

### 5.2 发布一张分享卡片

- **接口**: `POST /plaza/card`
- **入参**:
  
  ```json
  {
    "type": "answer",               // required, fortune 或 answer
    "sourceId": "ans_1002",         // required, 答案ID 或 运势日期(yyyy-mm-dd)
    "snapshotUrl": "https://img.com/card_v1.png",  // required, 有效图片URL
    "content": "有时候不回答也是一种回答。",       // optional, 1-100字符
    "tags": ["成长", "解忧"]         // optional, 最多3个，每个1-10字符
  }
  ```

- **返回 data**: 新创建的卡片对象 (同 5.1 中的卡片结构)
- **错误**:
  - 400: 参数校验失败（如 `snapshotUrl` 不是有效图片格式）
  - 429: 超出每小时发布限制

### 5.3 点赞 / 取消点赞卡片

- **接口**: `POST /plaza/like`
- **幂等性**: 重复 `like` 不会增加点赞数，返回当前状态；`unlike` 同理。
- **入参**:
  
  ```json
  {
    "cardId": "uuid_789",    // required
    "action": "like"         // required, 枚举: like | unlike
  }
  ```

- **返回 data**:
  
  ```json
  {
    "cardId": "uuid_789",
    "likes": 25,
    "isLiked": true
  }
  ```

---

## 6. 用户模块 (User) – 我的页面

### 6.1 获取个人中心概览

- **接口**: `GET /user/profile`
- **说明**: 返回用户信息、统计数据及 AI 绘制的用户画像（`profile`）。每次调用会检查画像冷却时间（默认 1 小时），过期则异步通过 LLM 自动更新情绪倾向、兴趣主题、个人情景。
- **返回 data**:
  ```json
  {
    "userInfo": {
      "uid": "10086",
      "nickname": "苏木 Salami",
      "avatar": "https://img.com/u.jpg"
    },
    "stats": {
      "diaryCount": 24,
      "answerCollected": 15,
      "plazaPostCount": 3
    },
    "profile": {
      "answer_style": null,
      "topic_interests": ["career", "health"],
      "self_context_tag": "日常",
      "mood_tendency": "optimistic",
      "preferred_feature": "fortune",
      "active_hour_bucket": "morning",
      "personalization_enabled": true
    }
  }
  ```

  `profile` 字段说明：

  | 字段 | 类型 | 说明 | 更新方式 |
  |------|------|------|----------|
  | `answer_style` | enum \| null | 答案风格偏好：`philosophical` / `humor`，目前由用户显式设定 | 用户手动 |
  | `topic_interests` | string[] | 兴趣标签，如 `["career","health","love"]`，由 AI 分析日记内容 + 提问记录生成 | AI 冷却触发 |
  | `self_context_tag` | string \| null | 用户当前生活情景，如"备考期"、"职场新人"，由 AI 推断 | AI 冷却触发 |
  | `mood_tendency` | string \| null | 情绪倾向，如 `optimistic` / `calm` / `anxious`，由 AI 分析日记 mood_tag + 内容生成 | AI 冷却触发 |
  | `preferred_feature` | enum \| null | 最常用功能：`mood_diary` / `fortune` / `answer`，由各模块使用频次统计 | 写入时触发 |
  | `active_hour_bucket` | enum \| null | 活跃时段：`morning` / `afternoon` / `night`，由行为时间分布统计 | 写入时触发 |
  | `personalization_enabled` | boolean | 是否启用个性化推荐，默认 `true` | 用户手动 |

### 6.2 获取历史运势记录
- **接口**: `GET /user/history/fortune`
- **查询参数**:
  - `page`: integer, 默认 1
  - `limit`: integer, 默认 10
- **返回 data** (传统分页格式):
  ```json
  {
    "total": 30,
    "page": 1,
    "limit": 10,
    "list": [
      {
        "date": "2026-04-18",
        "score": 88,
        "title": "大吉 · 宜行",
      },
      {
        "date": "2026-04-17",
        "score": 85,
        "title": "小吉 · 守成",
      }
    ]
  }
  ```

### 6.3 获取历史收藏答案
- **接口**: `GET /user/history/favorites`
- **说明**: 获取用户主动点击“收藏”的答案之书记录。
- **查询参数**:
  - `page`: integer, 默认 1
  - `limit`: integer, 默认 10
- **返回 data** (传统分页格式):
  ```json
  {
    "total": 15,
    "page": 1,
    "limit": 10,
    "list": [
      {
        "id": "ans_1002",
        "question": "下周的项目会顺利吗？",
        "answerText": "现在的努力终将获得回报。",
        "createdAt": "2026-04-15T14:20:00Z"
      },
      {
        "id": "ans_985",
        "question": "要不要去吃火锅？",
        "answerText": "这取决于你当下的心情，随心而动。",
        "createdAt": "2026-04-12T18:30:00Z"
      }
    ]
  }
  ```

### 6.4 保存情绪日记
- **接口**: `POST /diary/entry`
- **入参**:
  ```json
  {
    "moodTag": "happy",          // MoodType 枚举
    "content": "今天在公园看到了一只白色的流浪猫，很治愈。",
    "isPublic": false            // 默认 false
  }
  ```
- **返回 data**:
  ```json
  {
    "id": "diary_101",
    "createdAt": "2026-04-18T10:30:00Z"
  }
  ```

### 6.5 获取月度情绪日记
- **接口**: `GET /diary/timeline`
- **查询参数**:
  - `page`: integer, 默认 1
  - `limit`: integer, 默认 10
  - `yearMonth`: 可选，格式 `YYYY-MM`
- **返回 data**:
  ```json
  {
    "totalDays": 24,
    "page": 1,
    "limit": 10,
    "list": [
      {
        "id": "diary_101",
        "date": "2026-04-18",
        "weekday": "Friday",
        "moodTag": "happy",
        "snippet": "今天在公园看到了一只白色的流浪猫..."
      }
    ]
  }
  ```

### 6.6 获取单条日记详情
- **接口**: `GET /diary/entry/{id}`
- **返回 data**:
  ```json
  {
    "id": "diary_101",
    "moodTag": "happy",
    "content": "今天在公园看到了一只白色的流浪猫，很治愈。",
    "createdAt": "2026-04-18T10:30:00Z"
  }
  ```

### 6.7 更新日记
- **接口**: `PUT /diary/entry/{id}`
- **入参**: 同 6.4 (全部可选)
- **返回 data**: 更新后的完整日记对象

### 6.8 删除日记
- **接口**: `DELETE /diary/entry/{id}`
- **返回 data**: `{ "success": true }`

---

## 7. 错误码完整列表

| code | 含义                 | 典型场景                                 |
|------|----------------------|------------------------------------------|
| 200  | 成功                 | -                                        |
| 400  | 参数错误             | 缺少必填字段、字段超长、枚举值非法等       |
| 401  | Token 无效或过期      | 未登录、token 过期、token 格式错误        |
| 403  | 无权限操作           | 删除他人日记、修改他人卡片等              |
| 404  | 资源不存在           | 日记 ID 不存在、卡片 ID 不存在            |
| 429  | 请求过于频繁（限流）  | 超过接口调用频率限制，响应头带 Retry-After |
| 500  | 服务器内部错误       | 数据库连接失败等         |

---

## 8. 数据模型汇总（字段约束）

| 模型 | 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|------|
| **FortuneResponse** | id | string | 是 | 唯一识别码 |
| | date | string | 是 | YYYY-MM-DD |
| | score | integer | 是 | 0-100 整数 |
| | title | string | 是 | 1-20字符 |
| | content | string | 是 | 1-200字符 |
| | luckyColor | string | 否 | 1-20字符 |
| | luckyDirection | string | 否 | 1-20字符 |
| | yi | array | 是 | string 数组，最多5个 |
| | ji | array | 是 | string 数组，最多5个 |
| **AnswerRequest** | question | string | 是 | 1-200字符 |
| **AnswerResponse** | id | string | 是 | 唯一识别码 (ans_xxx) |
| | question | string | 是 | 1-200字符 |
| | answerText | string | 是 | 1-100字符 |
| | isFavorited | boolean | 否 | 仅在历史/收藏列表接口返回 |
| | createdAt | ISO8601 | 是 | - |
| **DiaryEntry** | id | string | 是 | - |
| | moodTag | enum | 是 | happy, calm, sad, angry, tired |
| | content | string | 是 | 1-2000字符 |
| | createdAt | ISO8601 | 是 | - |
| **PlazaCard** | cardId | string | 是 | - |
| | type | enum | 是 | fortune, answer |
| | owner | object | 是 | 包含 uid, nickname, avatar |
| | snapshotUrl | url | 是 | https 图片链接 |
| | stats | object | 是 | likes, isLiked |
| | createdAt | ISO8601 | 是 | - |
| **UserProfile** | answer_style | enum | 否 | philosophical, humor |
| | topic_interests | array | 否 | string 数组，最长20字符/项 |
| | self_context_tag | string | 否 | 最多20字 |
| | mood_tendency | string | 否 | 最多50字符 |
| | preferred_feature | enum | 否 | mood_diary, fortune, answer |
| | active_hour_bucket | enum | 否 | morning, afternoon, night |
| | personalization_enabled | boolean | 是 | 默认 true |

---

## 9. Mock 建议

前端可在 `src/mocks` 目录下按以下结构存放 JSON 文件，使用 Mock.js 或直接静态数据：

```
src/mocks/
  auth_wechat.json          // POST /auth/wechat 响应
  fortune_today.json
  fortune_trend.json
  answer_ask.json
  answer_history_page1.json
  plaza_cards_hot_page1.json
  plaza_cards_latest_page1.json
  user_profile.json
  history_fortune_page1.json
  diary_timeline_page1.json
  diary_entry_detail.json
```

建议配合 `vite-plugin-mock` 或类似工具实现拦截。

---

## 10. 扩展性与版本兼容说明

- 当前版本为 `v1`，URL 前缀 `/v1/` 保持不变。
- 后续新增字段时，应保持向后兼容（不删除已有字段，新增字段可选）。
- 废弃字段将在文档中标记 `deprecated`，并在至少一个大版本后移除。
- 如需破坏性变更，将发布 `v2` 版本，并保留 `v1` 一段时间。

---