from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from agents.interfacer import Interfacer

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
interfacer = Interfacer()

def stream_from_agent(messages):
    for chunk in interfacer.chat(messages, stream=True):
        content = chunk.get("message", {}).get("content", "")
        
        if content:
            yield f"data: {json.dumps({'role': 'assistant', 'content': content})}\n\n"

    yield "data: [DONE]\n\n"

@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    payload = await request.json()

    return StreamingResponse(
        stream_from_agent(payload["messages"]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
