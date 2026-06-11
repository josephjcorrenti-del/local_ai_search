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

    def fake_build_prompt(query, evidence):
        calls.append(("build_prompt", query, evidence))
        return "built prompt"

    def fake_ask(prompt: str) -> str:
        calls.append(("ask", prompt))
        return "answer text"

    monkeypatch.setattr(pipeline, "build_prompt", fake_build_prompt)
    monkeypatch.setattr(pipeline.local_ai, "ask", fake_ask)

    evidence = {"results": []}

    assert pipeline.run_query("question text", evidence) == "answer text"

    assert calls == [
        ("build_prompt", "question text", evidence),
        ("ask", "built prompt"),
    ]