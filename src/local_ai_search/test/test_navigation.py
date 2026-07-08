from local_ai_search.navigation import build_navigation_tree


def test_build_navigation_tree(monkeypatch):
    import local_ai_search.navigation as navigation

    monkeypatch.setattr(
        navigation,
        "session_names_get",
        lambda: ["default", "test"],
    )
    monkeypatch.setattr(
        navigation,
        "workspace_names_get",
        lambda: ["local_ai_search"],
    )
    monkeypatch.setattr(
        navigation,
        "workspace_load",
        lambda name: {
            "sessions": ["frontend"],
            "files": ["README.md", "docs/todo-list.md"],
        },
    )

    tree = build_navigation_tree()

    assert tree == {
        "sessions": [
            {"name": "default"},
            {"name": "test"},
        ],
        "workspaces": [
            {
                "name": "local_ai_search",
                "sessions": [
                    {"name": "frontend"},
                ],
                "files": [
                    {"path": "README.md"},
                    {"path": "docs/todo-list.md"},
                ],
            }
        ],
    }
