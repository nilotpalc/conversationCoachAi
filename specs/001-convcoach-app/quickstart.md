# Quickstart: ConvCoach Application

**Feature**: 001-convcoach-app  
**Date**: 2026-02-27  
**Prerequisites**: Python 3.11+, a Google Gemini API key

---

## 1. Clone and Set Up

```bash
# Clone (or navigate to) the repo
cd conv.coach

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\activate             # Windows
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` includes:
- `streamlit>=1.32`
- `google-generativeai>=0.5`
- `python-dotenv>=1.0`
- `pandas>=2.0`

---

## 3. Configure Your API Key

```bash
# Copy the example env file
cp .env.example .env

# Open .env and replace the placeholder:
# GEMINI_API_KEY=your-api-key-here
```

> The `.env` file is gitignored and will never be committed to the repository.

---

## 4. Run the App

```bash
streamlit run src/app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## 5. Use ConvCoach

**Submit a transcript for coaching:**
1. Type or paste a conversation transcript in the chat input box.
2. Optionally prefix with `Purpose: <your goal>` (e.g., `Purpose: persuade`).
3. Press Enter — ConvCoach analyzes the transcript and returns structured feedback.

**Request a rewrite:**
- Add "show rewrite" or "please rewrite" to your message, and ConvCoach will include a before/after rewrite section.

**View progress:**
- Open the sidebar to see your skill scores across all past sessions.

---

## 6. Run Tests

```bash
pytest tests/
```

---

## 7. Project Layout Reference

```text
src/
├── app.py                  # Streamlit entry point
├── agent.py                # Gemini calls and prompt construction
├── skill_selector.py       # Skill selection logic
├── scorer.py               # Rubric scoring + normalization
├── progress_tracker.py     # Session history load/save
├── models/                 # Data models (Session, Feedback, etc.)
└── utils/
    ├── formatting.py       # JSON → table
    └── rewrite_guard.py    # Rewrite intent detection

data/                       # Reference markdown files
sessions/                   # Auto-created; persisted session JSON (gitignored)
tests/                      # Unit + integration tests
.env                        # Your API key (gitignored)
.env.example                # Commit this; contains placeholder only
```
