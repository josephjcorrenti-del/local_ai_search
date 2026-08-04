from __future__ import annotations

from local_ai import chat, cli


def test_prompt_answer_get_uses_orchestrator_prompt(
    monkeypatch,
):
    calls = []

    monkeypatch.setattr(
        chat,
        "ollama_ensure_running",
        lambda: calls.append(("ollama_ensure_running",)),
    )

    def fake_ollama_chat(payload):
        calls.append(("ollama_chat", payload))
        return {
            "message": {
                "content": "plain answer",
            }
        }

    monkeypatch.setattr(chat, "ollama_chat", fake_ollama_chat)

    answer = chat.prompt_answer_get("orchestrator prompt")

    assert answer == "plain answer"
    assert calls == [
        ("ollama_ensure_running",),
        (
            "ollama_chat",
            {
                "model": chat.CONFIG.chat_model_name,
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
                        "content": "orchestrator prompt",
                    },
                ],
            },
        ),
    ]


def test_prompt_run_prints_returned_answer(
    monkeypatch,
    capsys,
):
    calls = []

    def fake_prompt_answer_get(
        prompt,
        model_name=None,
        *,
        session_name=None,
        user_content=None,
    ):
        calls.append(
            (
                prompt,
                model_name,
                session_name,
                user_content,
            )
        )
        return "plain answer"

    monkeypatch.setattr(
        cli,
        "prompt_answer_get",
        fake_prompt_answer_get,
    )

    result = cli.prompt_run("plain question")

    assert result is None
    assert capsys.readouterr().out == "plain answer\n"
    assert calls == [
        (
            "plain question",
            None,
            None,
            None,
        )
    ]


def test_chat_answer_get_uses_history_and_persists_turn(
    monkeypatch,
):
    calls = []

    monkeypatch.setattr(
        chat,
        "ollama_ensure_running",
        lambda: calls.append(("ollama_ensure_running",)),
    )

    def fake_session_turns_get(session_name):
        calls.append(("session_turns_get", session_name))
        return [
            {
                "role": "user",
                "content": "earlier question",
            },
            {
                "role": "assistant",
                "content": "earlier answer",
            },
        ]

    monkeypatch.setattr(
        chat,
        "session_turns_get",
        fake_session_turns_get,
    )

    def fake_ollama_chat(payload):
        calls.append(("ollama_chat", payload))
        return {
            "message": {
                "content": "current answer",
            }
        }

    monkeypatch.setattr(chat, "ollama_chat", fake_ollama_chat)

    def fake_session_append(role, content, session_name):
        calls.append(
            (
                "session_append",
                role,
                content,
                session_name,
            )
        )

    monkeypatch.setattr(
        chat,
        "session_append",
        fake_session_append,
    )

    answer = chat.chat_answer_get(
        "current question",
        session_name="test-session",
    )

    assert answer == "current answer"
    assert calls == [
        ("ollama_ensure_running",),
        ("session_turns_get", "test-session"),
        (
            "ollama_chat",
            {
                "model": chat.CONFIG.chat_model_name,
                "stream": False,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a concise local assistant. "
                            "Help with general questions, coding, debugging, "
                            "and technical reasoning. "
                            "Be practical and direct."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "earlier question",
                    },
                    {
                        "role": "assistant",
                        "content": "earlier answer",
                    },
                    {
                        "role": "user",
                        "content": "current question",
                    },
                ],
            },
        ),
        (
            "session_append",
            "user",
            "current question",
            "test-session",
        ),
        (
            "session_append",
            "assistant",
            "current answer",
            "test-session",
        ),
    ]


