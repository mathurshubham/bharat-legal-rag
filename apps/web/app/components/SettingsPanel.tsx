"use client"

import { useState } from "react"
import type { Settings } from "@/lib/types"

interface Props {
  settings: Settings
  onSave: (s: Settings) => void
  onClose: () => void
}

export function SettingsPanel({ settings, onSave, onClose }: Props) {
  const [draft, setDraft] = useState<Settings>(settings)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 space-y-5">
        <h2 className="text-lg font-semibold text-gray-900">Settings</h2>

        <div className="space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-gray-700">OpenRouter API Key *</span>
            <input
              type="password"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="sk-or-..."
              value={draft.openrouterKey}
              onChange={e => setDraft(d => ({ ...d, openrouterKey: e.target.value }))}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">
              Cohere API Key
              <span className="ml-1 text-xs text-gray-400 font-normal">(reranking — optional, free tier available)</span>
            </span>
            <input
              type="password"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="..."
              value={draft.cohereKey}
              onChange={e => setDraft(d => ({ ...d, cohereKey: e.target.value }))}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Cloudflare Account ID</span>
            <input
              type="text"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="abc123..."
              value={draft.cfAccountId}
              onChange={e => setDraft(d => ({ ...d, cfAccountId: e.target.value }))}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Cloudflare Gateway ID</span>
            <input
              type="text"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="legal-rag-gateway"
              value={draft.cfGatewayId}
              onChange={e => setDraft(d => ({ ...d, cfGatewayId: e.target.value }))}
            />
          </label>
        </div>

        <p className="text-xs text-gray-500">
          Keys are sent as request headers only — never stored or logged.
        </p>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={() => { onSave(draft); onClose() }}
            disabled={!draft.openrouterKey}
            className="px-4 py-2 text-sm rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
