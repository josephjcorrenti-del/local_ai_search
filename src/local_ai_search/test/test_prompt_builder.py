from local_ai_search.prompt_builder import build_prompt


def test_build_prompt_exists():
    try:
        build_prompt("test", {})
    except NotImplementedError:
        pass


def test_build_prompt_contains_query():
    prompt = build_prompt(
        "What is SQLite?",
        {"results": []},
    )

    assert "Question: What is SQLite?" in prompt


def test_build_prompt_contains_evidence_aware_instructions():
    prompt = build_prompt(
        "What is SQLite?",
        {"results": []},
    )

    assert "accurately, concisely, and conversationally" in prompt
    assert "Use it as your primary source of factual information" in prompt
    assert "Compare the evidence items for agreement" in prompt
    assert "describe the competing claims and the disagreement explicitly" in prompt
    assert "Do not silently choose one conflicting claim." in prompt
    assert "If one claim is better supported, explain why" in prompt
    assert "separate what is established, what is uncertain" in prompt
    assert "the available evidence does not establish this" in prompt
    assert "The application presents provenance separately." in prompt
    assert "Do not mention snippet numbers." in prompt
    assert "Do not attribute common programming constructs to individual sources." in prompt


def test_build_prompt_contains_evidence():
    prompt = build_prompt(
        "What is SQLite?",
        {
            "results": [
                {
                    "rank": 1,
                    "title": "SQLite",
                    "url": "https://example.com",
                    "snippet": "Embedded database",
                }
            ]
        },
    )

    assert "[1] SQLite" in prompt
    assert "https://example.com" in prompt
    assert "Embedded database" in prompt


def test_build_prompt_preserves_competing_evidence_and_requires_qualified_synthesis():
    prompt = build_prompt(
        "How long should records be retained?",
        {
            "results": [
                {
                    "rank": 1,
                    "title": "Thirty-day policy",
                    "url": "https://example.com/thirty-days",
                    "snippet": "Records should be retained for 30 days.",
                },
                {
                    "rank": 2,
                    "title": "Ninety-day policy",
                    "url": "https://example.com/ninety-days",
                    "snippet": "Records should be retained for 90 days.",
                },
            ]
        },
    )

    assert "[1] Thirty-day policy" in prompt
    assert "Records should be retained for 30 days." in prompt
    assert "[2] Ninety-day policy" in prompt
    assert "Records should be retained for 90 days." in prompt
    assert "describe the competing claims and the disagreement explicitly" in prompt
    assert "Do not silently choose one conflicting claim." in prompt
    assert "If one claim is better supported, explain why" in prompt


def test_run_query_calls_local_ai(monkeypatch):
    from local_ai_search import prompt_builder

    calls = []

    def fake_chat(
        user_prompt,
        *,
        session_name=None,
        orchestrator_context=None,
    ):
        calls.append(
            (
                user_prompt,
                session_name,
                orchestrator_context,
            )
        )
        return "answer text"

    monkeypatch.setattr(
        prompt_builder.local_ai,
        "chat",
        fake_chat,
    )

    answer = prompt_builder.run_query(
        "What is SQLite?",
        {
            "results": [
                {
                    "rank": 1,
                    "title": "SQLite",
                    "url": "https://example.com",
                    "snippet": "SQLite is an embedded database.",
                }
            ]
        },
    )

    assert answer == "answer text"
    assert len(calls) == 1

    user_prompt, session_name, orchestrator_context = calls[0]

    assert user_prompt == "What is SQLite?"
    assert session_name is None
    assert "Question: What is SQLite?" in orchestrator_context
    assert "SQLite is an embedded database." in orchestrator_context


def test_run_query_uses_build_prompt(monkeypatch):
    from local_ai_search import prompt_builder

    calls = []

    def fake_build_prompt(query, evidence, session_name=None):
        calls.append(("build_prompt", query, evidence, session_name))
        return "built prompt"

    def fake_chat(
            user_prompt,
            *,
            session_name=None,
            orchestrator_context=None,
    ):
        calls.append(
            (
                user_prompt,
                session_name,
                orchestrator_context,
            )
        )
        return "answer text"

    monkeypatch.setattr(prompt_builder, "build_prompt", fake_build_prompt)
    monkeypatch.setattr(prompt_builder.local_ai, "chat", fake_chat)

    evidence = {"results": []}

    assert prompt_builder.run_query("question text", evidence) == "answer text"

    assert calls == [
        (
            "build_prompt",
            "question text",
            evidence,
            None,
        ),
        (
            "question text",
            None,
            "built prompt",
        ),
    ]

def test_run_query_from_evidence_path_loads_evidence(monkeypatch):
    from pathlib import Path
    from local_ai_search import prompt_builder

    calls = []
    evidence = {"results": []}

    def fake_load_evidence(path, *, limit, max_chars):
        calls.append(("load_evidence", path, limit, max_chars))
        return evidence

    def fake_run_query(query, loaded_evidence):
        calls.append(("run_query", query, loaded_evidence))
        return "answer text"

    monkeypatch.setattr(prompt_builder, "load_evidence_from_local_search", fake_load_evidence)
    monkeypatch.setattr(prompt_builder, "run_query", fake_run_query)

    assert (
            prompt_builder.run_query_from_evidence_path(
                "question text",
                "artifact.json",
                limit=3,
                max_chars=100,
            )
            == "answer text"
    )

    assert calls == [
        ("load_evidence", Path("artifact.json"), 3, 100),
        ("run_query", "question text", evidence),
    ]

def test_run_query_from_evidence_path_uses_defaults(monkeypatch):
    from pathlib import Path
    from local_ai_search import prompt_builder

    calls = []

    def fake_load_evidence(path, *, limit, max_chars):
        calls.append(("load_evidence", path, limit, max_chars))
        return {"results": []}

    def fake_run_query(query, evidence):
        calls.append(("run_query", query, evidence))
        return "answer text"

    monkeypatch.setattr(prompt_builder, "load_evidence_from_local_search", fake_load_evidence)
    monkeypatch.setattr(prompt_builder, "run_query", fake_run_query)

    assert prompt_builder.run_query_from_evidence_path("question text", "artifact.json") == "answer text"

    assert calls == [
        ("load_evidence", Path("artifact.json"), 5, 4000),
        ("run_query", "question text", {"results": []}),
    ]


def test_run_query_delegates_named_session_persistence(monkeypatch):
    from local_ai_search import prompt_builder

    calls = []

    monkeypatch.setattr(
        prompt_builder,
        "build_prompt",
        lambda query, evidence, session_name=None: "built prompt",
    )

    def fake_chat(
            user_prompt,
            *,
            session_name=None,
            orchestrator_context=None,
    ):
        calls.append(
            (
                user_prompt,
                session_name,
                orchestrator_context,
            )
        )
        return "answer text"

    monkeypatch.setattr(prompt_builder.local_ai, "chat", fake_chat)

    answer = prompt_builder.run_query(
        "question text",
        {"results": []},
        session_name="api-test-session",
    )

    assert answer == "answer text"
    assert calls == [
        (
            "question text",
            "api-test-session",
            "built prompt",
        )
    ]