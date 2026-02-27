"""Data model for progress tracking."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProgressRecord:
    """Aggregated view of a user's progress from a single session."""

    session_id: str
    date: str  # ISO 8601
    skills_evaluated: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    top_focus_areas: list[str] = field(default_factory=list)
