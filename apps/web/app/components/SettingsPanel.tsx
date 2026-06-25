"use client"

import { useState } from "react"
import type { Settings } from "@/lib/types"

interface Props {
  settings: Settings
  onSave: (s: Settings) => void
  onClose: () => void
}

function Field({
  label, hint, type = "text", placeholder, value, onChange,
}: {
  label: string; hint?: string; type?: string; placeholder: string; value: string; onChange: (v: string) => void
}) {
  return (
    <div className="space-y-1.5">
      <div>
        <label className="text-sm font-medium text-slate-700">{label}</label>
        {hint && <p className="text-[11px] text-slate-400 mt-0.5">{hint}</p>}
      </div>
      <input
        type={type}
        className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400 focus:bg-white transition-all"
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
      />
    </div>
  )
}

export function SettingsPanel({ settings, onSave, onClose }: Props) {
  const [draft, setDraft] = useState<Settings>(settings)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Settings</h2>
            <p className="text-[11px] text-slate-400 mt-0.5">Keys sent as headers only — never stored server-side</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4">
          <Field
            label="OpenRouter API Key"
            hint="Required · used for generation and reranking"
            type="password"
            placeholder="sk-or-..."
            value={draft.openrouterKey}
            onChange={v => setDraft(d => ({ ...d, openrouterKey: v }))}
          />
          <div className="border-t border-slate-100 pt-4 space-y-4">
            <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wide">
              Cloudflare AI Gateway — optional
            </p>
            <Field
              label="Account ID"
              placeholder="abc123..."
              value={draft.cfAccountId}
              onChange={v => setDraft(d => ({ ...d, cfAccountId: v }))}
            />
            <Field
              label="Gateway ID"
              placeholder="my-rag-gateway"
              value={draft.cfGatewayId}
              onChange={v => setDraft(d => ({ ...d, cfGatewayId: v }))}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 px-6 py-4 border-t border-slate-100 bg-slate-50">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => { onSave(draft); onClose() }}
            disabled={!draft.openrouterKey}
            className="flex-1 px-4 py-2.5 text-sm rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
