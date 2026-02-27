# ConvCoach

An AI-powered conversational coaching application that analyzes conversation transcripts and delivers actionable, research-informed feedback using Google Gemini.

---

## Overview

ConvCoach is a Streamlit chat application where users paste conversation transcripts and receive structured coaching feedback. The agent evaluates communication across a set of defined skills — such as filler usage, signposting, sentence complexity, and tone — and returns scored analysis, coaching tips, and optional rewrites. Progress is persisted across sessions so users can track improvement over time.

---

## Features

- **Chat-based interface** — Submit transcripts or messages and receive structured feedback in a conversational UI
- **Skill-based analysis** — Evaluates 1–3 skills per turn from a curated registry (e.g., filler usage, signposting, topic drift, empathy)
- **Transparent scoring** — Hybrid scoring: 60% rules-based thresholds + 40% LLM judgment, normalized to a 0–5 scale
- **Actionable coaching** — Top 2 focus areas, micro-behavior suggestions, and explanations of why each change helps
- **On-demand rewrites** — Include "show rewrite" in your message to get a before/after rewrite section
- **Progress tracking** — Session history persisted locally; view skill score trends in the sidebar
- **Gemini LLM** — Powered by Google Gemini (configurable model via environment variable)

---

## Project Structure

```
conv.coach/
├── src/
│   ├── app.py                  # Streamlit entry point
│   ├── agent.py                # Gemini prompt construction and response parsing
│   ├── skill_selector.py       # Skill selection logic
│   ├── scorer.py               # Rubric scoring + normalization
│   ├── progress_tracker.py     # Session history load/save
│   ├── models/                 # Data models (Session, Feedback, Skill, etc.)
│   └── utils/
│       ├── formatting.py       # JSON → table conversion
│       └── rewrite_guard.py    # Rewrite intent detection
├── data/                       # Reference markdown files (skills, rubrics, output format)
├── sessions/                   # Auto-created; persisted session JSON (gitignored)
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end chat flow tests
├── specs/                      # Feature specifications and planning docs
├── app_description.md          # System instructions for the ConvCoach agent
├── skillregistry.md            # Skill definitions and evaluation instructions
├── scoringrubrics.md           # Scoring rubrics per skill
├── scorenorm.md                # Score normalization methodology
├── outputstructure.md          # Required output format definition
├── pyproject.toml              # Project metadata and dependencies (Poetry)
├── requirements.txt            # Pip fallback dependency list
└── .env.example                # API key placeholder (copy to .env)
```

---

## Prerequisites

- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd conv.coach
```

### 2. Create a virtual environment and install dependencies

**Using `uv` (recommended):**
```bash
uv venv
uv pip install -e .
uv pip install -e ".[dev]"   # includes pytest and ruff
```

**Using pip:**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

> A virtual environment is strongly recommended to isolate project dependencies from your system Python.

### 3. Configure your API key

Create a `.env` file in the repo root folder

Open `.env` and set your key:

```
GEMINI_API_KEY=your-api-key-here
```

> `.env` is gitignored and will never be committed to the repository.

You can also override the Gemini model via:
```
GEMINI_MODEL=gemini-3-pro-preview   # default
```

---

## Running the App

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "."; streamlit run src/app.py
```

**macOS/Linux:**
```bash
PYTHONPATH=. streamlit run src/app.py
```

The app opens at `http://localhost:8501`.

> Setting `PYTHONPATH` to the repo root ensures `src/` imports resolve correctly when running from the project directory.

---

## Usage

### Submit a transcript for coaching

1. Type or paste a conversation transcript into the chat input box.
2. Optionally prefix with `Purpose: <your goal>` (e.g., `Purpose: persuade`).
3. Press Enter — ConvCoach analyzes the transcript and returns structured feedback.

**Example input:**
```
Purpose: persuade
Transcript:
[00:00 A] Um, so I was kind of thinking we could maybe change the plan...
[00:06 B] What do you propose?
```

### Request a rewrite

Add a phrase like `"show rewrite"` or `"please rewrite"` to your message to include a before/after rewrite section in the response.

### View progress

Open the sidebar to see your skill scores and trends across all past sessions.

---

## Output Format

Each response is structured as:

```
## Summary
- Top 2 Focus Areas: ...
- Overall strengths: ...

## Skill Scores
- CA01_fillers (Filler Usage): 1 — High density; many turn-start fillers.

## Analysis
| Metric | Value |
|--------|-------|
| ...    | ...   |

## Coaching
- Start with your recommendation in sentence one.
- Why it helps: Reduces cognitive load and signals confidence.

## Rewrites (if requested)
[ {"before":"...", "after":"...", "rationale":"..."} ]
```

---

## Skills Registry

ConvCoach evaluates transcripts against a curated set of conversational skills, including:

| ID | Label |
|----|-------|
| `CA01_fillers` | Filler Usage |
| `CA02_sentence_complexity` | Sentence Length & Complexity |
| `CA03_ambiguous_references` | Ambiguous References |
| `SC01_signposting` | Signposting & Framing |
| `SC02_topic_drift` | Topic Drift |
| `CE02_purpose_alignment` | Purpose Alignment |

See [skillregistry.md](skillregistry.md) for the full registry and evaluation instructions.

---

## Running Tests

```bash
pytest tests/
```

Tests are organized into `unit/`, `integration/`, and `e2e/` subdirectories.

---

## Development

Lint and format checks use [Ruff](https://docs.astral.sh/ruff/):

```bash
ruff check src/ tests/
ruff format src/ tests/
```

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *(required)* | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-3-pro-preview` | Gemini model to use |

---

## License

This project is not yet licensed. All rights reserved.
