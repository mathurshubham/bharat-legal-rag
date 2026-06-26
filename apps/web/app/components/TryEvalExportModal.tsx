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
  if (settings.openrouterKey) {
    pairs.push({ key: "X-OpenRouter-Key", value: settings.openrouterKey })
  }
  return pairs
}

function CopyField({
  label, value, mono = false, rows = 1,
}: { label: string; value: string; mono?: boolean; rows?: number }) {
  const [copied, setCopied] = useState(false)
  function copy() {
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-slate-600 uppercase tracking-wide">{label}</label>
        <button
          onClick={copy}
          className={`flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-md transition-colors ${
            copied ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500 hover:bg-slate-200 hover:text-slate-700"
          }`}
        >
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      {rows > 1 ? (
        <textarea
          readOnly value={value} rows={rows}
          className={`w-full rounded-lg bg-slate-50 border border-slate-200 px-3 py-2 text-xs leading-relaxed focus:outline-none resize-none ${mono ? "font-mono text-slate-700" : "text-slate-800"}`}
        />
      ) : (
        <div className={`w-full rounded-lg bg-slate-50 border border-slate-200 px-3 py-2 text-xs leading-relaxed break-all select-all ${mono ? "font-mono text-slate-700" : "text-slate-800"}`}>
          {value}
        </div>
      )}
    </div>
  )
}

export function TryEvalExportModal({ demo, config, settings, mode, onClose }: Props) {
  const [allCopied, setAllCopied]                 = useState(false)
  const [unfilterVisibility, setUnfilterVisibility] = useState(false)

  const url         = buildUrl(demo, settings, mode)
  const headerPairs = buildHeaderPairs(settings)
  const visSuffix   = unfilterVisibility ? " — visibility unfiltered" : ""
  const name        = `${config.shortTitle} — ${MODE_LABELS[mode]}${visSuffix}`

  // TryEval uses ${PROMPT} and ${RESULT} as template variables
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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">T</div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Export to TryEval</h2>
              <p className="text-[11px] text-slate-400 mt-0.5">Copy fields into the Create Endpoint form</p>
            </div>
          </div>
          <button onClick={onClose} className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-4">
          <div className="flex items-center gap-2 bg-indigo-50 border border-indigo-200 rounded-xl px-3.5 py-2.5">
            <span className="text-xs text-indigo-700">
              Exporting config for <strong>{MODE_LABELS[mode]}</strong> mode on <strong>{config.shortTitle}</strong>.
            </span>
          </div>

          <CopyField label="Name" value={name} />
          <CopyField label="URL" value={url} mono />

          {/* Headers — one row per header, matching TryEval's "Add Header" key-value UI */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-600 uppercase tracking-wide">
              Headers <span className="normal-case font-normal text-slate-400">(add one at a time in TryEval)</span>
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

          <label className="flex items-start gap-2.5 text-[11px] text-slate-600 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 cursor-pointer hover:bg-slate-100 transition-colors">
            <input
              type="checkbox"
              checked={unfilterVisibility}
              onChange={e => setUnfilterVisibility(e.target.checked)}
              className="mt-0.5"
            />
            <span>
              <strong className="text-slate-800">Bypass visibility filter</strong>
              <span className="block text-slate-500 mt-0.5">
                Includes <code className="font-mono text-[10px]">internal</code> and <code className="font-mono text-[10px]">confidential</code> docs in retrieval. Use to demonstrate the leak failure mode in TryEval — expect refusal/confidentiality rubrics to drop.
              </span>
            </span>
          </label>

          <div className="grid grid-cols-2 gap-3">
            <CopyField label="Max Parallel Requests" value="1" />
            <CopyField label="Timeout (seconds)" value="60" />
          </div>

          {!settings.openrouterKey && (
            <p className="text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              No OpenRouter key set — add it in Settings first so it is included in the headers.
            </p>
          )}
        </div>

        <div className="px-5 py-3.5 border-t border-slate-100 bg-slate-50 shrink-0 flex items-center justify-between gap-3">
          <a href="https://www.tryeval.com" target="_blank" rel="noopener noreferrer" className="text-[11px] text-indigo-600 hover:underline">
            Open TryEval →
          </a>
          <button
            onClick={copyAll}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors ${allCopied ? "bg-green-600 text-white" : "bg-indigo-600 text-white hover:bg-indigo-700"}`}
          >
            {allCopied ? "All copied!" : "Copy all fields"}
          </button>
        </div>
      </div>
    </div>
  )
}
