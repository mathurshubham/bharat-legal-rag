import type { QueryResponse, Turn, Settings } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export type RetrievalMode = "hybrid" | "vanilla" | "bm25" | "hyde"

export async function postQuery(
  demo: string,
  q: string,
  history: Turn[],
  settings: Settings,
  mode: RetrievalMode = "hybrid",
  signal?: AbortSignal,
): Promise<QueryResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-OpenRouter-Key": settings.openrouterKey,
  }

  const params = new URLSearchParams({ mode })
  if (settings.cfAccountId) params.set("cf_account_id", settings.cfAccountId)
  if (settings.cfGatewayId) params.set("cf_gateway_id", settings.cfGatewayId)

  const resp = await fetch(`${API_URL}/api/${demo}/query?${params}`, {
    method: "POST",
    headers,
    body: JSON.stringify({ q, history }),
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
