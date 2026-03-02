"""ConvCoachAgent — Gemini prompt construction and response parsing."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from dotenv import load_dotenv

from src.models.feedback import Feedback
from src.models.skill import RewritePair, SkillResult
from src.models.session import Transcript
from src.scorer import score_transcript
from src.skill_selector import select_skills
from src.utils.formatting import analysis_json_to_table
from src.utils.rewrite_guard import is_rewrite_requested

load_dotenv()

# Use the src package's __file__ — Python always resolves package paths to absolute paths,
# making this immune to CWD at import time. src/__init__.py -> src/ -> repo root -> data/
import src as _src_pkg
DATA_DIR = Path(_src_pkg.__file__).parent.parent / "data"

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
MAX_TRANSCRIPT_LENGTH = 10000

CLARIFYING_QUESTION = (
    "I'd love to help with your communication! Could you paste the transcript or message "
    "you'd like me to analyse? Feel free to add a purpose (e.g., 'Purpose: persuade') if it helps."
)

VALIDATION_ERROR = (
    "Please submit a valid conversation transcript (at least a sentence or two) "
    "so I can give you meaningful feedback."
)


def _load_data_file(filename: str) -> str:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {path}\n"
            "Please ensure the data/ directory contains all reference files from the workspace root."
        )
    return path.read_text(encoding="utf-8")


def _build_system_prompt(
    skills: list,
    rewrite_requested: bool,
    rubrics_text: str,
    scorenorm_text: str,
    outputstructure_text: str,
    app_description_text: str,
    skill_registry_text: str,
) -> str:
    """Build the Gemini system prompt following the Prompt Construction Contract order."""
    parts: list[str] = []

    # 1. Identity and role
    parts.append(app_description_text.strip())
    parts.append("\n---")

    # 2. Selected skills context
    skill_ids = [s.id for s in skills]
    parts.append(f"\n## Selected Skills for This Analysis\nFocus on these skills only: {', '.join(skill_ids)}\n")
    for skill in skills:
        parts.append(
            f"### {skill.id} — {skill.label}\n"
            f"**When to use**: {skill.when_to_use}\n"
            f"**Analysis instructions**: {skill.analysis_instructions}\n"
            f"**Coaching instructions**: {skill.coaching_instructions}\n"
            f"**Output schema**: {skill.output_schema}\n"
        )

    # 3. Scoring rubrics for selected skills
    parts.append(f"\n---\n## Scoring Rubrics\n{rubrics_text.strip()}")

    # 4. Score normalization instructions
    parts.append(f"\n---\n## Score Normalization\n{scorenorm_text.strip()}")

    # 5. Output format instructions
    parts.append(f"\n---\n## Required Output Format\n{outputstructure_text.strip()}")

    # 6. Rewrite instructions (conditional)
    if rewrite_requested:
        rewrite_block = "\n---\n## Rewrite Instructions\n"
        for skill in skills:
            rewrite_block += f"**{skill.id}**: {skill.rewrite_instructions}\n"
        rewrite_block += (
            "\nInclude a ## Rewrites section in your response with before/after pairs in JSON format:\n"
            '[{"before": "...", "after": "...", "rationale": "..."}]'
        )
        parts.append(rewrite_block)
    else:
        parts.append("\n---\nDo NOT include a Rewrites section unless explicitly requested.")

    # T032 — Cultural bias and tone guardrails (G-01, G-02)
    parts.append(
        "\n---\n## Guardrails (MUST follow)\n"
        "- G-01: NEVER demean the user or provide culturally biased feedback. "
        "Adapt your language to the user's cultural and professional context. "
        "Avoid stereotyping or prescriptive cultural norms.\n"
        "- G-02: ALWAYS start your response by acknowledging strengths before listing improvements. "
        "Lead with at least one strength bullet in the Summary section.\n"
        "- G-03: Be supportive, encouraging, and respectful at all times. "
        "Frame all feedback as an opportunity for growth, never as criticism of the person."
    )

    return "\n".join(parts)


def _extract_json_blocks(text: str) -> list[dict]:
    """Extract all JSON objects (including inline arrays) from a text block."""
    results: list[dict] = []
    # Try to find JSON objects
    for match in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}", text, re.DOTALL):
        try:
            obj = json.loads(match.group())
            if isinstance(obj, dict) and ("skill" in obj or "skill_id" in obj):
                results.append(obj)
        except json.JSONDecodeError:
            pass
    return results


def _parse_agent_response(
    response_text: str,
    skills: list,
    session_id: str,
    turn_index: int,
    rewrite_requested: bool,
) -> tuple[Feedback, str]:
    """Parse Gemini's raw text response into a Feedback object and rendered markdown."""
    now = datetime.now(timezone.utc).isoformat()

    # Extract JSON analysis blocks
    json_blocks = _extract_json_blocks(response_text)
    skill_by_id: dict[str, dict] = {}
    for block in json_blocks:
        sid = block.get("skill") or block.get("skill_id", "")
        if sid:
            skill_by_id[sid] = block

    # Build llm_score_data from response
    llm_score_data: list[dict] = []
    for skill in skills:
        raw_score = _extract_score_from_text(response_text, skill.id)
        block = skill_by_id.get(skill.id, {})
        llm_score_data.append(
            {
                "skill_id": skill.id,
                "raw_score": raw_score,
                "rationale": _extract_rationale(response_text, skill.id),
                "metrics": block.get("metrics", {}),
                "examples": block.get("examples", []),
                "insight": block.get("insight", ""),
                "coaching_tips": _extract_coaching_tips(response_text),
                "why_it_helps": _extract_why_it_helps(response_text),
            }
        )

    skill_results = score_transcript("", skills, llm_score_data)

    # Extract top focus areas and strengths
    top_focus_areas = _extract_focus_areas(response_text)
    overall_strengths = _extract_strengths(response_text)

    # Handle rewrites
    if rewrite_requested:
        rewrites = _extract_rewrites(response_text)
        for sr in skill_results:
            if rewrites:
                sr.rewrite = rewrites
                break  # Attach to first skill result if not skill-specific

    feedback = Feedback(
        session_id=session_id,
        turn_index=turn_index,
        timestamp=now,
        top_focus_areas=top_focus_areas,
        overall_strengths=overall_strengths,
        skill_results=skill_results,
    )

    return feedback, response_text


