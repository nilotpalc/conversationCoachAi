
# Feature Specification: ConvCoach Application

**Feature Branch**: `[001-convcoach-app]`  
**Created**: 2026-02-27  
**Status**: Draft  
**Input**: User description: "Build an application basis the requirements mentioned in app_description.md file"

## Clarifications

### Session 2026-02-27
- Q: When a user submits an empty or irrelevant transcript, what should ConvCoach do? → A: Display a validation error message and prompt the user to submit a valid transcript
- Q: When the Gemini API call fails (e.g., network error, quota exceeded, invalid API key), what should the app do? → A: Display a clear error message to the user explaining the failure; no partial output shown
- Q: How should user progress be persisted between sessions in v1 (single-user local deployment)? → A: Persist progress to a local JSON file on disk between sessions
- Q: When skill registry or scoring files are missing or malformed at startup, what should the app do? → A: Refuse to start and display a clear error identifying the missing/malformed file
- Q: How should the system handle a very long transcript exceeding a practical processing limit? → A: Truncate to a defined maximum length, display a warning that includes the maximum limit, then proceed with analysis

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->


### User Story 1 - Chat-Based Coaching (Priority: P1)
A user submits a conversation transcript or message in a chat interface and receives actionable, research-informed feedback from ConvCoach, including a summary of top focus areas, skill-based analysis, and practical suggestions.

**Why this priority**: This is the core value proposition—delivering immediate, actionable feedback to improve conversational effectiveness.

**Independent Test**: Can be fully tested by submitting a transcript and verifying the output matches the required format and guidelines.

**Acceptance Scenarios**:
1. **Given** a user submits a transcript, **When** ConvCoach processes it, **Then** the user receives a structured response with top focus areas, skill analysis, and suggestions.
2. **Given** a user asks for a rewrite, **When** ConvCoach responds, **Then** the output includes a rewrite section as specified.

---


### User Story 2 - Skill Registry and Scoring (Priority: P2)
ConvCoach selects relevant skills from the skills registry, applies scoring rubrics, and normalizes scores as per guidelines, ensuring transparency and consistency.

**Why this priority**: Ensures feedback is research-based, consistent, and transparent, building user trust.

**Independent Test**: Can be tested by providing different transcripts and verifying correct skill selection, scoring, and normalization.

**Acceptance Scenarios**:
1. **Given** a transcript, **When** ConvCoach analyzes it, **Then** the output references the correct skills, scoring, and normalization methods.

---


### User Story 3 - Progress Tracking (Priority: P3)
The system tracks user progress over time using stable skills and metrics, allowing users to view their improvement history.

**Why this priority**: Progress tracking increases user engagement and supports long-term improvement.

**Independent Test**: Can be tested by submitting multiple transcripts and verifying that progress is tracked and displayed.

**Acceptance Scenarios**:
1. **Given** a user submits multiple transcripts, **When** ConvCoach processes them, **Then** the user can view historical feedback and progress.

---




### Edge Cases
- **Empty/irrelevant transcript**: System MUST display a validation error message and prompt the user to resubmit a valid transcript; no analysis is performed.
- **Gemini API failure**: System MUST display a clear error message describing the failure (e.g., network error, quota exceeded, invalid key); no partial output is shown.
- **Missing or malformed skill registry/scoring files**: System MUST refuse to start and display a clear error message identifying the missing or malformed file.
- **Very long transcript**: System MUST truncate the transcript to a defined maximum character/token length, display a warning message that includes the maximum limit value, and proceed with analysis on the truncated content.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->


