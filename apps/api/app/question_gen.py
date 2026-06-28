"""French question-bank generation: grade/chapter scoping + board×mode prompt
templates modelled on real exam patterns (CBSE official SQP, IB DP French B specs).

Two output modes:
- exam_paper   — full board-style paper (CBSE: sectioned A-D, mark-weighted, "au choix";
                 IB: Paper 1 / Paper 2 / Individual oral task shapes).
- practice_set — focused list of board-authentic question types, scoped to a chapter/unit.

Kept separate from main.py so the prompt can be iterated without touching routing.
"""
from __future__ import annotations

import re

# difficulty/grade → CBSE doc. IB is theme-based (no grade split).
_CBSE_DOC = {"9": "CBSE_9_ENTREJEUNES", "10": "CBSE_10_ENTREJEUNES"}
_LEVEL_GRADE = {"a1": "9", "a2": "10"}


def resolve_grade(board: str | None, grade: str | None, difficulty: str | None) -> str | None:
    """Best-effort CBSE grade (9/10) from explicit grade or difficulty level."""
    if (board or "").lower() != "cbse":
        return None
    if grade and str(grade) in _CBSE_DOC:
        return str(grade)
    lvl = (difficulty or "").strip().lower()
    return _LEVEL_GRADE.get(lvl)


def target_doc_ids(board: str | None, grade: str | None) -> list[str] | None:
    """Restrict retrieval to the right book(s). None = no doc restriction."""
    b = (board or "").lower()
    if b == "cbse" and grade in _CBSE_DOC:
        return [_CBSE_DOC[grade]]
    return None  # IB: keep all themes (chapter/unit filter narrows further)


def _meta(c: dict) -> dict:
    m = c.get("metadata")
    return m if isinstance(m, dict) else {}


def _chapter_match(c: dict, chapter: str) -> bool:
    """Match a chunk to a requested chapter. Handles CBSE 'Leçon N' (via metadata.lecon
    or section_ref) and IB unit codes like '5A'/'8A' (via section_ref/header_path)."""
    chap = chapter.strip().lower()
    sref = (c.get("section_ref") or "").lower()
    hdr = str(_meta(c).get("header_path") or "").lower()
    # CBSE Leçon N → compare numbers exactly (avoid 'Leçon 1' matching 'Leçon 10')
    m = re.search(r"le[çc]on\s*(\d+)", chap)
    if m:
        n = m.group(1)
        lecon_meta = _meta(c).get("lecon")
        if lecon_meta is not None and str(lecon_meta) == n:
            return True
        return bool(re.search(rf"le[çc]on\s*{n}\b", sref))
    # IB unit code e.g. 5a / 8a / 10b
    um = re.search(r"\b(\d{1,2}[ab])\b", chap)
    if um:
        code = um.group(1)
        return bool(re.search(rf"\b{code}\b", sref) or re.search(rf"\b{code}\b", hdr))
    # fallback substring
    return chap in sref or chap in hdr


async def fetch_chapter_chunks(
    demo_id: str, board: str | None, grade: str | None, chapter: str,
    *, limit: int = 30,
) -> list[dict]:
    """Pull chunks for a chapter/unit DIRECTLY by tag (not semantic retrieval), so
    chapter scope never depends on a query surfacing the right chunks in top-k.
    CBSE → metadata.lecon == N within the grade's doc; IB → unit code in section_ref."""
    from .db import get_pool

    chap = chapter.strip()
    where = ["demo_id = %s"]
    args: list = [demo_id]
    docs = target_doc_ids(board, grade)
    if docs:
        where.append("doc_id = ANY(%s)")
        args.append(docs)

    m = re.search(r"le[çc]on\s*(\d+)", chap, re.IGNORECASE)
    um = re.search(r"\b(\d{1,2}[ab])\b", chap, re.IGNORECASE)
    if m:
        where.append("metadata->>'lecon' = %s")
        args.append(m.group(1))
    elif um:
        where.append("section_ref ILIKE %s")
        args.append(f"%{um.group(1).upper()}%")
    else:
        where.append("section_ref ILIKE %s")
        args.append(f"%{chap}%")

    sql = (
        "SELECT id, doc_id, doc_title, section_ref, content, metadata "
        "FROM chunks WHERE " + " AND ".join(where) +
        " ORDER BY doc_id, chunk_index LIMIT %s"
    )
    args.append(limit)
    from psycopg.rows import dict_row
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(sql, args)
            rows = await cur.fetchall()
    return [
        {"id": r["id"], "doc_id": r["doc_id"], "doc_title": r["doc_title"],
         "section_ref": r["section_ref"], "content": r["content"],
         "metadata": r["metadata"], "score": 0.0, "rerank_score": None}
        for r in rows
    ]


