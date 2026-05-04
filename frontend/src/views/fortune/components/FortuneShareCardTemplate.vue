<template>
  <!-- 运势分享卡：中式八卦、按日变色；签文由外层摇签展示，此处不展示分数 -->
  <div class="fcard" role="img" :data-bagua="bagua" :aria-label="`运势分享卡：${title}`">
    <svg class="fcard__taiji" viewBox="0 0 100 100" aria-hidden="true">
      <circle cx="50" cy="50" r="48" class="fcard__taiji-ring" />
      <!-- 简笔太极 S 形，避免复杂曲线在不同引擎下走样 -->
      <path
        class="fcard__taiji-s"
        d="M50 2 A48 48 0 0 1 50 98 A24 24 0 0 1 50 50 A24 24 0 0 0 50 2Z"
      />
      <circle cx="50" cy="26" r="7" class="fcard__taiji-dot fcard__taiji-dot--yang" />
      <circle cx="50" cy="74" r="7" class="fcard__taiji-dot fcard__taiji-dot--yin" />
    </svg>

    <div class="fcard__inner">
      <header class="fcard__head">
        <div>
          <p class="fcard__brand">{{ brand }}</p>
          <p class="fcard__date">{{ date }}</p>
        </div>
        <p class="fcard__gua">{{ baguaLabel }}</p>
      </header>

      <p class="fcard__main">{{ contentMain }}</p>
      <p class="fcard__sub">{{ contentSub }}</p>

      <div class="fcard__dims" aria-label="四维">
        <span><em>情</em>{{ love }}</span>
        <span class="fcard__dot">·</span>
        <span><em>业</em>{{ career }}</span>
        <span class="fcard__dot">·</span>
        <span><em>身</em>{{ health }}</span>
        <span class="fcard__dot">·</span>
        <span><em>财</em>{{ wealth }}</span>
      </div>

      <div class="fcard__yiji">
        <div class="fcard__yiji-col fcard__yiji-col--yi">
          <span class="fcard__yiji-tag">宜</span>
          <p class="fcard__yiji-text">{{ yiLine }}</p>
        </div>
        <div class="fcard__yiji-col fcard__yiji-col--ji">
          <span class="fcard__yiji-tag">忌</span>
          <p class="fcard__yiji-text">{{ jiLine }}</p>
        </div>
      </div>

      <p v-if="footnote" class="fcard__foot">{{ footnote }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BAGUA_KEYS, BAGUA_LABELS, baguaIndexFromDate } from '../utils/fortuneShareBagua'

const props = withDefaults(
  defineProps<{
    brand?: string
    date: string
    title: string
    /** 已不在卡面展示，保留兼容字段 */
    score?: number
    contentMain: string
    contentSub: string
    love: string
    career: string
    health: string
    wealth: string
    yi: string[]
    ji: string[]
    footnote?: string
    /** 不传则按 `date` 自动映射，每日风格略变 */
    baguaIndex?: number
  }>(),
  {
    brand: '心运岛',
    footnote: '',
  },
)

const bagua = computed(() =>
  props.baguaIndex !== undefined ? props.baguaIndex % 8 : baguaIndexFromDate(props.date),
)
const baguaLabel = computed(() => BAGUA_LABELS[BAGUA_KEYS[bagua.value]!])

const yiLine = computed(() => props.yi.join(' · ') || '—')
const jiLine = computed(() => props.ji.join(' · ') || '—')
</script>

<style scoped>
.fcard {
  --fc-paper-a: #faf8f5;
  --fc-paper-b: #f4f1eb;
  --fc-ink: #1c1917;
  --fc-muted: #78716c;
  --fc-accent: #92400e;
  --fc-yi: #0f766e;
  --fc-ji: #9f1239;
  --fc-taiji-a: rgba(28, 25, 23, 0.07);
  --fc-taiji-b: rgba(28, 25, 23, 0.04);

  position: relative;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  border-radius: 4px;
  padding: 1px;
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--fc-accent) 22%, transparent),
    color-mix(in srgb, var(--fc-accent) 8%, transparent)
  );
  box-shadow:
    0 24px 48px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.4) inset;
}

