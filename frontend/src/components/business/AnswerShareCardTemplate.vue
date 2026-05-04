<template>
  <!--
    高精 HTML/CSS 分享卡模板，用于页面预览；与刘小莉侧 Canvas 导出（cardGenerator.drawAnswerCard）对齐说明：
    - Canvas 版当前仅绘制 answer 文案（AnswerCardData.answer）
    - 本模板额外展示 question，便于后续若用 html2canvas 截图上传广场时与内容一致
  -->
  <div class="share-card" role="img" :aria-label="`答案卡：${answerText}`">
    <div class="share-card__frame">
      <div class="share-card__ornament share-card__ornament--tl" />
      <div class="share-card__ornament share-card__ornament--tr" />
      <div class="share-card__ornament share-card__ornament--bl" />
      <div class="share-card__ornament share-card__ornament--br" />

      <p class="share-card__brand">{{ brand }}</p>
      <p class="share-card__kicker">ANSWER CARD</p>

      <div class="share-card__divider" />

      <p class="share-card__label">你的问题</p>
      <p class="share-card__question">{{ question }}</p>

      <div class="share-card__answer-shell">
        <p class="share-card__answer">{{ answerText }}</p>
      </div>

      <p v-if="footnote" class="share-card__footnote">{{ footnote }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    question: string
    answerText: string
    brand?: string
    footnote?: string
  }>(),
  {
    brand: '心运岛',
    footnote: '',
  },
)
</script>

<style scoped>
.share-card {
  width: 100%;
  max-width: 320px;
  margin: 0 auto;
  aspect-ratio: 320 / 480;
  border-radius: 22px;
  padding: 2px;
  background: linear-gradient(
    145deg,
    rgba(253, 230, 138, 0.95) 0%,
    rgba(196, 181, 253, 0.95) 45%,
    rgba(129, 140, 248, 0.98) 100%
  );
  box-shadow:
    0 22px 48px rgba(79, 70, 229, 0.28),
    0 0 0 1px rgba(255, 255, 255, 0.35) inset;
}

.share-card__frame {
  position: relative;
  height: 100%;
  border-radius: 20px;
  padding: 22px 18px 18px;
  background:
    radial-gradient(120% 80% at 50% -10%, rgba(255, 255, 255, 0.55), transparent 55%),
    linear-gradient(168deg, #1e1b4b 0%, #312e81 38%, #4338ca 100%);
  color: #f8fafc;
  overflow: hidden;
}

.share-card__ornament {
  position: absolute;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(253, 230, 138, 0.45);
  border-radius: 10px;
  pointer-events: none;
}
.share-card__ornament--tl {
  top: 12px;
  left: 12px;
}
.share-card__ornament--tr {
  top: 12px;
  right: 12px;
}
.share-card__ornament--bl {
  bottom: 12px;
  left: 12px;
}
.share-card__ornament--br {
  bottom: 12px;
  right: 12px;
}

.share-card__brand {
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.35em;
  color: #fde68a;
  margin: 0;
}

.share-card__kicker {
  text-align: center;
  margin: 6px 0 0;
  font-size: 10px;
  letter-spacing: 0.28em;
  color: rgba(226, 232, 240, 0.65);
}

.share-card__divider {
  height: 1px;
  margin: 16px 8px 14px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(253, 230, 138, 0.55),
    rgba(196, 181, 253, 0.55),
    transparent
  );
}

.share-card__label {
  margin: 0;
  font-size: 11px;
  color: rgba(226, 232, 240, 0.75);
}

.share-card__question {
  margin: 6px 0 0;
  font-size: 14px;
  line-height: 1.55;
  font-weight: 600;
  color: #f1f5f9;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.share-card__answer-shell {
  margin-top: 18px;
  padding: 16px 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
}

.share-card__answer {
  margin: 0;
  text-align: center;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 17px;
  line-height: 1.65;
  font-weight: 700;
  color: #fefce8;
  text-shadow: 0 1px 0 rgba(15, 23, 42, 0.35);
}

.share-card__footnote {
  margin: 14px 4px 0;
  text-align: center;
  font-size: 10px;
  color: rgba(226, 232, 240, 0.55);
}
</style>
