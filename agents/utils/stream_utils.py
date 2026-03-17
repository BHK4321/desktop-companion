import threading
from typing import Any, Dict, Iterator, List, Optional

from agents.agent import Agent
from agents.streaming import AgentStreamEvent, AgentStreamSession, agent_stream_registry


def start_stream_session(agent_name: str, session_id: Optional[str] = None) -> AgentStreamSession:
    """Begin or return an existing stream session for the given agent."""
    return agent_stream_registry.start_session(agent_name, session_id)


def connect_agent_session(agent_name: str, session_id: str) -> AgentStreamSession:
    """Reattach an agent to a live session so it can emit more events."""
    session = agent_stream_registry.get_session(session_id)
    if session is None:
        raise KeyError(f"Stream session {session_id} not found")
    return session


def emit_stream_event(
    session_id: str,
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    agent_name: Optional[str] = None,
) -> None:
    """Send an event into the given session without touching the stream iterator."""
    session = agent_stream_registry.get_session(session_id)
    if session is None:
        raise KeyError(f"Stream session {session_id} not found")
    session.emit(event_type, payload, agent_name=agent_name)


def end_stream_session(
    session_id: str,
    payload: Optional[Dict[str, Any]] = None,
    event_type: str = "completion",
) -> None:
    """Signal that the stream session is complete."""
    session = agent_stream_registry.get_session(session_id)
    if session is None:
        return
    session.finish(payload, event_type)


def stream_session_events(session_id: str) -> Iterator[AgentStreamEvent]:
    """Expose the queue iterator for a live session and clean up once done."""
    session = agent_stream_registry.get_session(session_id)
    if session is None:
        raise KeyError(f"Stream session {session_id} not found")
    def _iterator():
        try:
            for event in session.stream():
                yield event
        finally:
            agent_stream_registry.remove_session(session_id)

    return _iterator()


def signal_agent_stopped(
    session_id: str,
    agent_name: str,
    reason: Optional[str] = None,
    event_type: str = "agent_stopped",
) -> None:
    """Emit a stable marker that a particular agent has stopped thinking."""
    payload: Dict[str, Any] = {"reason": reason} if reason else {}
    emit_stream_event(session_id, event_type, payload, agent_name=agent_name)


def stream_agent_thoughts(
    agent: Agent,
    messages: List[Dict[str, str]],
    session_id: Optional[str] = None,
    close_on_complete: bool = True,
) -> str:
    """Run any agent through the shared stream session and return the session_id."""
    print("Assigned: " + agent.agent_name)
    session = start_stream_session(agent.agent_name, session_id)
    session_id = session.session_id

    def _run() -> None:
        try:
            for chunk in agent.chat(messages, stream=True):
                content = chunk.get("message", {}).get("content", "")
                if not content:
                    continue
                emit_stream_event(
                    session_id,
                    "assistant_chunk",
                    {"role": "assistant", "content": content},
                    agent_name=agent.agent_name,
                )
        except Exception as exc:
            emit_stream_event(
                session_id,
                "error",
                {"message": str(exc)},
                agent_name=agent.agent_name,
            )
        finally:
            signal_agent_stopped(session_id, agent.agent_name, reason="finished")
            if close_on_complete:
                end_stream_session(session_id)

    threading.Thread(target=_run, daemon=True).start()
    return session_id
