from local_ai_search.pipeline import build_prompt


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
    assert "If the evidence conflicts, explain the disagreement." in prompt
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


def test_run_query_calls_local_ai(monkeypatch):
    from local_ai_search import pipeline

    calls = []

    def fake_ask(prompt: str) -> str:
        calls.append(prompt)
        return "answer text"

    monkeypatch.setattr(pipeline.local_ai, "ask", fake_ask)

    answer = pipeline.run_query(
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
    assert "Question: What is SQLite?" in calls[0]
    assert "SQLite is an embedded database." in calls[0]


def test_run_query_uses_build_prompt(monkeypatch):
    from local_ai_search import pipeline

    calls = []

    def fake_build_prompt(query, evidence, session_name=None):
        calls.append(("build_prompt", query, evidence, session_name))
        return "built prompt"

    def fake_ask(prompt: str) -> str:
        calls.append(("ask", prompt))
        return "answer text"

    monkeypatch.setattr(pipeline, "build_prompt", fake_build_prompt)
    monkeypatch.setattr(pipeline.local_ai, "ask", fake_ask)

    evidence = {"results": []}

    assert pipeline.run_query("question text", evidence) == "answer text"

    assert calls == [
        ("build_prompt", "question text", evidence, None),
        ("ask", "built prompt"),
    ]

    def test_run_query_from_evidence_path_loads_evidence(monkeypatch):
        from pathlib import Path
        from local_ai_search import pipeline

        calls = []
        evidence = {"results": []}

        def fake_load_evidence(path, *, limit, max_chars):
            calls.append(("load_evidence", path, limit, max_chars))
            return evidence

        def fake_run_query(query, loaded_evidence):
            calls.append(("run_query", query, loaded_evidence))
            return "answer text"

        monkeypatch.setattr(pipeline, "load_evidence_from_local_search", fake_load_evidence)
        monkeypatch.setattr(pipeline, "run_query", fake_run_query)

        assert (
                pipeline.run_query_from_evidence_path(
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
        from local_ai_search import pipeline

        calls = []

        def fake_load_evidence(path, *, limit, max_chars):
            calls.append(("load_evidence", path, limit, max_chars))
            return {"results": []}

        def fake_run_query(query, evidence):
            calls.append(("run_query", query, evidence))
            return "answer text"

        monkeypatch.setattr(pipeline, "load_evidence_from_local_search", fake_load_evidence)
        monkeypatch.setattr(pipeline, "run_query", fake_run_query)

        assert pipeline.run_query_from_evidence_path("question text", "artifact.json") == "answer text"

        assert calls == [
            ("load_evidence", Path("artifact.json"), 5, 4000),
            ("run_query", "question text", {"results": []}),
        ]