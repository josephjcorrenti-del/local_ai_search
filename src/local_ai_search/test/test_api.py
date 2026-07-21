from fastapi.testclient import TestClient

from local_ai_search.api.app import create_app


def assert_success(response):
    assert response.status_code < 400

    data = response.json()

    assert data["ok"] is True

    return data


def assert_api_error(response, status, error_type):
    assert response.status_code == status

    data = response.json()

    assert data["ok"] is False
    assert data["error"]["type"] == error_type
    assert isinstance(data["error"]["message"], str)


def test_api_status():
    client = TestClient(create_app())

    response = client.get("/api/v1/status")

    data = assert_success(response)
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
            routes.CONFIG.default_session_name,
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


def test_api_session_history(monkeypatch):
    from local_ai_search.api import routes

    monkeypatch.setattr(
        routes,
        "session_turns_get",
        lambda session_name: [
            {
                "role": "user",
                "content": "My favorite database is SQLite.",
            },
            {
                "role": "assistant",
                "content": "SQLite is a good lightweight database.",
            },
        ],
    )

    client = TestClient(create_app())

    response = client.get("/api/v1/sessions/test")

    assert response.status_code == 200
    assert response.json() == {
        "name": "test",
        "messages": [
            {
                "role": "user",
                "content": "My favorite database is SQLite.",
            },
            {
                "role": "assistant",
                "content": "SQLite is a good lightweight database.",
            },
        ],
    }


