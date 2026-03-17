import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Optional


@dataclass
class AgentStreamEvent:
    agent_name: str
    session_id: str
    event_type: str
    payload: Dict[str, Any]
    sequence: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "session_id": self.session_id,
            "type": self.event_type,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class AgentStreamSession:
    def __init__(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
    ):
        self.agent_name = agent_name
        self.session_id = session_id or uuid.uuid4().hex
        self._queue: queue.Queue[AgentStreamEvent | object] = queue.Queue()
        self._sentinel = object()
        self._lock = threading.Lock()
        self._sequence = 0
        self._closed = False

    def emit(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        agent_name: Optional[str] = None,
    ) -> None:
        with self._lock:
            if self._closed:
                return
            self._sequence += 1
            sequence = self._sequence
        event_payload = self._normalize_payload(payload)
        event = AgentStreamEvent(
            agent_name=agent_name or self.agent_name,
            session_id=self.session_id,
            event_type=event_type,
            payload=event_payload,
            sequence=sequence,
        )
        self._queue.put(event)

    def finish(self, payload: Optional[Dict[str, Any]] = None, event_type: str = "completion") -> None:
        if payload is not None:
            self.emit(event_type, payload)
        with self._lock:
            if self._closed:
                return
            self._closed = True
        self._queue.put(self._sentinel)

    def stream(self) -> Iterator[AgentStreamEvent]:
        while True:
            item = self._queue.get()
            if item is self._sentinel:
                break
            yield item

    @staticmethod
    def _normalize_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, dict):
            return dict(payload)
        return {"value": payload}


class AgentStreamRegistry:
    def __init__(self):
        self._sessions: Dict[str, AgentStreamSession] = {}
        self._lock = threading.Lock()

    def start_session(
        self,
        agent_name: str,
        session_id: Optional[str] = None,
    ) -> AgentStreamSession:
        with self._lock:
            if session_id:
                existing = self._sessions.get(session_id)
                if existing is not None:
                    return existing
            session = AgentStreamSession(agent_name, session_id)
            self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[AgentStreamSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)


agent_stream_registry = AgentStreamRegistry()
