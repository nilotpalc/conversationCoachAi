# Research: ConvCoach Application

**Feature**: 001-convcoach-app  
**Date**: 2026-02-27  
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## Decision 1: LLM SDK for Google Gemini

**Decision**: Use the official `google-generativeai` Python SDK (`pip install google-generativeai`).

**Rationale**: Official SDK maintained by Google; supports Gemini 1.5 Pro/Flash models; supports system instructions, multi-turn conversation history, and streaming responses. Best-practice approach for production Python apps using Gemini.

**Alternatives considered**:
- REST API directly via `httpx/requests`: More verbose, no built-in retry or streaming helpers.
- LangChain `ChatGoogleGenerativeAI`: Adds heavy abstraction overhead not needed for this single-agent use case.

---

## Decision 2: API Key Management

**Decision**: Store the Gemini API key in a `.env` file at project root, loaded via `python-dotenv`. The `.env` file is added to `.gitignore`. An `.env.example` file with a placeholder is committed for developer setup.

**Rationale**: Industry-standard practice for Python projects. Prevents accidental credential exposure. Aligns with FR-010.

**Alternatives considered**:
- Hardcoded in source: Rejected — violates security standard and FR-010.
- System environment variables only: Valid but less dev-friendly; `.env` approach is more portable.

---

## Decision 3: Session/Conversation Persistence

**Decision**: Persist session history as JSON files in a `sessions/` directory at project root. Each session is a JSON file named by timestamp + session ID. A `progress_tracker.py` module aggregates these for the progress view. The `sessions/` directory is gitignored.

**Rationale**: No database required for single-user or small-team local deployment. JSON files are human-readable, zero-dependency, and easy to extend. Streamlit's `st.session_state` holds in-memory state during an active session; JSON files enable cross-session progress tracking.

**Alternatives considered**:
- SQLite: More robust for multi-user, but over-engineered for stated scope.
- Streamlit Community Cloud session storage: Not available without cloud deployment.

---

## Decision 4: Skill Selection Logic

**Decision**: Implement a two-step skill selector in `skill_selector.py`:
1. **Rule-based pass**: Keyword and intent matching against transcript + user request (e.g., "filler", "structure", "purpose") maps to specific skill IDs.
2. **LLM fallback**: If no rule match, include the skill registry descriptions in the Gemini system prompt and let the model select 1–3 most relevant skills.
Default skills when no context: `CA01_fillers`, `SC01_signposting`, `CE02_purpose_alignment`.

**Rationale**: Rule-based selection is fast and deterministic for common cases. LLM fallback ensures coverage for unusual transcripts. Aligns with FR-003 and app_description.md guidelines.

**Alternatives considered**:
- LLM-only selection: Non-deterministic; harder to test. Rejected in favor of ruled-based primary path.
- Static always-use-defaults: Too rigid; reduces relevance of feedback.

---

## Decision 5: Streamlit Chat UI Pattern

**Decision**: Use Streamlit's native `st.chat_input` and `st.chat_message` components (available since Streamlit 1.24) for the conversation UI. Multi-turn history is managed in `st.session_state["messages"]`. A sidebar exposes the progress history view.

**Rationale**: Native Streamlit chat components provide the cleanest UX with minimal code. They handle message rendering, scrolling, and iteration. Matches the [User]/[Agent] display pattern specified in app_description.md.

**Alternatives considered**:
- Custom HTML/CSS components: More effort, less maintainable, no Streamlit-native benefits.
- Gradio: Separate framework; not specified; adds unnecessary dependency.

---

## Decision 6: Rewrite Section Gating

**Decision**: Implement `rewrite_guard.py` — a small utility that inspects the user's latest message for explicit rewrite intent keywords (`rewrite`, `rephrase`, `show rewrite`, `alternative version`, etc.). The Gemini prompt includes/excludes the rewrite instruction based on this flag.

**Rationale**: FR-007 and app_description.md rule 6 require the rewrite section to appear only on explicit user request. A deterministic keyword guard is simpler and more reliable than asking the model to decide.

**Alternatives considered**:
- Always include rewrite in the prompt and filter in output: Wastes tokens and increases latency.
- Let the LLM decide: Non-deterministic; doesn't satisfy the explicit-only requirement.

---

## Decision 7: Output Table Rendering

**Decision**: The `formatting.py` utility converts the JSON analysis block for each skill into a `pandas` DataFrame and renders it as `st.dataframe()` or `st.markdown()` table in the Streamlit UI.

**Rationale**: Pandas is already a common Python data tool; `st.dataframe()` provides a clean, sortable display. Aligns with FR-007 (analysis JSON → table structure).

**Alternatives considered**:
- Manual markdown table string construction: Error-prone and harder to maintain.
- Display raw JSON: Violates FR-007 and output format contract.

---

## Decision 8: Scoring Pipeline

**Decision**: Implement `scorer.py` with two modes:
1. **Threshold-based** for skills with numeric thresholds (`CA01`, `SC01`) — directly compare extracted metrics to rubric thresholds in `scorenorm.md`.
2. **Qualitative/LLM-judged** for skills without numeric thresholds (`CB02`, `TP01`, `VE01`, `CE02`) — include rubric descriptions in prompt, Gemini returns a 0–5 score with rationale.
Final score = `0.6 × rules_score + 0.4 × llm_judgment` where both apply (from `scorenorm.md` weights).

**Rationale**: Matches the hybrid scoring approach defined in `scorenorm.md`. Threshold-based path is testable deterministically; LLM path handled qualitatively.

**Alternatives considered**:
- LLM-only scoring: Inconsistent; not aligned with scoring guidance.
- Rules-only: Insufficient for qualitative skills.

---

## Resolved Clarifications

| Item | Resolution |
|------|-----------|
| Python version | Python 3.11+ |
| Gemini model | `gemini-1.5-flash` (default; configurable to `gemini-1.5-pro`) |
| Multi-user support | Out of scope; single-user local deployment |
| Database | Not needed; JSON file persistence |
| Deployment target | Local machine via `streamlit run src/app.py` |
| Auth/login | Not required for initial version |
| Data retention | Sessions retained indefinitely in `sessions/` until manually cleared |