def scope_chunks(
    chunks: list[dict], board: str | None, grade: str | None, chapter: str | None,
    *, min_keep: int = 6,
) -> tuple[list[dict], dict]:
    """Hard-filter retrieved chunks to the target grade/doc and chapter when possible,
    falling back to a soft re-order when the hard filter is too sparse. Returns
    (ordered_chunks, scope_info)."""
    info: dict = {"doc_filtered": False, "chapter_filtered": False, "fallback": False}
    docs = target_doc_ids(board, grade)
    pool = chunks
    if docs:
        doc_pool = [c for c in pool if c.get("doc_id") in docs]
        if len(doc_pool) >= min_keep:
            pool = doc_pool
            info["doc_filtered"] = True
        else:
            info["fallback"] = True  # not enough in-grade chunks; keep board pool

    if chapter:
        in_chap = [c for c in pool if _chapter_match(c, chapter)]
        if len(in_chap) >= min(min_keep, 3):
            # hard filter — chapter chunks only (fixes cross-chapter leak)
            pool = in_chap
            info["chapter_filtered"] = True
        elif in_chap:
            # sparse: prioritise chapter chunks, keep others as filler
            pool = in_chap + [c for c in pool if c not in in_chap]
            info["fallback"] = True
    return pool, info


# ── Prompt templates ──────────────────────────────────────────────────────────

_CBSE_EXAM_SPEC = """Produce a COMPLETE CBSE-style French question paper (Code 018), 80 marks, 3 heures,
following the official board format EXACTLY. Use these four sections with the real titles, mark
weights, French instruction phrasing, and "X au choix" optionality:

Section A (Compréhension) — 10 marks
  • A short French reading passage drawn from the source content, then:
    "Répondez aux questions suivantes : (2 au choix) (2X2=4)"  — open short questions
    "Dites vrai ou faux : (6X0.5=3)"  — six statements
    "Trouvez dans le texte : (3 au choix) (3X1=3)"  — find a preposition / a verb form /
      a synonym / an opposite / a word meaning X
Section B (Expression écrite) — 20 marks
  "Ecrivez UNE lettre de 80 mots :" with three choices 2A / 2B / 2C (OU)  — 10 marks
  "Parmi les questions suivantes (3A/3B/3C) abordez DEUX au choix (5X2=10)"  — e.g. an invitation,
      a dialogue to put in order / fill, a guided cloze paragraph
Section C (Grammaire) — 30 marks  (each block 5X1=5, use "5 au choix" and OU alternatives)
  Conjuguez au temps qui convient; Trouvez la question; Mettez au négatif; style direct/indirect;
  adjectifs/pronoms démonstratifs OU possessifs; pronoms relatifs OU personnels; subjonctif.
Section D (Culture et Civilisation) — 20 marks
  "Répondez (20 à 30 mots) : (5 au choix) (5X2=10)"; word-bank "Complétez à l'aide des mots donnés
  (5X1=5)"; "Faites correspondre colonne A/B" OU "Vrai ou faux" (5X1=5).
Then a "## Corrigé / Answer key" with section-wise answers."""

_CBSE_PRACTICE_SPEC = """Produce a FOCUSED practice set (not a full paper) of {count} questions using
board-authentic CBSE question types and French instruction phrasing. Prefer the requested types
({qtypes}). Use real CBSE task verbs: "Conjuguez", "Complète", "Dites vrai ou faux",
"Trouvez dans le texte", "Reliez", "Mettez au négatif", "Remplis les blancs", MCQ "Que signifie…?
a)…b)…c)…d)…". Number questions; cite the source section_ref in italics after each. End with a
"## Corrigé" answer key."""

_IB_EXAM_SPEC = """Produce IB Diploma French B exam-style tasks (B1 SL / B2 HL) — NOT a CBSE-style paper.
Instructions ENTIRELY in French. Build three parts:

Épreuve 1 (Production écrite) — offer 3 themed task choices (the candidate picks ONE), each 450–600 mots,
  with a clearly different register/text type: (a) informel — blog/courriel/journal intime;
  (b) professionnel — rapport/proposition/lettre formelle; (c) médias — article/discours/texte d'opinion.
  For each task state le destinataire, le contexte, le but.
Épreuve 2 (Compréhension) — based on a short source text: questions de type QCM, "Vrai ou faux
  (justifiez avec les mots du texte)", synonyme/antonyme, "Reliez", and a few questions à réponse courte.
Épreuve orale individuelle — SL: "Faites une présentation sur cette image …"; HL: "Faites une
  présentation sur ce texte …" with 4–6 guiding questions, then themed discussion prompts.
Then "## Corrigé / Pistes de correction" with model answers / mark guidance."""

_IB_PRACTICE_SPEC = """Produce a FOCUSED IB French B practice set of {count} tasks (B1-B2), instructions in
French, using authentic IB task shapes (no CBSE sections). Prefer requested types ({qtypes}). Mix:
QCM, "Vrai ou faux — justifiez", "Reliez", short comprehension questions, a "Production écrite" prompt
(state destinataire/contexte/but), and an oral prompt ("Faites une présentation…"). End with
"## Corrigé / Pistes de correction"."""


