from fastapi.testclient import TestClient

from local_ai_search.api.app import create_app


def test_api_status():
    client = TestClient(create_app())

    response = client.get("/api/v1/status")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["service"] == "local_ai_search"


def test_api_query_contract():
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={"query": "what is sqlite?", "mode": "integrated"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "integrated"
    assert data["query"] == "what is sqlite?"
    assert "elapsed_ms" in data


def test_api_query_ai_only_calls_local_ai(monkeypatch):
    from local_ai_search.api import routes

    calls = []

    def fake_ask(prompt):
        calls.append(prompt)
        return "sqlite answer"

    monkeypatch.setattr(routes.local_ai, "ask", fake_ask)

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={"query": "what is sqlite?", "mode": "ai_only"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "ai_only"
    assert data["query"] == "what is sqlite?"
    assert data["answer"] == "sqlite answer"
    assert data["evidence"] is None
    assert calls == ["what is sqlite?"]

def test_api_query_web_only_returns_evidence(monkeypatch):
    from pathlib import Path
    from local_ai_search.api import routes

    calls = []

    evidence = {
        "retrieval_version": 1,
        "artifact_type": "web_search_results",
        "provider": "local_search",
        "query": "jumping insects",
        "fetched_at": "2026-06-19T00:00:00+00:00",
        "results": [
            {
                "rank": 1,
                "title": "Jumping insect result",
                "url": "https://example.com",
                "snippet": "A useful snippet.",
            }
        ],
    }

    def fake_search(query):
        calls.append(("search", query))
        return 0

    def fake_latest(query):
        calls.append(("latest", query))
        return Path("/tmp/search_jumping_insects.json")


    def fake_load(path, *, limit, max_chars):
        calls.append(("load", str(path), limit, max_chars))
        return evidence

    monkeypatch.setattr(routes.local_search, "search", fake_search)
    monkeypatch.setattr(routes, "latest_web_artifact_for_query", fake_latest)
    monkeypatch.setattr(routes, "load_evidence_from_local_search", fake_load)

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "jumping insects",
            "mode": "web_only",
            "limit": 3,
            "max_chars": 500,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "web_only"
    assert data["query"] == "jumping insects"
    assert data["answer"] is None
    assert data["evidence"]["provider"] == "local_search"
    assert data["evidence"]["results"][0]["title"] == "Jumping insect result"

    assert calls == [
        ("search", "jumping insects"),
        ("latest", "jumping insects"),
        ("load", "/tmp/search_jumping_insects.json", 3, 500),
    ]


def test_api_index_page():
    client = TestClient(create_app())

    response = client.get("/api/v1/")

    assert response.status_code == 200
    assert "local_ai_search" in response.text
    assert "/api/v1/query" in response.text


def test_api_query_integrated_returns_answer_and_evidence(monkeypatch):
    from pathlib import Path
    from local_ai_search.api import routes

    evidence = {
        "provider": "local_search",
        "results": [
            {
                "rank": 1,
                "title": "SQLite",
                "url": "https://example.com",
                "snippet": "SQLite is a database.",
            }
        ],
    }

    monkeypatch.setattr(
        routes.local_search,
        "search",
        lambda query: 0,
    )

    monkeypatch.setattr(
        routes,
        "latest_web_artifact_for_query",
        lambda query: Path("/tmp/test.json"),
    )

    monkeypatch.setattr(
        routes,
        "load_evidence_from_local_search",
        lambda path, *, limit, max_chars: evidence,
    )

    monkeypatch.setattr(
        routes.pipeline,
        "run_query",
        lambda query, evidence: "SQLite answer",
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is sqlite?",
            "mode": "integrated",
        },
    )

    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "integrated"
    assert data["answer"] == "SQLite answer"
    assert data["evidence"] == evidence