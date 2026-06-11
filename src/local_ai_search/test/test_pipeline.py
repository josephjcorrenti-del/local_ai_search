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