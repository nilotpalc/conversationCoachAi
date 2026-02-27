"""Unit tests for src/utils/rewrite_guard.py."""
from __future__ import annotations

import pytest

from src.utils.rewrite_guard import is_rewrite_requested


@pytest.mark.parametrize(
    "text",
    [
        "Please show me a rewrite for this message.",
        "Can you rephrase that last paragraph?",
        "show rewrite",
        "Give me an alternative version.",
        "Please rewrite the transcript.",
        "REWRITE the above.",
        "I'd like a rewritten version.",
    ],
)
def test_is_rewrite_requested_true(text: str):
    assert is_rewrite_requested(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Can you analyse my filler words?",
        "How did I do on structure?",
        "What are my top focus areas?",
        "Show me my coaching tips.",
        "Analyse this transcript.",
        "",
        "Hello there!",
    ],
)
def test_is_rewrite_requested_false(text: str):
    assert is_rewrite_requested(text) is False


def test_case_insensitive():
    assert is_rewrite_requested("PLEASE REWRITE MY MESSAGE") is True
    assert is_rewrite_requested("Can You REPHRASE this?") is True
