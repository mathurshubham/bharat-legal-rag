export interface RetrievedChunk {
  id: number
  doc_id: string
  section_ref: string
  content: string
  score: number
  rerank_score: number | null
}

export interface Citation {
  section_ref: string
  doc_title: string
}

export interface QueryConfig {
  mode: string
  top_k: number
  top_n: number
  rerank: boolean
  gen_model: string
  embed_model: string
  prompt_version: string
}

export interface Usage {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface Latency {
  condense_ms: number
  retrieve_ms: number
  rerank_ms: number
  generate_ms: number
  total_ms: number
}

export interface QueryResponse {
  answer: string
  retrieved_chunks: RetrievedChunk[]
  citations: Citation[]
  config: QueryConfig
  usage: Usage
  latency: Latency
  trace_id: string
}

export interface Turn {
  role: "user" | "assistant"
  content: string
}

export interface ChatMessage extends Turn {
  id: string
  response?: QueryResponse
  isLoading?: boolean
  error?: string
}

export interface Settings {
  openrouterKey: string
  cohereKey: string
  cfAccountId: string
  cfGatewayId: string
}
