import type { QueryResponse, Turn, Settings } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export type RetrievalMode = "hybrid" | "vanilla" | "bm25" | "hyde"
export type LanguageMode = "fr" | "en" | "bilingual"
export type BoardFilter = "cbse" | "ib" | "all"

export async function postQuery(
  demo: string,
  q: string,
  history: Turn[],
  settings: Settings,
  mode: RetrievalMode = "hybrid",
  signal?: AbortSignal,
  languageMode?: LanguageMode,
  board?: BoardFilter,
): Promise<QueryResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-OpenRouter-Key": settings.openrouterKey,
  }

  const params = new URLSearchParams({ mode })
  if (settings.cfAccountId) params.set("cf_account_id", settings.cfAccountId)
  if (settings.cfGatewayId) params.set("cf_gateway_id", settings.cfGatewayId)
  if (board && board !== "all") params.set("board", board)

  const body: Record<string, unknown> = { q, history }
  if (languageMode) body.language_mode = languageMode

  const resp = await fetch(`${API_URL}/api/${demo}/query?${params}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal,
  })

  if (!resp.ok) {
    const text = await resp.text().catch(() => resp.statusText)
    throw new Error(`API ${resp.status}: ${text}`)
  }

  return resp.json() as Promise<QueryResponse>
}

export interface DemoMeta {
  id: string
  title: string
  description: string
}

export async function fetchDemos(): Promise<DemoMeta[]> {
  const resp = await fetch(`${API_URL}/api/demos`)
  if (!resp.ok) return []
  const data = await resp.json()
  return data.demos ?? []
}

export interface CorpusDocument {
  doc_id: string
  doc_title: string
  chunk_count: number
  section_count: number
}

export interface CorpusInfo {
  demo_id: string
  documents: CorpusDocument[]
  total_chunks: number
}

export async function fetchCorpus(demo: string): Promise<CorpusInfo | null> {
  const resp = await fetch(`${API_URL}/api/${demo}/corpus`)
  if (!resp.ok) return null
  return resp.json()
}

export interface DatasetRow {
  eval_context: string
  input: string
  output: string
  expected_answer: string
  expected_citations: string
  expected_assertions: string
}

export interface DatasetInfo {
  demo_id: string
  version?: string
  columns: string[]
  rows: DatasetRow[]
  categories: Record<string, number>
  total: number
}

export async function fetchDataset(demo: string, version?: string): Promise<DatasetInfo | null> {
  const params = version ? `?version=${encodeURIComponent(version)}` : ""
  const resp = await fetch(`${API_URL}/api/${demo}/dataset${params}`)
  if (!resp.ok) return null
  return resp.json()
}

// ── Teacher dashboard — chapter outline ───────────────────────────────────────
export interface ChapterSection {
  section_ref: string
  type: string | null
  skill: string | null
  preview: string
}
export interface Chapter {
  id: string
  doc_id: string
  doc_title: string
  board: string | null
  level: string | null
  sections: ChapterSection[]
}
export interface ChapterOutline {
  demo_id: string
  chapters: Chapter[]
}

export async function fetchChapters(demo: string, board?: string): Promise<ChapterOutline | null> {
  const params = board && board !== "all" ? `?board=${board}` : ""
  const resp = await fetch(`${API_URL}/api/${demo}/chapters${params}`)
  if (!resp.ok) return null
  return resp.json()
}

// ── Question generator ───────────────────────────────────────────────────────
export interface GenQuestionsReq {
  chapter?: string
  board?: string
  count?: number
  difficulty?: string
  question_types?: string[]
  language_mode?: LanguageMode
}

export interface GenQuestionsResp {
  questions_markdown: string
  chunks_used: { section_ref: string; doc_title: string }[]
  config: Record<string, unknown>
  error?: string
}

export async function generateQuestions(
  demo: string,
  req: GenQuestionsReq,
  settings: Settings,
): Promise<GenQuestionsResp | null> {
  const resp = await fetch(`${API_URL}/api/${demo}/generate-questions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-OpenRouter-Key": settings.openrouterKey,
    },
    body: JSON.stringify(req),
  })
  if (!resp.ok) return null
  return resp.json()
}