def _extract_score_from_text(text: str, skill_id: str) -> float:
    """Extract a skill score from the agent's response text."""
    # Pattern: - CA01_fillers ...: 2.5 — or similar
    pattern = re.compile(
        rf"{re.escape(skill_id)}\s*(?:\([^)]*\))?\s*:?\s*([0-5](?:\.\d+)?)", re.IGNORECASE
    )
    m = pattern.search(text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 2.5  # neutral default


def _extract_rationale(text: str, skill_id: str) -> str:
    """Extract the rationale for a skill score from the agent's text."""
    pattern = re.compile(
        rf"{re.escape(skill_id)}\s*(?:\([^)]*\))?\s*:?\s*[0-5](?:\.\d+)?\s*[—–-]+\s*(.+?)(?:\n|$)",
        re.IGNORECASE,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def _extract_focus_areas(text: str) -> list[str]:
    """Extract the Top 2 Focus Areas from the response."""
    pattern = re.compile(r"Top\s*2?\s*Focus\s*Areas?\s*:?\s*(.+?)(?:\n|$)", re.IGNORECASE)
    m = pattern.search(text)
    if m:
        raw = m.group(1).strip()
        areas = [a.strip().strip("*").strip() for a in re.split(r"[;,]|—|–", raw) if a.strip()]
        return areas[:2] if areas else ["Review communication clarity", "Improve structure"]
    return ["Review communication clarity", "Improve structure"]


def _extract_strengths(text: str) -> list[str]:
    """Extract Overall Strengths from the response."""
    pattern = re.compile(r"Overall\s+strengths?\s*:?\s*(.+?)(?:\n\n|\n##|$)", re.IGNORECASE | re.DOTALL)
    m = pattern.search(text)
    if m:
        raw = m.group(1).strip()
        bullets = [
            line.lstrip("- •*").strip()
            for line in raw.splitlines()
            if line.strip().startswith(("-", "•", "*"))
        ]
        if bullets:
            return bullets[:2]
        return [raw[:150]]
    return []


def _extract_coaching_tips(text: str) -> list[str]:
    """Extract 2 coaching tips from the Coaching block."""
    coaching_section = re.search(
        r"##\s*Coaching\s*\n(.*?)(?=\n##|\Z)", text, re.IGNORECASE | re.DOTALL
    )
    if coaching_section:
        block = coaching_section.group(1)
        tips = [
            line.lstrip("- •*").strip()
            for line in block.splitlines()
            if line.strip().startswith(("-", "•", "*")) and "why it helps" not in line.lower()
        ]
        return tips[:2]
    return []


def _extract_why_it_helps(text: str) -> str:
    """Extract the 'Why it helps' sentence from the Coaching block."""
    m = re.search(r"Why\s+it\s+helps\s*:?\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _extract_rewrites(text: str) -> list[RewritePair]:
    """Extract rewrite pairs from the Rewrites block."""
    rewrites_section = re.search(
        r"##\s*Rewrites?\s*\n(.*?)(?=\n##|\Z)", text, re.IGNORECASE | re.DOTALL
    )
    if not rewrites_section:
        return []
    block = rewrites_section.group(1).strip()
    # Try JSON array
    try:
        arr = json.loads(block)
        if isinstance(arr, list):
            return [
                RewritePair(
                    before=item.get("before", ""),
                    after=item.get("after", ""),
                    rationale=item.get("rationale", ""),
                )
                for item in arr
                if isinstance(item, dict)
            ]
    except json.JSONDecodeError:
        pass
    return []


class ConvCoachAgent:
    """Main agent that orchestrates skill selection, scoring, and Gemini calls."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not found. Please copy .env.example to .env and add your key."
            )
        self.client = genai.Client(api_key=api_key)

        # Pre-load data files at startup (fail fast if missing)
        self.app_description = _load_data_file("app_description.md")
        self.rubrics_text = _load_data_file("scoringrubrics.md")
        self.scorenorm_text = _load_data_file("scorenorm.md")
        self.outputstructure_text = _load_data_file("outputstructure.md")
        self.skill_registry_text = _load_data_file("skillregistry.md")

    def _is_empty_or_short(self, text: str) -> bool:
        """Return True if the input is empty, whitespace-only, or < 10 meaningful chars."""
        stripped = text.strip()
        meaningful = re.sub(r"\s+", "", stripped)
        return len(meaningful) < 10

    def _is_ambiguous_no_transcript(self, text: str) -> bool:
        """Return True if the input seems to be small talk with no transcript content."""
        lower = text.lower().strip()
        small_talk_patterns = [
            r"^(hi|hello|hey|howdy|good morning|good afternoon|good evening)[.!?]*$",
            r"^how are you[.!?]*$",
            r"^what can you do[.!?]*$",
        ]
        return any(re.match(p, lower) for p in small_talk_patterns)

    def process(
        self,
        raw_text: str,
        session_id: str,
        turn_index: int,
        session_history: list[dict] | None = None,
    ) -> tuple[Feedback | None, str]:
        """Process a user input and return (Feedback | None, rendered_markdown).

        Returns:
            (None, message_string) for validation errors or clarifying questions.
            (Feedback, rendered_text) for successful analysis.
        """
        # T029 — Input validation
        if self._is_empty_or_short(raw_text):
            return None, VALIDATION_ERROR

        # T031 — Ambiguous / small talk
        if self._is_ambiguous_no_transcript(raw_text):
            return None, CLARIFYING_QUESTION

        # T037 — Transcript truncation (FR-019)
        truncated = False
        if len(raw_text) > MAX_TRANSCRIPT_LENGTH:
            raw_text = raw_text[:MAX_TRANSCRIPT_LENGTH]
            truncated = True

        # Parse rewrite intent
        rewrite_requested = is_rewrite_requested(raw_text)

        # Parse purpose prefix if present
        purpose: str | None = None
        purpose_match = re.match(r"^Purpose\s*:\s*(.+?)\n", raw_text, re.IGNORECASE)
        if purpose_match:
            purpose = purpose_match.group(1).strip()

        transcript = Transcript(
            raw_text=raw_text,
            purpose=purpose,
            rewrite_requested=rewrite_requested,
        )

        # Skill selection (rule-based + defaults)
        skills = select_skills(transcript.raw_text, purpose=transcript.purpose)

        # Build system prompt
        system_prompt = _build_system_prompt(
            skills=skills,
            rewrite_requested=rewrite_requested,
            rubrics_text=self.rubrics_text,
            scorenorm_text=self.scorenorm_text,
            outputstructure_text=self.outputstructure_text,
            app_description_text=self.app_description,
            skill_registry_text=self.skill_registry_text,
        )

        # Build user message (transcript + purpose)
        user_msg = raw_text

        # Call Gemini
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_msg,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                ),
            )
            response_text = response.text
        except Exception as exc:
            # T030 — Gemini API error handling
            error_msg = str(exc)
            if "API_KEY" in error_msg.upper() or "invalid" in error_msg.lower():
                return None, (
                    "⚠️ Invalid or missing Gemini API key. "
                    "Please check your `.env` file and ensure `GEMINI_API_KEY` is set correctly."
                )
            elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
                return None, (
                    "⚠️ Gemini API rate limit reached. Please wait a moment and try again."
                )
            else:
                return None, (
                    f"⚠️ An error occurred while contacting the Gemini API. "
                    f"Please try again.\n\n_Details: {error_msg}_"
                )

        feedback, rendered = _parse_agent_response(
            response_text=response_text,
            skills=skills,
            session_id=session_id,
            turn_index=turn_index,
            rewrite_requested=rewrite_requested,
        )

        # Prepend truncation warning if needed
        if truncated:
            rendered = (
                "⚠️ **Transcript truncated to 10,000 characters for processing.**\n\n" + rendered
            )

        return feedback, rendered
