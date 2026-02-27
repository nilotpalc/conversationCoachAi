"""Data model for agent feedback."""
from __future__ import annotations

from dataclasses import dataclass, field

from src.models.skill import RewritePair, SkillResult


@dataclass
class Feedback:
    """The complete structured response for a single user submission."""

    session_id: str
    turn_index: int
    timestamp: str
    top_focus_areas: list[str] = field(default_factory=list)
    overall_strengths: list[str] = field(default_factory=list)
    skill_results: list[SkillResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "timestamp": self.timestamp,
            "top_focus_areas": self.top_focus_areas,
            "overall_strengths": self.overall_strengths,
            "skill_results": [_skill_result_to_dict(sr) for sr in self.skill_results],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Feedback":
        return cls(
            session_id=data["session_id"],
            turn_index=data["turn_index"],
            timestamp=data["timestamp"],
            top_focus_areas=data.get("top_focus_areas", []),
            overall_strengths=data.get("overall_strengths", []),
            skill_results=[_skill_result_from_dict(sr) for sr in data.get("skill_results", [])],
        )


def _skill_result_to_dict(sr: SkillResult) -> dict:
    return {
        "skill_id": sr.skill_id,
        "skill_label": sr.skill_label,
        "raw_score": sr.raw_score,
        "normalized_score": sr.normalized_score,
        "rationale": sr.rationale,
        "metrics": sr.metrics,
        "examples": sr.examples,
        "insight": sr.insight,
        "coaching_tips": sr.coaching_tips,
        "why_it_helps": sr.why_it_helps,
        "rewrite": (
            [{"before": rp.before, "after": rp.after, "rationale": rp.rationale} for rp in sr.rewrite]
            if sr.rewrite is not None
            else None
        ),
    }


def _skill_result_from_dict(data: dict) -> SkillResult:
    rewrite = None
    if data.get("rewrite") is not None:
        rewrite = [
            RewritePair(before=rp["before"], after=rp["after"], rationale=rp["rationale"])
            for rp in data["rewrite"]
        ]
    return SkillResult(
        skill_id=data["skill_id"],
        skill_label=data["skill_label"],
        raw_score=data["raw_score"],
        normalized_score=data["normalized_score"],
        rationale=data["rationale"],
        metrics=data.get("metrics", {}),
        examples=data.get("examples", []),
        insight=data.get("insight", ""),
        coaching_tips=data.get("coaching_tips", []),
        why_it_helps=data.get("why_it_helps", ""),
        rewrite=rewrite,
    )