def build_key_prompt(*, board: str | None, paper_md: str, context: str) -> str:
    """Pass 2 for exam_paper: produce the COMPLETE marking scheme / answer key for an
    already-generated paper, with its own token budget so it can never be truncated."""
    is_ib = (board or "").lower() == "ib"
    rubric = (
        "For open IB tasks (production écrite, oral) give band-style guidance (langue / message / "
        "concept) + a brief model answer."
        if is_ib else
        "For open CBSE tasks (lettre, invitation) give the real mark breakdown — Format 4 "
        "(place/date/addressee/opening 2; closing+name 2); Idea & creativity 4; "
        "Content/accuracy/cohesion 2; deduct ≤2 grammar, ≤2 off-topic — plus a brief model answer."
    )
    return f"""You are the examiner writing the official CORRIGÉ / MARKING SCHEME for the French
paper below. Produce a COMPLETE key: one entry for EVERY numbered question in EVERY section.

Rules:
- Objective items (conjugation, fill-in, vrai/faux, matching, trouvez dans le texte, MCQ,
  négation, style direct/indirect, pronouns): give the EXACT answer + accepted alternatives.
- {rubric}
- Ground answers ONLY in the source chunks. Never omit or stop early.
- Output ONLY the marking scheme (start with "## Corrigé / Marking scheme"). Do not repeat the questions.

## The paper
{paper_md}

## Source chunks (for grounding answers)
{context}
"""


def build_prompt(
    *, board: str | None, mode: str, grade: str | None, level: str | None,
    chapter: str | None, count: int, question_types: list[str] | None,
    language_mode: str, teacher_notes: str | None, context: str,
    include_key: bool = True,
) -> str:
    b = (board or "").lower()
    qtypes = ", ".join(question_types or ["mcq", "fill_in", "short", "vrai_faux"])
    if b == "ib":
        spec = (_IB_EXAM_SPEC if mode == "exam_paper" else _IB_PRACTICE_SPEC).format(
            count=count, qtypes=qtypes)
        board_line = "Board: IB Diploma Programme French B (Oxford)."
        level_line = f"Niveau: {level or 'B1-B2'} (SL≈B1, HL≈B2)."
    else:
        spec = (_CBSE_EXAM_SPEC if mode == "exam_paper" else _CBSE_PRACTICE_SPEC).format(
            count=count, qtypes=qtypes)
        gl = grade or ("9" if (level or "").lower() == "a1" else "10" if (level or "").lower() == "a2" else "?")
        board_line = f"Board: CBSE (Entre Jeunes), Classe {gl}."
        level_line = f"Niveau CEFR: {level or ('A1' if gl=='9' else 'A2' if gl=='10' else 'A1-A2')}. " \
                     "Keep difficulty true to the grade (Classe 9 = A1 simple; Classe 10 = A2)."
    scope_line = f"Chapter/Unit scope: {chapter}. Stay strictly within it." if chapter \
        else "Scope: the whole grade/level corpus below."
    lang_line = {
        "fr": "Write everything in French.",
        "en": "Write instructions in English where the real board does; content/quotes in French.",
    }.get((language_mode or "bilingual").lower(),
          "Bilingual: keep French task instructions authentic; English glosses allowed.")
    teacher_line = (
        f"\nTEACHER INSTRUCTIONS (highest priority — follow these even if they override defaults):\n{teacher_notes.strip()}\n"
        if teacher_notes and teacher_notes.strip() else ""
    )
    if include_key:
        key_block = """
ANSWER KEY / CORRIGÉ (write this in full — it is graded as heavily as the questions):
- COMPLETE: an entry for EVERY numbered question in EVERY section. Never omit, never stop early,
  never write "etc.". If space is tight, shorten the QUESTIONS, never the key.
- OBJECTIVE items (conjugation, fill-in/cloze, vrai-faux, matching, "trouvez dans le texte",
  MCQ, négation, style direct/indirect, pronouns): give the EXACT answer. Include accepted
  alternatives where real (e.g. "à / pour", "dont / duquel", "Où habitaient-ils ? / Où est-ce
  qu'ils habitaient ?").
- OPEN tasks (lettre, invitation, essay/production écrite, oral/présentation): do NOT leave blank
  and do NOT invent one "correct" essay. Give a MARKING SCHEME = a mark breakdown plus a short
  model answer. Use the real CBSE letter rubric as the template:
  Format 4 (place/date/addressee/opening = 2; closing + writer's name = 2); Idea & creativity 4;
  Content/accuracy/cohesion 2; deduct ≤2 for grammar, ≤2 for off-topic. For IB, give band-style
  guidance (langue / message / conceptual focus) and a brief model."""
    else:
        key_block = """
DO NOT write any answers or a corrigé in this output — produce the QUESTIONS / TASKS ONLY.
The marking scheme is generated separately."""
    return f"""You are an experienced French examiner writing for {board_line.split(':',1)[1].strip()}

{board_line}
{level_line}
{scope_line}
{lang_line}

TASK:
{spec}

HARD RULES:
- Ground every question and answer ONLY in the source textbook chunks below. Do not invent facts,
  characters, statistics, or texts that are not present or directly inferable.
- Cite the originating section_ref (in italics) for each question or task where applicable.
- Respect the marks/word-limits stated above; keep numbering and section titles exactly.
{teacher_line}{key_block}
## Source chunks
{context}
"""
