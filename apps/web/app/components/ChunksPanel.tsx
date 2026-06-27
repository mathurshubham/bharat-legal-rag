"use client"

import type { RetrievedChunk } from "@/lib/types"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  chunks: RetrievedChunk[]
  config: DemoConfig
  accent: string
  onClose: () => void
}

function ScoreBar({ score, max = 1, accent }: { score: number; max?: number; accent: string }) {
  const pct = Math.min((score / max) * 100, 100)
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-0.5 bg-[var(--border)] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, backgroundColor: accent }}
        />
      </div>
      <span className="text-[10px] text-[var(--text-4)] tabular-nums w-7 text-right">
        {score.toFixed(2)}
      </span>
    </div>
  )
}

export function ChunksPanel({ chunks, config, accent, onClose }: Props) {
  const maxRerank = Math.max(...chunks.map(c => c.rerank_score ?? 0), 0.01)

  return (
    <div className="flex flex-col h-full bg-[var(--bg)]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)] shrink-0">
        <div>
          <p className="text-[13px] font-semibold text-[var(--text)]">Sources</p>
          <p className="text-[11px] text-[var(--text-4)] mt-0.5">{chunks.length} retrieved chunks</p>
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

      {/* Chunks */}
      <div className="overflow-y-auto flex-1 p-3 space-y-2">
        {chunks.map((c, i) => {
          const colorClass = config.docColors[c.doc_id] ?? "bg-[var(--bg-card)] text-[var(--text-3)] border-[var(--border)]"
          const label = c.doc_title ?? c.doc_id
          return (
            <div
              key={c.id}
              className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--border-hi)] p-3 transition-colors"
            >
              {/* Top row */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5 flex-wrap min-w-0">
                  <span className="citation-chip">{c.section_ref}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium shrink-0 ${colorClass}`}>
                    {label}
                  </span>
                </div>
                <span className="text-[10px] text-[var(--text-4)] shrink-0">#{i + 1}</span>
              </div>

              {/* Content */}
              <p className="text-[11px] text-[var(--text-2)] leading-relaxed line-clamp-4 mb-2.5 font-mono">
                {c.content}
              </p>

              {/* Scores */}
              <div className="space-y-1.5">
                {c.rerank_score != null && (
                  <div>
                    <p className="text-[9px] uppercase tracking-wide text-[var(--text-4)] mb-0.5">Rerank</p>
                    <ScoreBar score={c.rerank_score} max={maxRerank} accent={accent} />
                  </div>
                )}
                <div>
                  <p className="text-[9px] uppercase tracking-wide text-[var(--text-4)] mb-0.5">Retrieval</p>
                  <ScoreBar score={c.score} accent={accent} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
