# Implementation Plan: ConvCoach Application

**Branch**: `001-convcoach-app` | **Date**: 2026-02-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-convcoach-app/spec.md`

## Summary

ConvCoach is a Streamlit-based single-user conversational coaching application powered by Google Gemini. The agent accepts conversation transcripts, selects 1–3 relevant communication skills from a configurable registry, applies hybrid rubric scoring (threshold-based + LLM-judged, weighted 0.6/0.4), and returns structured feedback: top 2 focus areas, skill-level analysis table, coaching tips, and optional rewrites. Session history is persisted to local JSON files for cross-session progress tracking.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Streamlit ≥1.32, google-generativeai ≥0.5, python-dotenv ≥1.0, pandas ≥2.0, pytest ≥7.0, ruff ≥0.3  
**Storage**: Local JSON files in `sessions/` directory (single-user; no database)  
**Testing**: pytest — unit tests (`tests/unit/`) + integration tests (`tests/integration/`) with mocked Gemini API  
**Target Platform**: Local machine (Windows/macOS/Linux) via `streamlit run src/app.py`  
**Project Type**: Streamlit web application (local desktop deployment)  
**Performance Goals**: 95% of submissions receive full feedback in < 5 seconds (SC-001); standard Gemini API latency applies  
**Constraints**: Single-user local deployment; no authentication; no cloud deployment; Gemini API key stored in `.env` (gitignored); transcript max length enforced with inline warning  
**Scale/Scope**: Single user; ~10 source files; JSON file persistence; sessions retained indefinitely until manually cleared

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| C1 | **Code Quality** — Linting and static analysis enforced | ✅ PASS | `ruff` configured in `pyproject.toml` (T036); `ruff check src/ tests/` runs on scaffold |
| C2 | **Testing Standards** — Automated tests for all features | ✅ PASS | Unit tests (T016, T022, T023, T028) + integration tests (T017, T031) per tasks.md |
| C3 | **UX Consistency** — Unified design system and interaction patterns | ✅ PASS | Single Streamlit chat UI per agent-contract.md; consistent `[User]/[Agent]` pattern; sidebar progress view |
| C4 | **Performance Requirements** — Features meet defined benchmarks | ✅ PASS | SC-001 (< 5 s feedback) enforced; Gemini `gemini-1.5-flash` chosen for speed (research.md Decision 1) |
| C5 | **Dependencies tracked and approved** | ✅ PASS | All dependencies in `requirements.txt`; no unapproved packages |
| C6 | **Security** — No credential exposure | ✅ PASS | API key in `.env` + `.gitignore`; `.env.example` committed (research.md Decision 2) |
| C7 | **Development Workflow** — Spec → research → plan → tasks → implementation | ✅ PASS | All planning phases complete before implementation |

**Post-Design Re-check (Phase 1)**: All gates remain PASS. Hybrid scoring (C3-normalized) and persistent JSON (C5) are both justified by single-user scope.

## Project Structure

### Documentation (this feature)

```text
specs/001-convcoach-app/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/
│   └── agent-contract.md  # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── app.py                   # Streamlit entry point — chat UI, session state management
├── agent.py                 # ConvCoachAgent — Gemini prompt construction and response parsing
├── skill_selector.py        # Rule-based + LLM-fallback skill selection
├── scorer.py                # Threshold-based and LLM-judged scoring + normalization
├── progress_tracker.py      # Load/save session JSON; aggregate ProgressRecord list
├── models/
│   ├── __init__.py
│   ├── skill.py             # Skill, SkillResult, RewritePair dataclasses
│   ├── session.py           # Transcript, Message, Session dataclasses
│   ├── feedback.py          # Feedback dataclass
│   └── progress.py          # ProgressRecord dataclass
└── utils/
    ├── __init__.py
    ├── formatting.py        # analysis JSON → pandas DataFrame → markdown table
    └── rewrite_guard.py     # Rewrite intent keyword detection (returns bool)

data/                        # Reference markdown files (skillregistry, rubrics, scorenorm, outputstructure)
sessions/                    # Auto-created; persisted session JSON files (gitignored)
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_formatting.py
│   ├── test_rewrite_guard.py
│   ├── test_skill_selector.py
│   └── test_scorer.py
└── integration/
    ├── __init__.py
    ├── test_agent_pipeline.py
    └── test_progress_tracker.py

pyproject.toml               # ruff linter configuration
requirements.txt             # Pinned dependencies
.env.example                 # API key placeholder (committed)
.env                         # Actual API key (gitignored)
.gitignore
```

**Structure Decision**: Single-project layout (`src/` at repository root). No frontend/backend split needed — Streamlit handles both UI and application logic in the same Python process. The `models/` subpackage separates data structures from business logic. `utils/` holds stateless helper functions. `data/` holds reference markdown files loaded at startup. All paths match quickstart.md and tasks.md.
