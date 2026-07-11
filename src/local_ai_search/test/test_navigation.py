from local_ai_search.navigation import build_navigation_tree


def test_build_navigation_tree(monkeypatch):
    import local_ai_search.navigation as navigation

    monkeypatch.setattr(
        navigation,
        "sessions_stats_get",
        lambda: [
            {
                "session": "default",
                "last_updated": "2026-07-01T10:00:00+00:00",
            },
            {
                "session": "test",
                "last_updated": "2026-07-11T10:00:00+00:00",
            },
        ],
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
            {"name": "test"},
            {"name": "default"},
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


def test_build_navigation_tree_puts_recent_sessions_first(monkeypatch):
    import local_ai_search.navigation as navigation

    monkeypatch.setattr(
        navigation,
        "sessions_stats_get",
        lambda: [
            {
                "session": "older",
                "last_updated": "2026-07-01T10:00:00+00:00",
            },
            {
                "session": "missing-date",
            },
            {
                "session": "newer",
                "last_updated": "2026-07-11T10:00:00+00:00",
            },
        ],
    )
    monkeypatch.setattr(navigation, "workspace_names_get", lambda: [])

    tree = navigation.build_navigation_tree()

    assert tree["sessions"] == [
        {"name": "newer"},
        {"name": "older"},
        {"name": "missing-date"},
    ]