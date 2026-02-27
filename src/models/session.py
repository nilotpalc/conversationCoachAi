"""Data models for sessions and transcripts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.feedback import Feedback


@dataclass
class Transcript:
    """Represents the user-submitted conversation text for analysis."""

    raw_text: str
    purpose: str | None = None
    rewrite_requested: bool = False


@dataclass
class Message:
    """A single turn in the conversation."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    feedback: "Feedback | None" = None

    def to_dict(self) -> dict:
        result: dict = {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "feedback": None,
        }
        if self.feedback is not None:
            result["feedback"] = self.feedback.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        from src.models.feedback import Feedback  # local import to avoid circular

        feedback = None
        if data.get("feedback") is not None:
            feedback = Feedback.from_dict(data["feedback"])
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data["timestamp"],
            feedback=feedback,
        )


@dataclass
class Session:
    """Represents a single user session."""

    session_id: str
    created_at: str
    messages: list[Message] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "messages": [m.to_dict() for m in self.messages],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
        )
