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
        <label className="text-[13px] font-medium text-[var(--text)]">{label}</label>
        {hint && <p className="text-[11px] text-[var(--text-3)] mt-0.5">{hint}</p>}
      </div>
      <input
        type={type}
        className="w-full rounded-lg border border-[var(--border-hi)] bg-[var(--bg-input)] px-3.5 py-2.5 text-[13px] text-[var(--text)] placeholder:text-[var(--text-3)] focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]/30 transition-all"
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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden"
        style={{ boxShadow: "0 25px 50px rgba(0,0,0,0.5)" }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border)]">
          <div>
            <h2 className="text-[14px] font-semibold text-[var(--text)]">Settings</h2>
            <p className="text-[11px] text-[var(--text-3)] mt-0.5">Keys sent as headers only — never stored server-side</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-[var(--text-3)] hover:text-[var(--text)] hover:bg-[var(--bg-card)] transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-5 py-5 space-y-4">
          <Field
            label="OpenRouter API Key"
            hint="Optional · overrides the server default key"
            type="password"
            placeholder="sk-or-..."
            value={draft.openrouterKey}
            onChange={v => setDraft(d => ({ ...d, openrouterKey: v }))}
          />
          <div className="border-t border-[var(--border)] pt-4 space-y-4">
            <p className="text-[10px] font-semibold text-[var(--text-4)] uppercase tracking-wide">
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
        <div className="flex gap-2.5 px-5 py-4 border-t border-[var(--border)] bg-[var(--bg-card)]">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 text-[13px] font-medium rounded-lg border border-[var(--border)] text-[var(--text-2)] hover:text-[var(--text)] hover:border-[var(--border-hi)] hover:bg-[var(--bg-surface)] transition-all"
          >
            Cancel
          </button>
          <button
            onClick={() => { onSave(draft); onClose() }}
            className="flex-1 px-4 py-2.5 text-[13px] font-medium rounded-lg bg-[var(--accent)] text-white hover:opacity-90 transition-all"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
