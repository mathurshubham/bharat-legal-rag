import os

from .gateway import chat_completion

_CONDENSE_MODEL = os.getenv("HYDE_MODEL", "openai/gpt-4.1-mini")

_SYSTEM = (
    "You rewrite a follow-up question into a standalone search query. "
    "Output ONLY the rewritten query — no explanation, no preamble. "
    "Resolve pronoun references and implicit context into explicit terms. "
    "Do NOT inject legal substance or facts from prior turns — "
    "if the follow-up asks about something unrelated to prior legal context, "
    "rewrite it faithfully as-is (the retrieval system will handle relevance)."
)


def _format_history(history: list[dict]) -> str:
    lines = []
    for turn in history[-6:]:  # last 3 exchanges max
        role = turn.get("role", "user")
        lines.append(f"{role.upper()}: {turn['content']}")
    return "\n".join(lines)


async def condense_query(
    query: str,
    history: list[dict],
    openrouter_key: str,
    *,
    account_id: str | None = None,
    gateway_id: str | None = None,
) -> str:
    if not history:
        return query

    context = _format_history(history)
    user_msg = f"Conversation so far:\n{context}\n\nFollow-up: {query}\n\nStandalone query:"

    result = await chat_completion(
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        model=_CONDENSE_MODEL,
        openrouter_key=openrouter_key,
        account_id=account_id,
        gateway_id=gateway_id,
        max_tokens=128,
        temperature=0.0,
    )
    condensed = result["text"].strip().strip('"').strip("'")
    return condensed or query
