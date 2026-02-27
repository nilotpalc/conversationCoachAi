"""ConvCoach — Streamlit chat UI with session persistence and progress sidebar."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from src.agent import ConvCoachAgent
from src.models.session import Message, Session

# Page config
st.set_page_config(
    page_title="ConvCoach",
    page_icon="💬",
    layout="wide",
)


@st.cache_resource
def get_agent() -> ConvCoachAgent:
    """Instantiate the ConvCoachAgent once per Streamlit server lifecycle."""
    try:
        return ConvCoachAgent()
    except Exception:
        get_agent.clear()
        raise


def init_session_state() -> None:
    """Initialise all required session_state keys."""
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state["messages"] = []  # list of Message objects
    if "turn_index" not in st.session_state:
        st.session_state["turn_index"] = 0
    if "session_obj" not in st.session_state:
        st.session_state["session_obj"] = Session(
            session_id=st.session_state["session_id"],
            created_at=datetime.now(timezone.utc).isoformat(),
        )


def new_session() -> None:
    """Clear current session state and start a fresh session."""
    for key in ["session_id", "messages", "turn_index", "session_obj"]:
        st.session_state.pop(key, None)
    st.rerun()


def load_past_session(session_id: str) -> None:
    """Load a past session into the active chat view."""
    from src.progress_tracker import load_session

    session = load_session(session_id)
    if session is None:
        st.error("Could not load session.")
        return
    st.session_state["session_id"] = session.session_id
    st.session_state["messages"] = session.messages
    st.session_state["turn_index"] = sum(1 for m in session.messages if m.role == "user")
    st.session_state["session_obj"] = session
    st.rerun()


def render_sidebar() -> None:
    """Render the progress history sidebar."""
    from src.progress_tracker import aggregate_progress, delete_session, delete_all_sessions

    with st.sidebar:
        if st.button("➕ New Session", use_container_width=True):
            new_session()

        st.divider()
        st.title("📊 Progress History")
        records = aggregate_progress()
        if not records:
            st.info("No past sessions found. Submit a transcript to get started!")
            return

        # Clear all history (with confirmation)
        if st.session_state.get("confirm_clear_all"):
            st.warning("This will delete **all** session history permanently.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, delete all", key="confirm_yes", use_container_width=True):
                    delete_all_sessions()
                    for key in ["session_id", "messages", "turn_index", "session_obj", "confirm_clear_all"]:
                        st.session_state.pop(key, None)
                    st.rerun()
            with col2:
                if st.button("Cancel", key="confirm_no", use_container_width=True):
                    st.session_state.pop("confirm_clear_all", None)
                    st.rerun()
        else:
            if st.button("🗑️ Clear All History", use_container_width=True):
                st.session_state["confirm_clear_all"] = True
                st.rerun()

        st.divider()
        for rec in records:
            is_active = rec.session_id == st.session_state.get("session_id")
            label = f"{'🟢 ' if is_active else ''}Session — {rec.date[:10]}"
            with st.expander(label):
                st.write(f"**Skills evaluated**: {', '.join(rec.skills_evaluated)}")
                if rec.scores:
                    st.write("**Scores**:")
                    for skill_id, score in rec.scores.items():
                        st.write(f"- `{skill_id}`: {score:.1f}/5")
                if rec.top_focus_areas:
                    st.write(f"**Top Focus Areas**: {', '.join(rec.top_focus_areas)}")
                if is_active:
                    st.caption("(currently active)")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Open", key=f"open_{rec.session_id}", use_container_width=True):
                            load_past_session(rec.session_id)
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{rec.session_id}", use_container_width=True):
                            delete_session(rec.session_id)
                            st.rerun()


def render_message(msg: Message) -> None:
    """Render a single message in the chat UI."""
    with st.chat_message(msg.role):
        st.markdown(msg.content)


def persist_session() -> None:
    """Save the current session to disk."""
    from src.progress_tracker import save_session

    session_obj: Session = st.session_state["session_obj"]
    session_obj.messages = st.session_state["messages"]
    try:
        save_session(session_obj)
    except Exception:
        pass  # Non-critical; don't surface persistence errors to the user


def main() -> None:
    init_session_state()

    st.title("💬 ConvCoach")
    st.caption(
        "Submit a conversation transcript for structured coaching feedback. "
        "Prefix with `Purpose: <goal>` to get purpose-aligned analysis."
    )

    # Sidebar progress view
    render_sidebar()

    # Render existing conversation history
    for msg in st.session_state["messages"]:
        render_message(msg)

    # Chat input
    user_input = st.chat_input("Paste your transcript here… (Prefix with 'Purpose: <goal>' optionally)")

    if user_input:
        now = datetime.now(timezone.utc).isoformat()

        # Add user message to history
        user_msg = Message(role="user", content=user_input, timestamp=now)
        st.session_state["messages"].append(user_msg)

        with st.chat_message("user"):
            st.markdown(user_input)

        # Check truncation upfront and warn via st.warning
        if len(user_input) > 10000:
            st.warning("Transcript truncated to 10,000 characters for processing.")

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Analysing your transcript…"):
                try:
                    agent = get_agent()
                    feedback, rendered_text = agent.process(
                        raw_text=user_input,
                        session_id=st.session_state["session_id"],
                        turn_index=st.session_state["turn_index"],
                        session_history=[m.to_dict() for m in st.session_state["messages"]],
                    )
                except FileNotFoundError as e:
                    rendered_text = (
                        f"⚠️ **Missing data file**: {e}\n\n"
                        "Please ensure the `data/` directory contains all required reference files."
                    )
                    feedback = None
                except EnvironmentError as e:
                    rendered_text = f"⚠️ **Setup Error**: {e}"
                    feedback = None

            st.markdown(rendered_text)

        # Save assistant message
        assistant_msg = Message(
            role="assistant",
            content=rendered_text,
            timestamp=datetime.now(timezone.utc).isoformat(),
            feedback=feedback,
        )
        st.session_state["messages"].append(assistant_msg)
        st.session_state["turn_index"] += 1

        # Persist to disk after each assistant response (G-08)
        persist_session()

        st.rerun()


main()
