from dataclasses import replace

from local_ai import memory


def test_session_context_get_returns_normalized_summary_and_turns(monkeypatch):
    monkeypatch.setattr(
        memory,
        "session_load",
        lambda session_name: {
            "session": session_name,
            "summary": {"text": "User prefers SQLite."},
        },
    )
    monkeypatch.setattr(
        memory,
        "session_turns_get",
        lambda session_name: [
            {
                "role": "user",
                "content": "My favorite database is SQLite.",
            }
        ],
    )

    context = memory.session_context_get("api-test")

    assert context == {
        "session": "api-test",
        "summary": "User prefers SQLite.",
        "turns": [
            {
                "role": "user",
                "content": "My favorite database is SQLite.",
            }
        ],
        "available": True,
    }


def test_session_context_get_is_available_with_turns_only(monkeypatch):
    monkeypatch.setattr(
        memory,
        "session_load",
        lambda session_name: {
            "session": session_name,
            "summary": None,
        },
    )
    monkeypatch.setattr(
        memory,
        "session_turns_get",
        lambda session_name: [
            {
                "role": "assistant",
                "content": "SQLite is available.",
            }
        ],
    )

    context = memory.session_context_get("api-test")

    assert context["summary"] is None
    assert context["turns"] == [
        {
            "role": "assistant",
            "content": "SQLite is available.",
        }
    ]
    assert context["available"] is True


def test_session_context_get_is_unavailable_without_context(monkeypatch):
    monkeypatch.setattr(
        memory,
        "session_load",
        lambda session_name: {
            "session": session_name,
            "summary": None,
        },
    )
    monkeypatch.setattr(
        memory,
        "session_turns_get",
        lambda session_name: [],
    )

    context = memory.session_context_get("empty-session")

    assert context == {
        "session": "empty-session",
        "summary": None,
        "turns": [],
        "available": False,
    }


def test_session_summarize_persists_summary_and_recent_messages(monkeypatch):
    session_data = {
        "session": "api-test",
        "created_at": "2026-08-01T00:00:00+00:00",
        "updated_at": "2026-08-01T00:00:00+00:00",
        "summary": None,
        "messages": [
            {"role": "user", "content": "older user message"},
            {"role": "assistant", "content": "older assistant message"},
            {"role": "user", "content": "recent user message"},
            {"role": "assistant", "content": "recent assistant message"},
        ],
    }
    saved = []

    monkeypatch.setattr(
        memory,
        "CONFIG",
        replace(
            memory.CONFIG,
            summary_keep_recent_messages=2,
            summary_max_input_messages=12,
            summary_max_input_chars=4000,
        ),
    )
    monkeypatch.setattr(
        memory,
        "session_load",
        lambda session_name: session_data,
    )
    monkeypatch.setattr(
        memory,
        "ollama_ensure_running",
        lambda: None,
    )
    monkeypatch.setattr(
        memory,
        "ollama_generate",
        lambda prompt, model_name: "Generated summary.",
    )
    monkeypatch.setattr(
        memory,
        "timestamp_now_get",
        lambda: "2026-08-07T10:00:00+00:00",
    )
    monkeypatch.setattr(
        memory,
        "session_save",
        lambda data, session_name: saved.append((data, session_name)),
    )

    result = memory.session_summarize("api-test")

    assert result == {
        "changed": True,
        "reason": "summarized",
    }
    assert len(saved) == 1

    saved_session, saved_name = saved[0]

    assert saved_name == "api-test"
    assert saved_session["summary"] == {
        "text": "Generated summary.",
        "updated_at": "2026-08-07T10:00:00+00:00",
        "source_message_count": 4,
    }
    assert saved_session["messages"] == [
        {"role": "user", "content": "recent user message"},
        {"role": "assistant", "content": "recent assistant message"},
    ]