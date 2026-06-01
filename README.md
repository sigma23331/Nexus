# Nexus

docx/AppIcons 下存放了不同尺寸与命名方式的桌面图标

## 分享广场 · 评论功能

- **入口**：广场页每张卡片底部 💬 按钮，点击展开/收起评论区。
- **能力**：发表评论、回复顶级评论、查看全部回复、删除自己的评论；评论数与后端 `stats.comments` 同步。
- **接口**：见 `docx/API.md` 第 5.5–5.8 节；前端封装在 `frontend/src/api/plaza.ts`。
- **组件**：`PlazaCommentPanel.vue`、`PlazaCommentItem.vue`（`frontend/src/views/plaza/components/`）。

## 答案之书 · 彩蛋机制

抽取答案时，前端会在本地根据**时间 / 天气 / 节气**判断是否触发彩蛋（不上传服务端，不影响正常 API 记录）。

| 类型 | 触发条件 | 示例 |
|------|----------|------|
| 节气 | 春分、夏至、端午(6/16–6/22)、冬至 | 特殊前缀文案 + 节气动画 |
| 天气 | 需在「隐私设置」开启位置权限；调用 Open-Meteo 获取雨雪/晴夜 | 雨滴、雪花、星空动画 |
| 时间 | 子夜(0–1)、深夜(23–5)、清晨(5–7) | 子夜/晨光彩蛋 |

- **优先级**：节气 > 天气 > 时间（同一时刻只展示一个彩蛋）。
- **实现**：`frontend/src/composables/useAnswerEasterEgg.ts`（检测与本地统计）、`AnswerEasterEggEffects.vue`（弹窗动画）、`AnswerView.vue`（集成展示）。
- **统计**：触发次数写入 `localStorage`（`answer-easter-egg-stats-v1`），供后续「彩蛋猎人」徽章使用。
