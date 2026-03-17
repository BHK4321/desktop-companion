from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from agents.agent import Agent
from agents.coder import Coder
from agents.interfacer import Interfacer
from agents.utils.stream_utils import (
    end_stream_session,
    stream_agent_thoughts,
    stream_session_events,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AgentFactory = Dict[str, Callable[[], Agent]]

AGENT_REGISTRY: AgentFactory = {
    "interfacer": Interfacer,
    "coder": Coder,
}

SESSION_AGENT_ASSIGNMENTS: Dict[str, str] = {}


def resolve_agent(agent_name: str) -> Agent:
    key = agent_name.lower()
    cls = AGENT_REGISTRY.get(key)
    if cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown agent '{agent_name}'")
    return cls()


def _event_generator(session_id: str):
    yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
    iterator = stream_session_events(session_id)
    try:
        for event in iterator:
            yield f"data: {json.dumps(event.to_dict())}\n\n"
    finally:
        end_stream_session(session_id)

    yield "data: [DONE]\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    payload = await request.json()
    messages = payload.get("messages")

    if not isinstance(messages, list):
        raise HTTPException(status_code=400, detail="messages must be a list")
    
    session_id = payload.get("session_id")
    agent_name = "interfacer"
    agent = resolve_agent(agent_name)
    session_id = stream_agent_thoughts(
        agent,
        messages,
        session_id=session_id,
        close_on_complete=False,
    )
    agent_name = "coder"
    agent = resolve_agent(agent_name)
    session_id = stream_agent_thoughts(
        agent,
        messages,
        session_id=session_id,
        close_on_complete=True,
    )
    generator = _event_generator(session_id)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Stream-Session": session_id,
        },
    )
