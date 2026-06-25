"""
Law-specific ingest hooks.
Each function referenced in manifest.yaml normalizer_overrides
must match the signature: (text: str) -> str
"""
import re

_CONSTITUTION_ARTICLE_INLINE = re.compile(
    r"(?<!\d)(\d{1,3}[A-Z]?)\.\s+(?=[A-Z][a-z]|\[)"
)


def normalise_constitution(text: str) -> str:
    """
    The diglot Constitution PDF collapses article numbers inline.
    Insert a newline+sentinel before each article number so the standard
    line-anchored pattern can find them.
    """
    text = re.sub(r"^\d+\s*\n", "", text, flags=re.MULTILINE)
    text = _CONSTITUTION_ARTICLE_INLINE.sub(r"\nArticle \1. ", text)
    return text
