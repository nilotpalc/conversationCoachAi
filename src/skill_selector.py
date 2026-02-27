"""Skill selection logic — rule-based with LLM fallback."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.models.skill import Skill

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_SKILL_IDS = ["CA01_fillers", "SC01_signposting", "CE02_purpose_alignment"]

# Rule-based keyword → skill ID mapping
KEYWORD_RULES: list[tuple[list[str], str]] = [
    # CA01 – filler words
    (["filler", "um", "uh", "like", "you know", "kind of", "sort of", "disfluency", "articulation"], "CA01_fillers"),
    # CA02 – sentence complexity
    (["run-on", "sentence length", "pacing", "complex sentence", "sentence complexity"], "CA02_sentence_complexity"),
    # CA03 – ambiguous references
    (["ambiguous", "unclear reference", "this/that", "pronoun", "referent"], "CA03_ambiguous_references"),
    # SC01 – signposting
    (["signpost", "transition", "bluf", "opening", "closing", "structure", "framing"], "SC01_signposting"),
    # SC02 – topic drift
    (["drift", "tangent", "off topic", "coherence", "focus"], "SC02_topic_drift"),
    # SC03 – point ordering
    (["point ordering", "get to the point", "executive communication", "bluf"], "SC03_point_ordering"),
    # CB01 – talk time
    (["talk time", "turn taking", "monologue", "airtime", "interruption"], "CB01_talk_time"),
    # CB02 – questions
    (["question", "curiosity", "engagement", "reflective", "open question"], "CB02_questions"),
    # CB03 – acknowledgment
    (["acknowledge", "listening", "active listening", "paraphrase", "responsive"], "CB03_acknowledgement"),
    # TP01 – hedging
    (["hedge", "confident", "confidence", "assertive", "assertiveness", "tentative", "maybe", "perhaps"], "TP01_hedging"),
    # TP02 – empathy
    (["empathy", "empathetic", "warm", "rapport", "de-escalate", "validation", "validate"], "TP02_empathy"),
    # TP03 – politeness
    (["polite", "politeness", "professional", "professionalism", "tone", "harsh", "rude"], "TP03_politeness"),
    # VE01 – lexical diversity
    (["vocabulary", "lexical", "repetitive", "repetition", "diverse language"], "VE01_lexical_diversity"),
    # VE02 – jargon
    (["jargon", "plain language", "technical language", "insider language"], "VE02_jargon"),
    # VE03 – precision
    (["vague", "precision", "concrete", "specific", "specificity"], "VE03_precision"),
    # CE01 – audience alignment
    (["audience", "technical depth", "reading level", "acronym"], "CE01_audience_alignment"),
    # CE02 – purpose alignment
    (["purpose", "persuade", "cta", "call to action", "evidence", "goal"], "CE02_purpose_alignment"),
    # CE03 – register
    (["register", "formality", "formal", "informal", "casual", "slang"], "CE03_register"),
]


def _load_skills_from_registry() -> dict[str, Skill]:
    """Load all skills from data/skillregistry.md as a dict keyed by skill ID."""
    registry_path = DATA_DIR / "skillregistry.md"
    text = registry_path.read_text(encoding="utf-8")
    # Strip the outer markdown fence if present
    text = re.sub(r"^```(?:markdown)?\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text)
    try:
        raw = yaml.safe_load(text)
    except Exception:
        return {}
    skills: dict[str, Skill] = {}
    for item in raw.get("skills", []):
        skill = Skill(
            id=item["id"],
            label=item["label"],
            when_to_use=item.get("when_to_use", ""),
            analysis_instructions=item.get("analysis_instructions", ""),
            coaching_instructions=item.get("coaching_instructions", ""),
            rewrite_instructions=item.get("rewrite_instructions", ""),
            output_schema=item.get("output_schema", ""),
        )
        skills[skill.id] = skill
    return skills


_SKILL_REGISTRY: dict[str, Skill] | None = None


def get_skill_registry() -> dict[str, Skill]:
    """Return the skill registry, loading from disk if not yet cached."""
    global _SKILL_REGISTRY
    if _SKILL_REGISTRY is None:
        _SKILL_REGISTRY = _load_skills_from_registry()
    return _SKILL_REGISTRY


def select_skills(
    transcript_text: str,
    purpose: str | None = None,
    max_skills: int = 3,
) -> list[Skill]:
    """Select 1–3 relevant skills for the given transcript.

    Step 1: Rule-based keyword matching against transcript + purpose.
    Step 2: Default skills if no match found.

    LLM fallback is handled in agent.py when no strong rule match is achieved.

    Args:
        transcript_text: The raw transcript submitted by the user.
        purpose: Optional declared purpose (e.g., "persuade").
        max_skills: Maximum number of skills to select (default 3).

    Returns:
        A list of 1–3 Skill objects.
    """
    registry = get_skill_registry()
    text_lower = (transcript_text + " " + (purpose or "")).lower()

    matched_ids: list[str] = []
    for keywords, skill_id in KEYWORD_RULES:
        if any(kw in text_lower for kw in keywords):
            if skill_id not in matched_ids:
                matched_ids.append(skill_id)
        if len(matched_ids) >= max_skills:
            break

    if not matched_ids:
        matched_ids = list(DEFAULT_SKILL_IDS)

    result: list[Skill] = []
    for sid in matched_ids[:max_skills]:
        if sid in registry:
            result.append(registry[sid])

    # Guarantee at least 1 skill
    if not result:
        for sid in DEFAULT_SKILL_IDS:
            if sid in registry:
                result.append(registry[sid])
                break

    return result[:max_skills]
