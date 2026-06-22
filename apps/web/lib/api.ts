import type { QueryResponse, Turn, Settings } from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function postQuery(
  q: string,
  history: Turn[],
  settings: Settings,
  signal?: AbortSignal,
): Promise<QueryResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-OpenRouter-Key": settings.openrouterKey,
  }

  const params = new URLSearchParams({ mode: "hybrid" })
  if (settings.cfAccountId) params.set("cf_account_id", settings.cfAccountId)
  if (settings.cfGatewayId) params.set("cf_gateway_id", settings.cfGatewayId)

  const resp = await fetch(`${API_URL}/api/query?${params}`, {
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
