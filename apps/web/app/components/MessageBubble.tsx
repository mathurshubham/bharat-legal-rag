"use client"

import { useState } from "react"
import type { ChatMessage, RetrievedChunk } from "@/lib/types"
import { ChunksPanel } from "./ChunksPanel"

interface Props {
  message: ChatMessage
}

const REFUSAL_MARKERS = [
  "cannot answer",
  "i cannot answer",
  "not in the available",
  "please consult",
  "does not contain",
]

const OLD_LAW_MARKERS = [
  "repealed statute",
  "repealed law",
  "ipc",
  "crpc",
  "indian evidence act",
  "consumer protection act 1986",
]

function detectRefusal(text: string): boolean {
  const lower = text.toLowerCase()
  return REFUSAL_MARKERS.some(m => lower.includes(m))
}

function detectOldLaw(text: string): boolean {
  const lower = text.toLowerCase()
  return OLD_LAW_MARKERS.some(m => lower.includes(m))
}

function CitationPill({ ref: sRef, title }: { ref: string; title: string }) {
  return (
    <span
      title={title}
      className="inline-block bg-indigo-50 border border-indigo-200 text-indigo-700 rounded px-1.5 py-0.5 text-[11px] font-mono mr-1 mb-1 cursor-default"
    >
      {sRef}
    </span>
  )
}

export function MessageBubble({ message }: Props) {
  const [showChunks, setShowChunks] = useState(false)

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%] bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm">
          {message.content}
        </div>
      </div>
    )
  }

  // assistant
  if (message.isLoading) {
    return (
      <div className="flex justify-start">
        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <div className="flex gap-1.5 items-center h-5">
            {[0, 1, 2].map(i => (
              <span
                key={i}
                className="w-2 h-2 rounded-full bg-gray-300 animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (message.error) {
    return (
      <div className="flex justify-start">
        <div className="max-w-[80%] bg-red-50 border border-red-200 text-red-700 rounded-2xl rounded-tl-sm px-4 py-3 text-sm">
          <span className="font-semibold">Error: </span>{message.error}
        </div>
      </div>
    )
  }

  const resp = message.response
  const text = message.content
  const isRefusal = detectRefusal(text)
  const hasOldLaw = !isRefusal && detectOldLaw(text)

  return (
    <div className="flex justify-start gap-2">
      <div className="flex-1 max-w-[85%] space-y-2">
        {isRefusal && (
          <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-1.5 text-xs text-amber-800">
            <span>⚠</span>
            <span className="font-medium">Insufficient context — answer not in corpus</span>
          </div>
        )}
        {hasOldLaw && (
          <div className="flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-lg px-3 py-1.5 text-xs text-orange-800">
            <span>⚖</span>
            <span className="font-medium">References repealed law — see current statute</span>
          </div>
        )}

        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
            {text}
          </div>

          {resp && resp.citations.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-100">
              <p className="text-[10px] uppercase tracking-wide text-gray-400 mb-1.5">Citations</p>
              <div className="flex flex-wrap">
                {resp.citations.map((c, i) => (
                  <CitationPill key={i} ref={c.section_ref} title={c.doc_title} />
                ))}
              </div>
            </div>
          )}

          {resp && resp.retrieved_chunks.length > 0 && (
            <div className="mt-2 flex items-center justify-between text-[10px] text-gray-400">
              <div className="flex gap-3">
                <span>{resp.latency.total_ms}ms</span>
                <span>{resp.usage.total_tokens} tokens</span>
              </div>
              <button
                onClick={() => setShowChunks(v => !v)}
                className="text-indigo-500 hover:text-indigo-700 font-medium"
              >
                {showChunks ? "Hide sources" : `Show ${resp.retrieved_chunks.length} sources`}
              </button>
            </div>
          )}
        </div>

        {resp && showChunks && (
          <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm">
            <ChunksPanel chunks={resp.retrieved_chunks} onClose={() => setShowChunks(false)} />
          </div>
        )}
      </div>
    </div>
  )
}
