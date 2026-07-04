from pathlib import Path

from local_ai_search.filesystem_policy import path_should_include



def test_path_should_include_supported_file():
    assert path_should_include(Path("README.md")) is True
    assert path_should_include(Path("src/local_ai_search/cli.py")) is True


def test_path_should_skip_unsupported_extension():
    assert path_should_include(Path("image.png")) is False
    assert path_should_include(Path("archive.zip")) is False


def test_path_should_skip_ignored_directory():
    assert path_should_include(Path(".git/config")) is False
    assert path_should_include(Path("node_modules/typescript/index.js")) is False
    assert path_should_include(Path("src/local_ai_search/__pycache__/cli.pyc")) is False