.fcard[data-bagua='1'] {
  --fc-paper-a: #f8fafc;
  --fc-paper-b: #eef2f7;
  --fc-accent: #475569;
  --fc-taiji-a: rgba(71, 85, 105, 0.09);
  --fc-taiji-b: rgba(71, 85, 105, 0.05);
}
.fcard[data-bagua='2'] {
  --fc-paper-a: #fff7f5;
  --fc-paper-b: #ffe8e0;
  --fc-accent: #c2410c;
  --fc-taiji-a: rgba(194, 65, 12, 0.08);
  --fc-taiji-b: rgba(194, 65, 12, 0.04);
}
.fcard[data-bagua='3'] {
  --fc-paper-a: #f0fdf9;
  --fc-paper-b: #d1fae5;
  --fc-accent: #047857;
  --fc-taiji-a: rgba(4, 120, 87, 0.08);
  --fc-taiji-b: rgba(4, 120, 87, 0.04);
}
.fcard[data-bagua='4'] {
  --fc-paper-a: #f7fef9;
  --fc-paper-b: #ecfccb;
  --fc-accent: #3f6212;
  --fc-taiji-a: rgba(63, 98, 18, 0.08);
  --fc-taiji-b: rgba(63, 98, 18, 0.04);
}
.fcard[data-bagua='5'] {
  --fc-paper-a: #f0f9ff;
  --fc-paper-b: #e0f2fe;
  --fc-accent: #0369a1;
  --fc-taiji-a: rgba(3, 105, 161, 0.09);
  --fc-taiji-b: rgba(3, 105, 161, 0.05);
}
.fcard[data-bagua='6'] {
  --fc-paper-a: #fafaf9;
  --fc-paper-b: #e7e5e4;
  --fc-accent: #57534e;
  --fc-taiji-a: rgba(68, 64, 60, 0.09);
  --fc-taiji-b: rgba(68, 64, 60, 0.05);
}
.fcard[data-bagua='7'] {
  --fc-paper-a: #fdfcfa;
  --fc-paper-b: #f5f0e6;
  --fc-accent: #854d0e;
  --fc-taiji-a: rgba(133, 77, 14, 0.08);
  --fc-taiji-b: rgba(133, 77, 14, 0.04);
}

.fcard__taiji {
  position: absolute;
  left: 50%;
  top: 46%;
  width: 200px;
  height: 200px;
  transform: translate(-50%, -50%);
  opacity: 1;
  pointer-events: none;
}

.fcard__taiji-ring {
  fill: none;
  stroke: var(--fc-taiji-a);
  stroke-width: 1;
}

.fcard__taiji-s {
  fill: var(--fc-taiji-a);
}

.fcard__taiji-dot--yang {
  fill: var(--fc-paper-a);
  stroke: var(--fc-taiji-a);
  stroke-width: 0.6;
}

.fcard__taiji-dot--yin {
  fill: var(--fc-taiji-b);
  stroke: var(--fc-taiji-a);
  stroke-width: 0.6;
}

.fcard__inner {
  position: relative;
  border-radius: 3px;
  padding: 22px 18px 18px;
  background: linear-gradient(168deg, var(--fc-paper-a), var(--fc-paper-b));
  overflow: hidden;
}

.fcard__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--fc-ink) 8%, transparent);
  padding-bottom: 12px;
  margin-bottom: 4px;
}

.fcard__brand {
  margin: 0;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.42em;
  color: var(--fc-muted);
}

.fcard__date {
  margin: 6px 0 0;
  font-size: 11px;
  font-weight: 500;
  color: color-mix(in srgb, var(--fc-ink) 55%, var(--fc-muted));
}

.fcard__gua {
  margin: 0;
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--fc-accent);
  writing-mode: horizontal-tb;
  text-align: right;
  line-height: 1.35;
}

.fcard__main {
  position: relative;
  margin: 20px 0 0;
  text-align: center;
  font-family: 'Songti SC', 'Noto Serif SC', 'STSong', Georgia, serif;
  font-size: 20px;
  font-weight: 700;
  line-height: 1.5;
  color: var(--fc-ink);
  letter-spacing: 0.06em;
}

.fcard__sub {
  position: relative;
  margin: 12px 4px 0;
  text-align: center;
  font-size: 12px;
  line-height: 1.65;
  color: color-mix(in srgb, var(--fc-ink) 72%, transparent);
}

.fcard__dims {
  position: relative;
  margin-top: 22px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 4px 2px;
  font-size: 11px;
  color: var(--fc-muted);
  letter-spacing: 0.02em;
}

.fcard__dims em {
  font-style: normal;
  font-size: 10px;
  opacity: 0.75;
  margin-right: 2px;
  color: var(--fc-accent);
}

.fcard__dot {
  color: color-mix(in srgb, var(--fc-accent) 35%, transparent);
  user-select: none;
}

.fcard__yiji {
  position: relative;
  margin-top: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.fcard__yiji-col {
  padding: 11px 10px;
  border-radius: 2px;
  border: 1px solid transparent;
}

.fcard__yiji-col--yi {
  background: color-mix(in srgb, var(--fc-yi) 7%, var(--fc-paper-a));
  border-color: color-mix(in srgb, var(--fc-yi) 22%, transparent);
}

.fcard__yiji-col--ji {
  background: color-mix(in srgb, var(--fc-ji) 7%, var(--fc-paper-a));
  border-color: color-mix(in srgb, var(--fc-ji) 22%, transparent);
}

.fcard__yiji-tag {
  display: block;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.35em;
}

.fcard__yiji-col--yi .fcard__yiji-tag {
  color: var(--fc-yi);
}
.fcard__yiji-col--ji .fcard__yiji-tag {
  color: var(--fc-ji);
}

.fcard__yiji-text {
  margin: 8px 0 0;
  font-size: 11px;
  line-height: 1.5;
  color: color-mix(in srgb, var(--fc-ink) 78%, transparent);
}

.fcard__foot {
  margin: 16px 0 0;
  text-align: center;
  font-size: 9px;
  letter-spacing: 0.15em;
  color: var(--fc-muted);
}
</style>
