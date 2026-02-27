# Agent Contract: ConvCoach

**Feature**: 001-convcoach-app  
**Date**: 2026-02-27  
**Type**: Conversational AI Agent (Streamlit + Google Gemini)

This contract defines the inputs, outputs, and behavioral guarantees of the ConvCoach agent. All implementation MUST conform to this contract.

---

## Input Contract

The agent receives user input through `st.chat_input` in the Streamlit UI.

### Input Schema

```python
class AgentInput:
    raw_text: str          # Required. Transcript or message from user. Min 10 chars.
    purpose: str | None    # Optional. User-declared communication purpose.
    rewrite_requested: bool # Derived. True if user message contains rewrite keywords.
    session_history: list  # Required. Prior messages for multi-turn context.
```

### Valid Input Examples

```text
# Transcript with purpose
Purpose: persuade
Transcript:
[00:00 A] Um so I was thinking we could maybe postpone the deadline...

# Direct message without purpose
Can you review my tone in this message?
Hey team, just checking in on the project status.

# Rewrite request
Please show me a rewrite for the last transcript.
```

### Invalid Inputs → Agent Behavior

| Condition | Agent Behavior |
|-----------|---------------|
| Empty input | Ask one clarifying question; do not run analysis |
| Input < 10 characters | Ask one clarifying question; do not run analysis |
| No transcript, only small talk | Respond helpfully; do not attempt to score |

---

## Output Contract

All coaching responses MUST follow the structure defined in `data/outputstructure.md`. This section formalizes the contract fields.

### Output Schema

```python
class AgentOutput:
    summary: Summary           # REQUIRED. Always present.
    skill_scores: list[ScoreEntry]  # REQUIRED. 1–3 entries.
    analysis_table: str        # REQUIRED. Markdown table derived from JSON analysis.
    coaching: CoachingBlock    # REQUIRED. Always present.
    rewrites: list[RewritePair] | None  # CONDITIONAL. Only if rewrite_requested=True.
```

### Summary Block

```
## Summary
- Top 2 Focus Areas: <focus_area_1>, <focus_area_2>
- Overall strengths: <strength_1>; <strength_2>
```

**Contract rules**:
- MUST always contain exactly 2 focus areas
- MUST start with strengths (at least 1)

### Skill Scores Block

```
## Skill Scores
- <SKILL_ID> (<Label>): <0–5> — <one-line rationale>
```

**Contract rules**:
- MUST include 1–3 skill entries
- Score MUST be a float in range [0.0, 5.0]
- Default skills when none specified: `CA01_fillers`, `SC01_signposting`, `CE02_purpose_alignment`

### Analysis Block (rendered as table)

The raw JSON analysis output from the agent MUST be converted to a Markdown/Streamlit table.

**JSON schema** (per skill):
```json
{
  "skill": "<skill_id>",
  "metrics": { "<metric_name>": <value>, "..." : "..." },
  "examples": ["<example_1>", "<example_2>", "<example_3>"],
  "insight": "<one sentence summary>"
}
```

**Rendered as** (`formatting.py`):

| Metric | Value |
|--------|-------|
| `<metric_name>` | `<value>` |

Followed by examples and insight as bullet list below the table.

### Coaching Block

```
## Coaching
- <tip_1>
- <tip_2>
- Why it helps: <one sentence>
```

**Contract rules**:
- MUST provide exactly 2 tips
- MUST include a "Why it helps" explanation
- Tips MUST be concise and actionable

### Rewrites Block (conditional)

```
## Rewrites
[{"before": "...", "after": "...", "rationale": "..."}]
```

**Contract rules**:
- MUST only appear when `rewrite_requested=True`
- MUST NOT appear unless explicitly triggered
- Each rewrite MUST preserve the user's voice and intent

---

## Behavioral Guarantees

| Guarantee | Description |
|-----------|-------------|
| G-01 | Agent NEVER demeans or provides culturally biased feedback |
| G-02 | Agent ALWAYS starts with strengths before improvements |
| G-03 | Agent ALWAYS selects minimum 1 and maximum 3 skills per analysis |
| G-04 | Rewrite section appears ONLY on explicit user request |
| G-05 | Agent asks exactly ONE clarifying question when context is missing, then proceeds |
| G-06 | Skill IDs, labels, and metrics MUST match `data/skillregistry.md` exactly |
| G-07 | Scores MUST be derived via the rubric/normalization pipeline in `scorer.py` |
| G-08 | All session turns are persisted to `sessions/` after each assistant response |

---

## Prompt Construction Contract

The system prompt passed to Gemini MUST include (in order):

1. ConvCoach identity and role (from `app_description.md`)
2. Selected skills context (from `data/skillregistry.md`)
3. Scoring rubrics for selected skills (from `data/scoringrubrics.md`)
4. Score normalization instructions (from `data/scorenorm.md`)
5. Output format instructions (from `data/outputstructure.md`)
6. Rewrite instructions — ONLY if `rewrite_requested=True`
7. User's transcript and declared purpose (if any)

---

## Versioning

This contract is version **1.0**. Any breaking change (new required field, removed guarantee, changed score range) requires a constitution-compliant review and version bump.
