"use client"

import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import type { ChatMessage } from "@/lib/types"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  message: ChatMessage
  config: DemoConfig
  accent: string
  onShowSources: (id: string) => void
  activeSources: string | null
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 py-1">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-[var(--text-4)] animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  )
}

export function MessageBubble({ message, config, accent, onShowSources, activeSources }: Props) {
  const [copied, setCopied] = useState(false)
  const copyAnswer = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true); setTimeout(() => setCopied(false), 1500)
  }
  const detectRefusal = (t: string) =>
    config.refusalMarkers.some(m => t.toLowerCase().includes(m))
  const detectGuard = (t: string) =>
    config.guardMarkers.some(m => t.toLowerCase().includes(m))

  /* ── User ── */
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[78%] bg-[var(--text)] text-[var(--bg)] rounded-2xl rounded-tr-sm px-4 py-2.5 text-[14px] leading-relaxed">
          {message.content}
        </div>
      </div>
    )
  }

  /* ── Loading ── */
  if (message.isLoading) {
    return (
      <div className="flex items-start gap-3">
        <div
          className="w-6 h-6 rounded-lg flex items-center justify-center text-xs shrink-0 mt-0.5"
          style={{ backgroundColor: `${accent}20`, color: accent }}
        >
          {config.icon}
        </div>
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl rounded-tl-sm px-4 py-3">
          <TypingDots />
        </div>
      </div>
    )
  }

  /* ── Error ── */
  if (message.error) {
    return (
      <div className="flex items-start gap-3">
        <div className="w-6 h-6 rounded-lg bg-red-500/10 flex items-center justify-center text-red-500 text-xs shrink-0 mt-0.5">!</div>
        <div className="max-w-[80%] bg-red-500/5 border border-red-500/20 text-red-400 rounded-2xl rounded-tl-sm px-4 py-3 text-[13px]">
          <span className="font-semibold">Error: </span>{message.error}
        </div>
      </div>
    )
  }

  /* ── Assistant ── */
  const resp       = message.response
  const text       = message.content
  const isRefusal  = detectRefusal(text)
  const hasGuard   = !isRefusal && detectGuard(text)
  const sourcesOpen = activeSources === message.id

  return (
    <div className="flex items-start gap-3">
      {/* Avatar */}
      <div
        className="w-6 h-6 rounded-lg flex items-center justify-center text-xs shrink-0 mt-0.5"
        style={{ backgroundColor: `${accent}20`, color: accent }}
      >
        {config.icon}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        {/* Banners */}
        {isRefusal && (
          <div className="flex items-center gap-2 bg-amber-500/8 border border-amber-500/20 rounded-lg px-3 py-2 text-[12px] text-amber-600 dark:text-amber-400">
            <svg className="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
            {config.refusalBanner}
          </div>
        )}
        {hasGuard && (
          <div className="flex items-center gap-2 bg-orange-500/8 border border-orange-500/20 rounded-lg px-3 py-2 text-[12px] text-orange-600 dark:text-orange-400">
            <svg className="w-3.5 h-3.5 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clipRule="evenodd" />
            </svg>
            {config.guardBanner}
          </div>
        )}

        {/* Answer card */}
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl rounded-tl-sm overflow-hidden">
          <div className="px-4 py-3.5">
            <div className="prose-answer text-[14px]">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
            </div>
          </div>

          {resp && (
            <div className="px-4 pb-3.5 space-y-2.5">
              {/* Citation chips — monospace, Stitch style */}
              {resp.citations.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {resp.citations.map((c, i) => (
                    <span key={i} title={c.doc_title} className="citation-chip">
                      {c.section_ref}
                    </span>
                  ))}
                </div>
              )}

              {/* Footer */}
              <div className="flex items-center justify-between pt-1 border-t border-[var(--border)]">
                <span className="text-[11px] text-[var(--text-4)]">
                  {(resp.latency.total_ms / 1000).toFixed(1)}s · {resp.usage.total_tokens.toLocaleString()} tokens
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={copyAnswer}
                    className="text-[11px] font-medium px-2.5 py-1 rounded-md text-[var(--text-3)] hover:text-[var(--text)] hover:bg-[var(--bg-surface)] transition-colors"
                  >
                    {copied ? "Copied ✓" : "Copy"}
                  </button>
                  {resp.retrieved_chunks.length > 0 && (
                    <button
                      onClick={() => onShowSources(message.id)}
                      className={`text-[11px] font-medium px-2.5 py-1 rounded-md transition-colors ${
                        sourcesOpen
                          ? "text-[var(--bg)] bg-[var(--accent)]"
                          : "text-[var(--text-3)] hover:text-[var(--text)] hover:bg-[var(--bg-surface)]"
                      }`}
                      style={sourcesOpen ? { backgroundColor: "var(--accent)" } : {}}
                    >
                      {sourcesOpen ? "Sources open" : `${resp.retrieved_chunks.length} sources ›`}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
