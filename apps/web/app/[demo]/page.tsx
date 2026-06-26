"use client"

import { use, useEffect, useRef, useState } from "react"
import type { ChatMessage, QueryResponse, Settings, Turn } from "@/lib/types"
import { postQuery, type RetrievalMode } from "@/lib/api"
import type { DemoConfig } from "@/lib/demoConfig"
import { MessageBubble } from "../components/MessageBubble"
import { ChunksPanel } from "../components/ChunksPanel"
import { SettingsPanel } from "../components/SettingsPanel"
import { TryEvalExportModal } from "../components/TryEvalExportModal"
import { CorpusModal } from "../components/CorpusModal"

// Per-demo configs — add new demos here as they are built
import lawConfig       from "../../demos/law/web_config"
import insuranceConfig from "../../demos/insurance/web_config"
import healthConfig    from "../../demos/health/web_config"
import educationConfig from "../../demos/education/web_config"
import supportConfig   from "../../demos/support/web_config"

const DEMO_CONFIGS: Record<string, DemoConfig> = {
  law:       lawConfig,
  insurance: insuranceConfig,
  health:    healthConfig,
  education: educationConfig,
  support:   supportConfig,
}

function newId() { return Math.random().toString(36).slice(2) }

const SETTINGS_KEY = "rag-demo-settings"
const _EMPTY: Settings = { openrouterKey: "", cfAccountId: "", cfGatewayId: "" }

function loadSettings(): Settings {
  if (typeof window === "undefined") return _EMPTY
  try {
    const s = JSON.parse(localStorage.getItem(SETTINGS_KEY) ?? "null")
    return s ? { ..._EMPTY, ...s } : _EMPTY
  } catch { return _EMPTY }
}

function saveSettings(s: Settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(s))
}