### Functional Requirements
- **FR-001**: System MUST provide a chat interface for users to submit transcripts and receive feedback.
- **FR-002**: System MUST analyze transcripts for clarity, structure, balance, tone, vocabulary, and contextual fit.
- **FR-003**: System MUST select 1–3 relevant skills from the skills registry for each analysis.
- **FR-004**: System MUST apply scoring rubrics and normalization as per guidelines.
- **FR-005**: System MUST provide actionable, practical feedback and short rewrites (when requested).
- **FR-006**: System MUST display a "Top 2 Focus Areas" summary at the top of each response.
- **FR-007**: System MUST convert analysis JSON output into a table structure in the response.
- **FR-008**: System MUST track and display user progress over time.
- **FR-009**: System MUST use the Google Gemini LLM for analysis and feedback generation.
- **FR-010**: System MUST store the Gemini API key securely in the project folder (not synced to GitHub).
- **FR-011**: System MUST use the Streamlit package for the user interface.
- **FR-012**: System MUST handle ambiguous but non-empty input by asking exactly one clarifying question, then proceed with best analysis on the next turn. This applies when a transcript is present but context is unclear (e.g., no recognisable conversational purpose).
- **FR-013**: System MUST ensure all feedback is supportive, respectful, and free from cultural bias. *(See also: SC-005 — outcome quality gate.)*
- **FR-014**: System MUST follow the required output formats and reference files exactly as specified.
- **FR-015**: System MUST display a clear validation error message and prompt the user to resubmit a valid transcript when input is empty, whitespace-only, or clearly gibberish (< 10 meaningful characters); no skill selection, scoring, or analysis is performed in this case.
- **FR-016**: System MUST display a clear error message describing the cause when any Gemini API call fails (network error, quota exceeded, or invalid API key); no partial output is surfaced to the user.
- **FR-017**: System MUST persist session history and progress data to a local JSON file on disk so that progress is retained across app restarts (v1 single-user local deployment).
- **FR-018**: System MUST refuse to start and display a clear error message identifying the missing or malformed file if any required skill registry or scoring reference file is absent or unparseable at startup.
- **FR-019**: System MUST truncate transcripts exceeding **10,000 characters** to that limit, display an inline warning message stating the maximum limit (10,000 characters), and proceed with analysis on the truncated content.


### Non-Functional Requirements

- **NFR-001 (Accessibility — v1 Scope)**: The application relies on Streamlit's default rendering, which provides baseline WCAG 2.1 AA compliance for standard components. No custom widgets that break keyboard navigation or screen reader compatibility are permitted. Full accessibility audit is deferred to a post-v1 release. *(Satisfies Constitution §III within single-user local deployment scope.)*
- **NFR-002 (Privacy)**: Transcripts may contain sensitive conversational content. Session JSON files are stored locally in `sessions/` (gitignored) and are the user's responsibility to manage. No transcript content is transmitted beyond the Gemini API call. Data retention policy is at the user's discretion for v1.


### Key Entities
- **Session**: Represents a single usage session in the app; attributes include session ID, created timestamp, and ordered message history. Progress is aggregated across sessions by `session_id`. No user authentication is required for v1 (single-user local deployment). Session and progress data is persisted to a local JSON file on disk. *(Note: supersedes the originally-named "User" entity, which is not modelled separately — see data-model.md §Session.)*
- **Transcript**: Represents a submitted conversation or message; attributes include text, timestamp, and optional declared purpose.
- **Skill**: Represents a communication skill from the registry; attributes include skill ID, description, and scoring rubric.
- **Feedback**: Represents the structured response generated by ConvCoach; includes focus areas, analysis, scores, and suggestions.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->


### Measurable Outcomes
- **SC-001**: 95% of user submissions receive feedback in under 5 seconds.
- **SC-002**: 100% of feedback responses follow the required output format and reference files.
- **SC-003**: 100% of responses contain at least one coaching tip, one rewrite (when requested), and a populated "Top 2 Focus Areas" block, as verified by the integration test suite.
- **SC-004**: All sessions are persisted to `sessions/` as JSON files; the sidebar displays cumulative progress across all prior sessions, showing date, skills evaluated, normalized scores, and top focus areas per session — verifiable by submitting 2+ transcripts across separate app restarts.
- **SC-005**: No user receives culturally inappropriate or unsupportive feedback (verified by review).
