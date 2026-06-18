from pathlib import Path


def test_workspace_create_list_show(monkeypatch, tmp_path):
    from local_ai import workspace

    class FakePaths:
        app_data_root = tmp_path

    monkeypatch.setattr(workspace, "paths_get", lambda: FakePaths())

    created = workspace.workspace_create("test-ws")

    assert created["name"] == "test-ws"
    assert created["sessions"] == []
    assert created["files"] == []
    assert created["web_artifacts"] == []
    assert created["notes"] == ""

    assert workspace.workspace_names_get() == ["test-ws"]

    loaded = workspace.workspace_load("test-ws")
    assert loaded["name"] == "test-ws"


def test_workspace_adds_are_idempotent(monkeypatch, tmp_path):
    from local_ai import workspace

    class FakePaths:
        app_data_root = tmp_path

    monkeypatch.setattr(workspace, "paths_get", lambda: FakePaths())

    workspace.workspace_create("test-ws")

    first = workspace.workspace_session_add("test-ws", "default")
    second = workspace.workspace_session_add("test-ws", "default")

    assert first["changed"] is True
    assert second["changed"] is False

    first = workspace.workspace_file_add("test-ws", "README.md")
    second = workspace.workspace_file_add("test-ws", "README.md")

    assert first["changed"] is True
    assert second["changed"] is False

    first = workspace.workspace_web_artifact_add("test-ws", "/tmp/artifact.json")
    second = workspace.workspace_web_artifact_add("test-ws", "/tmp/artifact.json")

    assert first["changed"] is True
    assert second["changed"] is False

    loaded = workspace.workspace_load("test-ws")

    assert loaded["sessions"] == ["default"]
    assert loaded["files"] == ["README.md"]
    assert loaded["web_artifacts"] == ["/tmp/artifact.json"]

def test_prompt_get_with_workspace():
    from local_ai.shell import _prompt_get

    prompt = _prompt_get(
        {
            "workspace": "test-ws",
            "session": "default",
        }
    )

    assert prompt == "local-ai:test-ws.default> "

def test_prompt_get_without_workspace():
    from local_ai.shell import _prompt_get

    prompt = _prompt_get(
        {
            "workspace": None,
            "session": "default",
        }
    )

    assert prompt == "local-ai:default> "


def test_workspace_rejects_empty_name(tmp_path, monkeypatch):
    from local_ai import workspace

    class FakePaths:
        app_data_root = tmp_path

    monkeypatch.setattr(workspace, "paths_get", lambda: FakePaths())

    try:
        workspace.workspace_create("")
        assert False, "expected workspace_create to reject empty name"
    except ValueError as exc:
        assert "workspace name cannot be empty" in str(exc)


def test_workspace_rejects_path_like_names(tmp_path, monkeypatch):
    from local_ai import workspace

    class FakePaths:
        app_data_root = tmp_path

    monkeypatch.setattr(workspace, "paths_get", lambda: FakePaths())

    bad_names = ["../evil", "a/b", r"a\b", "safe..ish"]

    for name in bad_names:
        try:
            workspace.workspace_create(name)
            assert False, f"expected workspace_create to reject {name}"
        except ValueError as exc:
            assert "invalid workspace name" in str(exc)
