from pathlib import Path

import pytest

from local_ai_search.config import (
    AppConfig,
    ConfigError,
    DEFAULT_SEARCH_PROVIDER,
    SUPPORTED_SEARCH_PROVIDERS,
    default_config_text,
    load_config,
    validate_config,
)


def test_default_config_uses_local_search():
    config = load_config()

    assert config.search_provider == DEFAULT_SEARCH_PROVIDER
    assert config.search_provider == "local_search"


def test_supported_providers_document_duckduckgo_as_non_default():
    assert SUPPORTED_SEARCH_PROVIDERS == ("local_search", "duckduckgo")
    assert DEFAULT_SEARCH_PROVIDER == "local_search"


def test_default_config_text_documents_supported_providers():
    text = default_config_text()

    assert "search_provider = local_search" in text
    assert "# - local_search" in text
    assert "# - duckduckgo" in text


def test_load_config_from_file(tmp_path: Path):
    config_path = tmp_path / "local_ai_search.conf"
    config_path.write_text("search_provider = duckduckgo\n", encoding="utf-8")

    config = load_config(config_path)

    assert config.search_provider == "duckduckgo"


def test_reject_unsupported_provider():
    with pytest.raises(ConfigError, match="unsupported search_provider"):
        validate_config(AppConfig(search_provider="surprise_engine"))


def test_reject_unknown_config_key(tmp_path: Path):
    config_path = tmp_path / "local_ai_search.conf"
    config_path.write_text("banana = nope\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="unknown config key"):
        load_config(config_path)


def test_reject_invalid_config_line(tmp_path: Path):
    config_path = tmp_path / "local_ai_search.conf"
    config_path.write_text("search_provider local_search\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="invalid config line"):
        load_config(config_path)
