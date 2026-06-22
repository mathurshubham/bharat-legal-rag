"use client"

import type { RetrievedChunk } from "@/lib/types"

interface Props {
  chunks: RetrievedChunk[]
  onClose: () => void
}

export function ChunksPanel({ chunks, onClose }: Props) {
  return (
    <div className="flex flex-col h-full border-l border-gray-200 bg-gray-50 w-96 min-w-[320px] overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
        <span className="text-sm font-semibold text-gray-700">
          Retrieved chunks ({chunks.length})
        </span>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          aria-label="Close panel"
        >
          ×
        </button>
      </div>
      <div className="overflow-y-auto flex-1 p-3 space-y-3">
        {chunks.map((c, i) => (
          <div key={c.id} className="rounded-lg border border-gray-200 bg-white p-3 text-xs shadow-sm">
            <div className="flex items-start justify-between gap-2 mb-1">
              <span className="font-mono font-semibold text-indigo-700 break-all">{c.section_ref}</span>
              <div className="flex flex-col items-end shrink-0 text-gray-400 text-[10px] leading-tight">
                {c.rerank_score != null && (
                  <span title="Rerank score">r: {c.rerank_score.toFixed(3)}</span>
                )}
                <span title="Retrieval score">s: {c.score.toFixed(4)}</span>
              </div>
            </div>
            <p className="text-gray-500 text-[10px] mb-1">{c.doc_id.replace(/_/g, " ")}</p>
            <p className="text-gray-700 line-clamp-6 whitespace-pre-wrap leading-relaxed">
              {c.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
