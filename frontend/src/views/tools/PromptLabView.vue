<template>
  <div class="prompt-lab-page">
    <div class="prompt-lab-bg" aria-hidden="true"></div>
    <main class="prompt-lab-shell">
      <header class="prompt-lab-header">
        <p class="eyebrow">Developer Tool</p>
        <h1>Prompt Lab</h1>
        <p class="subtitle">Run answer, fortune, and profile prompts with editable inputs.</p>
      </header>

      <section class="prompt-lab-grid">
        <article class="panel controls">
          <div class="control-row">
            <label for="task">Task</label>
            <span class="help-text">answer=答案之书 / fortune=运势 / profile=用户画像分析</span>
            <select id="task" v-model="task" :disabled="loading">
              <option value="answer">answer</option>
              <option value="fortune">fortune</option>
              <option value="profile">profile</option>
            </select>
          </div>

          <div class="control-row temp-row">
            <label for="temperature">Temperature</label>
            <span class="help-text">越高输出越随机（0-2）</span>
            <input
              id="temperature"
              type="number"
              min="0"
              max="2"
              step="0.1"
              :disabled="loading"
              :value="temperature"
              @input="onTemperatureInput"
            />
            <input
              class="slider"
              type="range"
              min="0"
              max="2"
              step="0.01"
              :disabled="loading"
              :value="temperature"
              @input="onTemperatureInput"
            />
          </div>

          <div class="control-row temp-row">
            <label for="frequency-penalty">Frequency Penalty</label>
            <span class="help-text">负值鼓励重复用词，正值抑制重复（-2~2），默认 0</span>
            <input
              id="frequency-penalty"
              type="number"
              min="-2"
              max="2"
              step="0.1"
              :disabled="loading"
              :value="frequencyPenalty"
              @input="onFrequencyPenaltyInput"
            />
            <input
              class="slider"
              type="range"
              min="-2"
              max="2"
              step="0.01"
              :disabled="loading"
              :value="frequencyPenalty"
              @input="onFrequencyPenaltyInput"
            />
          </div>

          <div class="control-row temp-row">
            <label for="top-p">Top P</label>
            <span class="help-text">核采样阈值（0-1），1=不做限制，值越小输出越确定</span>
            <input
              id="top-p"
              type="number"
              min="0"
              max="1"
              step="0.01"
              :disabled="loading"
              :value="topP"
              @input="onTopPInput"
            />
            <input
              class="slider"
              type="range"
              min="0"
              max="1"
              step="0.01"
              :disabled="loading"
              :value="topP"
              @input="onTopPInput"
            />
          </div>

          <div class="control-row block">
            <label for="prompt">Prompt Text</label>
            <span class="help-text"
              >发给 LLM 的提示词模板，支持 {{ question }} {{ target_date }} {{ diary_summary }}
              {{ question_summary }} {{ mood_tendency }} {{ topic_interests }}
              {{ self_context_tag }} 以及 v4 的 {selected_style}/{score}/{title_main} 等占位符</span
            >
            <textarea id="prompt" v-model="promptText" rows="10" :disabled="loading"></textarea>
          </div>

          <div class="control-row block">
            <label for="input">Input JSON</label>
            <span class="help-text"
              >answer: &#123;"question":"..."&#125; / fortune:
              &#123;"target_date":"2026-04-29"&#125; / profile:
              &#123;"diary_entries":[...],"answer_questions":[...]&#125;</span
            >
            <textarea id="input" v-model="inputText" rows="10" :disabled="loading"></textarea>
          </div>

          <div class="button-row">
            <button class="run" :disabled="loading" @click="onRun">
              {{ loading ? 'Running...' : 'Run' }}
            </button>
            <button :disabled="loading" @click="onReset">Reset</button>
            <button :disabled="!result.output_text" @click="onCopyOutput">Copy Output</button>
          </div>
        </article>

        <article class="panel output">
          <section v-if="errorCard" class="error-card" role="alert">
            <h2>Error</h2>
            <p class="error-code">{{ errorCard.code }}</p>
            <p>{{ errorCard.message }}</p>
          </section>

          <section class="result-block">
            <h2>Output Text</h2>
            <pre>{{ result.output_text || 'No output yet.' }}</pre>
          </section>

          <section class="result-block">
            <h2>Output Preview</h2>
            <p>{{ result.output_preview || '-' }}</p>
          </section>

          <section class="metrics">
            <h2>Metrics</h2>
            <span class="help-text margin-b"
              >latency_ms=请求耗时 / success=是否执行成功 / parse_success=JSON解析成功 /
              schema_valid=字段校验通过 / fallback_used=是否触发降级兜底</span
            >
            <dl>
              <div>
                <dt>latency_ms</dt>
                <dd>{{ metricValue(result.latency_ms) }}</dd>
              </div>
              <div>
                <dt>success</dt>
                <dd>{{ metricValue(result.success) }}</dd>
              </div>
              <div>
                <dt>parse_success</dt>
                <dd>{{ metricValue(result.parse_success) }}</dd>
              </div>
              <div>
                <dt>schema_valid</dt>
                <dd>{{ metricValue(result.schema_valid) }}</dd>
              </div>
              <div>
                <dt>fallback_used</dt>
                <dd>{{ metricValue(result.fallback_used) }}</dd>
              </div>
            </dl>
          </section>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  fetchPromptTemplate,
  runPromptLab,
  type PromptLabRequest,
  type PromptLabRunData,
  type PromptLabTask,
} from '@/api/promptLab'

