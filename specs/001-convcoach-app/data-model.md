# Data Model: ConvCoach Application

**Feature**: 001-convcoach-app  
**Date**: 2026-02-27  
**Source**: spec.md + research.md

---

## Entities

### 1. `Session`

Represents a single user session in the app. Created at app start; persisted to `sessions/<session_id>.json` on each interaction.

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | UUID4, generated at session start |
| `created_at` | `str` (ISO 8601) | Timestamp when session was started |
| `messages` | `list[Message]` | Ordered list of conversation turns |

**State transitions**: `active` → `persisted` (when user ends session or app reruns)

---

### 2. `Message`

A single turn in the conversation — either from the user or the agent.

| Field | Type | Description |
|-------|------|-------------|
| `role` | `str` | `"user"` or `"assistant"` |
| `content` | `str` | Raw text of the message |
| `timestamp` | `str` (ISO 8601) | When the message was sent |
| `feedback` | `Feedback \| None` | Populated only for `role="assistant"` messages that contain coaching output |

---

### 3. `Transcript`

Represents the user-submitted conversation text for analysis.

| Field | Type | Description |
|-------|------|-------------|
| `raw_text` | `str` | The full text submitted by the user |
| `purpose` | `str \| None` | Optional user-declared purpose (e.g., "persuade", "give feedback") |
| `rewrite_requested` | `bool` | Whether the user explicitly asked for a rewrite in this turn |

**Validation rules**:
- `raw_text` must be non-empty (min 10 characters) to trigger analysis
- If `raw_text` is empty or < 10 chars, agent asks a clarifying question instead

---

### 4. `Skill`

A communication skill from the registry. Loaded from `data/skillregistry.md` at startup.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique skill ID (e.g., `CA01_fillers`) |
| `label` | `str` | Human-readable label (e.g., "Filler Usage") |
| `when_to_use` | `str` | Trigger condition description |
| `analysis_instructions` | `str` | Instructions for extracting metrics |
| `coaching_instructions` | `str` | Instructions for generating coaching tips |
| `rewrite_instructions` | `str` | Instructions for generating rewrites |
| `output_schema` | `str` | JSON schema string for the skill's analysis output |

**Relationships**: One `Skill` → many `SkillResult` (one per session turn)

---

### 5. `SkillResult`

The output of applying a single skill to a transcript.

| Field | Type | Description |
|-------|------|-------------|
| `skill_id` | `str` | References `Skill.id` |
| `skill_label` | `str` | Display label |
| `raw_score` | `float` | 0–5 raw score from rubric evaluation |
| `normalized_score` | `float` | Final score after normalization weighting |
| `rationale` | `str` | One-line explanation of the score |
| `metrics` | `dict` | Extracted numeric metrics (skill-specific) |
| `examples` | `list[str]` | 3 example excerpts with line refs and impact |
| `insight` | `str` | Summary insight sentence |
| `coaching_tips` | `list[str]` | 2 concise actionable coaching tips |
| `why_it_helps` | `str` | One-sentence explanation of the coaching value |
| `rewrite` | `list[RewritePair] \| None` | Before/after rewrites; only present when `rewrite_requested=True` |

---

### 6. `RewritePair`

A single before/after rewrite suggestion.

| Field | Type | Description |
|-------|------|-------------|
| `before` | `str` | Original excerpt from the transcript |
| `after` | `str` | Suggested rewrite preserving user voice |
| `rationale` | `str` | Why this change helps |

---

### 7. `Feedback`

The complete structured response for a single user submission. Aggregates all `SkillResult`s.

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | Parent session reference |
| `turn_index` | `int` | Which turn in the session (0-indexed) |
| `timestamp` | `str` (ISO 8601) | When feedback was generated |
| `top_focus_areas` | `list[str]` | Exactly 2 highest-impact improvement areas |
| `overall_strengths` | `list[str]` | 1–2 strength bullets |
| `skill_results` | `list[SkillResult]` | One per selected skill (1–3) |

---

### 8. `ProgressRecord`

Aggregated view of a user's progress across sessions. Built from persisted `sessions/*.json` files.

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | References the source Session |
| `date` | `str` (ISO 8601) | Session date |
| `skills_evaluated` | `list[str]` | Skill IDs evaluated in this session |
| `scores` | `dict[str, float]` | Mapping of skill_id → normalized_score |
| `top_focus_areas` | `list[str]` | Focus areas from this session |

**Used by**: `progress_tracker.py` to render a progress table/chart in the sidebar

---

## Entity Relationships

```text
Session
  └── messages: list[Message]
        └── feedback: Feedback (only on assistant messages)
              ├── top_focus_areas: list[str]
              ├── overall_strengths: list[str]
              └── skill_results: list[SkillResult]
                    ├── skill_id → Skill
                    └── rewrite: list[RewritePair] (conditional)

ProgressRecord ← aggregated from Session files
```

---

## Persistence Format

Sessions are stored as JSON files at `sessions/<session_id>.json`:

```json
{
  "session_id": "abc123",
  "created_at": "2026-02-27T10:00:00Z",
  "messages": [
    {
      "role": "user",
      "content": "[User transcript text]",
      "timestamp": "2026-02-27T10:00:05Z",
      "feedback": null
    },
    {
      "role": "assistant",
      "content": "[Rendered Streamlit output]",
      "timestamp": "2026-02-27T10:00:08Z",
      "feedback": {
        "session_id": "abc123",
        "turn_index": 0,
        "timestamp": "2026-02-27T10:00:08Z",
        "top_focus_areas": ["Reduce filler words", "Add a BLUF opening"],
        "overall_strengths": ["Clear purpose", "Good vocabulary range"],
        "skill_results": [...]
      }
    }
  ]
}
```
