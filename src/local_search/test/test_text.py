from local_search.text import chunk_snippet_build


def test_chunk_snippet_build_centers_near_query_term() -> None:
    content = (
        "intro words before the useful section. "
        "The release date was October 28, 2008 in North America. "
        "extra words after the useful section."
    )

    snippet = chunk_snippet_build(content, "release date", max_chars=80)

    assert "release date" in snippet.lower()
    assert len(snippet) <= 86


def test_chunk_snippet_build_bounds_output() -> None:
    content = "alpha " * 200

    snippet = chunk_snippet_build(content, "alpha", max_chars=50)

    assert len(snippet) <= 53


def test_chunk_snippet_build_normalizes_whitespace() -> None:
    content = "alpha\n\n\tbravo     charlie"

    snippet = chunk_snippet_build(content, "bravo", max_chars=80)

    assert snippet == "alpha bravo charlie"
