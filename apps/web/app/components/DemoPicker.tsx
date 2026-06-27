"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import type { DemoConfig } from "@/lib/demoConfig"
import { fetchDemos, type DemoMeta } from "@/lib/api"

interface Props { currentDemo: string; config: DemoConfig }

const ICONS: Record<string, string> = {
  law: "⚖", insurance: "🛡", health: "⚕", education: "📚", support: "🎧",
}
const ACCENTS: Record<string, string> = {
  law: "#4f46e5", insurance: "#0d9488", health: "#059669", education: "#7c3aed", support: "#0284c7",
}

export function DemoPicker({ currentDemo, config }: Props) {
  const router = useRouter()
  const [open, setOpen]   = useState(false)
  const [demos, setDemos] = useState<DemoMeta[]>([])
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => { fetchDemos().then(setDemos).catch(() => {}) }, [])

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const accent = ACCENTS[currentDemo] ?? "#6366f1"

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 h-8 px-2 rounded-lg hover:bg-[var(--bg-card)] transition-colors"
      >
        <div
          className="w-5 h-5 rounded-md flex items-center justify-center text-xs shrink-0"
          style={{ background: `${accent}20`, color: accent }}
        >
          {config.icon}
        </div>
        <span className="text-[13px] font-semibold text-[var(--text)] hidden sm:inline">
          {config.shortTitle}
        </span>
        <svg
          className={`w-3 h-3 text-[var(--text-4)] transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-1.5 w-56 bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl shadow-2xl overflow-hidden z-50"
          style={{ boxShadow: "0 20px 40px rgba(0,0,0,0.4)" }}>
          <div className="px-3 py-2 border-b border-[var(--border)]">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--text-4)]">Switch domain</p>
          </div>
          <div className="py-1">
            {demos.map(d => {
              const a = ACCENTS[d.id] ?? "#6366f1"
              const isActive = d.id === currentDemo
              return (
                <button
                  key={d.id}
                  onClick={() => { setOpen(false); router.push(`/${d.id}`) }}
                  className={`w-full flex items-center gap-3 px-3 py-2 text-left transition-colors ${
                    isActive ? "bg-[var(--bg-card)]" : "hover:bg-[var(--bg-card)]"
                  }`}
                >
                  <div
                    className="w-6 h-6 rounded-md flex items-center justify-center text-sm shrink-0"
                    style={{ background: `${a}20`, color: a }}
                  >
                    {ICONS[d.id] ?? "🤖"}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className={`text-[13px] font-medium leading-snug ${isActive ? "text-[var(--text)]" : "text-[var(--text-2)]"}`}>
                      {d.title.split("—").pop()?.trim() ?? d.title}
                    </p>
                  </div>
                  {isActive && (
                    <svg className="w-3.5 h-3.5 shrink-0" style={{ color: a }} fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
