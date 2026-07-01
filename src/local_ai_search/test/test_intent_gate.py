from local_ai_search.intent_gate import decide_intent


def test_web_only_requires_retrieval():
    decision = decide_intent("anything", mode="web_only")
    assert decision.needs_retrieval is True


def test_ai_only_skips_retrieval():
    decision = decide_intent("anything", mode="ai_only")
    assert decision.needs_retrieval is False


def test_recent_query_requires_retrieval():
    decision = decide_intent(
        "what is the latest Apple release?",
        mode="integrated",
        session_name="api-test",
    )
    assert decision.needs_retrieval is True


def test_session_followup_skips_retrieval_when_session_present():
    decision = decide_intent(
        "what database did I just tell you I liked?",
        mode="integrated",
        session_name="api-test",
    )
    assert decision.needs_retrieval is False


def test_session_followup_without_session_is_insufficient_context():
    decision = decide_intent(
        "what database did I just tell you I liked?",
        mode="integrated",
        session_name=None,
    )

    assert decision.route == "insufficient_context"
    assert decision.needs_retrieval is False


def test_integrated_defaults_to_retrieval():
    decision = decide_intent("what is sqlite?", mode="integrated")
    assert decision.needs_retrieval is True


def test_session_followup_skips_retrieval_when_session_has_turns(monkeypatch):
    from local_ai_search import intent_gate

    monkeypatch.setattr(
        intent_gate,
        "session_turns_get",
        lambda session_name: [{"role": "user", "content": "SQLite"}],
    )

    decision = intent_gate.decide_intent(
        "what database did I just tell you I liked?",
        mode="integrated",
        session_name="api-test",
    )

    assert decision.route == "model_only"
    assert decision.needs_retrieval is False


def test_session_followup_uses_summary_as_context_fallback(monkeypatch):
    from local_ai_search import intent_gate

    monkeypatch.setattr(intent_gate, "session_turns_get", lambda session_name: [])
    monkeypatch.setattr(
        intent_gate,
        "session_load",
        lambda session_name: {"summary": {"text": "User likes SQLite."}},
    )

    decision = intent_gate.decide_intent(
        "what database did I just tell you I liked?",
        mode="integrated",
        session_name="api-test",
    )

    assert decision.route == "model_only"
    assert decision.needs_retrieval is False


def test_session_followup_uses_summary_as_context_fallback(monkeypatch):
    from local_ai_search import intent_gate

    monkeypatch.setattr(intent_gate, "session_turns_get", lambda session_name: [])
    monkeypatch.setattr(
        intent_gate,
        "session_load",
        lambda session_name: {"summary": {"text": "User likes SQLite."}},
    )

    decision = intent_gate.decide_intent(
        "what database did I just tell you I liked?",
        mode="integrated",
        session_name="api-test",
    )

    assert decision.route == "model_only"
    assert decision.needs_retrieval is False