"use client"

import { useEffect, useState } from "react"
import {
  fetchChapters,
  generateQuestions,
  type Chapter,
  type ChapterSection,
  type LanguageMode,
} from "@/lib/api"
import type { Settings } from "@/lib/types"

interface Props {
  demo: string
  board: "cbse" | "ib" | "all"
  settings: Settings
  onClose: () => void
}

type Tab = "outline" | "questions"

const TYPE_BADGE: Record<string, string> = {
  grammar:     "bg-blue-50 text-blue-700",
  vocab:       "bg-purple-50 text-purple-700",
  exercise:    "bg-amber-50 text-amber-700",
  reading:     "bg-emerald-50 text-emerald-700",
  listening:   "bg-cyan-50 text-cyan-700",
  dialogue:    "bg-pink-50 text-pink-700",
  culture:     "bg-rose-50 text-rose-700",
  objectives:  "bg-gray-100 text-gray-700",
  revision:    "bg-orange-50 text-orange-700",
  exploration: "bg-teal-50 text-teal-700",
  content:     "bg-slate-50 text-slate-700",
}

export function TeacherToolsModal({ demo, board, settings, onClose }: Props) {
  const [tab, setTab] = useState<Tab>("outline")

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl w-full max-w-4xl max-h-[88vh] flex flex-col overflow-hidden"
        style={{ boxShadow: "0 25px 50px rgba(0,0,0,0.5)" }}>

        {/* Header + tabs */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-[var(--border)] shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="text-[14px] font-semibold text-[var(--text)]">Teacher tools</h2>
            <div className="flex items-center gap-0.5 bg-[var(--bg-card)] border border-[var(--border)] rounded-full p-0.5">
              {(["outline","questions"] as Tab[]).map(t => (
                <button key={t}
                  onClick={() => setTab(t)}
                  className={`px-3 py-1 text-[11px] font-medium rounded-full transition-all duration-150 ${
                    tab === t
                      ? "bg-[var(--text)] text-[var(--bg)] shadow-sm"
                      : "text-[var(--text-3)] hover:text-[var(--text-2)]"
                  }`}
                >
                  {t === "outline" ? "Chapter outline" : "Question generator"}
                </button>
              ))}
            </div>
          </div>
          <button onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-[var(--text-3)] hover:text-[var(--text)] hover:bg-[var(--bg-card)] transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1 px-5 py-4">
          {tab === "outline" && <OutlineTab demo={demo} board={board} />}
          {tab === "questions" && <QuestionsTab demo={demo} board={board} settings={settings} />}
        </div>
      </div>
    </div>
  )
}

