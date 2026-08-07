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