def test_api_query_passes_workspace_to_evidence_resolution(monkeypatch):
    from local_ai_search.api import routes

    calls = []

    def fake_decide_intent(
        query,
        *,
        mode="integrated",
        session_name=None,
    ):
        class Decision:
            route = "model_only"
            reason = "workspace context selected"
            needs_retrieval = False

        return Decision()

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
            {
                "query": query,
                "session_name": session_name,
                "workspace_name": workspace_name,
                "limit": limit,
                "max_chars": max_chars,
            }
        )
        return {
            "retrieval_version": 1,
            "artifact_type": "workspace_context",
            "provider": "local_ai",
            "workspace": workspace_name,
            "results": [],
        }

    monkeypatch.setattr(routes, "decide_intent", fake_decide_intent)
    monkeypatch.setattr(routes, "resolve_evidence", fake_resolve_evidence)
    monkeypatch.setattr(
        routes.prompt_builder,
        "run_query",
        lambda query, evidence, session_name=None: "workspace answer",
    )

    monkeypatch.setattr(
        routes,
        "workspace_session_add",
        lambda workspace_name, session_name: None,
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is this project working on?",
            "mode": "integrated",
            "session": "workspace-test",
            "workspace": "local_ai_search",
            "limit": 4,
            "max_chars": 2500,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session"] == "workspace-test"
    assert data["workspace"] == "local_ai_search"

    assert response.json()["answer"] == "workspace answer"

    assert calls == [
        {
            "query": "what is this project working on?",
            "session_name": "workspace-test",
            "workspace_name": "local_ai_search",
            "limit": 4,
            "max_chars": 2500,
        }
    ]


def test_api_create_workspace(monkeypatch):
    from local_ai_search.api import routes

    calls = []

    def fake_workspace_create(name):
        calls.append(name)
        return {
            "name": name,
            "sessions": [],
            "files": [],
            "web_artifacts": [],
            "notes": "",
        }

    monkeypatch.setattr(routes, "workspace_create", fake_workspace_create)

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/workspaces",
        json={"name": "frontend-test"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "ok": True,
        "workspace": {
            "name": "frontend-test",
            "sessions": [],
            "files": [],
        },
    }
    assert calls == ["frontend-test"]


def test_api_create_workspace_rejects_duplicate(monkeypatch):
    from local_ai_search.api import routes

    monkeypatch.setattr(
        routes,
        "workspace_create",
        lambda name: (_ for _ in ()).throw(
            RuntimeError(f"Workspace already exists: {name}")
        ),
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/workspaces",
        json={"name": "frontend-test"},
    )

    assert_api_error(
        response,
        409,
        "workspace_conflict",
    )


def test_api_create_workspace_rejects_invalid_name(monkeypatch):
    from local_ai_search.api import routes

    monkeypatch.setattr(
        routes,
        "workspace_create",
        lambda name: (_ for _ in ()).throw(
            ValueError("invalid workspace name")
        ),
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/workspaces",
        json={"name": "../bad"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "ok": False,
        "error": {
            "type": "invalid_workspace",
            "message": "invalid workspace name",
        },
    }


def test_api_integrated_query_adds_session_to_workspace(monkeypatch):
    from local_ai_search.api import routes

    calls = []

    class Decision:
        route = "model_only"
        reason = "workspace selected"
        needs_retrieval = False

    monkeypatch.setattr(
        routes,
        "decide_intent",
        lambda query, *, mode, session_name=None: Decision(),
    )

    monkeypatch.setattr(
        routes,
        "resolve_evidence",
        lambda query, **kwargs: {
            "retrieval_version": 1,
            "artifact_type": "workspace_context",
            "provider": "local_ai",
            "workspace": kwargs["workspace_name"],
            "results": [],
        },
    )

    monkeypatch.setattr(
        routes.prompt_builder,
        "run_query",
        lambda query, evidence, session_name=None: calls.append(
            ("run_query", query, session_name)
        ) or "workspace answer",
    )

    monkeypatch.setattr(
        routes,
        "workspace_session_add",
        lambda workspace_name, session_name: calls.append(
            ("workspace_session_add", workspace_name, session_name)
        ),
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is this workspace about?",
            "mode": "integrated",
            "workspace": "middleware-test",
            "session": "workspace-chat",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "workspace answer"
    assert response.json()["session"] == "workspace-chat"
    assert response.json()["workspace"] == "middleware-test"

    assert calls == [
        (
            "run_query",
            "what is this workspace about?",
            "workspace-chat",
        ),
        (
            "workspace_session_add",
            "middleware-test",
            "workspace-chat",
        ),
    ]


def test_api_workspace_query_associates_default_session(monkeypatch):
    from local_ai_search.api import routes

    calls = []

    def fake_decide_intent(
        query,
        *,
        mode="integrated",
        session_name=None,
    ):
        class Decision:
            route = "model_only"
            reason = "workspace selected"
            needs_retrieval = False

        return Decision()

    monkeypatch.setattr(routes, "decide_intent", fake_decide_intent)
    monkeypatch.setattr(
        routes,
        "resolve_evidence",
        lambda query, **kwargs: {"results": []},
    )
    monkeypatch.setattr(
        routes.prompt_builder,
        "run_query",
        lambda query, evidence, session_name=None: "answer",
    )
    monkeypatch.setattr(
        routes,
        "workspace_session_add",
        lambda workspace_name, session_name: calls.append(
            (
                workspace_name,
                session_name,
            )
        ),
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is this workspace about?",
            "mode": "integrated",
            "workspace": "middleware-test",
        },
    )

    assert response.status_code == 200
    assert calls == [
        (
            "middleware-test",
            routes.CONFIG.default_session_name,
        )
    ]


def test_api_query_resolves_default_session(monkeypatch):
    from local_ai_search.api import routes

    calls = []

    def fake_decide_intent(
        query,
        *,
        mode="integrated",
        session_name=None,
    ):
        calls.append(("decide_intent", session_name))

        class Decision:
            route = "model_only"
            reason = "general question"
            needs_retrieval = False

        return Decision()

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
                session_name,
                workspace_name,
            )
        )
        return {"results": []}

    monkeypatch.setattr(routes, "decide_intent", fake_decide_intent)
    monkeypatch.setattr(routes, "resolve_evidence", fake_resolve_evidence)
    monkeypatch.setattr(
        routes.prompt_builder,
        "run_query",
        lambda query, evidence, session_name=None: calls.append(
            ("run_query", session_name)
        )
        or "answer",
    )

    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is sqlite?",
            "mode": "integrated",
        },
    )

    assert response.status_code == 200
    assert calls == [
        ("decide_intent", routes.CONFIG.default_session_name),
        (
            "resolve_evidence",
            routes.CONFIG.default_session_name,
            None,
        ),
        ("run_query", routes.CONFIG.default_session_name),
    ]


def test_api_validation_error_uses_structured_contract():
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/query",
        json={
            "query": "what is sqlite?",
            "mode": "unsupported",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "ok": False,
        "error": {
            "type": "validation_error",
            "message": "The request is invalid.",
        },
    }


def test_api_missing_route_uses_structured_contract():
    client = TestClient(create_app())

    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": {
            "type": "not_found",
            "message": "Not Found",
        },
    }


def test_api_unexpected_error_uses_structured_contract(monkeypatch):
    from local_ai_search.api import routes

    monkeypatch.setattr(
        routes,
        "build_navigation_tree",
        lambda: (_ for _ in ()).throw(RuntimeError("private details")),
    )

    client = TestClient(
        create_app(),
        raise_server_exceptions=False,
    )

    response = client.get("/api/v1/navigation")

    assert response.status_code == 500
    assert response.json() == {
        "ok": False,
        "error": {
            "type": "internal_error",
            "message": "The request could not be completed.",
        },
    }