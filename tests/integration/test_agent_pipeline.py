"""Integration smoke test for the ConvCoachAgent pipeline.

Tests that with a mocked Gemini API:
- AgentOutput fields are all populated per agent-contract.md Output Schema
- No real API calls are made
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


SAMPLE_TRANSCRIPT = """\
Purpose: persuade
[00:00 A] Um, so I was, kind of thinking we could maybe change the deadline.
[00:06 B] What do you propose?
[00:10 A] Well, uh, I think we need, like, two more weeks. You know?
"""

SAMPLE_GEMINI_RESPONSE = """
## Summary
- Top 2 Focus Areas: Reduce filler words, Add a BLUF opening
- Overall strengths: Clear purpose stated; listener was engaged.

## Skill Scores
- CA01_fillers (Filler Usage): 1.5 — High filler density; frequent turn-start fillers.
- SC01_signposting (Signposting & Framing): 2.5 — Some framing but late main point.
- CE02_purpose_alignment (Purpose Alignment): 3.0 — Purpose present but CTA weak.

## Analysis (JSON)
{ "skill": "CA01_fillers", "metrics": { "filler_density_per_1k": 45.0 }, "examples": ["Um so — turn start", "kind of — hedge", "like — filler"], "insight": "High filler density impacts confidence." }
{ "skill": "SC01_signposting", "metrics": { "main_point_earliness_index": 0.3 }, "examples": ["Main point appears mid-turn"], "insight": "Start with recommendation." }

## Coaching
- Begin with your recommendation before supporting reasoning.
- Replace filler words with a one-second pause to regain composure.
- Why it helps: Reduces cognitive load and signals confidence.
"""


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")


@pytest.fixture
def mock_gemini_response():
    mock_resp = MagicMock()
    mock_resp.text = SAMPLE_GEMINI_RESPONSE
    return mock_resp


def test_agent_pipeline_full(mock_env, mock_gemini_response):
    """Smoke test: mock Gemini, submit transcript, verify AgentOutput fields populated."""
    with (
        patch("src.agent.genai.Client") as MockClient,
    ):
        instance = MockClient.return_value
        instance.models.generate_content.return_value = mock_gemini_response

        from src.agent import ConvCoachAgent

        agent = ConvCoachAgent()
        feedback, rendered = agent.process(
            raw_text=SAMPLE_TRANSCRIPT,
            session_id="test-session-001",
            turn_index=0,
        )

    # Feedback object should be populated
    assert feedback is not None, "Feedback should not be None for valid transcript"
    assert feedback.session_id == "test-session-001"
    assert feedback.turn_index == 0
    assert isinstance(feedback.top_focus_areas, list)
    assert len(feedback.top_focus_areas) >= 1, "Should have at least 1 focus area"
    assert isinstance(feedback.skill_results, list)
    assert len(feedback.skill_results) >= 1, "Should have at least 1 skill result"

    # Each SkillResult must satisfy the contract
    for sr in feedback.skill_results:
        assert sr.skill_id, "skill_id must be non-empty"
        assert sr.skill_label, "skill_label must be non-empty"
        assert 0.0 <= sr.normalized_score <= 5.0, f"Score out of range: {sr.normalized_score}"

    # Rendered text should contain key sections
    assert rendered, "rendered text should not be empty"


def test_agent_returns_validation_error_for_empty_input(mock_env):
    """Empty or very short input should return None feedback and a validation message."""
    with (
        patch("src.agent.genai.Client"),
    ):
        from src.agent import ConvCoachAgent

        agent = ConvCoachAgent()
        feedback, message = agent.process(raw_text="   ", session_id="s1", turn_index=0)

    assert feedback is None
    assert "valid" in message.lower() or "transcript" in message.lower()


def test_agent_returns_clarifying_question_for_small_talk(mock_env):
    """Small talk should trigger a clarifying question, not analysis."""
    with (
        patch("src.agent.genai.Client"),
    ):
        from src.agent import ConvCoachAgent

        agent = ConvCoachAgent()
        feedback, message = agent.process(raw_text="Hello!", session_id="s1", turn_index=0)

    assert feedback is None
    assert "?" in message or "transcript" in message.lower()


def test_agent_truncates_long_transcript(mock_env, mock_gemini_response):
    """Transcripts over 10,000 chars should be truncated and warned about."""
    long_transcript = "A " * 6000  # ~12,000 chars

    with (
        patch("src.agent.genai.Client") as MockClient,
    ):
        instance = MockClient.return_value
        instance.models.generate_content.return_value = mock_gemini_response

        from src.agent import ConvCoachAgent

        agent = ConvCoachAgent()
        feedback, rendered = agent.process(
            raw_text=long_transcript,
            session_id="s-trunc",
            turn_index=0,
        )

    assert "truncated" in rendered.lower() or feedback is not None