type TaskDefaults = {
  promptText: string
  temperature: number
  frequencyPenalty: number
  topP: number
  inputText: string
}

type ErrorCard = {
  code: string
  message: string
}

const TASK_DEFAULTS: Record<PromptLabTask, TaskDefaults> = {
  answer: {
    promptText: [
      '## 角色',
      '你是心运岛的答案之书',
      '## 风格',
      '本次请用以下风格回答：',
      '{selected_style}',
      '## 任务',
      '用户问了以下问题：',
      '{{question}}',
      '',
      '请你翻到某一页，告诉我那一页的答案是什么，只输出答案',
      '## constraint',
      '- 输出格式为一句话，不要包含"答案："/"答案是"',
      '- 长度自然，不要超过20个字',
    ].join('\n'),
    temperature: 0.7,
    frequencyPenalty: 0,
    topP: 1,
    inputText: JSON.stringify(
      {
        question: '这周面试能过吗？',
      },
      null,
      2,
    ),
  },
  fortune: {
    promptText: [
      '## 角色',
      '你是心运岛的中文运势助手',
      '## 约束',
      '今天是 {target_date}，用户整体运势分数为 {score}。',
      '请基于以下信息生成运势，只输出 JSON。',
      '',
      '## 主副标题风格',
      '主标题参考：{title_main}',
      '副标题参考：{title_sub}',
      '要求：主标题10-20字富有哲理；副标题15-30字具体建议。不要直接照搬参考，需结合分数重新创作。',
      '',
      '## 分项运势',
      '请根据以下关键词倾向生成各分项一句话：',
      '- 爱情：{love_keyword}',
      '- 事业：{career_keyword}',
      '- 健康：{health_keyword}',
      '- 财富：{wealth_keyword}',
      '',
      '## 宜忌参考',
      '宜参考：{yi_samples}',
      '忌参考：{ji_samples}',
      '要求：结合参考项为今日生成 3 条宜、3 条忌，语言贴近日常生活。',
      '',
      '## 输出格式',
      '严格输出 JSON：score/content_main/content_sub/love/career/health/wealth/yi/ji',
    ].join('\n'),
    temperature: 0.8,
    frequencyPenalty: 0,
    topP: 1,
    inputText: JSON.stringify(
      {
        target_date: '2026-04-29',
      },
      null,
      2,
    ),
  },
  profile: {
    promptText: [
      '## 角色',
      '你是专业的心理与行为分析助手。',
      '## 约束',
      '请仅输出json对象，不要输出额外说明。',
      '字段必须包含：mood_tendency,topic_interests,self_context_tag。',
      '示例json：',
      '{"mood_tendency":"anxious","topic_interests":["study","career"],"self_context_tag":"备考期"}',
    ].join('\n'),
    temperature: 0.6,
    frequencyPenalty: 0,
    topP: 1,
    inputText: JSON.stringify(
      {
        diary_entries: [
          { content: '今天专注学习了3小时，但下午被消息打断了节奏。' },
          { content: '完成了一个复杂任务，拆分步骤的方法很有效。' },
        ],
        answer_questions: [
          { question: '怎么应对焦虑？', answer: '先深呼吸，然后列出具体可以做的事。' },
        ],
      },
      null,
      2,
    ),
  },
}

const EMPTY_RESULT: PromptLabRunData = {
  task: 'answer',
  success: false,
  output_text: '',
  output_preview: '',
  latency_ms: 0,
  parse_success: null,
  schema_valid: null,
  fallback_used: false,
  error_code: null,
  error_message: null,
}

const task = ref<PromptLabTask>('answer')
const promptText = ref('')
const temperature = ref(0.7)
const frequencyPenalty = ref(0)
const topP = ref(1)
const inputText = ref('')
const loading = ref(false)
const templateLoading = ref(false)
const result = ref<PromptLabRunData>({ ...EMPTY_RESULT })
const errorCard = ref<ErrorCard | null>(null)

