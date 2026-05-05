
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

> 核心登录/注册方式为**手机号 + 短信验证码**（2.2），同时提供**昵称 + 密码**的辅助注册方式（2.1）。  
> 所有方式成功后均返回相同的 `token` 与用户信息，后续请求需携带 `Authorization: Bearer {token}`。

---

### 2.1 昵称密码方式（辅助）

> 无需手机号或短信验证码，用户直接通过 **昵称 + 密码** 完成注册与登录。  
> 昵称全局唯一，手机号可选；已注册用户后续可通过 2.2.4 绑定手机号。

#### 2.1.1 注册（昵称 + 密码）

- **接口**: `POST /auth/register/nickname`
- **说明**: 不含手机号，纯昵称注册；注册后可通过 2.2.5 绑定手机号。
- **入参**:
  ```json
  {
    "nickname": "苏木",       // required, 1-20字符，全局唯一
    "password": "password123" // required, 6-20字符
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
    },
    "isNewUser": true
  }
  ```
- **错误**:
  - 400：昵称已被占用 / 参数格式错误
  - 500：服务器错误

#### 2.1.2 登录（手机号 / 昵称 + 密码）

- **接口**: `POST /auth/password/login`
- **说明**: 同时支持手机号或昵称作为登录凭据。传入 `account` 字段时，系统自动识别；也可继续使用旧版 `phone` 字段。
- **入参**:
  ```json
  // 推荐方式（account 自动识别）
  {
    "account": "苏木",          // 手机号或昵称，required（与 phone 二选一）
    "password": "password123"
  }
  ```
  或
  ```json
  // 向后兼容（仅手机号）
  {
    "phone": "13800138000",
    "password": "password123"
  }
  ```
- **返回 data**: 同 2.1.1 返回结构（`isNewUser` 固定为 `false`）
- **错误**:
  - 400：账号或密码错误 / 账号未设置密码 / 参数缺失
  - 500：服务器错误

---

### 2.2 手机号方式（主要）

> 通过短信验证码进行登录或注册（自动创建账号），并支持已登录用户绑定/换绑手机号。

#### 2.2.1 发送短信验证码

- **接口**: `POST /auth/sms/send`
- **说明**: 根据手机号是否已注册，自动标记为“登录”或“注册”场景；同一手机号 60 秒内只能发送一次。
- **入参**:
  ```json
  {
    "phone": "13800138000"   // required, 中国大陆手机号
  }
  ```
- **返回 data**: 
  ```json
  {
    "success": true,
    "expiresIn": 300          // 验证码有效期 5 分钟（秒）
  }
  ```
- **错误**:
  - 400：手机号格式错误
  - 429：发送频率过高（60 秒内重复请求）

#### 2.2.2 登录 / 注册（短信验证码，无密码）

- **接口**: `POST /auth/sms/login`
- **说明**: 验证码核验通过后，若手机号未注册则自动创建用户，昵称默认为 “用户”+手机号后4位（若重复则追加序号）；已注册则直接登录。**不设置密码**。
- **入参**:
  ```json
  {
    "phone": "13800138000",   // required
    "code": "123456"          // required, 6位数字验证码
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
    "isNewUser": true          // 是否新注册
  }
  ```
- **错误**:
  - 400：验证码错误或过期 / 未找到验证码记录
  - 500：服务器错误

#### 2.2.3 手机号 + 验证码 + 密码注册（设置密码）

- **接口**: `POST /auth/register`
- **说明**: 在短信验证码基础上，额外设置密码；适用于希望保留密码登录能力的用户。昵称默认规则同 2.2.2。
- **入参**:
  ```json
  {
    "phone": "13800138000",
    "code": "123456",
    "password": "password123"  // required, 6-20字符
  }
  ```
- **返回 data**: 同 2.2.2 （`isNewUser` 为 `true`）
- **错误**:
  - 400：手机号已注册 / 验证码错误或过期 / 密码格式错误
  - 500：服务器错误

#### 2.2.4 绑定手机号 · 发送验证码（需登录）

