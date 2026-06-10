from local_ai_search.pipeline import build_prompt


def test_build_prompt_exists():
    try:
        build_prompt("test", {})
    except NotImplementedError:
        pass