function applyTaskDefaults(nextTask: PromptLabTask): void {
  const defaults = TASK_DEFAULTS[nextTask]
  promptText.value = defaults.promptText
  temperature.value = clampTemperature(defaults.temperature)
  frequencyPenalty.value = clampFrequencyPenalty(defaults.frequencyPenalty)
  topP.value = clampTopP(defaults.topP)
  inputText.value = defaults.inputText
}

async function loadPromptTemplate(nextTask: PromptLabTask): Promise<void> {
  templateLoading.value = true
  try {
    const response = await fetchPromptTemplate(nextTask)
    if (response.data?.code === 200 && response.data?.data?.prompt_text) {
      promptText.value = response.data.data.prompt_text
    }
  } catch {
    // keep local defaults when backend template API is unavailable
  } finally {
    templateLoading.value = false
  }
}

watch(task, (nextTask) => {
  applyTaskDefaults(nextTask)
  void loadPromptTemplate(nextTask)
  result.value = { ...EMPTY_RESULT, task: nextTask }
  errorCard.value = null
})

applyTaskDefaults(task.value)
void loadPromptTemplate(task.value)

function clampTemperature(value: number): number {
  const safe = Number.isFinite(value) ? value : 0
  return Math.min(2, Math.max(0, safe))
}

function onTemperatureInput(event: Event): void {
  const target = event.target as HTMLInputElement
  temperature.value = clampTemperature(Number.parseFloat(target.value))
}

function clampFrequencyPenalty(value: number): number {
  const safe = Number.isFinite(value) ? value : 0
  return Math.min(2, Math.max(-2, safe))
}

function clampTopP(value: number): number {
  const safe = Number.isFinite(value) ? value : 1
  return Math.min(1, Math.max(0, safe))
}

function onFrequencyPenaltyInput(event: Event): void {
  const target = event.target as HTMLInputElement
  frequencyPenalty.value = clampFrequencyPenalty(Number.parseFloat(target.value))
}

function onTopPInput(event: Event): void {
  const target = event.target as HTMLInputElement
  topP.value = clampTopP(Number.parseFloat(target.value))
}

function onReset(): void {
  applyTaskDefaults(task.value)
  result.value = { ...EMPTY_RESULT, task: task.value }
  errorCard.value = null
}

async function onCopyOutput(): Promise<void> {
  if (!result.value.output_text) {
    return
  }

  try {
    await navigator.clipboard.writeText(result.value.output_text)
  } catch {
    errorCard.value = {
      code: 'clipboard_error',
      message: 'Unable to copy output. Please copy manually.',
    }
  }
}

async function onRun(): Promise<void> {
  if (loading.value) {
    return
  }

  loading.value = true
  errorCard.value = null
  result.value = { ...EMPTY_RESULT, task: task.value }

  try {
    const parsedInput = JSON.parse(inputText.value) as unknown
    if (!parsedInput || typeof parsedInput !== 'object' || Array.isArray(parsedInput)) {
      throw new Error('Input JSON must be an object.')
    }

    const requestPayload = buildTaskRequest(task.value, parsedInput as Record<string, unknown>)
    const response = await runPromptLab(requestPayload)
    if (response.data?.code !== 200) {
      errorCard.value = {
        code: 'api_error',
        message: response.data?.message || 'Request failed.',
      }
      return
    }

    const responseData = response.data?.data
    if (responseData) {
      result.value = responseData
    } else {
      result.value = { ...EMPTY_RESULT, task: task.value }
    }

    if (responseData?.success === false) {
      errorCard.value = {
        code: responseData.error_code || 'provider_error',
        message: responseData.error_message || 'Prompt run failed.',
      }
    }
  } catch (error: unknown) {
    const axiosError = error as {
      code?: string
      message?: string
      response?: {
        data?: {
          message?: string
        }
      }
    }

    const isTimeout = axiosError.code === 'ECONNABORTED'
    errorCard.value = {
      code: isTimeout ? 'timeout' : 'request_error',
      message:
        (isTimeout
          ? 'Request timed out after 25s. Try a shorter prompt or retry.'
          : axiosError.response?.data?.message || axiosError.message) || 'Request failed.',
    }
    result.value = { ...EMPTY_RESULT, task: task.value }
  } finally {
    loading.value = false
  }
}

