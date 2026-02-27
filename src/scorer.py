"""Scoring pipeline — threshold-based and LLM-judged scoring with hybrid normalization."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.models.skill import Skill, SkillResult

DATA_DIR = Path(__file__).parent.parent / "data"

# Skills that support threshold-based (quantitative) scoring
THRESHOLD_SKILL_IDS = {"CA01_fillers", "SC01_signposting"}

# Hybrid weighting per scorenorm.md
RULES_WEIGHT = 0.6
LLM_WEIGHT = 0.4


def normalize_score(rules_score: float | None, llm_score: float | None) -> float:
    """Apply hybrid normalization: 0.6 × rules_score + 0.4 × llm_score.

    If only one source is available, that source's score is used as-is.
    Both inputs should be in [0.0, 5.0].
    """
    if rules_score is not None and llm_score is not None:
        combined = RULES_WEIGHT * rules_score + LLM_WEIGHT * llm_score
    elif rules_score is not None:
        combined = rules_score
    elif llm_score is not None:
        combined = llm_score
    else:
        combined = 0.0
    return round(max(0.0, min(5.0, combined)), 2)


def threshold_score(skill_id: str, metrics: dict[str, Any]) -> float:
    """Compute a deterministic threshold-based raw score for quantitative skills.

    Supported skills: CA01_fillers, SC01_signposting.
    Returns a score in [0, 5].
    """
    if skill_id == "CA01_fillers":
        return _score_ca01(metrics)
    elif skill_id == "SC01_signposting":
        return _score_sc01(metrics)
    else:
        raise ValueError(f"No threshold scoring defined for skill: {skill_id}")


def _score_ca01(metrics: dict[str, Any]) -> float:
    """Score CA01_fillers based on filler_density_per_1k threshold."""
    density = metrics.get("filler_density_per_1k", None)
    if density is None:
        return 2.5  # neutral fallback

    if density < 5:
        return 5.0
    elif density < 10:
        return 4.0
    elif density < 20:
        return 3.0
    elif density < 35:
        return 2.0
    elif density < 50:
        return 1.0
    else:
        return 0.0


def _score_sc01(metrics: dict[str, Any]) -> float:
    """Score SC01_signposting based on main_point_earliness_index threshold."""
    index = metrics.get("main_point_earliness_index", None)
    if index is None:
        return 2.5  # neutral fallback

    if index >= 0.8:
        return 5.0
    elif index >= 0.6:
        return 4.0
    elif index >= 0.4:
        return 3.0
    elif index >= 0.2:
        return 2.0
    elif index >= 0.1:
        return 1.0
    else:
        return 0.0


def score_transcript(
    transcript_text: str,
    skills: list[Skill],
    llm_score_data: list[dict] | None = None,
) -> list[SkillResult]:
    """Score the transcript against the selected skills.

    For threshold skills (CA01, SC01): uses threshold_score if metrics are available from
    llm_score_data, then normalizes.
    For qualitative skills: uses LLM score directly.

    Args:
        transcript_text: The raw transcript text.
        skills: Selected Skill objects to evaluate.
        llm_score_data: List of dicts returned by Gemini with keys:
            skill_id, raw_score (LLM 0–5), rationale, metrics, examples, insight,
            coaching_tips, why_it_helps, rewrite.

    Returns:
        List of SkillResult with normalized_score populated.
    """
    llm_by_skill: dict[str, dict] = {}
    if llm_score_data:
        for item in llm_score_data:
            sid = item.get("skill_id") or item.get("skill", "")
            llm_by_skill[sid] = item

    results: list[SkillResult] = []
    for skill in skills:
        llm_data = llm_by_skill.get(skill.id, {})
        llm_raw = llm_data.get("raw_score", None)
        if llm_raw is not None:
            llm_raw = float(llm_raw)

        metrics: dict = llm_data.get("metrics", {})
        examples: list = llm_data.get("examples", [])
        insight: str = llm_data.get("insight", "")
        coaching_tips: list = llm_data.get("coaching_tips", [])
        why_it_helps: str = llm_data.get("why_it_helps", "")
        rationale: str = llm_data.get("rationale", "")

        # Determine rules score for threshold skills
        rules_raw: float | None = None
        if skill.id in THRESHOLD_SKILL_IDS and metrics:
            try:
                rules_raw = threshold_score(skill.id, metrics)
            except (ValueError, KeyError):
                rules_raw = None

        normalized = normalize_score(rules_raw, llm_raw)
        raw = rules_raw if rules_raw is not None else (llm_raw if llm_raw is not None else 0.0)

        result = SkillResult(
            skill_id=skill.id,
            skill_label=skill.label,
            raw_score=raw,
            normalized_score=normalized,
            rationale=rationale,
            metrics=metrics,
            examples=examples,
            insight=insight,
            coaching_tips=coaching_tips,
            why_it_helps=why_it_helps,
            rewrite=None,
        )
        results.append(result)

    return results
