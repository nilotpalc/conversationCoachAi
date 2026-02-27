---
description: "Task list for ConvCoach Application implementation"
---

# Tasks: ConvCoach Application

**Input**: Design documents from `/specs/001-convcoach-app/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/agent-contract.md ✅, quickstart.md ✅

**Tech Stack**: Python 3.11+, Streamlit ≥1.32, google-generativeai ≥0.5, python-dotenv ≥1.0, pandas ≥2.0, pytest
**Project Layout**: Single-project; `src/` at repository root; `data/`, `sessions/`, `tests/` at root

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: User story this task delivers (US1, US2, US3)
- Exact file paths are included in every task description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and tooling. No user story work begins until this phase is complete.

- [X] T001 Create project directory structure: `src/`, `src/models/`, `src/utils/`, `data/`, `sessions/.gitkeep`, `tests/unit/`, `tests/integration/`, `tests/e2e/` per plan.md
- [X] T002 Create `requirements.txt` with pinned dependencies: `streamlit>=1.32`, `google-generativeai>=0.5`, `python-dotenv>=1.0`, `pandas>=2.0`, `pytest>=7.0`, `ruff>=0.3`
- [X] T003 [P] Create `.env.example` with `GEMINI_API_KEY=your-api-key-here` placeholder and configure `.gitignore` to exclude `.env`, `sessions/`, `__pycache__/`, `.venv/`
- [X] T004 [P] Populate `data/` directory: copy `skillregistry.md`, `scoringrubrics.md`, `scorenorm.md`, `outputstructure.md` from workspace root to `data/`
- [X] T005 Create Python package init files: `src/__init__.py`, `src/models/__init__.py`, `src/utils/__init__.py`, `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/e2e/__init__.py`
- [X] T036 [P] Configure `ruff` linter: create `pyproject.toml` with `[tool.ruff]` section (`line-length = 100`, `target-version = "py311"`); verify `ruff check src/ tests/` passes on empty scaffold

**Checkpoint**: Project scaffold ready — dependencies installable, environment configurable, linting enforced

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models used across ALL user stories. No user story work can begin until these models are in place.

**⚠️ CRITICAL**: Models are imported by agent.py, skill_selector.py, scorer.py, and progress_tracker.py — implement these before any Phase 3+ work.

- [X] T006 [P] Create `Skill`, `SkillResult`, and `RewritePair` dataclasses in `src/models/skill.py` per data-model.md (fields: id, label, when_to_use, analysis_instructions, coaching_instructions, rewrite_instructions, output_schema; SkillResult: skill_id, raw_score, normalized_score, rationale, metrics, examples, insight, coaching_tips, why_it_helps, rewrite)
- [X] T007 [P] Create `Transcript`, `Message`, and `Session` dataclasses in `src/models/session.py` per data-model.md (Transcript: raw_text, purpose, rewrite_requested; Message: role, content, timestamp, feedback; Session: session_id, created_at, messages)
- [X] T008 Create `Feedback` dataclass in `src/models/feedback.py` per data-model.md (fields: session_id, turn_index, timestamp, top_focus_areas, overall_strengths, skill_results) — depends on `SkillResult` from T006
- [X] T009 [P] Create `ProgressRecord` dataclass in `src/models/progress.py` per data-model.md (fields: session_id, date, skills_evaluated, scores, top_focus_areas)

**Checkpoint**: All data models in place — user story implementation can now begin

---

## Phase 3: User Story 1 — Chat-Based Coaching (Priority: P1) 🎯 MVP

**Goal**: A user submits a transcript through the Streamlit chat UI and receives a structured coaching response including top focus areas, skill analysis table, coaching tips, and optional rewrites — all powered by Gemini.

**Independent Test**: Run `streamlit run src/app.py`, submit a sample transcript, and verify the output matches the structure defined in `data/outputstructure.md` and `specs/001-convcoach-app/contracts/agent-contract.md`.

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement rewrite intent keyword detection in `src/utils/rewrite_guard.py` (returns `bool`; matches keywords: "rewrite", "rephrase", "show rewrite", "alternative version" per research.md Decision 6)
- [X] T011 [P] [US1] Implement `analysis_json_to_table()` in `src/utils/formatting.py` — converts per-skill JSON analysis dict to a pandas DataFrame and returns a markdown table string (per research.md Decision 7 and agent-contract.md Analysis Block schema)
- [X] T012 [US1] Implement `select_skills()` in `src/skill_selector.py` — returns 1–3 `Skill` objects loaded from `data/skillregistry.md`; uses default skills (`CA01_fillers`, `SC01_signposting`, `CE02_purpose_alignment`) when no match; includes LLM fallback when no keyword rule matches (per research.md Decision 4 and FR-003)
- [X] T013 [US1] Implement basic LLM-judged scoring in `src/scorer.py` — `score_transcript(transcript, skills)` calls Gemini with rubric context and returns a `list[SkillResult]` with 0–5 qualitative scores and rationale (per research.md Decision 8, qualitative path)
- [X] T020 [US1] Implement hybrid normalization in `src/scorer.py` — `normalize_score(rules_score, llm_score)` applies `0.6 × rules_score + 0.4 × llm_score` weighting per `data/scorenorm.md`; update `score_transcript()` so `SkillResult.normalized_score` is always populated (depends on T013; **promoted from Phase 4** to satisfy agent-contract.md G-07 from MVP; resolves **C3**)
- [X] T014 [US1] Implement `ConvCoachAgent` in `src/agent.py` — constructs system prompt in the order defined in agent-contract.md Prompt Construction Contract (identity → skills → rubrics → normalization → output format → optional rewrite instructions → transcript), calls Gemini `gemini-1.5-flash`, builds `Feedback` response, and returns formatted `AgentOutput` (depends on T010, T011, T012, T013, T020)
- [X] T015 [US1] Implement Streamlit chat UI in `src/app.py` — initializes session state, renders `st.chat_input` and `st.chat_message` turns, calls `ConvCoachAgent`, displays `Feedback` as structured markdown (summary → skill scores → analysis table → coaching → optional rewrites) per agent-contract.md Output Contract (depends on T014)
- [X] T016 [P] [US1] Add unit tests for `formatting.py` in `tests/unit/test_formatting.py` — verify JSON with metrics/examples/insight converts to correct markdown table structure
- [X] T017 [US1] Add integration smoke test in `tests/integration/test_agent_pipeline.py` — mock Gemini API, submit a sample transcript, verify `AgentOutput` fields are all populated per agent-contract.md Output Schema (depends on T014)

**Checkpoint**: User Story 1 fully functional — submit transcript → receive structured coaching response

---

## Phase 4: User Story 2 — Skill Registry and Scoring (Priority: P2)

**Goal**: ConvCoach selects contextually correct skills using rule-based matching, applies threshold-based scoring for quantitative skills (CA01, SC01), and normalizes all scores using the hybrid `0.6 × rules + 0.4 × LLM` formula from `data/scorenorm.md` — ensuring transparency and consistency.

**Independent Test**: Submit transcripts with known filler word counts and structure markers; verify skill IDs match the registry, raw scores align with rubric thresholds, and normalized scores follow the formula in `data/scorenorm.md`.

### Implementation for User Story 2

- [X] T018 [US2] Enhance `src/skill_selector.py` — add rule-based keyword/intent matching pass (step 1) before LLM fallback: map transcript keywords (e.g., "um," "uh," "so" → `CA01_fillers`; missing transitions → `SC01_signposting`) to skill IDs per research.md Decision 4 (depends on T012; resolves **I2**)
- [X] T019 [US2] Enhance `src/scorer.py` — add `threshold_score()` for quantitative skills (`CA01_fillers`, `SC01_signposting`) that compares extracted metrics against rubric thresholds in `data/scoringrubrics.md` to produce a deterministic `raw_score` (per research.md Decision 8, threshold-based path) (depends on T013; resolves **I2**)
- [X] T021 [US2] Integrate enhanced scoring into `src/agent.py` — ensure `SkillResult.normalized_score` is always populated via the scorer pipeline and `Skill` IDs/labels exactly match `data/skillregistry.md` per agent-contract.md G-06 and G-07 (depends on T019, T020)
- [X] T022 [P] [US2] Add unit tests for `skill_selector.py` in `tests/unit/test_skill_selector.py` — verify rule-based matching returns correct skill IDs for known inputs; verify LLM fallback returns 1–3 skills; verify default skills are returned when no context
- [X] T023 [P] [US2] Add unit tests for `scorer.py` in `tests/unit/test_scorer.py` — verify threshold scoring for CA01/SC01 against known metric values; verify normalization formula; verify qualitative scoring returns score in [0.0, 5.0]

**Checkpoint**: User Stories 1 AND 2 independently functional — skill selection and scoring are research-based, consistent, and transparent

---

## Phase 5: User Story 3 — Progress Tracking (Priority: P3)

**Goal**: Session history is persisted to `sessions/<session_id>.json` after every assistant turn, and users can view their skill score history in the sidebar across all past sessions.

**Independent Test**: Submit 2+ transcripts across separate Streamlit sessions; verify `sessions/` contains JSON files matching the persistence schema in data-model.md; verify the sidebar shows a progress table with per-session skill scores.

### Implementation for User Story 3

- [X] T024 [US3] Implement `save_session()` and `load_session()` in `src/progress_tracker.py` — serialize/deserialize `Session` objects (including nested `Message` and `Feedback`) to/from `sessions/<session_id>.json` using the JSON schema in data-model.md Persistence Format
- [X] T025 [US3] Implement `aggregate_progress()` in `src/progress_tracker.py` — scans `sessions/*.json`, builds a `list[ProgressRecord]` with per-session skill scores and top focus areas for display (depends on T024)
- [X] T026 [US3] Integrate session persistence into `src/app.py` — call `save_session()` after each assistant response is rendered (agent-contract.md G-08); ensure session_id is generated at session start using `uuid.uuid4()`
- [X] T027 [US3] Add sidebar progress view to `src/app.py` — call `aggregate_progress()`, render skill scores as `st.dataframe()` or `st.markdown()` table showing date, skills evaluated, scores, and top focus areas per session (depends on T025, T026)
- [X] T028 [P] [US3] Add unit tests for `progress_tracker.py` in `tests/unit/test_progress_tracker.py` — verify save/load round-trip preserves all fields; verify aggregation returns correct `ProgressRecord` entries from multiple session files

**Checkpoint**: All three user stories independently functional — chat coaching, accurate scoring, and progress tracking all work end-to-end

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Behavioural guarantees, edge cases, input validation, and overall hardening across all user stories.

- [ ] T029 [P] Add input validation in `src/agent.py` — if `raw_text` is empty, whitespace-only, or < 10 meaningful characters, return a validation error message (e.g., "Please submit a valid conversation transcript.") and do **not** run skill selection, scoring, or Gemini call (FR-015). Ambiguous but non-empty input is handled by T031 (FR-012).
- [ ] T030 [P] Add error handling in `src/agent.py` — catch Gemini API errors (rate limit, timeout, invalid key) and surface a user-friendly message in `st.chat_message`; catch missing `data/*.md` file errors at startup with a clear setup instruction
- [ ] T031 Implement single-clarifying-question flow in `src/agent.py` — when context is ambiguous (no transcript detected, only small talk), ask exactly one clarifying question then proceed with best analysis on next turn (agent-contract.md G-05 and FR-012)
- [ ] T032 [P] Embed cultural bias and tone guardrails in the Gemini system prompt in `src/agent.py` — include explicit instructions: always start with strengths (G-02), never demean or use culturally biased language (G-01), all feedback must be supportive and respectful (FR-013)
- [ ] T033 Run full test suite (`pytest tests/`) and resolve all failures — verify unit tests (formatting, skill_selector, scorer, progress_tracker) and integration test all pass
- [ ] T034 Validate end-to-end `quickstart.md` steps — create fresh `.venv`, install requirements, configure `.env`, run `streamlit run src/app.py`, submit the sample transcript from `specs/001-convcoach-app/quickstart.md` section 5, verify structured output
- [ ] T037 [P] [US1] Implement transcript truncation in `src/agent.py` — before calling Gemini, check `len(transcript.raw_text) > 10000`; if so, truncate to 10,000 characters, update `transcript.raw_text`, and surface an `st.warning()` with the message "Transcript truncated to 10,000 characters for processing." (FR-019; resolves **C1**)
- [ ] T035 [P] Add E2E test in `tests/e2e/test_chat_flow.py` using Streamlit `AppTest` — simulate submitting a transcript via `AppTest.from_file("src/app.py").run()`, assert rendered output contains a summary block, 1–3 skill score entries with values in [0.0, 5.0], and a coaching block; run via `pytest tests/e2e/` (Constitution II: E2E tests required; fulfils plan.md constitution check §II; `tests/e2e/__init__.py` already created in T005)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **BLOCKS all user story phases**
- **User Story Phases (3, 4, 5)**: All depend on Phase 2 completion; can proceed in priority order (US1 → US2 → US3) or in parallel if staffed
- **Polish (Phase 6)**: Depends on all desired user story phases being complete

### User Story Dependencies

- **US1 (Phase 3)**: Starts after Phase 2 — no dependency on US2 or US3
- **US2 (Phase 4)**: Starts after Phase 2 — enhances US1 components (`skill_selector.py`, `scorer.py`); independently testable via unit tests
- **US3 (Phase 5)**: Starts after Phase 2 — adds `progress_tracker.py` and sidebar; independently testable without US2

### Within Each User Story

- Utility tasks (T010, T011) before agent (T014)
- Models (Phase 2) before services and agents
- Core implementation before tests where integration tests require running components
- Story complete and checkpointed before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003 and T004 in parallel
- **Phase 2**: T006, T007, T009 all in parallel; T008 after T006
- **Phase 3**: T010 and T011 in parallel (different utility files); T016 in parallel with T015
- **Phase 4**: T022 and T023 in parallel (different test files); T018 and T019 can run in parallel once their respective Phase 3 dependencies (T012, T013) are complete
- **Phase 5**: T028 in parallel with T026/T027
- **Phase 6**: T029, T030, T032 in parallel (different concerns)

---

## Parallel Execution Examples

### Phase 2 — Foundational Models

```
Parallel batch:
  T006 — src/models/skill.py    (Skill, SkillResult, RewritePair)
  T007 — src/models/session.py  (Transcript, Message, Session)
  T009 — src/models/progress.py (ProgressRecord)

Then:
  T008 — src/models/feedback.py (Feedback — needs SkillResult from T006)
```

### Phase 3 — US1 Utilities First

```
Parallel batch:
  T010 — src/utils/rewrite_guard.py
  T011 — src/utils/formatting.py

Then sequential:
  T012 — src/skill_selector.py  (depends on Skill model)
  T013 — src/scorer.py          (depends on Transcript, SkillResult models)
  T020 — src/scorer.py          (normalization — depends on T013)
  T014 — src/agent.py           (depends on T010, T011, T012, T013, T020)
  T015 — src/app.py             (depends on T014)

Parallel with T015:
  T016 — tests/unit/test_formatting.py
```

### Phase 4 — US2 Tests in Parallel

```
Parallel batch (after T018, T019, T021 complete; T020 completed in Phase 3):
  T022 — tests/unit/test_skill_selector.py
  T023 — tests/unit/test_scorer.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational models (**CRITICAL — blocks everything**)
3. Complete Phase 3: User Story 1 (T010–T017)
4. **STOP and VALIDATE**: Run `streamlit run src/app.py`, submit transcript, verify structured output
5. Demo / deploy MVP if ready

### Incremental Delivery

1. Setup (Phase 1) + Foundational (Phase 2) → scaffold ready
2. User Story 1 (Phase 3) → **MVP**: chat coaching works end-to-end
3. User Story 2 (Phase 4) → scoring is research-based and transparent
4. User Story 3 (Phase 5) → progress tracking and history
5. Polish (Phase 6) → production-ready hardening

### Parallel Team Strategy

With multiple developers, once Foundational phase (Phase 2) is complete:
- Developer A: User Story 1 (chat UI + agent pipeline)
- Developer B: User Story 2 (skill selection + scoring pipeline)
- Developer C: User Story 3 (progress tracking)

---

## Notes

- `[P]` tasks touch different files and have no blocking dependencies within their phase — safe to parallelize
- `[StoryN]` label maps each task to its user story for traceability
- Each story has an independent test criterion — validate before moving to the next
- Tests follow the project structure in plan.md (`tests/unit/`, `tests/integration/`, `tests/e2e/`)
- Commit after each task or logical group; use the task ID as the commit scope
- **Do not** start Phase 3+ until Phase 2 models are fully implemented and importable
- `sessions/` directory must be gitignored; `data/` files are read-only references
- Gemini model: `gemini-1.5-flash` (default), configurable to `gemini-1.5-pro` via `.env`
