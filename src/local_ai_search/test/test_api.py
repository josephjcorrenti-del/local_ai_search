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
    assert data["mode"] == "ai_only"
    assert data["query"] == "what is sqlite?"
    assert "elapsed_ms" in data
