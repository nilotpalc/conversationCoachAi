"""Session persistence and progress aggregation."""
from __future__ import annotations

import json
from pathlib import Path

from src.models.progress import ProgressRecord
from src.models.session import Session

SESSIONS_DIR = Path(__file__).parent.parent / "sessions"


def _sessions_dir() -> Path:
    """Return the sessions directory, creating it if needed."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR


def save_session(session: Session) -> Path:
    """Serialize a Session to sessions/<session_id>.json.

    Args:
        session: The Session object to persist.

    Returns:
        The Path of the saved file.
    """
    target = _sessions_dir() / f"{session.session_id}.json"
    target.write_text(json.dumps(session.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def load_session(session_id: str) -> Session | None:
    """Deserialize a Session from sessions/<session_id>.json.

    Returns:
        The Session object, or None if the file does not exist.
    """
    path = _sessions_dir() / f"{session_id}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Session.from_dict(data)


def delete_session(session_id: str) -> bool:
    """Delete a session file from disk.

    Returns:
        True if deleted, False if file did not exist.
    """
    path = _sessions_dir() / f"{session_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


def delete_all_sessions() -> int:
    """Delete all session files from disk.

    Returns:
        Number of files deleted.
    """
    sessions_dir = _sessions_dir()
    count = 0
    for json_file in sessions_dir.glob("*.json"):
        if json_file.name == ".gitkeep":
            continue
        json_file.unlink()
        count += 1
    return count


def aggregate_progress() -> list[ProgressRecord]:
    """Scan sessions/*.json and build a list of ProgressRecord for the sidebar.

    Returns:
        List of ProgressRecord sorted by date (newest first).
    """
    sessions_dir = _sessions_dir()
    records: list[ProgressRecord] = []

    for json_file in sorted(sessions_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        if json_file.name == ".gitkeep":
            continue
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            session = Session.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

        # Extract skill scores and focus areas from assistant messages with feedback
        skills_evaluated: list[str] = []
        scores: dict[str, float] = {}
        top_focus_areas: list[str] = []

        for msg in session.messages:
            if msg.role == "assistant" and msg.feedback is not None:
                fb = msg.feedback
                if fb.top_focus_areas and not top_focus_areas:
                    top_focus_areas = fb.top_focus_areas
                for sr in fb.skill_results:
                    if sr.skill_id not in skills_evaluated:
                        skills_evaluated.append(sr.skill_id)
                    scores[sr.skill_id] = sr.normalized_score

        if not skills_evaluated:
            continue  # Skip sessions without any coaching output

        records.append(
            ProgressRecord(
                session_id=session.session_id,
                date=session.created_at,
                skills_evaluated=skills_evaluated,
                scores=scores,
                top_focus_areas=top_focus_areas,
            )
        )

    return records
