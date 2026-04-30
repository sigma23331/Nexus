import axios from 'axios'

const promptLabClient = axios.create({
  baseURL: import.meta.env.DEV ? '/api' : '',
  timeout: 25000,
})

export type PromptLabTask = 'answer' | 'fortune' | 'profile'

export interface PromptLabTaskInputMap {
  answer: { question: string }
  fortune: { target_date: string }
  profile: {
    diary_entries: Array<{ content: string }>
    answer_questions: Array<{ question: string; answer: string }>
  }
}

export interface PromptLabRunRequest {
  task: 'answer'
  prompt_text: string
  temperature: number
  frequency_penalty?: number
  top_p?: number
  input: PromptLabTaskInputMap['answer']
}

export interface PromptLabRunFortuneRequest {
  task: 'fortune'
  prompt_text: string
  temperature: number
  frequency_penalty?: number
  top_p?: number
  input: PromptLabTaskInputMap['fortune']
}

export interface PromptLabRunProfileRequest {
  task: 'profile'
  prompt_text: string
  temperature: number
  frequency_penalty?: number
  top_p?: number
  input: PromptLabTaskInputMap['profile']
}

export type PromptLabRequest =
  | PromptLabRunRequest
  | PromptLabRunFortuneRequest
  | PromptLabRunProfileRequest

export interface PromptLabRunData {
  task: PromptLabTask
  success: boolean
  output_text: string
  output_preview: string
  latency_ms: number
  parse_success: boolean | null
  schema_valid: boolean | null
  fallback_used: boolean
  error_code: string | null
  error_message: string | null
}

export interface PromptLabRunEnvelope {
  code: number
  message: string
  data: PromptLabRunData | null
}

export function runPromptLab(
  payload: PromptLabRequest,
): Promise<{ data: PromptLabRunEnvelope }> {
  return promptLabClient.post('/v1/dev/prompt-lab/run', payload)
}
