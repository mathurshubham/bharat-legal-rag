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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden"
        style={{ boxShadow: "0 25px 50px rgba(0,0,0,0.5)" }}>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border)] shrink-0">
          <div>
            <h2 className="text-[14px] font-semibold text-[var(--text)]">Indexed Corpus</h2>
            <p className="text-[11px] text-[var(--text-3)] mt-0.5">{config.title}</p>
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
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-5 h-5 border border-[var(--border-hi)] border-t-[var(--accent)] rounded-full animate-spin" />
            </div>
          ) : !corpus || corpus.documents.length === 0 ? (
            <p className="text-[13px] text-[var(--text-3)] text-center py-8">No documents indexed.</p>
          ) : (
            <div className="space-y-2">
              {corpus.documents.map(doc => {
                const colorClass = config.docColors[doc.doc_id] ?? "bg-[var(--bg-card)] text-[var(--text-3)] border-[var(--border)]"
                return (
                  <div key={doc.doc_id}
                    className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--border-hi)] px-4 py-3 transition-all">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <p className="text-[13px] font-medium text-[var(--text)] leading-snug">{doc.doc_title}</p>
                        <span className={`inline-block mt-1.5 text-[10px] px-2 py-0.5 rounded-full border font-medium ${colorClass}`}>
                          {doc.doc_id.replace(/_/g, " ")}
                        </span>
                      </div>
                      <div className="shrink-0 flex flex-col items-end gap-1 text-[11px] tabular-nums pt-0.5">
                        <span className="text-[13px] font-semibold text-[var(--text)]">{doc.chunk_count.toLocaleString()} <span className="font-normal text-[var(--text-3)]">chunks</span></span>
                        <span className="text-[11px] text-[var(--text-3)]">{doc.section_count.toLocaleString()} sections</span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        {corpus && (
          <div className="px-5 py-3 border-t border-[var(--border)] bg-[var(--bg-card)] shrink-0 flex items-center justify-between">
            <span className="text-[11px] text-[var(--text-3)]">
              {corpus.documents.length} document{corpus.documents.length !== 1 ? "s" : ""}
            </span>
            <span className="text-[11px] font-medium text-[var(--text-2)]">
              {corpus.total_chunks.toLocaleString()} total chunks
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
