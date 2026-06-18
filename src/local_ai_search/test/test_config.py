from pathlib import Path

import pytest
import configparser

from local_ai_search.config import (
    AppConfig,
    ConfigError,
    DEFAULT_SEARCH_PROVIDER,
    SUPPORTED_SEARCH_PROVIDERS,
    SearchConfig,
    AIConfig,
    IntegrationConfig,
    default_config_text,
    load_config,
    validate_config,
)


def write_config(path: Path, *, provider: str = "local_search") -> None:
    path.write_text(
        f"""
[search]
app_name = local_search
provider = {provider}
web_provider = searxng
provider_url = http://localhost:8080
default_limit = 10
timeout_seconds = 20
chunk_size = 1200
chunk_overlap = 200

[ai]
ollama_base_url = http://127.0.0.1:11434
request_timeout_seconds = 120
small_model = phi3:mini
lightweight_model = phi3:mini
large_model = qwen2.5-coder:3b
chat_model = large_model
summary_model = lightweight_model

[integration]
default_mode = integrated
evidence_limit = 5
evidence_max_chars = 4000
""".strip(),
        encoding="utf-8",
    )


def test_default_config_uses_local_search():
    config = load_config()

    assert config.search_provider == DEFAULT_SEARCH_PROVIDER
    assert config.search.provider == "local_search"


def test_supported_providers_document_duckduckgo_as_non_default():
    assert SUPPORTED_SEARCH_PROVIDERS == ("local_search", "duckduckgo")
    assert DEFAULT_SEARCH_PROVIDER == "local_search"


def test_default_config_text_documents_supported_providers():
    text = default_config_text()

    assert "[search]" in text
    assert "provider = local_search" in text
    assert "# - local_search" in text
    assert "# - duckduckgo" in text


def test_load_config_from_file(tmp_path: Path):
    config_path = tmp_path / "config.ini"
    write_config(config_path, provider="duckduckgo")

    config = load_config(config_path)

    assert config.search_provider == "duckduckgo"
    assert config.search.provider == "duckduckgo"
    assert config.integration.evidence_limit == 5
    assert config.integration.evidence_max_chars == 4000


def test_reject_unsupported_provider():
    config = AppConfig(
        search=SearchConfig(
            provider="surprise_engine",
            provider_url="http://localhost:8080",
            default_limit=10,
            timeout_seconds=20,
        ),
        ai=AIConfig(
            ollama_base_url="http://127.0.0.1:11434",
            request_timeout_seconds=120,
            small_model="phi3:mini",
            lightweight_model="phi3:mini",
            large_model="qwen2.5-coder:3b",
            chat_model="large_model",
            summary_model="lightweight_model",
        ),
        integration=IntegrationConfig(
            default_mode="integrated",
            evidence_limit=5,
            evidence_max_chars=4000,
        ),
    )

    with pytest.raises(ConfigError, match="unsupported search provider"):
        validate_config(config)


def test_reject_missing_config_file(tmp_path: Path):
    config_path = tmp_path / "missing.ini"

    with pytest.raises(ConfigError, match="config file not found"):
        load_config(config_path)


def test_reject_invalid_ini(tmp_path: Path):
    config_path = tmp_path / "config.ini"
    config_path.write_text("provider local_search\n", encoding="utf-8")

    with pytest.raises(configparser.MissingSectionHeaderError):
        load_config(config_path)