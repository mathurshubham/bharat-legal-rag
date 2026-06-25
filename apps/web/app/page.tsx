"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { fetchDemos, type DemoMeta } from "@/lib/api"

export default function RootPage() {
  const router = useRouter()
  const [demos, setDemos] = useState<DemoMeta[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDemos()
      .then(d => {
        if (d.length === 1) {
          // Single demo — skip picker, go straight to it
          router.replace(`/${d[0].id}`)
        } else {
          setDemos(d)
          setLoading(false)
        }
      })
      .catch(() => {
        // API not yet running — default to law
        router.replace("/law")
      })
  }, [router])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4 py-16">
      <div className="text-center mb-10">
        <h1 className="text-2xl font-semibold text-slate-900 mb-2">RAG Demos</h1>
        <p className="text-sm text-slate-500">Grounded question-answering over curated corpora</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl w-full">
        {demos.map(d => (
          <button
            key={d.id}
            onClick={() => router.push(`/${d.id}`)}
            className="flex flex-col items-start gap-2 text-left bg-white border border-slate-200 rounded-2xl px-6 py-5 hover:border-indigo-300 hover:bg-indigo-50 hover:shadow-md transition-all group"
          >
            <span className="text-base font-semibold text-slate-800 group-hover:text-indigo-700 leading-snug">{d.title}</span>
            {d.description && (
              <span className="text-sm text-slate-500 leading-snug">{d.description}</span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}
