"""Unit tests for src/progress_tracker.py."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models.feedback import Feedback
from src.models.progress import ProgressRecord
from src.models.session import Message, Session
from src.models.skill import SkillResult


def _make_session(session_id: str, created_at: str, with_feedback: bool = True) -> Session:
    sr = SkillResult(
        skill_id="CA01_fillers",
        skill_label="Filler Usage",
        raw_score=2.0,
        normalized_score=2.2,
        rationale="High density",
        metrics={"filler_density_per_1k": 30.0},
        examples=[],
        insight="",
        coaching_tips=["Pause instead of saying um"],
        why_it_helps="Sounds more confident",
    )
    feedback = (
        Feedback(
            session_id=session_id,
            turn_index=0,
            timestamp=created_at,
            top_focus_areas=["Reduce fillers", "Improve structure"],
            overall_strengths=["Clear purpose"],
            skill_results=[sr],
        )
        if with_feedback
        else None
    )
    messages = [
        Message(role="user", content="Test transcript", timestamp=created_at),
        Message(role="assistant", content="Feedback text", timestamp=created_at, feedback=feedback),
    ]
    return Session(session_id=session_id, created_at=created_at, messages=messages)


# ── save_session / load_session ──────────────────────────────────────────────


def test_save_and_load_round_trip(tmp_path):
    """Save then load a session; all fields should be preserved."""
    session = _make_session("abc123", "2026-02-27T10:00:00Z")

    with patch("src.progress_tracker.SESSIONS_DIR", tmp_path):
        from src import progress_tracker

        progress_tracker.SESSIONS_DIR = tmp_path
        saved_path = progress_tracker.save_session(session)

    assert saved_path.exists()
    raw = json.loads(saved_path.read_text(encoding="utf-8"))
    assert raw["session_id"] == "abc123"
    assert len(raw["messages"]) == 2

    # Reload
    with patch("src.progress_tracker.SESSIONS_DIR", tmp_path):
        loaded = progress_tracker.load_session("abc123")

    assert loaded is not None
    assert loaded.session_id == "abc123"
    assert loaded.created_at == "2026-02-27T10:00:00Z"
    assert len(loaded.messages) == 2

    # Feedback preserved
    asst_msg = next(m for m in loaded.messages if m.role == "assistant")
    assert asst_msg.feedback is not None
    assert asst_msg.feedback.top_focus_areas == ["Reduce fillers", "Improve structure"]
    assert len(asst_msg.feedback.skill_results) == 1
    assert asst_msg.feedback.skill_results[0].skill_id == "CA01_fillers"
    assert asst_msg.feedback.skill_results[0].normalized_score == 2.2


def test_load_session_missing_returns_none(tmp_path):
    """Loading a non-existent session should return None."""
    with patch("src.progress_tracker.SESSIONS_DIR", tmp_path):
        from src import progress_tracker

        progress_tracker.SESSIONS_DIR = tmp_path
        result = progress_tracker.load_session("does-not-exist")

    assert result is None


# ── aggregate_progress ───────────────────────────────────────────────────────


def test_aggregate_progress_returns_records(tmp_path):
    """aggregate_progress should return one ProgressRecord per session with feedback."""
    sessions = [
        _make_session("s1", "2026-02-26T09:00:00Z"),
        _make_session("s2", "2026-02-27T10:00:00Z"),
    ]

    import src.progress_tracker as pt

    original_dir = pt.SESSIONS_DIR
    pt.SESSIONS_DIR = tmp_path
    try:
        for s in sessions:
            pt.save_session(s)
        records = pt.aggregate_progress()
    finally:
        pt.SESSIONS_DIR = original_dir

    assert len(records) == 2
    session_ids = {r.session_id for r in records}
    assert "s1" in session_ids
    assert "s2" in session_ids


def test_aggregate_progress_extracts_scores(tmp_path):
    """ProgressRecord scores should match the SkillResult normalized_score."""
    session = _make_session("score-check", "2026-02-27T10:00:00Z")

    import src.progress_tracker as pt

    original_dir = pt.SESSIONS_DIR
    pt.SESSIONS_DIR = tmp_path
    try:
        pt.save_session(session)
        records = pt.aggregate_progress()
    finally:
        pt.SESSIONS_DIR = original_dir

    assert records
    rec = next(r for r in records if r.session_id == "score-check")
    assert "CA01_fillers" in rec.scores
    assert rec.scores["CA01_fillers"] == 2.2
    assert rec.top_focus_areas == ["Reduce fillers", "Improve structure"]


def test_aggregate_progress_skips_sessions_without_feedback(tmp_path):
    """Sessions with no assistant feedback should not appear in progress records."""
    session = _make_session("no-fb", "2026-02-27T11:00:00Z", with_feedback=False)

    import src.progress_tracker as pt

    original_dir = pt.SESSIONS_DIR
    pt.SESSIONS_DIR = tmp_path
    try:
        pt.save_session(session)
        records = pt.aggregate_progress()
    finally:
        pt.SESSIONS_DIR = original_dir

    ids = {r.session_id for r in records}
    assert "no-fb" not in ids


def test_aggregate_progress_empty_sessions_dir(tmp_path):
    """An empty sessions directory should return an empty list."""
    import src.progress_tracker as pt

    original_dir = pt.SESSIONS_DIR
    pt.SESSIONS_DIR = tmp_path
    try:
        records = pt.aggregate_progress()
    finally:
        pt.SESSIONS_DIR = original_dir

    assert records == []
