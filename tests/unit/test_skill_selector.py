"""Unit tests for src/skill_selector.py."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src.models.skill import Skill


# Helper to build a minimal mock registry
def _make_registry(*ids: str) -> dict:
    return {
        sid: Skill(
            id=sid,
            label=sid.replace("_", " ").title(),
            when_to_use="test",
            analysis_instructions="",
            coaching_instructions="",
            rewrite_instructions="",
            output_schema="",
        )
        for sid in ids
    }


ALL_DEFAULT_IDS = ["CA01_fillers", "SC01_signposting", "CE02_purpose_alignment"]
FULL_IDS = ALL_DEFAULT_IDS + [
    "CA02_sentence_complexity",
    "SC01_signposting",
    "CB02_questions",
    "TP01_hedging",
    "VE01_lexical_diversity",
    "VE02_jargon",
    "CE01_audience_alignment",
    "CE03_register",
    "TP02_empathy",
    "TP03_politeness",
    "VE03_precision",
    "SC02_topic_drift",
    "SC03_point_ordering",
    "CB01_talk_time",
    "CB03_acknowledgement",
    "CA03_ambiguous_references",
]


@pytest.fixture
def full_registry():
    return _make_registry(*FULL_IDS)


def test_select_skills_filler_keywords(full_registry):
    """Transcript containing 'um' and 'uh' should map to CA01_fillers."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        skills = select_skills("Um so I was uh thinking about the plan.")
        ids = [s.id for s in skills]
        assert "CA01_fillers" in ids


def test_select_skills_signposting_keywords(full_registry):
    """Transcript mentioning 'structure' or 'transition' should map to SC01_signposting."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        skills = select_skills("Can you help me add better transitions and signposting?")
        ids = [s.id for s in skills]
        assert "SC01_signposting" in ids


def test_select_skills_returns_defaults_when_no_match(full_registry):
    """When no keywords match, defaults CA01, SC01, CE02 should be returned."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        skills = select_skills("The quick brown fox jumps over the lazy dog.")
        ids = [s.id for s in skills]
        # Should fall back to defaults
        assert any(sid in ids for sid in ALL_DEFAULT_IDS)


def test_select_skills_max_3(full_registry):
    """At most 3 skills should be returned."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        text = "um uh filler question empathy politeness vocabulary jargon audience register"
        skills = select_skills(text)
        assert len(skills) <= 3


def test_select_skills_min_1(full_registry):
    """At least 1 skill should always be returned."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        skills = select_skills("")
        assert len(skills) >= 1


def test_select_skills_purpose_influences_selection(full_registry):
    """A stated purpose of 'persuade' should trigger CE02_purpose_alignment."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        skills = select_skills("Here is my message.", purpose="persuade")
        ids = [s.id for s in skills]
        assert "CE02_purpose_alignment" in ids


def test_select_skills_returns_skill_objects(full_registry):
    """Returned items should be Skill instances."""
    with patch("src.skill_selector.get_skill_registry", return_value=full_registry):
        from src.skill_selector import select_skills

        skills = select_skills("Test transcript.")
        assert all(isinstance(s, Skill) for s in skills)
