"use client"

import type { RetrievedChunk } from "@/lib/types"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  chunks: RetrievedChunk[]
  config: DemoConfig
  onClose: () => void
}

function ScoreBar({ score, max = 1 }: { score: number; max?: number }) {
  const pct = Math.min((score / max) * 100, 100)
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex-1 h-1 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-400 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[10px] text-slate-400 tabular-nums w-8 text-right">
        {score.toFixed(2)}
      </span>
    </div>
  )
}

export function ChunksPanel({ chunks, config, onClose }: Props) {
  const maxRerank = Math.max(...chunks.map(c => c.rerank_score ?? 0), 0.01)

  return (
    <div className="flex flex-col h-full bg-white border-l border-slate-200">
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-slate-100">
        <div>
          <p className="text-sm font-semibold text-slate-800">Sources</p>
          <p className="text-[11px] text-slate-400 mt-0.5">{chunks.length} retrieved chunks</p>
        </div>
        <button
          onClick={onClose}
          className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          aria-label="Close sources"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="overflow-y-auto flex-1 p-3 space-y-2.5">
        {chunks.map((c, i) => {
          const colorClass = config.docColors[c.doc_id] ?? "bg-slate-50 text-slate-600 border-slate-200"
          // Use server-provided doc_title if present; fall back to doc_id
          const label = c.doc_title ?? c.doc_id
          return (
            <div
              key={c.id}
              className="rounded-xl border border-slate-100 bg-slate-50 hover:bg-white hover:border-slate-200 hover:shadow-sm p-3.5 transition-all"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[11px] font-semibold font-mono text-indigo-600">
                    {c.section_ref}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium ${colorClass}`}>
                    {label}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 shrink-0">#{i + 1}</span>
              </div>

              <p className="text-[12px] text-slate-600 leading-relaxed line-clamp-5 mb-2.5">
                {c.content}
              </p>

              <div className="space-y-1">
                {c.rerank_score != null && (
                  <div>
                    <p className="text-[10px] text-slate-400 mb-0.5">Rerank</p>
                    <ScoreBar score={c.rerank_score} max={maxRerank} />
                  </div>
                )}
                <div>
                  <p className="text-[10px] text-slate-400 mb-0.5">Retrieval</p>
                  <ScoreBar score={c.score} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
