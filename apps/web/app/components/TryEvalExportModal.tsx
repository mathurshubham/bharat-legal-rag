"use client"

import { useState } from "react"
import type { Settings } from "@/lib/types"
import type { RetrievalMode } from "@/lib/api"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  demo: string
  config: DemoConfig
  settings: Settings
  mode: RetrievalMode
  onClose: () => void
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

const MODE_LABELS: Record<RetrievalMode, string> = {
  hybrid:  "Hybrid",
  vanilla: "RAG only",
  bm25:    "BM25",
  hyde:    "HyDE",
}

const MODE_DESCS: Record<RetrievalMode, string> = {
  hybrid:  "Dense + BM25 → RRF fusion",
  vanilla: "Dense vector search only",
  bm25:    "Full-text search only",
  hyde:    "Hypothetical doc → embed → retrieve",
}

function buildUrl(demo: string, settings: Settings, mode: RetrievalMode): string {
  const params = new URLSearchParams({ mode, rerank: "true" })
  if (settings.cfAccountId) params.set("cf_account_id", settings.cfAccountId)
  if (settings.cfGatewayId) params.set("cf_gateway_id", settings.cfGatewayId)
  return `${API_URL}/api/${demo}/query?${params.toString()}`
}

function buildHeaderPairs(settings: Settings): Array<{ key: string; value: string }> {
  const pairs: Array<{ key: string; value: string }> = [
    { key: "Content-Type", value: "application/json" },
  ]
  if (settings.openrouterKey) pairs.push({ key: "X-OpenRouter-Key", value: settings.openrouterKey })
  return pairs
}

