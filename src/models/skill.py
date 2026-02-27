"""Data models for communication skills."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RewritePair:
    """A single before/after rewrite suggestion."""

    before: str
    after: str
    rationale: str


@dataclass
class Skill:
    """A communication skill from the registry."""

    id: str
    label: str
    when_to_use: str
    analysis_instructions: str
    coaching_instructions: str
    rewrite_instructions: str
    output_schema: str


@dataclass
class SkillResult:
    """The output of applying a single skill to a transcript."""

    skill_id: str
    skill_label: str
    raw_score: float
    normalized_score: float
    rationale: str
    metrics: dict = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    insight: str = ""
    coaching_tips: list[str] = field(default_factory=list)
    why_it_helps: str = ""
    rewrite: list[RewritePair] | None = None
