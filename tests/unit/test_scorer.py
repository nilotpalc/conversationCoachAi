"""Unit tests for src/scorer.py."""
from __future__ import annotations

import pytest

from src.scorer import normalize_score, threshold_score, score_transcript
from src.models.skill import Skill


# ── normalize_score ──────────────────────────────────────────────────────────


def test_normalize_hybrid_weighting():
    """0.6 × rules + 0.4 × llm should apply correctly."""
    result = normalize_score(rules_score=4.0, llm_score=3.0)
    expected = round(0.6 * 4.0 + 0.4 * 3.0, 2)
    assert result == expected


def test_normalize_rules_only():
    """When no LLM score, rules score should be used as-is."""
    assert normalize_score(rules_score=3.5, llm_score=None) == 3.5


def test_normalize_llm_only():
    """When no rules score, LLM score should be used as-is."""
    assert normalize_score(rules_score=None, llm_score=2.0) == 2.0


def test_normalize_clamps_to_5():
    """Scores above 5.0 should be clamped to 5.0."""
    assert normalize_score(rules_score=5.0, llm_score=5.0) == 5.0


def test_normalize_clamps_to_0():
    """Scores below 0.0 should be clamped to 0.0."""
    assert normalize_score(rules_score=0.0, llm_score=0.0) == 0.0


def test_normalize_none_none():
    """Both None should return 0.0."""
    assert normalize_score(rules_score=None, llm_score=None) == 0.0


# ── threshold_score ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "density, expected",
    [
        (2.0, 5.0),
        (7.0, 4.0),
        (15.0, 3.0),
        (28.0, 2.0),
        (42.0, 1.0),
        (55.0, 0.0),
    ],
)
def test_threshold_score_ca01_fillers(density, expected):
    """CA01_fillers threshold scoring should match the rubric table."""
    score = threshold_score("CA01_fillers", {"filler_density_per_1k": density})
    assert score == expected


@pytest.mark.parametrize(
    "index, expected",
    [
        (0.9, 5.0),
        (0.7, 4.0),
        (0.5, 3.0),
        (0.3, 2.0),
        (0.15, 1.0),
        (0.05, 0.0),
    ],
)
def test_threshold_score_sc01_signposting(index, expected):
    """SC01_signposting threshold scoring should match the rubric table."""
    score = threshold_score("SC01_signposting", {"main_point_earliness_index": index})
    assert score == expected


def test_threshold_score_ca01_missing_metric():
    """Missing metric should return a neutral fallback score."""
    score = threshold_score("CA01_fillers", {})
    assert 0.0 <= score <= 5.0


def test_threshold_score_sc01_missing_metric():
    """Missing main_point_earliness_index should return a neutral fallback score."""
    score = threshold_score("SC01_signposting", {})
    assert 0.0 <= score <= 5.0


def test_threshold_score_unknown_skill_raises():
    """Requesting threshold score for a non-threshold skill should raise ValueError."""
    with pytest.raises(ValueError):
        threshold_score("CE02_purpose_alignment", {})


# ── score_transcript ─────────────────────────────────────────────────────────


def _make_skill(sid: str, label: str) -> Skill:
    return Skill(
        id=sid,
        label=label,
        when_to_use="",
        analysis_instructions="",
        coaching_instructions="",
        rewrite_instructions="",
        output_schema="",
    )


def test_score_transcript_returns_skill_results():
    """score_transcript should return one SkillResult per Skill."""
    skills = [
        _make_skill("CA01_fillers", "Filler Usage"),
        _make_skill("CE02_purpose_alignment", "Purpose Alignment"),
    ]
    llm_data = [
        {
            "skill_id": "CA01_fillers",
            "raw_score": 2.0,
            "rationale": "Many fillers",
            "metrics": {"filler_density_per_1k": 30.0},
            "examples": [],
            "insight": "",
            "coaching_tips": [],
            "why_it_helps": "",
        },
        {
            "skill_id": "CE02_purpose_alignment",
            "raw_score": 3.5,
            "rationale": "Purpose implied",
            "metrics": {},
            "examples": [],
            "insight": "",
            "coaching_tips": [],
            "why_it_helps": "",
        },
    ]
    results = score_transcript("", skills, llm_data)
    assert len(results) == 2
    ids = [r.skill_id for r in results]
    assert "CA01_fillers" in ids
    assert "CE02_purpose_alignment" in ids


def test_score_transcript_normalized_in_range():
    """All normalized scores must be in [0.0, 5.0]."""
    skills = [_make_skill("CA01_fillers", "Filler Usage")]
    llm_data = [
        {
            "skill_id": "CA01_fillers",
            "raw_score": 1.0,
            "rationale": "",
            "metrics": {"filler_density_per_1k": 40.0},
            "examples": [],
            "insight": "",
            "coaching_tips": [],
            "why_it_helps": "",
        }
    ]
    results = score_transcript("", skills, llm_data)
    for r in results:
        assert 0.0 <= r.normalized_score <= 5.0


def test_score_transcript_hybrid_formula_for_ca01():
    """CA01 should use hybrid: 0.6 × threshold_score + 0.4 × llm_score."""
    skills = [_make_skill("CA01_fillers", "Filler Usage")]
    # density=42 → threshold_score=1.0; llm_raw=3.0
    llm_data = [
        {
            "skill_id": "CA01_fillers",
            "raw_score": 3.0,
            "rationale": "",
            "metrics": {"filler_density_per_1k": 42.0},
            "examples": [],
            "insight": "",
            "coaching_tips": [],
            "why_it_helps": "",
        }
    ]
    results = score_transcript("", skills, llm_data)
    expected = round(0.6 * 1.0 + 0.4 * 3.0, 2)
    assert results[0].normalized_score == expected


def test_score_transcript_qualitative_uses_llm_only():
    """Qualitative skill (CE02) should use LLM score directly as normalized score."""
    skills = [_make_skill("CE02_purpose_alignment", "Purpose Alignment")]
    llm_data = [
        {
            "skill_id": "CE02_purpose_alignment",
            "raw_score": 4.0,
            "rationale": "",
            "metrics": {},
            "examples": [],
            "insight": "",
            "coaching_tips": [],
            "why_it_helps": "",
        }
    ]
    results = score_transcript("", skills, llm_data)
    assert results[0].normalized_score == 4.0