def test_chat_answer_get_accepts_orchestrator_context(
    monkeypatch,
):
    payloads = []

    monkeypatch.setattr(
        chat,
        "ollama_ensure_running",
        lambda: None,
    )
    monkeypatch.setattr(
        chat,
        "session_turns_get",
        lambda session_name: [
            {
                "role": "user",
                "content": "earlier question",
            },
            {
                "role": "assistant",
                "content": "earlier answer",
            },
        ],
    )

    def fake_ollama_chat(payload):
        payloads.append(payload)
        return {
            "message": {
                "content": "current answer",
            }
        }

    monkeypatch.setattr(
        chat,
        "ollama_chat",
        fake_ollama_chat,
    )
    monkeypatch.setattr(
        chat,
        "session_append",
        lambda role, content, session_name: None,
    )

    answer = chat.chat_answer_get(
        "current question",
        session_name="test-session",
        orchestrator_context=(
            "Use the supplied evidence when relevant.\n\n"
            "Evidence: SQLite is an embedded database."
        ),
    )

    assert answer == "current answer"
    assert payloads[0]["messages"] == [
        {
            "role": "system",
            "content": (
                "You are a concise local assistant. "
                "Help with general questions, coding, debugging, "
                "and technical reasoning. "
                "Be practical and direct."
            ),
        },
        {
            "role": "system",
            "content": (
                "Use the supplied evidence when relevant.\n\n"
                "Evidence: SQLite is an embedded database."
            ),
        },
        {
            "role": "user",
            "content": "earlier question",
        },
        {
            "role": "assistant",
            "content": "earlier answer",
        },
        {
            "role": "user",
            "content": "current question",
        },
    ]


def test_chat_run_prints_returned_answer(
    monkeypatch,
    capsys,
):
    calls = []

    def fake_chat_answer_get(
        user_prompt,
        session_name=None,
        model_name=None,
        stream=False,
        stream_chunk_handler=None,
    ):
        calls.append(
            (
                user_prompt,
                session_name,
                model_name,
                stream,
                stream_chunk_handler,
            )
        )
        return "current answer"

    monkeypatch.setattr(
        cli,
        "chat_answer_get",
        fake_chat_answer_get,
    )

    result = cli.chat_run(
        "current question",
        session_name="test-session",
    )

    assert result is None
    assert capsys.readouterr().out == "current answer\n"
    assert calls == [
        (
            "current question",
            "test-session",
            None,
            False,
            None,
        )
    ]


def test_chat_run_streams_chunks_and_prints_final_newline(
    monkeypatch,
    capsys,
):
    calls = []

    def fake_chat_answer_get(
        user_prompt,
        session_name=None,
        model_name=None,
        stream=False,
        stream_chunk_handler=None,
    ):
        calls.append(
            (
                user_prompt,
                session_name,
                model_name,
                stream,
            )
        )

        assert stream_chunk_handler is not None
        stream_chunk_handler("current ")
        stream_chunk_handler("answer")
        return "current answer"

    monkeypatch.setattr(
        cli,
        "chat_answer_get",
        fake_chat_answer_get,
    )

    result = cli.chat_run(
        "current question",
        session_name="test-session",
        model_name="test-model",
        stream=True,
    )

    assert result is None
    assert capsys.readouterr().out == "current answer\n"
    assert calls == [
        (
            "current question",
            "test-session",
            "test-model",
            True,
        )
    ]


def test_prompt_answer_get_persists_original_user_content(
    monkeypatch,
):
    calls = []

    monkeypatch.setattr(
        chat,
        "ollama_ensure_running",
        lambda: None,
    )
    monkeypatch.setattr(
        chat,
        "ollama_chat",
        lambda payload: {
            "message": {
                "content": "answer text",
            }
        },
    )

    def fake_session_append(role, content, session_name):
        calls.append((role, content, session_name))

    monkeypatch.setattr(
        chat,
        "session_append",
        fake_session_append,
    )

    answer = chat.prompt_answer_get(
        "full evidence-aware prompt",
        session_name="api-test-session",
        user_content="question text",
    )

    assert answer == "answer text"
    assert calls == [
        ("user", "question text", "api-test-session"),
        ("assistant", "answer text", "api-test-session"),
    ]