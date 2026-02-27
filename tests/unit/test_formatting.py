"""Unit tests for src/utils/formatting.py."""
from __future__ import annotations

import json

import pytest

from src.utils.formatting import analysis_json_to_table, skill_results_to_markdown_table


# ── analysis_json_to_table ───────────────────────────────────────────────────


def test_analysis_json_to_table_from_dict():
    data = {
        "skill": "CA01_fillers",
        "metrics": {"filler_density_per_1k": 42.0, "consecutive_filler_runs": 3},
        "examples": ["[00:00] Um so — turn-start filler", "[00:10] Kind of — hedged transition"],
        "insight": "High filler density at transition points.",
    }
    result = analysis_json_to_table(data)
    assert "CA01_fillers" in result
    assert "filler_density_per_1k" in result
    assert "42.0" in result
    assert "High filler density" in result
    assert "Um so" in result or "turn-start filler" in result


def test_analysis_json_to_table_from_json_string():
    data = {
        "skill": "SC01_signposting",
        "metrics": {"main_point_earliness_index": 0.75},
        "examples": ["Good opening signpost found."],
        "insight": "Mostly clear signposting.",
    }
    json_str = json.dumps(data)
    result = analysis_json_to_table(json_str)
    assert "SC01_signposting" in result
    assert "main_point_earliness_index" in result


def test_analysis_json_to_table_no_metrics():
    data = {
        "skill": "CE02_purpose_alignment",
        "metrics": {},
        "examples": [],
        "insight": "",
    }
    result = analysis_json_to_table(data)
    assert "No numeric metrics" in result


def test_analysis_json_to_table_invalid_json_string():
    result = analysis_json_to_table("not valid json {{{")
    assert "Unable to parse" in result


def test_analysis_json_to_table_has_insight_section():
    data = {
        "skill": "TP01_hedging",
        "metrics": {"hedge_term_rate": 0.15},
        "examples": ["Maybe we could — hedge"],
        "insight": "Frequent hedging reduces perceived confidence.",
    }
    result = analysis_json_to_table(data)
    assert "Frequent hedging" in result


# ── skill_results_to_markdown_table ─────────────────────────────────────────


def test_skill_results_to_markdown_table_basic():
    skill_results = [
        {"skill_id": "CA01_fillers", "skill_label": "Filler Usage", "normalized_score": 2.2, "rationale": "High density."},
        {"skill_id": "SC01_signposting", "skill_label": "Signposting", "normalized_score": 4.0, "rationale": "Good transitions."},
    ]
    result = skill_results_to_markdown_table(skill_results)
    assert "CA01_fillers" in result
    assert "2.2" in result
    assert "Signposting" in result


def test_skill_results_to_markdown_table_empty():
    result = skill_results_to_markdown_table([])
    assert "No skill results" in result
