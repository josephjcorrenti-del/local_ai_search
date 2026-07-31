from __future__ import annotations

from typing import Callable

from local_ai.config import CONFIG
from local_ai.memory import session_append, session_turns_get
from local_ai.runtime import (
    ollama_chat,
    ollama_chat_stream,
    ollama_ensure_running,
)


def chat_answer_get(
    user_prompt: str,
    session_name: str | None = None,
    model_name: str | None = None,
    stream: bool = False,
    stream_chunk_handler: Callable[[str], None] | None = None,
) -> str:
    """Run a session-aware chat request and return the answer."""
    ollama_ensure_running()

    model = model_name or CONFIG.chat_model_name

    messages = [
        {
            "role": "system",
            "content": (
                "You are a concise local assistant. "
                "Help with general questions, coding, debugging, and technical reasoning. "
                "Be practical and direct."
            ),
        }
    ]

    messages.extend(session_turns_get(session_name))
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model,
        "stream": stream,
        "messages": messages,
    }

    if stream:
        parts: list[str] = []

        for chunk in ollama_chat_stream(payload):
            if stream_chunk_handler is not None:
                stream_chunk_handler(chunk)

            parts.append(chunk)

        answer = "".join(parts)
    else:
        result = ollama_chat(payload)
        answer = result["message"]["content"]

    session_append("user", user_prompt, session_name)
    session_append("assistant", answer, session_name)

    return answer


def prompt_answer_get(
    prompt: str,
    model_name: str | None = None,
) -> str:
    """Run an orchestrator-supplied prompt and return the answer."""
    ollama_ensure_running()

    payload = {
        "model": model_name or CONFIG.chat_model_name,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a concise local assistant. "
                    "Answer clearly and directly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    result = ollama_chat(payload)
    return result["message"]["content"]