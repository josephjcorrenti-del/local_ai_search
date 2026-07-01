from local_ai_search.session_evidence import build_session_evidence


def test_build_session_evidence_includes_recent_turns(monkeypatch):
    from local_ai_search import session_evidence

    monkeypatch.setattr(
        session_evidence,
        "session_turns_get",
        lambda session_name: [
            {"role": "user", "content": "My favorite database is SQLite."},
            {"role": "assistant", "content": "Your favorite database is SQLite."},
        ],
    )
    monkeypatch.setattr(
        session_evidence,
        "session_load",
        lambda session_name: {
            "session": session_name,
            "summary": None,
        },
    )

    evidence = build_session_evidence("api-test")

    assert evidence["artifact_type"] == "session_context"
    assert evidence["provider"] == "local_ai"
    assert evidence["session"] == "api-test"
    assert evidence["results"][0]["source_type"] == "session"
    assert evidence["results"][0]["snippet"] == "My favorite database is SQLite."


def test_build_session_evidence_includes_summary_before_turns(monkeypatch):
    from local_ai_search import session_evidence

    monkeypatch.setattr(
        session_evidence,
        "session_turns_get",
        lambda session_name: [{"role": "user", "content": "Recent message"}],
    )
    monkeypatch.setattr(
        session_evidence,
        "session_load",
        lambda session_name: {
            "session": session_name,
            "summary": {"text": "Older summary"},
        },
    )

    evidence = build_session_evidence("api-test")

    assert evidence["results"][0]["title"] == "Session summary: api-test"
    assert evidence["results"][0]["snippet"] == "Older summary"
    assert evidence["results"][1]["snippet"] == "Recent message"
