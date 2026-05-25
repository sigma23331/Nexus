# Nexus

docx/AppIcons 下存放了不同尺寸与命名方式的桌面图标

## 分享广场 · 评论功能

- **入口**：广场页每张卡片底部 💬 按钮，点击展开/收起评论区。
- **能力**：发表评论、回复顶级评论、查看全部回复、删除自己的评论；评论数与后端 `stats.comments` 同步。
- **接口**：见 `docx/API.md` 第 5.5–5.8 节；前端封装在 `frontend/src/api/plaza.ts`。
- **组件**：`PlazaCommentPanel.vue`、`PlazaCommentItem.vue`（`frontend/src/views/plaza/components/`）。
