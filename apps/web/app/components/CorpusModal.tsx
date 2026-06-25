"use client"

import { useEffect, useState } from "react"
import { fetchCorpus, type CorpusInfo } from "@/lib/api"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  demo: string
  config: DemoConfig
  onClose: () => void
}

export function CorpusModal({ demo, config, onClose }: Props) {
  const [corpus, setCorpus] = useState<CorpusInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCorpus(demo).then(d => { setCorpus(d); setLoading(false) })
  }, [demo])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[85vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Indexed Corpus</h2>
            <p className="text-[11px] text-slate-400 mt-0.5">{config.title}</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1 px-5 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : !corpus || corpus.documents.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-8">No documents indexed.</p>
          ) : (
            <div className="space-y-2">
              {corpus.documents.map(doc => {
                const colorClass = config.docColors[doc.doc_id] ?? "bg-slate-50 text-slate-600 border-slate-200"
                return (
                  <div
                    key={doc.doc_id}
                    className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 hover:bg-white hover:border-slate-200 transition-all"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className={`shrink-0 text-[10px] px-2 py-0.5 rounded-full border font-medium ${colorClass}`}>
                        {doc.doc_id.replace(/_/g, " ")}
                      </span>
                      <span className="text-sm text-slate-700 truncate">{doc.doc_title}</span>
                    </div>
                    <div className="shrink-0 flex items-center gap-3 ml-3 text-[11px] text-slate-400 tabular-nums">
                      <span title="Sections">{doc.section_count.toLocaleString()} §</span>
                      <span title="Chunks" className="text-slate-500 font-medium">{doc.chunk_count.toLocaleString()} chunks</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        {corpus && (
          <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 shrink-0 flex items-center justify-between">
            <span className="text-[11px] text-slate-400">
              {corpus.documents.length} document{corpus.documents.length !== 1 ? "s" : ""}
            </span>
            <span className="text-[11px] font-medium text-slate-600">
              {corpus.total_chunks.toLocaleString()} total chunks
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
