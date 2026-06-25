"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { ChatMessage } from "@/lib/types"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  message: ChatMessage
  config: DemoConfig
  onShowSources: (id: string) => void
  activeSources: string | null
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-slate-300 animate-bounce"
          style={{ animationDelay: `${i * 0.18}s` }}
        />
      ))}
    </div>
  )
}

export function MessageBubble({ message, config, onShowSources, activeSources }: Props) {
  const detectRefusal = (t: string) =>
    config.refusalMarkers.some(m => t.toLowerCase().includes(m))
  const detectGuard = (t: string) =>
    config.guardMarkers.some(m => t.toLowerCase().includes(m))

  /* ── User ── */
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[72%] bg-indigo-600 text-white rounded-2xl rounded-tr-md px-4 py-2.5 text-[0.9rem] leading-relaxed shadow-sm">
          {message.content}
        </div>
      </div>
    )
  }

  /* ── Loading ── */
  if (message.isLoading) {
    return (
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0 mt-0.5">{config.icon}</div>
        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
          <TypingDots />
        </div>
      </div>
    )
  }

  /* ── Error ── */
  if (message.error) {
    return (
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-full bg-red-100 flex items-center justify-center text-red-600 text-xs shrink-0 mt-0.5">!</div>
        <div className="max-w-[80%] bg-red-50 border border-red-200 text-red-700 rounded-2xl rounded-tl-md px-4 py-3 text-sm">
          <span className="font-semibold">Error: </span>{message.error}
        </div>
      </div>
    )
  }

  /* ── Assistant answer ── */
  const resp = message.response
  const text = message.content
  const isRefusal = detectRefusal(text)
  const hasGuard  = !isRefusal && detectGuard(text)
  const sourcesOpen = activeSources === message.id

  return (
    <div className="flex items-start gap-3">
      <div className="w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-white text-[11px] font-bold shrink-0 mt-0.5">
        {config.icon}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        {isRefusal && (
          <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-xl px-3.5 py-2 text-xs text-amber-800">
            <svg className="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">{config.refusalBanner}</span>
          </div>
        )}
        {hasGuard && (
          <div className="flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-xl px-3.5 py-2 text-xs text-orange-800">
            <svg className="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">{config.guardBanner}</span>
          </div>
        )}

        <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-md shadow-sm overflow-hidden">
          <div className="px-5 py-4">
            <div className="prose-answer text-[0.9rem] text-slate-900">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {text}
              </ReactMarkdown>
            </div>
          </div>

          {resp && (
            <div className="px-5 pb-4 space-y-3">
              {resp.citations.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {resp.citations.map((c, i) => (
                    <span
                      key={i}
                      title={c.doc_title}
                      className="inline-flex items-center gap-1 bg-indigo-50 border border-indigo-200 text-indigo-700 rounded-full px-2.5 py-0.5 text-[11px] font-mono font-medium hover:bg-indigo-100 transition-colors cursor-default"
                    >
                      {c.section_ref}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between pt-1 border-t border-slate-100">
                <div className="flex items-center gap-3 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {(resp.latency.total_ms / 1000).toFixed(1)}s
                  </span>
                  <span>{resp.usage.total_tokens.toLocaleString()} tokens</span>
                </div>

                {resp.retrieved_chunks.length > 0 && (
                  <button
                    onClick={() => onShowSources(message.id)}
                    className={`flex items-center gap-1.5 text-[11px] font-medium px-3 py-1.5 rounded-lg transition-colors ${
                      sourcesOpen
                        ? "bg-indigo-600 text-white"
                        : "text-indigo-600 hover:bg-indigo-50"
                    }`}
                  >
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {sourcesOpen ? "Sources open" : `${resp.retrieved_chunks.length} sources`}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
