from local_ai_search.filesystem_walk import walk_filesystem


def test_walk_filesystem_returns_supported_files_deterministically(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    (root / "b.py").write_text("B", encoding="utf-8")
    (root / "a.md").write_text("A", encoding="utf-8")
    (root / "image.png").write_text("skip", encoding="utf-8")

    files = walk_filesystem(root)

    assert files == [
        "a.md",
        "b.py",
    ]


def test_walk_filesystem_skips_ignored_directories(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    (root / "README.md").write_text("readme", encoding="utf-8")

    ignored = root / "node_modules"
    ignored.mkdir()
    (ignored / "package.json").write_text("skip", encoding="utf-8")

    files = walk_filesystem(root)

    assert files == ["README.md"]


def test_walk_filesystem_respects_max_files(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()

    (root / "a.md").write_text("A", encoding="utf-8")
    (root / "b.md").write_text("B", encoding="utf-8")
    (root / "c.md").write_text("C", encoding="utf-8")

    from local_ai_search import filesystem_walk

    class FakeConfig:
        max_files = 2

    monkeypatch.setattr(
        filesystem_walk,
        "filesystem_config_get",
        lambda: FakeConfig(),
    )

    files = walk_filesystem(root)

    assert files == [
        "a.md",
        "b.md",
    ]


def test_walk_filesystem_rejects_missing_root(tmp_path):
    missing = tmp_path / "missing"

    try:
        walk_filesystem(missing)
        assert False, "expected missing root to fail"
    except ValueError as exc:
        assert "filesystem root does not exist" in str(exc)
