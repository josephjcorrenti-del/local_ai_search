from local_ai_search.workspace_evidence import build_workspace_evidence


def test_build_workspace_evidence_includes_notes(monkeypatch):
    from local_ai_search import workspace_evidence

    monkeypatch.setattr(
        workspace_evidence,
        "workspace_chat_sources_get",
        lambda workspace_name: {
            "name": workspace_name,
            "notes": "Use this workspace for local_ai_search development.",
            "sessions": [],
            "files": [],
            "web_artifacts": [],
        },
    )

    evidence = build_workspace_evidence("local_ai_search")

    assert evidence["artifact_type"] == "workspace_context"
    assert evidence["provider"] == "local_ai"
    assert evidence["workspace"] == "local_ai_search"
    assert evidence["results"][0]["source_type"] == "workspace"
    assert evidence["results"][0]["title"] == "Workspace notes: local_ai_search"
    assert evidence["results"][0]["snippet"] == "Use this workspace for local_ai_search development."


def test_build_workspace_evidence_includes_workspace_references(monkeypatch):
    from local_ai_search import workspace_evidence

    monkeypatch.setattr(
        workspace_evidence,
        "workspace_chat_sources_get",
        lambda workspace_name: {
            "name": workspace_name,
            "notes": "",
            "sessions": ["default"],
            "files": ["docs/todo-list.md"],
            "web_artifacts": ["data/local_search/artifacts/web/example.json"],
        },
    )

    evidence = build_workspace_evidence("local_ai_search")

    assert [result["title"] for result in evidence["results"]] == [
        "Workspace session: default",
        "Workspace file: docs/todo-list.md",
        "Workspace web artifact: data/local_search/artifacts/web/example.json",
    ]

    assert [result["rank"] for result in evidence["results"]] == [1, 2, 3]
    assert all(result["source_type"] == "workspace" for result in evidence["results"])
