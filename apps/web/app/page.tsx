"use client"

import { useEffect, useRef, useState } from "react"
import type { ChatMessage, Settings, Turn } from "@/lib/types"
import { postQuery } from "@/lib/api"
import { MessageBubble } from "./components/MessageBubble"
import { SettingsPanel } from "./components/SettingsPanel"

const SUGGESTED = [
  "What is the punishment for murder under the BNS 2023?",
  "What are the fundamental rights guaranteed under the Constitution?",
  "What constitutes a valid contract under the Indian Contract Act?",
  "What are the rights of a consumer under the Consumer Protection Act 2019?",
]

function newId() {
  return Math.random().toString(36).slice(2)
}

const _EMPTY_SETTINGS: Settings = { openrouterKey: "", cohereKey: "", cfAccountId: "", cfGatewayId: "" }

function loadSettings(): Settings {
  if (typeof window === "undefined") return _EMPTY_SETTINGS
  try {
    const stored = JSON.parse(localStorage.getItem("legal-rag-settings") ?? "null")
    return stored ? { ..._EMPTY_SETTINGS, ...stored } : _EMPTY_SETTINGS
  } catch {
    return _EMPTY_SETTINGS
  }
}

function saveSettings(s: Settings) {
  localStorage.setItem("legal-rag-settings", JSON.stringify(s))
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [settings, setSettings] = useState<Settings>(loadSettings)
  const bottomRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const buildHistory = (): Turn[] =>
    messages
      .filter(m => !m.isLoading && !m.error)
      .map(m => ({ role: m.role, content: m.content }))

  async function send(q: string) {
    if (!q.trim() || loading) return
    if (!settings.openrouterKey) {
      setShowSettings(true)
      return
    }

    const userMsg: ChatMessage = { id: newId(), role: "user", content: q }
    const loadingMsg: ChatMessage = { id: newId(), role: "assistant", content: "", isLoading: true }
    setMessages(prev => [...prev, userMsg, loadingMsg])
    setInput("")
    setLoading(true)

    const history = buildHistory()
    const ctrl = new AbortController()
    abortRef.current = ctrl

    try {
      const resp = await postQuery(q, history, settings, ctrl.signal)
      setMessages(prev =>
        prev.map(m =>
          m.id === loadingMsg.id
            ? { ...m, isLoading: false, content: resp.answer, response: resp }
            : m,
        ),
      )
    } catch (err: unknown) {
      if ((err as Error).name === "AbortError") return
      const msg = err instanceof Error ? err.message : String(err)
      setMessages(prev =>
        prev.map(m =>
          m.id === loadingMsg.id
            ? { ...m, isLoading: false, error: msg, content: "" }
            : m,
        ),
      )
    } finally {
      setLoading(false)
      abortRef.current = null
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  function handleSettings(s: Settings) {
    setSettings(s)
    saveSettings(s)
  }

  const empty = messages.length === 0

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">L</div>
          <div>
            <h1 className="text-sm font-semibold text-gray-900">Indian Legal RAG</h1>
            <p className="text-[10px] text-gray-400">BNS · Constitution · Contract Act · CP 2019 · DPDP</p>
          </div>
        </div>
        <button
          onClick={() => setShowSettings(true)}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Settings
        </button>
      </header>

      {/* not-legal-advice banner */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-1.5 text-center text-[11px] text-amber-800">
        For research purposes only. Not legal advice. Consult a qualified advocate for specific legal matters.
      </div>

      {/* messages */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {empty && (
            <div className="text-center space-y-6 pt-12">
              <p className="text-gray-500 text-sm">Ask a question about Indian law</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {SUGGESTED.map(q => (
                  <button
                    key={q}
                    onClick={() => send(q)}
                    className="text-left text-sm bg-white border border-gray-200 rounded-xl px-4 py-3 text-gray-700 hover:border-indigo-300 hover:bg-indigo-50 transition-colors shadow-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(m => (
            <MessageBubble key={m.id} message={m} />
          ))}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* input */}
      <div className="border-t border-gray-200 bg-white px-4 py-3">
        <div className="max-w-3xl mx-auto flex gap-3 items-end">
          <textarea
            className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[44px] max-h-36"
            placeholder="Ask about Indian law…"
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="h-11 px-5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            {loading ? "…" : "Send"}
          </button>
        </div>
        <p className="text-center text-[10px] text-gray-400 mt-1.5">Enter to send · Shift+Enter for newline</p>
      </div>

      {showSettings && (
        <SettingsPanel
          settings={settings}
          onSave={handleSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}
