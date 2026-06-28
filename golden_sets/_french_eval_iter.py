#!/usr/bin/env python3
"""French bot multi-iteration eval — runs sample queries, scores on rubric, prints diff.

Designed to be re-run after each chunking/retrieval change to see if quality improves.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass

API = "http://localhost:8000/api/french/query"

# ─── Rubric questions ─────────────────────────────────────────────────────────
# Each: (id, question, expected_doc_id_substr, expected_topic_keywords)
QUESTIONS = [
    ("Q1-secretary",
     "Quelles sont les responsabilités d'un secrétaire ?",
     "CBSE_10",
     ["secrétaire", "responsabilités", "bureau", "tâches"]),

    ("Q2-medias",
     "Qu'est-ce que c'est les médias ?",
     "CBSE_10",
     ["média", "presse", "journal", "télévision", "radio"]),

    ("Q3-doctor",
     "Que fait le médecin quand on le consulte ?",
     "CBSE_9",
     ["médecin", "consult", "ordonnance", "patient", "examiner"]),

    ("Q4-politique",
     "Décrivez le système politique français",
     "any",
     ["politique", "président", "assemblée", "république", "gouvernement"]),

    ("Q5-education",
     "Décrivez le système éducatif français",
     "any",
     ["éducat", "école", "lycée", "collège", "système", "bac"]),

    ("Q6-chomage",
     "Si on n'a pas de travail, que doit-on faire ?",
     "any",
     ["travail", "emploi", "chômage", "rechercher", "ANPE"]),

    ("Q7-grammar",
     "What is the difference between passé composé, imparfait and plus-que-parfait?",
     "any",
     ["passé composé", "imparfait", "plus-que-parfait", "auxiliaire", "temps"]),

    ("Q8-chap6",
     "help me revise chapter 6 of 10th grade textbook with a questionaire of 10 questions",
     "CBSE_10",
     ["Leçon 6", "chapter 6"]),

    ("Q9-passcomp-fr",
     "Explique le passé composé avec un exemple du manuel.",
     "any",
     ["passé composé", "auxiliaire", "participe passé", "avoir", "être"]),

    ("Q10-themes",
     "What themes are covered in IB DP French B?",
     "IB",
     ["Identités", "Expériences", "Ingéniosité", "Organisation", "Partage"]),
]


@dataclass
class Result:
    qid: str
    query: str
    citations: list[str]
    answer: str
    elapsed_s: float
    retrieved_chunks: list[dict]
    error: str = ""


def post(q: str, board: str = "all", lang: str = "bilingual") -> Result:
    params = f"?mode=hybrid&top_k=40&top_n=8&do_rerank=true"
    if board and board != "all":
        params += f"&board={board}"
    body = json.dumps({"q": q, "history": [], "language_mode": lang})
    t0 = time.monotonic()
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", API + params,
         "-H", "Content-Type: application/json",
         "--data-binary", body],
        capture_output=True, text=True, timeout=180,
    )
    elapsed = time.monotonic() - t0
    if not r.stdout.strip():
        return Result(qid="", query=q, citations=[], answer="", elapsed_s=elapsed,
                      retrieved_chunks=[], error="empty response")
    try:
        d = json.loads(r.stdout)
        return Result(
            qid="", query=q,
            citations=[c["section_ref"] for c in d.get("citations", [])],
            answer=d.get("answer", ""),
            elapsed_s=elapsed,
            retrieved_chunks=d.get("retrieved_chunks", []),
        )
    except json.JSONDecodeError as e:
        return Result(qid="", query=q, citations=[], answer="", elapsed_s=elapsed,
                      retrieved_chunks=[], error=f"json: {e}")


def score(qid: str, query: str, exp_doc_substr: str, exp_keywords: list[str], r: Result) -> dict:
    # 1. Retrieval relevance — does any citation match expected doc?
    if exp_doc_substr == "any":
        retrieval_ok = bool(r.citations)
    else:
        retrieval_ok = any(exp_doc_substr in (c.get("doc_id", "") if isinstance(c, dict) else "")
                           for c in r.retrieved_chunks)
    # 2. Topic keyword coverage in retrieved content
    content = " ".join(c.get("content", "") for c in r.retrieved_chunks).lower()
    kw_hits = sum(1 for k in exp_keywords if k.lower() in content)
    kw_score = kw_hits / max(1, len(exp_keywords))
    # 3. Answer refusal detection
    refused = any(m in r.answer.lower() for m in (
        "cannot answer", "i cannot", "outside the indexed", "outside your",
        "not in the indexed", "not in your", "je ne peux pas répondre"))
    # 4. Answer grounded — does it cite at least one section_ref?
    grounded = any(c in r.answer or c.replace("§", "") in r.answer for c in r.citations) if r.citations else False
    # 5. Latency
    latency_ok = r.elapsed_s < 30

    overall = (
        (1 if retrieval_ok else 0) * 0.3 +
        kw_score * 0.3 +
        (0 if refused and retrieval_ok else 1) * 0.2 +  # don't refuse when we have content
        (1 if grounded else 0) * 0.1 +
        (1 if latency_ok else 0) * 0.1
    )
    return {
        "retrieval_ok": retrieval_ok,
        "kw_hits": f"{kw_hits}/{len(exp_keywords)}",
        "kw_score": round(kw_score, 2),
        "refused": refused,
        "grounded": grounded,
        "latency_s": round(r.elapsed_s, 1),
        "overall": round(overall, 2),
    }


def main():
    print(f"Running {len(QUESTIONS)} queries via French bot...\n")
    iteration_results = []
    for qid, query, exp_doc, exp_kw in QUESTIONS:
        r = post(query)
        r.qid = qid
        s = score(qid, query, exp_doc, exp_kw, r)
        iteration_results.append({"qid": qid, "query": query, "score": s,
                                  "citations": r.citations[:3],
                                  "answer_excerpt": r.answer[:120].replace("\n", " "),
                                  "error": r.error})
        print(f"[{qid:12}] overall={s['overall']:.2f} retrieval={s['retrieval_ok']} "
              f"kw={s['kw_hits']} refused={s['refused']} {s['latency_s']:.1f}s")
        for c in r.citations[:3]:
            print(f"            · {c}")
        if r.error:
            print(f"            ! {r.error}")
        print()

    # Summary
    avg_overall = sum(x["score"]["overall"] for x in iteration_results) / len(iteration_results)
    n_refused_wrongly = sum(1 for x in iteration_results if x["score"]["refused"])
    n_no_retrieval = sum(1 for x in iteration_results if not x["score"]["retrieval_ok"])
    print(f"\n=== SUMMARY ===")
    print(f"Avg overall: {avg_overall:.2f}")
    print(f"Refused (sometimes wrong): {n_refused_wrongly}/{len(QUESTIONS)}")
    print(f"No retrieval: {n_no_retrieval}/{len(QUESTIONS)}")

    # Save full report
    out = json.dumps(iteration_results, ensure_ascii=False, indent=2)
    from pathlib import Path
    Path("/tmp/french_eval_results.json").write_text(out)
    print(f"\nFull → /tmp/french_eval_results.json")


if __name__ == "__main__":
    main()
