from pathlib import Path

from local_ai_search.filesystem_evidence import build_filesystem_evidence


def test_build_filesystem_evidence_reads_explicit_files(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    readme = root / "README.md"
    todo = root / "docs" / "todo-list.md"
    todo.parent.mkdir()

    readme.write_text("# Project\n\nThis is local_ai_search.", encoding="utf-8")
    todo.write_text("TODO contents", encoding="utf-8")

    evidence = build_filesystem_evidence(
        root,
        files=[
            "README.md",
            "docs/todo-list.md",
        ],
    )

    assert evidence["retrieval_version"] == 1
    assert evidence["artifact_type"] == "filesystem_context"
    assert evidence["provider"] == "filesystem"
    assert evidence["root"] == str(root)
    assert [result["rank"] for result in evidence["results"]] == [1, 2]
    assert evidence["results"][0]["title"] == "File: README.md"
    assert evidence["results"][0]["source_type"] == "file"
    assert "local_ai_search" in evidence["results"][0]["snippet"]
    assert evidence["results"][1]["title"] == "File: docs/todo-list.md"


def test_build_filesystem_evidence_is_deterministic(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    (root / "b.md").write_text("B", encoding="utf-8")
    (root / "a.md").write_text("A", encoding="utf-8")

    evidence = build_filesystem_evidence(
        root,
        files=[
            "b.md",
            "a.md",
        ],
    )

    assert [result["title"] for result in evidence["results"]] == [
        "File: a.md",
        "File: b.md",
    ]


def test_build_filesystem_evidence_rejects_path_escape(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")

    try:
        build_filesystem_evidence(root, files=["../outside.md"])
        assert False, "expected path escape to fail"
    except ValueError as exc:
        assert "outside filesystem evidence root" in str(exc)


def test_build_filesystem_evidence_skips_unsupported_extensions(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    (root / "README.md").write_text("readme", encoding="utf-8")
    (root / "image.png").write_text("not really an image", encoding="utf-8")

    evidence = build_filesystem_evidence(
        root,
        files=[
            "README.md",
            "image.png",
        ],
    )

    assert [result["title"] for result in evidence["results"]] == [
        "File: README.md",
    ]


def test_build_filesystem_evidence_bounds_file_content(tmp_path):
    root = tmp_path / "project"
    root.mkdir()

    (root / "README.md").write_text("abcdef", encoding="utf-8")

    evidence = build_filesystem_evidence(
        root,
        files=["README.md"],
        max_chars_per_file=3,
    )

    assert evidence["results"][0]["snippet"] == "abc"