// ─── Outline tab ────────────────────────────────────────────────────────────
function OutlineTab({ demo, board }: { demo: string; board: string }) {
  const [data, setData] = useState<Chapter[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState<Set<string>>(new Set())

  useEffect(() => {
    setLoading(true)
    fetchChapters(demo, board).then(r => {
      setData(r?.chapters ?? [])
      setLoading(false)
    })
  }, [demo, board])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-5 h-5 border border-[var(--border-hi)] border-t-[var(--accent)] rounded-full animate-spin" />
      </div>
    )
  }
  if (!data || data.length === 0) {
    return <p className="text-[13px] text-[var(--text-3)] text-center py-8">No chapters indexed for this scope.</p>
  }
  return (
    <div className="space-y-2">
      {data.map(ch => {
        const key = `${ch.doc_id}::${ch.id}`
        const isOpen = open.has(key)
        const byType = ch.sections.reduce<Record<string, number>>((a, s) => {
          const t = s.type ?? "?"; a[t] = (a[t] ?? 0) + 1; return a
        }, {})
        return (
          <div key={key} className="border border-[var(--border)] rounded-lg bg-[var(--bg-card)]">
            <button
              onClick={() => {
                const n = new Set(open)
                isOpen ? n.delete(key) : n.add(key)
                setOpen(n)
              }}
              className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-[var(--bg-surface)] transition-colors rounded-lg"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[13px] font-medium text-[var(--text)]">{ch.id}</span>
                  <span className="text-[10px] text-[var(--text-3)]">·</span>
                  <span className="text-[11px] text-[var(--text-3)]">{ch.doc_title}</span>
                  {ch.level && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--bg-surface)] text-[var(--text-3)] border border-[var(--border)]">
                      {ch.level}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  {Object.entries(byType).map(([t, n]) => (
                    <span key={t} className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_BADGE[t] ?? "bg-slate-50 text-slate-700"}`}>
                      {t} · {n}
                    </span>
                  ))}
                </div>
              </div>
              <span className="text-[var(--text-3)] text-[11px]">{ch.sections.length} sections</span>
            </button>
            {isOpen && (
              <div className="border-t border-[var(--border)] divide-y divide-[var(--border)]">
                {ch.sections.map((s, i) => (
                  <SectionRow key={i} s={s} />
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

function SectionRow({ s }: { s: ChapterSection }) {
  return (
    <div className="px-4 py-2 hover:bg-[var(--bg-surface)] transition-colors">
      <div className="flex items-center gap-2 flex-wrap">
        {s.type && (
          <span className={`text-[9px] px-1.5 py-0.5 rounded ${TYPE_BADGE[s.type] ?? "bg-slate-50 text-slate-700"}`}>
            {s.type}
          </span>
        )}
        <span className="text-[11px] text-[var(--text-2)] font-mono">{s.section_ref}</span>
      </div>
      <p className="text-[11px] text-[var(--text-3)] mt-1 line-clamp-2">{s.preview}</p>
    </div>
  )
}

// ─── Questions tab ──────────────────────────────────────────────────────────
function QuestionsTab({ demo, board, settings }: { demo: string; board: string; settings: Settings }) {
  const [chapter, setChapter] = useState("")
  const [count, setCount] = useState(10)
  const [difficulty, setDifficulty] = useState<string>("")
  const [types, setTypes] = useState<string[]>(["mcq","fill_in","short"])
  const [language, setLanguage] = useState<LanguageMode>("bilingual")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string>("")

  const toggleType = (t: string) =>
    setTypes(types.includes(t) ? types.filter(x => x !== t) : [...types, t])

  const onGenerate = async () => {
    setLoading(true); setResult("")
    const r = await generateQuestions(demo, {
      chapter: chapter || undefined,
      board: board === "all" ? undefined : board,
      count, difficulty: difficulty || undefined,
      question_types: types,
      language_mode: language,
    }, settings)
    setLoading(false)
    if (!r) { setResult("Error generating questions."); return }
    setResult(r.questions_markdown)
  }

  return (
    <div className="space-y-4">
      {/* Form */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] text-[var(--text-3)] mb-1">Chapter (e.g. "Leçon 6" or leave blank)</label>
          <input value={chapter} onChange={e => setChapter(e.target.value)}
            placeholder="Leçon 6"
            className="w-full text-[12px] bg-[var(--bg-input)] border border-[var(--border)] rounded-lg px-3 py-1.5 focus:outline-none focus:border-[var(--border-hi)]" />
        </div>
        <div>
          <label className="block text-[11px] text-[var(--text-3)] mb-1">Count</label>
          <input type="number" min={1} max={50} value={count}
            onChange={e => setCount(parseInt(e.target.value || "10"))}
            className="w-full text-[12px] bg-[var(--bg-input)] border border-[var(--border)] rounded-lg px-3 py-1.5 focus:outline-none focus:border-[var(--border-hi)]" />
        </div>
        <div>
          <label className="block text-[11px] text-[var(--text-3)] mb-1">Difficulty (CEFR)</label>
          <select value={difficulty} onChange={e => setDifficulty(e.target.value)}
            className="w-full text-[12px] bg-[var(--bg-input)] border border-[var(--border)] rounded-lg px-3 py-1.5 focus:outline-none focus:border-[var(--border-hi)]">
            <option value="">Any</option>
            <option value="A1">A1</option>
            <option value="A2">A2</option>
            <option value="B1">B1</option>
            <option value="B2">B2</option>
          </select>
        </div>
        <div>
          <label className="block text-[11px] text-[var(--text-3)] mb-1">Answer language</label>
          <select value={language} onChange={e => setLanguage(e.target.value as LanguageMode)}
            className="w-full text-[12px] bg-[var(--bg-input)] border border-[var(--border)] rounded-lg px-3 py-1.5 focus:outline-none focus:border-[var(--border-hi)]">
            <option value="fr">French only</option>
            <option value="en">English only</option>
            <option value="bilingual">Bilingual (FR + EN)</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-[11px] text-[var(--text-3)] mb-1">Question types</label>
        <div className="flex flex-wrap gap-2">
          {["mcq","fill_in","short","essay","true_false","translation"].map(t => (
            <button key={t}
              onClick={() => toggleType(t)}
              className={`text-[11px] px-3 py-1 rounded-full border transition-all ${
                types.includes(t)
                  ? "bg-[var(--text)] text-[var(--bg)] border-[var(--text)]"
                  : "bg-[var(--bg-card)] text-[var(--text-3)] border-[var(--border)] hover:border-[var(--border-hi)]"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>
      <button onClick={onGenerate} disabled={loading || types.length === 0}
        className="w-full py-2 rounded-lg bg-[var(--accent)] text-white text-[12px] font-medium disabled:opacity-50 transition-opacity">
        {loading ? "Generating…" : `Generate ${count} questions`}
      </button>

      {/* Result */}
      {result && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-[12px] font-semibold text-[var(--text)]">Question bank</h3>
            <button onClick={() => navigator.clipboard.writeText(result)}
              className="text-[11px] text-[var(--text-3)] hover:text-[var(--text)] transition-colors">
              Copy markdown
            </button>
          </div>
          <pre className="bg-[var(--bg-card)] border border-[var(--border)] rounded-lg px-3 py-3 text-[12px] text-[var(--text-2)] whitespace-pre-wrap overflow-x-auto leading-relaxed">{result}</pre>
        </div>
      )}
    </div>
  )
}
