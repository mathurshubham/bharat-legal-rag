"use client"

import { useEffect, useState } from "react"
import { fetchDataset, type DatasetInfo, type DatasetRow } from "@/lib/api"
import type { DemoConfig } from "@/lib/demoConfig"

interface Props {
  demo: string
  config: DemoConfig
  onClose: () => void
}

type OracleCol = "expected_answer" | "expected_citations" | "expected_assertions"

const ORACLE_LABELS: Record<OracleCol, string> = {
  expected_answer:     "Answer",
  expected_citations:  "Citations",
  expected_assertions: "Assertions",
}

const ORACLE_HINTS: Record<OracleCol, string> = {
  expected_answer:     "Ideal answer text — use with LLM-judge scoring",
  expected_citations:  "Section refs that must appear in citations[]",
  expected_assertions: "Machine-checkable pass/fail flags",
}

const CATEGORY_COLORS: Record<string, string> = {
  retrieval:      "bg-blue-100 text-blue-700 border-blue-200",
  refusal:        "bg-amber-100 text-amber-700 border-amber-200",
  guard:          "bg-orange-100 text-orange-700 border-orange-200",
  edge:           "bg-purple-100 text-purple-700 border-purple-200",
  leak:           "bg-red-100 text-red-700 border-red-200",
  freshness:      "bg-teal-100 text-teal-700 border-teal-200",
  conflict:       "bg-rose-100 text-rose-700 border-rose-200",
  confidentiality:"bg-slate-100 text-slate-700 border-slate-200",
  tone:           "bg-green-100 text-green-700 border-green-200",
  escalation:     "bg-pink-100 text-pink-700 border-pink-200",
}

function categoryClass(cat: string) {
  return CATEGORY_COLORS[cat] ?? "bg-slate-100 text-slate-600 border-slate-200"
}

function truncate(s: string, n: number) {
  return s.length > n ? s.slice(0, n) + "…" : s
}

function downloadCSV(rows: DatasetRow[], oracleCol: OracleCol, demoId: string) {
  const BOM = "﻿"
  const esc = (v: string) => '"' + (v ?? "").replace(/"/g, '""') + '"'
  const header = ["eval_context", "input", "output", "expected_output"].map(esc).join(",")
  const body = rows
    .map(r => [r.eval_context, r.input, r.output, r[oracleCol]].map(esc).join(","))
    .join("\n")
  const csv = BOM + header + "\n" + body
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = `${demoId}-dataset.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export function DatasetModal({ demo, config, onClose }: Props) {
  const [dataset, setDataset]         = useState<DatasetInfo | null>(null)
  const [loading, setLoading]         = useState(true)
  const [selectedCats, setSelectedCats] = useState<Set<string>>(new Set())
  const [oracleCol, setOracleCol]     = useState<OracleCol>("expected_answer")

  useEffect(() => {
    fetchDataset(demo).then(d => {
      if (d) {
        setDataset(d)
        setSelectedCats(new Set(Object.keys(d.categories)))
      }
      setLoading(false)
    })
  }, [demo])

  const filteredRows = dataset
    ? dataset.rows.filter(r => selectedCats.has(r.eval_context))
    : []
  const previewRows = filteredRows.slice(0, 10)

  function toggleCat(cat: string) {
    setSelectedCats(prev => {
      const next = new Set(prev)
      if (next.has(cat)) next.delete(cat)
      else next.add(cat)
      return next
    })
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Eval Dataset</h2>
            <p className="text-[11px] text-slate-400 mt-0.5">{config.title}</p>
          </div>
          <button onClick={onClose} className="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 transition-colors">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1 px-5 py-4 space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : !dataset ? (
            <p className="text-sm text-slate-400 text-center py-8">No dataset found for this demo.</p>
          ) : (
            <>
              {/* Stats row */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[11px] font-medium text-slate-500 mr-1">{dataset.total} questions ·</span>
                {Object.entries(dataset.categories).map(([cat, n]) => (
                  <button
                    key={cat}
                    onClick={() => toggleCat(cat)}
                    className={`text-[11px] font-medium px-2.5 py-1 rounded-full border transition-all ${
                      selectedCats.has(cat)
                        ? categoryClass(cat)
                        : "bg-white text-slate-300 border-slate-200 line-through"
                    }`}
                  >
                    {cat} {n}
                  </button>
                ))}
              </div>

              {/* Oracle column selector */}
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5">
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-2.5">
                  expected_output column in download
                </p>
                <div className="flex gap-2 flex-wrap">
                  {(Object.keys(ORACLE_LABELS) as OracleCol[]).map(col => (
                    <label key={col} className="flex items-start gap-2 cursor-pointer group">
                      <input
                        type="radio"
                        name="oracle"
                        checked={oracleCol === col}
                        onChange={() => setOracleCol(col)}
                        className="mt-0.5 accent-indigo-600"
                      />
                      <span>
                        <span className={`text-[12px] font-medium ${oracleCol === col ? "text-indigo-700" : "text-slate-600"}`}>
                          {ORACLE_LABELS[col]}
                        </span>
                        <span className="block text-[10px] text-slate-400 mt-0.5">{ORACLE_HINTS[col]}</span>
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Preview table */}
              <div>
                <p className="text-[11px] text-slate-400 mb-2">
                  Showing {previewRows.length} of {filteredRows.length} rows
                  {filteredRows.length !== dataset.total && ` (${dataset.total} total, filtered)`}
                </p>
                <div className="rounded-xl border border-slate-200 overflow-hidden">
                  <table className="w-full text-[12px]">
                    <thead className="bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="text-left px-3 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wide w-28">Category</th>
                        <th className="text-left px-3 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wide">Input</th>
                        <th className="text-left px-3 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wide w-48">
                          expected_output
                          <span className="ml-1 text-indigo-400 normal-case font-normal">({ORACLE_LABELS[oracleCol]})</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {previewRows.map((row, i) => (
                        <tr key={i} className="hover:bg-slate-50 transition-colors">
                          <td className="px-3 py-2.5">
                            <span className={`inline-block text-[10px] px-2 py-0.5 rounded-full border font-medium ${categoryClass(row.eval_context)}`}>
                              {row.eval_context}
                            </span>
                          </td>
                          <td className="px-3 py-2.5 text-slate-700">{truncate(row.input, 70)}</td>
                          <td className="px-3 py-2.5 text-slate-500 font-mono text-[11px]">{truncate(row[oracleCol], 55)}</td>
                        </tr>
                      ))}
                      {filteredRows.length === 0 && (
                        <tr>
                          <td colSpan={3} className="px-3 py-6 text-center text-slate-400 text-[12px]">
                            No rows match the selected categories.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3.5 border-t border-slate-100 bg-slate-50 shrink-0 flex items-center justify-between gap-3">
          <a
            href="https://www.tryeval.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[11px] text-indigo-600 hover:underline"
          >
            Open TryEval →
          </a>
          <button
            onClick={() => dataset && downloadCSV(filteredRows, oracleCol, demo)}
            disabled={!dataset || filteredRows.length === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download CSV {filteredRows.length > 0 && `(${filteredRows.length})`}
          </button>
        </div>
      </div>
    </div>
  )
}
