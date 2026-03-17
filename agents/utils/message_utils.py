from __future__ import annotations

from typing import Iterable


def prepare_messages(messages: Iterable[dict], system_prompt: str) -> list[dict]:
    """Ensure the provided conversation contains a system prompt."""
    batch = list(messages)
    if any(message.get("role") == "system" for message in batch):
        return batch
    return [{"role": "system", "content": system_prompt}, *batch]