function buildTaskRequest(
  nextTask: PromptLabTask,
  parsedInput: Record<string, unknown>,
): PromptLabRequest {
  const shared = {
    prompt_text: promptText.value,
    temperature: clampTemperature(temperature.value),
    frequency_penalty: clampFrequencyPenalty(frequencyPenalty.value),
    top_p: clampTopP(topP.value),
  }

  if (nextTask === 'answer') {
    return {
      task: 'answer',
      ...shared,
      input: {
        question: String(parsedInput.question ?? ''),
      },
    }
  }

  if (nextTask === 'fortune') {
    return {
      task: 'fortune',
      ...shared,
      input: {
        target_date: String(parsedInput.target_date ?? ''),
      },
    }
  }

  return {
    task: 'profile',
    ...shared,
    input: {
      diary_entries: Array.isArray(parsedInput.diary_entries)
        ? (parsedInput.diary_entries as Array<{ content: string }>)
        : [],
      answer_questions: Array.isArray(parsedInput.answer_questions)
        ? (parsedInput.answer_questions as Array<{ question: string; answer: string }>)
        : [],
    },
  }
}

const metricValue = computed(() => {
  return (value: boolean | number | null): string => {
    if (value === null) {
      return 'null'
    }
    if (typeof value === 'boolean') {
      return value ? 'true' : 'false'
    }
    return String(value)
  }
})
</script>

<style scoped>
.prompt-lab-page {
  --lab-bg-1: #f6f1e8;
  --lab-bg-2: #e4efe8;
  --lab-ink: #1f2a2e;
  --lab-muted: #5f6d70;
  --lab-panel: rgba(255, 255, 255, 0.84);
  --lab-border: #b9c9be;
  --lab-accent: #215f68;
  --lab-danger-bg: #fff2ec;
  --lab-danger-border: #e7a88c;
  min-height: 100vh;
  position: relative;
  padding: 24px;
  color: var(--lab-ink);
}

.prompt-lab-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(1200px 560px at 8% 0%, #d2e7da 0%, transparent 60%),
    radial-gradient(900px 460px at 95% 10%, #f0dbbf 0%, transparent 55%),
    linear-gradient(140deg, var(--lab-bg-1), var(--lab-bg-2));
}

.prompt-lab-shell {
  max-width: 1200px;
  margin: 0 auto;
}

.prompt-lab-header {
  margin-bottom: 18px;
}

.prompt-lab-header h1 {
  margin: 0;
  font-size: 2rem;
  letter-spacing: 0.02em;
}

.eyebrow {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--lab-muted);
}

.subtitle {
  margin: 8px 0 0;
  color: var(--lab-muted);
}

.prompt-lab-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
}

.panel {
  backdrop-filter: blur(8px);
  background: var(--lab-panel);
  border: 1px solid var(--lab-border);
  border-radius: 20px;
  padding: 16px;
}

.control-row {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.control-row.block {
  margin-bottom: 14px;
}

label {
  font-size: 0.84rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--lab-muted);
}

input,
select,
textarea,
button {
  font: inherit;
}

input,
select,
textarea {
  border: 1px solid var(--lab-border);
  border-radius: 12px;
  padding: 10px;
  color: var(--lab-ink);
  background: #fdfdfb;
}

textarea {
  resize: vertical;
}

.help-text {
  display: block;
  font-size: 0.75rem;
  color: var(--lab-muted);
  line-height: 1.4;
  margin-bottom: 2px;
}

.help-text.margin-b {
  margin-bottom: 8px;
}

.temp-row {
  grid-template-columns: 1fr;
}

.slider {
  padding: 0;
}

.button-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

button {
  border: 1px solid var(--lab-border);
  border-radius: 999px;
  padding: 10px 14px;
  background: #f6f7f5;
  color: var(--lab-ink);
  cursor: pointer;
}

button.run {
  background: linear-gradient(135deg, #2e6f66, var(--lab-accent));
  border-color: #2e6f66;
  color: #f7fffe;
}

button:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.output {
  display: grid;
  gap: 12px;
  align-content: start;
}

.result-block {
  border: 1px solid var(--lab-border);
  border-radius: 14px;
  background: #fbfcfa;
  padding: 12px;
}

.result-block h2,
.metrics h2,
.error-card h2 {
  margin: 0 0 8px;
  font-size: 0.95rem;
}

.result-block pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.metrics {
  border: 1px solid var(--lab-border);
  border-radius: 14px;
  background: #fbfcfa;
  padding: 12px;
}

.metrics dl {
  margin: 0;
  display: grid;
  gap: 8px;
}

.metrics dl div {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed #d2ddd5;
  padding-bottom: 4px;
}

.metrics dt {
  color: var(--lab-muted);
}

.error-card {
  border: 1px solid var(--lab-danger-border);
  background: var(--lab-danger-bg);
  border-radius: 14px;
  padding: 12px;
}

.error-card .error-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  color: #9f3415;
  margin: 0 0 6px;
}

@media (max-width: 960px) {
  .prompt-lab-page {
    padding: 14px;
  }

  .prompt-lab-grid {
    grid-template-columns: 1fr;
  }
}
</style>
