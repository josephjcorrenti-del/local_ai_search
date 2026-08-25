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
        *,
        orchestrator_context=None,
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
        *,
        orchestrator_context=None,
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

        stream_chunk_handler("first")
        stream_chunk_handler(" second")

        return "first second"

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
    assert capsys.readouterr().out == "first second\n"
    assert len(calls) == 1

    (
        user_prompt,
        session_name,
        model_name,
        stream,
        stream_chunk_handler,
    ) = calls[0]

    assert user_prompt == "current question"
    assert session_name == "test-session"
    assert model_name == "test-model"
    assert stream is True
    assert callable(stream_chunk_handler)


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
        "built prompt",
        session_name="api-test-session",
        user_content="question text",
    )

    assert answer == "answer text"
    assert calls == [
        ("user", "question text", "api-test-session"),
        ("assistant", "answer text", "api-test-session"),
    ]


def test_chat_run_passes_orchestrator_context(
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
        *,
        orchestrator_context=None,
    ):
        calls.append(
            (
                user_prompt,
                session_name,
                orchestrator_context,
            )
        )
        return "current answer"

    monkeypatch.setattr(
        cli,
        "chat_answer_get",
        fake_chat_answer_get,
    )

    cli.chat_run(
        "current question",
        session_name="test-session",
        orchestrator_context="evidence context",
    )

    assert capsys.readouterr().out == "current answer\n"
    assert calls == [
        (
            "current question",
            "test-session",
            "evidence context",
        )
    ]


def test_chat_answer_get_repairs_citations_before_persisting(
    monkeypatch,
):
    payloads = []
    persisted = []
    answers = iter(
        [
            "SQLite is an embedded database.",
            "SQLite is an embedded database [1].",
        ]
    )

    monkeypatch.setattr(
        chat,
        "ollama_ensure_running",
        lambda: None,
    )
    monkeypatch.setattr(
        chat,
        "session_turns_get",
        lambda session_name: [],
    )

    def fake_ollama_chat(payload):
        payloads.append(payload)
        return {
            "message": {
                "content": next(answers),
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
        lambda role, content, session_name: persisted.append(
            (role, content, session_name)
        ),
    )

    answer = chat.chat_answer_get(
        "What is SQLite?",
        session_name="citation-test",
        orchestrator_context="Selected evidence: [1] SQLite",
        citation_ranks=(1,),
    )

    assert answer == "SQLite is an embedded database [1]."
    assert len(payloads) == 2
    assert payloads[1]["messages"][-2] == {
        "role": "assistant",
        "content": "SQLite is an embedded database.",
    }
    assert "Use only these references: [1]." in (
        payloads[1]["messages"][-1]["content"]
    )
    assert persisted == [
        ("user", "What is SQLite?", "citation-test"),
        (
            "assistant",
            "SQLite is an embedded database [1].",
            "citation-test",
        ),
    ]