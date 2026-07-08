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
        json={"query": "what is sqlite?", "mode": "ai_only"},
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

    def fake_resolve_evidence(
        query,
        *,
        decision,
        session_name=None,
        workspace_name=None,
        filesystem_root=None,
        filesystem_files=None,
        limit=None,
        max_chars=None,
    ):
        calls.append(
            (
                "resolve_evidence",
                query,
                decision.route,
                session_name,
                limit,
                max_chars,
            )
        )
        return evidence

    monkeypatch.setattr(routes, "resolve_evidence", fake_resolve_evidence)

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
    assert data["answer"] is None
    assert data["evidence"] == evidence

    assert calls == [
        (
            "resolve_evidence",
            "jumping insects",
            "retrieve",
            None,
            3,
            500,
        )
    ]


def test_api_index_page():
    client = TestClient(create_app())

    response = client.get("/api/v1/")

    assert response.status_code == 200
    assert "local_ai_search" in response.text
    assert "/api/v1/query" in response.text


def test_api_query_integrated_returns_answer_and_evidence(monkeypatch):
    from local_ai_search.api import routes

    calls = []

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

    def fake_resolve_evidence(
        query,
        *,
        decision,
        session_name=None,
        workspace_name=None,
        filesystem_root=None,
        filesystem_files=None,
        limit=None,
        max_chars=None,
    ):
        calls.append(("resolve_evidence", query))
        return evidence

    def fake_run_query(query, loaded_evidence, session_name=None):
        calls.append(("run_query", query, loaded_evidence))
        return "SQLite answer"

    monkeypatch.setattr(routes, "resolve_evidence", fake_resolve_evidence)
    monkeypatch.setattr(routes.prompt_builder, "run_query", fake_run_query)

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is sqlite?",
            "mode": "integrated",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["mode"] == "integrated"
    assert data["answer"] == "SQLite answer"
    assert data["evidence"] == evidence

    assert calls == [
        ("resolve_evidence", "what is sqlite?"),
        ("run_query", "what is sqlite?", evidence),
    ]


def test_api_query_contract(monkeypatch):
    from local_ai_search.api import routes

    monkeypatch.setattr(routes.local_ai, "ask", lambda prompt: "test answer")

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
    assert "elapsed_ms" in data


def test_search_route_exists():
    client = TestClient(create_app())

    response = client.get("/search/")

    assert response.status_code == 200
    assert "local_ai_search" in response.text


def test_search_route_exists():
    client = TestClient(create_app())

    response = client.get("/search/")

    assert response.status_code == 200
    assert "local_ai_search" in response.text


def test_api_navigation(monkeypatch):
    from local_ai_search.api import routes

    monkeypatch.setattr(
        routes,
        "build_navigation_tree",
        lambda: {
            "sessions": [{"name": "default"}],
            "workspaces": [],
        },
    )

    client = TestClient(create_app())

    response = client.get("/api/v1/navigation")

    assert response.status_code == 200
    assert response.json() == {
        "sessions": [{"name": "default"}],
        "workspaces": [],
    }