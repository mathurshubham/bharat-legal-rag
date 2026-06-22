"use client"

import type { RetrievedChunk } from "@/lib/types"

interface Props {
  chunks: RetrievedChunk[]
  activeMessageId?: string
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

const DOC_LABELS: Record<string, string> = {
  BNS_2023: "BNS 2023",
  BNSS_2023: "BNSS 2023",
  BSA_2023: "BSA 2023",
  CONSTITUTION: "Constitution",
  CONSUMER_PROTECTION_2019: "CP Act 2019",
  CONTRACT_ACT_1872: "Contract Act",
  DPDP_2023: "DPDP 2023",
  LAW_MAPPINGS: "Law Mappings",
}

const DOC_COLORS: Record<string, string> = {
  BNS_2023: "bg-red-50 text-red-700 border-red-200",
  BNSS_2023: "bg-orange-50 text-orange-700 border-orange-200",
  BSA_2023: "bg-yellow-50 text-yellow-700 border-yellow-200",
  CONSTITUTION: "bg-blue-50 text-blue-700 border-blue-200",
  CONSUMER_PROTECTION_2019: "bg-green-50 text-green-700 border-green-200",
  CONTRACT_ACT_1872: "bg-purple-50 text-purple-700 border-purple-200",
  DPDP_2023: "bg-pink-50 text-pink-700 border-pink-200",
  LAW_MAPPINGS: "bg-slate-50 text-slate-700 border-slate-200",
}

export function ChunksPanel({ chunks, onClose }: Props) {
  const maxRerank = Math.max(...chunks.map(c => c.rerank_score ?? 0), 0.01)

  return (
    <div className="flex flex-col h-full bg-white border-l border-slate-200">
      {/* Header */}
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

      {/* Chunks */}
      <div className="overflow-y-auto flex-1 p-3 space-y-2.5">
        {chunks.map((c, i) => (
          <div
            key={c.id}
            className="rounded-xl border border-slate-100 bg-slate-50 hover:bg-white hover:border-slate-200 hover:shadow-sm p-3.5 transition-all"
          >
            {/* Top row */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[11px] font-semibold font-mono text-indigo-600">
                  {c.section_ref}
                </span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium ${DOC_COLORS[c.doc_id] ?? "bg-slate-50 text-slate-600 border-slate-200"}`}>
                  {DOC_LABELS[c.doc_id] ?? c.doc_id}
                </span>
              </div>
              <span className="text-[10px] text-slate-400 shrink-0">#{i + 1}</span>
            </div>

            {/* Content */}
            <p className="text-[12px] text-slate-600 leading-relaxed line-clamp-5 mb-2.5">
              {c.content}
            </p>

            {/* Scores */}
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
        ))}
      </div>
    </div>
  )
}