function CopyField({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  const [copied, setCopied] = useState(false)
  function copy() {
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-[10px] font-semibold text-[var(--text-2)] uppercase tracking-wide">{label}</label>
        <button onClick={copy}
          className={`text-[11px] font-medium px-2 py-0.5 rounded border transition-all ${
            copied
              ? "bg-green-500/15 text-green-600 border-green-500/30 dark:text-green-400"
              : "bg-[var(--bg-card)] border-[var(--border)] text-[var(--text-2)] hover:text-[var(--text)] hover:border-[var(--border-hi)]"
          }`}>
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <div
        onClick={copy}
        className={`w-full rounded-lg bg-[var(--bg-input)] border border-[var(--border)] px-3 py-2 text-[12px] leading-relaxed break-all select-all cursor-pointer hover:border-[var(--border-hi)] transition-colors ${
          mono ? "font-mono text-[var(--text-2)]" : "text-[var(--text-2)]"
        }`}
      >
        {value || <span className="text-[var(--text-4)]">—</span>}
      </div>
    </div>
  )
}

export function TryEvalExportModal({ demo, config, settings, mode: initialMode, onClose }: Props) {
  const [allCopied, setAllCopied]                 = useState(false)
  const [unfilterVisibility, setUnfilterVisibility] = useState(false)
  const [mode, setMode]                           = useState<RetrievalMode>(initialMode)

  const url         = buildUrl(demo, settings, mode)
  const headerPairs = buildHeaderPairs(settings)
  const visSuffix   = unfilterVisibility ? " — visibility unfiltered" : ""
  const name        = `${config.shortTitle} — ${MODE_LABELS[mode]}${visSuffix}`

  const inputTemplate  = unfilterVisibility
    ? '{"q": "${PROMPT}", "visibility": ["public", "internal", "confidential"]}'
    : '{"q": "${PROMPT}"}'
  const outputTemplate = '{"answer": "${RESULT}"}'

  function copyAll() {
    const headerLines = headerPairs.map(h => `  ${h.key}: ${h.value}`).join("\n")
    const text = [
      `Name: ${name}`,
      `URL: ${url}`,
      `Headers:\n${headerLines}`,
      `Input Type: JSON`,
      `Input Template: ${inputTemplate}`,
      `Output Type: JSON`,
      `Output Template: ${outputTemplate}`,
      `Max Parallel Requests: 1`,
      `Timeout (seconds): 60`,
    ].join("\n\n")
    navigator.clipboard.writeText(text)
    setAllCopied(true)
    setTimeout(() => setAllCopied(false), 1800)
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden"
        style={{ boxShadow: "0 25px 50px rgba(0,0,0,0.5)" }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border)] shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-[var(--accent)] flex items-center justify-center text-white text-xs font-bold">T</div>
            <div>
              <h2 className="text-[14px] font-semibold text-[var(--text)]">Export to TryEval</h2>
              <p className="text-[11px] text-[var(--text-3)] mt-0.5">Copy fields into the Create Endpoint form</p>
            </div>
          </div>
          <button onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-[var(--text-3)] hover:text-[var(--text)] hover:bg-[var(--bg-card)] transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-4">

          {/* Mode picker */}
          <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-3">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--text-4)] mb-2.5">
              Retrieval mode
            </p>
            <div className="grid grid-cols-2 gap-1.5">
              {(Object.keys(MODE_LABELS) as RetrievalMode[]).map(m => (
                <button key={m} onClick={() => setMode(m)}
                  className="flex flex-col items-start px-3 py-2 rounded-lg border text-left transition-all"
                  style={mode === m
                    ? { background: "var(--accent)", borderColor: "var(--accent)", color: "#fff" }
                    : { background: "var(--bg-input)", borderColor: "var(--border)", color: "var(--text-2)" }
                  }>
                  <span className="text-[12px] font-semibold">{MODE_LABELS[m]}</span>
                  <span className="text-[10px] mt-0.5 opacity-60">{MODE_DESCS[m]}</span>
                </button>
              ))}
            </div>
          </div>

          <CopyField label="Name" value={name} />
          <CopyField label="URL" value={url} mono />

          {/* Headers */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-semibold text-[var(--text-2)] uppercase tracking-wide">
              Headers <span className="normal-case font-normal text-[var(--text-3)]">(add one at a time in TryEval)</span>
            </label>
            <div className="space-y-2">
              {headerPairs.map(h => (
                <div key={h.key} className="grid grid-cols-2 gap-2">
                  <CopyField label="Key" value={h.key} mono />
                  <CopyField label="Value" value={h.value} mono />
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <CopyField label="Input Type" value="JSON" />
            <CopyField label="Output Type" value="JSON" />
          </div>

          <CopyField label="Input Template" value={inputTemplate} mono />
          <CopyField label="Output Template" value={outputTemplate} mono />

          {/* Visibility bypass */}
          <label className="flex items-start gap-2.5 bg-[var(--bg-card)] border border-[var(--border)] rounded-lg px-3 py-2.5 cursor-pointer hover:border-[var(--border-hi)] transition-colors">
            <input type="checkbox" checked={unfilterVisibility}
              onChange={e => setUnfilterVisibility(e.target.checked)}
              className="mt-0.5" style={{ accentColor: "var(--accent)" }} />
            <span>
              <strong className="text-[12px] font-semibold text-[var(--text)]">Bypass visibility filter</strong>
              <span className="block text-[11px] text-[var(--text-3)] mt-0.5">
                Surfaces <code className="font-mono text-[10px] bg-[var(--bg-input)] px-1 py-0.5 rounded">internal</code> and <code className="font-mono text-[10px] bg-[var(--bg-input)] px-1 py-0.5 rounded">confidential</code> docs. Use to test the leak failure mode in TryEval.
              </span>
            </span>
          </label>

          <div className="grid grid-cols-2 gap-3">
            <CopyField label="Max Parallel Requests" value="1" />
            <CopyField label="Timeout (seconds)" value="60" />
          </div>

          {!settings.openrouterKey && (
            <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2">
              <svg className="w-3.5 h-3.5 text-amber-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
              </svg>
              <p className="text-[11px] text-amber-500">No OpenRouter key set — add it in Settings first.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3.5 border-t border-[var(--border)] bg-[var(--bg-card)] shrink-0 flex items-center justify-between gap-3">
          <a href="https://www.tryeval.com" target="_blank" rel="noopener noreferrer"
            className="text-[11px] text-[var(--accent)] hover:underline">
            Open TryEval →
          </a>
          <button onClick={copyAll}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-medium transition-all ${
              allCopied ? "bg-green-500 text-white" : "bg-[var(--accent)] text-white hover:opacity-90"
            }`}>
            {allCopied ? "All copied!" : "Copy all fields"}
          </button>
        </div>
      </div>
    </div>
  )
}
