from local_ai_search.artifacts import query_slug


def test_query_slug():
    assert query_slug("Jumping insects!") == "jumping_insects"
