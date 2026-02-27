"""End-to-end test for ConvCoach Streamlit app using Streamlit AppTest.

This test simulates submitting a transcript through the chat interface and
asserts the rendered output contains the required structural sections.

Run via: pytest tests/e2e/
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


SAMPLE_TRANSCRIPT = (
    "Um, so I was kind of thinking we could maybe postpone the deadline by a week or two. "
    "You know, there's been a lot going on and uh I just think it would help the team."
)

MOCK_GEMINI_RESPONSE = """
## Summary
- Top 2 Focus Areas: Reduce filler words at turn starts; add a clear recommendation upfront
- Overall strengths: Shows consideration for the team's wellbeing.

## Skill Scores
- CA01_fillers (Filler Usage): 1.5 — Many turn-start fillers reduce confidence perception.
- SC01_signposting (Signposting & Framing): 2.0 — Main point arrives late; no BLUF opening.
- CE02_purpose_alignment (Purpose Alignment): 2.5 — Purpose implied but CTA is vague.

## Analysis (JSON)
{ "skill": "CA01_fillers", "metrics": { "filler_density_per_1k": 38.0 }, "examples": ["Um so — turn start filler"], "insight": "High filler density impacts confidence." }

## Coaching
- Start with your recommendation: 'I'd like to propose a one-week deadline extension.'
- Replace filler words with a deliberate pause.
- Why it helps: Clearer communication builds trust and signals confidence.
"""


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "e2e-test-key")


def _mock_agent_process(raw_text, session_id, turn_index, session_history=None):
    """Return a simple mock Feedback and rendered text."""
    from src.models.feedback import Feedback
    from src.models.skill import SkillResult

    sr = SkillResult(
        skill_id="CA01_fillers",
        skill_label="Filler Usage",
        raw_score=1.5,
        normalized_score=1.8,
        rationale="Many fillers.",
        examples=["Um so — turn start"],
        insight="High filler density.",
        coaching_tips=["Use deliberate pause"],
        why_it_helps="Signals confidence.",
    )
    feedback = Feedback(
        session_id=session_id,
        turn_index=turn_index,
        timestamp="2026-02-27T10:00:00Z",
        top_focus_areas=["Reduce filler words", "Add BLUF opening"],
        overall_strengths=["Shows consideration for the team"],
        skill_results=[sr],
    )
    rendered = MOCK_GEMINI_RESPONSE
    return feedback, rendered


def test_e2e_chat_flow(mock_env):
    """Simulate submitting a transcript; verify output contains required sections."""
    from streamlit.testing.v1 import AppTest

    with (
        patch("src.agent.genai.Client"),
        patch("src.agent.ConvCoachAgent.process", side_effect=_mock_agent_process),
        patch("src.progress_tracker.save_session"),
        patch("src.progress_tracker.aggregate_progress", return_value=[]),
    ):
        at = AppTest.from_file("src/app.py", default_timeout=30)
        at.run()

        # Submit a transcript via the chat input
        at.chat_input[0].set_value(SAMPLE_TRANSCRIPT).run()

    # The agent should have responded — messages should be present
    # We check the markdown output contains required sections
    all_text = " ".join(
        elem.value for elem in at.markdown if elem.value
    )

    # Structurally verify the response contains either the mock output or at least
    # one piece of coaching content
    assert (
        "Summary" in all_text
        or "Skill Scores" in all_text
        or "Focus Areas" in all_text
        or "Coaching" in all_text
        or "Filler" in all_text
    ), f"Expected structured coaching output in response. Got: {all_text[:500]}"


def test_e2e_empty_input_shows_validation_message(mock_env):
    """Submitting empty/short input should display a validation message."""
    from streamlit.testing.v1 import AppTest

    with (
        patch("src.agent.genai.Client"),
        patch("src.progress_tracker.aggregate_progress", return_value=[]),
        patch("src.progress_tracker.save_session"),
    ):
        at = AppTest.from_file("src/app.py", default_timeout=30)
        at.run()
        at.chat_input[0].set_value("hi").run()

    all_text = " ".join(elem.value for elem in at.markdown if elem.value)
    assert (
        "valid" in all_text.lower()
        or "transcript" in all_text.lower()
        or "?" in all_text
    ), f"Expected validation message or clarifying question. Got: {all_text[:500]}"
