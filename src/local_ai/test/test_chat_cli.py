from __future__ import annotations

from local_ai import chat, cli


def test_prompt_run_uses_plain_prompt_and_prints_answer(
    monkeypatch,
    capsys,
):
    calls = []

    monkeypatch.setattr(
        cli,
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

    monkeypatch.setattr(cli, "ollama_chat", fake_ollama_chat)

    result = cli.prompt_run("plain question")

    assert result is None
    assert capsys.readouterr().out == "plain answer\n"
    assert calls == [
        ("ollama_ensure_running",),
        (
            "ollama_chat",
            {
                "model": cli.CONFIG.chat_model_name,
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
                        "content": "plain question",
                    },
                ],
            },
        ),
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