- **接口**: `POST /auth/sms/bind/send`
- **说明**: 已登录用户绑定新的手机号（或换绑），先发送验证码到目标号码。若目标号码已被其他用户占用，直接拒绝。
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
    "expiresIn": 300
  }
  ```
- **错误**:
  - 400：手机号已被其他用户绑定 / 手机号格式错误
  - 401：token 无效
  - 429：发送频率过高

#### 2.2.5 确认绑定手机号（需登录）

- **接口**: `POST /auth/sms/bind/confirm`
- **说明**: 验证码确认后，将当前用户账号与手机号绑定。若用户已有手机号，则用新号覆盖旧号（换绑），前提是新号未被占用。
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
    "success": true
  }
  ```
- **错误**:
  - 400：验证码错误或过期 / 手机号已被其他用户占用
  - 401：token 无效
  - 404：未找到验证码记录

---

### 2.3 通用接口

#### 2.3.1 验证 Token 有效性

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
      "phone": "13800138000"    // 未绑定时为 null
    }
  }
  ```
  token 无效或用户不存在时返回 `401`。

#### 2.3.2 登出

- **接口**: `POST /auth/logout`
- **请求头**: `Authorization: Bearer {token}`
- **返回 data**:
  ```json
  {
      "success": true
  }
  ```
#### 补充说明
- 昵称唯一性： nickname 字段全局唯一，自动生成的默认昵称若冲突会自动追加序号。
- 手机号可为空： 通过昵称注册的用户 phone 字段为 null，可通过 2.2.5 绑定。 
- 密码安全： 所有密码均经 bcrypt 哈希后存储，登录时自动校验。 
- 验证码存储： 当前为内存模拟，生产环境需迁移至 Redis，并确保有效期 5 分钟。
- 绑定逻辑： 
  - 用户必须已登录（携带 token）。 
  - 一个手机号只能绑定一个用户，绑定前校验唯一性。 
  - 若用户已有手机号，绑定新号将直接覆盖（换绑），无需验证旧号。 
- 微信登录： 暂未实现，预留 wechat_openid / wechat_unionid 字段。

---

## 3. 运势模块 (Fortune)

### 3.1 获取今日运势

- **接口**: `GET /fortune/today`
- **对应任务**: 运势看板主页展示
- **返回 data**:
  ```json
  {
    "id": "f_20260418_10086",
    "date": "2026-04-18",
    "score": 88,
    "title": "大吉 · 宜行/上上签",                      // 签文等级
    "content_main": "风起云开，顺遂自来",   // 签文主旨
    "content_sub": "今日宜稳中求进，心静则通达", // 签文解读
    "yi": ["喝奶茶", "摸鱼五分钟"],
    "ji": ["熬夜", "已读不回"],
    "love": "中上",
    "career": "平稳",
    "health": "注意作息",
    "wealth": "谨慎消费"
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

### 6.9 修改头像
- **接口**: `PUT /user/profile/avatar`
- **说明**: 更新当前用户的头像URL
- **请求体 (JSON)**: 
  ```json
    {
  "avatar": "https://example.com/avatars/user123.jpg"
    }
  ```
- **返回data**：
  ```json
    {
    "code": 200,
    "message": "头像更新成功",
    "data": {
     "avatar": "https://example.com/avatars/user123.jpg"
     }
    }
  ```
- **错误响应**：
  - 400 缺少参数或URL格式错误: {"code": 400, "message": "缺少 avatar 参数", "data": null}
  - 404 用户不存在: {"code": 404, "message": "用户不存在", "data": null}


### 6.10 修改昵称
- **接口**: `PUT /user/profile/nickname`
- **说明**: 更新当前用户的昵称，全局唯一且长度1-20字符
- **请求体 (JSON)**: 
  ```json
    {
        "nickname": "心韵旅人"
    }
  ```
- **返回data**：
  ```json
    {
  "code": 200,
  "message": "昵称更新成功",
  "data": {
    "nickname": "心韵旅人"
    }
  }
  ```
- **错误响应**：
  - 400 长度不符: {"code": 400, "message": "昵称长度必须在1-20个字符之间", "data": null}
  - 409 昵称重复: {"code": 409, "message": "该昵称已被使用，请更换", "data": null}
  - 404 用户不存在: {"code": 404, "message": "用户不存在", "data": null}

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
| **FortuneToday** | id | string | 是 | 唯一识别码 |
| | date | string | 是 | YYYY-MM-DD |
| | score | integer | 是 | 0-100 整数 |
| | title | string | 是 | 签文等级，1-20字符，如“上上签” |
| | content_main | string | 是 | 签文主旨，1-200字符，如“风起云开，顺遂自来” |
| | content_sub | string | 是 | 签文解读，1-200字符，如“今日宜稳中求进，心静则通达” |
| | yi | array | 是 | string 数组，最多5个，代表“宜”的事项 |
| | ji | array | 是 | string 数组，最多5个，代表“忌”的事项 |
| | love | string | 否 | 爱情运势描述，1-20字符 |
| | career | string | 否 | 事业运势描述，1-20字符 |
| | health | string | 否 | 健康运势描述，1-20字符 |
| | wealth | string | 否 | 财富运势描述，1-20字符 |
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

## 11. 后端本地开发环境启动指南
前端开发人员需要运行后端 API 服务以便联调。以下步骤使用 **Docker Compose** 一键启动所有依赖。

### 11.1 环境要求

- Docker Desktop (>= 20.10)
- Docker Compose (>= 2.0)
- 至少 4GB 可用内存

### 11.2 启动步骤
- 创建 .env 文件，复制并修改.env.example，去除.example后缀
- 可以使用如下命令构建并启动
   ```bash
    docker-compose up -d --build
  ```
- 初始化数据库（仅首次）
  ```bash
  \# 运行迁移脚本创建表
  docker-compose exec backend flask db upgrade

  \# 如果提示 "No such command 'db'"，则先初始化：
  docker-compose exec backend flask db init
  docker-compose exec backend flask db migrate -m "init"
  docker-compose exec backend flask db upgrade

  ```
- 验证服务是否正常
  - 健康检查：访问 http://localhost:5000/health 应返回 {"status":"healthy","database":"connected"}
### 11.3 常用命令
以下是常用的命令，均需在项目根目录（docker-compose.yml 所在目录）执行。
```bash
# ---- 容器管理 ----

# 查看所有容器状态（运行中/停止）
docker-compose ps

# 查看后端实时日志（可看到打印的短信验证码、SQL 语句）
docker-compose logs -f backend

# 重启后端服务（修改 Python 代码后生效，因为挂载了源码卷）
docker-compose restart backend

# 重新构建镜像并启动（当依赖包变更或 Dockerfile 修改时）
docker-compose up -d --build

# 停止并移除所有容器（保留数据库数据）
docker-compose down

# 停止并清除数据库数据卷（全部数据将丢失）
docker-compose down -v

# ---- 数据库操作 ----

# 进入 PostgreSQL 命令行（手动查看/修改数据）
docker-compose exec db psql -U nexus_user -d nexus_db

# 执行数据库迁移（当拉取代码后模型有变更时）
docker-compose exec backend flask db upgrade

# 生成新的迁移文件（通常由后端开发执行，前端一般不需要）
docker-compose exec backend flask db migrate -m "变更描述"

# ---- 进入容器内部 ----

# 进入后端容器 Shell
docker-compose exec backend sh

# 在容器内可执行任意命令，如：
#   - flask routes              查看所有注册的接口
#   - python -m pytest           运行测试（如果有）
#   - pip list                   查看已安装的 Python 包
```

### 11.4注意事项
- 验证码为模拟输出：开发环境下，短信验证码会打印在 docker-compose logs backend 中，不会真实发送短信。
- 默认后端地址：前端应配置 API Base URL 为 http://localhost:5000。
- 数据库持久化：PostgreSQL 数据保存在 Docker 卷 postgres_data 中，删除卷会丢失所有数据。
- 端口冲突：若本地 5000 或 5432 端口被占用，请修改 docker-compose.yml 中的映射端口。
