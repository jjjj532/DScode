export interface Config {
  provider: 'openai' | 'anthropic' | 'ollama';
  model: string;
  api_base: string | null;
  api_key?: string;
  max_tokens: number;
  temperature: number;
  top_p: number;
  system_prompt: string | null;
}

export interface Session {
  id: string;
  title: string;
  provider?: string;
  model?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}
