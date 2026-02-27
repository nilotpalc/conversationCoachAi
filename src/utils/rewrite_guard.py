"""Rewrite intent keyword detection utility."""
from __future__ import annotations

REWRITE_KEYWORDS = [
    "rewrite",
    "rephrase",
    "show rewrite",
    "alternative version",
    "show me a rewrite",
    "please rewrite",
    "can you rewrite",
    "give me a rewrite",
    "rewritten version",
]


def is_rewrite_requested(text: str) -> bool:
    """Return True if the user's text contains an explicit rewrite intent keyword.

    Args:
        text: The raw user input string.

    Returns:
        True if any rewrite keyword phrase is found (case-insensitive), False otherwise.
    """
    lower = text.lower()
    return any(keyword in lower for keyword in REWRITE_KEYWORDS)