export default function DemoPage({ params }: { params: Promise<{ demo: string }> }) {
  const { demo } = use(params)
  const config = DEMO_CONFIGS[demo] ?? lawConfig   // fallback to law until all demos are registered

  const [messages, setMessages]           = useState<ChatMessage[]>([])
  const [input, setInput]                 = useState("")
  const [loading, setLoading]             = useState(false)
  const [showSettings, setShowSettings]   = useState(false)
  // Initialize empty to match SSR; load from localStorage after mount to avoid hydration mismatch
  const [settings, setSettings]           = useState<Settings>(_EMPTY)
  const [activeSources, setActiveSources] = useState<string | null>(null)
  const [mode, setMode]                   = useState<RetrievalMode>("hybrid")
  const [showTryEval, setShowTryEval]     = useState(false)
  const [showCorpus, setShowCorpus]       = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef  = useRef<HTMLTextAreaElement>(null)
  const abortRef  = useRef<AbortController | null>(null)

  useEffect(() => {
    setSettings(loadSettings())
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const activeResponse = activeSources
    ? messages.find(m => m.id === activeSources)?.response ?? null
    : null

  const buildHistory = (): Turn[] =>
    messages.filter(m => !m.isLoading && !m.error).map(m => ({ role: m.role, content: m.content }))

  function toggleSources(id: string) {
    setActiveSources(prev => (prev === id ? null : id))
  }

  async function send(q: string) {
    if (!q.trim() || loading) return
    if (!settings.openrouterKey) { setShowSettings(true); return }

    const userId   = newId()
    const assistId = newId()
    const userMsg: ChatMessage = { id: userId,   role: "user",      content: q }
    const loadMsg: ChatMessage = { id: assistId, role: "assistant", content: "", isLoading: true }

    setMessages(prev => [...prev, userMsg, loadMsg])
    setInput("")
    setLoading(true)
    inputRef.current?.focus()

    const ctrl = new AbortController()
    abortRef.current = ctrl

    try {
      const resp = await postQuery(demo, q, buildHistory(), settings, mode, ctrl.signal)
      setMessages(prev =>
        prev.map(m => m.id === assistId
          ? { ...m, isLoading: false, content: resp.answer, response: resp }
          : m),
      )
      setActiveSources(assistId)
    } catch (err: unknown) {
      if ((err as Error).name === "AbortError") return
      const msg = err instanceof Error ? err.message : String(err)
      setMessages(prev =>
        prev.map(m => m.id === assistId ? { ...m, isLoading: false, error: msg, content: "" } : m),
      )
    } finally {
      setLoading(false)
      abortRef.current = null
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input) }
  }

  function handleSettings(s: Settings) { setSettings(s); saveSettings(s) }

  const empty = messages.length === 0
  const iconBg = `bg-${config.primaryColor}-600`
  const iconBgStyle = { backgroundColor: config.primaryColor === "indigo" ? "#4f46e5" : undefined }

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-50">
      {/* ── Header ── */}
      <header className="flex items-center justify-between px-5 py-3 bg-white border-b border-slate-200 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center text-white text-base shadow-sm"
            style={{ backgroundColor: primaryHex(config.primaryColor) }}
          >
            {config.icon}
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900 leading-tight">{config.title}</h1>
            <p className="text-[10px] text-slate-400 leading-tight mt-0.5">{config.subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 bg-amber-50 border border-amber-200 rounded-lg px-2.5 py-1 text-[10px] text-amber-700 font-medium">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            {config.disclaimerChip}
          </div>

          <button
            onClick={() => setShowCorpus(true)}
            className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 border border-slate-200 rounded-lg px-3 py-1.5 hover:bg-slate-50 transition-colors"
            title="View indexed corpus"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Corpus
          </button>

          <button
            onClick={() => setShowTryEval(true)}
            className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 hover:text-indigo-700 border border-slate-200 rounded-lg px-3 py-1.5 hover:bg-indigo-50 hover:border-indigo-300 transition-colors"
            title="Export endpoint config to TryEval"
          >
            <div className="w-4 h-4 rounded bg-indigo-600 flex items-center justify-center text-white text-[9px] font-bold">T</div>
            TryEval
          </button>

          <button
            onClick={() => setShowSettings(true)}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 border border-slate-200 rounded-lg px-3 py-1.5 hover:bg-slate-50 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className={settings.openrouterKey ? "text-slate-500" : "text-red-500 font-medium"}>
              {settings.openrouterKey ? "Settings" : "Add API key"}
            </span>
          </button>
        </div>
      </header>

      {/* ── Body ── */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex flex-col flex-1 overflow-hidden">
          <main className="flex-1 overflow-y-auto px-4 md:px-6 py-6">
            {empty ? (
              <div className="max-w-2xl mx-auto">
                <div className="text-center mb-8 pt-8">
                  <div
                    className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4 shadow-lg"
                    style={{ backgroundColor: primaryHex(config.primaryColor) }}
                  >
                    {config.icon}
                  </div>
                  <h2 className="text-xl font-semibold text-slate-800 mb-1.5">{config.shortTitle}</h2>
                  <p className="text-[11px] text-slate-400">{config.subtitle}</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {config.suggestedQuestions.map(({ q, icon }) => (
                    <button
                      key={q}
                      onClick={() => send(q)}
                      className="flex items-start gap-3 text-left bg-white border border-slate-200 rounded-xl px-4 py-3.5 hover:border-indigo-300 hover:bg-indigo-50 hover:shadow-md transition-all group"
                    >
                      <span className="text-base mt-0.5 shrink-0">{icon}</span>
                      <span className="text-sm text-slate-700 group-hover:text-indigo-700 leading-snug">{q}</span>
                    </button>
                  ))}
                </div>

                {config.about && (
                  <div
                    className="mt-6 pl-4 py-3 pr-4 rounded-r-xl"
                    style={{
                      borderLeft: `3px solid ${primaryHex(config.primaryColor)}`,
                      background: `${primaryHex(config.primaryColor)}0d`,
                    }}
                  >
                    <p className="text-[11px] font-semibold mb-1" style={{ color: primaryHex(config.primaryColor) }}>
                      What this covers
                    </p>
                    <p className="text-[13px] text-slate-600 leading-relaxed">{config.about}</p>
                  </div>
                )}

              </div>
            ) : (
              <div className="max-w-2xl mx-auto space-y-6">
                {messages.map(m => (
                  <MessageBubble
                    key={m.id}
                    message={m}
                    config={config}
                    onShowSources={toggleSources}
                    activeSources={activeSources}
                  />
                ))}
                <div ref={bottomRef} />
              </div>
            )}
          </main>

          {/* ── Input ── */}
          <div className="border-t border-slate-200 bg-white px-4 md:px-6 py-3.5 shrink-0">
            <div className="max-w-2xl mx-auto">
              <div className="flex items-center gap-1.5 mb-2.5 flex-wrap">
                {([
                  { id: "hybrid",  label: "Hybrid",  desc: "Dense + BM25 → RRF fusion" },
                  { id: "vanilla", label: "RAG only", desc: "Dense vector search only" },
                  { id: "bm25",    label: "BM25",     desc: "Full-text search only" },
                  { id: "hyde",    label: "HyDE",     desc: "Hypothetical doc → embed → retrieve" },
                ] as const).map(m => (
                  <button
                    key={m.id}
                    title={m.desc}
                    onClick={() => setMode(m.id)}
                    className={`px-2.5 py-1 text-[11px] font-medium rounded-lg border transition-colors ${
                      mode === m.id
                        ? "bg-indigo-600 text-white border-indigo-600"
                        : "bg-white text-slate-500 border-slate-200 hover:border-indigo-300 hover:text-indigo-600"
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
                <span className="text-[10px] text-slate-400 ml-0.5 hidden sm:inline">
                  {mode === "hybrid"  && "Dense + BM25 → RRF fusion"}
                  {mode === "vanilla" && "Dense vector search only"}
                  {mode === "bm25"    && "BM25 full-text only"}
                  {mode === "hyde"    && "Generate hypothetical doc → embed → retrieve"}
                </span>
              </div>
              <div className="flex gap-2 items-end bg-white border border-slate-200 rounded-2xl px-4 py-2.5 shadow-sm focus-within:border-indigo-400 focus-within:ring-1 focus-within:ring-indigo-400 transition-all">
                <textarea
                  ref={inputRef}
                  className="flex-1 resize-none text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none bg-transparent min-h-[24px] max-h-32"
                  placeholder={config.inputPlaceholder}
                  rows={1}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                />
                <button
                  onClick={() => send(input)}
                  disabled={!input.trim() || loading}
                  className="w-8 h-8 shrink-0 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white disabled:text-slate-400 flex items-center justify-center transition-colors"
                  aria-label="Send"
                >
                  {loading ? (
                    <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                  ) : (
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                    </svg>
                  )}
                </button>
              </div>
              <p className="text-center text-[10px] text-slate-400 mt-1.5">
                Enter to send · Shift+Enter for newline
              </p>
            </div>
          </div>
        </div>

        {/* ── Sources panel ── */}
        {activeResponse && (
          <div className="hidden md:flex w-80 lg:w-96 shrink-0 border-l border-slate-200 flex-col overflow-hidden">
            <ChunksPanel
              chunks={activeResponse.retrieved_chunks}
              config={config}
              onClose={() => setActiveSources(null)}
            />
          </div>
        )}
      </div>

      {showSettings && (
        <SettingsPanel
          settings={settings}
          onSave={handleSettings}
          onClose={() => setShowSettings(false)}
        />
      )}

      {showTryEval && (
        <TryEvalExportModal
          demo={demo}
          config={config}
          settings={settings}
          mode={mode}
          onClose={() => setShowTryEval(false)}
        />
      )}

      {showCorpus && (
        <CorpusModal
          demo={demo}
          config={config}
          onClose={() => setShowCorpus(false)}
        />
      )}
    </div>
  )
}

/** Map Tailwind color name to a hex for inline style (avoids purging dynamic class names) */
function primaryHex(color: string): string {
  const map: Record<string, string> = {
    indigo:  "#4f46e5",
    teal:    "#0d9488",
    emerald: "#059669",
    sky:     "#0284c7",
    amber:   "#d97706",
    violet:  "#7c3aed",
    rose:    "#e11d48",
  }
  return map[color] ?? "#4f46e5"
}
